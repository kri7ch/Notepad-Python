import datetime
import os.path
import webbrowser

from PyQt5 import QtWidgets, Qt, QtCore
from PyQt5.QtCore import QUrl, QSettings
from PyQt5.QtGui import QDesktopServices, QPixmap, QTextCursor, QFont
from PyQt5.QtPrintSupport import QPrintDialog, QPageSetupDialog, QPrinter
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QMessageBox, QFontDialog, \
    QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout
import sys
import os


class ReplaceWindow(QMainWindow):
    def __init__(self, text, text_edit, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Заменить')
        self.setWindowIcon(Qt.QIcon("notepad_icon.png"))
        self.setFixedSize(500, 200)
        self.text = text
        self.text_edit = text_edit
        self.main_layout = QGridLayout()
        self.vbox_1 = QVBoxLayout()
        self.vbox_2 = QVBoxLayout()

        self.row1_layout = QHBoxLayout()
        self.label_1 = QLabel("Что:")
        self.line_edit_1 = QtWidgets.QLineEdit()
        self.line_edit_1.setStyleSheet("font-size: 20px")
        self.line_edit_1.textChanged.connect(lambda: self.check_line())
        self.label_1.setStyleSheet("font-size: 20px")
        self.row1_layout.addWidget(self.label_1)
        self.row1_layout.addWidget(self.line_edit_1)
        self.vbox_1.addLayout(self.row1_layout)

        self.row2_layout = QHBoxLayout()
        self.label_2 = QLabel("Чем:")
        self.line_edit_2 = QtWidgets.QLineEdit()
        self.label_2.setStyleSheet("font-size: 20px")
        self.line_edit_2.setStyleSheet("font-size: 20px")
        self.row2_layout.addWidget(self.label_2)
        self.row2_layout.addWidget(self.line_edit_2)
        self.vbox_1.addLayout(self.row2_layout)
        self.vbox_1.setContentsMargins(10, 0, 0, 60)

        self.row3_layout = QVBoxLayout()
        self.button_search = QPushButton("Найти далее")
        self.button_search.clicked.connect(lambda: self.search())
        self.button_replace = QPushButton("Заменить")
        self.button_replace.clicked.connect(lambda: self.replace())
        self.button_replace_all = QPushButton("Заменить все")
        self.button_replace_all.clicked.connect(lambda: self.replace_all())
        self.button_cancel = QPushButton("Отмена")
        self.button_cancel.clicked.connect(lambda: self.close())
        self.row3_layout.addWidget(self.button_search)
        self.row3_layout.addWidget(self.button_replace)
        self.row3_layout.addWidget(self.button_replace_all)
        self.row3_layout.addWidget(self.button_cancel)
        self.vbox_2.addLayout(self.row3_layout)
        self.vbox_2.setContentsMargins(10, 0, 0, 10)
        self.main_layout.addLayout(self.vbox_1, 0, 0)
        self.main_layout.addLayout(self.vbox_2, 0, 1)

        self.central = QtWidgets.QWidget()
        self.central.setLayout(self.main_layout)
        self.setCentralWidget(self.central)

    def check_line(self):
        if not self.line_edit_1.text():
            self.button_search.setEnabled(False)
            self.button_replace.setEnabled(False)
            self.button_replace_all.setEnabled(False)
            return
        self.button_search.setEnabled(True)
        if self.windowTitle() == "Заменить":
            self.button_replace.setEnabled(True)
            self.button_replace_all.setEnabled(True)

    def search(self):
        text = self.text_edit.toPlainText()
        cursor_position = self.text_edit.textCursor().position()
        index = text.find(self.line_edit_1.text(), cursor_position)
        if index != -1:
            cursor = self.text_edit.textCursor()
            cursor.setPosition(index)
            cursor.setPosition(index + len(self.line_edit_1.text()), QTextCursor.KeepAnchor)
            self.text_edit.setTextCursor(cursor)
        else:
            QMessageBox.information(self, "Блокнот", f'Не удается найти "{self.line_edit_1.text()}"')

    def replace_all(self):
        text = self.text_edit.toPlainText()
        self.text_edit.setText(str(text).replace(self.line_edit_1.text(), self.line_edit_2.text()))

    def replace(self):
        self.search()
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.line_edit_2.text())


class Notepad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.font = None
        self.replace_window = ReplaceWindow
        self.find_window = ReplaceWindow
        self.menubar = QtWidgets.QMenuBar()
        self.setMinimumSize(700, 500)
        self.setWindowIcon(Qt.QIcon("notepad_icon.png"))
        self.setWindowTitle('Безымянный - Блокнот')
        self.path = None
        self.printer = QPrinter(QPrinter.HighResolution)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        vbox = QtWidgets.QVBoxLayout(central_widget)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

        self.text_edit = QtWidgets.QTextEdit()
        self.settings = QSettings()
        self.text_edit.setStyleSheet("border: 0.5px;")
        self.text_edit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.text_edit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.text_edit.textChanged.connect(self.check)
        self.text_edit.selectionChanged.connect(self.selection_control)
        self.text_edit.cursorPositionChanged.connect(self.update_cursor_label)
        self.upd_settings()
        vbox.addWidget(self.text_edit)

        self.reply = QMessageBox(self)
        self.reply.setWindowTitle("Блокнот")
        self.reply.setText(f"Вы хотите сохранить изменения в файле?")
        self.reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        self.reply.button(QMessageBox.Yes).setText("    Сохранить   ")
        self.reply.button(QMessageBox.No).setText("     Не сохранять    ")
        self.reply.button(QMessageBox.Cancel).setText("Отмена")
        self.reply.setIcon(QMessageBox.NoIcon)

        self.file_menu = QtWidgets.QMenu('&Файл')
        self.correction_menu = QtWidgets.QMenu('&Правка')
        self.format_menu = QtWidgets.QMenu('Фор&мат')
        self.view_menu = QtWidgets.QMenu('&Вид')
        self.help_menu = QtWidgets.QMenu('&Справка')
        self.menubar_widgets()

        self.create_file = QtWidgets.QAction('Созд&ать')
        self.create_file.triggered.connect(lambda: self.new_file_action())
        self.create_file.setShortcut("ctrl+n")
        self.new_window = QtWidgets.QAction('&Новое окно')
        self.new_window.triggered.connect(lambda: self.new_window_action())
        self.new_window.setShortcut("ctrl+shift+n")
        self.open_file = QtWidgets.QAction('&Открыть...')
        self.open_file.triggered.connect(lambda: self.open_file_dialog())
        self.open_file.setShortcut("ctrl+o")
        self.save_file = QtWidgets.QAction('&Сохранить')
        self.save_file.triggered.connect(lambda: self.save_text())
        self.save_file.setShortcut("ctrl+s")
        self.save_as_file = QtWidgets.QAction('&Сохранить как...')
        self.save_as_file.triggered.connect(lambda: self.save_as_text())
        self.save_as_file.setShortcut("ctrl+shift+s")
        self.param_of_list = QtWidgets.QAction('Пара&метры страницы')
        self.param_of_list.triggered.connect(lambda: self.list_param())
        self.print_file = QtWidgets.QAction('&Печать')
        self.print_file.triggered.connect(lambda: self.file_print())
        self.print_file.setShortcut("ctrl+P")
        self.exit_notepad = QtWidgets.QAction('В&ыход')
        self.exit_notepad.triggered.connect(lambda: self.close())
        self.file_menu_widgets()

        self.revert = QtWidgets.QAction('&Отменить')
        self.revert.triggered.connect(lambda: self.text_edit.undo())
        self.revert.setShortcut('ctrl+z')
        self.cut = QtWidgets.QAction('&Вырезать')
        self.cut.triggered.connect(lambda: self.text_edit.cut())
        self.cut.setShortcut('ctrl+x')
        self.copy = QtWidgets.QAction('&Копировать')
        self.copy.triggered.connect(lambda: self.text_edit.copy())
        self.copy.setShortcut('ctrl+c')
        self.insert = QtWidgets.QAction('Вст&авить')
        self.insert.triggered.connect(lambda: self.insert_text())
        self.insert.setShortcut('ctrl+v')
        self.delete = QtWidgets.QAction('&Удалить')
        self.delete.triggered.connect(lambda: self.delete_text())
        self.delete.setShortcut('del')
        self.search = QtWidgets.QAction('&Поиск с помощью Bing...')
        self.search.triggered.connect(lambda: self.search_with_bing())
        self.search.setShortcut('ctrl+e')
        self.seek = QtWidgets.QAction('&Найти...')
        self.seek.triggered.connect(lambda: self.find_text())
        self.seek.setShortcut('ctrl+f')
        self.replace = QtWidgets.QAction('&Заменить...')
        self.replace.triggered.connect(lambda: self.replace_text())
        self.replace.setShortcut('ctrl+h')
        self.go_to = QtWidgets.QAction('Перей&ти...')
        self.go_to.setShortcut('ctrl+g')
        self.select_all = QtWidgets.QAction('Выделить в&се')
        self.select_all.triggered.connect(lambda: self.text_edit.selectAll())
        self.select_all.setShortcut('ctrl+a')
        self.date_time = QtWidgets.QAction('Врем&я и дата')
        self.date_time.triggered.connect(lambda: self.insert_date())
        self.date_time.setShortcut('f5')
        self.revert.setEnabled(False)
        self.cut.setEnabled(False)
        self.copy.setEnabled(False)
        self.delete.setEnabled(False)
        self.search.setEnabled(False)
        self.go_to.setEnabled(False)
        self.search.setEnabled(False)
        self.seek.setEnabled(False)
        self.search.setEnabled(False)
        self.correction_menu_widgets()

        self.transfer = QtWidgets.QAction("&Перенос по словам", self, checkable=True)
        self.transfer.setChecked(True)
        self.transfer.triggered.connect(lambda: self.checkbox_action())
        self.font_menu = QtWidgets.QAction('&Шрифт')
        self.font_menu.triggered.connect(lambda: self.shrift_menu())
        self.format_menu_widgets()

        self.scale = QtWidgets.QMenu('&Масштаб')
        self.rise_up = QtWidgets.QAction('&Увеличить')
        self.rise_up.triggered.connect(self.rise_up_action)
        self.rise_down = QtWidgets.QAction('&Уменьшить')
        self.rise_down.triggered.connect(self.rise_down_action)
        self.rise_to_default = QtWidgets.QAction('&Восстановить масштаб по умолчанию')
        self.rise_to_default.triggered.connect(self.rise_to_default_action)
        self.statusbar_menu = QtWidgets.QAction('&Строка состояния', self, checkable=True)
        self.statusbar_menu.setChecked(True)
        self.statusbar_menu.triggered.connect(lambda: self.statusbar_menu_action())
        self.view_menu_widgets()

        self.see_help = QtWidgets.QAction('Прос&мотреть справку')
        self.see_help.triggered.connect(lambda: webbrowser.open(
            r'https://www.bing.com/search?q=справка+по+использованию+'
            r'блокнота+в+windows%c2%a010&filters=guid:"4466414-ru-dia"%20lang:"ru"&form=T00032&ocid=HelpPane-BingIA'))
        self.send_rate = QtWidgets.QAction('&Отправить отзыв')
        self.send_rate.triggered.connect(lambda: self.open_feedback_center())
        self.about_program = QtWidgets.QAction('&О программе')
        self.about_program.triggered.connect(lambda: self.open_notepad_info())
        self.help_menu_widgets()

        self.statusbar = QtWidgets.QStatusBar()
        self.label = QLabel("Стр 1, стлб 1" + " " * 20)
        self.label2 = QLabel("100%" + " " * 6)
        self.label3 = QLabel("Windows (CRLF)" + " " * 9)
        self.label4 = QLabel("UTF-8" + " " * 26)
        self.statusbar_widgets()

    def statusbar_widgets(self) -> None:
        self.statusbar.addPermanentWidget(self.label)
        self.statusbar.addPermanentWidget(self.label2)
        self.statusbar.addPermanentWidget(self.label3)
        self.statusbar.addPermanentWidget(self.label4)
        self.setStatusBar(self.statusbar)

    def menubar_widgets(self) -> None:
        self.menubar.addMenu(self.file_menu)
        self.menubar.addMenu(self.correction_menu)
        self.menubar.addMenu(self.format_menu)
        self.menubar.addMenu(self.view_menu)
        self.menubar.addMenu(self.help_menu)
        self.setMenuBar(self.menubar)

    def file_menu_widgets(self) -> None:
        self.file_menu.addAction(self.create_file)
        self.file_menu.addAction(self.new_window)
        self.file_menu.addAction(self.open_file)
        self.file_menu.addAction(self.save_file)
        self.file_menu.addAction(self.save_as_file)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.param_of_list)
        self.file_menu.addAction(self.print_file)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_notepad)

    def correction_menu_widgets(self) -> None:
        self.correction_menu.addAction(self.revert)
        self.correction_menu.addSeparator()
        self.correction_menu.addAction(self.cut)
        self.correction_menu.addAction(self.copy)
        self.correction_menu.addAction(self.insert)
        self.correction_menu.addAction(self.delete)
        self.correction_menu.addSeparator()
        self.correction_menu.addAction(self.search)
        self.correction_menu.addAction(self.seek)
        self.correction_menu.addAction(self.replace)
        self.correction_menu.addAction(self.go_to)
        self.correction_menu.addSeparator()
        self.correction_menu.addAction(self.select_all)
        self.correction_menu.addAction(self.date_time)

    def format_menu_widgets(self) -> None:
        self.format_menu.addAction(self.transfer)
        self.format_menu.addAction(self.font_menu)

    def view_menu_widgets(self) -> None:
        self.view_menu.addMenu(self.scale)

        self.scale.addAction(self.rise_up)
        self.rise_up.setShortcut('ctrl+=')
        self.scale.addAction(self.rise_down)
        self.rise_down.setShortcut('ctrl+-')
        self.scale.addAction(self.rise_to_default)
        self.rise_to_default.setShortcut('ctrl+0')
        self.view_menu.addAction(self.statusbar_menu)

    def help_menu_widgets(self) -> None:
        self.help_menu.addAction(self.see_help)
        self.help_menu.addAction(self.send_rate)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.about_program)

    def new_file_action(self) -> None | bool:
        if not self.windowTitle().startswith("*"):
            self.path = None
            self.text_edit.clear()
            self.setWindowTitle('Безымянный - Блокнот')
            return
        result = self.reply.exec_()
        if result == QMessageBox.Yes:
            if self.save_text():
                self.path = None
                self.text_edit.clear()
                self.setWindowTitle('Безымянный - Блокнот')
                return True
            else:
                return False
        if result == QMessageBox.No:
            self.setWindowTitle('Безымянный - Блокнот')
            self.text_edit.clear()
            self.path = None
        else:
            self.path = None
            return True

    @staticmethod
    def new_window_action() -> None:
        new_window = Notepad()
        new_window.showNormal()

    def open_file_dialog(self) -> None:
        if self.windowTitle().startswith("*"):
            result = self.reply.exec_()
            if result == QMessageBox.Yes:
                self.save_as_text()
                return
            elif result == QMessageBox.No:
                pass
            else:
                return
        filename, _ = QFileDialog.getOpenFileName(self, filter="*.txt")
        if filename:
            with open(filename, 'r') as file:
                self.text_edit.setText(file.read())
            self.window().setWindowTitle(str(filename).split('/')[-1])
            self.path = str(filename)

    def save_file_dialog(self) -> bool:
        filename = QFileDialog.getSaveFileName(self, filter="*.txt")
        if filename[0]:
            if os.path.isfile(filename[0]):
                with open(filename[0], 'w') as file:
                    file.write(self.text_edit.toPlainText())
                self.window().setWindowTitle(os.path.basename(filename[0]))
                self.path = str(filename[0])
            else:
                with open(filename[0], 'x') as file:
                    file.write(self.text_edit.toPlainText())
                self.window().setWindowTitle(os.path.basename(filename[0]))
                self.path = str(filename[0])
            return True
        else:
            return False

    def save_text(self) -> bool:
        if self.path is not None:
            with open(self.path, "w") as file:
                file.write(self.text_edit.toPlainText())
            self.window().setWindowTitle(str(self.path).split('/')[-1])
            return True
        else:
            return self.save_file_dialog()

    def save_as_text(self) -> None:
        self.save_file_dialog()

    def file_print(self) -> None:
        dlg = QPrintDialog(self.printer, self)
        if dlg.exec_() == QPrintDialog.Accepted:
            self.text_edit.print_(self.printer)

    def list_param(self) -> None:
        dlg = QPageSetupDialog(self.printer, self)
        if dlg.exec_() == QPageSetupDialog.Accepted:
            self.printer = dlg.printer()

    def insert_text(self) -> None:
        clipboard = QApplication.clipboard()
        text_to_insert = clipboard.text()
        self.text_edit.insertPlainText(text_to_insert)

    def delete_text(self) -> None:
        selected_text = self.text_edit.toPlainText()[
                        self.text_edit.textCursor().selectionStart():self.text_edit.textCursor().selectionEnd()]
        self.text_edit.setText(self.text_edit.toPlainText().replace(selected_text, ""))

    def search_with_bing(self) -> None:
        selected_text = self.text_edit.toPlainText()[
                        self.text_edit.textCursor().selectionStart():self.text_edit.textCursor().selectionEnd()]
        webbrowser.open(f"https:/www.bing.com/search?q={selected_text}&form=NPCTXT")

    def configure_find_window(self, title: str, enable_line_edit: bool = False) -> None:
        find_window = self.find_window(text=self.text_edit.toPlainText(), text_edit=self.text_edit)
        find_window.setWindowTitle(title)
        find_window.button_search.setEnabled(False)
        find_window.button_replace_all.setEnabled(False)
        find_window.button_replace.setEnabled(False)
        find_window.line_edit_2.setEnabled(enable_line_edit)
        find_window.show()

    def find_text(self) -> None:
        self.configure_find_window("Найти")

    def replace_text(self) -> None:
        self.configure_find_window("Заменить", enable_line_edit=True)

    def insert_date(self) -> None:
        text_to_insert = str(datetime.date.today())
        self.text_edit.insertPlainText(text_to_insert)

    def checkbox_action(self) -> None:
        if self.transfer.isChecked():
            self.text_edit.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        else:
            self.text_edit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

    def upd_settings(self):
        font = self.settings.value("font", QFont())
        self.text_edit.setFont(font)

    def shrift_menu(self):
        font, ok = QFontDialog.getFont(self.font if self.font else QFont(), self)
        if ok:
            self.font = font
            self.text_edit.setFont(self.font)
            self.settings.setValue("font", self.font)

    def statusbar_menu_action(self) -> None:
        if self.statusbar_menu.isChecked():
            self.statusbar.show()
        else:
            self.statusbar.hide()

    def rise_up_action(self) -> None:
        label_text = int(self.label2.text().replace('%', ''))
        if label_text < 500:
            self.text_edit.zoomIn(1)
            self.label2.setText(f"{label_text + 10}%" + " " * 6)

    def rise_down_action(self) -> None:
        label_text = int(self.label2.text().replace('%', ''))
        if label_text > 10:
            self.text_edit.zoomOut(1)
            self.label2.setText(f"{label_text - 10}%" + " " * 6)

    def rise_to_default_action(self, leave) -> None:
        if not leave:
            self.text_edit.setFont(self.font)
        self.label2.setText(f"100%" + " " * 6)

    @staticmethod
    def open_feedback_center() -> None:
        feedback_url = QUrl("feedback-hub:")
        QDesktopServices.openUrl(feedback_url)

    def check(self) -> None:
        text_edit_text = self.text_edit.toPlainText()
        if text_edit_text:
            self.revert.setEnabled(True)
            self.seek.setEnabled(True)
        else:
            self.revert.setEnabled(False)
            self.seek.setEnabled(False)
        if self.path is not None:
            if os.path.isfile(self.path):
                with open(self.path, "r") as file:
                    file_text = file.read()
                if text_edit_text == file_text:
                    self.window().setWindowTitle(str(self.path).split("/")[-1])
                else:
                    self.window().setWindowTitle("*" + str(self.path).split("/")[-1])
            else:
                self.window().setWindowTitle(self.path.split("/")[-1])
            return
        file_text = ""
        if text_edit_text == file_text:
            self.window().setWindowTitle("Безымянный - Блокнот")
        else:
            self.window().setWindowTitle("*Безымянный - Блокнот")

    def selection_control(self) -> None:
        selected_text = self.text_edit.textCursor().selectedText()
        if selected_text:
            self.cut.setEnabled(True)
            self.copy.setEnabled(True)
            self.delete.setEnabled(True)
            self.search.setEnabled(True)
        else:
            self.cut.setEnabled(False)
            self.copy.setEnabled(False)
            self.delete.setEnabled(False)
            self.search.setEnabled(False)

    def update_cursor_label(self) -> None:
        cursor = self.text_edit.textCursor()
        position = cursor.columnNumber()
        block_number = cursor.blockNumber() + 1
        self.label.setText(f"Стр {block_number}, стлб {position + 1}" + " " * 20)

    def open_notepad_info(self) -> None:
        picture = QLabel()
        label_text = ('Notepad - Rakhmaev \n'
                      'Версия программы 22H2 \n'
                      'Приложение для работы с текстом')
        picture.setPixmap(QPixmap("notepad_mini.png"))
        mssbox = QMessageBox(self)
        mssbox.setText(label_text)
        mssbox.setIconPixmap(picture.pixmap())
        mssbox.setWindowTitle("Сведения")
        mssbox.exec_()

    def save_settings(self):
        settings = QSettings("Notepad", "font")
        font = self.text_edit.font()
        settings.setValue("font", font)

    def upd_settings(self):
        settings = QSettings("Notepad", "font")
        self.font = settings.value("font", QFont())
        self.text_edit.setFont(self.font)

    def closeEvent(self, event) -> None:
        if self.text_edit.document().isModified():
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Блокнот")
            dialog.setText("Вы хотите сохранить изменения в файле?")
            dialog.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            dialog.setDefaultButton(QMessageBox.Save)
            dialog.button(QMessageBox.Save).setText("    Сохранить   ")
            dialog.button(QMessageBox.Discard).setText("     Не сохранять    ")
            dialog.button(QMessageBox.Cancel).setText("Отмена")
            answer = dialog.exec_()

            if answer == QMessageBox.Save:
                filename, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "Текстовые файлы (*.txt);;Все файлы (*)")
                if filename:
                    with open(filename, 'w') as f:
                        f.write(self.text_edit.toPlainText())
                    event.accept()
                else:
                    event.ignore()
            elif answer == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == '__main__':
    app = QApplication([])
    notepad = Notepad()
    notepad.show()
    sys.exit(app.exec_())
