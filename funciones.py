"""Funciones para app streamlit demo herramienta asignación de recursos según demanda."""

import streamlit as st 
#from streamlit_folium import st_folium
import numpy as np
import pandas as pd 
import folium
import random
from shapely.geometry import Point, Polygon

# Función para asignar recursos a los cuadrantes y actualizar 'Oferta_total'
def asignar_recursos(df_necesidades, df_recursos):
    # Iterar sobre cada cuadrante
    for index, row in df_necesidades.iterrows():
        cuadrante = row['Cuadrante']
        necesidad = row['Necesidad']
        #print(f"\nAsignando recursos para Cuadrante {cuadrante} con necesidad {necesidad}")
        
        # Encontrar recursos disponibles
        recursos_disponibles = df_recursos[df_recursos['Asignacion'] == 0]
        
        # Asignar recursos hasta cubrir la necesidad
        while necesidad > 0 and not recursos_disponibles.empty:
            # Tomar el primer recurso disponible
            recurso_index = recursos_disponibles.index[0]
            oferta_unitaria = recursos_disponibles.loc[recurso_index, 'Oferta Unitaria']
            
            # Asignar el recurso al cuadrante
            df_recursos.at[recurso_index, 'Asignacion'] = cuadrante
            necesidad -= oferta_unitaria
            #print(f"Asignado recurso {recurso_index} con oferta unitaria {oferta_unitaria}")
            
            # Actualizar 'Oferta_total' en el DataFrame de necesidades
            df_necesidades.at[index, 'Oferta_total'] += oferta_unitaria
            
            # Actualizar recursos disponibles
            recursos_disponibles = df_recursos[df_recursos['Asignacion'] == 0]
        
        if necesidad > 0:
            print(f"No se pudo cubrir la necesidad completa para Cuadrante {cuadrante}. Necesidad restante: {necesidad}")
        else:
            print(f"Necesidad cubierta para Cuadrante {cuadrante}")

    
    df_necesidades['Diferencia'] = df_necesidades['Oferta_total'] + df_necesidades['Cuarteles'] - df_necesidades['Necesidad']
    recursos_disponibles = df_recursos[df_recursos['Asignacion'] == 0]

    # Ordenar los cuadrantes según tengan la menor diferencia
    if not recursos_disponibles.empty:
    
        df_necesidades = df_necesidades.sort_values(by='Diferencia')


        # Iterar sobre los cuadrantes ordenados inversamente y asignar recursos remanentes
        for index, row in df_necesidades.iterrows():
            if not recursos_disponibles.empty:
                cuadrante = row['Cuadrante']  # Obtener el cuadrante
                oferta_unitaria = recursos_disponibles.iloc[0]['Oferta Unitaria']  # Obtener la oferta unitaria del primer recurso disponible
                df_necesidades.at[index, 'Oferta_total'] += oferta_unitaria  # Actualizar oferta total en el DataFrame de necesidades
                df_recursos.at[recursos_disponibles.index[0], 'Asignacion'] = cuadrante  # Asignar el cuadrante al primer recurso disponible
                recursos_disponibles = recursos_disponibles.iloc[1:]  # Remover el recurso asignado
            else:
                break  # Si no hay recursos disponibles, salir del bucle
            
    df_necesidades['Diferencia'] = df_necesidades['Oferta_total'] + df_necesidades['Cuarteles'] - df_necesidades['Necesidad']
    df_necesidades = df_necesidades.sort_values(by='Cuadrante')
            
    return df_recursos, df_necesidades

# Función para transformar polígonos
def transform_polygon(shapely_polygon, name):
    """
    Convert a Shapely polygon to a Folium polygon.

    Parameters:
    - shapely_polygon: A Shapely polygon object.
    - color: Color of the polygon outline (default: 'blue').
    - weight: Weight of the polygon outline (default: 2).
    - fill_color: Fill color of the polygon (default: 'blue').
    - fill_opacity: Opacity of the fill color (default: 0.4).

    Returns:
    - A Folium polygon object.
    """
    # Extract coordinates from the Shapely polygon
    coordinates = shapely_polygon.exterior.coords.xy

    # Create a list of latitudes and longitudes
    latitudes = list(coordinates[1])
    longitudes = list(coordinates[0])

    # Create a list of (latitude, longitude) pairs
    points = list(zip(latitudes, longitudes))

    # Definir color
    color="deepskyblue"
    fill_color="deepskyblue"

    # Create a Folium polygon
    folium_polygon = folium.vector_layers.Polygon(
        locations=points,
        color=color,
        weight=2,
        fill_color=fill_color,
        fill_opacity=0.2,
        tooltip=name
    )

    return folium_polygon


# Función para etiquetas de diferencia
def label_diferencia(cuadrante, df, gdf):

    # Definir polígono
    poligono = gdf[gdf["CUADRANTE_"]==cuadrante]["geometry"].values[0]
    center_lat = poligono.centroid.y.mean()
    center_lon = poligono.centroid.x.mean()

    # Definir diferencia
    diferencia = df[df["Cuadrante"]==cuadrante]["Diferencia"].values[0]

    if diferencia>0:
        color="green"
    elif diferencia<0:
        color="red"

    # Crear etiqueta
    div_icon = folium.DivIcon(html="""
    <div style="font-family: sans-serif; color: white; background-color:"""+str(color)+"""; padding: 2px 10px; border-radius: 3px; width: 50px; text-align: center;">
        <b>"""+str(round(diferencia,2))+"""</b>
    </div>
    """)

    # Crear objeto marker
    label = folium.Marker(
        location=[center_lat, center_lon],
        icon=div_icon
    ) 

    return label  

# Función para generar puntos al azar dentro de un polígono
def random_point(polygon: Polygon, std_dev_factor=0.2):
    centroid = polygon.centroid
    centroid_x, centroid_y = centroid.x, centroid.y
    min_x, min_y, max_x, max_y = polygon.bounds
    
    # Calculate standard deviation based on the polygon size and the factor provided
    std_dev_x = (max_x - min_x) * std_dev_factor
    std_dev_y = (max_y - min_y) * std_dev_factor
    
    while True:
        random_x = np.random.normal(centroid_x, std_dev_x)
        random_y = np.random.normal(centroid_y, std_dev_y)
        random_point = Point(random_x, random_y)
        if polygon.contains(random_point):
            return [random_point.y, random_point.x]
        
# Función para agregar medios asignados
def viz_medios(df, id_medio, gdf):

    tipo = df[df["Id"]==id_medio]["Medio"].values[0]
    cuadrante = df[df["Id"]==id_medio]["Asignacion"].values[0]

    if tipo == "RPT":
        icon = "car"
        color = "darkblue"
    elif tipo == "MTT":
        icon = "motorcycle"
        color = "blue"
    elif tipo == "INF":
        icon = "person"
        color = "cadetblue"
    
    poligono = gdf[gdf["CUADRANTE_"]==cuadrante]["geometry"].values[0]
    
    marcador = folium.Marker(
        location=random_point(poligono),
        icon=folium.Icon(icon=icon, color=color, prefix='fa')
    )

    return marcador

# Función para generar mapa
def mapa_medios(gdf,df_asignados, df_cuadrantes):
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
        transform_polygon(gdf["geometry"].iloc[x],gdf["CUADRANTE_"].iloc[x]).add_to(m)

    # Agregar diferencia
    for x in list(gdf["CUADRANTE_"].unique()):
        label_diferencia(x,df_cuadrantes,gdf).add_to(m)

    medios_asignados = df_asignados[df_asignados["Asignacion"]!=0]
    for x in list(medios_asignados["Id"]):
        viz_medios(df_asignados,x,gdf).add_to(m)

    return m
