"""Demo de aplicativo de distribución de recursos V0.5
Actualizado 04/07/2024"""

import streamlit as st 
#from streamlit_folium import st_folium
import streamlit.components.v1 as components
import numpy as np
import pandas as pd 
import geopandas as gpd
import folium
import random
from shapely.geometry import Point, Polygon
import funciones as f

# Configuración de página
st.set_page_config(page_title="Demo", 
                   page_icon=None, 
                   layout="wide", 
                   initial_sidebar_state="auto", 
                   menu_items=None)

#---------------------------------------------------------------
#                  DATA PRE CARGADA
#---------------------------------------------------------------
# Capa delegación poniente
capa = gpd.read_file("poniente.geojson")

# Definir coordenadas centrales
center_lat = capa.geometry.centroid.y.mean()
center_lon = capa.geometry.centroid.x.mean()

# Mapa base
mapa = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=14,
)

# Agregar capa cuadrantes, la constante en todos los mapas a ser renderizados
for x in range(0,len(capa)):
    f.transform_polygon(capa["geometry"].iloc[x],capa["CUADRANTE_"].iloc[x]).add_to(mapa)

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

#---------------------------------------------------------------
#                  CARGA DE ARCHIVOS
#---------------------------------------------------------------
# Botón de carga de archivos
st.write("Cargar datos iniciales")

upload = st.file_uploader(label="Cargar archivo",
                        type="xlsx")

if upload != None:
    cuadrantes = pd.read_excel(upload, sheet_name="Cuadrantes")
    medios = pd.read_excel(upload, sheet_name="Medios")
    conjuntos = pd.read_excel(upload, sheet_name="Conjuntos")
else:
    cuadrantes = pd.read_excel("Datos_inicio1.xlsx", sheet_name="Cuadrantes")
    medios = pd.read_excel("Datos_inicio1.xlsx", sheet_name="Medios")
    conjuntos = pd.read_excel("Datos_inicio1.xlsx", sheet_name="Conjuntos")

#---------------------------------------------------------------
#                  SELECCIÓN DE CONJUNTOS DISPONIBLES
#---------------------------------------------------------------
# Creación de columna "name" para relacionar con nombres de cuadrantes
medios["name"] = medios["Id_Medio"].astype(str).str.cat(medios["Medio"], sep='-')

# Lista de opciones de medios
opciones_medios = list(medios["Medio"])

# Escoger medios
seleccion = st.multiselect("Escoger medios disponibles:", opciones_medios)

#---------------------------------------------------------------
#                           CÁLCULO
#---------------------------------------------------------------

# Botón para calcular
if st.button("Calcular",type="primary") == False:
    # En caso de no estar activado, sugerir a usuario activar
    st.write("Presionar para calcular")
else:
    df1 = cuadrantes
    df2 = medios
    df3 = conjuntos

    for i in range(4):
        turno = i + 1
        
        if turno == 1: 
            # Filtrar por rangos
            cabos_sargentos = df3[(df3['Rango'].isin(['Cabo', 'Sargento'])) & ((df3['Grupo']== 1) | (df3['Grupo']== 2))]
            agentes = df3[(df3['Rango'] == 'Agente') & ((df3['Grupo']== 1) | (df3['Grupo']== 2))]
            # Totales de RPT y MTT
            total_RPT_Prev = len(df2.loc[(df2['Medio'] == 'RPT') & (df2['Asignacion_Cuadrante_T1'] != 0)])
            total_RPT_Proc = len(df2.loc[(df2['Medio'] == 'RPT') & (df2['Asignacion_Cuadrante_T1'] == 0)])
            total_MTT = len(df2.loc[df2['Medio'] == 'MTT'])
        elif turno ==2:
            # Filtrar por rangos
            cabos_sargentos = df3[(df3['Rango'].isin(['Cabo', 'Sargento'])) & (df3['Grupo']== 3)]
            agentes = df3[(df3['Rango'] == 'Agente') & (df3['Grupo']== 3)]
            # Totales de RPT y MTT
            total_RPT_Prev = len(df2.loc[(df2['Medio'] == 'RPT') & (df2['Asignacion_Cuadrante_T2'] != 0)])
            total_RPT_Proc = len(df2.loc[(df2['Medio'] == 'RPT') & (df2['Asignacion_Cuadrante_T2'] == 0)])
        elif turno == 3: 
            # Filtrar por rangos
            cabos_sargentos = df3[(df3['Rango'].isin(['Cabo', 'Sargento'])) & ((df3['Grupo']== 4) | (df3['Grupo']== 5))]
            agentes = df3[(df3['Rango'] == 'Agente') & ((df3['Grupo']== 4) | (df3['Grupo']== 5))]
            # Totales de RPT y MTT
            total_RPT_Prev = len(df2.loc[(df2['Medio'] == 'RPT') & (df2['Asignacion_Cuadrante_T3'] != 0)])
            total_RPT_Proc = len(df2.loc[(df2['Medio'] == 'RPT') & (df2['Asignacion_Cuadrante_T3'] == 0)])
        elif turno ==4:
            # Filtrar por rangos
            cabos_sargentos = df3[(df3['Rango'].isin(['Cabo', 'Sargento'])) & (df3['Grupo']== 6)]
            agentes = df3[(df3['Rango'] == 'Agente') & (df3['Grupo']== 6)]
            # Totales de RPT y MTT
            total_RPT_Prev = len(df2.loc[(df2['Medio'] == 'RPT') & (df2['Asignacion_Cuadrante_T4'] != 0)])
            total_RPT_Proc = len(df2.loc[(df2['Medio'] == 'RPT') & (df2['Asignacion_Cuadrante_T4'] == 0)])
        
        
        # Inicializar Id_Conjunto
        id_conjunto = 1


        # Función para asignar conjuntos y actualizar el DataFrame
        def asignar_conjuntos(df3, jefe, agentes_seleccionados, id_conjunto,medio,asignacion):
            # Actualizar Id_Conjunto para jefe
            df3.loc[df3['Id_agente'] == jefe['Id_agente'], 'Id_Conjunto'] = id_conjunto
            df3.loc[df3['Id_agente'] == jefe['Id_agente'], 'Medio'] = medio
            df3.loc[df3['Id_agente'] == jefe['Id_agente'], 'Asignacion_Medios'] = asignacion
            df3.loc[df3['Id_agente'] == jefe['Id_agente'], 'Turno'] = turno
            
            # Actualizar Id_Conjunto para los agentes seleccionados
            for _, agente in agentes_seleccionados.iterrows():
                df3.loc[df3['Id_agente'] == agente['Id_agente'], 'Id_Conjunto'] = id_conjunto
                df3.loc[df3['Id_agente'] == agente['Id_agente'], 'Medio'] = medio
                df3.loc[df3['Id_agente'] == agente['Id_agente'], 'Asignacion_Medios'] = asignacion
                df3.loc[df3['Id_agente'] == agente['Id_agente'], 'Turno'] = turno

        asignacion = 1
        # Asignar conjuntos de 4 personas (1 Cabo o Sargento y 3 Agentes) para RPT
        for _ in range(total_RPT_Prev):
            if len(cabos_sargentos) > 0 and len(agentes) >= 3:
                # Seleccionar un jefe aleatoriamente
                jefe = cabos_sargentos.sample(n=1).iloc[0]
                # jefe es una Series, jefe.name devuelve el índice de esta Series
                
                # Seleccionar tres agentes aleatoriamente
                agentes_seleccionados = agentes.sample(n=3)
                # agentes_seleccionados es un DataFrame, agentes_seleccionados.index devuelve un Index con los índices de las filas seleccionadas
                
                asignar_conjuntos(df3, jefe, agentes_seleccionados, id_conjunto,'RPT',asignacion)
                
                # Eliminar el jefe y agentes seleccionados de los dataframes
                cabos_sargentos = cabos_sargentos.drop(jefe.name)
                agentes = agentes.drop(agentes_seleccionados.index)
                
                id_conjunto += 1
                asignacion += 1
        asignacion = 1
        # Asignar conjuntos de 3 personas (1 Cabo o Sargento y 2 Agentes) para MTT
        for _ in range(total_MTT):
            if len(cabos_sargentos) > 0 and len(agentes) >= 2:
                jefe = cabos_sargentos.iloc[0]
                agentes_seleccionados = agentes.head(2)
                
                
                asignar_conjuntos(df3, jefe, agentes_seleccionados, id_conjunto,'MTT',asignacion)
                
                # Eliminar el jefe y agentes seleccionados de los dataframes
                cabos_sargentos = cabos_sargentos.iloc[1:]
                agentes = agentes.iloc[2:]
                
                id_conjunto += 1
                asignacion += 1


#---------------------------------------------------------------
#                  SELECCIÓN DE TURNO
#---------------------------------------------------------------
# Opción para escoger un turno
turno = st.selectbox(label="Escoger turno",
                     options=[1,2,3,4]
                     )

#---------------------------------------------------------------
#                  CREACIÓN DE MAPA
#---------------------------------------------------------------
with st.container:
    
    # Agregar diferencia
    for x in list(capa["CUADRANTE_"].unique()):
        f.label_diferencia(x,df1,capa).add_to(mapa)

    # Convertir objeto de mapa a HTML
    map_html1 = mapa._repr_html_()

    # Mostrar mapa
    components.html(map_html1, width=1200, height=750)

    if turno ==1:
        # Agregar diferencia
        for x in list(capa["CUADRANTE_"].unique()):
            f.label_diferencia(x,df1,capa).add_to(mapa)

        # Agregar marcadores de medios asignados
        medios_asignados = df2[df2["Asignacion_Cuadrante_T1"] != 0] # Filtrar por medios que han sido asignados
        polygon_counter = {key: 0 for key in predefined_coords.keys()}
        for x in list(medios_asignados["Id"]):
            id_conjunto = df2["Asignacion_Cuadrante_T1"][x]
            marker = f.viz_medios(df2, x, predefined_coords, polygon_counter, id_conjunto, turno)
            if marker:
                marker.add_to(mapa)

        # Convertir mapa a HTML
        map_html = mapa._repr_html_()

        # Mostrar mapa
        components.html(map_html, width=1200, height=750)
    
    elif turno ==2:
        # Agregar diferencia
        for x in list(capa["CUADRANTE_"].unique()):
            f.label_diferencia(x,df1,capa).add_to(mapa)

        # Agregar marcadores de medios asignados
        medios_asignados = df2[df2["Asignacion_Cuadrante_T2"] != 0] # Filtrar por medios que han sido asignados
        polygon_counter = {key: 0 for key in predefined_coords.keys()}
        for x in list(medios_asignados["Id"]):
            id_conjunto = df2["Asignacion_Cuadrante_T2"][x]
            marker = f.viz_medios(df2, x, predefined_coords, polygon_counter, id_conjunto)
            if marker:
                marker.add_to(mapa)

        # Convertir mapa a HTML
        map_html = mapa._repr_html_()

        # Mostrar mapa
        components.html(map_html, width=1200, height=750)

    elif turno ==3:
        # Agregar diferencia
        for x in list(capa["CUADRANTE_"].unique()):
            f.label_diferencia(x,df1,capa).add_to(mapa)

        # Agregar marcadores de medios asignados
        medios_asignados = df2[df2["Asignacion_Cuadrante_T3"] != 0] # Filtrar por medios que han sido asignados
        polygon_counter = {key: 0 for key in predefined_coords.keys()}
        for x in list(medios_asignados["Id"]):
            id_conjunto = df2["Asignacion_Cuadrante_T3"][x]
            marker = f.viz_medios(df2, x, predefined_coords, polygon_counter, id_conjunto)
            if marker:
                marker.add_to(mapa)

        # Convertir mapa a HTML
        map_html = mapa._repr_html_()

        # Mostrar mapa
        components.html(map_html, width=1200, height=750)
    
    else:
        # Agregar diferencia
        for x in list(capa["CUADRANTE_"].unique()):
            f.label_diferencia(x,df1,capa).add_to(mapa)

        # Agregar marcadores de medios asignados
        medios_asignados = df2[df2["Asignacion_Cuadrante_T4"] != 0] # Filtrar por medios que han sido asignados
        polygon_counter = {key: 0 for key in predefined_coords.keys()}
        for x in list(medios_asignados["Id"]):
            id_conjunto = df2["Asignacion_Cuadrante_T4"][x]
            marker = f.viz_medios(df2, x, predefined_coords, polygon_counter, id_conjunto)
            if marker:
                marker.add_to(mapa)

        # Convertir mapa a HTML
        map_html = mapa._repr_html_()

        # Mostrar mapa
        components.html(map_html, width=1200, height=750)