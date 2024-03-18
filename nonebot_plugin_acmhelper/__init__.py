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
from nonebot_plugin_PicMenu.img_tool import img2b64


scheduler = require("nonebot_plugin_apscheduler").scheduler

rd_problem = on_command("来点", permission=GROUP, priority=5, block=False)

rank = on_command("cf排行", permission=GROUP, priority=5, block=False)

rank_add = on_command("rank添加", permission=GROUP, priority=5, block=False)

help_list = on_command("acmhelp", permission=GROUP, priority=5, block=False)

week_rank = on_command("cf周榜", permission=GROUP, priority=5, block=False)

rating_rank = on_command("rating", permission=GROUP, priority=5, block=False)

max_rating_rank = on_command("maxrating", permission=GROUP, priority=5, block=False)


cf_tags = ["binary search", "bitmasks", "brute force", "chinese remainder theorem", "combinatorics", "constructive algorithms", "data structures", "dfs and similar", "divide and conquer", "dp", "dsu", "expression parsing", "fft", "flows", "games", "geometry", "graph matchings", "graphs", "greedy", "hashing", "implementation", "math", "matrices", "meet-in-the-middle", "number theory", "probabilities", "schedules", "shortest paths", "sortings", "string suffix structures", "strings", "ternary search", "trees", "two pointers"]

notice_group = [796613975]


@scheduler.scheduled_job("cron", hour=23, minute=54)
async def _():
    bot = get_bot()
    msg = await cf.rank(cmd="day")
    for group in notice_group:
        await bot.send_group_msg(group_id=int(group), message=msg)

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
    msg = await cf.rank(cmd="day")
    if type(msg) is not str:
        await week_rank.finish(MessageSegment.image('base64://' + img2b64(msg)))
    else:
        await week_rank.finish(msg)


@rank_add.handle()
async def rank_add_handle(args: Message = CommandArg()):
    cmd = args.extract_plain_text().split(" ")
    if len(cmd) < 2:
        await rank_add.finish("该命令需要两个参数(handle + 名字，用空格分隔)")
    else:
        cf.add_rank_list(cmd[0], cmd[1])
        await rank_add.finish("添加成功捏")
    # if len(cmd) > 0:
    #     cf.add_rank_list(cmd)
    #     await rank_add.finish("添加成功捏")
    # else:
    #     await rank_add.finish("添加失败捏")


@week_rank.handle()
async def week_rank_handle():
    await week_rank.send("查询中...请稍等几秒")
    msg = await cf.rank(cmd="week")
    if type(msg) is not str:
        await week_rank.finish(MessageSegment.image('base64://' + img2b64(msg)))
    else:
        await week_rank.finish(msg)


@rating_rank.handle()
async def rating_rank_handle():
    await rating_rank.send("查询中...请稍等几秒")
    msg = await cf.rating_rank()
    if type(msg) is not str:
        await rating_rank.finish(MessageSegment.image('base64://' + img2b64(msg)))
    else:
        await rating_rank.finish(msg)
        
@max_rating_rank.handle()
async def max_rating_rank_handle():
    await max_rating_rank.send("查询中...请稍等几秒")
    msg = await cf.max_rating_rank()
    if type(msg) is not str:
        await max_rating_rank.finish(MessageSegment.image('base64://' + img2b64(msg)))
    else:
        await max_rating_rank.finish(msg)

@help_list.handle()
async def help_list_handle():
    msg = "ACM助手使用说明\n\n"
    msg += "1. 来点题目:从洛谷和cf随机抽题\n"
    msg += "2. 来点[tag](暂时只支持cf内的tags)\n"
    msg += "3. cf排行:查看每日cf刷题排行\n"
    msg += "4. rank添加 [cfid, name]:在cf排行里加入指定id和名字\n"
    msg += "5. cf周榜:查看cf周榜\n"
    msg += "6. rating:查看cf rating排行\n"
    msg += "7. cfrate [cfid]:查看指定id的rating\n"
    await help_list.finish(msg)
