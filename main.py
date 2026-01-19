import streamlit as st
import pandas as pd
from components.calc_v2 import show_calculator as show_calculator_v2
from components.supplier import show_supplier_manager
from utils.db import fetch_jobs, delete_job
from utils.styles import inject_dashboard_css

# Page Configuration
st.set_page_config(
    page_title="Daniel Signs Quote Calculator",
    page_icon="📏",
    layout="wide"
)

def main():
    # --- Theme Logic ---
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'

    # Inject CSS
    inject_dashboard_css()

    # --- Session State Init ---
    defaults = {
        "hourly_rate": 66.04, "workshop_rate": 60.00, "fitting_rate": 75.00,
        "travel_rate": 75.00, "wastage_def": 15.0, "markup_def": 3.0, "job_items": []
    }
    for key, val in defaults.items():
        if key not in st.session_state: st.session_state[key] = val

    # --- Sidebar: Reset Buttons Only ---
    with st.sidebar:
        st.markdown("### 👤 CLIENT DETAILS")
        c_name = st.text_input("Client Name", placeholder="Start typing...")
        c_contact = st.text_input("Contact / Ref", placeholder="e.g. email or PO#")
        j_desc = st.text_area("Job Description", placeholder="Brief description...")
        
        st.divider()
        if st.button("♻️ RESET CALCULATOR", use_container_width=True):
            st.session_state.job_items = []; st.rerun()
        if st.button("♻️ RESET FULL STATE", use_container_width=True):
            for k in defaults:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    client_info = {"name": c_name, "contact": c_contact, "description": j_desc}

    # --- TOPBAR: Fixed Branding & Theme Toggle ---
    # Using a 3-column layout for consistent alignment
    header_left, header_mid, header_right = st.columns([3, 1, 1.5])
    
    with header_left:
        st.markdown('<p class="ds-title">DANIEL SIGNS HUB</p>', unsafe_allow_html=True)
    
    with header_right:
        # Theme toggle area
        t_col1, t_col2 = st.columns([2, 1])
        t_col1.markdown('<p class="ds-subtle" style="text-align: right; margin-top: 10px;">Dark Mode</p>', unsafe_allow_html=True)
        prev_theme = st.session_state.theme
        dark_mode = t_col2.toggle(" ", value=(st.session_state.theme == "dark"), label_visibility="collapsed", key="global_theme_toggle")
        st.session_state.theme = "dark" if dark_mode else "light"
        if prev_theme != st.session_state.theme:
            st.rerun()

    # --- MAIN TABS (Styled to span full width via CSS) ---
    tab_calc, tab_supp, tab_hist, tab_settings = st.tabs(
        ["💰 Calculator", "📦 Supplier Manager", "📜 Job History", "⚙️ Settings"]
    )

    with tab_calc:
        show_calculator_v2(st.session_state.hourly_rate, client_info)
        
    with tab_supp:
        show_supplier_manager()

    with tab_hist:
        st.header("Job History")
        jobs = fetch_jobs()
        if jobs:
            history_data = []
            for j in jobs:
                c_info = j.get('client', {}) or {}
                res = j.get('results', {}) or {}
                raw_date = j.get('created_at')
                
                # Calculate Profit (Quote - Material Costs)
                quote_val = res.get('quote_price', 0)
                mat_cost_val = res.get('material_cost_total', 0)
                profit_val = quote_val - mat_cost_val

                history_data.append({
                    "ID": j.get('id'), 
                    "Delete": False, 
                    "Date": raw_date, 
                    "Client": c_info.get('name', 'Unknown'),
                    "Description": c_info.get('description', ''), 
                    "Quote": quote_val,
                    "Profit": profit_val
                })
            
            df_history = pd.DataFrame(history_data)
            
            # Professional column configuration
            st.data_editor(
                df_history, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "ID": None,  # Hides the ID column from view
                    "Date": st.column_config.DateColumn("Date", format="MMM DD, YYYY"),
                    "Quote": st.column_config.NumberColumn("Quote", format="£%.2f"),
                    "Profit": st.column_config.NumberColumn("Profit", format="£%.2f"),
                }
            )
        else:
            st.info("No saved jobs found.")
            
    with tab_settings:
        st.header("Settings")
        st.number_input("Workshop Rate (£/hr)", key="workshop_rate")
        st.number_input("Fitting Rate (£/hr)", key="fitting_rate")
        st.number_input("Travel Rate (£/hr)", key="travel_rate")
        st.number_input("Shop Overhead (£/hr)", key="hourly_rate")
        st.divider()
        st.number_input("Material Wastage (%)", key="wastage_def")
        st.slider("Markup Multiplier (x)", min_value=2.5, max_value=5.0, key="markup_def")

if __name__ == "__main__":
    main()
