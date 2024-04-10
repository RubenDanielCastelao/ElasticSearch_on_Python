import sys
from PyQt6.QtCore import QSize, Qt, QTimer, QRegularExpression, QTime, QDateTime
from PyQt6.QtGui import QKeyEvent, QIntValidator, QRegularExpressionValidator, QClipboard
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGridLayout, QVBoxLayout, QHBoxLayout, QWidget,
                             QLabel, QPushButton, QComboBox,  QLineEdit, QCheckBox,
                             QRadioButton, QGroupBox, QTableView, QAbstractItemView,QHeaderView, QMessageBox, QSlider, QDateTimeEdit)
from tableModel import TableModel
from DBConnection import DBConnection
from PyQt6 import QtCore
import os


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
            QPushButton:disabled {
                background-color: #D3D3D3;
                color: #808080;
            }
            QLineEdit:disabled {
                background-color: #D3D3D3;
                color: #808080;
            }
            QCheckBox:disabled {
                background-color: #a3a19b;
                color: #808080;
            }
            QDateTimeEdit:disabled {
                background-color: #D3D3D3;
                color: #808080;
            }
            QSlider:disabled {
                background-color: #D3D3D3;
                color: #808080;
            }
        """)

        QApplication.instance().installEventFilter(self)

        vBox = QVBoxLayout()
        grid = QGridLayout()

        vBox.addLayout(grid)

        lblName = QLabel("Nombre: ")
        lblTimestamp = QLabel("Hora de registro de: ")
        lblTimestamp_2 = QLabel(" a ")
        lblCoords = QLabel("Lugar de registro: ")
        lblCoordsLat = QLabel("Lat ")
        lblCoordsLon = QLabel("Lon ")
        lblSlider = QLabel("Distancia: ")
        lblImageTxt = QLabel("Referencia imagen: ")

        self.txtName = QLineEdit()
        self.dateTimeEdit = QDateTimeEdit(self)
        self.dateTimeEditRange = QDateTimeEdit(self)
        self.dateTimeEdit.setDisplayFormat("yyyy-MM-dd'T'HH:mm:ss.zzz")
        self.dateTimeEditRange.setDisplayFormat("yyyy-MM-dd'T'HH:mm:ss.zzz")
        self.dateCheck = QCheckBox(" Filtrar por fecha")
        self.txtCoords_1 = QLineEdit()
        self.txtCoords_2 = QLineEdit()
        self.txtKmSlider = QLineEdit()
        self.kmSlider = QSlider(Qt.Orientation.Horizontal, self)
        self.txtImage = QLineEdit()

        self.txtKmSlider.setMaxLength(3)
        self.txtKmSlider.setFixedWidth(30)

        self.dateCheck.setFixedWidth(150)
        self.dateCheck.stateChanged.connect(self.toggleDateTimeEdit)
        self.dateCheck.installEventFilter(self)

        self.kmSlider.setGeometry(50, 50, 200, 50)
        self.kmSlider.setMinimum(0)
        self.kmSlider.setMaximum(100)
        self.kmSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.kmSlider.setTickInterval(2)

        # Connect the slider's valueChanged signal to the updateLineEdit method
        self.kmSlider.valueChanged.connect(self.updateLineEdit)
        # Connect the QLineEdit's textChanged signal to the updateSlider method
        self.txtKmSlider.textChanged.connect(self.updateSlider)

        # Create a QRegExp object with a regular expression that matches only integers
        regex = QRegularExpression("^\\d*$")

        # Create a QRegExpValidator object with the QRegExp
        validator = QRegularExpressionValidator(regex)

        # Set the validator on the QLineEdit
        self.txtKmSlider.setValidator(validator)

        coordsLine = QHBoxLayout()
        kmLine = QHBoxLayout()
        hourLine = QHBoxLayout()

        lblSlider.setFixedWidth(90)
        kmLine.addWidget(lblSlider)
        kmLine.addWidget(self.txtKmSlider)

        lblName.setFixedWidth(120)
        grid.addWidget(lblName, 0, 0, 1, 1)
        lblTimestamp.setFixedWidth(150)
        grid.addWidget(lblTimestamp, 1, 0, 1, 1)
        lblCoords.setFixedWidth(120)
        grid.addWidget(lblCoords, 2,0,1,1)
        grid.addLayout(kmLine, 3,0,1,1)
        lblImageTxt.setFixedWidth(130)
        grid.addWidget(lblImageTxt, 5,0,1,1)

        coordsLine.addWidget(lblCoordsLat)
        coordsLine.addWidget(self.txtCoords_1)
        coordsLine.addWidget(lblCoordsLon)
        coordsLine.addWidget(self.txtCoords_2)

        self.dateTimeEdit.setMinimumSize(250, 0)
        self.dateTimeEditRange.setMinimumSize(250, 0)

        hourLine.addWidget(self.dateTimeEdit)
        hourLine.addWidget(lblTimestamp_2)
        hourLine.addWidget(self.dateTimeEditRange)
        hourLine.addWidget(self.dateCheck)

        grid.addWidget(self.txtName, 0,1,1,1)
        grid.addLayout(hourLine, 1,1,1,1)
        grid.addLayout(coordsLine, 2,1,1,1)
        grid.addWidget(self.kmSlider, 3,1,1,1)
        grid.addWidget(self.txtImage, 5,1,1,1)

        vBoxTable = QVBoxLayout()

        self.dataTable = QTableView()
        self.dataTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.dataTable.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.dataTable.doubleClicked.connect(self.copy_cell_data)
        vBoxTable.addWidget(self.dataTable)

        self.addBttn = QPushButton("Añadir")
        self.editBttn = QPushButton("Editar")
        self.delBttn = QPushButton("Borrar")
        self.srchBttn = QPushButton("Buscar")
        self.addBttn.pressed.connect(self.on_addBttn_pressed)
        self.addBttn.setShortcut("Ctrl+A")
        self.editBttn.pressed.connect(self.on_editBttn_pressed)
        self.editBttn.setShortcut("Ctrl+E")
        self.delBttn.pressed.connect(self.on_delBttn_pressed)
        self.delBttn.setShortcut("Ctrl+D")
        self.srchBttn.pressed.connect(self.on_searchBttn_pressed)
        self.srchBttn.setShortcut("Ctrl+F")

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
        self.txtIndex.installEventFilter(self)
        self.exitButton = QPushButton("Salir")
        self.indexBttn = QPushButton("Cargar Index")
        self.saveBttn = QPushButton("Guardar Cambios")
        self.cancelBttn = QPushButton("Descartar Cambios")
        self.saveBttn.pressed.connect(self.on_saveBttn_pressed)
        self.saveBttn.setShortcut("Shift+Return")
        self.cancelBttn.pressed.connect(self.on_cancelBttn_pressed)
        self.cancelBttn.setShortcut("Shift+Backspace")
        self.exitButton.clicked.connect(self.confirmExit)
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

        self.txtIndex.setFocus()

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
        self.txtKmSlider.setText('0')
        self.dateTimeEdit.setEnabled(False)
        self.dateTimeEditRange.setEnabled(False)
        self.txtName.setFocus()
        self.reloadModel()

    def on_addBttn_pressed(self):
        self.operacion = "ADD"
        self.blockControls(False)
        self.blockBttns(False)
        self.blockEditBttns(True)
        self.clearFields()
        self.txtKmSlider.setEnabled(False)
        self.kmSlider.setEnabled(False)
        self.dateCheck.setEnabled(False)
        self.dateTimeEditRange.setEnabled(False)
        self.txtName.setFocus()

    def on_editBttn_pressed (self):

        if self.select.hasSelection():
            self.operacion = "EDIT"
            self.blockControls(False)
            self.blockBttns(False)
            self.blockEditBttns(True)
            self.loadFieldsFromSelection()
            self.txtKmSlider.setEnabled(False)
            self.kmSlider.setEnabled(False)
            self.dateCheck.setEnabled(False)
            self.dateTimeEditRange.setEnabled(False)
            self.txtName.setFocus()
        else:
            print ("Selecciona una fila")


    def on_delBttn_pressed(self):
        if self.select.hasSelection():
            self.operacion = "DELETE"
            self.blockControls(False)
            self.blockBttns(False)
            self.blockEditBttns(True)
            self.loadFieldsFromSelection()
            self.txtKmSlider.setEnabled(False)
            self.kmSlider.setEnabled(False)
            self.dateCheck.setEnabled(False)
            self.dateTimeEditRange.setEnabled(False)
            self.delBttn.setFocus()
            print ("Pulse o botón gardar para borrar")
        else:
            print ("Selecciona una fila")


    def on_saveBttn_pressed(self):
        if self.operacion == "ADD":
            conxBD = DBConnection("https://192.168.1.168:9200", "elastic", "password", index_name)
            conxBD.dbConnect()

            data = [self.txtName.text(), self.dateTimeEdit.text(), self.txtCoords_1.text(), self.txtCoords_2.text(), self.txtImage.text()]
            conxBD.addQuery(data)

            conxBD.dbClose()
            self.indexDataModel.datos.append ((data[0],
                                           data[1],
                                           {"lat": float(data[2]), "lon": float(data[3])},
                                           data[4]))
            self.indexDataModel.layoutChanged.emit()

        if self.operacion == "EDIT":
            linhas = self.select.selectedRows()
            for linha in linhas:
                i = linha.row()
            conxBD = DBConnection("https://192.168.1.168:9200", "elastic", "password", index_name)
            conxBD.dbConnect()

            selected_row_data = self.get_selected_row_data()

            data = [self.txtName.text(), self.dateTimeEdit.text(), self.txtCoords_1.text(), self.txtCoords_2.text(), self.txtImage.text()]

            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"name": selected_row_data[0]}},
                            {"match": {"timestamp": selected_row_data[1]}},
                            {"match": {"image": selected_row_data[3]}}
                        ]
                    }
                }
            }

            print(query)

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
                            {"match": {"timestamp": self.dateTimeEdit.date().toString("yyyy-MM-dd") + "T" + self.dateTimeEdit.time().toString("HH:mm:ss")}},
                            {"match": {"image": self.txtImage.text()}}
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
                name_filter = "wildcard"
                name_srch1 = "name"
                name_srch2 = "*" + self.txtName.text() + "*"
            else:
                name_filter = "exists"
                name_srch1 = "field"
                name_srch2 = "name"

            if self.dateCheck.isChecked():
                timestamp_filter = "range"
                timestamp_srch1 = "timestamp"
                timestamp_srch2 = {
                    "gte": self.dateTimeEdit.date().toString("yyyy-MM-dd") + "T" + self.dateTimeEdit.time().toString(
                        "HH:mm:ss"),
                    "lte": self.dateTimeEditRange.date().toString(
                        "yyyy-MM-dd") + "T" + self.dateTimeEditRange.time().toString("HH:mm:ss"),
                    "format": "yyyy-MM-dd'T'HH:mm:ss"
                }
            else:
                timestamp_filter = "exists"
                timestamp_srch1 = "field"
                timestamp_srch2 = "timestamp"

            lat = float(self.txtCoords_1.text()) if self.txtCoords_1.text() else None
            lon = float(self.txtCoords_2.text()) if self.txtCoords_2.text() else None

            distance = self.txtKmSlider.text() + "km"

            if self.txtImage.text():
                image_filter = "wildcard"
                image_srch1 = "image"
                image_srch2 = "*" + self.txtImage.text() + "*"
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
                        "distance": distance,
                        "location": {"lat": float(lat), "lon": float(lon)}
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
        self.srchBttn.setEnabled(not opcion)


    def blockControls(self, opcion):
        self.txtName.setEnabled(not opcion)
        self.dateTimeEdit.setEnabled(not opcion)
        self.dateTimeEditRange.setEnabled(not opcion)
        self.txtCoords_1.setEnabled(not opcion)
        self.txtCoords_2.setEnabled(not opcion)
        self.txtImage.setEnabled(not opcion)
        self.txtKmSlider.setEnabled(not opcion)
        self.kmSlider.setEnabled(not opcion)
        self.dateCheck.setEnabled(not opcion)

    def clearFields (self):
        self.txtName.setText('')
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.txtCoords_1.setText('')
        self.txtCoords_2.setText('')
        self.txtImage.setText('')
        self.txtKmSlider.setText('')
        self.kmSlider.setValue(0)
        self.dateCheck.setChecked(False)

    def loadFieldsFromSelection(self):
        filas = self.select.selectedRows()
        for fila in filas:
            i = fila.row()
            self.txtName.setText(str(self.indexDataModel.datos[i][0]))

            # Convert the string to a QDateTime object
            datetime_str = str(self.indexDataModel.datos[i][1])

            # Truncate the microseconds
            datetime_str = datetime_str[:23]

            datetime_obj = QDateTime.fromString(datetime_str, "yyyy-MM-dd'T'HH:mm:ss.zzz")

            self.dateTimeEdit.setDateTime(datetime_obj)

            data = self.indexDataModel.datos[i][2]
            self.txtCoords_1.setText(str(data['lat']))
            self.txtCoords_2.setText(str(data['lon']))
            self.txtImage.setText(str(self.indexDataModel.datos[i][3]))

    def confirmExit(self):
        QApplication.instance().removeEventFilter(self)
        reply = QMessageBox.question(self, '¿Salir?',
                                     "¿Estás seguro de que quieres salir?", QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.instance().quit()


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
                elif event.key() in (16777220, 16777221) and obj is self.txtName and self.txtName.hasFocus():
                    if not self.dateCheck.isEnabled():
                        self.dateTimeEdit.setFocus()
                    else:
                        self.dateCheck.setFocus()
                elif event.key() in (16777220, 16777221) and obj is self.dateCheck and self.dateCheck.hasFocus():
                    if self.dateCheck.isChecked():
                        self.dateTimeEdit.setFocus()
                    else:
                        self.txtCoords_1.setFocus()
                elif event.key() in (16777220, 16777221) and obj is self.dateTimeEdit and self.dateTimeEdit.hasFocus():
                    self.dateTimeEditRange.setFocus()
                elif event.key() in (16777220, 16777221) and obj is self.dateTimeEditRange and self.dateTimeEditRange.hasFocus():
                    self.txtCoords_1.setFocus()
                elif event.key() in (16777220, 16777221) and obj is self.txtCoords_1 and self.txtCoords_1.hasFocus():
                    self.txtCoords_2.setFocus()
                elif event.key() in (16777220, 16777221) and obj is self.txtCoords_2 and self.txtCoords_2.hasFocus():
                    self.txtKmSlider.setFocus()
                elif event.key() in (16777220, 16777221) and obj is self.txtKmSlider and self.txtKmSlider.hasFocus():
                    self.txtImage.setFocus()
                elif event.key() in (16777220, 16777221) and obj is self.txtImage and self.txtImage.hasFocus():
                    self.saveBttn.setFocus()
                if event.key() == Qt.Key.Key_Space and obj is self.dateCheck and self.dateCheck.hasFocus():
                    # Toggle the checkbox state
                    self.dateCheck.setChecked(not self.dateCheck.isChecked())
                    return True
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

    def updateLineEdit(self):
        # Get the current value of the slider
        slider_value = self.kmSlider.value()
        # Update the QLineEdit's text with the slider's value
        self.txtKmSlider.setText(str(slider_value))

    def updateSlider(self):
        # Get the current text of the QLineEdit
        line_edit_text = self.txtKmSlider.text()
        if line_edit_text == '':
            # If the QLineEdit is empty, set the QSlider's value to 0
            self.kmSlider.setValue(0)
        else:
            try:
                # Try to convert the text to an integer
                value = int(line_edit_text)
            except ValueError:
                # If the conversion fails, return from the method without updating the QSlider
                return
            # If the conversion succeeds, update the QSlider's value
            self.kmSlider.setValue(value)

    def showEvent(self, event):
        super().showEvent(event)
        self.txtIndex.setFocus()

    def toggleDateTimeEdit(self):
        if self.dateCheck.isChecked():
            self.dateTimeEdit.setEnabled(True)
            self.dateTimeEditRange.setEnabled(True)
        else:
            self.dateTimeEdit.setEnabled(False)
            self.dateTimeEditRange.setEnabled(False)

    def reloadModel(self):
        conxBD = DBConnection("https://192.168.1.168:9200", "elastic", "password", index_name)
        conxBD.dbConnect()
        indexData = conxBD.loadIndex()
        conxBD.dbClose()

        self.indexDataModel = TableModel(indexData)
        self.dataTable.setModel(self.indexDataModel)
        self.select = self.dataTable.selectionModel()
        self.indexDataModel.layoutChanged.emit()



    def copy_cell_data(self, index):
        # Get the model from the index
        model = index.model()

        # Get the data for the clicked cell
        cell_data = model.data(index)

        # Copy the data to the clipboard
        QApplication.clipboard().setText(str(cell_data))

    @staticmethod
    def change_index_name(new_index_name):
        global index_name
        index_name = new_index_name

if __name__=="__main__":

    app = QApplication(sys.argv)
    window = GUI_Main()

    app.exec()