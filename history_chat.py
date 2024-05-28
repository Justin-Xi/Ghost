# -*- coding:utf-8 -*-
# author:xiajiayi
# datetime:2024/1/24 19:39
# software: PyCharm
from typing import Dict

from langchain_core.messages import HumanMessage, AIMessage

from utils.logger import logger

logger.basicConfig(20)


class ConversationHistory:
    """
    会话历史
    """

    def __init__(self):
        self.memory = []

    def append_history(self, role, message):
        if role == "user":
            self.memory.append(HumanMessage(content=message))
        elif role == "assistant":
            self.memory.append(AIMessage(content=message))
        else:
            logger.error("Invalid role. Please use 'user' or 'model'.")

    def get_history(self) -> list:
        return self.memory

    # 删除最后一个user
    def pop_user(self):
        # 判断最后一个是否是HumanMessage类
        if type(self.memory[-1]) == HumanMessage:
            self.memory.pop()
            logger.info(f"删除最后一个user")

    # 删除最后一个assistant
    def pop_assistant(self):
        # 判断最后一个是否是assistant
        if type(self.memory[-1]) == AIMessage:
            self.memory.pop()
            logger.info(f"删除最后一个assistant")


history_chat: Dict[str, ConversationHistory] = {}


# 初始化历史对话
def init_history(session_uuid):
    if session_uuid in history_chat:
        return
    conversation_history = ConversationHistory()
    conversation_history.append_history("assistant",
                                        "你的角色是个人助理，你需要一步一步来完成被吩咐的事项。当遇到有时间相关的请求时，你一定要先通过给定的时间函数获取当前的时间，然后再进行下一步操作。")
    history_chat[session_uuid] = conversation_history
    logger.info(f"初始化历史对话:{session_uuid}")


# 存储用户的话到历史会话
def append_user_message(session_uuid, message):
    init_history(session_uuid)
    history_chat[session_uuid].append_history("user", message)
    logger.info(f"存储用户的话到历史会话:{session_uuid},message:{message}")


# 存储模型的话到历史会话
def append_model_message(session_uuid, message):
    init_history(session_uuid)
    history_chat[session_uuid].append_history("assistant", message)
    logger.info(f"存储模型的话到历史会话:{session_uuid},message:{message}")


# 获取历史会话
def get_history(session_uuid) -> list:
    init_history(session_uuid)
    history = history_chat[session_uuid].get_history()
    logger.info(f"获取历史会话:{session_uuid},history:{history}")
    return history


# 删除最后一侧历史会话，并返回历史会话
def pop_history(session_uuid) -> list:
    init_history(session_uuid)
    conversation_history = history_chat[session_uuid]
    history = conversation_history.get_history()
    # 判断list长度
    if len(history) == 1:
        return history
    conversation_history.pop_user()
    conversation_history.pop_assistant()
    logger.info(f"删除最后一侧历史会话，并返回历史会话:{session_uuid},history:{history}")
    return history
