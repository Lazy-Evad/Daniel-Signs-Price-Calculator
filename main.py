import streamlit as st
import pandas as pd
from components.calc_v2 import show_calculator as show_calculator_v2
from components.supplier import show_supplier_manager
from utils.db import fetch_jobs
from utils.styles import get_custom_css

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
    st.markdown(get_custom_css(st.session_state.theme), unsafe_allow_html=True)

    # --- Session State Init ---
    if 'hourly_rate' not in st.session_state:
        st.session_state.hourly_rate = 66.04
    if 'workshop_rate' not in st.session_state:
        st.session_state.workshop_rate = 60.00
    if 'fitting_rate' not in st.session_state:
        st.session_state.fitting_rate = 75.00
    if 'travel_rate' not in st.session_state:
        st.session_state.travel_rate = 75.00
    if 'wastage_def' not in st.session_state:
        st.session_state.wastage_def = 15.0
    if 'markup_def' not in st.session_state:
        st.session_state.markup_def = 3.0

    # --- Sidebar: Client Details ---
    with st.sidebar:
        st.markdown("### 👤 CLIENT DETAILS")
        # Simplified labels as per requested look
        c_name = st.text_input("Client Name", placeholder="Start typing...")
        c_contact = st.text_input("Contact / Ref", placeholder="e.g. email or PO#")
        j_desc = st.text_area("Job Description", placeholder="Brief description...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        # Reset buttons grouped
        if st.button("♻️ RESET CALCULATOR"):
            st.session_state.job_items = []
            st.rerun()

    client_info = {"name": c_name, "contact": c_contact, "description": j_desc}

    # --- TOP HEADER BAR ---
    h_col1, h_col2, h_col3 = st.columns([4, 1.5, 2.5])
    
    with h_col1:
        # NAVIGATION TABS on the Left
        tab_calc, tab_supp, tab_hist, tab_settings = st.tabs(["💰 Calculator", "📦 Supplier Manager", "📜 Job History", "⚙️ Settings"])

    with h_col2:
        # THEME TOGGLE shifted toward center/right
        st.markdown("<p style='text-align:right; font-size:0.8rem; font-weight:700; opacity:0.6; margin-top:12px;'>THEME</p>", unsafe_allow_html=True)
        prev_theme = st.session_state.theme
        dark_mode = st.toggle("🌙", value=(st.session_state.theme == 'dark'), label_visibility="collapsed", key="top_bar_theme")
        st.session_state.theme = 'dark' if dark_mode else 'light'
        if prev_theme != st.session_state.theme:
            st.rerun()

    with h_col3:
        # BRANDING TITLE on the Right
        st.markdown("<h3 style='color:#FB923C; text-align:right; margin:0; padding-top:10px; font-size:1.4rem !important;'>DANIEL SIGNS OPERATIONS HUB</h3>", unsafe_allow_html=True)
    
    with tab_calc:
        # Emergency Reset if data format changed
        if st.sidebar.button("♻️ RESET CALCULATOR STATE"):
            st.session_state.job_items = []
            st.rerun()
        show_calculator_v2(st.session_state.hourly_rate, client_info)
        
    with tab_supp:
        show_supplier_manager()

    with tab_hist:
        st.header("Job History")
        
        if st.button("Refresh History"):
            st.rerun()
            
        from utils.db import fetch_jobs, delete_job
        jobs = fetch_jobs()

        if jobs:
            # Flatten for display
            history_data = []
            for j in jobs:
                # Handle missing keys safely
                c_info = j.get('client', {}) or {}
                res = j.get('results', {}) or {}
                
                # Format Date
                raw_date = j.get('created_at')
                try:
                    dt = pd.to_datetime(raw_date)
                    fmt_date = dt.strftime('%d-%b-%Y %H:%M')
                except:
                    fmt_date = str(raw_date)

                history_data.append({
                    "ID": j.get('id'), # Essential for delete
                    "Delete": False,   # Checkbox
                    "Date": fmt_date,
                    "Client": c_info.get('name', 'Unknown'),
                    "Reference": c_info.get('contact', ''),
                    "Description": c_info.get('description', ''),
                    "Quote": res.get('quote_price', res.get('standard_price', 0)), # Fallback for old records
                })
            
            df_hist = pd.DataFrame(history_data)
            
            # Interactive Table
            edited_df = st.data_editor(
                df_hist,
                key="history_editor",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": None, # Hide ID
                    "Delete": st.column_config.CheckboxColumn(
                        "Delete?",
                        help="Select to delete",
                        default=False,
                        width="small"
                    ),
                    "Date": st.column_config.TextColumn("Date", width="medium"),
                    "Client": st.column_config.TextColumn("Client", width="medium"),
                    "Description": st.column_config.TextColumn("Description", width="large"),
                    "Quote": st.column_config.NumberColumn("Quote", format="£%.2f"),
                },
                disabled=["ID", "Date", "Client", "Reference", "Description", "Quote"]
            )
            
            # Delete Logic
            to_delete = edited_df[edited_df["Delete"] == True]
            if not to_delete.empty:
                st.warning(f"Selected {len(to_delete)} jobs for deletion.")
                if st.button("🗑️ Confirm Delete"):
                    count = 0
                    for idx, row in to_delete.iterrows():
                        if delete_job(row['ID']):
                            count += 1
                    if count > 0:
                        st.success(f"Deleted {count} jobs!")
                        st.rerun()
        else:
            st.info("No saved jobs found.")
            
    with tab_settings:
        st.header("System Settings")
        st.subheader("Financial Defaults")
        col_rates1, col_rates2 = st.columns(2)
        with col_rates1:
            st.number_input(
                "Workshop Rate (£/hr/person)", 
                min_value=0.0,
                step=1.0, 
                format="%.2f",
                key="workshop_rate",
                help="Rate charged for production/workshop time per person."
            )
            st.number_input(
                "Fitting Rate (£/hr/person)", 
                min_value=0.0,
                step=1.0, 
                format="%.2f",
                key="fitting_rate",
                help="Rate charged for installation/fitting time per person."
            )
        with col_rates2:
            st.number_input(
                "Traveling Rate (£/hr/person)", 
                min_value=0.0,
                step=1.0, 
                format="%.2f",
                key="travel_rate",
                help="Rate charged for travel time per person."
            )
            st.number_input(
                "Internal Shop Overhead (£/hr)", 
                min_value=0.0,
                step=1.0, 
                format="%.2f",
                key="hourly_rate",
                help="The internal cost of running the shop per hour (for breakeven)."
            )

        st.divider()
        st.number_input(
            "Material Wastage (%)", 
            min_value=0.0,
            max_value=100.0,
            step=5.0, 
            key="wastage_def",
            help="Percentage of material cost added to cover offcuts and errors."
        )
        
        st.slider(
            "Markup Multiplier (x)", 
            min_value=2.5,
            max_value=5.0,
            step=0.1, 
            format="%.1f",
            key="markup_def",
            help="Multiplier applied to material cost for quoting."
        )

if __name__ == "__main__":
    main()
