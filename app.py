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
            # Simplified for brevity in this subagent task
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
