"""Demo streamlit app herramienta asignación de recursos según demanda."""

import streamlit as st
import streamlit.components.v1 as components
import folium
#from streamlit_folium import st_folium
import numpy as np
import pandas as pd 
import geopandas as gpd
import funciones as f
import random
from shapely.geometry import Point, Polygon

#-------------------- DATA INICIAL ---------------------
# Definir el DataFrame 1: Cuadrantes y Necesidades
data1 = {
    'Cuadrante': ["SSC-12.01", "SSC-12.02", "SSC-12.03", "SSC-12.04", "SSC-12.05", "SSC-12.06", "SSC-12.07"],
    'Cuarteles': [0.88, 0.88, 0, 0, 0, 0.6, 0],
    'Necesidad': [0.97, 0.77, 0.75, 1.68, 0.7, 0.82, 0.83],
    'Oferta_total': [0,0,0,0,0,0,0],
    'Diferencia' : [0,0,0,0,0,0,0]
}
df1 = pd.DataFrame(data1)

# Definir el DataFrame 2: Medios disponibles y sus ofertas unitarias
data2 = {
    'Id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    'Medio': ['RPT', 'RPT', 'RPT', 'RPT','RPT', 'RPT','MTT','MTT','MTT','MTT','INF','INF'],
    'Oferta Unitaria': [1, 1, 1, 1,1,1,1.35,1.35,1.35,1.35,1.2,1.2],
    'Asignacion': [0, 0, 0, 0,0, 0, 0, 0,0, 0, 0, 0]  # Inicialmente sin asignación
}
df2 = pd.DataFrame(data2)

# Importar polígonos de cuadrantes
gdf = gpd.read_file("poniente.geojson")

#-------------------- ELEMENTOS VISUALES ---------------------
st.title("Asignación de recursos")

#-------------------- USER INPUT ---------------------
df2["name"] = df2["Id"].astype(str).str.cat(df2["Medio"], sep='-')

medios = list(df2["name"])
seleccion = st.multiselect("Escoger medios disponibles:", medios)

df2_filtrado = df2[df2["name"].isin(seleccion)]

df2_asignado, df1_actualizado = f.asignar_recursos(df1, df2_filtrado)
#-------------------- RESULTADOS ---------------------
col1, col2 = st.columns([2,1])

# Definir coordenadas centrales
center_lat = gdf.geometry.centroid.y.mean()
center_lon = gdf.geometry.centroid.x.mean()

# Mapa base
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=14,
)

# Agregar capa cuadrantes
for x in range(0,len(gdf)):
    f.transform_polygon(gdf["geometry"].iloc[x],gdf["CUADRANTE_"].iloc[x]).add_to(m)

# Agregar diferencia
for x in list(gdf["CUADRANTE_"].unique()):
    f.label_diferencia(x,df1_actualizado,gdf).add_to(m)

medios_asignados = df2_asignado[df2_asignado["Asignacion"]!=0]
for x in list(medios_asignados["Id"]):
    f.viz_medios(df2_asignado,x,gdf).add_to(m)

with col1:
    # Render the map in HTML
    map_html = m._repr_html_()

    # Display the map in Streamlit
    st.title("Folium Map in Streamlit")
    components.html(map_html)

with col2:
    st.dataframe(df2_asignado)
    st.dataframe(df1_actualizado)
