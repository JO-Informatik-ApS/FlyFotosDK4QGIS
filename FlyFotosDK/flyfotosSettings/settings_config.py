import os.path
from PyQt5 import uic
from qgis.gui import (QgsOptionsPageWidget)
from PyQt5.QtWidgets import QVBoxLayout, QMessageBox
from PyQt5.QtGui import QFont, QRegExpValidator
from qgis.core import (QgsSettings)
from PyQt5.QtCore import QRegExp

WIDGET, BASE = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'flyfotos_settings.ui')
)


class ConfigOptionsPage(QgsOptionsPageWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.config_widget = ConfigDialog()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setMargin(0)
        self.setLayout(layout)
        layout.addWidget(self.config_widget)
        self.setObjectName('widgetOptions')

    def apply(self):
        self.config_widget.accept_dialog()


class ConfigDialog(WIDGET, BASE):
    """[summary]
        This class deals with saving and reading the user token inside the QGIS settings.
    """
    token_user_input_text = ""

    def __init__(self):
        super(ConfigDialog, self).__init__(None)
        self.setupUi(self)
        # Display url link to contact page
        urlLink = "<a href=\"https://flyfotos.dk/da-dk/Produkter/Adgang\">Please contact us</a>"
        self.labelLinkRegister.setText(urlLink)
        self.labelLinkRegister.setFont(QFont('Arial', 9))
        self.labelLinkRegister.setOpenExternalLinks(True)
        # Display url link to about page
        urlLink = "<a href=\"https://flyfotos.dk/da-dk/Om-FlyFotosdk\">here</a>"
        self.labelLink.setText(urlLink)
        self.labelLink.setFont(QFont('Arial', 9))
        self.labelLink.setOpenExternalLinks(True)
        # Set Token value from QgsSettings
        user_data_read = QgsSettings()
        token = user_data_read.value("flyfotosdk/token", "")
        self.token_user_input_text = token
        self.lineEditFlyfotosToken.setText(token)

    def accept_dialog(self):
        reg_exp = QRegExp("^[a-zA-Z0-9\-]{2,40}$")
        reg_exp_validator = QRegExpValidator(reg_exp, self)
        user_input_check = self.lineEditFlyfotosToken.setValidator(
            reg_exp_validator)
        if user_input_check:
            token_text = self.lineEditFlyfotosToken.text()
            self.token_user_input_text = token_text
            user_token_input = QgsSettings()
            user_token_input.setValue("flyfotosdk/token", token_text)
        else:
            print("User token validation error")
            settingErrorDialog = QMessageBox()
            settingErrorDialog.setIcon(QMessageBox.Information)
            settingErrorDialog.setText(
                "Token validation error: token format was incorrect, or it included forbidden characters. A token may consist of letters [a-zA-Z], numbers[0-9] and a dash '-'.")
            settingErrorDialog.setStandardButtons(QMessageBox.Ok)
            settingErrorDialog.exec()
