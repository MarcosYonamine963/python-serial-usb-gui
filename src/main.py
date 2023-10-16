import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, 
    QComboBox, QLineEdit, QHBoxLayout, QRadioButton, QLabel
)
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import Qt

class SerialCommunication(QMainWindow):
    def __init__(self):
        super().__init__()

        self.display_as_hex = True
        self.is_connected = False

        self.predefined_data = {
            "ACK": "4F4B0D",
            "Requisitar Status": "02556C32",
            "Requisitar Número de Série": "025EDD59",
            "Testar Buzzer": "02611AE5",
            "Habilitar Login": "025901CA66",
            "Habilitar Logout": "025601DA58",
            "Desabilitar Login": "025900DA47",
            "Desabilitar Logout": "025600CA79",
            "Habilitar ACK de Comandos": "0262011309",
            "Desabilitar ACK de Comandos": "0262000328",
            "Habilitar ACK comandos AT": "0263012038",
            "Desabilitar ACK comandos AT": "0263003019",
            "Resetar Módulo": "025FCD78",
            "Restaurar ao Padrão de Fábrica": "025A9DDD"
        }

        self.initUI()
        self.serial_port = QSerialPort()
        self.serial_port.readyRead.connect(self.receive_data)

    def initUI(self):
        self.setWindowTitle("Serial Communication")
        self.setGeometry(100, 100, 1000, 600)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)

        self.text_edit_ascii = QTextEdit(self)
        self.text_edit_ascii.setReadOnly(True)

        self.text_edit_hex = QTextEdit(self)
        self.text_edit_hex.setReadOnly(True)

        self.send_button = QPushButton("Enviar", self)
        self.send_button.clicked.connect(self.send_data)

        self.connect_button = QPushButton("Conectar", self)
        self.connect_button.clicked.connect(self.connect_port)

        self.refresh_button = QPushButton("Atualizar Portas", self)
        self.refresh_button.clicked.connect(self.populate_ports_list)

        self.disconnect_button = QPushButton("Desconectar", self)
        self.disconnect_button.clicked.connect(self.disconnect_all_ports)

        self.clear_button = QPushButton("Limpar Texto", self)
        self.clear_button.clicked.connect(self.clear_text_edit)

        self.port_combobox = QComboBox(self)
        self.populate_ports_list()

        self.data_input = QLineEdit(self)
        self.data_input.returnPressed.connect(self.send_data_enter_pressed)

        self.ascii_radio = QRadioButton("ASCII", self)
        self.hex_radio = QRadioButton("Hexadecimal", self)
        self.hex_radio.setChecked(True)

        self.ascii_radio.toggled.connect(self.update_display_format)
        self.hex_radio.toggled.connect(self.update_display_format)

        send_layout = QHBoxLayout()
        send_layout.addWidget(self.data_input)
        send_layout.addWidget(self.ascii_radio)
        send_layout.addWidget(self.hex_radio)
        send_layout.addWidget(self.send_button)

        config_btns_layout = QHBoxLayout()
        config_btns_layout.addWidget(self.port_combobox)
        config_btns_layout.addWidget(self.connect_button)
        config_btns_layout.addWidget(self.disconnect_button)
        config_btns_layout.addWidget(self.refresh_button)
        config_btns_layout.addWidget(self.clear_button)

        text_edit_layout = QVBoxLayout()
        text_edit_layout.addWidget(self.text_edit)
        text_edit_layout.addWidget(self.text_edit_ascii)
        text_edit_layout.addWidget(self.text_edit_hex)
        text_edit_layout.addLayout(send_layout)

        h_layout = QHBoxLayout()
        h_layout.addLayout(text_edit_layout)

        self.predefined_buttons_layout = QVBoxLayout()
        h_layout.addLayout(self.predefined_buttons_layout)

        layout = QVBoxLayout()
        layout.addLayout(config_btns_layout)
        layout.addLayout(h_layout)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        for label, data in self.predefined_data.items():
            self.add_predefined_data_button(label, data)

    def add_predefined_data_button(self, label, data):
        button = QPushButton(label, self)
        button.clicked.connect(lambda: self.send_predefined_data(data))
        self.predefined_buttons_layout.addWidget(button)

    def populate_ports_list(self):
        self.port_combobox.clear()
        available_ports = QSerialPortInfo.availablePorts()
        for port_info in available_ports:
            self.port_combobox.addItem(port_info.portName())

        self.update_connection_status()

    def update_connection_status(self):
        if self.is_connected:
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
        else:
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)

    def connect_port(self):
        if self.serial_port.isOpen():
            self.text_edit.append("A porta já está conectada.")
        else:
            port_name = self.port_combobox.currentText()
            self.serial_port.setPortName(port_name)
            self.serial_port.setBaudRate(QSerialPort.Baud115200)

            if self.serial_port.open(QSerialPort.ReadWrite):
                self.text_edit.append(f"Porta serial aberta em {port_name} com baud rate 115200.")
                self.is_connected = True
                self.update_connection_status()
            else:
                self.text_edit.append(f"Falha ao abrir porta serial em {port_name}. Motivo: {self.serial_port.errorString()}")

    def send_data(self):
        if not self.serial_port.isOpen():
            self.text_edit.append("A porta serial não está aberta.")
            return

        data = self.data_input.text()
        if self.hex_radio.isChecked():
            try:
                data = bytes.fromhex(data)
            except ValueError:
                self.text_edit.append("Erro: Dados em formato hexadecimal inválido.")
                return
        else:
            data = data.encode('utf-8')

        if self.serial_port.write(data) == -1:
            self.text_edit.append(f"Erro ao enviar dados para a porta serial. Motivo: {self.serial_port.errorString()}")

        self.data_input.clear()

    def send_data_enter_pressed(self):
        self.send_data()

    def send_predefined_data(self, data):
        if not self.serial_port.isOpen():
            self.text_edit.append("A porta serial não está aberta.")
            return

        if self.hex_radio.isChecked():
            try:
                data = bytes.fromhex(data)
            except ValueError:
                self.text_edit.append("Erro: Dados em formato hexadecimal inválido.")
                return
        else:
            data = data.encode('utf-8')

        if self.serial_port.write(data) == -1:
            self.text_edit.append(f"Erro ao enviar dados para a porta serial. Motivo: {self.serial_port.errorString()}")

    def receive_data(self):
        data = self.serial_port.readAll()
        ascii_data = data.data().decode('utf-8')
        hex_data = data.toHex().data().decode('utf-8')

        self.text_edit_ascii.insertPlainText(f"{ascii_data}")
        self.text_edit_hex.insertPlainText(f"{hex_data}")

        if b'\x0d' in data:
            self.text_edit_hex.insertPlainText("\n")

    def disconnect_all_ports(self):
        if self.serial_port.isOpen():
            self.serial_port.close()
            self.text_edit.append("Porta serial desconectada.")
            self.is_connected = False
            self.update_connection_status()

    def update_display_format(self):
        self.display_as_hex = self.hex_radio.isChecked()

    def clear_text_edit(self):
        self.text_edit.clear()
        self.text_edit_ascii.clear()
        self.text_edit_hex.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SerialCommunication()
    window.show()
    sys.exit(app.exec_())
