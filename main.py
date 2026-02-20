import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from components.calc_v5 import show_calculator as show_calculator_v5
from components.supplier import show_supplier_manager
from utils.db import fetch_jobs, delete_job
from utils.styles import inject_dashboard_css

# Page Configuration
st.set_page_config(
    page_title="Daniel Signs Quote Calculator",
    page_icon="📏",
    layout="wide"
)

# ─────────────────────────────────────────────
#  AUTH CONFIG
#  To change passwords: update 'password' fields
#  below with new bcrypt hashes generated via:
#  python -c "import bcrypt; print(bcrypt.hashpw(b'NEW_PASS', bcrypt.gensalt(12)).decode())"
# ─────────────────────────────────────────────
credentials = {
    "usernames": {
        "dean": {
            "name": "Dean",
            "password": "$2b$12$W.bpFKI34YLAdqIkCOR0mOy0y1tm5BmWr4inOt8wyDuS/ybaCHvZm",  # signs2024
        },
        "admin": {
            "name": "Admin",
            "password": "$2b$12$9Xo16S1vHGUO9QzeSbN/gO.HXRxEiDIxgGcmQvdlwTkZt/q0EnDlO",  # admin2024
        },
    }
}

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="daniel_signs_auth",
    cookie_key="ds_secret_key_2024_xK9mP",   # any random string - keeps sessions valid
    cookie_expiry_days=7,
)

# ─────────────────────────────────────────────
#  LOGIN WIDGET
# ─────────────────────────────────────────────
authenticator.login(location="main")

auth_status = st.session_state.get("authentication_status")
username    = st.session_state.get("username", "")
name        = st.session_state.get("name", "")

# ── NOT LOGGED IN ──────────────────────────────
if auth_status is False:
    st.error("❌ Username or password is incorrect. Please try again.")
    st.stop()

elif auth_status is None:
    # Show a nice branded holding message under the login box
    st.markdown(
        """
        <div style="text-align:center; margin-top:2rem; color:#888; font-size:0.9rem;">
            🔒 Please log in to access the Daniel Signs Quote Calculator
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ── LOGGED IN ──────────────────────────────────
def main():
    # --- Theme Logic ---
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'

    # Inject CSS
    inject_dashboard_css()

    # --- Session State Init ---
    defaults = {
        "hourly_rate": 66.04, "workshop_rate": 60.00, "fitting_rate": 75.00,
        "travel_rate": 75.00, "wastage_v5": 15.0, "markup_v5": 1.0, "job_items": []
    }
    for key, val in defaults.items():
        if key not in st.session_state: st.session_state[key] = val

    # --- Sidebar ---
    with st.sidebar:
        st.markdown("### 👤 CLIENT DETAILS")
        c_name    = st.text_input("Client Name",    placeholder="Start typing...")
        c_contact = st.text_input("Contact / Ref",  placeholder="e.g. email or PO#")
        j_desc    = st.text_area("Job Description",  placeholder="Brief description...")

        st.divider()
        if st.button("♻️ RESET CALCULATOR", use_container_width=True):
            st.session_state.job_items = []; st.rerun()
        if st.button("♻️ RESET FULL STATE", use_container_width=True):
            for k in defaults:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

        st.divider()
        # Logout button in sidebar
        authenticator.logout("🚪 Sign Out", location="sidebar")
        st.caption(f"Signed in as **{name}**")

    client_info = {"name": c_name, "contact": c_contact, "description": j_desc}

    # --- TOPBAR ---
    header_left, header_mid, header_right = st.columns([3, 1, 1.5])

    with header_left:
        st.markdown(
            f'<p class="ds-title">DANIEL SIGNS HUB '
            f'<span style="font-size: 12px; color: #888;">[v1.4] — {name}</span></p>',
            unsafe_allow_html=True
        )

    with header_right:
        t_col1, t_col2 = st.columns([2, 1])
        t_col1.markdown('<p class="ds-subtle" style="text-align: right; margin-top: 10px;">Dark Mode</p>', unsafe_allow_html=True)
        prev_theme = st.session_state.theme
        dark_mode = t_col2.toggle(" ", value=(st.session_state.theme == "dark"), label_visibility="collapsed", key="global_theme_toggle")
        st.session_state.theme = "dark" if dark_mode else "light"
        if prev_theme != st.session_state.theme:
            st.rerun()

    # --- MAIN TABS ---
    tab_calc, tab_supp, tab_hist, tab_settings = st.tabs(
        ["💰 Calculator", "📦 Supplier Manager", "📜 Job History", "⚙️ Settings"]
    )

    with tab_calc:
        show_calculator_v5(st.session_state.hourly_rate, client_info)

    with tab_supp:
        show_supplier_manager()

    with tab_hist:
        st.header("Job History")
        jobs = fetch_jobs()
        if jobs:
            st.markdown("""
                <style>
                [data-testid="stColumn"] {
                    border-right: 1px solid rgba(255, 255, 255, 0.3) !important;
                    padding-right: 15px !important;
                    padding-left: 15px !important;
                }
                [data-testid="stColumn"]:last-child { border-right: none !important; }
                div.stButton > button { padding: 0px; }
                </style>
            """, unsafe_allow_html=True)

            h1, h2, h3, h4, h5, h6, h7, h8 = st.columns([1.5, 2, 3, 1.2, 1.2, 1.2, 0.8, 0.8])
            h1.markdown("**Date**");       h2.markdown("**Client**")
            h3.markdown("**Description**"); h4.markdown("**Cost to Produce**")
            h5.markdown("**Quote**");       h6.markdown("**Profit**")
            h7.markdown("**Details**");     h8.markdown("**Del**")
            st.divider()

            for i, j in enumerate(jobs):
                c_info    = j.get('client', {}) or {}
                res       = j.get('results', {}) or {}
                raw_date  = j.get('created_at')
                date_str  = raw_date.strftime("%b %d, %Y") if hasattr(raw_date, 'strftime') else str(raw_date)[:10]

                quote_val  = res.get('quote_price', 0)
                cost_val   = res.get('breakeven',   0)
                profit_val = res.get('profit',      0)
                markup_val = j.get('markup', 'N/A')

                r1, r2, r3, r4, r5, r6, r7, r8 = st.columns([1.5, 2, 3, 1.2, 1.2, 1.2, 0.8, 0.8])
                r1.write(date_str)
                r2.write(c_info.get('name', 'Unknown'))
                r3.write(c_info.get('description', ''))
                r4.write(f"£{cost_val:,.2f}")
                r5.write(f"£{quote_val:,.2f}")
                r6.write(f"£{profit_val:,.2f}")

                with r7:
                    if st.button("👁️", key=f"view_{i}", help="View Details"):
                        st.session_state[f"show_details_{i}"] = not st.session_state.get(f"show_details_{i}", False)

                with r8:
                    if st.button("🗑️", key=f"del_job_{i}", help="Delete Job"):
                        if delete_job(j.get('id')):
                            st.toast(f"Deleted job for {c_info.get('name')}")
                            st.rerun()

                if st.session_state.get(f"show_details_{i}", False):
                    with st.container(border=True):
                        st.markdown(f"#### Breakdown — {c_info.get('name')}")
                        st.markdown(f"**Markup:** {markup_val}x")
                        cols = st.columns(2)
                        with cols[0]:
                            st.markdown("**Items & Labour:**")
                            for item in j.get('items', []):
                                st.write(f"- {item['description']}")
                        with cols[1]:
                            st.markdown("**Financial Summary:**")
                            st.write(f"- Material Cost: £{res.get('material_cost_total', 0):,.2f}")
                            st.write(f"- Labour/Internal Cost: £{res.get('shop_cost_internal', 0) + res.get('install_cost_internal', 0) + res.get('travel_cost_internal', 0):,.2f}")
                            st.write(f"- Total Cost to Produce: £{cost_val:,.2f}")
                            st.write(f"- Markup Multiplier: {markup_val}x")
                            st.write(f"- Final Quote: £{quote_val:,.2f}")
                            st.write(f"**- Calculated Profit: £{profit_val:,.2f}**")
                st.divider()
        else:
            st.info("No saved jobs found.")

    with tab_settings:
        st.header("Settings")
        st.number_input("Workshop Rate (£/hr)", key="workshop_rate")
        st.number_input("Fitting Rate (£/hr)",  key="fitting_rate")
        st.number_input("Travel Rate (£/hr)",   key="travel_rate")
        st.number_input("Shop Overhead (£/hr)", key="hourly_rate")


if __name__ == "__main__":
    main()
