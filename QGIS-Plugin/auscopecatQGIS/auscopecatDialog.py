import os

import geopandas as gpd
import requests
from PyQt6 import QtWidgets, uic
from qgis.core import QgsProject, QgsRasterLayer, QgsVectorLayer
from shapely import wkt

from auscopecat.nvcl import search_cql_tsg_df

# Define the base and the form class from your UI file
# Ensure the path is correct relative to the Python file
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'auscopecat.ui')) #

class AuscopecatDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(AuscopecatDialog, self).__init__(parent)
        self.setupUi(self)
        self.searchButton.clicked.connect(self.on_search) #

    def on_search(self):
        """Slot (method) to be called when the button is clicked."""
        searchtext = self.searchText.toPlainText()
        print(f'{searchtext=}')
        df = None
        df = search_cql_tsg_df(prov='WA', name = searchtext, bbox='110.,-44.,156,-9.')
        geometry = wkt.loads(df["gsmlp:shape"])
        gdf = gpd.GeoDataFrame(df, geometry=geometry,crs="EPSG:4326")
        geojson_string = gdf.to_json()
        service_url = "mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
        service_uri = f"type=xyz&zmin=0&zmax=21&url=https://{requests.utils.quote(service_url)}"
        baselayer = QgsRasterLayer(service_uri, "GoogleSatellite", "wms")

        qgs_instance =QgsProject.instance()
        active_layers = list(qgs_instance.mapLayers().keys())

        if len(active_layers):
            qgs_instance.removeMapLayers(active_layers)
        if baselayer.isValid():
            qgs_instance.addMapLayer(baselayer)

        bh_layer = QgsVectorLayer(geojson_string, "NVCL", "ogr")
        if bh_layer.isValid():
            qgs_instance.addMapLayer(bh_layer)
            print("AuscopecatDialog loaded successfully.")
        else:
            print("AuscopecatDialog failed to load!")
