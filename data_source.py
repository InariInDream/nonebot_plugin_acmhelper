import re
import urllib
import httpx
import random
import json
from bs4 import BeautifulSoup as bs
from nonebot import logger
from .data_struct import MsgData

headers = {
            "authority": "www.luogu.com.cn",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "max-age=0",
            "referer": "https://www.luogu.com.cn/",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        }


async def msg_manager(msg_data):
    msg = ''
    msg += f"题目名称：{msg_data.title}\n"
    msg += f"难度：{msg_data.difficulty}\n"
    msg += "标签："
    for i in msg_data.tags:
        msg += f"{i}, "
    msg += "\n"
    msg += f"链接：{ msg_data.href}\n"
    msg += f"题目来源：{ msg_data.platform}"

    return msg


class Luogu:
    def __init__(self):
        self.data = MsgData()

    async def luogu_random_button(self, data: MsgData):
        """
        获取洛谷随机题目
        :return:
        """
        msg = ''
        url = "https://www.luogu.com.cn/problem/P"
        num = str(int(random.uniform(0, 1) * 7400 + 100))
        url += num

        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(url, headers=headers)
        except Exception as e:
            return "网络错误"
        else:
            if r.status_code == 200:
                t = r.text
                soup = bs(t, "lxml")

                # 关键代码
                urlen = re.search(r'JSON\.parse\(decodeURIComponent\("(.+?)"\)', t).group(1)
                rrrr = urllib.parse.unquote(urlen)
                j = json.loads(rrrr)

                diff = {
                    0: "暂无评定",
                    1: "入门",
                    2: "普及-",
                    3: "普及/提高-",
                    4: "普及+/提高",
                    5: "提高+/省选-",
                    6: "省选/NOI-",
                    7: "NOI/NOI+/CTSC"
                }

                try:
                    msg += diff[j['currentData']['problem']['difficulty']]
                except Exception as e:
                    # 没这个题就再来一次捏
                    return await self.luogu_random_button(data)
                else:
                    title = soup.find("title").text[:-5]

                    data.title = title
                    data.href = url
                    data.platform = "洛谷"
                    data.difficulty = diff[j['currentData']['problem']['difficulty']]
                    data.tags = await self.get_luogu_tag(j['currentData']['problem']['tags'])

                    self.data = data

                    return self.data

    async def get_luogu_tag(self, data: list):
        """
        获取洛谷题目标签
        :param data:
        :return:
        """
        url = "https://www.luogu.com.cn/_lfe/tags"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=headers)
        j = r.json()
        tag_data = j["tags"]
        tag_list = []
        for i in tag_data:
            if i["id"] in data:
                tag_list.append(i["name"])
        return tag_list


luogu = Luogu()


class Codeforces:
    def __init__(self):
        self.data = MsgData()

    async def random_problem_set(self, data: MsgData):
        """
        随机获取Codeforces题目
        :return:
        """
        url = "https://codeforces.com/api/problemset.problems"
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(url)
        except Exception as e:
            logger.error(e)
            pass
        else:
            j = r.json()
            if j["status"] == "OK":
                problem_list = j["result"]["problems"]
                problem = random.choice(problem_list)
                data.title = problem["name"]
                data.href = "https://codeforces.com/contest/" + str(problem["contestId"]) + "/" + "problem/" + problem["index"]
                data.platform = "Codeforces"
                data.difficulty = problem["rating"]
                data.tags = problem["tags"]
                self.data = data
                return self.data


cf = Codeforces()

