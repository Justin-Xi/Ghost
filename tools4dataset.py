import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Type, Union

import requests
import websockets
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class ImSendMsgInput(BaseModel):
    App: str = Field(description="发送消息的工具，如果没有提到就忽略这个参数，忽略这个参数不影响函数调用。")
    Receiver: list = Field(description="接收消息人的名字；可以是一个接收人，表示为[\"李四\"]；或是一组接收人，表示为[\"小刘\",\"小王\"]；")
    Msg: str = Field(description="发送消息的内容")


class ImSendMsgTool(BaseTool):
    name: str = "ImSendMsg"
    description: str = "在你需要发送消息时调用，需要发送的消息如果有条件，要看清这个条件，符合条件再发送。"
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

class ImWatchMsgInput(BaseModel):
    App: str = Field(description="看消息的工具，没有提到就忽略这个参数")
    Sender: list = Field(description="你要看消息的人的名字；可以是看一个人的消息，表示为[\"小芳芳\"];也可以是多个人的消息，表示为[\"小刘\",\"小王\"]；如果没有提到看谁发的消息就忽略这个参数")
    Type: str = Field(description="如果提到未读就是Unread，没有提到就忽略这个参数")
    Time: list = Field(description="看消息的时间，如果是一个时间就表示为[\"这两天\"]；如果是时间范围就表示为:[昨晚十点，今天上午九点]；如果没有提到时间就忽略这个参数；")


class ImWatchMsgTool(BaseTool):
    name: str = "ImWatchMsg"
    description: str = "在你需要看消息时调用"
    args_schema: Type[BaseModel] = ImWatchMsgInput
    optional_para = ["App","Sender","Type","Time"] # 可选参数列表

    def _run(
        self,
        App: str,
        Sender: str,
        Type: str,
        Time: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        result = ""
        print(f"ImWatchMsgTool: App:{App}, Sender:{Sender}, Type:{Type},Time:{Time}")
        return "done"


class NotesCreateInput(BaseModel):

    Msg: str = Field(description="所创建便签的内容,比如‘创建便签，列出需要整理的文件和归档方式’就是’列出需要整理的文件和归档方式‘")



class NotesCreateTool(BaseTool):
    name: str = "NotesCreate"
    description: str = "在你需要创建便签时调用，可以是创建一个便签或者写个便签或者生成一条便签或者便签"
    args_schema: Type[BaseModel] = NotesCreateInput

    def _run(
        self,

        Msg: str,
    ) -> str:
        """Use the tool."""
        result = ""
        print(f"NotesCreateTool: Msg:{Msg}")
        return "done"



class ScheduleCreateInput(BaseModel):

    Msg: str = Field(description="所创建日程的内容,比如‘创建明天上午十点的会议日程。’就是‘会议‘，要把‘明天上午十点’忽略，再比如‘建立日程提醒我周五团建’就是’团建‘")
    Time: str = Field(description="所创日程的时间,比如‘创建明天上午十点的会议日程’就是明天上午十点,'设置每周一和周四早上8点到9点的团队讨论会议日程'就是每周一和周四早上8点到9点")


class ScheduleCreateTool(BaseTool):
    name: str = "ScheduleCreate"
    description: str = "在你需要创建日程时调用，可以是创建一个日程或者建个日程或者添加一个日程或者日程"
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


class LocalOrderInput(BaseModel):

    Msg: str = Field(description="所要查看订单的内容,需要总结一下，比如‘给我看看这几天我吃麻辣烫花了多少钱’就是我吃麻辣烫花了多少钱，'帮我看看昨天的菜单'就是‘我的菜单’")
    Time: Optional[str] = Field(description="所要查看订单的时间,1、如果是时间范围就要用时间区间表示，比如’看看我周一到周四喝奶茶花了多少钱‘时间就是[周一，周四]；2、如果不是时间范围就只写指定时间，比如‘帮我看看我这几天都吃了些什么’时间就是这几天，或者‘帮我查一下最近的菜单’时间就是‘最近’；3、如果没有提到时间就忽略这个参数")


class LocalOrderTool(BaseTool):
    name: str = "LocalOrder"
    description: str = "在明确需要查看美团订单时调用，可以是查看菜单或者看看菜单，如果只说查一下账单不要调用"
    args_schema: Type[BaseModel] = LocalOrderInput

    def _run(
        self,

        Msg: str,
        Time: Optional[str],

    ) -> str:
        """Use the tool."""
        result = ""
        print(f"LocalOrderTool: Msg:{Msg},Time:{Time}")
        return "done"



class SearchCreateMessageInput(BaseModel):

        Msg: str = Field(description="搜索消息的内容,比如‘帮我在网上搜索鱼香肉丝的烹饪流程。’就是鱼香肉丝的烹饪流程")
class SearchCreateMessageTool(BaseTool):
        name: str = "SearchCreate"
        description: str = "在你需要搜索信息时调用,可以是搜索一个信息或者查找一个信息"
        args_schema: Type[BaseModel] = SearchCreateMessageInput

        def _run(
                self,

                Msg: str,
                run_manager: Optional[CallbackManagerForToolRun] = None,
        ) -> str:
            """Use the tool."""
            result = ""
            print(f"SearchCreateMessageTool:Msg:{Msg}")
            return "done"

class BotCreateCreateInput(BaseModel):
            Msg: str = Field(description="聊天内容，1.例如在旅行时，如何更好地体验当地文化？那么聊天的内容就是‘在旅行时，如何更好地体验当地文化？’这句话2.例如你认为时间管理的重要性是什么？有什么好的方法可以提高效率吗？，那么聊天内容就是'你认为时间管理的重要性是什么？有什么好的方法可以提高效率吗？'这一整句话")

class BotCreateCreateTool(BaseTool):
            name: str = "BotCreate"
            description: str = "在你需要聊天时调用，例如如何准备一份出色的简历和面试？"
            args_schema: Type[BaseModel] = BotCreateCreateInput

            def _run(
                    self,

                    Msg: str,
                    run_manager: Optional[CallbackManagerForToolRun] = None,
            ) -> str:
                """Use the tool."""
                result = ""
                print(f"BotCreateCreateTool: Msg:{Msg}")
                return "done"

class SnsShareMessageInput(BaseModel):
                App: Optional[str] = Field(
                    description="分享消息的工具，如果提到用微博分享消息就是微博，抖音消息就是抖音,没有提到就忽略这个参数")
                Msg: str = Field(description="分享消息的内容")


class SnsShareMessageTool(BaseTool):
    name: str = "SnsShare"
    description: str = "在你需要分享消息时调用，可以是分享微博消息或分享抖音消息或只是说分享消息例如把这个工作报告文件上传到我的 LinkedIn 职业网络，同时写一段评论，介绍一下我们项目团队的成就。也属于分享消息，发布也属于分享消息"
    args_schema: Type[BaseModel] = SnsShareMessageInput

    def _run(
            self,
            App: Optional[str],
            Msg: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        result = ""
        print(f"SnsShareMessageTool:Msg:{Msg}, App:{App}")
        return "done"

class TakeoutSearchInput(BaseModel):
            App: Optional[str] = Field(
                description="点外卖的工具，1、如果提到用饿了么点外卖，工具就是饿了么，2.如果提到用美团，工具就写美团外卖3如果没有参数，工具就写成‘外卖’.例如找两家评价好，服务好的餐厅，分别点个招牌菜。工具就写成外卖。例如在798附近帮我买一份汉堡。例如点一份牛肉汉堡。App就写成'外卖'")
            Msg: str = Field(
                description="点外卖的内容，1.例如点一份汉堡，不要辣的，价格在30元以内，内容就是点一份汉堡，不要辣的。2.我想吃麻辣烫，不要辣，三十块钱以内。内容就写麻辣烫，不要辣。例如明天朋友来，在美团上点份烤鸭和几个家常菜，少辣，100元左右。内容就是’点份烤鸭和几个家常菜，少辣‘")
            Location: Optional[str] = Field(
                description="地点\附近。不要以null的形式输出。如果写地点，地点就写地点。例如想吃披萨，美团CBD那家不错，地点就写CBD。如果写地点附近，就只用写地点。例如在798附近帮我买一份汉堡，地点\附近就写成地点是’798‘。没有明确标地点，地点就默认写成附近。例如帮我在美团上点份汉堡，不要辣的，速度快点。地点就写成附近。")
            Range: Optional[str] = Field(
                description="范围，不要以null的形式输出。提到几公里以内范围就是几公里以内1.例如别超过两公里，范围就是两公里内。2.没有提到参数就忽略不计")
            OrderBy: Optional[str] = Field(
                description="指的是排序方式(评价好、送餐快)不要以null的形式输出。1.例如找家粤菜或日料，服务和评价好的，排序就写评价好，服务好。2.例如外卖送到我公司，速度快点。排序就写速度快。没有参数就忽略不计")
            Limit: Optional[str] = Field(
                description="指的是数量限制，不要以null的形式输出。1.例如请打开美团，找两家餐厅，数量就是2。没有参数就忽略不计，")
            Price: Optional[str] = Field(
                description="指的是价格[小,大]，不要以null的形式输出。1.例如你能打开饿了么帮我点一份烤鸭吗？三十块钱以内，价格就是[0元,30元].2.例如价格在大概30元左右.价格就写成30元左右。")


class TakeoutSearchTool(BaseTool):
    name: str = "TakeoutSearch"
    description: str = "在你需要点外卖调用，可以是点饿了么外卖,或者是美团外卖,或只是说点外卖"
    args_schema: Type[BaseModel] = TakeoutSearchInput

    def _run(
            self,
            App: Optional[str],
            Msg: str,
            Location: str,
            Range: str,
            OrderBy: str,
            Limit: str,
            Price: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        result = ""
        print(
            f"TakeoutSearchTool: Msg:{Msg}, App:{App},Location:{Location},Range:{Range},OrderBy:{OrderBy},Limit:{Limit},Price:{Price}")
        return "done"

class LocalCateringSearchInput(BaseModel):
            App: Optional[str] = Field(
                description="用来搜索地方的工具：如果没有提到App，工具就写Loca1.App:美团本地，大众点评.例如打开美团，查找附近的中餐厅，工具就写‘美团本地’，例如大众点评，工具就写大众点评。2.如果没有提到，工具就写Local,例如找找附近有啥好吃的,工具就是'Local'")
            Msg: str = Field(
                description="搜索的内容：我想吃望京小腰，看看附近有没有比较好的，帮我推荐两家，内容就是望京小腰。看看望京附近有啥好吃的，特色餐馆，一公里以内，评价高的，内容就是好吃的，特色餐馆")
            Location: Optional[str] = Field(
                description="地点\附近。地点和附近只能写一个1.例如请帮我看看附近有什么好吃的，地点就是附近。2.想在世贸天阶附近找一家有特色的中餐厅.地点就是世贸天阶3.没有提点准确的地名，地点就写附近。")
            Range: Optional[str] = Field(
                description="范围，提到几公里以内范围就是几公里以内没有提到参数就不写，不要以null的形式输出，1.例如别超过两公里，范围就是两公里内。2.没有提到参数就忽略不计例如看看798附近有啥好吃的中餐，例如推荐一下东直门附近的高档餐厅啊，就可以不写")
            OrderBy: Optional[str] = Field(
                description="指的是排序方式(评价好)1.例如找家粤菜或日料，服务和评价好的，排序就写评价好，服务好。没有参数就不写，")
            Limit: Optional[str] = Field(
                description="指的是数量限制，1.例如请打开美团，找两家餐厅，数量就是2。没有参数就不写，")
            Price: Optional[str] = Field(
                description="指的是价格便宜，适中，贵和[小,大]，不要以null的形式输出1.例如三十块钱以内，价格就是[0元,30元].2例如给我找一个好吃的餐厅，价格不要太贵.价格就写价格适中，价格便宜就写价格便宜。没有提到参数就不写，")


class LocalCateringSearchTool(BaseTool):
    name: str = "LocalCateringSearch"
    description: str = "在你需要搜索地点时调用，可以是找一家餐厅，或者我想去哪家餐厅，或者推荐一下餐厅"
    args_schema: Type[BaseModel] = LocalCateringSearchInput

    def _run(
            self,
            App: Optional[str],
            Msg: str,
            Location: str,
            Range: str,
            OrderBy: str,
            Limit: str,
            Price: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        result = ""
        print(
            f"LocalCateringSearchTool: Msg:{Msg}, App:{App},Location:{Location},Range:{Range},OrderBy:{OrderBy},Limit:{Limit},Price:{Price}")
        return "done"


class HotelSearchInput(BaseModel):
    App: Optional[str] = Field(description="指的是搜索住宿的的工具，1、如果提到用美团搜索就是美团，用携程搜索就是携程,比如’在携程看看哪个酒店现在离我三公里不到’工具就是‘携程’。2、如果没有指定工具就忽略这个参数")
    Msg: str = Field(description="指的是搜索住宿的的内容，需要总结一下。1、比如‘想定一个附近的高级套间，帮我在携程上定一下，明天晚上九点入住’总结一下就是’定一个高级套间‘；2、’帮我定一个明天两点半入住的酒店‘总结一下就是’帮我定一个酒店‘；3、’在携程看一下离我距离最近的汉庭酒店，今晚十点入住，后天下午两点退房‘总结一下就是’查看一下汉庭酒店‘；4、‘明天要出差了，美团上有哪些酒店既经济实惠又干净整洁呢’就是‘搜索一下经济实惠又干净整洁的酒店’")
    Time: Optional[str] = Field( description="指的是搜索住宿的时间；1、如果是时间范围就要用时间区间表示，比如’在携程看一下离我距离最近的汉庭酒店，今晚十点入住，后天下午两点退房‘时间就是[今晚十点，后天下午两点]；2、如果不是时间范围就只写指定时间，比如‘帮我在美团上找个周五入住的酒店’时间就是周五，或者‘国庆去北京旅游，有哪些酒店推荐入住呢’时间就是国庆；3、如果没有提到时间就忽略这个参数")
    Location: Optional[str] = Field(description="指的是搜索住宿的位置,1、如果提到‘附近’或者’距离最近‘就是附近，比如‘附近有高级套房吗‘位置就是附近;2、如果提到具体地点就是这个地点，比如’想去三亚旅游，帮我定一个评价最好的酒店‘位置就是三亚，比如’找个离望京公园不超过3公里的酒店‘位置就是望京公园；3、如果没有提到位置就忽略这个参数")
    Range: Optional[str] = Field(description="指的是搜索住宿的范围,例如1、’在携程看看哪个酒店现在离我三公里不到'范围就是三公里内。2、没有提到范围就忽略这个参数，比如’国庆去北京旅游，有哪些酒店推荐入住呢‘就只用写位置是北京而不用写范围")
    OrderBy: Optional[str] = Field(description="指的是搜索住宿的的排序方式，1、如果提到评价好就是评价好，如果提到距离近就是距离近；2、如果都没有提到就忽略这个参数")
    Limit: Optional[str] = Field(description="指的是搜索住宿的数量，1、预定两间双人间或者预定两个单人间或者预定两个商务套房就都是2；2、定个、定一个、定间、找个都是1；3、没有提到明确数量就忽略这个参数")
    Price: Optional[str] = Field(description="指的是搜索住宿的价格；1、如果是价格范围就要用价格区间表示，比如‘帮我在美团上找个300到500元的酒店’价格就是[300元,500元]；2、如果不是价格范围就只写指定价格，比如‘帮我在美团上找个300元左右的酒店’价格就是300元左右。3、如果没有提到价格就忽略这个参数")
    RoomType: Optional[str] = Field(description="指的是搜索住宿的房间类型，包括单人间、双人间、标间、大床房、豪华间、商务间、行政间、套间、高级套房等；1、比如‘想定一个附近的高级套间，帮我在携程上定一下，明天晚上九点入住’就是‘高级套间’。2、如果没有指定房间类型就忽略这个参数，而不要以null形式输出")

class HotelSearchTool(BaseTool):
    name: str = "HotelSearch"
    description: str = "在明确需要搜索住宿时调用，可以是查看附近酒店或者看看酒店或者定一个双人间或者定个套房或者帮我预定房间"
    args_schema: Type[BaseModel] = HotelSearchInput

    def _run(
        self,
        App: Optional[str],
        Msg: str,
        Time: Optional[str],
        Location: Optional[str],
        Range: Optional[str],
        OrderBy: Optional[str],
        Limit: Optional[str],
        Price: Optional[str],
        RoomType: Optional[str],

    ) -> str:
        """Use the tool."""
        result = ""
        print(f"HotelSearchTool: App:{App},Msg:{Msg},Time:{Time},Location:{Location},Range:{Range},OrderBy:{OrderBy},Limit:{Limit},Price:{Price},RoomType:{RoomType}")
        return "done"



class LocalMovieSearchInput(BaseModel):
    App: Optional[str] = Field(description="指的是搜索电影或者电影院的的工具，1、如果提到用美团本地搜索就是美团本地，用大众点评搜索就是大众点评；2、如果没有提到用美团本地搜索或者用大众点评搜索那就是Local；比如’替我在大众点评上检索一下最近评分最高的电影’工具就是‘大众点评’；而‘帮我看看我附近一公里以内都有什么电影院，想看电影啦’工具就是‘Local'")
    Msg: str = Field(description="指的是搜索电影或者电影院的的内容，需要总结一下。1、比如‘帮我看看我附近一公里以内都有什么电影院，想看电影啦’总结一下就是’查找电影院‘；2、’好想看《肖申克的救赎》！明天附近有电影院上映吗，帮我找找‘总结一下就是’查找上映《肖申克的救赎》的电影院‘；3、’好无聊啊，海淀哪家电影院环境比较好，要评价高一点的，想看电影了‘总结一下就是’查找环境好、评价高的电影院‘；4、‘现在离我最近的电影院是哪个，帮我在美团本地上找找看’就是‘搜索一下离我最近的电影院’：5、‘帮我买两张明晚八点在万达影城播出的电影的票’总结一下就是‘买电影票’")
    Time: Optional[str] = Field( description="指的是搜索电影或者电影院的时间；比如‘可以在美团本地上帮我买今晚八点在万达影城上映的《长安三万里》吗’时间就是今晚八点，或者‘国庆想去看电影，有哪些电影推荐观看呢’时间就是国庆，或者‘这几天有什么比较好看的片子上映吗’时间就是这几天；3、如果没有提到时间就忽略这个参数，而不要以null形式输出")
    Location: Optional[str] = Field(description="指的是搜索电影或者电影院的位置,1、如果提到‘附近’或者’距离最近‘就是附近，比如‘附近有评价好一点的电影院吗‘位置就是附近;2、如果提到具体地点就是这个地点，比如’想去万达影城看电影，帮我买张票’位置就是万达影城，比如’找个离望京公园不超过3公里的电影院‘位置就是望京公园；3、如果没有提到位置就忽略这个参数")
    Range: Optional[str] = Field(description="指的是搜索电影或者电影院的范围,例如1、’在大众点评上看看哪个电影院现在离我三公里不到'范围就是三公里内，或者’离我五公里内的电影院今晚九点都有哪些影片上映呢，在美团本地帮我查一下‘范围就是五公里内。2、没有提到范围就忽略这个参数，比如’国庆想去看电影，有哪些电影推荐观看呢‘就不用写范围")
    OrderBy: Optional[str] = Field(description="指的是搜索电影或者电影院的的排序方式，1、如果提到评价好或者评价高就是评价好，如果提到距离近或者距离最近就是距离近；2、如果都没有提到就忽略这个参数，而不要以null形式输出")
    Limit: Optional[str] = Field(description="指的是搜索电影或者电影院的数量，1、找两个评价好的电影院或者找两个离我比较近的电影院或者买两张电影票就都是2；2、定个、定一个、定张、买张、找个、找家就都是1，而查找哪个、哪家就忽略数量这个参数；3、找几家评价好的电影院或者找几部评价比较高的影片就是几家或者几部；4、没有提到明确数量就忽略这个参数，而不要以null形式输出")
    Price: Optional[str] = Field(description="指的是搜索电影或者电影院的价格；1、如果是价格范围就要用价格区间表示，比如‘帮我在美团上找个票价40到70元的电影院’价格就是[40元,70元]；2、如果不是价格范围就只写指定价格，比如‘帮我在美团上找个票价50元左右的电影院’价格就是50元左右。3、如果没有提到价格就忽略这个参数，而不要以null形式输出")
    MovieType: Optional[str] = Field(description="指的是搜索电影的影片类型，包括动作片、喜剧片、剧情片、悬疑片、恐怖片、爱情片、历史片、记录片、科幻片、动画片、战争片等；1、比如‘朝阳区电影院有新出的悬疑片吗？帮我找一下！’就是‘悬疑片’，比如’帮我找两部历史题材的影片‘就是’历史片‘。2、如果没有指定房间类型就忽略这个参数，而不要以null形式输出")

class LocalMovieSearchTool(BaseTool):
    name: str = "LocalMovieSearch"
    description: str = "在明确需要搜索电影或者电影院时调用，可以是查看附近电影院或者看看电影或者预定一张电影票或者买几张电影票或者推荐几部电影"
    args_schema: Type[BaseModel] = LocalMovieSearchInput

    def _run(
        self,
        App: Optional[str],
        Msg: str,
        Time: Optional[str],
        Location: Optional[str],
        Range: Optional[str],
        OrderBy: Optional[str],
        Limit: Optional[str],
        Price: Optional[str],
        MovieType: Optional[str],

    ) -> str:
        """Use the tool."""
        result = ""
        print(f"LocalMovieSearchTool: App:{App},Msg:{Msg},Time:{Time},Location:{Location},Range:{Range},OrderBy:{OrderBy},Limit:{Limit},Price:{Price},MovieType:{MovieType}")
        return "done"

class ImMeetingCreateInput(BaseModel):
            App: Optional[str] = Field(
                description="指的是创建会议，可以是创建飞书会议，也可以是创建腾讯会议，例如‘安排一场飞书会议’，app就写‘飞书会议’")
            Time: Optional[str] = Field(
                description="指的是开会的时间，1.例如'帮我安排一个飞书会议，时间定在下周二下午3点到5点'，时间就是下周二下午三点到五点。2.例如创建腾讯会议，同时邀请王晶晶和李董一起参加，时间就定在周五下午五点半，持续时间为一个小时。时间就写‘周五下午五点半，持续时间为一个小时’3.例如可不可以建立一个腾讯会议，议题是探讨企业文化建设，参会人是孙倩倩和我，时间就定在周五下午吧，找一个时间，参会时长是两小时。时间就写‘周五下午，找一个时间，参会时长是两小时’")
            MeetingRoom: Optional[str] = Field(
                description="指的是会议地点，不要以null的形式出现1.例如'通知崔元，杨广到202会议室参会'，会议地点就写‘202’如果没有出现这个参数就忽略不计")
            People: Optional[str] = Field(
                description="指的是参会人,格式必须是‘[陈红,刘冬]’如果有‘我’的话就写‘myself’；多个人就以名字列表表示，1.比如‘同时邀请赵三和王铁柱与我一起参会’就是‘[赵三,王铁柱]’,2.例如'能不能邀请赵老师和高老师在周四下午三点去203参加会议'，就写‘[赵老师,高老师]’")
            Title: Optional[str] = Field(
                description="指的是议题，不要以null的形式出现1.例如‘我想开个会议，就创一个飞书会议吧。同时邀请赵三和王铁柱与我一起参会，会议时间在一点到三点，议题为人的发展’，议题就写‘人的发展’，2.例如‘主要讨论新产品推广策略’，议题就写‘新产品推广策略’3.例如我们来探讨下季度市场策略。议题就是‘下季度市场策略’如果没有这个参数就忽略不计")
class ImMeetingCreateTool(BaseTool):
        name: str = "ImMeetingCreate"
        description: str = "在明确需要创建会议时调用，可以是创建会议，安排会议，开会议，建立会议"
        args_schema: Type[BaseModel] = ImMeetingCreateInput

        def _run(
                self,
                App: Optional[str],
                Time: Optional[str],
                MeetingRoom: Optional[str],
                People: Optional[str],
                Title: Optional[str],

        ) -> str:
            """Use the tool."""
            result = ""
            print(
                f"ImMeetingCreateTool: App:{App},Time:{Time},MeetingRoom:{MeetingRoom},People:{People},Title:{Title}")
            return "done"


