import firebase_admin
from firebase_admin import credentials, firestore
import os

cred = None
db = None

def init_firebase():
    global cred, db
    
    if firebase_admin._apps:
        db = firestore.client()
        return db
    
    cred_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'privateKey_firebase.json'
    )
    
    print(f"Firebase cred path: {cred_path}")
    print(f"Exists: {os.path.exists(cred_path)}")
    
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase initialized successfully")
        return db
    
    print("Firebase cred file not found!")
    return None

def get_db():
    global db
    if db is None:
        init_firebase()
    return db

def get_technicians():
    db = get_db()
    if db is None:
        return []
    
    docs = db.collection('technicians').stream()
    return [{'id': doc.id, **doc.to_dict()} for doc in docs]

def get_incidents():
    db = get_db()
    if db is None:
        return []
    
    docs = db.collection('incidences').stream()
    return [{'id': doc.id, **doc.to_dict()} for doc in docs]

def get_visits():
    db = get_db()
    if db is None:
        return []
    
    docs = db.collection('visits').stream()
    return [{'id': doc.id, **doc.to_dict()} for doc in docs]

def get_contracts():
    db = get_db()
    if db is None:
        return []
    
    docs = db.collection('contracts').stream()
    return [{'id': doc.id, **doc.to_dict()} for doc in docs]

def get_reports():
    db = get_db()
    if db is None:
        return []
    
    docs = db.collection('reports').stream()
    return [{'id': doc.id, **doc.to_dict()} for doc in docs]

def get_pending_tasks():
    db = get_db()
    if db is None:
        return []
    
    visits = db.collection('visits').where('status', 'in', ['pendent', 'en_proces']).stream()
    tasks = []
    
    for visit in visits:
        visit_data = visit.to_dict()
        
        incidence = None
        if visit_data.get('incidence_id'):
            incidence_ref = db.collection('incidences').document(visit_data['incidence_id']).get()
            if incidence_ref.exists:
                incidence = incidence_ref.to_dict()
        
        charger = None
        contract = None
        if visit_data.get('incidence_id'):
            incidence = incidence_ref.to_dict() if incidence_ref.exists else None
        
        task = {
            'id': visit.id,
            'type': visit_data.get('visit_type', 'manteniment'),
            'status': visit_data.get('status', 'pendent'),
            'address': visit_data.get('address', ''),
            'latitude': visit_data.get('location', {}).get('_latitude'),
            'longitude': visit_data.get('location', {}).get('_longitude'),
            'planned_date': visit_data.get('planned_date', {}).get('_seconds'),
            'incidence': incidence,
            'technician_id': visit_data.get('technician_id')
        }
        tasks.append(task)
    
    return tasks

def get_technician(tech_id):
    db = get_db()
    if db is None:
        return None
    
    doc = db.collection('technicians').document(tech_id).get()
    if doc.exists:
        return {'id': doc.id, **doc.to_dict()}
    return None
