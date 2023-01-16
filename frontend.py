import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QLineEdit, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
import requests

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.title = "PyQt5 Task Categories"
        self.top = 100
        self.left = 100
        self.width = 600
        self.height = 400

        self.InitWindow()
        
    def InitWindow(self):
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)

        self.createTable()
        self.createButtons()

        vbox = QVBoxLayout()
        vbox.addWidget(self.table)
        vbox.addWidget(self.addButton)
        vbox.addWidget(self.removeButton)

        self.label = QLabel(self)
       
        self.label.move(20, 20)
        self.label.resize(200, 40)

        self.addButton.clicked.connect(self.addCategory)
        self.removeButton.clicked.connect(self.removeCategory)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addWidget(self.label)

        widget = QtWidgets.QWidget(self)
        widget.setLayout(hbox)
        self.setCentralWidget(widget)
        self.show()

    def createTable(self):
        self.table = QtWidgets.QTableWidget()
        self.table.setRowCount(5)
        self.table.setColumnCount(2)

        self.table.setHorizontalHeaderLabels(["Id", "Name"])
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)

        self.populateTable()

    def createButtons(self):
        self.addButton = QPushButton("Add", self)
        self.addButton.move(20, 100)
        self.removeButton = QPushButton("Remove", self)
        self.removeButton.move(100, 100)

    def populateTable(self):
        url = 'http://localhost:5000/categories'
        categories = requests.get(url).json()
        for i, category in enumerate(categories):
            self.table.setItem(i, 0, QTableWidgetItem(str(category['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(category['name']))

    def addCategory(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "Add Category", "Enter the category name:")

        if ok and name:
            url = 'http://localhost:5000/categories'
            requests.post(url, json={'name': name})
            self.populateTable()

    def removeCategory(self):
        selected = self.table.selectedItems()
        if selected:
            id = int(selected[0].text())
            url = f'http://localhost:5000/categories/{id}'
            requests.delete(url)
            self.populateTable()

App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())

