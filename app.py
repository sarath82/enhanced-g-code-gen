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

    /* CLEAR INPUTS & NO LABEL BOXES */
    div[data-baseweb="input"], 
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"],
    div[data-baseweb="select"], 
    div[data-baseweb="select"] > div,
    div[role="combobox"],
    div.stSelectbox div,
    div.stNumberInput div,
    div.stTextInput div {
        background-color: transparent !important;
        background: transparent !important;
        color: #ffffff !important;
        border-color: #334155 !important;
        box-shadow: none !important;
    }

    input, select {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
    }

    /* MEGA WHITE LABELS - Flat, no boxes */
    label[data-testid="stWidgetLabel"] p {
        background-color: transparent !important;
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px !important;
        border: none !important;
    }
    
    /* TITLES */
    h1 { 
        font-size: 4.8rem !important; 
        font-weight: 900 !important; 
        color: #ffffff !important; 
        text-transform: uppercase;
        margin-bottom: 1rem !important;
    }
    
    .stMarkdown h3 {
        font-size: 2.2rem !important;
        color: #818cf8 !important;
        font-weight: 700 !important;
    }
    
    h2 { 
        font-size: 3rem !important; 
        color: #f1f5f9 !important; 
        border-left: 10px solid #38bdf8; 
        padding-left: 20px; 
        margin-top: 40px !important;
        text-transform: uppercase;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 50px;
        background-color: transparent !important; 
        margin-bottom: 30px !important;
    }
    .stTabs [data-baseweb="tab"] p { 
        font-size: 2.2rem !important; 
        font-weight: 800 !important; 
        color: #94a3b8 !important; 
    }
    .stTabs [aria-selected="true"] p { 
        color: #38bdf8 !important; 
    }

    /* BUTTONS */
    .stButton>button {
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%) !important;
        color: #ffffff !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 12px !important;
        font-weight: 900 !important;
        font-size: 1.8rem !important;
        min-height: 80px !important;
        width: 100% !important;
        text-transform: uppercase;
        box-shadow: 0 5px 15px rgba(56, 189, 248, 0.2) !important;
    }
    .stButton>button:hover {
        border-color: #ffffff !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(56, 189, 248, 0.4) !important;
    }

    /* CODE TERMINAL */
    .stCodeBlock {
        background-color: #000000 !important;
        border: 2px solid #ffffff !important;
        border-radius: 15px !important;
        padding: 20px !important;
        margin-top: 30px !important;
    }
    
    div[data-testid="stCodeBlock"] pre, 
    div[data-testid="stCodeBlock"] code {
        font-size: 1.8rem !important;
        color: #ffffff !important;
    }

    /* Sidebar Background Specificity */
    [data-testid="stSidebar"] section {
        background-color: #020617 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Material Settings
MATERIALS = {
    "Aluminum (6061)": {"speed": 2500, "feed": 0.25, "doc": 1.5},
    "Mild Steel (1018)": {"speed": 1200, "feed": 0.15, "doc": 1.0},
    "Stainless Steel (304)": {"speed": 800, "feed": 0.10, "doc": 0.5},
    "Brass": {"speed": 2200, "feed": 0.30, "doc": 2.0},
    "Custom": {"speed": 1200, "feed": 0.2, "doc": 1.0}
}

st.title("⚙️ CNC G-CODE GENERATOR")
st.markdown("### Industrial-Grade Precision Manufacturing")

# Initialize Session States
def init_state(key, default):
    if key not in st.session_state:
        st.session_state[key] = default

init_state('init_dia', 50.0)
init_state('fin_dia', 40.0)
init_state('init_len', 100.0)
init_state('fin_len', 80.0)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1035/1035651.png", width=80)
    st.header("📂 Machine Layout")
    machine_type = st.selectbox("Controller Type", ["Fanuc / Haas", "Siemens", "LinuxCNC"], key='machine_type_select')
    
    st.markdown("---")
    st.subheader("💎 Stock Selection")
    material = st.selectbox("Stock Material", list(MATERIALS.keys()), key='material_select')
    mat_data = MATERIALS[material]
    
    st.markdown("---")
    st.subheader("🏎 Performance")
    max_rpm = st.number_input("Max RPM Limit", value=3000)

tab1, tab2, tab3, tab4 = st.tabs(["Turning & Facing", "Step Turning", "Threading", "Advanced Options"])

with tab1:
    st.subheader("🧾 Workpiece Dimensions")
    c1, c2 = st.columns(2)
    with c1:
        i_dia = st.number_input("Initial Diameter (mm)", value=st.session_state.init_dia, key='i_dia_input')
        f_dia = st.number_input("Final Diameter (mm)", value=st.session_state.fin_dia, key='f_dia_input')
    with c2:
        i_len = st.number_input("Initial Length (mm)", value=st.session_state.init_len, key='i_len_input')
        f_len = st.number_input("Final Length (mm)", value=st.session_state.fin_len, key='f_len_input')

    # THE GRAPH (Digital Twin)
    st.markdown('<div style="background: rgba(255,255,255,0.02); padding: 25px; border-radius: 20px; border: 1px solid #1e293b; margin-top: 20px;">', unsafe_allow_html=True)
    st.subheader("🖼 Digital Workpiece Twin")
    fig = visualizer.plot_workpiece(i_dia, f_dia, i_len, f_len)
    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("⚙️ Cutting Parameters")
    c3, c4, c5 = st.columns(3)
    with c3: doc = st.number_input("Depth of Cut", value=mat_data["doc"], key="doc_input")
    with c4: speed = st.number_input("Spindle RPM", value=mat_data["speed"], key="speed_input")
    with c5: feed = st.number_input("Feed (mm/rev)", value=mat_data["feed"], key="feed_input")

    if st.button("🚀 GENERATE INDUSTRIAL G-CODE"):
        res = get_machine_header(machine_type, "0101", speed, max_rpm)
        res.append("( OPERATION: MULTI-PASS TURNING )")
        
        # Proper Multi-Pass Logic
        current_dia = i_dia
        while current_dia > f_dia:
            current_dia -= doc
            if current_dia < f_dia: current_dia = f_dia
            res.append(f"G00 X{round(current_dia, 3)} Z2.0")
            res.append(f"G01 Z-{round(f_len, 3)} F{feed}")
            res.append(f"G00 X{round(i_dia + 2, 3)}") # Safely Retract
            res.append(f"G00 Z2.0")
            
        res.extend(get_machine_footer(machine_type))
        st.code("\n".join(res))
        st.download_button("📥 DOWNLOAD NC FILE", "\n".join(res), file_name="turning_facing.nc")

with tab2:
    st.subheader("🧾 Multi-Step Turning Details")
    col1, col2 = st.columns(2)
    with col1:
        s_initial_dia = st.number_input("Initial Diameter (mm)", min_value=0.0, value=st.session_state.init_dia, key="s_init_dia")
        s_initial_len = st.number_input("Initial Length (mm)", min_value=0.0, value=st.session_state.init_len, key="s_init_len")
    with col2:
        s_num_steps = st.number_input("Number of Steps", min_value=1, step=1, value=2, key="s_num")

    steps_data = []
    for i in range(int(s_num_steps)):
        st.markdown(f"#### Step {i+1}")
        col_a, col_b = st.columns(2)
        with col_a: step_dia = st.number_input(f"Step {i+1} Diameter", value=s_initial_dia - (i+1)*5, key=f"s_dia_{i}")
        with col_b: step_len = st.number_input(f"Step {i+1} Length", value=10.0, key=f"s_len_{i}")
        steps_data.append((step_dia, step_len))
    
    st.markdown('<div style="background: rgba(255,255,255,0.02); padding: 25px; border-radius: 20px; border: 1px solid #1e293b; margin-top: 20px;">', unsafe_allow_html=True)
    st.subheader("🖼 Step Preview")
    step_fig = visualizer.plot_step_turning(s_initial_dia, s_initial_len, steps_data)
    st.pyplot(step_fig)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 GENERATE STEP G-CODE"):
        res = get_machine_header(machine_type, "0202", mat_data["speed"], max_rpm)
        res.append("( OPERATION: MULTI-STEP TURNING )")
        z_pos = 0
        for i, (dia, length) in enumerate(steps_data):
            res.append(f"( STEP {i+1}: DIA {dia} LEN {length} )")
            res.append(f"G00 X{dia} Z{z_pos}")
            res.append(f"G01 Z-{z_pos + length} F{mat_data['feed']}")
            z_pos += length
        res.extend(get_machine_footer(machine_type))
        st.code("\n".join(res))
        st.download_button("📥 DOWNLOAD STEP NC", "\n".join(res), file_name="step_turning.nc")

with tab3:
    st.subheader("🧵 Threading Cycle (G76)")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        thread_dia = st.number_input("Major Diameter (mm)", value=20.0, key="t_dia")
        thread_pitch = st.number_input("Pitch (mm)", value=1.5, step=0.1, key="t_pitch")
    with col_t2:
        thread_len = st.number_input("Thread Length (mm)", value=30.0, key="t_len")
        thread_depth = st.number_input("Thread Depth (mm)", value=0.92, key="t_depth")

    if st.button("🚀 GENERATE THREADING G-CODE"):
        res = get_machine_header(machine_type, "0303", "500", max_rpm)
        res.append("( OPERATION: THREADING )")
        if machine_type == "Fanuc / Haas":
            res.append(f"G76 P010060 Q100 R0.05")
            res.append(f"G76 X{round(thread_dia - 2*thread_depth, 3)} Z-{thread_len} P{int(thread_depth*1000)} Q200 F{thread_pitch}")
        elif machine_type == "Siemens":
            res.append(f"CYCLE97({thread_pitch}, 0, {thread_dia}, -{thread_len}, {thread_dia}, {thread_dia - 2*thread_depth}, 0, 0, {thread_depth}, 0, 0, 0)")
        else: # LinuxCNC
            res.append(f"G76 P{thread_pitch} Z-{thread_len} I-0.1 J0.2 K{thread_depth} H3 L0 R1.5")
        res.extend(get_machine_footer(machine_type))
        st.code("\n".join(res))
        st.download_button("📥 DOWNLOAD THREADING NC", "\n".join(res), file_name="threading.nc")

with tab4:
    st.subheader("🛠 Advanced Machining Modules")
    st.markdown("---")
    c_adv1, c_adv2 = st.columns(2)
    with c_adv1:
        st.info("💎 **Grooving Module** (Coming Soon)")
        st.info("📐 **Taper Turning** (Coming Soon)")
    with c_adv2:
        st.info("🕳 **Boring Cycle** (Coming Soon)")
        st.info("⚙️ **Tool Library Manager** (Coming Soon)")
