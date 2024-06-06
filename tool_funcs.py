import copy

from langchain_core.utils.function_calling import convert_to_openai_function

def funcs(custom_tools):
    im_send_msg = custom_tools.ImSendMsgTool()
    im_read_msg = custom_tools.ImReadMsgTool()
    note_create = custom_tools.NoteCreateTool()
    schedule_create = custom_tools.ScheduleCreateTool()
    todo_create = custom_tools.TodoCreateTool()
    ai_generate = custom_tools.AIGenerateTool()
    network_search = custom_tools.NetworkSearchTool()
    message_search = custom_tools.MessageSearchTool()

    tools = [
        im_send_msg,
        im_read_msg,
        note_create,
        schedule_create,
        todo_create,
        ai_generate,
        network_search,
        message_search,
    ]
    return tools

def cvt_to_openai_function(t):
    t2 = convert_to_openai_function(t)
    t3 = copy.deepcopy(t2)
    if 'optional_para' in vars(t) and 'parameters' in t2 and 'required' in t2['parameters']:
        for para in t2['parameters']['required']:
            if para in t.optional_para:
                t3['parameters']['required'].remove(para)
    return t3

def funcs_json(custom_tools):
    tools = funcs(custom_tools)
    functions = [cvt_to_openai_function(t) for t in tools]
    return functions

def del_func_paras(functions, is_train=False):
    for f in functions:
        del f['description']
        if is_train:
            f['parameters']['properties'].clear()
            f['parameters']['required'].clear()
        else:
            del f['parameters']
        # del f['parameters']['type']
