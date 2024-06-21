from typing import Optional, Type, Union, Any

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class ImSendMsgInput(BaseModel):
    App: str = Field(description="发送消息的工具，如果没有提到就忽略这个参数，可忽略参数")
    Receiver: list = Field(
        description="接收消息人的名字；可以是一个接收人，表示为[\"李四\"]；或是一组接收人，表示为[\"小刘\",\"小王\"]")
    Msg: str = Field(description="发送消息的内容")
    Time: list = Field(description="发送消息的时间，表示为[\"晚上8点\"]；可忽略参数")
    Location: list = Field(description="发送消息的地点或位置，表示为[\"望京\"]，可忽略参数")


class ImSendMsgTool(BaseTool):
    name: str = "ImSendMsg"
    description: str = "在你需要发送消息时调用或有位置条件要发消息时调用，如果有发送消息的地点或位置信息，直接放入Location字段中，不要追问具体位置在哪！如：到了香港给我发消息Location为[\"香港\"]"
    args_schema: Type[BaseModel] = ImSendMsgInput
    optional_para = ["App", "Time", "Location"]  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class ImReadMsgInput(BaseModel):
    App: str = Field(description="看消息的工具，没提到就忽略这个参数")
    Sender: list = Field(
        description="你要看消息的人的名字；可以是看一个人/群的消息，表示为[\"小芳芳\"];也可以是多个人/群的消息，表示为[\"小刘\",\"老乡群\"];如果是多级关系，如’老乡群里的小刘‘,表示为[\"老乡群->小刘\"]；没提到就忽略这个参数")
    Type: str = Field(description="如果提到未读就是Unread，没有提到就忽略这个参数")
    Time: list = Field(
        description="看消息的时间，如果是一个时间就表示为[\"这两天\"]；如果是时间范围就表示为:[昨晚十点，今天上午九点]；没提到就忽略这个参数")
    Msg: str = Field(description="想要看的详细内容，没有提到就忽略这个参数")


class ImReadMsgTool(BaseTool):
    name: str = "ImReadMsg"
    description: str = "在你需要看消息时调用；如果有时间需要分析：1、如果是看消息的时间，放入Time字段，2、否则放入Msg字段"
    args_schema: Type[BaseModel] = ImReadMsgInput
    optional_para = ["App", "Sender", "Type", "Time", "Msg"]  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class MessageSearchInput(BaseModel):
    App: str = Field(description="看消息或搜消息的工具，可忽略参数")
    SearchCondition: str = Field(
        description="要搜索的或看到消息的详细描述,需要把搜索相关的信息都放进来，包括上下文信息，不要漏掉任何信息。")
    Sender: list = Field(
        description="看消息或搜消息的人或群；表示为[\"小刘\",\"老乡群\"];如果是多级关系，如’老乡群里的小刘‘,表示为[\"老乡群->小刘\"]；可忽略参数")
    Sign: str = Field(description="消息标记，未读：Unread，已读：Read，未回复：Unrespond，可忽略参数")
    Time: list = Field(
        description="消息发送时间，如果是一个时间就表示为[\"这两天\"]；如果是时间范围就表示为:[昨晚十点，今天上午九点]；可忽略参数")
    Type: str = Field(description="消息类型：文本：Text，图片：Image，视频：Video，语音：Audio，文件：File，可忽略参数")
    Length: str = Field(description="消息长度相关消息，大于50字的为'大于50'，可忽略参数")
    Favorite: bool = Field(description="是否为收藏消息，可忽略参数")
    Pin: bool = Field(description="是否为置顶消息，可忽略参数")
    At: bool = Field(description="是否为@我的消息，可忽略参数")


class MessageSearchTool(BaseTool):
    name: str = "MessageSearch"
    description: str = "在需要进行消息搜索或查看时调用，如：找一下xxx的聊天记录，看一下xxx的消息，搜一下xxx跟我发的内容等，把搜索的详细描述都放到Msg字段，包括上下文信息，不要漏掉任何信息。"
    args_schema: Type[BaseModel] = MessageSearchInput
    optional_para = ["App", "Sender", "Sign", "Time", "Type", "Length", "Favorite", "Pin", "At"]  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class NoteCreateInput(BaseModel):
    Msg: str = Field(description="创建便签的内容")
    Folder: str = Field(description="便签放置的文件夹，用户会说放在xxx中，Folder就是xxx，可忽略参数")
    Favorite: bool = Field(description="便签放置到收藏，用户会说标记为收藏、放入收藏或收藏，可忽略参数")
    Pin: bool = Field(description="将便签置顶，用户会说标记为置顶、设置置顶或置顶，可忽略参数")


class NoteCreateTool(BaseTool):
    name: str = "NoteCreate"
    description: str = "在你需要创建便签时调用，用户可以说'创建一个便签'或'写个便签'或'生成一条便签'或'便签'，如果有需要生成/搜索的内容要先生成/搜索再创建便签，如果不确定是否有生成或搜索的内容需要进一步追问。"
    args_schema: Type[BaseModel] = NoteCreateInput
    optional_para = ["Folder", "Favorite", "Pin"]  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class NoteModifyChdInput(BaseModel):
    Msg: str = Field(description="便签的内容")
    Folder: str = Field(description="便签放置的文件夹，用户会说放在xxx中，Folder就是xxx，可忽略参数")
    Favorite: bool = Field(description="便签放置到收藏，用户会说标记为收藏、放入收藏或收藏，可忽略参数")
    Pin: bool = Field(description="将便签置顶，用户会说标记为置顶、设置置顶或置顶，可忽略参数")


class NoteModifyChdTool(BaseTool):
    name: str = "NoteModifyChd"
    description: str = "delete"  #特殊标记，需要在最终的函数列表里删除
    args_schema: Type[BaseModel] = NoteModifyChdInput
    optional_para = ["Msg", "Folder", "Favorite", "Pin"]  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class NoteModifyInput(BaseModel):
    QueryCondition: str = Field(description="查询条件", examples="NoteModifyChd")  # 这里examples是一个特殊标记，指定用某个函数的参数替换这个值
    NewContent: str = Field(description="修改的新内容", examples="NoteModifyChd")


class NoteModifyTool(BaseTool):
    name: str = "NoteModify"
    description: str = "在你需要修改便签或往便签中添加内容时调用"
    args_schema: Type[BaseModel] = NoteModifyInput
    optional_para = []  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class NoteDeleteInput(BaseModel):
    DeleteCondition: str = Field(description="删除条件", examples="NoteModifyChd")


class NoteDeleteTool(BaseTool):
    name: str = "NoteDelete"
    description: str = "在你需要删除便签时调用，用户可以说‘删除一个便签’"
    args_schema: Type[BaseModel] = NoteDeleteInput
    optional_para = []  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class ScheduleCreateInput(BaseModel):
    Msg: str = Field(description="所创建日程的内容，去掉日程的日期时间部分，只保留内容")
    Time: str = Field(
        description="日程的日期和时间，需要具体的日期和时间,如果只提到一个日期和时间如‘创建明天上午十点的会议日程’记成[\"明天上午10点\"],如果提到两个日期和时间如'创建明天上午十点到11点的会议日程'记成[\"明天上午10点\",\"明天上午11点\"]，前面是开始时间，后面是结束时间")
    Note: str = Field(description="备注信息，可忽略参数")
    Recurring: str = Field(description="循环规则，按年、月、周、日的循环，可忽略参数")
    # Folder: str = Field(description="待办放置的文件夹，用户会说放在xxx中，Folder就是xxx，可忽略参数")
    Favorite: bool = Field(description="待办放置到收藏，用户会说标记为收藏、放入收藏或收藏，可忽略参数")
    Pin: bool = Field(description="将便签置顶，用户会说标记为置顶、设置置顶或置顶，可忽略参数")
    ReminderTime: str = Field(description="日程的提醒时间，如：提前十分钟提醒我,表示为[\"十分钟\"]，可忽略参数")
    Location: str = Field(description="日程的地点，可忽略参数")
    Attendees: str = Field(description="日程的参与人，如：定一个张三和王五的日程，表示为[\"张三\",\"王五\"]，可忽略参数")
    FullDay: bool = Field(description="是否为全天日程，可忽略参数")
    Url: str = Field(description="日程的附带的URL，可忽略参数")
    AttachmentID: str = Field(description="日程的附件ID，可忽略参数")
    Account: str = Field(description="日程账户，可忽略参数")
    Group: str = Field(description="日程组，可忽略参数")


class ScheduleCreateTool(BaseTool):
    name: str = "ScheduleCreate"
    description: str = "在你需要创建日程时调用，用户可以说‘创建一个日程’或者‘添加一个日程’或者‘日程’，日程说成日历也可以，如‘创建一个日历’，一定检查日期和时间的完整性，如果没有日期和时间参数需要询问，如果有需要生成/搜索的内容要先调用生成/搜索函数得到结果再创建日程，如果不确定是否有生成或搜索的内容需要进一步追问。"
    args_schema: Type[BaseModel] = ScheduleCreateInput
    optional_para = ["Note", "Recurring", "Folder", "Favorite", "Pin", "ReminderTime", "Location", "Attendees",
                     "FullDay", "Url", "AttachmentID", "Account", "Group"]  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class ScheduleModifyChdInput(BaseModel):
    Msg: str = Field(description="所创建日程的内容，去掉日程的日期时间部分，只保留内容")
    Time: str = Field(
        description="日程的日期和时间，需要具体的日期和时间,如果只提到一个日期和时间如‘创建明天上午十点的会议日程’记成[\"明天上午10点\"],如果提到两个日期和时间如'创建明天上午十点到11点的会议日程'记成[\"明天上午10点\",\"明天上午11点\"]，前面是开始时间，后面是结束时间")
    Note: str = Field(description="备注信息，可忽略参数")
    Recurring: str = Field(description="循环规则，按年、月、周、日的循环，可忽略参数")
    # Folder: str = Field(description="待办放置的文件夹，用户会说放在xxx中，Folder就是xxx，可忽略参数")
    Favorite: bool = Field(description="待办放置到收藏，用户会说标记为收藏、放入收藏或收藏，可忽略参数")
    Pin: bool = Field(description="将便签置顶，用户会说标记为置顶、设置置顶或置顶，可忽略参数")
    ReminderTime: str = Field(description="日程的提醒时间，如：提前十分钟提醒我,表示为[\"十分钟\"]，可忽略参数")
    Location: str = Field(description="日程的地点，可忽略参数")
    Attendees: str = Field(description="日程的参与人，如：定一个张三和王五的日程，表示为[\"张三\",\"王五\"]，可忽略参数")
    FullDay: bool = Field(description="是否为全天日程，可忽略参数")
    Url: str = Field(description="日程的附带的URL，可忽略参数")
    AttachmentID: str = Field(description="日程的附件ID，可忽略参数")
    Account: str = Field(description="日程账户，可忽略参数")
    Group: str = Field(description="日程组，可忽略参数")


class ScheduleModifyChdTool(BaseTool):
    name: str = "ScheduleModifyChd"
    description: str = "delete"  #特殊标记，需要在最终的函数列表里删除
    args_schema: Type[BaseModel] = ScheduleModifyChdInput
    optional_para = ["Msg", "Time", "Note", "Recurring", "Folder", "Favorite", "Pin", "ReminderTime", "Location",
                     "Attendees", "FullDay", "Url", "AttachmentID", "Account", "Group"]  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class ScheduleModifyInput(BaseModel):
    QueryCondition: str = Field(description="查询条件",
                                examples="ScheduleModifyChd")  # 这里examples是一个特殊标记，指定用某个函数的参数替换这个值
    NewContent: str = Field(description="修改的新内容", examples="ScheduleModifyChd")


class ScheduleModifyTool(BaseTool):
    name: str = "ScheduleModify"
    description: str = "在你需要修改日程或往日程中添加内容时调用"
    args_schema: Type[BaseModel] = ScheduleModifyInput
    optional_para = []  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class ScheduleDeleteInput(BaseModel):
    DeleteCondition: str = Field(description="删除条件", examples="ScheduleModifyChd")


class ScheduleDeleteTool(BaseTool):
    name: str = "ScheduleDelete"
    description: str = "在你需要删除日程时调用，用户可以说‘删除一个日程’"
    args_schema: Type[BaseModel] = ScheduleDeleteInput
    optional_para = []  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class TodoCreateInput(BaseModel):
    Msg: str = Field(description="所创建待办的内容，去掉待办的日期时间部分，只保留内容")
    Time: str = Field(
        description="待办的时间,可以忽略,可以是具体的日期时间，也可以是宽泛的日期,格式如下‘创建明天上午十点的待办’记成[\"明天上午10点\"]")
    Note: str = Field(description="备注信息，可忽略参数")
    Recurring: str = Field(description="循环规则，按年、月、周、日的循环，可忽略参数")
    Folder: str = Field(description="待办放置的文件夹，用户会说放在xxx中，Folder就是xxx，可忽略参数")
    Favorite: bool = Field(description="待办放置到收藏，用户会说标记为收藏、放入收藏或收藏，可忽略参数")
    Pin: bool = Field(description="将便签置顶，用户会说标记为置顶、设置置顶或置顶，可忽略参数")


class TodoCreateTool(BaseTool):
    name: str = "TodoCreate"
    description: str = "在你需要创建待办时调用，用户可以说‘创建一个待办’或者‘添加一个待办’或者‘待办’，如果有需要生成/搜索的内容要先生成/搜索再创建待办，如果不确定是否有生成或搜索的内容需要进一步追问。"
    args_schema: Type[BaseModel] = TodoCreateInput
    optional_para = ["Time", "Note", "Recurring", "Folder", "Favorite", "Pin"]  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class TodoModifyChdInput(BaseModel):
    Msg: str = Field(description="待办的内容，去掉待办的日期时间部分，只保留内容")
    Time: str = Field(
        description="待办的时间,可以忽略,可以是具体的日期时间，也可以是宽泛的日期,格式如下‘明天上午十点的待办’记成[\"明天上午10点\"]")
    Note: str = Field(description="备注信息，可忽略参数")
    Recurring: str = Field(description="循环规则，按年、月、周、日的循环，可忽略参数")
    Folder: str = Field(description="待办放置的文件夹，用户会说放在xxx中，Folder就是xxx，可忽略参数")
    Favorite: bool = Field(description="待办放置到收藏，用户会说标记为收藏、放入收藏或收藏，可忽略参数")
    Pin: bool = Field(description="将便签置顶，用户会说标记为置顶、设置置顶或置顶，可忽略参数")


class TodoModifyChdTool(BaseTool):
    name: str = "TodoModifyChd"
    description: str = "delete"  #特殊标记，需要在最终的函数列表里删除
    args_schema: Type[BaseModel] = TodoModifyChdInput
    optional_para = ["Msg", "Time", "Note", "Recurring", "Folder", "Favorite", "Pin"]  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class TodoModifyInput(BaseModel):
    QueryCondition: str = Field(description="查询条件", examples="TodoModifyChd")  # 这里examples是一个特殊标记，指定用某个函数的参数替换这个值
    NewContent: str = Field(description="修改的新内容", examples="TodoModifyChd")


class TodoModifyTool(BaseTool):
    name: str = "TodoModify"
    description: str = "在你需要修改待办或往待办中添加内容时调用"
    args_schema: Type[BaseModel] = TodoModifyInput
    optional_para = []  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class TodoDeleteInput(BaseModel):
    DeleteCondition: str = Field(description="删除条件", examples="TodoModifyChd")


class TodoDeleteTool(BaseTool):
    name: str = "TodoDelete"
    description: str = "在你需要删除待办时调用，用户可以说‘删除一个待办’"
    args_schema: Type[BaseModel] = TodoDeleteInput
    optional_para = []  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class AIGenerateInput(BaseModel):
    Msg: str = Field(description="要生成内容的描述")


class AIGenerateTool(BaseTool):
    name: str = "AIGenerate"
    description: str = "在需要内容生成时调用，例如讲故事、写小说、做总结等，把详细的描述都放到Msg字段，包括上下文信息，不要漏掉任何信息。"
    args_schema: Type[BaseModel] = AIGenerateInput

    def _run(elf) -> str:
        return "done"


class NetworkSearchInput(BaseModel):
    Msg: str = Field(description="要搜索的详细描述,需要把搜索相关的信息都放进来。")


class NetworkSearchTool(BaseTool):
    name: str = "NetworkSearch"
    description: str = "在需要对内容进行网络搜索时调用，把搜索的详细描述都放到Msg字段，包括上下文信息，不要漏掉任何信息。"
    args_schema: Type[BaseModel] = NetworkSearchInput

    def _run(elf) -> str:
        return "done"


class ContactCreateInput(BaseModel):
    first_name: str = Field(description="新建联系人的first name")
    middle_name: str = Field(description="新建联系人的middle name")
    last_name: str = Field(description="新建联系人的last name")
    contact_avatar: str = Field(description="新建联系人的头像图片")
    phone_number: str = Field(description="新建联系人的电话号码，允许多条手机号数据")
    email: str = Field(description="邮箱地址和标签,允许多条邮箱数据")
    iMessage: str = Field(description="iMessage关联的手机号或者邮箱")
    WhatsApp: str = Field(description="WhatsApp关联的手机号")
    Facebook_Messenger: str = Field(description="Facebook Messenger的名字或Facebook主页链接")
    MicrosoftTeams: str = Field(description="Microsoft Teams的账号")
    Google_Chat: str = Field(description="Google Chat的账号")
    Slack: str = Field(description="Slack的账号")
    birthday: str = Field(description="新建联系人的生日年月日或月日")
    address: str = Field(description="地址和标签，允许多条数据")
    company: str = Field(description="联系人所在公司名称")
    note: str = Field(description="针对该联系人的补充描述")
    URL: str = Field(description="联系人的个人网站等相关URL和标签，允许多条数据")
    custom_fields: str = Field(description="任意自定义字段，允许多条数据")


class ContactCreateTool(BaseTool):
    name: str = "ContactCreate"
    description: str = "在需要创建联系人时调用，在通讯录里创建一个新的联系人,并为联系人添加个人信息和联系方式。"
    args_schema: Type[BaseModel] = ContactCreateInput
    optional_para = ["first_name", "middle_name", "last_name", "contact_avatar", "phone_number", "email", "iMessage",
                     "WhatsApp", "Facebook_Messenger", "MicrosoftTeams", "Google_Chat", "Slack", "birthday", "address",
                     "company", "note", "URL", "custom_fields"]  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class ContactSearchInput(BaseModel):
    first_name: str = Field(description="新建联系人的first name")
    middle_name: str = Field(description="新建联系人的middle name")
    last_name: str = Field(description="新建联系人的last name")
    contact_avatar: str = Field(description="新建联系人的头像图片")
    phone_number: str = Field(description="新建联系人的电话号码，允许多条手机号数据")
    email: str = Field(description="邮箱地址和标签,允许多条邮箱数据")
    iMessage: str = Field(description="iMessage关联的手机号或者邮箱")
    WhatsApp: str = Field(description="WhatsApp关联的手机号")
    Facebook_Messenger: str = Field(description="Facebook Messenger的名字或Facebook主页链接")
    MicrosoftTeams: str = Field(description="Microsoft Teams的账号")
    Google_Chat: str = Field(description="Google Chat的账号")
    Slack: str = Field(description="Slack的账号")
    birthday: str = Field(description="新建联系人的生日年月日或月日")
    address: str = Field(description="地址和标签，允许多条数据")
    company: str = Field(description="联系人所在公司名称")
    note: str = Field(description="针对该联系人的补充描述")
    URL: str = Field(description="联系人的个人网站等相关URL和标签，允许多条数据")
    ContactType: str = Field(description="联系人的类型:通讯录联系人、组织联系人和保存到通讯录的群聊联系类型")
    ContactSource: str = Field(description="联系人来源:手机通讯录,手动添加")
    Star: str = Field(description="是否为星标联系人,Boolean")
    Block: str = Field(description="是否是黑名单,Boolean")
    CommonGroupChat: str = Field(description="共同群聊的名称,允许多条数据")
    LastContactTime: str = Field(description="最后一次发送/收到消息距今时间，")
    CreationTime: str = Field(description="创建时间")
    ContactLabel: str = Field(description="预设/智能标签")


class ContactSearchTool(BaseTool):
    name: str = "ContactSearch"
    description: str = "根据用户提供的信息在通讯录中查找匹配的联系人,返回值应当是匹配的联系人ID的列表储存在contact_id中等待其他函数调用。"
    args_schema: Type[BaseModel] = ContactSearchInput
    optional_para = ["first_name", "middle_name", "last_name", "contact_avatar", "phone_number", "email", "iMessage",
                     "WhatsApp", "Facebook_Messenger", "MicrosoftTeams", "Google_Chat", "Slack", "birthday", "address",
                     "company", "note", "URL", "ContactType", "ContactSource", "Star", "Block", "CommonGroupChat",
                     "LastContactTime", "CreationTime", "ContactLabel"]  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class ContactDeleteInput(BaseModel):
    contact_id: str = Field(description="要删除联系人的id，允许多条数据", emaples="ContactInfoModifyChd")


class ContactDeleteTool(BaseTool):
    name: str = "ContactDelete"
    description: str = "在需要删除联系人时调用，根据联系人的id删除联系人"
    args_schema: Type[BaseModel] = ContactDeleteInput
    optional_para = []  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class ContactBlockInput(BaseModel):
    contact_id: str = Field(description="要拉黑的联系人的id,值唯一")
    contact_methods: str = Field(description="联系方式，如手机号、邮箱等，允许多条数据")


class ContactBlockTool(BaseTool):
    name: str = "ContactBlock"
    description: str = "在需要拉黑联系人时调用，根据联系人的id将通讯录中某个联系人的一个或部分联系方式拉黑"
    args_schema: Type[BaseModel] = ContactBlockInput
    optional_para = ["contact_methods"]  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class ContactInfoAddInput(BaseModel):
    contact_id: str = Field(description="要添加联系人信息的联系人id,值唯一")
    contact_information_add: str = Field(description="需要添加的联系人信息字段，如手机号、邮箱等，允许多条数据")


class ContactInfoAddTool(BaseTool):
    name: str = "ContactInfoAdd"
    description: str = "在需要添加联系人信息时调用，为一个已保存的联系人添加一条或多条基础信息或联系方式"
    args_schema: Type[BaseModel] = ContactInfoAddInput
    optional_para = []  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class ContactInfoModifyChdInput(BaseModel):
    contact_id: str = Field(description="要修改联系人信息的联系人id,值唯一")
    first_name: str = Field(description="新建联系人的first name")
    middle_name: str = Field(description="新建联系人的middle name")
    last_name: str = Field(description="新建联系人的last name")
    contact_avatar: str = Field(description="新建联系人的头像图片")
    phone_number: str = Field(description="新建联系人的电话号码，允许多条手机号数据")
    email: str = Field(description="邮箱地址和标签,允许多条邮箱数据")
    iMessage: str = Field(description="iMessage关联的手机号或者邮箱")
    WhatsApp: str = Field(description="WhatsApp关联的手机号")
    Facebook_Messenger: str = Field(description="Facebook Messenger的名字或Facebook主页链接")
    MicrosoftTeams: str = Field(description="Microsoft Teams的账号")
    Google_Chat: str = Field(description="Google Chat的账号")
    Slack: str = Field(description="Slack的账号")
    birthday: str = Field(description="新建联系人的生日年月日或月日")
    address: str = Field(description="地址和标签，允许多条数据")
    company: str = Field(description="联系人所在公司名称")
    note: str = Field(description="针对该联系人的补充描述")
    URL: str = Field(description="联系人的个人网站等相关URL和标签，允许多条数据")
    custom_fields: str = Field(description="任意自定义字段，允许多条数据")
    star: bool = Field(description="是否为星标联系人,Boolean")


class ContactInfoModifyChdTool(BaseTool):
    name: str = "ContactInfoModifyChd"
    description: str = "delete"  # 特殊标记，需要在最终的函数列表里删除
    args_schema: Type[BaseModel] = ContactInfoModifyChdInput
    optional_para = ["first_name", "middle_name", "last_name", "contact_avatar", "phone_number", "email", "iMessage",
                     "WhatsApp", "Facebook_Messenger", "MicrosoftTeams", "Google_Chat", "Slack", "birthday", "address",
                     "company", "note", "URL", "custom_fields", "star"]  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class ContactInfoModifyInput(BaseModel):
    QueryCondition: str = Field(description="查询条件",
                                examples="ContactInfoModifyChd")  # 这里examples是一个特殊标记，指定用某个函数的参数替换这个值
    NewContent: str = Field(description="修改的新内容", examples="ContactInfoModifyChd")


class ContactInfoModifyTool(BaseTool):
    name: str = "ContactInfoModify"
    description: str = "在需要修改联系人信息时调用，修改一个联系人的基础信息、星标状态或联系方式等信息"
    args_schema: Type[BaseModel] = ContactInfoModifyInput
    optional_para = []  # 可选参数列表

    def _run(elf) -> str:
        return "done"


class ContactInfoDeleteInput(BaseModel):
    contact_id: str = Field(description="要删除联系人信息的联系人id,值唯一")
    contact_information_add: str = Field(description="需要删除的联系人信息字段，如手机号、邮箱等，允许多条数据")


class ContactInfoDeleteTool(BaseTool):
    name: str = "ContactInfoDelete"
    description: str = "在需要删除联系人信息时调用，为一个已保存的联系人删除一条或多条基础信息或联系方式"
    args_schema: Type[BaseModel] = ContactInfoDeleteInput
    optional_para = []  # 可选参数列表

    def _run(elf) -> str:
        return "done"


# class GroupChatSaveInput:
#     GroupChatID: str = Field(description="要保存的群聊ID，允许多条数据")
#
#
# class GroupChatSaveTool(BaseTool):
#     name: str = "GroupChatSave"
#     description: str = "在需要保存一个或多个群聊到通讯录时调用，根据群聊的ID保存群聊"
#     args_schema: Type[BaseModel] = GroupChatSaveInput
#     optional_para = []  # optional parameter list
#
#     def _run(elf) -> str:
#         return "done"

class ContactMergeInput(BaseModel):
    contact_id: str = Field(description="要合并的联系人ID，至少需要两条或以上数据")

class ContactMergeTool(BaseTool):
    name: str = "ContactMerge"
    description: str = "在需要合并联系人时调用，根据联系人的ID合并两个或多个联系人到一个联系人中"
    args_schema: Type[BaseModel] = ContactMergeInput
    optional_para = []  # optional parameter list

    def _run(elf) -> str:
        return "done"