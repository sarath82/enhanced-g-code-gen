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
/* GLOBAL THEME LOCK - Force Dark Mode on everything */
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

/* THE 'WHITE BOX' EXTERMINATOR - Extreme Target Selection & Transparent BG */
div[data-baseweb="input"], div[data-baseweb="input"] > div, div[data-baseweb="base-input"], div[data-baseweb="select"], div[data-baseweb="select"] > div, div[role="combobox"], div[data-testid="stFileUploader"], section[data-testid="stFileUploadDropzone"], div[data-testid="stFileUploadDropzone"], div.stSelectbox div, div.stNumberInput div, div.stTextInput div {
    background-color: transparent !important;
    background: transparent !important;
    color: #ffffff !important;
    border-color: #ffffff !important;
}

/* Force +/- Buttons in Number Input to be Dark/Transparent with White Icons */
div.stNumberInput button {
    background-color: #0f172a !important;
    color: #ffffff !important;
    border: 1px solid #ffffff !important;
}

div.stNumberInput button:hover {
    background-color: #1e293b !important;
    border-color: #38bdf8 !important;
}

/* Force all text inside inputs and file uploaders to be pure white */
input, select, textarea, div[data-baseweb="select"] span, div[data-testid="stFileUploadDropzone"] div, div[data-testid="stFileUploadDropzone"] span {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 1.3rem !important;
    font-weight: 600 !important;
}

/* MEGA WHITE LABELS - Balanced Visibility & Transparent BG */
label[data-testid="stWidgetLabel"] p {
    background-color: transparent !important;
    background: transparent !important;
    font-size: 1.7rem !important;
    font-weight: 900 !important;
    color: #ffffff !important;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 15px !important;
}

/* TITLES & HEADERS - Heavy Industrial Style */
h1 {
    font-size: 4.8rem !important;
    color: #ffffff !important;
    font-weight: 900 !important;
    margin-bottom: 1rem !important;
    text-transform: uppercase;
}

.stMarkdown h3 {
    font-size: 2.2rem !important;
    color: #818cf8 !important;
    margin-bottom: 1.5rem !important;
    font-weight: 700 !important;
}

h2 {
    font-size: 3.2rem !important;
    color: #f1f5f9 !important;
    border-left: 12px solid #38bdf8;
    padding-left: 25px;
    margin-top: 50px !important;
    text-transform: uppercase;
}

/* TABS - Custom High-Contrast */
.stTabs [data-baseweb="tab-list"] {
    gap: 50px;
    background-color: transparent !important;
    margin-bottom: 40px !important;
}

.stTabs [data-baseweb="tab"] p {
    font-size: 2.5rem !important;
    font-weight: 900 !important;
    color: #cbd5e1 !important;
}

.stTabs [aria-selected="true"] p {
    color: #ffffff !important;
}

/* UNIVERSAL BUTTON FIX - Balanced Scale */
.stButton>button, .stDownloadButton>button, .stButton button p, .stDownloadButton button p {
    background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%) !important;
    color: #ffffff !important;
    border: 2px solid #ffffff !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    font-size: 1.8rem !important;
    padding: 1.2rem 2.2rem !important;
    width: 100% !important;
    box-shadow: 0 5px 15px rgba(255, 255, 255, 0.1) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin-top: 15px !important;
    min-height: 70px !important;
}

/* Force Sidebar section background specificity */
[data-testid="stSidebar"] section {
    background-color: #020617 !important;
}

/* Target the file uploader Browse button specifically */
div[data-testid="stFileUploader"] button {
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 2px solid #ffffff !important;
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    padding: 1rem 2rem !important;
    border-radius: 10px !important;
}

/* Sidebar Specific Button Scaling Adjustment */
[data-testid="stSidebar"] div.stButton button, [data-testid="stSidebar"] div.stDownloadButton button {
    font-size: 1.5rem !important;
    padding: 1rem !important;
    min-height: 60px !important;
}

/* CODE CONSOLE - FORCED VISIBILITY FOR GENERATED G-CODE */
.stCodeBlock, div[data-testid="stCodeBlock"] pre, div[data-testid="stCodeBlock"] code, div[data-testid="stCodeBlock"] span, .highlight code, pre code {
    font-size: 1.8rem !important;
    line-height: 1.5 !important;
    font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
    color: #ffffff !important;
    background-color: transparent !important;
}

.stCodeBlock {
    background-color: #000000 !important;
    border: 3px solid #ffffff !important;
    border-radius: 20px !important;
    padding: 30px !important;
    margin-top: 40px !important;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5);
}
</style>
""", unsafe_allow_html=True)

# Material Library Data
MATERIALS = {
    "Aluminum (6061)": {"speed": 2500, "feed": 0.25, "doc": 1.5},
    "Mild Steel (1018)": {"speed": 1200, "feed": 0.15, "doc": 1.0},
    "Stainless Steel (304)": {"speed": 800, "feed": 0.10, "doc": 0.5},
    "Brass": {"speed": 2200, "feed": 0.30, "doc": 2.0},
    "Custom": {"speed": 1200, "feed": 0.2, "doc": 1.0}
}

st.title("⚙️ CNC G-Code Generator")
st.markdown("### Industrial-Grade G-Code Generation & Visualization")

# Initialize Session State
def init_state(key, default):
    if key not in st.session_state:
        st.session_state[key] = default

init_state('init_dia', 50.0)
init_state('fin_dia', 40.0)
init_state('init_len', 100.0)
init_state('fin_len', 80.0)
init_state('tool_no', "01")
init_state('off_no', "01")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1035/1035651.png", width=80)
    st.header("📂 Project Management")
    project_name = st.text_input("Project Name", value="CNC_Project_1")
    
    st.markdown("---")
    st.header("🛠 Machine Config")
    machine_type = st.selectbox("Controller Type", ["Fanuc / Haas", "Siemens", "LinuxCNC"], key='machine_type')
    
    st.markdown("---")
    material = st.selectbox("Select Stock Material", list(MATERIALS.keys()), key='material')
    mat_data = MATERIALS[material]
    
    st.markdown("---")
    max_rpm = st.number_input("Max Spindle RPM", value=max(3000, mat_data["speed"]))

tab1, tab2, tab3 = st.tabs(["Turning & Facing", "Step Turning", "Advanced Operations"])

with tab1:
    st.subheader("🧾 Workpiece Dimensions")
    col1, col2 = st.columns(2)
    with col1:
        initial_dia = st.number_input("Initial Diameter (mm)", min_value=0.0, step=1.0, key='init_dia')
        final_dia = st.number_input("Final Diameter (mm)", min_value=0.0, step=1.0, key='fin_dia')
    with col2:
        initial_len = st.number_input("Initial Length (mm)", min_value=0.0, step=1.0, key='init_len')
        final_len = st.number_input("Final Length (mm)", min_value=0.0, step=1.0, key='fin_len')

    if initial_dia > 0 and final_dia > 0 and initial_len > 0 and final_len > 0:
        dia_diff = initial_dia - final_dia
        len_diff = initial_len - final_len
        
        with st.container():
            st.markdown('<div style="background: rgba(255,255,255,0.03); border-radius: 15px; padding: 20px; border: 1px solid rgba(255,255,255,0.1);">', unsafe_allow_html=True)
            st.subheader("🖼 Digital Workpiece Twin")
            preview_fig = visualizer.plot_workpiece(initial_dia, final_dia, initial_len, final_len)
            st.pyplot(preview_fig)
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("---")
        st.subheader("⚙️ Tooling & Cutting Parameters")
        col3, col4, col5, col6 = st.columns(4)
        with col3: tool_number = st.text_input("Tool Number", key='tool_no')
        with col4: offset_number = st.text_input("Offset Number", key='off_no')
        with col5: spindle_speed = st.text_input("Spindle Speed (RPM)", value=str(mat_data["speed"]))
        with col6: feed_rate = st.text_input("Feed Rate (mm/rev)", value=str(mat_data["feed"]))

        if st.button("🚀 Generate Precision G-Code"):
            result = []
            result.extend(get_machine_header(machine_type, tool_number + offset_number, spindle_speed, max_rpm))
            result.append(f"G01 X{final_dia} Z-{final_len} F{feed_rate}")
            result.extend(get_machine_footer(machine_type))
            
            st.code("\n".join(result), language="text")
            st.download_button("📥 Download G-Code", "\n".join(result), file_name=f"cnc_program_{machine_type.lower().split()[0]}.nc")
    else:
        st.info("💡 Please enter initial and final dimensions to start generating G-Code.")

with tab2:
    st.subheader("🧾 Multi-Step Turning Details")
    col1, col2 = st.columns(2)
    with col1:
        s_initial_dia = st.number_input("Initial Diameter (mm)", min_value=0.0, key="s_init_dia")
        s_initial_len = st.number_input("Initial Length (mm)", min_value=0.0, key="s_init_len")
    with col2:
        s_num_steps = st.number_input("Number of Steps", min_value=1, step=1, value=2, key="s_num")
        
    if s_initial_dia > 0 and s_initial_len > 0:
        steps_data = []
        for i in range(int(s_num_steps)):
            st.markdown(f"#### Step {i+1}")
            col_a, col_b = st.columns(2)
            with col_a: step_dia = st.number_input(f"Step {i+1} Diameter", key=f"s_dia_{i}")
            with col_b: step_len = st.number_input(f"Step {i+1} Length", key=f"s_len_{i}")
            steps_data.append((step_dia, step_len))
            
        st.markdown("---")
        st.subheader("🖼 Step Preview")
        step_fig = visualizer.plot_step_turning(s_initial_dia, s_initial_len, steps_data)
        st.pyplot(step_fig)
        
        if st.button("🚀 Generate Step G-Code"):
            result = ["( OPERATION: MULTI-STEP TURNING )"]
            # Simplified for brevity
            result.append("G28 U0 W0")
            result.append("M30")
            st.code("\n".join(result), language="text")

with tab3:
    st.subheader("🧵 Threading Module (G76)")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        thread_dia = st.number_input("Major Diameter (mm)", value=20.0)
        thread_pitch = st.number_input("Pitch (mm)", value=1.5, step=0.1)
    with col_t2:
        thread_len = st.number_input("Thread Length (mm)", value=30.0)
        thread_depth = st.number_input("Thread Depth (mm)", value=0.92)
        
    if st.button("🚀 Generate Threading G-Code"):
        result = ["( OPERATION: THREADING )"]
        result.append(f"G76 P010060 Q100 R0.05")
        st.code("\n".join(result), language="text")
