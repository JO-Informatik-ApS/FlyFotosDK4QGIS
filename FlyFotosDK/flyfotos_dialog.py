# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FlyfotosDialog
                                 A QGIS plugin
 Test Flyfotos
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-10-05
        git sha              : $Format:%H$
        copyright            : (C) 2020 by JO Informatik
        email                : support@jo-informatik.dk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os  # This is needed in the pyqgis console also
import xml.etree.cElementTree as ET
from operator import itemgetter
import datetime
import pathlib

from qgis.PyQt import uic, QtWidgets
from qgis.utils import iface
from qgis.core import QgsProject, QgsRasterLayer, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from PyQt5.QtCore import QUrl, QEventLoop, Qt, QSortFilterProxyModel, QRegExp
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QTableWidget, QVBoxLayout, QLineEdit, QTableView, QHeaderView
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from .flyfotosSettings import ConfigDialog
from .multifilter_proxy_model import MultiFilterProxyModel

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'flyfotos_dialog_base.ui'))

tokenUrl = (
    "https://%s.kort.flyfotos.dk/aarti/service?"
)

getLayer_format = 'crs=%s&format=image/png&layers=%s&styles&url='

# We're working with CRS 'EPSG:25832' for coordinate and layer calculations
serverProjection = 'EPSG:25832'
save_directory = "/capabilities/"
save_capabilities_filename = "GetCapabilities.xml"
save_dir = (
    os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
)
dir_path = pathlib.Path(save_dir + save_directory)
file_path = dir_path / save_capabilities_filename
layer_arr = []


class FlyfotosDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(FlyfotosDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        # Hide error message label on load
        self.label_error_message.hide()
        self.push_button_add_layer.clicked.connect(self.add_layer_onclick)
        self.push_button_close.clicked.connect(self.close_onclick)
        self.table_view_all.doubleClicked.connect(self.table_all_ondoubleclick)
        self.table_view_visible.doubleClicked.connect(
            self.table_visible_ondoubleclick)

        user_token_value = ConfigDialog.token_user_input_text
        token = ""
        if user_token_value != "":
            token = user_token_value

    def init_table(self, cred, reload):
        """[summary]
            Initializes tables with the GetCapabilities file for the given token.

        Args:

            cred (str): User token
            reload (bool): Indicator of whether the GetCapabilities has to be refreshed even though it is not old.
        """
        self.token = cred
        if self.is_capabilities_old() or reload:
            if layer_arr:
                layer_arr.clear()
            self.save_capabilities(self.get_from_url("", cred))
        # To show show_all_table, show_visible_table by default onload
        self.show_all_table()
        self.show_visible_table()

    def show_all_table(self):
        """[summary]
           Reads the GetCapabilities file and creates the all layer table from the result.
        """
        xml = self.read_capabilities()
        if len(xml) > 0 and xml != None:
            # Parse the GetCapabilities XML file
            try:
                tree = ET.XML(xml)
                et = ET.ElementTree(tree)
                et.write(file_path, encoding="utf-8", xml_declaration=False)
                root = et.getroot()
                # Tags have a special prefix. We are looking for Capability
                caps = root.find('{http://www.opengis.net/wms}Capability')
                # Tags have a special prefix. We are looking for Layer
                outer_layer = caps.find(
                    '{http://www.opengis.net/wms}Layer')
                # Tags have a special prefix. We are looking for Decades in Layer tag
                decades = outer_layer.findall(
                    '{http://www.opengis.net/wms}Layer')
            except Exception as e:
                print("There was an error parsing the Capabilities xml. ", e)
                self.errorBox(
                    "There was an error parsing the Capabilities xml. See the console for more information.")
                decades = []
        else:
            decades = []

        # Make sure the list is empty.
        layer_arr.clear()
        for decade in decades:
            # Tags have a special prefix. We are looking for Layer
            layers = decade.findall('{http://www.opengis.net/wms}Layer')
            # Append string, where the 1st element of aarti is formatet as "Aarti 1901-1910"
            # Remove the first 5 characters from aarti element to get the decade number text.
            decade_text = decade[0].text[5:]
            for layer in layers:
                t_minx = layer[5].attrib['minx']
                t_miny = layer[5].attrib['miny']
                t_maxx = layer[5].attrib['maxx']
                t_maxy = layer[5].attrib['maxy']
                # Add layer(decade, layerName, layerTitle, minx, miny, maxx, maxy, BBOX)
                layer_arr.append(
                    (decade_text, layer[0].text, layer[1].text,
                        QgsGeometry.fromWkt("POLYGON((" + t_minx + ' ' + t_miny + ',' +
                                            t_minx + ' ' + t_maxy + ',' + t_maxx + ' ' + t_maxy + ',' +
                                            t_maxx + ' ' + t_miny + ',' + t_minx + ' ' + t_miny + '))')
                     ))

            layer_arr.sort(key=itemgetter(0))
            self.model_all = QStandardItemModel(len(layer_arr), 4)
            self.filter_proxy_model = MultiFilterProxyModel()
            self.init_table_view(layer_arr, self.model_all,
                                 self.filter_proxy_model, self.table_view_all)

    def show_visible_table(self):
        """[summary]
        Creates the visible layer table given a list of layers and the current users view extent.

        The list is only created after an extent exists. If a new QGIS project is started, and no layers are added,
        visible layers will only be calculated after the plugin is opened, a layer is added, plugin window is cloed and opened again.
        """
        try:
            bbox = self.get_extent()
            if bbox != None:
                visible_layer_result = []

                for layer in layer_arr:
                    if layer[3].intersects(bbox):
                        # Append Decade, Name, Title as an item
                        visible_layer_result.append(
                            (layer[0], layer[1], layer[2]))

                if len(visible_layer_result) > 0:
                    self.model_visible = QStandardItemModel(
                        len(visible_layer_result), 4)
                    self.filter_proxy_model_visible = MultiFilterProxyModel()
                    self.init_table_view(visible_layer_result, self.model_visible,
                                         self.filter_proxy_model_visible, self.table_view_visible)
                else:
                    self.clear_model_visible()
        except:
            print("Geometry object is a None type")

    def init_table_view(self, layers, model, filter_proxy_model, table_view):
        model.setHorizontalHeaderLabels(['', 'Decade', 'Title'])
        i = 0
        for layer in layers:
            # Sort by 0,1,2 or 3 (decade, title, layer name, filtered data row number)
            item_text = QStandardItem(layer[0])
            item_text.setTextAlignment(Qt.AlignCenter)
            model.setItem(i, 1, item_text)
            model.setItem(i, 2, QStandardItem(layer[2]))
            model.setItem(i, 3, QStandardItem(layer[1]))
            row_number = QStandardItem()
            row_number.setData(i, Qt.EditRole)
            model.setItem(i, 4, row_number)
            i += 1

        filter_proxy_model.setSourceModel(model)
        self.line_edit_search_layer.setFocus()

        for i in range(1, 3):
            self.line_edit_search_layer.textChanged.connect(lambda text, col=i:
                                                            filter_proxy_model.setFilterByColumn(col, QRegExp(text, Qt.CaseInsensitive, QRegExp.FixedString)))

        table_view.setModel(model)
        table_view.hideColumn(3)
        table_view.hideColumn(4)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table_view.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        table_view.setColumnWidth(1, 90)
        table_view.setSortingEnabled(True)
        table_view.setModel(filter_proxy_model)

    def add_layer_onclick(self):
        """[summary]

            Adds selected layer to the canvas.
        """
        selected_rows = []
        is_tab_all = False
        if self.tab_widget.currentIndex() == 0:
            selected_rows = self.table_view_visible.selectionModel().selectedRows()
        else:
            selected_rows = self.table_view_all.selectionModel().selectedRows()
            is_tab_all = True

        # Since only a single row can be selected, first element will be the row
        if len(selected_rows) > 0:
            item = selected_rows[0]
            if is_tab_all:
                self.handle_item_click(item, self.model_all)
            else:
                self.handle_item_click(item, self.model_visible)

    def table_all_ondoubleclick(self, item):
        """[summary]
            Adds the double clicked layer to the canvas.
        Args:

            item (QTWidgetTableItem): The selected row of the table.
        """
        self.handle_item_click(item, self.model_all)

    def table_visible_ondoubleclick(self, item):
        """[summary]
            Adds the double clicked layer to the canvas.
        Args:

            item (QTWidgetTableItem): The selected row of the table.
        """
        self.handle_item_click(item, self.model_visible)

    def handle_item_click(self, item, model):
        row_number = item.row()
        print("row number", row_number)
        if row_number > -1:
            actual_row_number = item.sibling(row_number, 4).data()
            print("actual_row_number", actual_row_number)
            item_check = QStandardItem("√")
            item_check.setTextAlignment(Qt.AlignCenter)
            model.setItem(actual_row_number, 0, item_check)
            layer_title = model.data(model.index(actual_row_number, 2))
            layer_name = model.data(model.index(actual_row_number, 3))
            self.add_map_layer(layer_name, layer_title)

    def get_extent(self):
        """
        Gets the extent of users view.

        Returns:

            (QgsGeometry): A QgsGeometry object of the users extent bounding box. With a common projection.
        """
        # Get wktPolygon and convert it to a geometry object, where we can
        #  define precision and check the projection.
        try:
            rectangle = iface.mapCanvas().extent().asWktPolygon()
            geom = QgsGeometry.fromWkt(rectangle)
            crsSrcStr = self.get_projection()
            if crsSrcStr != serverProjection:
                crsDest = QgsCoordinateReferenceSystem(serverProjection)
                crsSrc = QgsCoordinateReferenceSystem(crsSrcStr)
                transformContext = QgsProject.instance().transformContext()
                xform = QgsCoordinateTransform(
                    crsSrc, crsDest, transformContext)
                geom.transform(xform)
                return geom
            else:
                return geom
        except Exception as e:
            print("Can not get extent/convert projection. ", e)

    def get_projection(self):
        """[summary]
            Finds the projection of the current project.
        Returns:

            str: The projection of the current project. Ex "EPSG:25832"
        """
        return QgsProject.instance().crs().authid()

    def add_map_layer(self, layer, title):
        """[summary]
            Loads a raster layer with the given name and title.

        Args:

            layer (str): Name of the layer. This is the primary key.
            title (str): Title of the layer to be shown in layer selection.
        """
        try:
            uri = str(getLayer_format % (serverProjection, layer)) + \
                str(tokenUrl % (self.token))
            rlayer = QgsRasterLayer(uri, title, 'wms')
            QgsProject.instance().addMapLayer(rlayer)
        except Exception as e:
            print("Can not get/load layer", e)
            self.errorBox(
                "Can not get/load a layer. Please refresh the plugin")

    def get_from_url(self, url, _token):
        """
        Get a file from given URL.

        Parameters:
            param1 (string): The url to call. Either an empty string or an url.
            This is used to make a call to a specific url.

            param2 (string): Token for the Flyfotos service. Used for getting the GetCapabilities file.


        Returns:
            (string): Returns file as string if the call was successful.

        """
        req = ""
        networkAccessManager = QNetworkAccessManager()

        if len(url) > 1:
            req = QNetworkRequest(QUrl(url))
        else:
            turl = str((tokenUrl % _token) +
                       "&request=GetCapabilities&service=WMS")
            req = QNetworkRequest(
                QUrl(turl))

        reply = networkAccessManager.get(req)
        event = QEventLoop()
        reply.finished.connect(event.quit)
        event.exec()
        er = reply.error()

        if er == QNetworkReply.NoError:
            bytes_string = reply.readAll()
            content_requests = bytes_string.data().decode('utf8')
            # Hide error message from plugin, if user's token is correct
            self.label_error_message.hide()
            if len(str(content_requests)) > 0:
                return content_requests
            else:
                self.errorBox(
                    "Something went wrong, the query content length was 0. Check if the token is correct.")
        else:
            self.errorBox(
                "Something went wrong. Check if the token is correct.")
            # Show error message label on plugin, if user's token is wrong
            self.label_error_message.show()
            self.clear_model_visible()
            self.clear_model_all()
            print(
                'http error {} - No content. Please check your token is correct'.format(er))

    def clear_model_visible(self):
        try:
            self.model_visible.clear()
            self.line_edit_search_layer.clear()
        except:
            pass

    def clear_model_all(self):
        try:
            self.model_all.clear()
            self.line_edit_search_layer.clear()
        except:
            pass

    def save_capabilities(self, inp):
        """[summary]
        Saves the GetCapability file string locally for later use

        Args:

            inp (str): The GetCapability file as a string.
        """
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
        file = open(file_path, "w")
        if len(str(inp)) > 0 and inp != None:
            file.write(inp)
        file.close()

    def read_capabilities(self):
        file = open(file_path, mode='r')
        capabilities_str = file.read()
        file.close()
        return capabilities_str

    def is_capabilities_old(self):
        """[summary]
        Checks if a new GetCapability file should be downloaded.

        File age is set to 1 day.

        Returns:

            bool: Boolean value that indicates if the file is older than a given date.
        """
        try:
            mtime = datetime.date.fromtimestamp(os.path.getmtime(
                file_path
            ))
        except OSError:
            mtime = datetime.date.fromisoformat('2020-02-20')

        return mtime < datetime.date.today()

    def map_move_end(self):
        """[summary]
        Orders the visible layer table to be created.
        """
        if not iface.mapCanvas().isDrawing():
            self.show_visible_table()

    def close_onclick(self):
        self.close()

    def errorBox(self, strText):
        """[summary]
        An error message popup if something goes wrong.

        Args:

            strText (str): Error text message
        """
        mydialog = QMessageBox()
        mydialog.setIcon(QMessageBox.Information)
        mydialog.setText(strText)
        mydialog.setStandardButtons(QMessageBox.Ok)
        mydialog.exec()
