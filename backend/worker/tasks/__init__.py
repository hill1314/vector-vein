# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-04-13 15:43:01
# @Last Modified by:   Bi Ying
# @Last Modified time: 2024-06-15 14:32:42
import time
from functools import wraps

from utilities.general import mprint
from utilities.workflow import Workflow


# 任务 装饰器
class Task:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def s(self, *args, **kwargs):
        # （返回函数信息）
        return (self, args, kwargs)


def task(func):
    return Task(func)


class Chain:
    def __init__(self, *tasks):
        self.tasks = tasks

    def __call__(self, initial_data):
        result = initial_data
        # 遍历执行task任务，异常时 设置异常信息
        for task, args, kwargs in self.tasks:
            try:
                result = task(result, *args, **kwargs)
            except Exception as e:
                e.task_name = task.func.__name__
                raise e
        return result


def chain(*tasks):
    return Chain(*tasks)


@task
def on_finish(workflow_data: dict):
    workflow = Workflow(workflow_data)
    workflow.update_original_workflow_data()
    workflow.clean_workflow_data()
    workflow.report_workflow_status(200)
    return True


def on_error(*args, **kwargs):
    mprint.error(f"workflow error: {args}, {kwargs}")
    workflow_data = args[-1]
    workflow = Workflow(workflow_data)
    workflow.report_workflow_status(500)
    return True


# 测量函数运行时间的装饰器
def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        if len(args) > 1:
            node_id = args[1]
        else:
            node_id = kwargs.get("node_id")
        mprint(f"<Node:{node_id}> Function {func.__name__} took {elapsed_time} seconds to run.")
        if node_id is not None and isinstance(result, dict):
            if "node_run_time" not in result:
                result["node_run_time"] = {}
            result["node_run_time"][node_id] = elapsed_time
        return result

    return wrapper
