# -*- coding:utf-8 -*-
# author:xiajiayi
# datetime:2024/1/24 17:34
# software: PyCharm
import json
from azure_openai import predict
from history_chat import append_user_message, get_history, append_model_message, pop_history
from response import Response, Status
from utils.logger import logger

logger.basicConfig(20)


class MessageHandler:
    def __init__(self):
        self.should_return_value = True

    def handle_message(self, message: dict) -> Response:
        msg_id = message.get("msgId")
        session_uuid = message.get("sessionUuid")
        event = message.get("event")
        text = message.get("text")
        logger.info(f"接收到:msgId:{msg_id},sessionUuid:{session_uuid},event:{event},text:{text}")

        if event == "msg":
            self.should_return_value = True
            msg_event = self.handle_msg_event(session_uuid, text)
            # 如果无返回
            if msg_event:
                success = Response(msg_id=message["msgId"], text=msg_event, ai_count=1, count=1,
                                   status=Status.CONTINUE)
                return success
        elif event == "stop":
            self.handle_stop_event()
            stop = Response(msg_id=message["msgId"], text="", ai_count=1, count=1,
                            status=Status.END)
            return stop
        elif event == "regen":
            self.should_return_value = True
            regen_msg = self.handle_regen_event(session_uuid, text)
            regen = Response(msg_id=message["msgId"], text=regen_msg, ai_count=1, count=1,
                             status=Status.CONTINUE)
            return regen
        elif event == "resend":
            return self.handle_resend_event()
        else:
            return self.handle_other_event()

    def handle_msg_event(self, session_uuid: str, text: str) -> str:
        logger.info("开始会话")
        history = get_history(session_uuid)
        output_dic = predict(text, history)
        logger.info(f"返回的结果:{output_dic}")
        if self.should_return_value:
            output = output_dic.get("output")
            append_user_message(session_uuid, text)
            append_model_message(session_uuid, output)
            return output
        else:
            logger.info("终止任务")

    def handle_stop_event(self) -> str:
        # TODO: 发送消息给function服务终止任务
        logger.info("终止任务")
        self.should_return_value = False

    def handle_regen_event(self, session_uuid: str, text: str) -> str:
        logger.info("重新生成")
        # TODO: 实现重新生成逻辑
        history = pop_history(session_uuid)
        output_dic = predict(text, history)
        logger.info(f"返回的结果:{output_dic}")
        if self.should_return_value:
            output = output_dic.get("output")
            append_user_message(session_uuid, text)
            append_model_message(session_uuid, output)
            # 输出当前历史会话
            history = get_history(session_uuid)
            logger.info(f"当前历史会话:{history}")
            return output
        else:
            logger.info("终止任务")

    def handle_resend_event(self) -> str:
        logger.info("重新发送")
        # TODO: 实现重新发送逻辑
        return "重新发送"

    def handle_other_event(self) -> str:
        logger.info("其他")
        # TODO: 实现其他逻辑
        return "其他"


# 示例用法
if __name__ == "__main__":
    message_handler = MessageHandler()

    # 假设有一个消息
    sample_message = {
        "msgId": "123",
        "sessionUuid": "456",
        "event": "msg",
        "text": [{"text": "Hello, world!"}]
    }

    # 处理消息
    result = message_handler.handle_message(sample_message)
    print(result)
