import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import streamlit as st
import json
import os
from datetime import datetime

# Placeholder for mock data if DB is not available
MOCK_MATERIALS = [
    {"name": "Standard Vinyl", "cost_per_m2": 15.0, "roll_width": 1.37, "supplier": "Supplier A", "category": "Vinyl"},
    {"name": "Premium Vinyl", "cost_per_m2": 25.0, "roll_width": 1.52, "supplier": "Supplier B", "category": "Vinyl"},
    {"name": "Laminate Gloss", "cost_per_m2": 10.0, "roll_width": 1.37, "supplier": "Supplier A", "category": "Vinyl"},
    {"name": "Laminate Matte", "cost_per_m2": 12.0, "roll_width": 1.37, "supplier": "Supplier C", "category": "Vinyl"},
]

def get_db():
    """
    Initializes and returns the Firestore client.
    Supports both local 'serviceAccountKey.json' and Streamlit Cloud 'st.secrets'.
    """
    # Check if app is already initialized
    try:
        app = firebase_admin.get_app()
        return firestore.client()
    except ValueError:
        pass # Not initialized, proceed

    # 1. Try Local File (Best for development)
    cred_path = "serviceAccountKey.json"
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        return firestore.client()

    # 2. Try Streamlit Secrets (Best for Cloud)
    # This expects a [firebase] section in .streamlit/secrets.toml
    if "firebase" in st.secrets:
        key_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(key_dict)
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
        for i, m in enumerate(MOCK_MATERIALS):
            if 'id' not in m:
                m['id'] = str(i)
        materials = MOCK_MATERIALS
        
    return materials

def update_material(mat_id, updates):
    """
    Updates a material in Firestore or Mock list.
    """
    db = get_db()
    if db:
        try:
            db.collection('materials').document(mat_id).update(updates)
            return True
        except Exception as e:
            st.error(f"Error updating DB: {e}")
            return False
    else:
        # Mock Mode
        for m in MOCK_MATERIALS:
            if m.get('id') == mat_id:
                m.update(updates)
                return True
        return False

def add_material(name, cost_m2, width, supplier, category="Vinyl", unit_cost=None, unit_type="linear_m"):
    """
    Adds a single material to Firestore.
    cost_m2: The standardized cost per square meter (for logic engine).
    unit_cost: The original cost entered by user (e.g. per sheet, per lm).
    unit_type: 'linear_m', 'sheet', 'item'
    """
    db = get_db()
    
    data = {
        'name': name,
        'cost_per_m2': float(cost_m2),
        'roll_width': float(width),
        'supplier': supplier,
        'category': category,
        'unit_cost': float(unit_cost) if unit_cost is not None else float(cost_m2),
        'unit_type': unit_type
    }

    if db:
        try:
            db.collection('materials').add(data)
            return True
        except Exception as e:
            st.error(f"Error adding to DB: {e}")
            return False
    else:
        # Mock Mode: Add to local list
        MOCK_MATERIALS.append(data)
        st.success(f"Added {name} to local session (Mock Mode).")
        return True

def bulk_upload_materials(df):
    """
    Uploads a dataframe of materials to Firestore.
    Expected columns: 'Product', 'Price', 'Width', 'Supplier' (optional)
    """
    db = get_db()
    
    count = 0
    # In bulk upload, we assume 'Vinyl' / 'Linear Meter' pricing for now unless specified
    # Or, we can update this later to handle columns for Category.
    
    if not db:
        # Mock Mode: Bulk add to local list
        for index, row in df.iterrows():
            MOCK_MATERIALS.append({
                'name': row.get('Product', 'Unknown'),
                'cost_per_m2': float(row.get('Price', 0.0)), # Processed outside to be m2
                'roll_width': float(row.get('Width', 1.37)),
                'supplier': row.get('Supplier', 'Unknown'),
                'category': 'Vinyl', # Default
                'unit_cost': float(row.get('Price', 0.0)) * float(row.get('Width', 1.37)), # Approximate reconstruction or just store raw
                'unit_type': 'linear_m'
            })
            count += 1
        return count
    
    batch = db.batch()
    
    for index, row in df.iterrows():
        doc_ref = db.collection('materials').document()
        # 'Price' in df is already converted to m2 by supplier.py logic before calling this?
        # Actually supplier.py sends converted price.
        # Ideally we update bulk_upload signature to be more robust, but tight constraint.
        batch.set(doc_ref, {
            'name': row.get('Product', 'Unknown'),
            'cost_per_m2': float(row.get('Price', 0.0)),
            'roll_width': float(row.get('Width', 1.37)),
            'supplier': row.get('Supplier', 'Unknown'),
            'category': 'Vinyl',
            'unit_type': 'linear_m'
        })
        count += 1
        
        # Firestore batch limit is 500, commit every 400 to be safe
        if count % 400 == 0:
            batch.commit()
            batch = db.batch()
            
    if count % 400 != 0:
        batch.commit()
    
    return count

# Placeholder for mock jobs
MOCK_JOBS = []

def save_job(job_data):
    """
    Saves a job estimate to Firestore 'jobs' collection.
    job_data: Dict containing client info, description, items, and totals.
    """
    db = get_db()
    
    # Add timestamp
    job_data['created_at'] = datetime.now()
    
    if db:
        try:
            db.collection('jobs').add(job_data)
            return True
        except Exception as e:
            st.error(f"Error adding job to DB: {e}")
            return False
    else:
        # Mock Mode
        MOCK_JOBS.append(job_data)
        st.success("Job saved to local session (Mock Mode).")
        return True

def fetch_jobs():
    """
    Fetches job history from Firestore 'jobs' collection.
    Returns a list of dicts.
    """
    db = get_db()
    jobs = []
    
    if db:
        try:
            # Order by created_at desc (Simplifying for debug)
            docs = db.collection('jobs').stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                jobs.append(data)
        except Exception as e:
            st.error(f"Error fetching jobs from DB: {e}")
            return MOCK_JOBS
    else:
        # Return mock data
        return MOCK_JOBS
        
    return jobs

def delete_job(job_id):
    """
    Deletes a job from Firestore or Mock list.
    """
    db = get_db()
    if db:
        try:
            db.collection('jobs').document(job_id).delete()
            return True
        except Exception as e:
            st.error(f"Error deleting job: {e}")
            return False
    else:
        # Mock Mode
        global MOCK_JOBS
        MOCK_JOBS = [j for j in MOCK_JOBS if j.get('id') != job_id]
        return True

def delete_material(mat_id):
    """
    Deletes a material from Firestore or Mock list.
    """
    db = get_db()
    if db:
        try:
            db.collection('materials').document(mat_id).delete()
            return True
        except Exception as e:
            st.error(f"Error deleting material: {e}")
            return False
    else:
        # Mock Mode
        global MOCK_MATERIALS
        MOCK_MATERIALS = [m for m in MOCK_MATERIALS if m.get('id') != mat_id]
        return True

# ── Settings persistence ─────────────────────────────────────────────────────

SETTINGS_DEFAULTS = {
    "hourly_rate":   66.04,
    "workshop_rate": 60.00,
    "fitting_rate":  75.00,
    "travel_rate":   75.00,
}

def load_settings():
    """
    Load rate settings from Firestore 'settings/rates' document.
    Returns a dict with the four rate keys, falling back to hardcoded defaults.
    """
    db = get_db()
    if db:
        try:
            doc = db.collection('settings').document('rates').get()
            if doc.exists:
                data = doc.to_dict()
                # Merge with defaults so any missing key still has a value
                return {k: float(data.get(k, v)) for k, v in SETTINGS_DEFAULTS.items()}
        except Exception as e:
            st.warning(f"Could not load settings from DB — using defaults. ({e})")
    return dict(SETTINGS_DEFAULTS)


def save_settings(rate_dict):
    """
    Persist rate settings to Firestore 'settings/rates' document.
    rate_dict: dict with keys hourly_rate, workshop_rate, fitting_rate, travel_rate
    """
    db = get_db()
    if db:
        try:
            db.collection('settings').document('rates').set(
                {k: float(v) for k, v in rate_dict.items()}
            )
            return True
        except Exception as e:
            st.error(f"Error saving settings: {e}")
            return False
    return False
