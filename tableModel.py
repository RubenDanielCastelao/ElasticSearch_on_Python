

from PyQt6.QtCore import QAbstractTableModel, Qt



class TableModel(QAbstractTableModel):
    def __init__(self, datos):
        super().__init__()
        self.datos = datos

    def rowCount(self, parent=None):
        if self.datos is not None:
            return len(self.datos)
        else:
            return 0

    def columnCount(self, index):
        if self.datos is not None and len(self.datos) > 0:
            return len(self.datos[0])
        else:
            return 0

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                value = self.datos[index.row()][index.column()]
                return str(value)

    def setData(self, index, value, role):
        if role == Qt.ItemDataRole.EditRole:
            self.datos[index.row()][index.column()] = value
            return True
        return False

    def headerData(self, section, orientation, role):
        headers = ["Nombre", "Hora de registro", "Lugar de registro", "Referencia imagen"]
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section < len(headers):
                    return headers[section]
                else:
                    return ""  # return an empty string or a default value if section is out of range
            else:
                return str(section)