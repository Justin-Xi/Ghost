import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Type

import requests
import websockets
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

global_websocket: websockets = None

global_func_address = "ws://10.60.200.240:8100"


# global_func_address = "ws://autofunc:8000"


class ScheduleLarkMeetingInput(BaseModel):
    summary: str = Field(description="The summary of the meeting")
    description: str = Field(description="The description of the meeting")
    start_time: str = Field(description="The earliest time to start the meeting")
    end_time: str = Field(description="The latest time to end the meeting")
    duration: str = Field(description="The duration of the meeting", default="30")
    users: str = Field(description="The users to invite to the meeting")
    # 设置所有参数为必须的


class ScheduleLarkMeetingTool(BaseTool):
    name: str = "schedule_feishu_meeting"
    description: str = "useful for when you need to schedule Feishu meeting to someone. "
    args_schema: Type[BaseModel] = ScheduleLarkMeetingInput

    def _run(
            self,
            summary: str,
            description: str,
            start_time: str,
            end_time: str,
            duration: str,
            users: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        result = ""
        print("ScheduleLarkMeetingTool")
        return "done"

        def connect_websocket():
            nonlocal result

            async def host_connect():
                nonlocal result
                url = f"{global_func_address}/function/run"
                async with websockets.connect(url) as websocket:
                    await websocket.send(
                        json.dumps(
                            {
                                "running_id": "run123456",
                                "host_id": HOST_ID,
                                "func_id": "ltd.loox.feishu.meeting.new@1",
                                "args": {
                                    "summary": summary,
                                    "description": description,
                                    "start_time": start_time,
                                    "end_time": end_time,
                                    "duration": duration,
                                    "users": users,
                                    "timezone_offset_hours": 8,
                                },
                            }
                        )
                    )
                    while True:
                        response = await websocket.recv()
                        data = json.loads(response)
                        print(f"Response: {data}")
                        if "running_id" in data or data["result"] != 0:
                            result = f"{data}"
                            break

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(host_connect())
            loop.close()

        connect_websocket()
        if result:
            return result
        return "done"

    async def _arun(
            self,
            summary: str,
            description: str,
            start_time: str,
            end_time: str,
            duration: str,
            users: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("ScheduleLarkMeetingTool does not support async")


class DeleteLarkMeetingInput(BaseModel):
    event_id: str = Field(description="The id of the meeting to be deleted")
    # 设置所有参数为必须的


class DeleteLarkMeetingTool(BaseTool):
    name: str = "delete_feishu_meeting"
    description: str = "useful for when you need to delete Feishu meeting. "
    args_schema: Type[BaseModel] = DeleteLarkMeetingInput

    def _run(
            self,
            event_id: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        result = ""
        print("DeleteLarkMeetingTool")
        return "done"

        def connect_websocket():
            nonlocal result

            async def host_connect():
                nonlocal result
                url = f"{global_func_address}/function/run"
                async with websockets.connect(url) as websocket:
                    await websocket.send(
                        json.dumps(
                            {
                                "running_id": "run123456",
                                "host_id": HOST_ID,
                                "func_id": "ltd.loox.feishu.meeting.delete@1",
                                "args": {
                                    "event_id": event_id,
                                },
                            }
                        )
                    )
                    while True:
                        response = await websocket.recv()
                        data = json.loads(response)
                        print(f"Response: {data}")
                        if "running_id" in data or data["result"] != 0:
                            result = f"{data}"
                            break

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(host_connect())
            loop.close()

        connect_websocket()
        if result:
            return result
        return "done"

    async def _arun(
            self,
            event_id: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("DeleteLarkMeetingTool does not support async")


class SendFeishuMessageInput(BaseModel):
    context: str = Field()
    user: str = Field()
    message: str = Field()


class SendFeishuMessageTool(BaseTool):
    name: str = "send_feishu_message"
    description: str = "useful for when you need to send Feishu message to someone. 'context' is the context of the message, like 'shrugged his shoulders', '脸上带着微笑', '尴尬而不失礼貌' and so on."
    args_schema: Type[BaseModel] = SendFeishuMessageInput

    def _run(
        self,
        context: str,
        user: str,
        message: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        result = ""
        print(f"SendFeishuMessageTool: user:{user}, message:{message}")
        return "done"

        def connect_websocket():
            nonlocal result

            async def host_connect():
                nonlocal result
                url = f"{global_func_address}/function/run"
                async with websockets.connect(url) as websocket:
                    await websocket.send(
                        json.dumps(
                            {
                                "running_id": "run123456",
                                "host_id": HOST_ID,
                                "func_id": "ltd.loox.feishu.send_message@1",
                                "args": {"delegate": "功夫熊猫", "context": context, "user": user, "message": message},
                            }
                        )
                    )
                    while True:
                        response = await websocket.recv()
                        data = json.loads(response)
                        print(f"Response: {data}")
                        if "running_id" in data or data["result"] != 0:
                            result = f"{data}"
                            break

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(host_connect())
            loop.close()

        connect_websocket()
        if result:
            return result
        return "done"

    async def _arun(
        self, context: str, user: str, message: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("SendFeishuMessageTool does not support async")


class SearchInput(BaseModel):
    serach_keywords: str = Field()


class SearchTool(BaseTool):
    name: str = "search"
    description: str = "useful for when you need to search something using search engine"
    args_schema: Type[BaseModel] = SearchInput

    def _run(
        self,
        serach_keywords: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        result = ""
        print("SearchTool")
        return "done"

        def connect_websocket():
            nonlocal result

            async def host_connect():
                nonlocal result
                url = f"{global_func_address}/function/run"
                async with websockets.connect(url) as websocket:
                    await websocket.send(
                        json.dumps(
                            {
                                "running_id": "run123456",
                                "host_id": HOST_ID,
                                "func_id": "ltd.loox.macos.safari.search_the_web@1",
                                "args": {"search_keywords": serach_keywords},
                            }
                        )
                    )
                    while True:
                        response = await websocket.recv()
                        print("Response: ", response)
                        data = json.loads(response)
                        if "running_id" in data or data["result"] != 0:
                            result = f"{data}"
                            break

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(host_connect())
            loop.close()

        connect_websocket()
        if result:
            return result
        return "done"

    async def _arun(self, serach_keywords: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("SearchTool does not support async")


class MailInput(BaseModel):
    pass


class ReadLatestMailTool(BaseTool):
    name: str = "read_latest_email"
    description: str = "useful for when you need to read the latest email"
    args_schema: Type[BaseModel] = MailInput

    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        result = ""
        print("ReadLatestMailTool")
        return "done"

        def connect_websocket():
            nonlocal result

            async def host_connect():
                nonlocal result
                url = f"{global_func_address}/function/run"
                async with websockets.connect(url) as websocket:
                    await websocket.send(
                        json.dumps(
                            {
                                "running_id": "run123456",
                                "host_id": HOST_ID,
                                "func_id": "ltd.loox.macos.mail.latest@1",
                                "args": {"key": "value"},
                            }
                        )
                    )
                    while True:
                        response = await websocket.recv()
                        print("Response: ", response)
                        data = json.loads(response)
                        if "running_id" in data or data["result"] != 0:
                            result = f"{data}"
                            break

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(host_connect())
            loop.close()

        connect_websocket()
        if result:
            return result
        return "done"

    async def _arun(self, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("ReadLatestMailTool does not support async")


class CreateReminderInput(BaseModel):
    category: str = Field()
    content: str = Field()
    should_set_remind_time: bool = Field()
    remind_time: Optional[str] = Field()


HOST_ID = "AA5C-0FB4-0725"


class CreateReminderTool(BaseTool):
    name: str = "create_reminder"
    description: str = "useful for when you need to create a reminder. if should set remind time, remind_time must be a meaningful time, with format '%Y-%m-%d %H:%M:%S' "
    args_schema: Type[BaseModel] = CreateReminderInput

    def _run(
        self,
        category: str,
        content: str,
        should_set_remind_time: bool,
        remind_time: Optional[str],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        result = ""
        print("CreateReminderTool",category, remind_time)
        return "done"

        def connect_websocket():
            nonlocal result

            async def host_connect():
                nonlocal result
                url = f"{global_func_address}/function/run"
                async with websockets.connect(url) as websocket:
                    send_data = {
                        "list_name": category,
                        "title_name": content,
                        "should_set_reminder_time": should_set_remind_time,
                    }

                    if should_set_remind_time:
                        dt = datetime.strptime(remind_time, "%Y-%m-%d %H:%M:%S")
                        remind_time_year = dt.year
                        remind_time_month = dt.month
                        remind_time_day = dt.day
                        remind_time_hour = dt.hour
                        remind_time_minute = dt.minute
                        remind_time_second = dt.second
                        send_data["year_value"] = remind_time_year
                        send_data["month_value"] = remind_time_month
                        send_data["day_value"] = remind_time_day
                        send_data["hour_value"] = remind_time_hour
                        send_data["minute_value"] = remind_time_minute
                        send_data["second_value"] = remind_time_second
                    await websocket.send(
                        json.dumps(
                            {
                                "running_id": "run123456",
                                "host_id": HOST_ID,
                                "func_id": "ltd.loox.macos.reminders.new@1",
                                "args": send_data,
                            }
                        )
                    )
                    while True:
                        response = await websocket.recv()
                        print("Response: ", response)
                        data = json.loads(response)
                        if "running_id" in data:
                            result = f"{data['message']}"
                            break

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(host_connect())
            loop.close()

        connect_websocket()
        if result:
            return result
        return "done"

    async def _arun(
        self,
        category: str,
        content: str,
        should_set_remind_time: bool,
        remind_time: Optional[str],
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("CreateReminderTool does not support async")


class WechatSendMessageInput(BaseModel):
    id: str = Field()
    content: str = Field()


class WechatSendMessageTool(BaseTool):
    name: str = "weixin_send_message"
    description: str = "useful for when you need to send message to others using weixin(微信)"
    args_schema: Type[BaseModel] = WechatSendMessageInput
    # weachat_url: str = "http://47.117.67.9:5000/sessions"

    def _run(
        self,
        id: str,
        content: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        print("WechatSendMessageTool:", content)
        return "done"
        return self._perform(user_name, content)

    def _perform(
        self,
        id: str,
        content: str,
    ) -> str:
        result = ""

        def connect_websocket():
            nonlocal result

            async def host_connect():
                nonlocal result
                url = f"{global_func_address}/function/run"
                async with websockets.connect(url) as websocket:
                    send_data = {"name": id, "message": content}
                    await websocket.send(
                        json.dumps(
                            {
                                "running_id": "run123456",
                                "host_id": HOST_ID,
                                "func_id": "ltd.loox.wechat.send_message@1",
                                "args": send_data,
                            }
                        )
                    )
                    while True:
                        response = await websocket.recv()
                        print("Response: ", response)
                        data = json.loads(response)
                        if "running_id" in data:
                            result = f"{data['message']}"
                            break

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(host_connect())
            loop.close()

        connect_websocket()
        if result:
            return result
        return "done"

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("wechat does not support async")


class WechatReadMessageInput(BaseModel):
    id: str = Field()


class WechatReadMessageTool(BaseTool):
    name: str = "weixin_read_message"
    description: str = "useful for when you need to read messages from single contact within weixin(微信)"
    args_schema: Type[BaseModel] = WechatReadMessageInput
    # weachat_url: str = "http://47.117.67.9:5000/sessions"

    def _run(
        self,
        id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        print("WechatReadMessageTool")
        return "你好吗"
        return self._perform(id)

    def _perform(
        self,
        id: str,
    ) -> str:
        result = ""

        def connect_websocket():
            nonlocal result

            async def host_connect():
                nonlocal result
                url = f"{global_func_address}/function/run"
                async with websockets.connect(url) as websocket:
                    send_data = {"name": id}
                    await websocket.send(
                        json.dumps(
                            {
                                "running_id": "run123456",
                                "host_id": HOST_ID,
                                "func_id": "ltd.loox.wechat.read_chat@1",
                                "args": send_data,
                            }
                        )
                    )
                    while True:
                        response = await websocket.recv()
                        print("Response: ", response)
                        data = json.loads(response)
                        if "running_id" in data:
                            result = f"{data['message']}"
                            break

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(host_connect())
            loop.close()

        connect_websocket()
        if result:
            return result
        return "done"

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("wechat does not support async")


class WechatCreateGroupInput(BaseModel):
    users: str = Field()
    group_name: str = Field()


class WechatCreateGroupTool(BaseTool):
    name: str = "weixin_create_group"
    description: str = "useful for when you need to create a chat group(群) within weixin(微信), all names must be separated by a vertical bar (|). For example, '张三|李四|王五' "
    args_schema: Type[BaseModel] = WechatCreateGroupInput
    # weachat_url: str = "http://47.117.67.9:5000/sessions"

    def _run(
        self,
        users: str,
        group_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        print("WechatCreateGroupTool")
        return "done"
        return self._perform(users, group_name)

    def _perform(self, users: str, group_name: str) -> str:
        result = ""

        def connect_websocket():
            nonlocal result

            async def host_connect():
                nonlocal result
                url = f"{global_func_address}/function/run"
                async with websockets.connect(url) as websocket:
                    send_data = {"name": group_name, "users": users}
                    await websocket.send(
                        json.dumps(
                            {
                                "running_id": "run123456",
                                "host_id": HOST_ID,
                                "func_id": "ltd.loox.wechat.create_group@1",
                                "args": send_data,
                            }
                        )
                    )
                    while True:
                        response = await websocket.recv()
                        print("Response: ", response)
                        data = json.loads(response)
                        if "running_id" in data:
                            result = f"{data['message']}"
                            break

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(host_connect())
            loop.close()

        connect_websocket()
        if result:
            return result
        return "done"

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("wechat does not support async")


class WechatReadGroupChatInput(BaseModel):
    group_name: str = Field()


class WechatReadGroupChatTool(BaseTool):
    name: str = "weixin_read_group_chat"
    description: str = "useful for when you need to read chat history from group(群) within weixin(微信). "
    args_schema: Type[BaseModel] = WechatReadGroupChatInput
    # weachat_url: str = "http://47.117.67.9:5000/sessions"

    def _run(
        self,
        group_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        print("WechatReadGroupChatTool", group_name)
        return "ha ha ha !"
        return self._perform(group_name)

    def _perform(self, group_name: str) -> str:
        result = ""

        def connect_websocket():
            nonlocal result

            async def host_connect():
                nonlocal result
                url = f"{global_func_address}/function/run"
                async with websockets.connect(url) as websocket:
                    send_data = {"name": group_name}
                    await websocket.send(
                        json.dumps(
                            {
                                "running_id": "run123456",
                                "host_id": HOST_ID,
                                "func_id": "ltd.loox.wechat.read_group_chat@1",
                                "args": send_data,
                            }
                        )
                    )
                    while True:
                        response = await websocket.recv()
                        print("Response: ", response)
                        data = json.loads(response)
                        if "running_id" in data:
                            result = f"{data['message']}"
                            break

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(host_connect())
            loop.close()

        connect_websocket()
        if result:
            return result
        return "done"

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("wechat does not support async")


class WhetherInput(BaseModel):
    city: str = Field()


class WhetherTool(BaseTool):
    name: str = "weather"
    description: str = "useful for when you need to check the current temperature"
    args_schema: Type[BaseModel] = WhetherInput

    def _run(
        self,
        city: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        print("WhetherTool")
        return "done"
        return self._perform(city)

    def _perform(self, city: str, **tool_kwargs) -> str:
        weather_str = f"""https://api.seniverse.com/v3/weather/now.json?key=SujpBm2YMxDnzNfNv&location={city}&language=zh-Hans&unit=c"""
        r = requests.get(url=weather_str)
        if "results" in r.json():
            txt = r.json()["results"][0]["now"]["text"]
            temperature = r.json()["results"][0]["now"]["temperature"]
            return f"{txt}，温度{temperature}"
        elif "status" in r.json():
            return r.json()["status"]
        else:
            return "未知错误"

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("whether does not support async")


class NoteInput(BaseModel):
    content: str = Field()


class NoteTool(BaseTool):
    name: str = "note"
    description: str = "useful for when you need to note something"
    args_schema: Type[BaseModel] = NoteInput

    def _run(
        self,
        content: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        print("NoteTool")
        return "done"
        return self._perform(content)

    def _perform(self, content: str, **tool_kwargs) -> str:
        return "done"

    async def _arun(self, content: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("note does not support async")


class TimeInput(BaseModel):
    pass


class TimeTool(BaseTool):
    name: str = "time"
    description: str = "useful for when you need to know the current time"
    args_schema: Type[BaseModel] = TimeInput

    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        print("TimeTool")
        return self._perform()

    def _perform(self, **tool_kwargs) -> str:
        beijing = timezone(timedelta(hours=8))
        utc_time = datetime.utcnow()
        return utc_time.astimezone(beijing)

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("time does not support async")


class MeetingInput(BaseModel):
    when: str = Field()
    title: str = Field()


class MeetingTool(BaseTool):
    name: str = "meeting"
    description: str = "useful for when you need to schedule a new meeting"
    args_schema: Type[BaseModel] = MeetingInput

    def _run(
        self,
        when: str,
        title: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        print("MeetingTool")
        return "done"
        return self._perform(when, title)

    def _perform(self, when: str, title: str, **tool_kwargs) -> str:
        return "done"

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("meeting does not support async")
