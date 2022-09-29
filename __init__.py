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

rd_problem = on_command("来点", permission=GROUP, priority=5, block=True)

notice_group = [632712897]


# 每天早八推送随机题目
# @scheduler.scheduled_job("cron", hour=1, minute=25)
# async def _():
#
#     logger.info("推送随机题目成功")

@rd_problem.handle()
async def rd_problem_handle(args: Message = CommandArg()):
    cmd = args.extract_plain_text()
    data = MsgData()
    msg = ""
    if cmd == "题目":
        f = random.choice(['luogu', 'cf'])
        try:
            if f == 'luogu':
                msg = msg_manager(luogu.luogu_random_button(data))
            elif f == 'cf':
                msg = msg_manager(cf.random_problem_set(data))
            await rd_problem.finish(msg)
        except httpx.ConnectTimeout as e:
            logger.error(e)
            await rd_problem.finish("出错了捏")
