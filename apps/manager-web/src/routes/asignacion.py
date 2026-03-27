from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.firebase_service import get_technicians, get_visits, get_db
from src.services.vrp_optimizer import generar_asignaciones, calcular_puntuacion
from src.services.ia_explicacion import generar_explicacion, sugerir_asignacion_ia, guardar_correccion, obtener_correcciones

asignacion = Blueprint('asignacion', __name__)

@asignacion.route('/asignacion')
@login_required
def vista_asignacion():
    return render_template('asignacion.html', title='Asistente de Asignación')

@asignacion.route('/api/asignacion/datos')
@login_required
def obtener_datos():
    technicians = get_technicians()
    visits = get_visits()
    
    tecnicos = []
    for t in technicians:
        tecnicos.append({
            'id': t.get('id'),
            'nombre': t.get('name'),
            'zona': t.get('zone'),
            'expertice': t.get('expertice', 5),
            'expert': t.get('expert', False)
        })
    
    tareas_pendientes = []
    for v in visits:
        if v.get('status') in ['pendent', 'en_proces']:
            tareas_pendientes.append({
                'id': v.get('id'),
                'tipo': v.get('visit_type', 'manteniment'),
                'zona': v.get('zona', 'Tarragona'),
                'lat': v.get('location', {}).get('_latitude', 41.1),
                'lng': v.get('location', {}).get('_longitude', 1.2),
                'direccion': v.get('address', ''),
                'cliente': v.get('cliente', ''),
                'estado': v.get('status', 'pendent')
            })
    
    return jsonify({
        'tecnicos': tecnicos,
        'tareas_pendientes': tareas_pendientes
    })

@asignacion.route('/api/asignacion/recomendar', methods=['POST'])
@login_required
def recomendar_asignacion():
    data = request.json or {}
    tecnicos = data.get('tecnicos', [])
    tareas = data.get('tareas', [])
    
    if not tecnicos:
        technicians = get_technicians()
        for t in technicians:
            tecnicos.append({
                'id': t.get('id'),
                'nombre': t.get('name'),
                'zona': t.get('zone'),
                'expertice': t.get('expertice', 5),
                'expert': t.get('expert', False)
            })
    
    if not tareas:
        visits = get_visits()
        for v in visits:
            if v.get('status') in ['pendent', 'en_proces']:
                tareas.append({
                    'id': v.get('id'),
                    'tipo': v.get('visit_type', 'manteniment'),
                    'zona': v.get('zona', 'Tarragona'),
                    'lat': v.get('location', {}).get('_latitude', 41.1),
                    'lng': v.get('location', {}).get('_longitude', 1.2),
                    'direccion': v.get('address', ''),
                    'cliente': v.get('cliente', ''),
                    'estado': v.get('status', 'pendent')
                })
    
    asignaciones = generar_asignaciones(tareas, tecnicos)
    
    resultados = []
    for asig in asignaciones:
        explicacion = generar_explicacion(asig)
        
        resultados.append({
            'tarea': asig['tarea'],
            'recomendacion': {
                'tecnico': explicacion['tecnico'],
                'puntuacion': explicacion['puntuacion'],
                'explicacion': explicacion['explicacion'],
                'factores': explicacion['factores'],
                'todas_opciones': explicacion.get('todas_opciones', [])
            }
        })
    
    return jsonify({'asignaciones': resultados})

@asignacion.route('/api/asignacion/sugerir-ia', methods=['POST'])
@login_required
def sugerir_asignacion_ia_endpoint():
    """
    Endpoint que usa Groq/Llama para sugerir asignaciones óptimas
    considerando todas las tareas y el histórico de correcciones.
    """
    data = request.json or {}
    tecnicos = data.get('tecnicos', [])
    tareas = data.get('tareas', [])
    
    if not tecnicos:
        technicians = get_technicians()
        for t in technicians:
            tecnicos.append({
                'id': t.get('id'),
                'name': t.get('name'),
                'zone': t.get('zone'),
                'expertice': t.get('expertice', 5),
                'expert': t.get('expert', False)
            })
    
    if not tareas:
        visits = get_visits()
        for v in visits:
            if v.get('status') in ['pendent', 'en_proces']:
                tareas.append({
                    'id': v.get('id'),
                    'tipo': v.get('visit_type', 'manteniment'),
                    'zona': v.get('zona', 'Tarragona'),
                    'lat': v.get('location', {}).get('_latitude', 41.1),
                    'lng': v.get('location', {}).get('_longitude', 1.2),
                    'direccion': v.get('address', ''),
                    'cliente': v.get('cliente', ''),
                    'address': v.get('address', ''),
                    'visit_type': v.get('visit_type', 'manteniment')
                })
    
    db = get_db()
    correcciones = obtener_correcciones(db) if db else []
    
    try:
        tareas_limitadas = tareas[:10]
        resultado_ia = sugerir_asignacion_ia(tareas_limitadas, tecnicos, correcciones)
        
        if resultado_ia and resultado_ia.get('asignaciones'):
            return jsonify({
                'success': True,
                'asignaciones': resultado_ia.get('asignaciones', []),
                'resumen': resultado_ia.get('resumen', ''),
                'usada_ia': True
            })
    except Exception as e:
        print(f"Error en IA: {e}")
    
    return jsonify({
        'success': False,
        'error': 'No se pudo obtener sugerencias de IA. Usando algoritmo VRP.',
        'usada_ia': False
    })

@asignacion.route('/api/asignacion/generar', methods=['POST'])
@login_required
def generar_recomendaciones():
    """
    Genera recomendaciones para TODAS las tareas usando múltiples llamadas a Groq.
    Combina VRP + IA en un solo botón.
    """
    data = request.json or {}
    tecnicos = data.get('tecnicos', [])
    tareas = data.get('tareas', [])
    
    if not tecnicos:
        technicians = get_technicians()
        for t in technicians:
            tecnicos.append({
                'id': t.get('id'),
                'name': t.get('name'),
                'zone': t.get('zone'),
                'expertice': t.get('expertice', 5),
                'expert': t.get('expert', False)
            })
    
    if not tareas:
        visits = get_visits()
        for v in visits:
            if v.get('status') in ['pendent', 'en_proces']:
                tareas.append({
                    'id': v.get('id'),
                    'tipo': v.get('visit_type', 'manteniment'),
                    'zona': v.get('zona', 'Tarragona'),
                    'lat': v.get('location', {}).get('_latitude', 41.1),
                    'lng': v.get('location', {}).get('_longitude', 1.2),
                    'direccion': v.get('address', ''),
                    'cliente': v.get('cliente', ''),
                    'address': v.get('address', ''),
                    'visit_type': v.get('visit_type', 'manteniment')
                })
    
    db = get_db()
    correcciones = obtener_correcciones(db) if db else []
    
    todas_asignaciones = []
    resumen_total = []
    errors = []
    batch_size = 10
    
    total_batches = (len(tareas) + batch_size - 1) // batch_size
    print(f"[DEBUG] Procesando {len(tareas)} tareas en {total_batches} lotes...")
    
    for i in range(0, len(tareas), batch_size):
        batch = tareas[i:i + batch_size]
        batch_num = i // batch_size + 1
        print(f"[DEBUG] Lote {batch_num}/{total_batches}: {len(batch)} tareas...")
        
        try:
            resultado = sugerir_asignacion_ia(batch, tecnicos, correcciones)
            print(f"[DEBUG] Resultado lote {batch_num}: {resultado is not None}")
            if resultado and resultado.get('asignaciones'):
                todas_asignaciones.extend(resultado.get('asignaciones', []))
                if resultado.get('resumen'):
                    resumen_total.append(f"Lote {batch_num}: {resultado.get('resumen')}")
            else:
                errors.append(f"Lote {batch_num}: resultado vacío o sin asignaciones")
        except Exception as e:
            print(f"[ERROR] Lote {batch_num}: {e}")
            errors.append(f"Lote {batch_num}: {str(e)}")
    
    print(f"[DEBUG] Total asignaciones: {len(todas_asignaciones)}, Errors: {len(errors)}")
    
    if todas_asignaciones:
        return jsonify({
            'success': True,
            'asignaciones': todas_asignaciones,
            'resumen': f"Se procesaron {len(todas_asignaciones)} tareas en {total_batches} lotes. " + " ".join(resumen_total),
            'usada_ia': True,
            'total_tareas': len(tareas),
            'total_asignaciones': len(todas_asignaciones)
        })
    else:
        return jsonify({
            'success': False,
            'error': 'No se pudieron obtener recomendaciones de IA',
            'usada_ia': False
        })

@asignacion.route('/api/asignacion/corregir', methods=['POST'])
@login_required
def corregir_asignacion():
    """
    Guarda una corrección del usuario para autoaprendizaje.
    """
    data = request.json
    tarea_id = data.get('tarea_id')
    tecnico_original = data.get('tecnico_original')
    tecnico_corregido = data.get('tecnico_corregido')
    razon = data.get('razon', '')
    
    db = get_db()
    
    if db:
        guardar_correccion(
            db, 
            tarea_id, 
            tecnico_original, 
            tecnico_corregido, 
            razon,
            'admin'
        )
        
        db.collection('visits').document(tarea_id).update({
            'technician_id': tecnico_corregido,
            'status': 'assignat'
        })
        
        return jsonify({
            'success': True,
            'message': f'Corrección guardada. Tarea {tarea_id} reasignada a {tecnico_corregido}'
        })
    
    return jsonify({
        'success': False,
        'error': 'No se pudo conectar a la base de datos'
    })

@asignacion.route('/api/asignacion/calcular-puntuacion', methods=['POST'])
@login_required
def calcular_puntuacion_endpoint():
    data = request.json
    tarea = data.get('tarea')
    tecnico = data.get('tecnico')
    
    puntuacion = calcular_puntuacion(tarea, tecnico, [])
    
    return jsonify({'puntuacion': puntuacion})

@asignacion.route('/api/asignacion/asignar', methods=['POST'])
@login_required
def asignar_tarea():
    data = request.json
    tarea_id = data.get('tarea_id')
    tecnico_id = data.get('tecnico_id')
    prioridad = data.get('prioridad', 'normal')
    
    db = get_db()
    
    if db:
        db.collection('visits').document(tarea_id).update({
            'technician_id': tecnico_id,
            'status': 'assignat'
        })
    
    return jsonify({
        'success': True,
        'message': f'Tarea {tarea_id} asignada al técnico {tecnico_id} con prioridad {prioridad}'
    })