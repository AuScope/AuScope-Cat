import os
from PyQt6 import uic
from PyQt6 import QtWidgets
from auscopecat.nvcl import search_cql_tsg_df
import pandas as pd
import geopandas as gpd
from shapely import wkt
from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsProject
import requests
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
        searchText = self.searchText.toPlainText()
        print(f'{searchText=}')
        df = None
        df = search_cql_tsg_df(prov='WA', name = searchText, bbox='110.,-44.,156,-9.')
        geometry = wkt.loads(df["gsmlp:shape"])
        gdf = gpd.GeoDataFrame(df, geometry=geometry,crs="EPSG:4326")
        geojson_string = gdf.to_json()
        service_url = "mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
        service_uri = f"type=xyz&zmin=0&zmax=21&url=https://{requests.utils.quote(service_url)}"
        baselayer = QgsRasterLayer(service_uri, "GoogleSatellite", "wms")

        qgsInstance =QgsProject.instance()
        activeLayers = list(qgsInstance.mapLayers().keys())

        if len(activeLayers):
            qgsInstance.removeMapLayers(activeLayers)
        if baselayer.isValid():
            qgsInstance.addMapLayer(baselayer)

        bhLayer = QgsVectorLayer(geojson_string, "NVCL", "ogr")
        if bhLayer.isValid():
            qgsInstance.addMapLayer(bhLayer)
            print("AuscopecatDialog loaded successfully.")
        else:
            print("AuscopecatDialog failed to load!")