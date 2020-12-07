import os
from pathlib import Path
from qgis.gui import (QgsOptionsWidgetFactory)
from PyQt5.QtGui import QIcon

from .settings_config import ConfigOptionsPage


class MyPluginOptionsFactory(QgsOptionsWidgetFactory):

    def __init__(self):
        super().__init__()

    def icon(self):
        pdir = Path(os.path.dirname(__file__)).parent.resolve()
        icon_path = os.path.join(pdir, 'images/icon.png')
        return QIcon(icon_path)

    def createWidget(self, parent):
        return ConfigOptionsPage(parent)
