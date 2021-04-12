import os.path
import re
from PyQt5 import uic
from qgis.gui import (QgsOptionsPageWidget)
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtGui import QFont
from qgis.core import (QgsSettings)

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
        self.label_link_register.setText(urlLink)
        self.label_link_register.setFont(QFont('Arial', 9))
        self.label_link_register.setOpenExternalLinks(True)
        # Display url link to about page
        urlLink = "<a href=\"https://flyfotos.dk/da-dk/Om-FlyFotosdk\">here</a>"
        self.label_link.setText(urlLink)
        self.label_link.setFont(QFont('Arial', 9))
        self.label_link.setOpenExternalLinks(True)
        # Set Token value from QgsSettings
        user_data_read = QgsSettings()
        token = user_data_read.value("flyfotosdk/token", "")
        self.token_user_input_text = token
        self.line_edit_flyfotos_token.setText(token)

    def accept_dialog(self):
        # Check if token has correct format and continue
        regex = re.compile("^[0-9A-Za-z\-]{2,40}$")
        match = regex.match(str(self.line_edit_flyfotos_token.text()))
        if match:
            token_text = self.line_edit_flyfotos_token.text()
            self.token_user_input_text = token_text
            user_token_input = QgsSettings()
            user_token_input.setValue("flyfotosdk/token", token_text)
        else:
            print("User token validation error")
            setting_error_dialog = QMessageBox()
            setting_error_dialog.setIcon(QMessageBox.Information)
            setting_error_dialog.setText(
                "Token validation error: token format was incorrect, or it included forbidden characters. A token may consist of letters [a-zA-Z], numbers[0-9] and a dash '-'.")
            setting_error_dialog.setStandardButtons(QMessageBox.Ok)
            setting_error_dialog.exec()
