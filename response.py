# -*- coding:utf-8 -*-
# author:xiajiayi
# datetime:2024/1/25 15:10
# software: PyCharm
# -*- coding: utf-8 -*-
from typing import Dict

# status的枚举类
from enum import Enum


class Status(Enum):
    CONTINUE = "CONTINUE"
    END = "END"
    ERROR = "ERROR"


class Response:
    def __init__(self, msg_id, text, ai_count, count, status: Status, error_code=0, error_msg="", trace_id="",
                 usage: Dict = None):
        self.msg_id = msg_id
        self.text = text
        self.ai_count = ai_count
        self.count = count
        self.status = status
        self.error_code = error_code
        self.error_msg = error_msg
        self.trace_id = trace_id
        self.usage = usage

    def to_dict(self):
        result = {
            "msgId": self.msg_id,
            "text": self.text,
            "aiCount": self.ai_count,
            "count": self.count,
            "status": self.status.value,
        }

        if self.error_code is not None:
            result["errorCode"] = self.error_code

        if self.error_msg is not None:
            result["errorMsg"] = self.error_msg

        if self.trace_id is not None:
            result["traceId"] = self.trace_id

        if self.usage is not None:
            result["usage"] = self.usage

        return result

    def to_json(self):
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False)


# 示例用法


if __name__ == '__main__':
    json = Response(msg_id="123", text="你好", ai_count=1, count=1, status=Status.CONTINUE).to_json()
    print(json)