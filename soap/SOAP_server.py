from PyQt5 import QtCore, QtGui, QtWidgets
import os

import pandas as pd
from PandasModel import PandasModel

import csv
import xml.etree.ElementTree as et
import sqlite3

import multiprocessing
import time

from spyne import Application, ServiceBase, Unicode, rpc
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

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
        
        self.loadBtn = QtWidgets.QPushButton("Importuj z pliku", self)
        hLayout.addWidget(self.loadBtn)
        self.loadXMLBtn = QtWidgets.QPushButton("Importuj z pliku XML", self)
        hLayout.addWidget(self.loadXMLBtn)
        self.loadDBBtn = QtWidgets.QPushButton("Importuj z bazy danych", self)
        hLayout.addWidget(self.loadDBBtn)
        self.saveBtn = QtWidgets.QPushButton("Eksportuj do pliku", self)
        hLayout.addWidget(self.saveBtn)
        self.saveXMLBtn = QtWidgets.QPushButton("Eksportuj do pliku XML", self)
        hLayout.addWidget(self.saveXMLBtn)
        self.saveDBBtn = QtWidgets.QPushButton("Eksportuj do bazy danych", self)
        hLayout.addWidget(self.saveDBBtn)
        
        vLayout.addLayout(hLayout)
        self.pandasTv = QtWidgets.QTableView(self)
        vLayout.addWidget(self.pandasTv)
        
        self.loadBtn.clicked.connect(self.loadFile)
        self.loadXMLBtn.clicked.connect(self.loadXMLFile)
        self.loadDBBtn.clicked.connect(self.loadDBFile)
        self.saveBtn.clicked.connect(self.saveFile)
        self.saveXMLBtn.clicked.connect(self.saveXMLFile)
        self.saveDBBtn.clicked.connect(self.saveDBFile)
        
        self.pandasTv.setSortingEnabled(True)

    def loadFile(self):
        fileName = os.path.abspath('..\katalog.txt')
        df = pd.read_csv(fileName, sep=';', header=None, )
        columns = COLUMN_NAMES.copy()
        columns.append('drop')
        df.columns = columns
        df = df.drop('drop', 1)
        
        model = PandasModel(df)
        self.pandasTv.setModel(model)

    def loadXMLFile(self):
        parsedXML = et.parse('..\katalog.xml')

        dfcols = COLUMN_NAMES
        df = pd.DataFrame(columns=dfcols)
        
        for node in parsedXML.getroot():
            manufacturer = node.find('manufacturer')
            touch = node.attrib.get('touch')
            size = node.find('screen/size')
            resolution = node.find('screen/resolution')
            screen_type = node.find('screen/type')
            processor_name = node.find('processor/name')
            physical_cores = node.find('processor/physical_cores')
            clock_speed = node.find('processor/clock_speed')
            ram = node.find('ram')
            disc_type = node.attrib.get('type')
            storage = node.find('disc/storage')
            card_name = node.find('graphic_card/name')
            memory = node.find('graphic_card/memory')
            os = node.find('os')
            disc_reader = node.find('disc_reader')
            df = df.append( pd.Series( 
                [getvalueofnode(manufacturer), getvalueofnode(size), getvalueofnode(resolution),
                 getvalueofnode(screen_type), touch, getvalueofnode(processor_name), getvalueofnode(physical_cores),
                 getvalueofnode(clock_speed), getvalueofnode(ram), disc_type, getvalueofnode(storage),
                 getvalueofnode(card_name), getvalueofnode(memory), getvalueofnode(os), getvalueofnode(disc_reader)],
                index=dfcols) ,ignore_index=True)
        
        model = PandasModel(df)
        self.pandasTv.setModel(model)

    def loadDBFile(self):
        con = sqlite3.connect('katalog.db')
        cur = con.cursor()

        query = 'SELECT * FROM "catalogue";'
        
        df = pd.read_sql_query(query, con)

        df = df.drop('id', 1)
        df.columns = COLUMN_NAMES
        
        model = PandasModel(df)
        self.pandasTv.setModel(model)
    
    def saveFile(self):
        model = self.pandasTv.model()
        df = model.getDataFrame()
        
        df.to_csv('..\katalog.txt', sep=';', float_format="%d", header=None, index=False, quoting=csv.QUOTE_NONE, line_terminator=';\n')

    def saveXMLFile(self):
        model = self.pandasTv.model()
        df = model.getDataFrame()

        root = et.Element('laptops')

        for name, item in df.iterrows():
            laptop = et.SubElement(root, 'laptop')
            laptop.set('id', str(name))

            manufacturer = et.SubElement(laptop, 'manufacturer')
            manufacturer.text = str(item['producent'])
            
            screen = et.SubElement(laptop, 'screen')
            screen.set('touch', str(item['dotykowy']))
            screen_size = et.SubElement(screen, 'size')
            screen_size.text = str(item['przekątna'])
            screen_resolution = et.SubElement(screen, 'resolution')
            screen_resolution.text = str(item['ekran'])
            screen_type = et.SubElement(screen, 'type')
            screen_type.text = str(item['typ ekranu'])
            
            processor = et.SubElement(laptop, 'processor')
            processor_name = et.SubElement(processor, 'name')
            processor_name.text = str(item['procesor'])
            processor_cores = et.SubElement(processor, 'physical_cores')
            processor_cores.text = str(item['liczba rdzeni'])
            processor_speed = et.SubElement(processor, 'clock_speed')
            processor_speed.text = str(item['MHz'])
            
            ram = et.SubElement(laptop, 'ram')
            ram.text = str(item['RAM'])
            
            disc = et.SubElement(laptop, 'disc')
            disc.set('type', str(item['rodzaj dysku']))
            storage = et.SubElement(disc, 'storage')
            storage.text = str(item['pojemność dysku'])
            
            graphic_card = et.SubElement(laptop, 'graphic_card')
            graphic_card_name = et.SubElement(graphic_card, 'name')
            graphic_card_name.text = str(item['GPU'])
            graphic_card_memory = et.SubElement(graphic_card, 'memory')
            graphic_card_memory.text = str(item['pamięć GPU'])
            
            os = et.SubElement(laptop, 'os')
            os.text = str(item['OS'])
            
            disc_reader = et.SubElement(laptop, 'disc_reader')
            disc_reader.text = str(item['rodzaj napędu fizycznego'])

        output = et.tostring(root)

        with open("..\katalog.xml", "wb") as f:
            f.write(output)

    def saveDBFile(self):
        con = sqlite3.connect('katalog.db')
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS catalogue ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                    "producent TEXT,"
                    "diagonal TEXT,"
                    "screen TEXT,"
                    "screen_type TEXT,"
                    "touchscreen BOOLEAN,"
                    "processor TEXT,"
                    "cores INTEGER,"
                    "mhz INTEGER,"
                    "ram TEXT,"
                    "disc_capacity TEXT,"
                    "disc_type TEXT,"
                    "gpu TEXT,"
                    "gpu_ram TEXT,"
                    "os TEXT,"
                    "disc_drive TEXT)")

        model = self.pandasTv.model()
        df = model.getDataFrame()

        for name, item in df.iterrows():
            
            query = 'INSERT INTO catalogue (producent, diagonal, screen, screen_type, touchscreen, processor, \
                     cores, mhz, ram, disc_capacity, disc_type, gpu, gpu_ram, os, disc_drive) \
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
            cur.execute(query, (item['producent'], item['przekątna'], item['ekran'], item['typ ekranu'],
                                item['dotykowy'], item['procesor'], item['liczba rdzeni'], item['MHz'], item['RAM'],
                                item['pojemność dysku'], item['rodzaj dysku'], item['GPU'], item['pamięć GPU'],
                                item['OS'], item['rodzaj napędu fizycznego']))

        con.commit()
        con.close()

class SOAPService(ServiceBase):
    

    @rpc(Unicode, _returns=int)
    def count_laptops_by_producent(ctx, producent):
        con = sqlite3.connect('katalog.db')
        cur = con.cursor()
        cur.execute('SELECT COUNT(*) FROM "catalogue" WHERE "producent"=\''+producent+'\';')
        answer = cur.fetchall()
        print(answer)
        return answer[0][0]
    
    @rpc(Unicode, _returns=Unicode)
    def return_laptops_by_matrix(ctx, screen_type):
        con = sqlite3.connect('katalog.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM "catalogue" WHERE "screen_type"=\''+screen_type+'\';')
        answer = cur.fetchall()
        print(answer)
        return answer
    
    @rpc(Unicode, _returns=int)
    def count_laptops_by_resolution(ctx, diagonal):
        con = sqlite3.connect('katalog.db')
        cur = con.cursor()
        cur.execute('SELECT COUNT(*) FROM "catalogue" WHERE "diagonal"=\''+diagonal+'\';')
        answer = cur.fetchall()
        print(answer)
        return answer[0][0]

application = Application(
    services=[SOAPService],
    tns='http://tests.python-zeep.org/',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11())

application = WsgiApplication(application)

def serve_SOAP():
    from wsgiref.simple_server import make_server
    server = make_server('127.0.0.1', 8000, application)
    server.serve_forever()

def run_app():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

def getvalueofnode( node ):
    return node.text if node is not None else None

if __name__ == "__main__":
    pser = multiprocessing.Process(name='pser', target=serve_SOAP)
    pide = multiprocessing.Process(name='pide', target=run_app)
    pser.start()
    pide.start()
    pser.join()
    pide.join()
    
    
