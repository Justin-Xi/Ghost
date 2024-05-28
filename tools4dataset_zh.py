from typing import Optional, Type, Union

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class ImSendMsgInput(BaseModel):
    App: str = Field(description="发送消息的工具，如果没有提到就忽略这个参数，忽略这个参数不影响函数调用")
    Receiver: list = Field(description="接收消息人的名字；可以是一个接收人，表示为[\"李四\"]；或是一组接收人，表示为[\"小刘\",\"小王\"]")
    Msg: str = Field(description="发送消息的内容")

class ImSendMsgTool(BaseTool):
    name: str = "ImSendMsg"
    description: str = "在你需要发送消息时调用，需要发送的消息如果有条件，要看清这个条件，符合条件再调用；注意App参数可以忽略；请仔细查看，找出所有接收人或群，放在一个Receiver列表中发送"
    args_schema: Type[BaseModel] = ImSendMsgInput
    optional_para = ["App"] # 可选参数列表

    def _run(
        self,
        App: str,
        Receiver: str,
        Msg: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        result = ""
        print(f"ImSendMsgTool: Receiver:{Receiver}, Msg:{Msg}, App:{App}")
        return "done"


class ImReadMsgInput(BaseModel):
    App: str = Field(description="看消息的工具，没提到就忽略这个参数")
    Sender: list = Field(description="你要看消息的人的名字；可以是看一个人/群的消息，表示为[\"小芳芳\"];也可以是多个人/群的消息，表示为[\"小刘\",\"老乡群\"];如果是多级关系，如’老乡群里的小刘‘,表示为[\"老乡群->小刘\"]；没提到就忽略这个参数")
    Type: str = Field(description="如果提到未读就是Unread，没有提到就忽略这个参数")
    Time: list = Field(description="看消息的时间，如果是一个时间就表示为[\"这两天\"]；如果是时间范围就表示为:[昨晚十点，今天上午九点]；没提到就忽略这个参数")
    Msg: str = Field(description="想要看的详细内容，没有提到就忽略这个参数")

class ImReadMsgTool(BaseTool):
    name: str = "ImReadMsg"
    description: str = "在你需要看消息时调用；如果有时间需要分析：1、如果是看消息的时间，放入Time字段，2、否则放入Msg字段"
    args_schema: Type[BaseModel] = ImReadMsgInput
    optional_para = ["App","Sender","Type","Time","Msg"] # 可选参数列表

    def _run(
        self,
        App: str,
        Sender: str,
        Type: str,
        Time: str,
        Msg: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        result = ""
        print(f"ImReadMsgTool: App:{App}, Sender:{Sender}, Type:{Type},Time:{Time}")
        return "done"


class NoteCreateInput(BaseModel):
    Msg: str = Field(description="创建便签的内容")

class NoteCreateTool(BaseTool):
    name: str = "NoteCreate"
    description: str = "在你需要创建便签时调用，用户可以说'创建一个便签'或'写个便签'或'生成一条便签'或'便签'"
    args_schema: Type[BaseModel] = NoteCreateInput

    def _run(
        self,

        Msg: str,
    ) -> str:
        """Use the tool."""
        result = ""
        print(f"NoteCreateTool: Msg:{Msg}")
        return "done"



class ScheduleCreateInput(BaseModel):

    Msg: str = Field(description="所创建日程的内容，去掉日程的日期时间部分，只保留内容")
    Time: str = Field(description="日程的日期和时间，需要具体的日期和时间,如果只提到一个日期和时间如‘创建明天上午十点的会议日程’记成[\"明天上午10点\"],如果提到两个日期和时间如'创建明天上午十点到11点的会议日程'记成[\"明天上午10点\",\"明天上午11点\"]，前面是开始时间，后面是结束时间")

class ScheduleCreateTool(BaseTool):
    name: str = "ScheduleCreate"
    description: str = "在你需要创建日程时调用，用户可以说‘创建一个日程’或者‘添加一个日程’或者‘日程’，日程说成日历也可以，如‘创建一个日历’，一定检查日期和时间的完整性，如果没有日期和时间参数需要询问"
    args_schema: Type[BaseModel] = ScheduleCreateInput

    def _run(
        self,

        Msg: str,
        Time: str,
    ) -> str:
        """Use the tool."""
        result = ""
        print(f"ScheduleCreateTool: Msg:{Msg},Time:{Time}")
        return "done"


class TodoCreateInput(BaseModel):

    Msg: str = Field(description="所创建待办的内容，去掉待办的日期时间部分，只保留内容")
    Time: str = Field(description="待办的时间,可以忽略,可以是具体的日期时间，也可以是宽泛的日期,格式如下‘创建明天上午十点的待办’记成[\"明天上午10点\"]")

class TodoCreateTool(BaseTool):
    name: str = "TodoCreate"
    description: str = "在你需要创建待办时调用，用户可以说‘创建一个待办’或者‘添加一个待办’或者‘待办’，Time参数可以忽略"
    args_schema: Type[BaseModel] = TodoCreateInput
    optional_para = ["Time"] # 可选参数列表

    def _run(
        self,

        Msg: str,
        Time: str,
    ) -> str:
        """Use the tool."""
        result = ""
        print(f"TodoCreateTool: Msg:{Msg},Time:{Time}")
        return "done"



