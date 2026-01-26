import streamlit as st
import visualizer
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- G-CODE GENERATION LOGIC ---

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

# --- UI CONFIGURATION ---

st.set_page_config(page_title="CNC G-Code Generator", page_icon="🔧", layout="wide")

# PREMIUM CSS (Industrial Dark Theme)
st.markdown("""
<style>
/* GLOBAL THEME LOCK */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"], .main {
    background-color: #020617 !important;
    background: #020617 !important;
    color: #f8fafc !important;
}

[data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="stSidebarNav"] {
    background-color: #020617 !important;
    background: #020617 !important;
    border-right: 2px solid #1e293b !important;
}

div[data-baseweb="input"], div[data-baseweb="select"], div.stNumberInput div, div.stTextInput div {
    background-color: transparent !important;
    color: #ffffff !important;
    border-color: #334155 !important;
}

input, select { color: #ffffff !important; font-size: 1.3rem !important; font-weight: 600 !important; }

label[data-testid="stWidgetLabel"] p {
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    text-transform: uppercase;
    margin-bottom: 5px !important;
}

h1 { font-size: 4.8rem !important; font-weight: 900 !important; color: #ffffff !important; text-transform: uppercase; }

.stTabs [data-baseweb="tab"] p { font-size: 2rem !important; font-weight: 800 !important; color: #94a3b8 !important; }
.stTabs [aria-selected="true"] p { color: #38bdf8 !important; }

.stButton>button {
    background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%) !important;
    color: #ffffff !important;
    border: 2px solid #38bdf8 !important;
    border-radius: 12px !important;
    font-weight: 900 !important;
    font-size: 1.8rem !important;
    min-height: 80px !important;
    width: 100% !important;
}
.stCodeBlock { background-color: #000000 !important; border: 2px solid #ffffff !important; border-radius: 15px !important; }
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

# Initialize Session States
if 'init_dia' not in st.session_state: st.session_state.init_dia = 50.0
if 'fin_dia' not in st.session_state: st.session_state.fin_dia = 40.0
if 'init_len' not in st.session_state: st.session_state.init_len = 100.0
if 'fin_len' not in st.session_state: st.session_state.fin_len = 80.0

with st.sidebar:
    st.header("📂 Machine Layout")
    machine_type = st.selectbox("Controller Type", ["Fanuc / Haas", "Siemens", "LinuxCNC"])
    material = st.selectbox("Stock Material", list(MATERIALS.keys()))
    mat_data = MATERIALS[material]
    max_rpm = st.number_input("Max RPM Limit", value=3000)

tab1, tab2, tab3, tab4 = st.tabs(["Turning & Facing", "Step Turning", "Threading", "Advanced Options"])

with tab1:
    st.subheader("🧾 Workpiece Dimensions")
    c1, c2 = st.columns(2)
    with c1:
        i_dia = st.number_input("Initial Diameter (mm)", value=st.session_state.init_dia)
        f_dia = st.number_input("Final Diameter (mm)", value=st.session_state.fin_dia)
    with c2:
        i_len = st.number_input("Initial Length (mm)", value=st.session_state.init_len)
        f_len = st.number_input("Final Length (mm)", value=st.session_state.fin_len)

    st.markdown('<div style="background: rgba(255,255,255,0.02); padding: 25px; border-radius: 20px; border: 1px solid #1e293b;">', unsafe_allow_html=True)
    st.subheader("🖼 Digital Workpiece Twin")
    fig = visualizer.plot_workpiece(i_dia, f_dia, i_len, f_len)
    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)

    doc = st.number_input("Depth of Cut", value=mat_data["doc"])
    feed = st.number_input("Feed (mm/rev)", value=mat_data["feed"])
    speed = st.number_input("Spindle RPM", value=mat_data["speed"])

    if st.button("🚀 GENERATE INDUSTRIAL G-CODE"):
        res = get_machine_header(machine_type, "0101", speed, max_rpm)
        current_dia = i_dia
        while current_dia > f_dia:
            current_dia -= doc
            if current_dia < f_dia: current_dia = f_dia
            res.append(f"G00 X{round(current_dia, 3)} Z2.0")
            res.append(f"G01 Z-{round(f_len, 3)} F{feed}")
            res.append(f"G00 X{round(i_dia + 2, 3)} Z2.0")
        res.extend(get_machine_footer(machine_type))
        st.code("\n".join(res))

with tab2:
    st.subheader("🧾 Multi-Step Turning")
    s_num_steps = st.number_input("Number of Steps", min_value=1, step=1, value=2)
    steps_data = []
    for i in range(int(s_num_steps)):
        st.markdown(f"#### Step {i+1}")
        col_a, col_b = st.columns(2)
        with col_a: s_dia = st.number_input(f"Step {i+1} Diameter", value=40.0 - (i*5), key=f"s_dia_{i}")
        with col_b: s_len = st.number_input(f"Step {i+1} Length", value=15.0, key=f"s_len_{i}")
        steps_data.append((s_dia, s_len))
    
    st.subheader("🖼 Step Preview")
    step_fig = visualizer.plot_step_turning(i_dia, i_len, steps_data)
    st.pyplot(step_fig)

with tab3:
    st.subheader("🧵 Threading Cycle (G76)")
    t_dia = st.number_input("Major Diameter", value=20.0)
    t_pitch = st.number_input("Pitch", value=1.5)
    t_len = st.number_input("Length", value=30.0)
    if st.button("🚀 GENERATE THREAD"):
        st.code("( THREADING G-CODE GENERATED )")

with tab4:
    st.subheader("🛠 Advanced Machining")
    st.info("💎 Grooving | 📐 Tapering | 🕳 Boring (Coming Soon)")
