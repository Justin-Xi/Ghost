# -*- coding:utf-8 -*-
# author:xiajiayi
# datetime:2024/1/24 13:37
# software: PyCharm
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.chat_models import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ChatMessage, SystemMessage, FunctionMessage, ToolMessage
from langchain_core.prompts import SystemMessagePromptTemplate, ChatPromptTemplate, PromptTemplate, MessagesPlaceholder, \
    HumanMessagePromptTemplate
import tools as custom_tools

# init tools
weather = custom_tools.WhetherTool()
we_chat_send_msg = custom_tools.WechatSendMessageTool()
we_chat_read_msg = custom_tools.WechatReadMessageTool()
we_chat_create_group = custom_tools.WechatCreateGroupTool()
we_chat_read_group_msg = custom_tools.WechatReadGroupChatTool()
time = custom_tools.TimeTool()
note = custom_tools.NoteTool()
meeting = custom_tools.MeetingTool()
reminder = custom_tools.CreateReminderTool()
mail = custom_tools.ReadLatestMailTool()
search = custom_tools.SearchTool()
send_feishu_message = custom_tools.SendFeishuMessageTool()
schedule_lark_meeting_tool = custom_tools.ScheduleLarkMeetingTool()
delete_lark_meeting_tool = custom_tools.DeleteLarkMeetingTool()
tools = [
    we_chat_send_msg,
    we_chat_read_msg,
    we_chat_create_group,
    we_chat_read_group_msg,
    send_feishu_message,
    time,
    reminder,
    mail,
    search,
    schedule_lark_meeting_tool,
    delete_lark_meeting_tool
]

GPT_35_DISPLAY = "GPT3.5"
GPT_35_16K_DISPLAY = "GPT3.5 16K"
GPT_4_DISPLAY = "GPT4"
GPT_4_32K_DISPLAY = "GPT4 32K"
GPT_4_Turbo_DISPLAY = "GPT4 Turbo"
GPT_4_Turbo_VISION_DISPLAY = "GPT4 Turbo Vision"

display_deployment_dict = {
    GPT_35_DISPLAY: "gpt35",
    GPT_35_16K_DISPLAY: "gpt35-16k",
    GPT_4_DISPLAY: "gpt4",
    GPT_4_32K_DISPLAY: "gpt4-32k",
    GPT_4_Turbo_DISPLAY: "gpt4turbo",
    GPT_4_Turbo_VISION_DISPLAY: "gpt4turbo-vision"
}
# init agent
gpt4Model = AzureChatOpenAI(
    deployment_name="gpt4turbo", openai_api_version="2023-12-01-preview"
)

gpt4vModel = AzureChatOpenAI(
    deployment_name="gpt4turbo-vision", openai_api_version="2023-12-01-preview"
)

prompt = ChatPromptTemplate(
    input_variables=['agent_scratchpad', 'input'],
    input_types={
        'chat_history': [AIMessage, HumanMessage, ChatMessage, SystemMessage, FunctionMessage, ToolMessage],
        'agent_scratchpad': [AIMessage, HumanMessage, ChatMessage, SystemMessage, FunctionMessage, ToolMessage]
    },
    messages=[
        SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[],
                                                          template='你的角色是个人助理，你需要一步一步来完成被吩咐的事项。当遇到有时间相关的请求时，你一定要先通过给定的时间函数获取当前的时间，然后再进行下一步操作。不要使用在线搜索')),
        MessagesPlaceholder(variable_name='chat_history', optional=True),
        HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}')),
        MessagesPlaceholder(variable_name='agent_scratchpad')
    ]
)


def predict(question, history=[]) -> dict:
    """
    调用模型预测
    :param question: 用户的输入
    :param history: 历史上下文
    :return: 模型的输出
    """
    once_agent = create_openai_functions_agent(
        llm=gpt4Model,
        tools=tools,
        prompt=prompt
    )

    agentExec = AgentExecutor(
        agent=once_agent, tools=tools, verbose=True
    )
    agentExec.handle_parsing_errors = True
    invoke_data = {
        "input": question,
        "chat_history": history
    }
    ret = agentExec.invoke(invoke_data)
    return ret


if __name__ == '__main__':
    memory = [
        HumanMessage(content="hi! my name is bob"),
        AIMessage(content="Hello Bob! How can I assist you today?"),
    ]
    # print(predict("创建一个待办：今晚买菜", memory))
    print(predict("查看一下微信李四的未读消息，把这些消息总结一下微信发给张三，飞书发给李四", memory))
