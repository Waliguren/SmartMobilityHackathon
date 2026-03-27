import os
import json
from datetime import datetime

def get_groq_client():
    try:
        from groq import Groq
        
        api_key = os.environ.get('GROQ_API_KEY') or os.environ.get('GROK_API_KEY')
        
        if not api_key:
            posibles_rutas = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '..', '..', '..', '.env'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '..', '.env'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'),
                '/home/oscar/Documentos/URV/3ro/Hackathon SmartMobility/SmartMobilityHackathon/.env'
            ]
            
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    print(f"Buscando API key en: {ruta}")
                    with open(ruta, 'r') as f:
                        contenido = f.read()
                        for line in contenido.split('\n'):
                            line = line.strip()
                            if line.startswith('GROQ_API_KEY') or line.startswith('GROK_API_KEY'):
                                partes = line.split(':', 1)
                                if len(partes) > 1:
                                    api_key = partes[1].strip()
                                    print(f"API Key encontrada: {api_key[:20]}...")
                                    break
        
        if api_key:
            return Groq(api_key=api_key)
        else:
            print("No se encontró GROQ_API_KEY en ningún archivo .env")
            return None
    except Exception as e:
        print(f"Error inicializando Groq: {e}")
        return None

def generar_explicacion(asignacion):
    tarea = asignacion['tarea']
    tecnico = asignacion['tecnico_asignado']
    puntuacion = asignacion['puntuacion']
    factores = asignacion['factores']
    
    tipo_labels = {
        'avaria': 'Incidencia',
        'manteniment': 'Mantenimiento',
        'preventiu': 'Preventivo',
        'incidencia': 'Incidencia',
        'mantenimiento': 'Mantenimiento'
    }
    
    tipo_tarea = tipo_labels.get(tarea.get('tipo', ''), tarea.get('tipo', ''))
    
    distancia = factores.get('distancia', 0)
    carga_actual = factores.get('carga_actual', 0)
    zona_coincide = factores.get('zona_coincide', False)
    
    explicacion = f"Se recomienda a {tecnico.get('nombre', tecnico.get('id'))} con puntuación de {puntuacion}/100. "
    
    if zona_coincide:
        explicacion += f"Está en la misma zona ({tecnico.get('zona', '')}). "
    else:
        explicacion += f"Zona del técnico: {tecnico.get('zona', 'diferente')}. "
    
    if carga_actual < 2:
        explicacion += f"Tiene capacidad disponible ({carga_actual} tareas)."
    else:
        explicacion += f"Tiene {carga_actual} tareas asignadas."
    
    return {
        'tecnico': tecnico,
        'puntuacion': puntuacion,
        'explicacion': explicacion,
        'factores': factores,
        'todas_opciones': asignacion.get('todas_puntuaciones', [])
    }

def generar_explicacion_con_groq(asignacion):
    try:
        client = get_groq_client()
        if not client:
            return generar_explicacion(asignacion)
        
        tarea = asignacion['tarea']
        tecnico = asignacion['tecnico_asignado']
        factores = asignacion['factores']
        
        prompt = f"""
Eres un asistente de asignación de tareas para técnicos de campo.

Analiza esta recomendación y genera una explicación breve y clara (2-3 frases):

DATOS DE LA TAREA:
- Tipo: {tarea.get('tipo', 'N/A')}
- Dirección: {tarea.get('direccion', tarea.get('address', 'N/A'))}
- Cliente: {tarea.get('cliente', 'N/A')}

DATOS DEL TÉCNICO:
- Nombre: {tecnico.get('nombre', tecnico.get('id', 'N/A'))}
- Zona: {tecnico.get('zona', 'N/A')}
- Carga actual: {factores.get('carga_actual', 0)} tareas

FACTORES:
- Distancia: {factores.get('distancia', 0):.1f} km
- Zona coincide: {'Sí' if factores.get('zona_coincide') else 'No'}

Genera una explicación natural de por qué este técnico es óptimo para esta tarea.
"""
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )
        
        return {
            'explicacion': completion.choices[0].message.content,
            'usada_ia': True
        }
        
    except Exception as e:
        print(f"Error con Groq: {e}")
        return generar_explicacion(asignacion)

def sugerir_asignacion_ia(tareas, tecnicos, correcciones_previas=None):
    """
    Usa Groq para sugerir la mejor asignación para cada tarea.
    Envía todas las tareas de golpe para obtener recomendaciones completas.
    """
    try:
        client = get_groq_client()
        if not client:
            return None
        
        if not tareas or not tecnicos:
            return None
        
        tecnicos_info = "\n".join([
            f"- {t['id']}: {t.get('name', t['id'])} - Zona: {t.get('zone', 'N/A')} - Experticia: {t.get('expertice', 5)}/10"
            for t in tecnicos
        ])
        
        tareas_info = "\n".join([
            f"- {t['id']}: Tipo={t.get('tipo', t.get('visit_type', 'N/A'))}, "
            f"Dirección={t.get('direccion', t.get('address', 'N/A'))}, "
            f"Zona={t.get('zona', 'N/A')}, Cliente={t.get('cliente', 'N/A')}"
            for t in tareas
        ])
        
        correcciones_text = ""
        if correcciones_previas:
            correcciones_text = "\nHISTÓRICO DE CORRECCIONES (considerar estas preferencias):\n"
            correcciones_text += "\n".join([
                f"- {c['tarea_id']}: originally assigned to {c['tecnico_original']}, "
                f"changed to {c['tecnico_corregido']}. Reason: {c.get('razon', 'N/A')}"
                for c in correcciones_previas[-10:]
            ])
        
        prompt = f"""
Eres un sistema experto en asignación de tareas para técnicos de campo. Tu trabajo es recomendar el mejor técnico para cada tarea.

IMPORTANT: Las explicaciones DEBEN ser TOTALMENTE DIFERENTES para cada tarea. No uses la misma frase dos veces.

DATOS DE TÉCNICOS:
{tecnicos_info}

DATOS DE TAREAS:
{tareas_info}
{correcciones_text}

REGLAS:
1. Cada tarea debe tener un técnico asignado
2. Considera: zona, distancia, carga de trabajo, experiencia
3. Las incidencias (avaria) son prioridad alta
4. Máximo 4 tareas por técnico

IMPORTANTE: Para CADA tarea, escribe una explicación ÚNICA y DIFERENTE. No repitas nunca la misma estructura.

Ejemplos de lo que NO hacer:
- "El técnico es óptimo porque tiene experiencia" (repetitivo)
- "El técnico es el mejor por su zona" (repetitivo)

Ejemplos de lo que SÍ hacer:
- "Marc Rovira: Está a solo 5km, conoce al cliente de anteriores instalaciones."
- "Julia Soler: Experta en mantenimiento preventivo, disponibilidad inmediata mañana."
- "Sara Luna: única disponible en Tortosa, conoce el restaurante."
- "Anna Vila: CERTIFICADA para cargadores rápidos Tesla, urgencia del cliente."

IMPORTANTE: Recomienda también la PRIORIDAD de la tarea:
- "urgente": Para averías (avaria) o emergencias
- "normal": Para mantenimiento preventivo o rutinario
- "baja": Para tareas que pueden esperar

FORMATO JSON:
{{
  "asignaciones": [
    {{
      "tarea_id": "ID",
      "tecnico_id": "ID",
      "tecnico_nombre": "Nombre",
      "zona": "Zona",
      "prioridad": "normal",
      "puntuacion": 85,
      "explicacion": "Frase ÚNICA para esta tarea - incluye detalles específicos distintos a otras tareas",
      "factores": {{"distancia_km": 5, "zona_coincide": true, "carga_actual": 2, "experticia_tecnico": 9, "tipo_tarea": "avaria"}}
    }}
  ],
  "resumen": "Resumen"
}}

Cada explicación DEBE contener información única. ¡Sé creativo y específico!
"""
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.95,
            max_tokens=5000
        )
        
        respuesta = completion.choices[0].message.content
        
        respuesta_limpia = respuesta.strip()
        if respuesta_limpia.startswith('```json'):
            respuesta_limpia = respuesta_limpia[7:]
        if respuesta_limpia.startswith('```'):
            respuesta_limpia = respuesta_limpia[3:]
        if respuesta_limpia.endswith('```'):
            respuesta_limpia = respuesta_limpia[:-3]
        respuesta_limpia = respuesta_limpia.strip()
        
        try:
            resultado = json.loads(respuesta_limpia)
            return resultado
        except json.JSONDecodeError:
            print(f"Error parseando JSON de Groq: {respuesta_limpia[:200]}")
            
            inicio = respuesta_limpia.find('{')
            fin = respuesta_limpia.rfind('}') + 1
            if inicio >= 0 and fin > inicio:
                try:
                    resultado = json.loads(respuesta_limpia[inicio:fin])
                    return resultado
                except:
                    pass
            
            return None
        
    except Exception as e:
        print(f"Error en sugerir_asignacion_ia: {e}")
        return None

def guardar_correccion(db, tarea_id, tecnico_original, tecnico_corregido, razon, usuario='admin'):
    """
    Guarda una corrección del usuario para autoaprendizaje.
    """
    if not db:
        return False
    
    try:
        correccion = {
            'tarea_id': tarea_id,
            'tecnico_original': tecnico_original,
            'tecnico_corregido': tecnico_corregido,
            'razon': razon,
            'usuario': usuario,
            'fecha': datetime.now().isoformat()
        }
        
        db.collection('correcciones').add(correccion)
        return True
    except Exception as e:
        print(f"Error guardando corrección: {e}")
        return False

def obtener_correcciones(db, limite=20):
    """
    Obtiene las últimas correcciones para considerar en futuras sugerencias.
    """
    if not db:
        return []
    
    try:
        correcciones = db.collection('correcciones').order_by('fecha', direction='DESCENDING').limit(limite).stream()
        return [c.to_dict() for c in correcciones]
    except Exception as e:
        print(f"Error obteniendo correcciones: {e}")
        return []
