import math

COORDENADAS_ZONAS = {
    'Tarragona': (41.1169, 1.2395),
    'Reus': (41.1555, 1.1072),
    'Barcelona': (41.4081, 2.2158),
    'Cambrils': (41.0652, 1.0612),
    'Tortosa': (40.8125, 0.5214)
}

def haversine_distance(lat1, lng1, lat2, lng2):
    R = 6371
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def get_tecnico_coords(tecnico):
    zona = tecnico.get('zona', 'Tarragona')
    if zona in COORDENADAS_ZONAS:
        return COORDENADAS_ZONAS[zona]
    return COORDENADAS_ZONAS['Tarragona']

def calcular_puntuacion(tarea, tecnico, tareas_tecnico):
    puntuacion = 0
    
    lat_tecnico, lng_tecnico = get_tecnico_coords(tecnico)
    lat_tarea = tarea.get('lat', 41.1)
    lng_tarea = tarea.get('lng', 1.2)
    
    distancia = haversine_distance(lat_tarea, lng_tarea, lat_tecnico, lng_tecnico)
    if distancia < 10:
        distancia_score = 100
    elif distancia < 50:
        distancia_score = 80
    elif distancia < 100:
        distancia_score = 60
    elif distancia < 200:
        distancia_score = 40
    else:
        distancia_score = 20
    
    puntuacion += distancia_score * 0.30
    
    carga_actual = len(tareas_tecnico)
    carga_max = 4
    
    if carga_actual == 0:
        carga_score = 100
    elif carga_actual < carga_max:
        carga_score = ((carga_max - carga_actual) / carga_max) * 100
    else:
        carga_score = 0
    
    puntuacion += carga_score * 0.25
    
    zona_tarea = tarea.get('zona', 'Tarragona')
    zona_tecnico = tecnico.get('zona', 'Tarragona')
    if zona_tarea == zona_tecnico:
        zona_score = 100
    else:
        zona_score = 20
    
    puntuacion += zona_score * 0.25
    
    tipo = tarea.get('tipo', '')
    if tipo in ['avaria', 'incidencia']:
        sla_score = 80
    elif tipo == 'manteniment':
        sla_score = 60
    else:
        sla_score = 40
    
    puntuacion += sla_score * 0.20
    
    return round(puntuacion, 1)

def generar_asignaciones(tareas, tecnicos):
    asignaciones = []
    
    for tarea in tareas:
        mejor_tecnico = None
        mejor_puntuacion = 0
        puntuaciones = []
        
        for tecnico in tecnicos:
            tareas_tecnico = [a for a in asignaciones if a['tecnico_asignado'].get('id') == tecnico.get('id')]
            puntuacion = calcular_puntuacion(tarea, tecnico, tareas_tecnico)
            
            puntuaciones.append({
                'tecnico': tecnico,
                'puntuacion': puntuacion
            })
            
            if puntuacion > mejor_puntuacion:
                mejor_puntuacion = puntuacion
                mejor_tecnico = tecnico
        
        if mejor_tecnico:
            lat_tecnico, lng_tecnico = get_tecnico_coords(mejOR_tecnico)
            lat_tarea = tarea.get('lat', 41.1)
            lng_tarea = tarea.get('lng', 1.2)
            
            puntuaciones.sort(key=lambda x: x['puntuacion'], reverse=True)
            
            asignacion = {
                'tarea': tarea,
                'tecnico_asignado': mejor_tecnico,
                'puntuacion': mejor_puntuacion,
                'todas_puntuaciones': puntuaciones,
                'factores': {
                    'distancia': haversine_distance(lat_tarea, lng_tarea, lat_tecnico, lng_tecnico),
                    'carga_actual': len([a for a in asignaciones if a['tecnico_asignado'].get('id') == mejor_tecnico.get('id')]),
                    'zona_coincide': tarea.get('zona') == mejor_tecnico.get('zona'),
                    'tipo': tarea.get('tipo', '')
                }
            }
            asignaciones.append(asignacion)
    
    return asignaciones
