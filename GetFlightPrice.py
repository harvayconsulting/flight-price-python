import argparse
from serpapi import GoogleSearch
import requests
import json
from tabulate import tabulate

# Parsear argumentos desde la línea de comandos
parser = argparse.ArgumentParser(description='Comparar precios de vuelos.')
parser.add_argument('--adultos', type=int, required=True, help='Número de adultos')
parser.add_argument('--ninos_menores_2', type=int, required=True, help='Número de niños menores de 2 años')
parser.add_argument('--ninos_mayores_2', type=int, required=True, help='Número de niños mayores de 2 años')
parser.add_argument('--fecha_ida', type=str, required=True, help='Fecha de ida (YYYY-MM-DD)')
parser.add_argument('--fecha_vuelta', type=str, required=True, help='Fecha de vuelta (YYYY-MM-DD)')
args = parser.parse_args()

# API Key y parámetros base
API_KEY = "c761c1fd248a32d136025d2b99c52200499771a56769b7b9325c6ed6fe8b2791"
params_base = {
    "engine": "google_flights",
    "show_hidden": "true",
    "deep_search": "true",
    "no_cache": "true",
    "adults": args.adultos,
    "children": args.ninos_mayores_2,
    "infants_in_seat": args.ninos_menores_2,
    "infants_on_lap": 0,
    "bags": 1,
    "hl": "en",
    "gl": "us",
    "currency": "USD"
}

# Tasa de cambio aproximada (a actualizar)
USD_TO_BRL = 5.0  # Ejemplo, usar API para tasa real

# Lista de rutas (ejemplo, completar con todas)
rutas = [
    "SLZ-GRU-AEP-COR",
    "SLZ-GIG-AEP-COR",
    # ... otras rutas
]

# Función para parsear segmentos de ruta
def parse_ruta(ruta):
    return ruta.split('-')

# Función para buscar vuelos y filtrar por aerolíneas
def buscar_vuelos(ruta, fecha):
    segmentos = parse_ruta(ruta)
    flight_segments = []
    for i in range(len(segmentos)-1):
        flight_segments.append({
            "departure_id": segmentos[i],
            "arrival_id": segmentos[i+1],
            "date": fecha
        })
    params = params_base.copy()
    params["flight_segments"] = json.dumps(flight_segments)
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("other_flights", [])

# Función para filtrar itinerarios por aerolíneas
def filtrar_por_aerolineas(itinerarios, aerolineas_por_tramo):
    resultados_filtrados = []
    for itinerario in itinerarios:
        flights = itinerario.get("flights", [])
        if len(flights) != len(aerolineas_por_tramo):
            continue
        valido = True
        for i, flight in enumerate(flights):
            airline = flight.get("airline", "")
            if aerolineas_por_tramo[i] and airline != aerolineas_por_tramo[i]:
                valido = False
                break
        if valido:
            resultados_filtrados.append(itinerario)
    return resultados_filtrados

# Procesar cada ruta y aerolínea
resultados = []
for ruta in rutas:
    fila = {"Ruta": ruta}
    # Determinar si es ida o vuelta para usar fecha adecuada
    es_ida = ruta.startswith("SLZ")
    fecha = args.fecha_ida if es_ida else args.fecha_vuelta
    
    # Buscar vuelos
    itinerarios = buscar_vuelos(ruta, fecha)
    
    # Procesar cada columna de aerolínea
    # Ejemplo para Gol (todos los tramos G3)
    aerolineas_gol = ["G3"] * (len(parse_ruta(ruta))-1)
    filtrados_gol = filtrar_por_aerolineas(itinerarios, aerolineas_gol)
    precio_gol = min([it["price"] for it in filtrados_gol], default=None) * USD_TO_BRL if filtrados_gol else None
    fila["Gol"] = precio_gol if precio_gol and precio_gol <= 5000 else "N/A"
    
    # Similar para otras aerolíneas y combinaciones...
    # (Completar lógica para Latam, AR, combinaciones, etc.)
    
    resultados.append(fila)

# Mostrar tabla
headers = ["Ruta", "Gol", "Latam", "Aerolineas Argentinas", "Gol + Aerolineas Argentinas", "LATAM + Aerolineas Argentinas"]
print(tabulate(resultados, headers=headers, tablefmt="grid"))