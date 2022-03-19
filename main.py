# -*- coding: utf-8 -*-
import platform
import time
import wx
import random
import os

# from win32ctypes import win32api

from arxml2dbc.switchFile import convert

APP_TITLE = u'ARXML文件转换DBC工具'
APP_ICON = './resources/switch_16.png'
TMP_PATH = "/tmp/template.docx"
ITEM_ICON = "./resources/file.png"
OUTPUT_PATH = "./output"

WILD_CARD = u"Python 文件 (*.py)|*.py|" \
            u"编译的 Python 文件 (*.pyc)|*.pyc|" \
            u" 垃圾邮件文件 (*.spam)|*.spam|" \
            "Egg file (*.egg)|*.egg|" \
            "All files (*.*)|*.*"


class mainFrame(wx.Frame):
    """程序主窗口类，继承自wx.Frame"""
    id_open = wx.NewIdRef(count=1)
    id_save = wx.NewIdRef(count=1)
    id_quit = wx.NewIdRef(count=1)

    id_help = wx.NewIdRef(count=1)
    id_about = wx.NewIdRef(count=1)

    def __init__(self, parent):
        """构造函数"""
        wx.Frame.__init__(self, parent, -1, APP_TITLE,
                          style=wx.MAXIMIZE_BOX|wx.MAXIMIZE_BOX)

        self.SetBackgroundColour(wx.Colour(250, 250, 250))
        self.SetSize((900, 600))
        self.SetMaxSize((900, 600))
        self.Center()

        # if hasattr(sys, "frozen") and getattr(sys, "frozen") == "windows_exe":
        #     exeName = win32api.GetModuleFileName(win32api.GetModuleHandle(None))
        #     icon = wx.Icon(exeName, wx.BITMAP_TYPE_ICO)
        # else :
        #     icon = wx.Icon(APP_ICON, wx.BITMAP_TYPE_ICO)
        # self.SetIcon(icon)

        icon = wx.Icon(APP_ICON, wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon)

        # self.Maximize()
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE)

        # self._CreateMenuBar()  # 菜单栏
        # self._CreateToolBar()  # 工具栏
        self._CreateStatusBar()  # 状态栏


        # 设置当前选择的功能项
        self.current_func = 0

        self.choices = {
            0: 'Arxml转dbc',
            1: 'Csv转dbc'
        }
        self.cb1 = wx.ComboBox(self, -1, value=self.choices[self.current_func], choices=list(self.choices.values()), style=wx.CB_SORT, pos=(110, 10))
        # 添加事件处理
        self.Bind(wx.EVT_COMBOBOX, self.on_combobox, self.cb1)



        # b1 = wx.Button(self, -1, u"打开模板", (10, 10))
        # self.Bind(wx.EVT_BUTTON, self.OnButton1, b1)

        b2 = wx.Button(self, -1, u"选择文件", (10, 10))
        self.Bind(wx.EVT_BUTTON, self.__OpenSingleFile, b2)

        self.__file_label = wx.StaticText(self, label="", style=wx.ALIGN_CENTER_VERTICAL, pos=(185, 12))
        self.__file_path = None

        b4 = wx.Button(self, -1, u"开始转换", (800, 10))
        self.Bind(wx.EVT_BUTTON, self.OnButton4, b4)

        # panel = wx.Panel(self)
        # my_button = MyButton(self, title="点我", pos=(410, 2))

        b4.SetBackgroundColour("#0288d1")  # 设置按钮的背景颜色
        b4.SetForegroundColour("#fff")
        b4.SetSize(75, 25)

        self.list = wx.ListCtrl(self,
                                -1,
                                style=wx.LC_REPORT,
                                pos=(10, 40),
                                size=(862, 486))  # 创建列表

        self.list.InsertColumn(0, "文件名")
        self.list.InsertColumn(1, "创建时间")  # 添加表头

        self.list.SetColumnWidth(0, 700)  # 设置列的宽度
        self.list.SetColumnWidth(1, 142)
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnDclick)
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnLeftClick)

        self.render_list()

    def _CreateMenuBar(self):
        """创建菜单栏"""
        self.mb = wx.MenuBar()

        # 文件菜单
        m = wx.Menu()
        m.Append(self.id_open, u"打开文件")
        m.Append(self.id_save, u"保存文件")
        m.AppendSeparator()
        m.Append(self.id_quit, u"退出系统")
        self.mb.Append(m, u"文件")

        self.Bind(wx.EVT_MENU, self.OnOpen, id=self.id_open)
        self.Bind(wx.EVT_MENU, self.OnSave, id=self.id_save)
        self.Bind(wx.EVT_MENU, self.OnQuit, id=self.id_quit)

        # 帮助菜单
        m = wx.Menu()
        m.Append(self.id_help, u"帮助主题")
        m.Append(self.id_about, u"关于...")
        self.mb.Append(m, u"帮助")

        self.Bind(wx.EVT_MENU, self.OnHelp, id=self.id_help)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=self.id_about)

        self.SetMenuBar(self.mb)

    def _CreateToolBar(self):
        """创建工具栏"""

        # bmp_open = wx.Bitmap('open_16.png', wx.BITMAP_TYPE_ANY) # 请自备按钮图片
        # bmp_save = wx.Bitmap('save_16.png', wx.BITMAP_TYPE_ANY) # 请自备按钮图片
        # bmp_help = wx.Bitmap('help_16.png', wx.BITMAP_TYPE_ANY) # 请自备按钮图片
        bmp_about = wx.Bitmap('aboutus.png', wx.BITMAP_TYPE_ANY)  # 请自备按钮图片

        self.tb = wx.ToolBar(self)
        self.tb.SetToolBitmapSize((16, 16))

        self.tb.AddTool(self.id_about, u'关于', bmp_about)
        # self.Bind(wx.EVT_TOOL_RCLICKED, self.OnOpen, id=self.id_open)

        self.tb.Realize()

    def _CreateStatusBar(self):
        """创建状态栏"""

        self.sb = self.CreateStatusBar()
        self.sb.SetFieldsCount(3)
        self.sb.SetStatusWidths([-3, 0, -1])
        self.sb.SetStatusStyles([wx.SB_RAISED, wx.SB_RAISED, wx.SB_RAISED])

        self.sb.SetStatusText(u'V1.0.0', 0)
        self.sb.SetStatusText(u'', 1)
        self.sb.SetStatusText(u'北京经纬恒润科技股份有限公司', 2)

    def OnOpen(self, evt):
        """打开文件"""
        self.sb.SetStatusText(u'打开文件', 1)

    def OnSave(self, evt):
        """保存文件"""
        self.sb.SetStatusText(u'保存文件', 1)

    def OnQuit(self, evt):
        """退出系统"""

        self.sb.SetStatusText(u'退出系统', 1)
        self.Destroy()

    def OnHelp(self, evt):
        """帮助"""
        self.sb.SetStatusText(u'帮助', 1)

    def OnAbout(self, evt):
        """关于"""

        self.sb.SetStatusText(u'成都樱桃智库', 1)

    def OnDclick(self, evt):
        """
        双击触发事件
        :param evt:
        :return:
        """
        itemText = evt.GetText()
        self.sb.SetStatusText(u'正在打开' + itemText, 0)
        sys = platform.system()
        if sys == "Windows":
            print("OS is Windows!!!")
            os.startfile(itemText)
        elif sys == "Linux":
            import subprocess, sys
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, itemText])
        else:
            print("====")

    def OnLeftClick(self, evt):
        """

        :param evt:
        :return:
        """
        itemText = evt.GetText()
        self.sb.SetStatusText(u'选中' + itemText, 0)

    def OnButton1(self, evt):

        # path = r'C:\Documents and Settings\liushen\Application Data\Macromedia\Flash Player\#SharedObjects'
        # os.startfile(path)
        import subprocess, sys
        filename = os.getcwd() + TMP_PATH
        sys = platform.system()
        if sys == "Windows":
            print("OS is Windows!!!")
            os.startfile(filename)
        elif sys == "Linux":
            # https://stackoverflow.com/questions/29823028/attributeerror-module-object-has-no-attribute-startfile
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])
        else:
            print("====")

    def __OpenSingleFile(self, event):
        alternative_file = {
            0: "Canoe (*.arxml)|*.arxml|" "All files (*.*)|*.*",
            1: "csv (*.csv)|*.csv|" "All files (*.*)|*.*"
        }
        files_filter = alternative_file[self.current_func]
        fileDialog = wx.FileDialog(self, message="选择单个文件", wildcard=files_filter, style=wx.FD_OPEN)
        dialogResult = fileDialog.ShowModal()
        if dialogResult != wx.ID_OK:
            return
        path = fileDialog.GetPath()
        self.__file_path = path
        file = fileDialog.GetFilename()
        # 第一类文件：arxml
        if os.path.splitext(file)[-1][1:] == "arxml" or os.path.splitext(file)[-1][1:] == "arxml":
            self.__file_label.SetLabel(file)
            self.sb.SetStatusText(u'准备转换' + path, 0)
            self.filename = os.path.splitext(file)[0]

            self.current_func = 0
            self.cb1.SetValue(self.choices[self.current_func])

        elif os.path.splitext(file)[-1][1:] == "csv":
            self.__file_label.SetLabel(file)
            self.sb.SetStatusText(u'准备转换' + path, 0)
            self.filename = os.path.splitext(file)[0]
            self.current_func = 1
            self.cb1.SetValue(self.choices[self.current_func])

        else:
            self.__file_label.SetLabel(file)
            self.sb.SetStatusText(u'准备转换' + path, 0)
            self.filename = None
        fileDialog.Destroy()

    def OnButton4(self, evt):
        if self.__file_path is None:
            self.sb.SetStatusText("转换文件为空！")
            return
        if os.path.exists(self.__file_path) is False:
            self.sb.SetStatusText("转换文件不存在，请更换！")
            return
        if self.filename is None:
            return
        self.sb.SetStatusText("正在转换" + self.__file_path)
        time_format = time.strftime('%Y%m%d_%H%M%S', time.localtime())
        output_path = OUTPUT_PATH + "/" + self.filename + "_" + time_format + ".dbc"

        # 转换分支，如果是arxml转换方式为1
        if self.current_func == 0:
            convert_result = convert(os.path.normpath(self.__file_path), os.path.normpath(output_path))
        elif self.current_func == 1:
            convert_result = {}
        else:
            return
        if convert_result["state"]:
            self.sb.SetStatusText("转换完毕" + self.__file_path)
        else:
            self.sb.SetStatusText(self.__file_path + "" + convert_result["msg"])

        # if start_switch(self.__file_path, self.filename):
        #     self.sb.SetStatusText("转换完毕" + self.__file_path)
        # else:
        #     self.sb.SetStatusText(self.__file_path + "转换失败，请检查")

        self.__file_label.SetLabel("")
        self.render_list()

    def render_list(self):
        self.list.DeleteAllItems()

        path = os.getcwd() + "\output"
        g = os.walk(path)

        rows_list = []
        for path, dir_list, file_list in g:
            for file_name in file_list:
                t = os.path.getctime(os.path.join(path, file_name))
                rows_list.append([os.path.join(path, file_name), TimeStampToTime(t)])
        rows_list.reverse()
        print(rows_list)
        data1 = {
            "columns": ['文件名', '创建时间'],
            "rows": rows_list
        }
        image_list = wx.ImageList(16, 16, True)
        bmp = wx.Bitmap(ITEM_ICON, wx.BITMAP_TYPE_PNG)
        il_max = image_list.Add(bmp)
        # 添加图标
        self.list.AssignImageList(image_list, wx.IMAGE_LIST_SMALL)
        data = Dict(data1)
        for index, item in enumerate(data.rows):  # 增加行
            # index = self.list.InsertItem(sys.maxsize, item[0])
            index = self.list.InsertItem(index, item[0])
            for col, text in enumerate(item[1:]):
                self.list.SetItem(index, col + 1, text)

            # give each item a random image
            img = random.randint(0, il_max)
            self.list.SetItemImage(index, img, img)

    def on_combobox(self, event):
        """ 下拉框的选项
        用来设置当前选择的功能
        Args：
            self: None -> 实例
            event: Combox Event -> 下拉框的事件
        returns:
            None
        """
        self.current_func = self.cb1.GetCurrentSelection()


class mainApp(wx.App):
    def OnInit(self):
        self.SetAppName(APP_TITLE)
        self.Frame = mainFrame(None)
        self.Frame.Show()
        return True


class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__


class BlockWindow(wx.Panel):
    def __init__(self, parent, ID=-1, label="", pos=wx.DefaultPosition, size=(100, 25)):
        wx.Panel.__init__(self, parent, ID, pos, size, wx.RAISED_BORDER, label)
        self.label = label
        self.SetBackgroundColour("white")
        self.SetMinSize(size)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        sz = self.GetClientSize()
        dc = wx.PaintDC(self)
        w, h = dc.GetTextExtent(self.label)
        dc.SetFont(self.GetFont())
        dc.DrawText(self.label, (sz.width - w) / 2, (sz.height - h) / 2)


def TimeStampToTime(timestamp):
    """
    把时间戳转化为时间: 1479264792 to 2016-11-16 10:53:12
    :param timestamp:
    :return:
    """
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)


class MyButton(wx.Button, wx.EvtHandler):
    """自定义按钮"""

    def __init__(self, parent, title, pos, size=(60, 35), borderColor='#EAEAEA', borderSize=1):
        self.button, self.border = self.__CreateButton(parent, title, pos, size, borderColor, borderSize)

    def __CreateButton(self, parent, title, pos, size, borderColor, borderSize):
        """创建自定义按钮"""
        border = wx.StaticText(parent, -1, '', pos=pos, size=size)
        border.SetBackgroundColour(borderColor)
        # 设置按钮在border上的位置，使其刚好露出borderSize大小的边框
        button = wx.Button(border, -1, title, size=((size[0] - borderSize * 2), (size[1] - borderSize * 2)),
                           pos=(borderSize, borderSize), style=wx.NO_BORDER)

        button.SetBackgroundColour('white')
        button.SetForegroundColour('black')
        return button, border

    def SetForegroundColour(self, colour):
        self.button.SetForegroundColour(colour)
        self.button.Refresh()

    def SetBackgroundColour(self, colour):
        self.button.SetBackgroundColour(colour)

    def SetBorderColour(self, colour):
        self.border.SetBackgroundColour(colour)
        self.border.Refresh()

    def Disable(self):
        self.button.Disable()

    def Enable(self, enable=True):
        self.button.Enable(enable)

    def Bind(self, event, handler, source=None, id=wx.ID_ANY, id2=wx.ID_ANY):
        self.button.Bind(event, handler)


if __name__ == "__main__":
    app = mainApp()
    app.MainLoop()
