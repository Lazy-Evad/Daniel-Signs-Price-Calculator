import streamlit as st
from components.calculator import show_calculator
from components.supplier import show_supplier_manager

# Page Configuration
st.set_page_config(
    page_title="Signage Pricing Calculator",
    page_icon="📏",
    layout="wide"
)

def main():
    st.title("Signage Pricing Calculator 🖨️")

    # --- Sidebar Settings ---
    st.sidebar.header("Overhead Settings")
    hourly_shop_rate = st.sidebar.number_input(
        "Hourly Shop Rate (£)", 
        value=66.04, 
        step=1.0, 
        format="%.2f",
        help="The cost of running the shop per hour (overhead)."
    )
    
    # --- Main Navigation ---
    tab_calc, tab_supp = st.tabs(["💰 Calculator", "📦 Supplier Manager"])
    
    with tab_calc:
        show_calculator(hourly_shop_rate)
        
    with tab_supp:
        show_supplier_manager()

if __name__ == "__main__":
    main()
