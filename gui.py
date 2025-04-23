import os
import sys
import wx
import asyncio
from buttons_handlers import main, clean_db


class MyFrame(wx.Frame):
    '''Создание графического интерфейса'''

    def __init__(self, parent, title, style, size=(420, 220)):
        '''
        Инициализатор графического интерфейса

        Args:
            parent (wx.Window): Родительский элемент интерфейса
            title (str): Заголовок окна
            style (int): Стиль окна
            size (tuple[int, int]): Размер окна
        '''

        super().__init__(parent, title=title, style=style, size=size)

        #Инициализация цикла событий asyncio
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        #Создание панели и основных элементов интерфейса
        self.panel = wx.Panel(self)
        self.CreateUi()

        #Привязка событий
        self.BindEvents()

        #Установка начальных значений
        self.action = self.action_choices[0]
        self.sourse = 'api'
        self.action = 'excel-no-db'

        #Добавление иконки
        icon_path = self.get_icon_path()
        self.SetIcon(wx.Icon(icon_path))

        self.Show()


    def CreateUi(self):
        '''Инициализация элементов интерфейса'''

        fb = wx.FlexGridSizer(6, 2, 10, 10)
        vertical_box_sizer = wx.BoxSizer(wx.VERTICAL)

        #Создание полей ввода
        self.match_id = wx.TextCtrl(self.panel)
        self.path = wx.TextCtrl(self.panel)
        self.database_name = wx.TextCtrl(self.panel)

        #Создание списка действий
        self.action_choices = [
            'Создать Excel, не добавлять матч в Базу данных',
            'Создать Excel, добавить матч в Базу данных',
            'Не создавать Excel, добавить матч в Базу данных',
            'Извлечь матч из Базы Данных'
        ]
        self.actions = wx.ComboBox(
            self.panel,
            id=wx.ID_ANY,
            value=self.action_choices[0],
            choices=self.action_choices,
            style=wx.CB_DROPDOWN | wx.CB_READONLY
        )

        #Добавление элементов в сетку
        fb.AddMany([
            (wx.StaticText(self.panel, label='ID матча'), 0, wx.EXPAND),
            (self.match_id, 0, wx.EXPAND),
            (wx.StaticText(self.panel, label='Путь'), 0, wx.EXPAND),
            (self.path, 0, wx.EXPAND),
            (wx.StaticText(self.panel, label='Название турнира'), 0, wx.EXPAND),
            (self.database_name, 0, wx.EXPAND),
            (wx.StaticText(self.panel, label='Действие'), 0, wx.EXPAND),
            (self.actions, 0, wx.EXPAND),
        ])
        fb.AddGrowableCol(1, 1)
        vertical_box_sizer.Add(fb, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        #Создание кнопок
        button_enter = wx.Button(self.panel, id=0, label='Ввод')
        button_clear_db = wx.Button(self.panel, id=1, label='Очистить БД')

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(button_enter, 0, wx.LEFT, 10)
        button_sizer.AddStretchSpacer(1)
        button_sizer.Add(button_clear_db, 0, wx.RIGHT, 10)
        vertical_box_sizer.Add(button_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)

        self.panel.SetSizer(vertical_box_sizer)


    def BindEvents(self):
        '''Привязка событий к элементам интерфейса'''

        self.Bind(wx.EVT_BUTTON, self.RunScript, id=0)
        self.Bind(wx.EVT_COMBOBOX, self.ActionSelected, self.actions)
        self.Bind(wx.EVT_BUTTON, self.ClearDatabase, id=1)


    def ActionSelected(self, event):
        '''
        Обработчик события выбора турнира

        Args:
            event (wx.CommandEvent): Событие выбора элемента управления
        '''

        match self.actions.GetValue():
            case 'Создать Excel, не добавлять матч в Базу данных':
                self.sourse = 'api'
                self.action = 'excel-no-db'
            case 'Создать Excel, добавить матч в Базу данных':
                self.sourse = 'api'
                self.action = 'excel-db'
            case 'Не создавать Excel, добавить матч в Базу данных':
                self.sourse = 'api'
                self.action = 'no-excel-db'
            case 'Извлечь матч из Базы Данных':
                self.sourse = 'db'
                self.action = ''


    def RunScript(self, event):
        '''Функция, вызываемая при нажатии кнопки

        Args:
            event (wx.CommandEvent): Событие выбора элемента управления
        '''

        match_id = self.match_id.GetValue().strip()
        path = self.path.GetValue()
        database_name = self.database_name.GetValue()
        if not database_name:
            database_name = 'Tournament'
        asyncio.run(main(match_id, path, self.sourse, self.action,  database_name))


    def ClearDatabase(self, event):
        '''
        Функция, вызываемая при нажатии на "Очистить Базу Данных"

        Args:
            event (wx.CommandEvent): Событие выбора элемента управления
        '''

        database_name = self.database_name.GetValue()
        if not database_name:
            database_name = 'Tournament'
        clean_db(database_name)


    @staticmethod
    def get_icon_path():
        '''
            Возвращает путь к иконке приложения

            Если программа упакована (например, с помощью pyinstaller), используется путь
            к временной папке с ресурсами (sys._MEIPASS), если нет - используется
            путь к текущей директории

            Returns:
                str: Полный путь к файлу иконки (logo.ico)
        '''

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        return os.path.join(base_path, 'static', 'img', 'logo.ico')


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(None, 'DOTA 2 Stats', style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX & ~wx.RESIZE_BORDER)
    frame.Center()
    frame.Show()
    app.MainLoop()