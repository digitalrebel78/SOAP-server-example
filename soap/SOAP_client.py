from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QLineEdit, QLabel
import os

import pandas as pd
from PandasModel import PandasModel

import csv
import xml.etree.ElementTree as et
import sqlite3

import time

from zeep import Client

COLUMN_NAMES = ['producent',
                'przekątna',
                'ekran',
                'typ ekranu',
                'dotykowy',
                'procesor',
                'liczba rdzeni',
                'MHz',
                'RAM',
                'pojemność dysku',
                'rodzaj dysku',
                'GPU',
                'pamięć GPU',
                'OS',
                'rodzaj napędu fizycznego']


class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=None)
        vLayout = QtWidgets.QVBoxLayout(self)
        hLayout = QtWidgets.QHBoxLayout()
        h2Layout = QtWidgets.QHBoxLayout()
        h3Layout = QtWidgets.QHBoxLayout()
        
        self.U1 = QtWidgets.QPushButton("Liczba laptopów od producenta:", self)
        hLayout.addWidget(self.U1)
        self.U2 = QtWidgets.QPushButton("Laptopy o matrycy:", self)
        hLayout.addWidget(self.U2)
        self.U3 = QtWidgets.QPushButton("Liczba laptopów o przekatnej:", self)
        hLayout.addWidget(self.U3)
        vLayout.addLayout(hLayout)

        self.linePrefix = QLabel(self)
        self.linePrefix.setText("Wprowadź argument:")
        h2Layout.addWidget(self.linePrefix)
        self.line = QLineEdit(self)
        h2Layout.addWidget(self.line)

        self.label = QLabel(self)
        h3Layout.addWidget(self.label)
        
        
        vLayout.addLayout(h2Layout)
        vLayout.addLayout(h3Layout)
        self.pandasTv = QtWidgets.QTableView(self)
        vLayout.addWidget(self.pandasTv)
        
        self.U1.clicked.connect(self.numberOfRecordsByProducent)
        self.U2.clicked.connect(self.laptopsByMatrix)
        self.U3.clicked.connect(self.numberOfRecordsByResolution)
        
        self.pandasTv.setSortingEnabled(True)

    def numberOfRecordsByProducent(self):
        client = Client(wsdl='http://127.0.0.1:8000/application.asmx?wsdl')
        producer = self.line.text()
        self.label.setText("Liczba laptopów od producenta " + producer + " - " + str(client.service.count_laptops_by_producent(producer)))

    def laptopsByMatrix(self):
        client = Client(wsdl='http://127.0.0.1:8000/application.asmx?wsdl')
        matrix = self.line.text()
        self.label.setText("Laptopy " + matrix + " - " + str(client.service.return_laptops_by_matrix(matrix)))

    def numberOfRecordsByResolution(self):
        client = Client(wsdl='http://127.0.0.1:8000/application.asmx?wsdl')
        resolution = self.line.text()
        self.label.setText("Liczba laptopów o przekatnej " + resolution + " - " + str(client.service.count_laptops_by_resolution(resolution)))
    

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

def getvalueofnode( node ):
    return node.text if node is not None else None

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
    
    
