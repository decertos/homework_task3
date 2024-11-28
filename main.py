import sys

from PyQt6.QtWidgets import QWidget, QMainWindow, QApplication, QTableWidgetItem

from UI.addEditCoffeeForm import Ui_Edit_Form
from UI.main_ui import Ui_Form

import sqlite3


class MainWindow(QMainWindow, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.addButton.clicked.connect(self.add_edit_data)
        self.editButton.clicked.connect(self.add_edit_data)
        self.load_data()

    def load_data(self):
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Название сорта", "Степень обжарки", "Молотый/в зёрнах",
                                                    "Описание вкуса", "Цена", "Объём упаковки"])
        conn = sqlite3.connect("data/coffee.sqlite")
        cur = conn.cursor()
        for i, values in enumerate(cur.execute("""SELECT * FROM Coffee""").fetchall()):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, value in enumerate(values):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(value)))
        self.tableWidget.resizeColumnsToContents()
        cur.close()
        conn.close()

    def add_edit_data(self):
        if self.sender().text() == "Добавить":
            self.addEditForm = AddEditForm("Добавить", self)
        elif self.sender().text() == "Изменить" and self.tableWidget.item(self.tableWidget.currentRow(), 0):
            self.addEditForm = AddEditForm("Изменить", self,
                                           column_id=self.tableWidget.item(self.tableWidget.currentRow(), 0).text())

        self.addEditForm.show()


class AddEditForm(QWidget, Ui_Edit_Form):
    def __init__(self, mode, window, column_id=None):
        super().__init__()
        self.setupUi(self)
        self.window = window
        self.mode = mode
        self.saveButton.clicked.connect(self.saveData)
        self.column_id = column_id
        if self.mode == "Изменить":
            conn = sqlite3.connect("data/coffee.sqlite")
            cur = conn.cursor()
            all_data = cur.execute(f"""SELECT * FROM Coffee WHERE id = {column_id}""").fetchall()[0]
            coffee_id, name, roasting, selection, description, price, value = map(str, all_data)
            self.nameInput.setText(name)
            self.roastingInput.setText(roasting)
            self.selectionSelect.setCurrentText(selection)
            self.descriptionInput.setText(description)
            self.priceInput.setText(price)
            self.valueInput.setText(value)

    def saveData(self):
        conn = sqlite3.connect("data/coffee.sqlite")
        cur = conn.cursor()

        name, roasting, selection, description, price, value = (self.nameInput.text(),
                                                                self.roastingInput.text(),
                                                                self.selectionSelect.currentText(),
                                                                self.descriptionInput.toPlainText(),
                                                                self.priceInput.text(), self.valueInput.text())

        all_values = [name, roasting, selection, description, price, value]
        for i in all_values:
            if not i.strip():
                self.textLabel.setText("Неправильный ввод данных")
                return
        for value in range(len(all_values)):
            if not all_values[value].isdigit():
                all_values[value] = f'"{all_values[value]}"'
        if self.mode == "Добавить":
            cur.execute(f"""INSERT INTO Coffee("Название сорта", "Степень обжарки", "Молотый/в зёрнах", 
            "Описание вкуса", "Цена", "Объём упаковки") VALUES({", ".join(all_values)})""")
        elif self.mode == "Изменить":
            string = ""
            for column_name, new_value in zip(["Название сорта", "Степень обжарки", "Молотый/в зёрнах",
                                               "Описание вкуса", "Цена", "Объём упаковки"], all_values):
                string += f'"{column_name}" = {new_value}' + ", "
            string = string[:-2]
            cur.execute(f"""UPDATE Coffee SET {string} WHERE "ID" = {self.column_id}""")
        conn.commit()
        cur.close()
        conn.close()
        self.window.load_data()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
