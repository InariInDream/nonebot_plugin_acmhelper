import asyncio
import re
import urllib
import httpx
import random
import json
import datetime
from bs4 import BeautifulSoup as bs
from nonebot import logger
from pathlib import Path
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

cwd = Path.cwd()


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
        self.cwd = Path.cwd()
        self.config_folder_make()
        self.rank_list = []


    async def random_problem_set(self, data: MsgData, cmd=None):
        """
        随机获取Codeforces题目
        :return:
        """
        if cmd is None:
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
        else:
            url = f"https://codeforces.com/api/problemset.problems?tags={cmd}"
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

    def config_folder_make(self):
        """
        创建配置文件夹
        :return:
        """
        if not (self.cwd / 'data' / 'acm_helper').exists():
            (self.cwd / 'data' / 'acm_helper').mkdir()
        if not (self.cwd / 'data' / 'acm_helper' / 'config.json').exists():
            with open(self.cwd / 'data' / 'acm_helper' / 'config.json', 'w', encoding='utf-8') as f:
                json.dump({"rank_list": []}, f, ensure_ascii=False, indent=4)

    def get_rank_list(self):
        """
        获取配置文件中的rank_list
        :return:
        """
        with open(self.cwd / 'data' / 'acm_helper' / 'config.json', 'r', encoding='utf-8') as f:
            self.rank_list = json.load(f)["rank_list"]

    def add_rank_list(self, handle: str):
        """
        添加rank_list
        :param handle:
        :return:
        """
        self.get_rank_list()
        if handle not in self.rank_list:
            self.rank_list.append(handle)
            with open(self.cwd / 'data' / 'acm_helper' / 'config.json', 'w', encoding='utf-8') as f:
                json.dump({"rank_list": self.rank_list}, f, ensure_ascii=False, indent=4)

    async def rank(self):
        """
        获取Codeforces排名
        :return:
        """
        res = {}
        msg = ""
        self.get_rank_list()
        for user in self.rank_list:
            url = f"https://codeforces.com/api/user.status?handle={user}&from=1&count=100"
            try:
                async with httpx.AsyncClient() as client:
                    r = await client.get(url)
            except Exception as e:
                logger.error(e)
                return "获取失败,请稍后再试"
            else:
                try:
                    j = r.json()
                except json.decoder.JSONDecodeError:
                    logger.error("请求过快")
                    await asyncio.sleep(0.5)  # 过0.5秒再次请求
                    async with httpx.AsyncClient() as client:
                        r = await client.get(url)
                    j = r.json()
                if j["status"] == "OK":
                    res[user] = {"solved": 0,
                                 "rating": 0,
                                 "rated_solved": 0,
                                 'average_rating': 0}
                    problem_list = j["result"]
                    sol_list = set()
                    for p in problem_list:
                        pass_time = str(datetime.datetime.fromtimestamp(p["creationTimeSeconds"]))[0:10]
                        now_time = str(datetime.datetime.now())[0:10]
                        if pass_time == now_time and p["verdict"] == "OK" and p["problem"]["name"] not in sol_list:
                            sol_list.add(p["problem"]["name"])
                            res[user]["solved"] += 1
                            try:
                                res[user]["rating"] += p['problem']['rating']
                                res[user]["rated_solved"] += 1
                            except KeyError:
                                pass
                        elif pass_time != now_time:
                            break
                try:
                    res[user]['average_rating'] = res[user]['rating'] // res[user]['rated_solved']
                except ZeroDivisionError:
                    res[user]['average_rating'] = 0
                except KeyError:
                    pass
        sorted_res = sorted(res.items(), key=lambda x: (x[1]['solved'], x[1]['average_rating']), reverse=True)
        index = 1
        for i in sorted_res:
            if i[1]['solved'] != 0:
                msg += f"{index}：{i[0]}: solved {i[1]['solved']} 题, 平均难度 {i[1]['average_rating']}\n"
                index += 1
        if msg == "":
            msg = "今天还没有人AC题哦"
        else:
            msg = "今日AC题排名:\n" + msg
        return msg


cf = Codeforces()

