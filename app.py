import streamlit as st
import visualizer
import pandas as pd
import numpy as np
import json
from datetime import datetime

def get_machine_header(machine_type, tool, spindle, max_rpm=3000):
    if machine_type == "Fanuc / Haas":
        return [
            "O1000 (PROGRAM NAME)",
            "G21 G18 G40 G80 G99 (SAFETY LINE)",
            f"T{tool} (TOOL SELECTION)",
            f"G50 S{max_rpm} (MAX SPINDLE SPEED)",
            f"G97 S{spindle} M03 (CONST SPINDLE START)"
        ]
    elif machine_type == "Siemens":
        return [
            "; PROGRAM FOR SIEMENS 840D",
            "G71 G90 G95 (METRIC, ABSOLUTE, FEED/REV)",
            f"LIMS={max_rpm} (LIMIT SPINDLE SPEED)",
            f"T=\"TOOL_{tool[:2]}\" D1",
            f"G97 S{spindle} M3"
        ]
    else: # LinuxCNC
        return [
            "( PROGRAM FOR LINUXCNC )",
            "G21 G18 G40 G49 G80 G90 G94",
            f"T{tool} M6",
            f"G96 S{spindle} M3 (CSS MODE)"
        ]

def get_machine_footer(machine_type):
    if machine_type == "Siemens":
        return ["M09", "M05", "G74 X0 Z0", "M30"]
    return ["M09", "M05", "G28 U0 W0", "M30"]

st.set_page_config(page_title="CNC G-Code Generator", page_icon="🔧", layout="wide")

# Custom CSS for Premium Engineering Look
st.markdown("""
<style>
/* GLOBAL THEME LOCK */
html, body, [data-testid="stAppViewContainer"], .main {
    background-color: #020617 !important;
    color: #f8fafc !important;
}
/* TRANSPARENT INPUTS */
div[data-baseweb="input"], div[data-baseweb="select"], div.stNumberInput div, div.stTextInput div {
    background-color: transparent !important;
    color: #ffffff !important;
    border: 1px solid #ffffff !important;
}
input { color: #ffffff !important; font-size: 1.3rem !important; font-weight: 600 !important; }
label p { font-size: 1.5rem !important; font-weight: 900 !important; color: #ffffff !important; text-transform: uppercase; }
h1 { font-size: 4rem !important; color: #ffffff !important; font-weight: 900 !important; }
.stButton>button {
    background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%) !important;
    color: #ffffff !important;
    border: 2px solid #ffffff !important;
    font-weight: 800 !important;
    font-size: 1.8rem !important;
    min-height: 70px !important;
}
.stCodeBlock { background-color: #000000 !important; border: 2px solid #38bdf8 !important; border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

MATERIALS = {
    "Aluminum (6061)": {"speed": 2500, "feed": 0.25, "doc": 1.5},
    "Mild Steel (1018)": {"speed": 1200, "feed": 0.15, "doc": 1.0},
    "Stainless Steel (304)": {"speed": 800, "feed": 0.10, "doc": 0.5},
    "Brass": {"speed": 2200, "feed": 0.30, "doc": 2.0},
    "Custom": {"speed": 1200, "feed": 0.2, "doc": 1.0}
}

st.title("⚙️ CNC G-CODE GENERATOR")

# Initialize state
if 'init_dia' not in st.session_state: st.session_state.init_dia = 50.0
if 'fin_dia' not in st.session_state: st.session_state.fin_dia = 40.0
if 'init_len' not in st.session_state: st.session_state.init_len = 100.0
if 'fin_len' not in st.session_state: st.session_state.fin_len = 80.0

with st.sidebar:
    st.header("🛠 Configuration")
    machine_type = st.selectbox("Controller Type", ["Fanuc / Haas", "Siemens", "LinuxCNC"])
    material = st.selectbox("Material", list(MATERIALS.keys()))
    mat_data = MATERIALS[material]
    max_rpm = st.number_input("Max RPM", value=3000)

tab1, tab2 = st.tabs(["Turning & Facing", "Threading"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        i_dia = st.number_input("Initial Diameter", value=st.session_state.init_dia)
        f_dia = st.number_input("Final Diameter", value=st.session_state.fin_dia)
    with col2:
        i_len = st.number_input("Initial Length", value=st.session_state.init_len)
        f_len = st.number_input("Final Length", value=st.session_state.fin_len)
    
    doc = st.number_input("Depth of Cut (Diameter)", value=mat_data["doc"])
    feed = st.number_input("Feed Rate (mm/rev)", value=mat_data["feed"])
    speed = st.number_input("Spindle Speed (RPM)", value=mat_data["speed"])

    if st.button("🚀 GENERATE MULTI-PASS G-CODE"):
        res = get_machine_header(machine_type, "0101", speed, max_rpm)
        
        # Logic for multiple passes
        current_dia = i_dia
        res.append("( --- STARTING PASSES --- )")
        while current_dia > f_dia:
            current_dia -= doc
            if current_dia < f_dia: current_dia = f_dia
            res.append(f"G00 X{round(current_dia, 3)} Z2.0")
            res.append(f"G01 Z-{round(f_len, 3)} F{feed}")
            res.append(f"G00 X{round(i_dia + 2, 3)}") # Safely retract
            res.append(f"G00 Z2.0")
            
        res.extend(get_machine_footer(machine_type))
        st.code("\n".join(res))
