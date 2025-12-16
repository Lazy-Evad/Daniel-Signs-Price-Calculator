import streamlit as st
import pandas as pd
from components.calculator import show_calculator
from components.supplier import show_supplier_manager
from utils.db import fetch_jobs

# Page Configuration
st.set_page_config(
    page_title="Daniel Signs Quote Calculator",
    page_icon="📏",
    layout="wide"
)

def main():
    st.markdown("<h1 style='text-align: center;'>Daniel Signs Quote Calculator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; font-size: 0.8em;'>Built by Lazylabz</p>", unsafe_allow_html=True)

    # --- Session State Init ---
    if 'hourly_rate' not in st.session_state:
        st.session_state.hourly_rate = 66.04
    if 'wastage_def' not in st.session_state:
        st.session_state.wastage_def = 15.0
    if 'markup_std_def' not in st.session_state:
        st.session_state.markup_std_def = 2.5
    if 'markup_prem_def' not in st.session_state:
        st.session_state.markup_prem_def = 4.0

    # --- Sidebar Settings ---
    # Moved Overhead Settings to 'Settings' tab
    
    st.sidebar.header("Client Details")
    c_name = st.sidebar.text_input("Client Name", placeholder="Start typing...")
    c_contact = st.sidebar.text_input("Contact / Ref", placeholder="e.g. email or PO#")
    j_desc = st.sidebar.text_area("Job Description", placeholder="Brief description of the job...")
    
    client_info = {
        "name": c_name,
        "contact": c_contact,
        "description": j_desc
    }
    
    # --- Main Navigation ---
    tab_calc, tab_supp, tab_hist, tab_settings = st.tabs(["💰 Calculator", "📦 Supplier Manager", "📜 Job History", "⚙️ Settings"])
    
    with tab_calc:
        show_calculator(st.session_state.hourly_rate, client_info)
        
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
                    "Quote (Std)": res.get('standard_price', 0),
                    "Quote (Prem)": res.get('premium_price', 0),
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
                    "Quote (Std)": st.column_config.NumberColumn("Quote (Std)", format="£%.2f"),
                    "Quote (Prem)": st.column_config.NumberColumn("Quote (Prem)", format="£%.2f"),
                },
                disabled=["ID", "Date", "Client", "Reference", "Description", "Quote (Std)", "Quote (Prem)"]
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
        st.number_input(
            "Hourly Shop Rate (£)", 
            min_value=0.0,
            step=1.0, 
            format="%.2f",
            key="hourly_rate",
            help="The cost of running the shop per hour (overhead)."
        )
        st.number_input(
            "Material Wastage (%)", 
            min_value=0.0,
            max_value=100.0,
            step=5.0, 
            key="wastage_def",
            help="Percentage of material cost added to cover offcuts and errors."
        )
        
        c1, c2 = st.columns(2)
        with c1:
            st.number_input(
                "Standard Markup (x)", 
                min_value=1.0,
                step=0.1, 
                format="%.1f",
                key="markup_std_def",
                help="Multiplier applied to material cost for standard pricing."
            )
        with c2:
            st.number_input(
                "Premium Markup (x)", 
                min_value=1.0,
                step=0.1, 
                format="%.1f",
                key="markup_prem_def",
                help="Multiplier applied to material cost for premium pricing."
            )

if __name__ == "__main__":
    main()
