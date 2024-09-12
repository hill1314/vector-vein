# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-05-15 02:02:39
# @Last Modified by:   Bi Ying
# @Last Modified time: 2024-06-25 15:22:18
import httpx

from utilities.general import mprint
from utilities.network import proxies
from utilities.config import Settings, cache
from .utils import JResponse


headers = {"user-agent": "vector-vein client"}


# 远程调用
def request(method: str, path: str, payload=None):
    settings = Settings()
    # vectorvein.ai
    url = f"https://{settings.website_domain}{path}"
    try_times = 0
    while try_times < 3:
        try:
            payload_params = {"json": payload} if method == "POST" and payload else {"params": payload}
            response = httpx.request(
                method,
                url,
                headers=headers,
                proxies=proxies(),
                timeout=15,
                **payload_params,
            )
            return response.json()
        except Exception as e:
            mprint.error(e)
            try_times += 1
    return JResponse(status=500, msg="request failed")


# 官方网站API
class OfficialSiteAPI:
    name = "official_site"

    def get_update_info(self, payload):
        if cache.get("update_info"):
            return JResponse(data=cache.get("update_info"))
        else:
            path = "/api/v1/client-software/update-info"
            response_data = request("GET", path, payload)["data"]
            official_version = response_data["version"]
            # compare official_version with self.version
            # Version format: major.minor.patch
            official_version = tuple(map(int, official_version.split(".")))
            current_version = tuple(map(int, self.version.split(".")))
            response_data["updatable"] = official_version > current_version
            cache.set("update_info", response_data, expire=600)
            return JResponse(data=response_data)

    def list_agents(self, payload):
        path = "/api/v1/client-software/agent/list"
        return request("GET", path, payload)

    def get_agent(self, payload):
        path = "/api/v1/client-software/agent/get"
        return request("GET", path, payload)

    def duplicate_agent(self, payload):
        path = "/api/v1/client-software/agent/duplicate"
        return request("GET", path, payload)

    def list_templates(self, payload):
        path = "/api/v1/client-software/template/list"
        return request("GET", path, payload)

    def get_template(self, payload):
        path = "/api/v1/client-software/template/get"
        return request("GET", path, payload)

    def list_tags(self, payload):
        path = "/api/v1/client-software/tag/list"
        return request("GET", path, payload)
