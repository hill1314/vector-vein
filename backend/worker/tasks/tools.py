# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-04-26 20:58:33
# @Last Modified by:   Bi Ying
# @Last Modified time: 2024-06-25 21:42:59
import re
import io
import sys
import json
import shutil
import traceback
from pathlib import Path
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup

from utilities.config import Settings
from utilities.workflow import Workflow
from utilities.general import Retry, mprint
from utilities.network import proxies, headers
from utilities.media_processing import get_screenshot
from worker.tasks import task, timer


SKIPPING_FIELDS = [
    "language",
    "code",
    "output",
    "use_oversea_node",
    "list_input",
    "error_msg",
    "console_msg",
    "files",
]


def convert_parameter_value(value, parameter_type):
    if parameter_type == "str":
        return str(value)
    elif parameter_type == "int":
        return int(value)
    elif parameter_type == "float":
        return float(value)
    elif parameter_type == "bool":
        return bool(value)
    return value  # if none of the types match


# 程序代码
@task
@timer
def programming_function(
    workflow_data: dict,
    node_id: str,
):
    workflow = Workflow(workflow_data)
    code = workflow.get_node_field_value(node_id, "code")
    language = workflow.get_node_field_value(node_id, "language")
    fields = workflow.get_node_fields(node_id)
    list_input = workflow.get_node_field_value(node_id, "list_input")
    if isinstance(list_input, str):
        list_input = True if list_input.lower() == "true" else False

    parameters_batch = []
    for field in fields:
        if field in SKIPPING_FIELDS:
            continue
        parameter = workflow.get_node_field_value(node_id, field)
        parameter_type = workflow.get_node(node_id).get_field(field).get("type")
        if list_input:
            parameters_batch = parameters_batch or [dict() for _ in range(len(parameter))]
            for batch, parameter_value in zip(parameters_batch, parameter):
                batch[field] = convert_parameter_value(parameter_value, parameter_type)
        else:
            parameters_batch = parameters_batch or [dict()]
            parameters_batch[0][field] = convert_parameter_value(parameter, parameter_type)

    pattern = r"```.*?\n(.*?)\n```"
    code_block_search = re.search(pattern, code, re.DOTALL)

    if code_block_search:
        pure_code = code_block_search.group(1)
    else:
        pure_code = code

    output_batch = []
    files_batch = []
    error_msg_batch = []
    console_msg_batch = []
    if len(parameters_batch) == 0:
        parameters_batch.append({})

    # 创建一个StringIO对象来捕获输出
    # Create a StringIO object to capture the output
    console_output = io.StringIO()

    # 保存原始的stdout对象
    # Save the original stdout object
    original_stdout = sys.stdout

    # 将stdout重定向到StringIO对象
    # Redirect stdout to the StringIO object
    sys.stdout = console_output

    original_files = set(Path(".").iterdir())

    settings = Settings()
    output_folder = settings.output_folder

    for parameters in parameters_batch:
        if language == "python":
            try:
                exec(pure_code, globals())
                result = main(**parameters)
                output_batch.append(result)
                error_msg_batch.append("")
                console_msg_batch.append(console_output.getvalue())
            except Exception as e:
                if "name 'main' is not defined" in str(e):
                    # 如果用户没有定义main函数，则尝试直接执行代码块
                    # If the user does not define the main function, try to execute the code block directly.
                    try:
                        console_output.truncate(0)
                        console_output.seek(0)
                        exec(pure_code, globals())
                        output_batch.append(None)
                        error_msg_batch.append("")
                        console_msg_batch.append(console_output.getvalue())
                    except Exception:
                        output_batch.append(None)
                        error_msg_batch.append(traceback.format_exc())
                        console_msg_batch.append(console_output.getvalue())
                else:
                    output_batch.append(None)
                    error_msg_batch.append(traceback.format_exc())
                    console_msg_batch.append(console_output.getvalue())
            finally:
                # 清空StringIO对象以捕获下一次的输出
                # Clear the StringIO object to capture the next output
                console_output.truncate(0)
                console_output.seek(0)
        else:
            raise Exception("Unsupported language")

        # 获取新的文件列表并确定新生成的文件
        new_files = set(Path(".").iterdir()) - original_files
        new_file_paths = []
        for file_path in new_files:
            dest_file_path = Path(output_folder) / file_path.name
            shutil.move(str(file_path), str(dest_file_path))
            new_file_paths.append(str(dest_file_path.absolute()))
        files_batch.append(new_file_paths)

    # 恢复原始的stdout对象
    # Restore the original stdout object
    sys.stdout = original_stdout

    if not list_input:
        output_batch = output_batch[0]
        files_batch = files_batch[0]
        error_msg_batch = error_msg_batch[0]
        console_msg_batch = console_msg_batch[0]
    workflow.update_node_field_value(node_id, "output", output_batch)
    workflow.update_node_field_value(node_id, "files", files_batch)
    workflow.update_node_field_value(node_id, "error_msg", error_msg_batch)
    workflow.update_node_field_value(node_id, "console_msg", console_msg_batch)
    return workflow.data


# 图片搜索
@task
@timer
def image_search(
    workflow_data: dict,
    node_id: str,
):
    workflow = Workflow(workflow_data)
    search_text = workflow.get_node_field_value(node_id, "search_text")
    search_engine = workflow.get_node_field_value(node_id, "search_engine")
    count = workflow.get_node_field_value(node_id, "count")
    output_type = workflow.get_node_field_value(node_id, "output_type")

    results = []
    if search_engine == "bing":
        if isinstance(search_text, list):
            search_texts = search_text
        else:
            search_texts = [search_text]
        for text in search_texts:
            params = {
                "q": text,
                "first": "-",
                "count": 30,
                "cw": 1920,
                "ch": 929,
                "relp": 59,
                "tsc": "ImageHoverTitle",
                "datsrc": "I",
                "layout": "RowBased_Landscape",
                "mmasync": 1,
            }
            images = []
            response = httpx.get(
                "https://cn.bing.com/images/async",
                params=params,
                headers=headers,
                proxies=proxies(),
            )
            soup = BeautifulSoup(response.text, "lxml")
            images_elements = soup.select(".imgpt>a")
            for image_element in images_elements[:count]:
                image_data = json.loads(image_element["m"])
                title = image_data["t"]
                url = image_data["murl"]
                if output_type == "text":
                    images.append(url)
                elif output_type == "markdown":
                    images.append(f"![{title}]({url})")
            results.append(images)
    elif search_engine == "pexels":
        pexels_api_key = Settings().pexels_api_key
        if isinstance(search_text, list):
            search_texts = search_text
        else:
            search_texts = [search_text]
        for text in search_texts:
            params = {
                "query": text,
                "per_page": 30,
            }
            images = []
            response = httpx.get(
                "https://api.pexels.com/v1/search",
                params=params,
                headers={"Authorization": pexels_api_key},
                proxies=proxies(),
            )
            data = response.json()
            for image_data in data["photos"][:count]:
                title = image_data["photographer"]
                url = image_data["src"]["original"]
                photographer = image_data["photographer"]
                pexels_photo_url = image_data["url"]
                if output_type == "text":
                    images.append(f"{url}\nPexels {photographer}: {pexels_photo_url}")
                elif output_type == "markdown":
                    images.append(
                        f"![{title}]({url})\nPexels {photographer}: [{pexels_photo_url}]({pexels_photo_url})"
                    )
            results.append(images)

    output = results if isinstance(search_text, list) else results[0]
    workflow.update_node_field_value(node_id, "output", output)
    return workflow.data


# 截屏
@task
@timer
def screenshot(
    workflow_data: dict,
    node_id: str,
):
    workflow = Workflow(workflow_data)
    monitor_number = workflow.get_node_field_value(node_id, "monitor_number")
    output_type = workflow.get_node_field_value(node_id, "output_type")

    workflow.update_node_field_value(
        node_id, "output", get_screenshot(output_type=output_type, monitor_number=monitor_number)
    )
    return workflow.data


# 文本搜索
@task
@timer
def text_search(
    workflow_data: dict,
    node_id: str,
):
    def format_output(text: str, text_type: str, output_type: str):
        if output_type == "text":
            return text
        if text_type == "name" or text_type == "title":
            return f"### {text}"
        elif text_type == "url":
            return f"[{text}]({text})"
        elif text_type == "snippet" or text_type == "content":
            return text

    def search_with_jinaai(query: str, max_results: int = 5, try_times: int = 0) -> list:
        if try_times > 5:
            return []

        headers = {"Accept": "application/json"}
        if try_times > 2:
            headers["Authorization"] = f"Bearer {settings.get('web_search.jinaai.api_key')}"

        try:
            response = httpx.get(
                f"https://s.jina.ai/{quote(query)}",
                headers=headers,
                proxies=proxies(),
                timeout=30,
            )
            result = response.json()

            if result["code"] == 200:
                return result["data"]
            else:
                return search_with_jinaai(query, max_results, try_times + 1)
        except Exception as e:
            mprint.error(e)
            return search_with_jinaai(query, max_results, try_times + 1)

    def format_text_search_results(
        results: list, combine_result_in_text: bool, output_type: str, max_snippet_length: int
    ):
        split_str = "\n\n" if output_type == "markdown" else "\n"
        output_title, output_url, output_snippet = [], [], []

        for result in results:
            title = format_output(result["title"], "title", output_type)
            url = format_output(result["url"], "url", output_type)
            snippet = format_output(
                result.get("content", result.get("description", ""))[:max_snippet_length], "content", output_type
            )

            output_title.append(title)
            output_url.append(url)
            output_snippet.append(snippet)

        if combine_result_in_text:
            return {
                "title": split_str.join(output_title),
                "url": split_str.join(output_url),
                "snippet": split_str.join(output_snippet),
            }
        return {
            "title": output_title,
            "url": output_url,
            "snippet": output_snippet,
        }

    settings = Settings()
    workflow = Workflow(workflow_data)
    search_text = workflow.get_node_field_value(node_id, "search_text")
    search_engine = workflow.get_node_field_value(node_id, "search_engine")
    count = workflow.get_node_field_value(node_id, "count")
    combine_result_in_text = workflow.get_node_field_value(node_id, "combine_result_in_text")
    max_snippet_length = workflow.get_node_field_value(node_id, "max_snippet_length", 300)
    output_type = workflow.get_node_field_value(node_id, "output_type")

    search_texts = [search_text] if isinstance(search_text, str) else search_text

    results = {
        "output_page_title": [],
        "output_page_url": [],
        "output_page_snippet": [],
    }

    def handle_bing_results(search_results):
        split_str = "\n\n" if output_type == "markdown" else "\n"
        titles, urls, snippets = [], [], []

        for web_page in search_results["webPages"]["value"]:
            titles.append(format_output(web_page["name"], "name", output_type))
            urls.append(format_output(web_page["url"], "url", output_type))
            snippets.append(format_output(web_page["snippet"][:max_snippet_length], "snippet", output_type))

        if combine_result_in_text:
            results["output_page_title"].append(split_str.join(titles))
            results["output_page_url"].append(split_str.join(urls))
            results["output_page_snippet"].append(split_str.join(snippets))
        else:
            results["output_page_title"].append(titles)
            results["output_page_url"].append(urls)
            results["output_page_snippet"].append(snippets)

    if search_engine == "bing":
        search_url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": settings.get("web_search.bing.ocp_apim_subscription_key")}
        for text in search_texts:
            params = {"q": text, "count": count}
            request_success, response = (
                Retry(httpx.get)
                .args(
                    url=search_url,
                    headers=headers,
                    params=params,
                    proxies=proxies(),
                    timeout=20,
                )
                .retry_times(3)
                .sleep_time(10)
                .run()
            )

            search_results = response.json()
            handle_bing_results(search_results)

    elif search_engine == "jina.ai":
        for text in search_texts:
            search_results = search_with_jinaai(text, max_results=count)
            output = format_text_search_results(
                search_results, combine_result_in_text, output_type, max_snippet_length
            )
            results["output_page_title"].append(output["title"])
            results["output_page_url"].append(output["url"])
            results["output_page_snippet"].append(output["snippet"])

    if isinstance(search_text, list):
        workflow.update_node_field_value(node_id, "output_page_title", results["output_page_title"])
        workflow.update_node_field_value(node_id, "output_page_url", results["output_page_url"])
        workflow.update_node_field_value(node_id, "output_page_snippet", results["output_page_snippet"])
    else:
        workflow.update_node_field_value(node_id, "output_page_title", results["output_page_title"][0])
        workflow.update_node_field_value(node_id, "output_page_url", results["output_page_url"][0])
        workflow.update_node_field_value(node_id, "output_page_snippet", results["output_page_snippet"][0])

    return workflow.data
