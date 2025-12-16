import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import streamlit as st
import json
import os

# Placeholder for mock data if DB is not available
MOCK_MATERIALS = [
    {"name": "Standard Vinyl", "cost_per_m2": 15.0, "roll_width": 1.37, "supplier": "Supplier A"},
    {"name": "Premium Vinyl", "cost_per_m2": 25.0, "roll_width": 1.52, "supplier": "Supplier B"},
    {"name": "Laminate Gloss", "cost_per_m2": 10.0, "roll_width": 1.37, "supplier": "Supplier A"},
    {"name": "Laminate Matte", "cost_per_m2": 12.0, "roll_width": 1.37, "supplier": "Supplier C"},
]

def get_db():
    """
    Initializes and returns the Firestore client.
    Returns None if credentials are missing (Mock mode).
    """
    # Check if app is already initialized
    try:
        app = firebase_admin.get_app()
        return firestore.client()
    except ValueError:
        pass # Not initialized, proceed

    # Try to find credentials
    cred_path = "serviceAccountKey.json"
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        return firestore.client()
    
    return None

def fetch_materials():
    """
    Fetches materials from Firestore 'materials' collection.
    Returns a list of dicts.
    """
    db = get_db()
    materials = []
    
    if db:
        try:
            docs = db.collection('materials').stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                materials.append(data)
        except Exception as e:
            st.error(f"Error fetching from DB: {e}")
            return MOCK_MATERIALS
    else:
        # Return mock data if no DB connection
        materials = MOCK_MATERIALS
        
    return materials

def add_material(name, cost, width, supplier):
    """
    Adds a single material to Firestore.
    """
    db = get_db()
    if db:
        try:
            db.collection('materials').add({
                'name': name,
                'cost_per_m2': float(cost),
                'roll_width': float(width),
                'supplier': supplier
            })
            return True
        except Exception as e:
            st.error(f"Error adding to DB: {e}")
            return False
    else:
        # Mock Mode: Add to local list
        MOCK_MATERIALS.append({
            'name': name,
            'cost_per_m2': float(cost),
            'roll_width': float(width),
            'supplier': supplier
        })
        st.success(f"Added {name} to local session (Mock Mode).")
        return True

def bulk_upload_materials(df):
    """
    Uploads a dataframe of materials to Firestore.
    Expected columns: 'Product', 'Price', 'Width', 'Supplier' (optional)
    """
    db = get_db()
    
    count = 0
    if not db:
        # Mock Mode: Bulk add to local list
        for index, row in df.iterrows():
            MOCK_MATERIALS.append({
                'name': row.get('Product', 'Unknown'),
                'cost_per_m2': float(row.get('Price', 0.0)),
                'roll_width': float(row.get('Width', 1.37)),
                'supplier': row.get('Supplier', 'Unknown')
            })
            count += 1
        return count
    
    batch = db.batch()
    
    for index, row in df.iterrows():
        doc_ref = db.collection('materials').document()
        batch.set(doc_ref, {
            'name': row.get('Product', 'Unknown'),
            'cost_per_m2': float(row.get('Price', 0.0)),
            'roll_width': float(row.get('Width', 1.37)),
            'supplier': row.get('Supplier', 'Unknown')
        })
        count += 1
        
        # Firestore batch limit is 500, commit every 400 to be safe
        if count % 400 == 0:
            batch.commit()
            batch = db.batch()
            
    if count % 400 != 0:
        batch.commit()
    
    return count
