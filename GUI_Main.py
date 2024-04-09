import sys
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGridLayout, QVBoxLayout, QHBoxLayout, QWidget,
                             QLabel, QPushButton, QComboBox,  QLineEdit,
                             QRadioButton, QGroupBox, QTableView, QAbstractItemView,QHeaderView, QMessageBox)
from tableModel import TableModel
from DBConnection import DBConnection
from PyQt6 import QtCore

index_name = None

class GUI_Main (QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ElasticSearch APP")

        self.resize(QSize(850, 700))

        self.operacion = "None"

        self.setStyleSheet("""
            QMainWindow {
                background-color: #a3a19b;
            }
        """)

        QApplication.instance().installEventFilter(self)

        vBox = QVBoxLayout()
        grid = QGridLayout()


        vBox.addLayout(grid)

        lblName = QLabel("Nombre")
        lblTimestamp = QLabel("Hora de registro")
        lblCoords = QLabel("Lugar de registro: ")
        lblCoordsLat = QLabel("Lat ")
        lblCoordsLon = QLabel("Lon ")
        lblImageTxt = QLabel("Referencia imagen")

        self.txtName=QLineEdit()
        self.txtTimestamp = QLineEdit()
        self.txtCoords_1= QLineEdit()
        self.txtCoords_2 = QLineEdit()
        self.txtImage = QLineEdit()

        coordsLine= QHBoxLayout()

        grid.addWidget(lblName, 0,0,1,1)
        grid.addWidget(lblTimestamp, 1, 0, 1, 1)
        grid.addWidget(lblCoords, 2,0,1,1)
        grid.addWidget(lblImageTxt, 3,0,1,1)

        coordsLine.addWidget(lblCoordsLat)
        coordsLine.addWidget(self.txtCoords_1)
        coordsLine.addWidget(lblCoordsLon)
        coordsLine.addWidget(self.txtCoords_2)

        grid.addWidget(self.txtName, 0,1,1,1)
        grid.addWidget(self.txtTimestamp, 1,1,1,1)
        grid.addLayout(coordsLine, 2,1,1,1)
        grid.addWidget(self.txtImage, 3,1,1,1)


        vBoxTable = QVBoxLayout()

        self.dataTable = QTableView()
        self.dataTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.dataTable.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        vBoxTable.addWidget(self.dataTable)

        self.addBttn = QPushButton("Añadir")
        self.editBttn = QPushButton("Editar")
        self.delBttn = QPushButton("Borrar")
        self.srchBttn = QPushButton("Buscar")
        self.addBttn.pressed.connect(self.on_addBttn_pressed)
        self.editBttn.pressed.connect(self.on_editBttn_pressed)
        self.delBttn.pressed.connect(self.on_delBttn_pressed)

        buttonBox = QHBoxLayout()
        buttonBox.setAlignment(Qt.AlignmentFlag.AlignTop)
        buttonBox.addWidget(self.srchBttn)
        buttonBox.addWidget(self.addBttn)
        buttonBox.addWidget(self.editBttn)
        buttonBox.addWidget(self.delBttn)

        vBoxTable.addLayout(buttonBox)

        conxBD = DBConnection("https://192.168.1.168:9200", "elastic", "password", index_name)
        conxBD.dbConnect()
        indexData = conxBD.loadIndex()
        conxBD.dbClose()

        self.indexDataModel = TableModel(indexData)
        self.dataTable.setModel(self.indexDataModel)
        self.select = self.dataTable.selectionModel()

        header = self.dataTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)

        vBox.addLayout(vBoxTable)

        hBoxButton = QHBoxLayout()
        self.txtIndex = QLineEdit()
        self.txtIndex.setPlaceholderText("Nombre del index")
        self.txtIndex.installEventFilter(self)
        self.exitButton = QPushButton("Salir")
        self.indexBttn = QPushButton("Cargar Index")
        self.saveBttn = QPushButton("Guardar Cambios")
        self.cancelBttn = QPushButton("Descartar Cambios")
        self.saveBttn.pressed.connect(self.on_saveBttn_pressed)
        self.cancelBttn.pressed.connect(self.on_cancelBttn_pressed)
        self.exitButton.clicked.connect(self.confirmExit)
        self.srchBttn.pressed.connect(self.on_searchBttn_pressed)
        hBoxButton.setAlignment(Qt.AlignmentFlag.AlignRight)
        hBoxButton.addWidget(self.cancelBttn)
        hBoxButton.addWidget(self.saveBttn)
        hBoxIndex = QHBoxLayout()
        hBoxIndex.addWidget(self.txtIndex)
        hBoxIndex.addWidget(self.indexBttn)
        self.blockEditBttns(False)
        self.blockControls(True)
        self.blockBttns(True)
        self.indexBttn.pressed.connect(self.changeIndex)
        vBox.addLayout(hBoxButton)
        vBox.addLayout(hBoxIndex)
        vBox.addWidget(self.exitButton)


        container = QWidget()

        container.setLayout(vBox)

        self.setCentralWidget(container)

        self.show()


    def on_searchBttn_pressed(self):
        self.operacion = "SEARCH"
        self.blockControls(False)
        self.blockBttns(False)
        self.blockEditBttns(True)
        self.clearFields()

    def on_addBttn_pressed(self):
        self.operacion = "ADD"
        self.blockControls(False)
        self.blockBttns(False)
        self.blockEditBttns(True)
        self.clearFields()

    def on_editBttn_pressed (self):

        if self.select.hasSelection():
            self.operacion = "EDIT"
            self.blockControls(False)
            self.blockBttns(False)
            self.blockEditBttns(True)
            self.cargarCamposDendeSeleccion()
        else:
            print ("Selecciona una fila")


    def on_delBttn_pressed(self):
        if self.select.hasSelection():
            self.operacion = "DELETE"
            self.blockControls(False)
            self.blockBttns(False)
            self.blockEditBttns(True)
            self.cargarCamposDendeSeleccion()
            print ("Pulse o botón gardar para borrar")
        else:
            print ("Selecciona una fila")


    def on_saveBttn_pressed(self):
        if self.operacion == "ADD":
            conxBD = DBConnection("https://192.168.1.168:9200", "elastic", "password", index_name)
            conxBD.dbConnect()

            data = [self.txtName.text(), self.txtTimestamp.text(), self.txtCoords_1.text(), self.txtCoords_2.text(), self.txtImage.text()]
            conxBD.addQuery(data)

            conxBD.dbClose()
            self.indexDataModel.datos.append ((data[0],
                                           data[1],
                                           {"lat": data[2], "lon": data[3]},
                                           data[4]))
            self.indexDataModel.layoutChanged.emit()

        if self.operacion == "EDIT":
            linhas = self.select.selectedRows()
            for linha in linhas:
                i = linha.row()
            conxBD = DBConnection("https://192.168.1.168:9200", "elastic", "password", index_name)
            conxBD.dbConnect()

            selected_row_data = self.get_selected_row_data()

            data = [self.txtName.text(), self.txtTimestamp.text(), self.txtCoords_1.text(), self.txtCoords_2.text(), self.txtImage.text()]
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"name": selected_row_data[0]}},
                            {"match": {"timestamp": selected_row_data[1]}}
                        ]
                    }
                }
            }

            conxBD.updateQuery(data, query)

            conxBD.dbClose()

            self.indexDataModel.datos[i] = (data[0],
                                           data[1],
                                           {"lat": data[2], "lon": data[3]},
                                           data[4])

            self.indexDataModel.layoutChanged.emit()


        if self.operacion == "DELETE":
            lines = self.select.selectedRows()
            for line in lines:
                i = line.row()
            conxBD = DBConnection("https://192.168.1.168:9200", "elastic", "password", index_name)
            conxBD.dbConnect()

            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"name": self.txtName.text()}},
                            {"match": {"timestamp": self.txtTimestamp.text()}}
                        ]
                    }
                }
            }

            conxBD.deleteQuery(query)

            conxBD.dbClose()
            del (self.indexDataModel.datos[i])
            self.indexDataModel.layoutChanged.emit()

        if self.operacion == "SEARCH":

            conxBD = DBConnection("https://192.168.1.168:9200", "elastic", "password", index_name)
            conxBD.dbConnect()

            if self.txtName.text():
                name_filter = "term"
                name_srch1 = "name"
                name_srch2 = self.txtName.text()
            else:
                name_filter = "exists"
                name_srch1 = "field"
                name_srch2 = "name"

            if self.txtTimestamp.text():
                timestamp_filter = "term"
                timestamp_srch1 = "timestamp"
                timestamp_srch2 = self.txtTimestamp.text()
            else:
                timestamp_filter = "exists"
                timestamp_srch1 = "field"
                timestamp_srch2 = "timestamp"

            lat = float(self.txtCoords_1.text()) if self.txtCoords_1.text() else None
            lon = float(self.txtCoords_2.text()) if self.txtCoords_2.text() else None

            if self.txtImage.text():
                image_filter = "term"
                image_srch1 = "image"
                image_srch2 = self.txtImage.text()
            else:
                image_filter = "exists"
                image_srch1 = "field"
                image_srch2 = "image"

            aux_query = [
                            {name_filter: {name_srch1: name_srch2}},
                            {timestamp_filter: {timestamp_srch1: timestamp_srch2}},
                            {image_filter: {image_srch1: image_srch2}}
                        ]

            if lat and lon:
                aux_query.append({
                    "geo_distance": {
                        "distance": "1km",
                        "pin"
                        "location": [float(lat), float(lon)]
                    }
                })

            query = {
                "query": {
                    "bool": {
                        "must": aux_query
                    }
                }
            }

            indexData = conxBD.searchQuery(query)
            conxBD.dbClose()

            self.indexDataModel = TableModel(indexData)
            self.dataTable.setModel(self.indexDataModel)
            self.select = self.dataTable.selectionModel()
            self.indexDataModel.layoutChanged.emit()

        self.blockControls(True)
        self.blockEditBttns(False)
        self.blockBttns(True)
        self.clearFields()


    def on_cancelBttn_pressed(self):
        self.operacion= None
        self.blockControls(True)
        self.blockEditBttns(False)
        self.blockBttns(True)
        self.clearFields()

    def blockBttns (self, opcion):
        self.saveBttn.setEnabled(not opcion)
        self.cancelBttn.setEnabled(not opcion)

    def blockEditBttns (self, opcion):
        self.editBttn.setEnabled(not opcion)
        self.addBttn.setEnabled(not opcion)
        self.delBttn.setEnabled(not opcion)


    def blockControls(self, opcion):
        self.txtName.setEnabled(not opcion)
        self.txtTimestamp.setEnabled(not opcion)
        self.txtCoords_1.setEnabled(not opcion)
        self.txtCoords_2.setEnabled(not opcion)
        self.txtImage.setEnabled(not opcion)

    def clearFields (self):
        self.txtName.setText('')
        self.txtTimestamp.setText('')
        self.txtCoords_1.setText('')
        self.txtCoords_2.setText('')
        self.txtImage.setText('')


    def cargarCamposDendeSeleccion(self):
        filas = self.select.selectedRows()
        for fila in filas:
            i = fila.row()
            self.txtName.setText(str(self.indexDataModel.datos[i][0]))
            self.txtTimestamp.setText(str(self.indexDataModel.datos[i][1]))
            data = self.indexDataModel.datos[i][2]
            self.txtCoords_1.setText(str(data['lat']))
            self.txtCoords_2.setText(str(data['lon']))
            self.txtImage.setText(str(self.indexDataModel.datos[i][3]))

    def confirmExit(self):
        QApplication.instance().removeEventFilter(self)
        reply = QMessageBox.question(self, 'Exit Confirmation',
                                     "Are you sure you want to exit?", QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.instance().quit()
        else:
            QTimer.singleShot(0, lambda: QApplication.instance().installEventFilter(self))


    def changeIndex(self):
        if self.txtIndex.text() == "":
            print("Introduce un index")
        else:
            aux = index_name
            index = self.txtIndex.text()
            self.change_index_name(index)
            print(index_name)
            conxBD = DBConnection("https://192.168.1.168:9200", "elastic", "password", index_name)
            try:
                conxBD.dbConnect()
            except Exception as e:
                print("Error al conectar a: " + conxBD.dbip + ": " + str(e))
                self.change_index_name(aux)
                return
            indexData = conxBD.loadIndex()
            conxBD.dbClose()

            if index_name == "app_index":
                self.blockEditBttns(False)
                self.blockControls(True)
                self.blockBttns(True)
            else:
                self.blockEditBttns(True)
                self.blockControls(True)
                self.blockBttns(True)
            self.indexDataModel = TableModel(indexData)
            self.dataTable.setModel(self.indexDataModel)
            self.select = self.dataTable.selectionModel()
            self.indexDataModel.layoutChanged.emit()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.KeyPress:
            if isinstance(event, QKeyEvent):
                if event.key() == Qt.Key.Key_Escape:
                    self.confirmExit()
                elif event.key() in (16777220, 16777221) and obj is self.txtIndex and self.txtIndex.hasFocus():
                    print('Enter pressed')
                    self.changeIndex()
        return super().eventFilter(obj, event)

    def get_selected_row_data(self):
        # Get the selected rows
        selected_rows = self.select.selectedRows()

        # If there are any selected rows
        if selected_rows:
            # Get the first selected row
            first_selected_row = selected_rows[0]

            # Get the row number
            row_number = first_selected_row.row()

            # Get the data for this row from the model
            row_data = self.indexDataModel.datos[row_number]

            return row_data

        # If there are no selected rows, return None
        return None

    @staticmethod
    def change_index_name(new_index_name):
        global index_name
        index_name = new_index_name

if __name__=="__main__":

    app = QApplication(sys.argv)
    window = GUI_Main()

    app.exec()