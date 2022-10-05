from nonebot import logger
from nonebot.params import CommandArg

from nonebot import on_startswith, on_command, require, get_bot
from nonebot.adapters.onebot.v11 import (
    GROUP,
    GroupMessageEvent,
    MessageSegment,
    Message
)
import random
import httpx
from .data_source import luogu, cf, msg_manager
from .data_struct import MsgData


scheduler = require("nonebot_plugin_apscheduler").scheduler

rd_problem = on_command("来点", permission=GROUP, priority=5, block=False)

rank = on_command("cf排行", permission=GROUP, priority=5, block=False)

rank_add = on_command("rank添加", permission=GROUP, priority=5, block=False)


cf_tags = ["binary search", "bitmasks", "brute force", "chinese remainder theorem", "combinatorics", "constructive algorithms", "data structures", "dfs and similar", "divide and conquer", "dp", "dsu", "expression parsing", "fft", "flows", "games", "geometry", "graph matchings", "graphs", "greedy", "hashing", "implementation", "math", "matrices", "meet-in-the-middle", "number theory", "probabilities", "schedules", "shortest paths", "sortings", "string suffix structures", "strings", "ternary search", "trees", "two pointers"]


@rd_problem.handle()
async def rd_problem_handle(args: Message = CommandArg()):
    cmd = args.extract_plain_text()
    data = MsgData()
    msg = ""
    if cmd == "题目":
        f = random.choice(['luogu', 'cf'])
        try:
            if f == 'luogu':
                msg = await msg_manager(await luogu.luogu_random_button(data))
            elif f == 'cf':
                msg = await msg_manager(await cf.random_problem_set(data))
            await rd_problem.finish(msg)
        except httpx.ConnectTimeout as e:
            logger.error(e)
            await rd_problem.finish("出错了捏")

    elif len(cmd) > 0:
        if cmd in cf_tags:
            try:
                msg = await msg_manager(await cf.random_problem_set(data, cmd=cmd))
                await rd_problem.finish(msg)
            except httpx.ConnectTimeout as e:
                logger.error(e)
                await rd_problem.finish("出错了捏")

    else:
        pass


@rank.handle()
async def rank_handle():
    await rank.send("查询中...请稍等几秒")
    msg = await cf.rank()
    await rank.finish(msg)


@rank_add.handle()
async def rank_add_handle(args: Message = CommandArg()):
    cmd = args.extract_plain_text()
    if len(cmd) > 0:
        cf.add_rank_list(cmd)
        await rank_add.finish("添加成功捏")
    else:
        await rank_add.finish("添加失败捏")
