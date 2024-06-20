import copy

from langchain_core.utils.function_calling import convert_to_openai_function

def funcs(custom_tools):
    im_send_msg = custom_tools.ImSendMsgTool()
    im_read_msg = custom_tools.ImReadMsgTool()
    note_create = custom_tools.NoteCreateTool()
    note_modifychd = custom_tools.NoteModifyChdTool()
    note_modify = custom_tools.NoteModifyTool()
    note_del = custom_tools.NoteDeleteTool()
    schedule_create = custom_tools.ScheduleCreateTool()
    schedule_modifychd = custom_tools.ScheduleModifyChdTool()
    schedule_modify = custom_tools.ScheduleModifyTool()
    schedule_del = custom_tools.ScheduleDeleteTool()
    todo_create = custom_tools.TodoCreateTool()
    todo_modifychd = custom_tools.TodoModifyChdTool()
    todo_modify = custom_tools.TodoModifyTool()
    todo_del = custom_tools.TodoDeleteTool()
    ai_generate = custom_tools.AIGenerateTool()
    network_search = custom_tools.NetworkSearchTool()
    message_search = custom_tools.MessageSearchTool()
    contact_create = custom_tools.ContactCreateTool()
    contact_search = custom_tools.ContactSearchTool()
    contact_delete = custom_tools.ContactDeleteTool()
    contact_block = custom_tools.ContactBlockTool()
    contact_info_add = custom_tools.ContactInfoAddTool()
    contact_info_modifychd = custom_tools.ContactInfoModifyChdTool()
    contact_info_modify = custom_tools.ContactInfoModifyTool()
    contact_info_delete = custom_tools.ContactInfoDeleteTool()
    # groupchat_save = custom_tools.GroupChatSaveTool()
    contact_merge = custom_tools.ContactMergeTool()

    tools = [
        im_send_msg,
        # im_read_msg,
        message_search,
        note_create,
        note_modifychd,
        note_modify,
        note_del,
        schedule_create,
        schedule_modifychd,
        schedule_modify,
        schedule_del,
        todo_create,
        todo_modifychd,
        todo_modify,
        todo_del,
        ai_generate,
        network_search,
        contact_create,
        contact_search,
        contact_delete,
        contact_block,
        contact_info_add,
        contact_info_modifychd,
        contact_info_modify,
        contact_info_delete,
        # groupchat_save,
        contact_merge
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

def get_func_by_name(functions, name):
    for func in functions:
        if func['name'] == name:
            return func
    return None

def replace_examples_to_chd_json(functions):
    for func in functions:
        if 'parameters' in func and 'properties' in func['parameters']:
            properties = func['parameters']['properties']
            for key in properties:
                if 'examples' in properties[key]:
                    chg_func = get_func_by_name(functions, properties[key]['examples'])
                    if chg_func is None:
                        print("error function not find:", properties[key]['examples'])
                        continue
                    properties[key]['type'] = "object"
                    properties[key]['properties'] = copy.deepcopy(chg_func['parameters']['properties'])
                    del properties[key]['examples']
        pass
    return functions
def delete_useless_func(functions):
    len_funcs = len(functions)
    for idx in reversed(range(len_funcs)):
        if "description" in functions[idx] and functions[idx]["description"] == "delete":
            del functions[idx]
    return functions
def funcs_json(custom_tools):
    tools = funcs(custom_tools)
    functions = [cvt_to_openai_function(t) for t in tools]
    functions = replace_examples_to_chd_json(functions)
    functions = delete_useless_func(functions)
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
