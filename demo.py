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


# TODO Mapa muestra marcadores del csv
# TODO Buscar el evento del marcador y SET las nuevas coordenadas en el csv
# TODO Calcular el csv

# Configuración de página
st.set_page_config(page_title="Demo", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

#-------------------- DATA INICIAL ---------------------
# Definir el DataFrame 1: Cuadrantes y Necesidades
data1 = {
    'Cuadrante': ["SSC-12.01", "SSC-12.02", "SSC-12.03", "SSC-12.04", "SSC-12.05", "SSC-12.06", "SSC-12.07"],
    'Cuarteles': [0.88, 0.88, 0, 0, 0, 0.6, 0],
    'Necesidad': [1.09, 0.88, 0.83, 1.71, 0.76, 0.91, 0.85],
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

# Coordenadas predeterminadas para asignación de marcadores en polígonos
predefined_coords = {
    "SSC-12.01": [
        (13.711347, -89.245041), (13.706200, -89.243542), (13.709451, -89.238279),
        (13.704066, -89.229599), (13.704913, -89.238732)
    ],
    "SSC-12.02": [
        (13.699606, -89.244572), (13.696846, -89.242720), (13.698806, -89.234116),
        (13.689046, -89.240456), (13.685677, -89.242013)
    ],
    "SSC-12.03": [
        (13.685677, -89.242013), (13.697569, -89.219173), (13.685726, -89.232846),
        (13.687617, -89.225779), (13.687219, -89.220658)
    ],
    "SSC-12.04": [
        (13.725679, -89.234178), (13.723589, -89.230900), (13.716674, -89.242525),
        (13.715828, -89.237916), (13.714186, -89.233000)
    ],
    "SSC-12.05": [
        (13.714917, -89.228318), (13.712130, -89.221146), (13.710296, -89.226053),
        (13.724232, -89.226808), (13.721665, -89.219862)
    ],
    "SSC-12.06": [
        (13.719245, -89.212841), (13.720272, -89.207782), (13.711397, -89.216087),
        (13.706115, -89.219485), (13.708023, -89.215181)
    ],
    "SSC-12.07": [
        (13.724232, -89.248930), (13.720345, -89.254064), (13.714184, -89.251422),
        (13.718291, -89.251271), (13.708169, -89.251195)
    ]
}

#-------------------- ELEMENTOS VISUALES ---------------------
st.title("Asignación de recursos")

#-------------------- USER INPUT ---------------------

# Creación de columna "name" para relacionar con nombres de cuadrantes
df2["name"] = df2["Id"].astype(str).str.cat(df2["Medio"], sep='-')

if 'df2' not in st.session_state:
    st.session_state.df = df2

# Lista de medios
medios = list(st.session_state.df["name"])

# Objeto de selección
seleccion = st.multiselect("Escoger medios disponibles:", medios)

# Botón para calcular
if st.button("Calcular",type="primary") == False:

    #------------------ESTADO INICIAL----------------------
    # Definir coordenadas centrales
    center_lat = gdf.geometry.centroid.y.mean()
    center_lon = gdf.geometry.centroid.x.mean()

# NOTA: creación de mapas con función a ser implementado a futuro

    # Mapa base
    m1 = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=14,
    )

    # Agregar capa cuadrantes
    for x in range(0,len(gdf)):
        f.transform_polygon(gdf["geometry"].iloc[x],gdf["CUADRANTE_"].iloc[x]).add_to(m1)

    # Agregar diferencia
    for x in list(gdf["CUADRANTE_"].unique()):
        f.label_diferencia(x,df1,gdf).add_to(m1)

    # Convertir objeto de mapa a HTML
    map_html1 = m1._repr_html_()

    # Mostrar mapa
    components.html(map_html1, width=1200, height=750)

    # Mostrar DataFrame original de medios asignados
    st.write("Medios asignados:")
    st.dataframe(st.session_state.df[["Id","Medio","Oferta Unitaria","Asignacion"]],hide_index=True)

    # Mostrar DataFrame original de oferta y demanda
    st.write("Demanda y oferta actualizadas:")
    st.dataframe(df1, hide_index=True)

else:
    #-------------------- RESULTADOS ---------------------

    # Actualizar función
    df2_filtrado = st.session_state.df[st.session_state.df["name"].isin(seleccion)]
    df2_asignado, df1_actualizado = f.asignar_recursos(df1, df2_filtrado)

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

    # Agregar marcadores de medios asignados
    medios_asignados = df2_asignado[df2_asignado["Asignacion"] != 0] # Filtrar por medios que han sido asignados
    polygon_counter = {key: 0 for key in predefined_coords.keys()}
    for x in list(medios_asignados["Id"]):
        marker = f.viz_medios(df2_asignado, x, predefined_coords, polygon_counter)
        if marker:
            marker.add_to(m)

    # Convertir mapa a HTML
    map_html = m._repr_html_()

    # Mostrar mapa
    components.html(map_html, width=1200, height=750)

    # Mostrar DataFrame de medios asignados actualizado
    st.header("Medios asignados:")
    st.dataframe(df2_asignado[["Id","Medio","Oferta Unitaria","Asignacion"]],hide_index=True)

    # Mostrar DataFrame de demanda y oferta actualizado
    st.header("Demanda y oferta actualizadas:")
    st.dataframe(df1_actualizado, hide_index=True)
