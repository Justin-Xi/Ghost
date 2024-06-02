from typing import Optional, Type, Union

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class ImSendMsgInput(BaseModel):
    App: str = Field(description="A tool for sending messages, if not mentioned, ignore this parameter. Ignoring this parameter does not affect the function call")
    Receiver: list = Field(description="Recipient's name; it can be a single recipient, represented as [\"John\"]; or a group of recipients, represented as [\"Mike\", \"David\"]")
    Msg: str = Field(description="Content of the message to be sent")


class ImSendMsgTool(BaseTool):
    name: str = "ImSendMsg"
    description: str = "Call when you need to send a message. If there are conditions for the message to be sent, make sure to understand these conditions. Call only if conditions are met,The App parameter can be ignored;Please carefully check and find all the recipients or groups, and send them in a Receiver list."
    args_schema: Type[BaseModel] = ImSendMsgInput
    optional_para = ["App"] # 可选参数列表

    def _run(elf) -> str:
        return "done"

class ImReadMsgInput(BaseModel):
    App: str = Field(description="Message viewing tool, ignore this parameter if not mentioned")
    Sender: list = Field(description="The name of the person whose messages you want to see; it can be the messages of one person or group, represented as [\"Sophie\"]; it can also be the messages of multiple people/group, represented as [\"Liam\", \"Oliver\"];If it's a multi-level relationship, such as 'Tom in the hometown group', it is represented as [\"Hometown Group->Tom\"]; if there is no mention of whose message to view, ignore this parameter")
    Type: str = Field(description="If it mentions Unread, then it's Unread. If not mentioned, ignore this parameter.")
    Time: list = Field(description="Check the time of the message. If it's a single time, represent it as [\"These two days\"]; If it's a time range, represent it as: [\"10 pm\", \"9 am\"]; If no time is mentioned, ignore this parameter.")
    Msg: str = Field(description="The detailed content you want to view, ignore this parameter if not mentioned.")


class ImReadMsgTool(BaseTool):
    name: str = "ImReadMsg"
    description: str = "Call when you need to view messages; if there is time needed for analysis: 1. If it's time to view messages, put it into the Time field, 2. Otherwise, put it into the Msg field."
    args_schema: Type[BaseModel] = ImReadMsgInput
    optional_para = ["App","Sender","Type","Time","Msg"] # 可选参数列表

    def _run(elf) -> str:
        return "done"


class NoteCreateInput(BaseModel):
    Msg: str = Field(description="Creating the content of the note")

class NoteCreateTool(BaseTool):
    name: str = "NoteCreate"
    description: str = "Call this function when you need to create a note. Users can say 'Create a note', 'Write a note', 'Generate a note', or simply 'Note'"
    args_schema: Type[BaseModel] = NoteCreateInput

    def _run(elf) -> str:
        return "done"



class ScheduleCreateInput(BaseModel):

    Msg: str = Field(description="The content of the created schedule, removing the date and time part of the schedule, only retaining the content")
    Time: str = Field(description="The date and time of the schedule, If only one date and time is mentioned, such as 'create a meeting schedule at 10 am tomorrow', it is recorded as [\"10 am tomorrow\"]. If two date and time are mentioned, such as 'create a meeting schedule from 10 am to 11 am tomorrow', it is recorded as [\"10 am tomorrow\", \"11 am tomorrow\"], the first is the start time and the latter is the end time")

class ScheduleCreateTool(BaseTool):
    name: str = "ScheduleCreate"
    description: str = "Call when you need to create a schedule. Users can say 'create a schedule', 'add a schedule', or simply 'schedule'. Schedule can also be referred to as calendar, like 'create a calendar',Make sure to check the completeness of the date and time. If there are no date and time parameters, you need to ask."
    args_schema: Type[BaseModel] = ScheduleCreateInput

    def _run(elf) -> str:
        return "done"


class TodoCreateInput(BaseModel):

    Msg: str = Field(description="The content of the created todo, remove the date and time part of the to-do, only keep the content.")
    Time: str = Field(description="The time of the todo,can be ignored,can be a specific date and time, or a broad date, such as 'create a todo for tomorrow at 10 am' is noted as [\"Tomorrow at 10 am\"].")

class TodoCreateTool(BaseTool):
    name: str = "TodoCreate"
    description: str = "Call this function when you need to create a to-do. Users can say 'create a todo', 'add a todo', or 'todo',The Time parameter can be ignored"
    args_schema: Type[BaseModel] = TodoCreateInput
    optional_para = ["Time"] # 可选参数列表

    def _run(elf) -> str:
        return "done"


