import tkinter as tk
from tkinter import messagebox

def input_show(title="请输入标题"):
    def get_input():
        root.destroy()

    root = tk.Tk()
    root.title(title)

    # tk_text = tk.Text(root)
    tk_text = tk.Entry(root)
    tk_text.pack(padx=20, pady=20, ipadx=200, ipady=5)

    button = tk.Button(root, text='提交', command=get_input)
    button.pack(padx=20, pady=5, ipadx=50)
    root.mainloop()
    return tk_text.get()

def msg_box(text="内容展示", cancel_bt="取消", ok_bt="确定", title="请选择"):
    def ok_rt():
        rt.append("ok")
        root.destroy()
    def cancel_rt():
        root.destroy()

    rt = []
    root = tk.Tk()
    root.title(title)

    tk_label = tk.Label(root, text=text)
    tk_label.pack(padx=20, pady=30, ipadx=50)

    button_ok = tk.Button(root, text=ok_bt, command=ok_rt)
    button_ok.pack(side=tk.LEFT, padx=100, pady=20, ipadx=50)

    button_cancel = tk.Button(root, text=cancel_bt, command=cancel_rt)
    button_cancel.pack(side=tk.RIGHT, padx=100, pady=20, ipadx=50)

    root.mainloop()
    return "ok" in rt

def msg_box_2button(text="内容展示", bt0=["按钮0","bt0"], bt1=["按钮1","bt1"], title="请选择"):
    def bt_rt0():
        rt.append(bt_text[0])
        root.destroy()
    def bt_rt1():
        rt.append(bt_text[1])
        root.destroy()

    bt_text = [bt0[1],bt1[1]]
    rt = []
    root = tk.Tk()
    root.title(title)

    tk_label = tk.Label(root, text=text)
    tk_label.pack(padx=20, pady=30, ipadx=50)

    button0 = tk.Button(root, text=bt0[0], command=bt_rt0)
    button0.pack(side=tk.LEFT, padx=50, pady=20, ipadx=50)

    button1 = tk.Button(root, text=bt1[0], command=bt_rt1)
    button1.pack(side=tk.LEFT, padx=50, pady=20, ipadx=50)

    root.mainloop()
    return rt[0]

def msg_box_3button(text="内容展示", bt0=["按钮0","bt0"], bt1=["按钮1","bt1"], bt2=["按钮2","bt2"], title="请选择"):
    def bt_rt0():
        rt.append(bt_text[0])
        root.destroy()
    def bt_rt1():
        rt.append(bt_text[1])
        root.destroy()
    def bt_rt2():
        rt.append(bt_text[2])
        root.destroy()

    bt_text = [bt0[1],bt1[1],bt2[1]]
    rt = []
    root = tk.Tk()
    root.title(title)

    tk_label = tk.Label(root, text=text)
    tk_label.pack(padx=20, pady=30, ipadx=50)

    button0 = tk.Button(root, text=bt0[0], command=bt_rt0)
    button0.pack(side=tk.LEFT, padx=50, pady=20, ipadx=50)

    button1 = tk.Button(root, text=bt1[0], command=bt_rt1)
    button1.pack(side=tk.LEFT, padx=50, pady=20, ipadx=50)

    button2 = tk.Button(root, text=bt2[0], command=bt_rt2)
    button2.pack(side=tk.LEFT, padx=50, pady=20, ipadx=50)

    root.mainloop()
    return rt[0]

def get_input(tk_text, root):
    print(tk_text.get('0.0','end'))
    root.quit()

def input_test(title="请输入标题"):

    def on_text_change(event):
        print("Text changed to:")

    def create_sub_window(root):
        # 创建子窗口
        sub_window = tk.Toplevel(root)
        # 设置子窗口的标题
        sub_window.title("子窗口")
        sub_window.attributes("-topmost", True)
        sub_window.grab_set()
        # 在子窗口中添加一个标签
        label = tk.Label(sub_window, text="这是一个子窗口5555555555555555555555555555555555")
        label.pack()
        # root.mainloop()

    root = tk.Tk()
    root.title(title)
    create_sub_window(root)

    tk_text = tk.Text(root)
    # tk_text = tk.Entry(root)
    tk_text.pack(padx=20, pady=20, ipadx=200, ipady=5)
    tk_text.insert('insert', "123")
    tk_text.bind("<Key>", on_text_change)
    # tk_text.bind("<Return>", on_text_change)

    button = tk.Button(root, text='提交', command=lambda:create_sub_window(root))
    button.pack(padx=20, pady=5, ipadx=50)

    root.mainloop()
    return

if __name__ == '__main__':
    xxx = input_test()
    print("")