import streamlit as st

def get_custom_css(theme: str):
    if theme == "dark":
        bg = "#0b0f14"
        surface = "#111827"
        surface2 = "#0f172a"
        text = "rgba(255,255,255,0.92)"
        text_muted = "rgba(255,255,255,0.68)"
        border = "rgba(255,255,255,0.12)"
        input_bg = "#1f2937" # Solid dark grey for inputs
        accent = "#f59e0b"
        shadow = "0 8px 24px rgba(0,0,0,0.35)"
    else:
        bg = "#f4f6fb"
        surface = "#ffffff"
        surface2 = "#ffffff"
        text = "rgba(17,24,39,0.92)"
        text_muted = "rgba(17,24,39,0.65)"
        border = "rgba(17,24,39,0.12)"
        input_bg = "#f9fafb"
        accent = "#f59e0b"
        shadow = "0 8px 24px rgba(0,0,0,0.10)"

    return f"""
    <style>
      :root {{
        --bg: {bg};
        --surface: {surface};
        --surface2: {surface2};
        --text: {text};
        --muted: {text_muted};
        --border: {border};
        --input: {input_bg};
        --accent: {accent};
        --shadow: {shadow};
        --r-card: 16px;
        --r-input: 12px;
      }}

      /* Base App */
      .stApp {{
        background: var(--bg) !important;
        color: var(--text) !important;
      }}

      /* KILL ALL DEFAULT WHITE BACKGROUNDS */
      [data-testid="stHeader"], 
      header, 
      .stTabs, 
      [data-baseweb="tab-list"],
      [data-testid="stVerticalBlockBorderWrapper"],
      .stForm,
      [data-testid="stNotification"] {{
        background-color: transparent !important;
      }}

      /* Canvas Layout */
      .block-container {{
        max-width: 1400px;
        padding: 1.5rem 2rem;
        margin-left: 0;
        margin-right: auto;
      }}

      /* TEXT VISIBILITY */
      p, label, span, h1, h2, h3, h4, h5, h6, small, 
      [data-testid="stMarkdownContainer"] p,
      [data-testid="stWidgetLabel"] p,
      .stMetric div {{
        color: var(--text) !important;
      }}

      /* INPUT FIELDS - KILL WHITE PARENTS */
      div[data-baseweb="input"],
      div[data-baseweb="base-input"],
      div[data-testid="stTextInputRootElement"],
      div[data-testid="stNumberInputContainer"],
      div[data-testid="stTextAreaRootElement"],
      div[data-baseweb="select"] > div {{
        background-color: var(--input) !important;
        background: var(--input) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--r-input) !important;
      }}

      .stTextInput input, 
      .stNumberInput input, 
      .stTextArea textarea,
      input[data-testid="stWidgetInput"],
      [data-baseweb="input"] input,
      [data-baseweb="textarea"] textarea {{
        background-color: transparent !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
        caret-color: var(--text) !important;
      }}

      /* FORM SUBMISSION BUTTONS (KILLS GIANT WHITE BOXES) */
      button[data-testid="stBaseButton-secondaryFormSubmit"],
      button[data-testid="stBaseButton-primary"],
      button[data-testid="stBaseButton-secondary"] {{
        background-color: var(--input) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--r-input) !important;
        width: 100% !important;
      }}
      button[data-testid="stBaseButton-secondaryFormSubmit"]:hover {{
        background-color: var(--accent) !important;
        color: #000 !important;
      }}

      /* CARDS (Containers) */
      [data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--r-card) !important;
        box-shadow: var(--shadow) !important;
        padding: 0 !important;
        margin-bottom: 1.5rem;
      }}
      
      .ds-card-header {{
        padding: 14px 20px;
        border-bottom: 1px solid var(--border);
        margin-bottom: 15px;
        font-weight: 800;
        color: var(--accent) !important;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }}

      /* TABS - SPREAD FULL WIDTH */
      .stTabs [data-baseweb="tab-list"] {{
        display: flex !important;
        width: 100% !important;
        gap: 30px !important;
        border-bottom: 1px solid var(--border) !important;
        margin-bottom: 30px !important;
      }}
      .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        border: none !important;
        color: var(--muted) !important;
        font-weight: 750 !important;
        padding: 12px 15px !important;
        flex-grow: 1 !important;
        text-align: center !important;
      }}
      .stTabs [aria-selected="true"] {{
        color: var(--text) !important;
        border-bottom: 3px solid var(--accent) !important;
      }}

      /* Sidebar & Utilities */
      section[data-testid="stSidebar"] {{
        background: var(--surface2) !important;
        border-right: 1px solid var(--border);
      }}
      .ds-title {{
        color: var(--accent) !important;
        font-size: 1.8rem !important;
        font-weight: 900;
        margin: 0;
      }}
      .ds-subtle {{
        color: var(--muted) !important;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
      }}

      /* Fix White Lines */
      hr, div.st-emotion-cache-1833ps4 {{
        border-color: var(--border) !important;
        background-color: var(--border) !important;
      }}

      /* Primary Theme Overrides */
      .ds-primary button {{
        background: var(--accent) !important;
        color: #000 !important;
        font-weight: 800 !important;
      }}
    </style>
    """

import streamlit as st

def inject_dashboard_css():
    theme = st.session_state.get('theme', 'dark')
    st.markdown(get_custom_css(theme), unsafe_allow_html=True)
