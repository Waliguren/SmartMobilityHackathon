import requests
import time

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

def get_address_from_coords(lat, lon, timeout=5):
    """
    Obtiene la dirección a partir de coordenadas usando OpenStreetMap Nominatim.
    """
    if not lat or not lon:
        return None
    
    try:
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json',
            'addressdetails': 1,
            'zoom': 18
        }
        
        headers = {
            'User-Agent': 'SmartMobilityHackathon/1.0'
        }
        
        response = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('address'):
                address = data['address']
                
                parts = []
                
                if address.get('house_number'):
                    parts.append(address['house_number'])
                
                if address.get('road'):
                    parts.append(address['road'])
                
                if address.get('city') or address.get('town') or address.get('village'):
                    city = address.get('city') or address.get('town') or address.get('village')
                    parts.append(city)
                
                if address.get('municipality'):
                    parts.append(f"({address['municipality']})")
                
                if parts:
                    return ", ".join(parts)
                
                return address.get('display_name', '')
        
        return None
    except Exception as e:
        print(f"Error getting address: {e}")
        return None

def get_address_formatted(lat, lon):
    """
    Obtiene una dirección formateada de manera legible.
    """
    address = get_address_from_coords(lat, lon)
    return address

def enrich_task_with_address(tarea):
    """
    Enriquece una tarea con la dirección obtenida de las coordenadas.
    """
    lat = tarea.get('lat') or tarea.get('location', {}).get('_latitude')
    lng = tarea.get('lng') or tarea.get('location', {}).get('_longitude')
    
    if lat and lng:
        address = get_address_from_coords(lat, lng)
        if address:
            tarea['direccion_completa'] = address
    
    return tarea
