from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import sqlite3

try:
    conn = sqlite3.connect('treker_base.db')
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS 'treker_basic' (
        name TEXT,
        description TEXT,
        quan_row INTEGER,
        quan_coln INTEGER
    )
    """)
except Exception as e:
    print(f"Ошибка при подключении к базе данных: {e}")

class TrekerDataManager:
    def __init__(self):
        self.treker_name = ''

    def set_treker_name(self, name):
        self.treker_name = name
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.bl = BoxLayout(orientation='vertical', padding=100)
        self.add_widget(self.bl)
        self.gl = GridLayout(cols=1, spacing=10)

    def on_enter(self):
        try:
            c.execute("SELECT * FROM 'treker_basic'")
            rows_in_base = c.fetchall()

            names = [row[0] for row in rows_in_base]

            self.gl.clear_widgets()

            for name in names:
                btn = Button(text=name)
                btn.bind(on_release=lambda x, n=name: self.set_and_go(n))
                self.gl.add_widget(btn)

            create_new_pattern_button = Button(text="+")
            create_new_pattern_button.bind(on_release=lambda x: setattr(self.manager, 'current', 'createtreker'))
            self.gl.add_widget(create_new_pattern_button)

            self.bl.add_widget(self.gl)
        except Exception as e:
            print(f"Ошибка в MainScreen: {e}")

    def set_and_go(self, text):
        self.manager.data_manager.set_treker_name(text)
        self.manager.current = 'config'


class ConfigTrekerScreen(Screen):
    def __init__(self, **kwargs):
        super(ConfigTrekerScreen, self).__init__(**kwargs)
        self.treker_name = ''
        self.tr_cell_tab_name = ''
        self.treker_colnname_list = ''
        self.treker_rowname_list = ''

    def on_pre_enter(self):

        self.treker_name = self.manager.data_manager.treker_name
        self.update_screen()

    def update_screen(self):
        self.del_list = []
        self.input_row_vid_list = []
        self.input_row_list = []
        self.input_coln_vid_list = []
        self.input_coln_list = []

        self.clear_widgets()

        # Создать ScrollView
        sv = ScrollView()
        root_layout = GridLayout(cols=1, size_hint_y=None, spacing=10)  # Добавить промежуток для лучшей эстетики
        root_layout.bind(minimum_height=root_layout.setter('height'))
        sv.add_widget(root_layout)
        self.add_widget(sv)


        try:
            c.execute("SELECT * FROM treker_basic WHERE name = ?", (self.treker_name,))
            basic_info = c.fetchone()
        except Exception as e:
            print(f"Ошибка при получении базовой информации: {e}")
            return

        if basic_info:

            self.tr_cell_tab_name = 'сells' + (str(self.treker_name)).replace(" ", "_")
            self.treker_colnname_list = 'colnname' + (str(self.treker_name)).replace(" ", "_")
            self.treker_rowname_list = 'rowname' + (str(self.treker_name)).replace(" ", "_")

            # Количество строк и столбцов
            q_row = basic_info[2]
            q_coln = basic_info[3]

            # NEW: GridLayout для названий столбцов над таблицей
            gl_colnname = GridLayout(rows=1, cols=q_coln, size_hint_y=None, height=40, size_hint_x=None)
            gl_colnname.bind(minimum_height=gl_colnname.setter('height'))
            gl_colnname.size_hint_x = None
            gl_colnname.width = Window.width - 150

            col_name_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            col_name_layout.add_widget(Widget(size_hint_x=None, width=150))
            col_name_layout.add_widget(gl_colnname)


            try:
                c.execute(f"SELECT * FROM {self.treker_colnname_list}")
                colnname_info = c.fetchall()
            except Exception as e:
                print(f"Ошибка при получении названий столбцов: {e}")
                return

            for a_1 in range(q_coln):
                 if a_1 < len(colnname_info):
                     text = str(colnname_info[a_1][1])
                 else:
                    text = ""

                 self.colnname_inp = TextInput(text=text, size_hint_y=None, height=40, size_hint_x=None, width=40) # Не задавать ширину
                 self.input_coln_vid_list.append(self.colnname_inp)
                 gl_colnname.add_widget(self.colnname_inp)

            root_layout.add_widget(col_name_layout)
            # Интерактивная часть + таблица для названий строк
            table_and_row_names_layout = GridLayout(cols=2, size_hint_y=None)
            table_and_row_names_layout.bind(minimum_height=table_and_row_names_layout.setter('height'))

            # Таблица для названий строк
            gl_rowname = GridLayout(rows=q_row, cols=1, size_hint_y=None, width=150)
            gl_rowname.bind(minimum_height=gl_rowname.setter('height'))
            gl_rowname.size_hint_x = None

            try:
                c.execute(f"SELECT * FROM {self.treker_rowname_list}")
                rowname_info = c.fetchall()
            except Exception as e:
                print(f"Ошибка при получении названий строк: {e}")
                return

            for a_2 in range(q_row):
                 if a_2 < len(rowname_info):
                     text = str(rowname_info[a_2][1])
                 else:
                     text = ""

                 self.rowname_inp = TextInput(text=text, size_hint_y=None, height=40, size_hint_x=None, width=150)
                 self.input_row_vid_list.append(self.rowname_inp)
                 gl_rowname.add_widget(self.rowname_inp)

            table_and_row_names_layout.add_widget(gl_rowname)


            gl_table = GridLayout(rows=q_row, cols=q_coln, size_hint_y=None)
            gl_table.bind(minimum_height=gl_table.setter('height'))

            try:
                c.execute(f"SELECT * FROM {self.tr_cell_tab_name}")
                cell_info = c.fetchall()
            except Exception as e:
                print(f"Ошибка при получении информации о ячейках: {e}")
                return

            total_cells = q_row * q_coln
            for a_55 in range(total_cells):
                if a_55 < len(cell_info):
                    if cell_info[a_55][1] == 'empty':
                        btn = Button(background_color=[0, 0, 0, 1], size_hint=(None,None), size=(40, 40)) #Правильный размер ячейки
                    else:
                        btn = Button(background_color=[1, 1, 1, 1], size_hint=(None,None), size=(40, 40)) #Правильный размер ячейки
                else:  #Если данные в БД отсутствуют, создаем кнопку по умолчанию "empty"
                    btn = Button(background_color=[0, 0, 0, 1], size_hint=(None,None), size=(40, 40)) # по умолчанию черный

                btn.bind(on_release=lambda x, ind=a_55, btn_ref=btn: self.if_release(ind, btn_ref))
                gl_table.add_widget(btn)

            table_and_row_names_layout.add_widget(gl_table)

            root_layout.add_widget(table_and_row_names_layout)

    def if_release(self, cell_ind, btn):
        if btn.background_color == [0, 0, 0, 1]:
            btn.background_color = [1, 1, 1, 1]
            self.del_list.remove(cell_ind)
        if btn.background_color == [1, 1, 1, 1]:
            btn.background_color = [0, 0, 0, 1]
            self.del_list.append(cell_ind)

    #сохраниение
    def config_complit():
        for b_1 in self.del_list: #сохр состояния ячеек
            c.execute(f"UPDATE {self.treker_cells_list} SET color = ? WHERE ind = ?", ('empty', b_1))

        for b_3 in self.input_row_list:
            c.execute(f"UPDATE {self.treker_colnname_list} SET color = ? WHERE ind = ?", ('empty', b_3))

        for b_4 in self.input_coln_list:
            c.execute(f"UPDATE {self.treker_rowname_list} SET color = ? WHERE ind = ?", ('empty', b_3))


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main_scr'))
        sm.add_widget(ConfigTrekerScreen(name='config'))

        self.data_manager = TrekerDataManager()
        sm.data_manager = self.data_manager

        return sm

if __name__ == "__main__":
    MyApp().run()
        