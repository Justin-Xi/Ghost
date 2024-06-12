from typing import Optional, Type, Union

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class ImSendMsgInput(BaseModel):
    App: str = Field(description="Message sending tool, ignore this parameter if not mentioned")
    Receiver: list = Field(description="The name of the person who will receive the message; it can be the message of one person or group, represented as [\"Sophie\"]; it can also be the messages of multiple people/group, represented as [\"Liam\", \"Oliver\"]")
    Msg: str = Field(description="The content of the message to be sent")
    Time: list = Field(description="Provide the time when the message should be sent, formatted as ['8pm']. This parameter is optional and can be omitted if not applicable.")
    Location: list = Field(description="Specify the location from which the message is sent, represented as ['NewYork']. This parameter is optional and can be omitted if not relevant.")


class ImSendMsgTool(BaseTool):
    name: str = "ImSendMsg"
    description: str = "Call when you need to send a message or when the location condition is required to send a message. If there is location information for sending messages, put it directly into the Location field, do not ask for the specific location! For example: when you arrive in Hong Kong, send me a message with Location as ['Hong Kong']"
    args_schema: Type[BaseModel] = ImSendMsgInput
    optional_para = ["App","Time","Location"] # optional parameter list

    def _run(elf) -> str:
        return "done"

class ImReadMsgInput(BaseModel):
    App: str = Field(description="The tool for reading messages, ignore this parameter if not mentioned")
    Sender: list = Field(description="The name of the person whose messages you want to read; it can be the messages of one person/group, represented as [\"Sophie\"]; it can also be the messages of multiple people/groups, represented as [\"Liam\", \"Oliver\"]; if it is a multi-level relationship, such as 'Oliver in the group of friends', it is represented as [\"Friends->Oliver\"]; ignore this parameter if not mentioned")
    Type: str = Field(description="If it is mentioned as unread, it is Unread; ignore this parameter if not mentioned")
    Time: list = Field(description="The time to read the messages, if it is a single time, it is represented as ['these two days']; if it is a time range, it is represented as: ['last night at ten', 'nine this morning']; ignore this parameter if not mentioned")
    Msg: str = Field(description="The detailed content you want to read, ignore this parameter if not mentioned")


class ImReadMsgTool(BaseTool):
    name: str = "ImReadMsg"
    description: str = "Call when you need to read messages; if there is a time to analyze: 1. If it is the time to read messages, put it in the Time field, 2. Otherwise put it in the Msg field"
    args_schema: Type[BaseModel] = ImReadMsgInput
    optional_para = ["App","Sender","Type","Time","Msg"] # optional parameter list

    def _run(elf) -> str:
        return "done"

class MessageSearchInput(BaseModel):
    App: str = Field(description="A tool for viewing or searching messages. This parameter is optional and can be omitted if not relevant.")
    SearchCondition: str = Field(description="The detailed description of the message to be searched, including all relevant information.")
    Sender: list = Field(description="The name of the person who sent the message; it can be the message of one person or group, represented as [\"Sophie\"]; it can also be the messages of multiple people/group, represented as [\"Liam\", \"Oliver\"].For multi-level relationships, such as 'Liam in the Hometown Group', represent it as ['Hometown Group->Liam']. This parameter is optional and can be omitted if not mentioned.")
    Sign: str = Field(description="The signature of the message, such as 'good night', 'good morning', 'goodbye', etc., represented as ['good night']. This parameter is optional and can be omitted if not relevant.")
    Time: list = Field(description="The time of the message, if it is a single time, it is represented as ['these two days']; if it is a time range, it is represented as: ['last night at ten', 'nine this morning']; ignore this parameter if not mentioned")
    Type: str = Field(description="Message type. Options include 'Text' for text messages, 'Image' for images, 'Video' for videos, 'Audio' for voice messages, and 'File' for files. This parameter is optional and can be omitted if not relevant.")
    Length: str = Field(description="Message length. Specify as 'greater than 50' for messages exceeding 50 characters. This parameter is optional and can be omitted if not applicable.")
    Favorite: bool = Field(description="Whether the message is marked as a favorite, represented as True or False. This parameter is optional and can be omitted if not relevant.")
    Pin: bool = Field(description="Whether the message is pinned, represented as True or False. This parameter is optional and can be omitted if not relevant.")
    At: bool = Field(description="Whether the message is @, represented as True or False. This parameter is optional and can be omitted if not relevant.")

class MessageSearchTool(BaseTool):
    name: str = "MessageSearch"
    description: str = "Invoke this when you need to search for or view messages. For example, you might say 'find the chat history with xxx', 'view messages from xxx', or 'search the content xxx sent me'. Place the detailed description of the search in the 'Msg' field, including all relevant context. Ensure no information is omitted."
    args_schema: Type[BaseModel] = MessageSearchInput
    optional_para = ["App","Sender","Sign","Time","Type","Length","Favorite","Pin","At"] # optional parameter list

    def _run(elf) -> str:
        return "done"

class NoteCreateInput(BaseModel):
    Msg: str = Field(description="The content of the created note")
    Folder: str = Field(description="The folder where the note is placed. Users will say 'put in abc', and Folder is abc. This parameter is optional and can be omitted if not applicable.")
    Favorite: bool = Field(description="Include an option to mark the note as a favorite. Users might express this action using phrases like 'mark as favorite', 'put in favorite', or simply 'favorite'. This parameter is optional and can be omitted if not applicable.")
    Pin: bool = Field(description="Include an option to pin the note. Users might express this action using phrases like 'mark as pinned', 'set as pinned', or simply 'pinned'. This parameter is optional and can be omitted if not applicable.")
class NoteCreateTool(BaseTool):
    name: str = "NoteCreate"
    description: str ="Invoke this when you need to create a note. Users might say 'create a note', 'write a note', 'generate a note', or simply 'note'. If content needs to be generated or searched prior to creating the note, ensure that you generate/search for this content first. If it's uncertain whether there is content to generate or search, further inquiry is required."
    args_schema: Type[BaseModel] = NoteCreateInput
    optional_para = ["Folder","Favorite","Pin"] # optional parameter list

    def _run(elf) -> str:
        return "done"

class NoteModifyChdInput(BaseModel):
    Msg: str = Field(description="The content of the created note")
    Folder: str = Field(description="The folder where the note is placed. Users will say 'put in abc', and Folder is abc. This parameter is optional and can be omitted if not applicable.")
    Favorite: bool = Field(description="Include an option to mark the note as a favorite. Users might express this action using phrases like 'mark as favorite', 'put in favorite', or simply 'favorite'. This parameter is optional and can be omitted if not applicable.")
    Pin: bool = Field(description="Include an option to pin the note. Users might express this action using phrases like 'mark as pinned', 'set as pinned', or simply 'pinned'. This parameter is optional and can be omitted if not applicable.")

class NoteModifyChdTool(BaseTool):
    name: str = "NoteModifyChd"
    description: str = "delete"
    args_schema: Type[BaseModel] = NoteModifyChdInput
    optional_para = ["Msg","Folder","Favorite","Pin"]

    def _run(elf) -> str:
        return "done"


class NoteModifyInput(BaseModel):
    QueryCondition: str = Field(description="query condition", examples = "NoteModifyChd")
    NewContent: str = Field(description="modified new content", examples = "NoteModifyChd")

class NoteModifyTool(BaseTool):
    name: str = "NoteModify"
    description: str = "Called when you need to modify or add content to a note"
    args_schema: Type[BaseModel] = NoteModifyInput
    optional_para = []

    def _run(elf) -> str:
        return "done"

class NoteDeleteInput(BaseModel):
    DeleteCondition: str = Field(description="delete condition", examples = "NoteModifyChd")

class NoteDeleteTool(BaseTool):
    name: str = "NoteDelete"
    description: str = "Called when you need to delete a note, the user can say 'delete a note'"
    args_schema: Type[BaseModel] = NoteDeleteInput
    optional_para = []

    def _run(elf) -> str:
        return "done"


class ScheduleCreateInput(BaseModel):

    Msg: str = Field(description="The content of the created schedule, remove the date and time part of the schedule, only keep the content.")
    Time: str = Field(description="The date and time of the schedule, need specific date and time, if only one date and time is mentioned like 'create a meeting schedule at 10 am tomorrow' noted as [\"tomorrow at 10 am\"], if two date and time are mentioned like 'create a meeting schedule from 10 am to 11 am tomorrow' noted as [\"tomorrow at 10 am\",\"tomorrow at 11 am\"], the first is the start time and the second is the end time.")
    Note: str = Field(description="Include a field for additional information. This parameter is optional and can be omitted if not relevant.")
    Recurring: str = Field(description="Include a field for recurring rules, such as yearly, monthly, weekly, or daily recurrence. This parameter is optional and can be omitted if not relevant.")
    # Folder: str = Field(description="The folder where the schedule is placed. Users will say 'put in abc', and Folder is abc. This parameter is optional and can be omitted if not applicable.")
    Favorite: bool = Field(description="Include an option to mark the schedule as a favorite. Users might express this action using phrases like 'mark as favorite', 'put in favorite', or simply 'favorite'. This parameter is optional and can be omitted if not applicable.")
    Pin: bool = Field(description="Include an option to pin the schedule. Users might express this action using phrases like 'mark as pinned', 'set as pinned', or simply 'pinned'. This parameter is optional and can be omitted if not applicable.")
    ReminderTime: str = Field(description="Include a field for the reminder time of the schedule, such as 'remind me ten minutes in advance', represented as [\"ten minutes\"]. This parameter is optional and can be omitted if not relevant.")
    Location: str = Field(description="Include a field for the location of the schedule, such as 'create a meeting schedule at 10 am tomorrow at the office', represented as [\"office\"]. This parameter is optional and can be omitted if not relevant.")
    Attendees: list = Field(description="Include a field for the attendees of the schedule, such as 'create a meeting schedule with John and Alice', represented as [\"John\", \"Alice\"]. This parameter is optional and can be omitted if not relevant.")
    FullDay: bool = Field(description="Include a field to indicate whether it is an all-day schedule. This parameter is optional and can be omitted if not relevant.")
    Url: str = Field(description="Include a field for the URL attached to the schedule. This parameter is optional and can be omitted if not relevant.")
    AttachmentID: str = Field(description="Include a field for the attachment ID of the schedule. This parameter is optional and can be omitted if not relevant.")
    Account: str = Field(description="Include a field for the account of the schedule. This parameter is optional and can be omitted if not relevant.")
    Group: str = Field(description="Include a field for the group of the schedule. This parameter is optional and can be omitted if not relevant.")

class ScheduleCreateTool(BaseTool):
    name: str = "ScheduleCreate"
    description: str = "Invoke this when you need to create a schedule. Users might say 'create a schedule', 'add a schedule', or simply 'schedule'. Referring to schedules as 'calendar', like in 'create a calendar', is also acceptable. Always check for the completeness of the date and time. If date and time parameters are missing, prompt the user to provide them. If there is content to be generated or searched before creating the schedule, first call the appropriate generate/search function to obtain the results. If it's unclear whether there is content to be generated or searched, further inquiry is necessary."
    args_schema: Type[BaseModel] = ScheduleCreateInput
    optional_para = ["Note","Recurring","Favorite","Pin","ReminderTime","Location","Attendees","FullDay","Url","AttachmentID","Account","Group"] # optional parameter list

    def _run(elf) -> str:
        return "done"

class ScheduleModifyChdInput(BaseModel):

    Msg: str = Field(description="The content of the created schedule, remove the date and time part of the schedule, only keep the content.")
    Time: str = Field(description="The date and time of the schedule, need specific date and time, if only one date and time is mentioned like 'create a meeting schedule at 10 am tomorrow' noted as [\"tomorrow at 10 am\"], if two date and time are mentioned like 'create a meeting schedule from 10 am to 11 am tomorrow' noted as [\"tomorrow at 10 am\",\"tomorrow at 11 am\"], the first is the start time and the second is the end time.")
    Note: str = Field(description="Include a field for additional information. This parameter is optional and can be omitted if not relevant.")
    Recurring: str = Field(description="Include a field for recurring rules, such as yearly, monthly, weekly, or daily recurrence. This parameter is optional and can be omitted if not relevant.")
    # Folder: str = Field(description="The folder where the schedule is placed. Users will say 'put in abc', and Folder is abc. This parameter is optional and can be omitted if not applicable.")
    Favorite: bool = Field(description="Include an option to mark the schedule as a favorite. Users might express this action using phrases like 'mark as favorite', 'put in favorite', or simply 'favorite'. This parameter is optional and can be omitted if not applicable.")
    Pin: bool = Field(description="Include an option to pin the schedule. Users might express this action using phrases like 'mark as pinned', 'set as pinned', or simply 'pinned'. This parameter is optional and can be omitted if not applicable.")
    ReminderTime: str = Field(description="Include a field for the reminder time of the schedule, such as 'remind me ten minutes in advance', represented as [\"ten minutes\"]. This parameter is optional and can be omitted if not relevant.")
    Location: str = Field(description="Include a field for the location of the schedule, such as 'create a meeting schedule at 10 am tomorrow at the office', represented as [\"office\"]. This parameter is optional and can be omitted if not relevant.")
    Attendees: list = Field(description="Include a field for the attendees of the schedule, such as 'create a meeting schedule with John and Alice', represented as [\"John\", \"Alice\"]. This parameter is optional and can be omitted if not relevant.")
    FullDay: bool = Field(description="Include a field to indicate whether it is an all-day schedule. This parameter is optional and can be omitted if not relevant.")
    Url: str = Field(description="Include a field for the URL attached to the schedule. This parameter is optional and can be omitted if not relevant.")
    AttachmentID: str = Field(description="Include a field for the attachment ID of the schedule. This parameter is optional and can be omitted if not relevant.")
    Account: str = Field(description="Include a field for the account of the schedule. This parameter is optional and can be omitted if not relevant.")
    Group: str = Field(description="Include a field for the group of the schedule. This parameter is optional and can be omitted if not relevant.")

class ScheduleModifyChdTool(BaseTool):
    name: str = "ScheduleModifyChd"
    description: str = "delete"
    args_schema: Type[BaseModel] = ScheduleModifyChdInput
    optional_para = ["Msg","Time","Note","Recurring","Folder","Favorite","Pin","ReminderTime","Location","Attendees","FullDay","Url","AttachmentID","Account","Group"] # ��ѡ�����б�

    def _run(elf) -> str:
        return "done"

class ScheduleModifyInput(BaseModel):
    QueryCondition: str = Field(description="query condition", examples = "ScheduleModifyChd")
    NewContent: str = Field(description="modified new content", examples = "ScheduleModifyChd")

class ScheduleModifyTool(BaseTool):
    name: str = "ScheduleModify"
    description: str = "Called when you need to modify the schedule or add content to previous schedules"
    args_schema: Type[BaseModel] = ScheduleModifyInput
    optional_para = []

    def _run(elf) -> str:
        return "done"

class ScheduleDeleteInput(BaseModel):
    DeleteCondition: str = Field(description="delete condition", examples = "ScheduleModifyChd")

class ScheduleDeleteTool(BaseTool):
    name: str = "ScheduleDelete"
    description: str = "Called when you need to delete a schedule, the user can say 'delete a schedule'"
    args_schema: Type[BaseModel] = ScheduleDeleteInput
    optional_para = []

    def _run(elf) -> str:
        return "done"


class TodoCreateInput(BaseModel):

    Msg: str = Field(description="The content of the created todo, remove the date and time part of the to-do, only keep the content.")
    Time: str = Field(description="The time of the todo,can be ignored,can be a specific date and time, or a broad date, such as 'create a todo for tomorrow at 10 am' is noted as [\"Tomorrow at 10 am\"].")
    Note: str = Field(description="Include a field for additional information. This parameter is optional and can be omitted if not relevant.")
    Recurring: str = Field(description="Include a field for recurring rules, such as yearly, monthly, weekly, or daily recurrence. This parameter is optional and can be omitted if not relevant.")
    Folder: str = Field(description="The folder where the todo is placed. Users will say 'put in abc', and Folder is abc. This parameter is optional and can be omitted if not applicable.")
    Favorite: bool = Field(description="Include an option to mark the todo as a favorite. Users might express this action using phrases like 'mark as favorite', 'put in favorite', or simply 'favorite'. This parameter is optional and can be omitted if not applicable.")
    Pin: bool = Field(description="Include an option to pin the todo. Users might express this action using phrases like 'mark as pinned', 'set as pinned', or simply 'pinned'. This parameter is optional and can be omitted if not applicable.")

class TodoCreateTool(BaseTool):
    name: str = "TodoCreate"
    description: str = "Invoke this when you need to create a to-do item. Users might say 'create a to-do', 'add a to-do', or simply 'to-do'. If content needs to be generated or searched before creating the to-do, ensure you generate/search for this content first. If it is unclear whether there is content to generate or search, further inquiry is necessary."
    args_schema: Type[BaseModel] = TodoCreateInput
    optional_para = ["Note","Recurring","Folder","Favorite","Pin"] # optional parameter list

    def _run(elf) -> str:
        return "done"

class TodoModifyChdInput(BaseModel):

    Msg: str = Field(description="The content of the created todo, remove the date and time part of the to-do, only keep the content.")
    Time: str = Field(description="The time of the todo,can be ignored,can be a specific date and time, or a broad date, such as 'create a todo for tomorrow at 10 am' is noted as [\"Tomorrow at 10 am\"].")
    Note: str = Field(description="Include a field for additional information. This parameter is optional and can be omitted if not relevant.")
    Recurring: str = Field(description="Include a field for recurring rules, such as yearly, monthly, weekly, or daily recurrence. This parameter is optional and can be omitted if not relevant.")
    Folder: str = Field(description="The folder where the todo is placed. Users will say 'put in abc', and Folder is abc. This parameter is optional and can be omitted if not applicable.")
    Favorite: bool = Field(description="Include an option to mark the todo as a favorite. Users might express this action using phrases like 'mark as favorite', 'put in favorite', or simply 'favorite'. This parameter is optional and can be omitted if not applicable.")
    Pin: bool = Field(description="Include an option to pin the todo. Users might express this action using phrases like 'mark as pinned', 'set as pinned', or simply 'pinned'. This parameter is optional and can be omitted if not applicable.")

class TodoModifyChdTool(BaseTool):
    name: str = "TodoModifyChd"
    description: str = "delete"
    args_schema: Type[BaseModel] = TodoModifyChdInput
    optional_para = ["Msg", "Time","Note","Recurring","Folder","Favorite","Pin"]

    def _run(elf) -> str:
        return "done"


class TodoModifyInput(BaseModel):
    QueryCondition: str = Field(description="query condition", examples = "TodoModifyChd")
    NewContent: str = Field(description="modified new content", examples = "TodoModifyChd")

class TodoModifyTool(BaseTool):
    name: str = "TodoModify"
    description: str = "Called when you need to modify or add content to a to-do list"
    args_schema: Type[BaseModel] = TodoModifyInput
    optional_para = []

    def _run(elf) -> str:
        return "done"

class TodoDeleteInput(BaseModel):
    DeleteCondition: str = Field(description="delete condition", examples = "TodoModifyChd")

class TodoDeleteTool(BaseTool):
    name: str = "TodoDelete"
    description: str = "Called when you need to delete a to-do, the user can say 'delete a to-do'"
    args_schema: Type[BaseModel] = TodoDeleteInput
    optional_para = []

    def _run(elf) -> str:
        return "done"


class AIGenerateInput(BaseModel):
    Msg: str = Field(description="The content to be generated")

class AIGenerateTool(BaseTool):
    name: str = "AIGenerate"
    description: str = "Invoke while AI generation tasks such as storytelling, writing novels, creating summaries, etc are needed"
    args_schema: Type[BaseModel] = AIGenerateInput

    def _run(elf) -> str:
        return "done"

class NetworkSearchInput(BaseModel):
    Msg: str = Field(description="The detailed description to be searched, include all relevant information.")

class NetworkSearchTool(BaseTool):
    name: str = "NetworkSearch"
    description: str = "Invoke when content needs to be searched on the network"
    args_schema: Type[BaseModel] = NetworkSearchInput

    def _run(elf) -> str:
        return "done"


