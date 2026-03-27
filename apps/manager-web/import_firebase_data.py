import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

def init_firestore_with_data():
    cred_path = 'privateKey_firebase.json'
    
    if not os.path.exists(cred_path):
        print(f"Error: No se encuentra {cred_path}")
        return
    
    cred = credentials.Certificate(cred_path)
    
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    json_path = '/home/oscar/Documentos/URV/3ro/Hackathon SmartMobility/Material Suport Hackato SmAIrt Mobility/database_backup.json'
    
    if not os.path.exists(json_path):
        print(f"Error: No se encuentra {json_path}")
        return
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    for collection_name, documents in data.items():
        print(f"Procesando colección: {collection_name}")
        
        for doc in documents:
            doc_id = doc.get('id')
            if doc_id:
                db.collection(collection_name).document(doc_id).set(doc)
                print(f"  - Insertado: {doc_id}")
            else:
                doc_ref = db.collection(collection_name).add(doc)
                print(f"  - Insertado con ID: {doc_ref[1].id}")
    
    print("\n¡Datos importados correctamente a Firestore!")

if __name__ == '__main__':
    init_firestore_with_data()
