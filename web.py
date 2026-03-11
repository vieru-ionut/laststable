import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import urllib.request

# --- CONFIGURARE PAGINA ---
st.set_page_config(page_title="Calculator", layout="wide")
# --- 2. SECURITATE: VERIFICARE PAROLA ---
def check_password():
    """Returneaza True daca parola este corecta."""
    
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Afisam ecranul de logare
    st.title("🔐")
    parola_introdusa = st.text_input("Password", type="password")
    
    if st.button("Log In"):
        # Verificam parola din Secrets
        if parola_introdusa == st.secrets["password"]:
            st.session_state["password_correct"] = True
            st.rerun() # Reincarcam pagina ca sa dispara ecranul de logare
        else:
            st.error("😕 Incorrect- please try again")
    
    return False

# Daca parola NU este corecta, oprim executia AICI
if not check_password():
    st.stop()

# --- DE AICI INCOLO INCEPE CODUL APLICATIEI TALE ---
# (Definirea tabelelor, meniul lateral, modulele etc.)
# --- BAZA DE DATE TABELE (EXACT PDF TABLES) ---
def get_ds60364_data(insulation, loaded_cond):
    if insulation == "PVC":
        if loaded_cond == 2:
            return {
                "Cable Tray (E)":        [22, 30, 40, 51, 70, 94, 119, 148, 180, 232, 282, 328, 379, 434, 514, 593],
                "In Conduit (B2)":       [16.5, 23, 30, 38, 52, 69, 90, 111, 133, 168, 201, 232, 258, 294, 344, 394],
                "Pipe in Ground (D1)":   [22, 29, 37, 46, 60, 78, 99, 119, 140, 173, 204, 231, 261, 292, 336, 379],
                "Direct in Ground (D2)": [22, 28, 38, 48, 64, 83, 110, 132, 156, 192, 230, 261, 293, 331, 382, 427]
            }
        else: 
            return {
                "Cable Tray (E)":        [18.5, 25, 34, 43, 60, 80, 101, 126, 153, 196, 238, 276, 319, 364, 430, 497],
                "In Conduit (B2)":       [15, 20, 27, 34, 46, 62, 80, 99, 118, 149, 179, 206, 225, 255, 297, 339],
                "Pipe in Ground (D1)":   [18, 24, 30, 38, 50, 64, 82, 98, 116, 143, 169, 192, 217, 243, 280, 316],
                "Direct in Ground (D2)": [19, 24, 33, 41, 54, 70, 92, 110, 130, 162, 193, 220, 246, 278, 320, 359]
            }
    else: # XLPE
        if loaded_cond == 2:
            return {
                "Cable Tray (E)":        [26, 36, 49, 63, 86, 115, 149, 185, 225, 289, 352, 410, 473, 542, 641, 741],
                "In Conduit (B2)":       [22, 30, 40, 51, 69, 91, 119, 146, 175, 221, 265, 305, 334, 384, 459, 532],
                "Pipe in Ground (D1)":   [25, 33, 43, 53, 71, 91, 116, 139, 164, 203, 239, 271, 306, 343, 395, 446],
                "Direct in Ground (D2)": [27, 35, 46, 58, 77, 100, 129, 155, 183, 225, 270, 306, 343, 387, 448, 502]
            }
        else: 
            return {
                "Cable Tray (E)":        [23, 32, 42, 54, 75, 100, 127, 158, 192, 246, 298, 346, 399, 456, 538, 621],
                "In Conduit (B2)":       [19.5, 26, 35, 44, 60, 80, 105, 128, 154, 194, 233, 268, 300, 340, 398, 455],
                "Pipe in Ground (D1)":   [21, 28, 36, 44, 58, 75, 96, 115, 135, 167, 197, 223, 251, 281, 324, 365],
                "Direct in Ground (D2)": [23, 30, 39, 49, 65, 84, 107, 129, 153, 188, 226, 257, 287, 324, 375, 419]
            }

# --- MENIU LATERAL (SIDEBAR) ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)

st.sidebar.title("Calculator")
module = st.sidebar.radio("", [
    "1. Short Circuit", 
    "2. Cable Sizing", 
    "3. Voltage Drop & Dimensioning", 
    "4. Cable Capacity",
    "5. Parallel Cable Load",
    "6. Converter"
    
    
])

st.sidebar.markdown("---")
st.sidebar.caption("*Built and Maintained - Ionut Vieru*")
# ==========================================

# ==========================================
# MODULE 1: SHORT CIRCUIT
# ==========================================
if module == "1. Short Circuit":
    st.header("Short Circuit for Transformer")
    
    col1, col2 = st.columns(2)
    with col1:
        u_pri = st.number_input("U_pri [kV]", value=10.0)
        i_k_pri = st.text_input("I_k_pri [kA]", value="inf")
        s_r = st.number_input("S_r [kVA]", value=1600.0)
    with col2:
        u_n = st.number_input("U_n [V]", value=400.0)
        u_k = st.number_input("u_k [%]", value=6.0)
        
    if st.button("Calculate & Show Graph"):
        try:
            # Calculele tale matematice
            IrT = (s_r * 1000) / (np.sqrt(3) * u_n)
            Ikp_s = i_k_pri.lower()
            ZQ = 0 if Ikp_s in ['inf', 'infinity'] else (1.05 * u_n**2) / (np.sqrt(3) * u_pri * 1000 * float(Ikp_s) * 1000)
            ZT = (u_k / 100) * (u_n**2 / (s_r * 1000))
            RT = 0.1 * ZT
            XT = np.sqrt(ZT**2 - RT**2)
            Ikmax = (1.05 * u_n) / (np.sqrt(3) * (ZQ + ZT))
            # Calcul curent de scurtcircuit maxim secundar
            Ikmax = (1.05 * u_n) / (np.sqrt(3) * (ZQ + ZT))
            
            # --- NOU: Calcul I_peak (ip) ---
            # Factorul kappa (κ) depinde de raportul R/X sau X/R
            if XT > 0:
                kappa = 1.02 + 0.98 * np.exp(-3 * (RT / XT))
            else:
                kappa = 2.0  # Cazul pur reactiv
            
            ipeak = kappa * np.sqrt(2) * Ikmax
            # --- REZULTATE CU SCRIS MARE ---
            # Folosim culori contrastante: Albastru inchis pentru etichete, Verde pentru valori
            rezultat_html = f"""
            <div style="background-color: #eaf2f8; padding: 32px; border-radius: 10px; border-left: 5px solid #1a5276;">
                <div style="font-size: 32px; color: #1a5276; margin-bottom: 10px;">
                    <b>Nominal Current (IrT):</b> <span style="color: #1e8449;">{IrT:.1f} A</span>
                </div>
                <div style="font-size: 32px; color: #1a5276; margin-bottom: 10px;">
                    <b>I_k_max'':</b> <span style="color: #a93226;">{Ikmax/1000:.2f} kA</span>
                </div>
                <div style="font-size: 32px; color: #1a5276;">
                    <b>i_peak (ip):</b> <span style="color: #1e8449;">{ipeak/1000:.2f} kA</span>
                </div>
            </div>
            <br>
            """
            st.markdown(rezultat_html, unsafe_allow_html=True)
            
            # Parametrii undei
            t = np.linspace(0, 0.06, 1000)
            omega = 2 * np.pi * 50
            phi = np.arctan(XT/RT) if RT != 0 else np.pi/2
            tau = (XT/omega)/RT if RT != 0 else 0.045
            i_tot = np.sqrt(2) * Ikmax * (np.sin(omega*t - phi) + np.sin(phi) * np.exp(-t/tau))
            
           # 1. Mărim dimensiunea la (5, 3) pentru claritate, dar controlăm afișarea
            # Adăugăm dpi=300 pentru o rezoluție foarte clară (High Definition)
            fig, ax = plt.subplots(figsize=(5, 3), dpi=300) 
            
            ax.plot(t*1000, i_tot/1000, 'r', linewidth=1.5)
            ax.axhline(0, color='black', lw=0.8)
            
            # 2. Folosim dimensiuni de font rezonabile (nu mai punem 5 sau 6)
            ax.set_title("Short Circuit Current [kA]", fontsize=10, fontweight='bold')
            ax.set_xlabel("Time [ms]", fontsize=9)
            ax.set_ylabel("Current [kA]", fontsize=9)
            
            ax.tick_params(axis='both', labelsize=8)
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # 3. Această linie elimină marginile albe inutile
            plt.tight_layout()

            # 4. Afișăm în Streamlit cu lățime controlată (ca să nu ocupe tot ecranul)
            st.pyplot(fig, use_container_width=False)
        # AICI E CHEIA: Trebuie să fie aliniat cu "try" de mai sus!
        except Exception as e:
            st.error(f"Eroare la calcul: {e}")

# ==========================================
# MODULE 2: CABLE SIZING
# ==========================================
elif module == "2. Cable Sizing":
    st.header("Cable Sizing")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        ib = st.number_input("Load Current Ib [A]:", value=160.0)
        temp = st.number_input("Ambient Temp [°C]:", value=30.0)
        k2 = st.number_input("Grouping Factor (K2):", value=1.0)
        n = st.number_input("Parallel Cables (n):", value=1, min_value=1)
    
    with col2:
        v_mat = st.radio("Material", ["Cu", "Al"])
        v_ins = st.radio("Insulation", ["XLPE", "PVC"])
        
    with col3:
        v_cond = st.radio("Loaded Conductors", [3, 2])
        v_neu = st.checkbox("Loaded Neutral (K3 = 0.86)", value=False)
        
    if st.button("Calculate", type="primary"):
        try:
            # --- CALCUL FACTOR DE TEMPERATURA K1 ---
            k1 = 1.0
            if v_ins == "XLPE":
                if temp <= 30: k1 = 1.0
                elif temp <= 35: k1 = 0.96
                elif temp <= 40: k1 = 0.91
                elif temp <= 45: k1 = 0.87
                elif temp <= 50: k1 = 0.82
                elif temp <= 55: k1 = 0.76
                elif temp <= 60: k1 = 0.71
                elif temp <= 65: k1 = 0.65
                elif temp <= 70: k1 = 0.58
                else: k1 = 0.50
            else: # PVC
                if temp <= 30: k1 = 1.0
                elif temp <= 35: k1 = 0.94
                elif temp <= 40: k1 = 0.87
                elif temp <= 45: k1 = 0.79
                elif temp <= 50: k1 = 0.71
                elif temp <= 55: k1 = 0.61
                elif temp <= 60: k1 = 0.50
                else: k1 = 0.40

            k3 = 0.86 if v_neu else 1.0
            k_total = k1 * k2 * k3
            
            # --- AFISARE FACTORI (SCRIS MARE) ---
            st.info(f"### Temperature correction (k1): **{k1:.2f}** | Total correction (K): **{k_total:.3f}**")
            
            # ... restul calculelor tale cu target, load_per_cable etc.
            
            # Curentul tinta per cablu
            target = ib / (k_total * n)
            mat_faktor = 1.0 if v_mat == "Cu" else 0.78
            load_per_cable = ib / n
            
            sect = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]
            metoder = get_ds60364_data(v_ins, v_cond)
            
            out = f"<div style='font-size: 20px;'><b>Required Iz per cable:</b> > {target:.1f} A | <b>Total Factor (K):</b> {k_total:.3f}</div><br><hr><br>"
            
            # Bucla de cautare a sectiunilor
            for m, vals in metoder.items():
                # --- REPARARE LINIA 174: Paranteza inchisa corect ---
                idx = next((i for i, v in enumerate(vals) if v * mat_faktor >= target), -1)
                
                if idx != -1 and idx < len(sect):
                    chosen_sect = sect[idx]
                    base_iz = vals[idx] * mat_faktor
                    actual_capacity = base_iz * k_total
                    procent = (load_per_cable / actual_capacity) * 100
                    
                    # --- Stiluri Culori ---
                    c_m = "color: #1a5276;" # Albastru
                    c_s = "color: #d35400;" # Portocaliu
                    c_p = "color: #1e8449;" # Verde
                    
                    out += (
                        f"<div style='font-size: 30px; line-height: 1.6;'>"
                        f"<span style='{c_m} font-weight: bold;'>{m:<20}:</span> "
                        f"<span style='{c_s} font-weight: bold; background-color: #fdf2e9; padding: 2px 8px; border-radius: 5px;'>{chosen_sect:>4} mm²</span> "
                        f"<span style='{c_p} font-weight: bold;'> [Cap: {actual_capacity:>5.1f}A | {procent:.1f}%]</span>"
                        f"</div><br>"
                    )
                else:
                    out += f"<div style='font-size: 30px; color: #a93226; font-weight: bold;'>{m:<20}: N/A (>300 mm²)</div><br>"
            
            # Afisare Rezultate
            st.markdown(out, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Eroare la calcul: {e}")
# ==========================================
# MODULE 3: VOLTAGE DROP & DIMENSIONING
# ==========================================
elif module == "3. Voltage Drop & Dimensioning":
    st.header("Voltage Drop Calculator")
    
    col1, col2 = st.columns(2)
    with col1:
        e_len = st.number_input("Length [m]:", value=50.0)
        e_curr = st.number_input("Current Ib [A]:", value=16.0)
        e_sect = st.number_input("Test Section [mm²]:", value=2.5)
    
    with col2:
        v_mat = st.radio("Material", ["Cu", "Al"])
        v_sys = st.selectbox("System Voltage [V]", [12, 24, 230, 400], index=1)
        # --- NOU: Selecție Tip Curent ---
        v_type = st.radio("Current Type", ["AC", "DC"], horizontal=True)
        
    if st.button("Calculate Voltage Drop", type="primary"):
        try:
            rho = 0.0225 if v_mat == "Cu" else 0.036
            
            # --- LOGICĂ ACTUALIZATĂ ---
            if v_type == "DC":
                factor = 2 # Dus-întors
                cos_phi = 1.0 # Nu există defazaj în DC
            else: # AC
                # Pentru AC, verificăm dacă e Monofazat sau Trifazat
                factor = np.sqrt(3) if v_sys == 400 else 2
                cos_phi = 0.85 # Factor standard pentru motoare/sarcini inductive

            dV_volts = (factor * e_len * e_curr * rho * cos_phi) / e_sect
            du_percent = (dV_volts / v_sys) * 100

            def get_required_section(target_percent):
                target_volts = (target_percent / 100.0) * v_sys
                return (factor * e_len * e_curr * rho * cos_phi) / target_volts

            s_req_3 = get_required_section(3)
            s_req_5 = get_required_section(5)
            s_req_8 = get_required_section(8)

            std_cables = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]
            
            def match_standard(req_val):
                for cab in std_cables:
                    if cab >= req_val:
                        return f"{cab} mm²"
                return ">300 mm²"

            out =  f"### ANALYSIS FOR {e_sect} mm² ({v_mat}) AT {v_sys}V\n"
            out += f"**Voltage Drop (dU):** `{du_percent:.2f} %`  ({dV_volts:.2f} V)\n\n"
            
            out += f"### RECOMMENDED SECTIONS FOR MAX LIMITS\n"
            out += f"- **Limit 3% :** Req. {s_req_3:>6.2f} mm² -> Use: **{match_standard(s_req_3)}**\n"
            out += f"- **Limit 5% :** Req. {s_req_5:>6.2f} mm² -> Use: **{match_standard(s_req_5)}**\n"
            out += f"- **Limit 8% :** Req. {s_req_8:>6.2f} mm² -> Use: **{match_standard(s_req_8)}**\n"
            
            st.success(out)

        except Exception as e:
            st.error(f"Please check your inputs. Error: {e}")

# ==========================================
# MODULE 4: CABLE CAPACITY
# ==========================================
elif module == "4. Cable Capacity":
    st.header("Cable Capacity")
    
    sections_list = [1.5, 2.5, 4.0, 6.0, 10.0, 16.0, 25.0, 35.0, 50.0, 70.0, 95.0, 120.0, 150.0, 185.0, 240.0, 300.0]
    
    col1, col2 = st.columns(2)
    with col1:
        selected_section = st.selectbox("Cross-Section [mm²]:", sections_list, index=5)
        v_mat = st.radio("Material", ["Cu", "Al"])
        
    with col2:
        v_ins = st.radio("Insulation", ["XLPE", "PVC"])
        v_cond = st.radio("Loaded Conductors", [3, 2])
        
    if st.button("Get Max Capacity", type="primary"):
        try:
            idx = sections_list.index(selected_section)

            metoder = get_ds60364_data(v_ins, v_cond)
            mat_faktor = 1.0 if v_mat == "Cu" else 0.78
            
            warning = ""
            if v_mat == "Al" and selected_section < 16:
                warning = "\n*(Note: Al conductors < 16mm² are rarely allowed)*\n"

            # --- CODUL TAU MODIFICAT PENTRU CULOARE SI BOLD ---
            out = f"### Max Capacity (Iz) | {selected_section} mm² {v_mat} | {v_ins} | {v_cond}-Cond\n"
            out += warning + "\n"
            out += "--- \n"
            
            for m, vals in metoder.items():
                # 1. Calculăm valoarea finală
                capacitate_finala = vals[idx] * mat_faktor
                
                # 2. Cream textul cu formatare HTML (Culoare albastră și Bold)
                # Am pus culoarea 'blue' si fontul 'bold' folosind CSS.
                formatted_text = f"<span style='color: blue; font-weight: bold;'>{m:<24}:</span> <span style='color: green; font-weight: bold;'>{capacitate_finala:.1f} A</span>"
                
                # 3. Adăugăm în output cu un font mai mare (ex: 20px)
                out += f"<span style='font-size: 20px;'>{formatted_text}</span><br><br>"

            # --- FOARTE IMPORTANT: Schimbă st.info(out) cu st.markdown ---
            # Aceasta linie permite afișarea culorilor HTML pe care le-am pus.
            st.markdown(out, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Could not fetch capacity. Error: {e}")


# ==========================================
# MODULE 5: PARALLEL CABLE LOAD
# ==========================================
elif module == "5. Parallel Cable Load":
    st.header("Parallel Load Distribution & Safety Check")
    st.info("")

    col1, col2 = st.columns(2)
    with col1:
        i_total = st.number_input("Total Load Current (I_total) [A]:", value=400.0)
        num_cables = st.number_input("Number of cables per phase:", min_value=2, max_value=6, value=2)
    with col2:
        v_ins = st.radio("Insulation (for capacity check)", ["XLPE", "PVC"], horizontal=True)
        v_meth = st.selectbox("Installation Method", ["Cable Tray (E)", "In Conduit (B2)", "Direct in Ground (D2)"])

    st.subheader("Cable Specifications:")
    cable_inputs = []
    cols = st.columns(num_cables)
    
    # Secțiuni disponibile în tabelul tău
    std_sect = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]

    for i in range(num_cables):
        with cols[i]:
            st.markdown(f"**Cable {i+1}**")
            L = st.number_input(f"Length [m]", value=10.0, key=f"L_p_{i}")
            S = st.selectbox(f"Sect [mm²]", std_sect, index=10, key=f"S_p_{i}") # Default 95mm2
            cable_inputs.append({"L": L, "S": S})

    if st.button("Calculate & Check Safety", type="primary"):
        try:
            # 1. Calculăm Conductanța G = S / L pentru fiecare
            total_G = sum(c["S"] / c["L"] for c in cable_inputs)
            
            # 2. Luăm datele de capacitate din tabel (presupunem 3 cond. încărcați)
            metoder_data = get_ds60364_data(v_ins, 3)
            tab_vals = metoder_data[v_meth]

            out = "### Analysis Results\n---\n"
            c_black = "color: #000000; font-weight: bold;"
            c_green = "color: #1e8449; font-weight: bold;"
            c_red   = "color: #a93226; font-weight: bold;"

            for i, c in enumerate(cable_inputs):
                # Distribuția curentului (Legea lui Ohm)
                i_cable = i_total * ((c["S"] / c["L"]) / total_G)
                
                # Căutăm capacitatea maximă (Iz) în tabel pentru secțiunea aleasă
                idx_s = std_sect.index(c["S"])
                max_iz = tab_vals[idx_s]
                
                # Procentul de încărcare real
                procent = (i_cable / max_iz) * 100
                color_res = c_red if procent > 100 else c_green

                out += (
                    f"<div style='font-size: 28px; line-height: 1.5;'>"
                    f"<span style='{c_black}'>Cable {i+1} ({c['S']}mm², {c['L']}m):</span><br>"
                    f"Load: <span style='{color_res}'>{i_cable:.1f} A</span> | "
                    f"Max load: <b>{max_iz:.1f} A</b> | "
                    f"Load in %: <span style='{color_res}'>{procent:.1f}%</span>"
                    f"</div><br>"
                )
            
            st.markdown(out, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error: {e}")

# ==========================================
# MODULE 6: CONVERTER (kVA / kW / A)
# ==========================================
elif module == "6. Converter":
    st.header("⚡ Power & Current Converter")
    st.info("Enter a value in any field and press the button for automatic conversion.")

    # System settings for calculation
    col_sys1, col_sys2 = st.columns(2)
    with col_sys1:
        v_sys = st.selectbox("System Voltage [V]", [12, 24, 230, 400, 690], index=3)
    with col_sys2:
        cos_phi = st.number_input("Power Factor (cos φ)", value=0.85, step=0.05)

    # Session state initialization
    if 'val_kva' not in st.session_state: st.session_state.val_kva = 0.0
    if 'val_kw' not in st.session_state: st.session_state.val_kw = 0.0
    if 'val_amp' not in st.session_state: st.session_state.val_amp = 0.0

    col1, col2, col3 = st.columns(3)
    
    with col1:
        kva_in = st.number_input("Apparent Power [kVA]", value=st.session_state.val_kva, key="kva_input")
    with col2:
        kw_in = st.number_input("Active Power [kW]", value=st.session_state.val_kw, key="kw_input")
    with col3:
        amp_in = st.number_input("Current [A]", value=st.session_state.val_amp, key="amp_input")

    if st.button("🔄 Transform & Sync", type="primary"):
        # Detection logic for phase factor
        factor_faza = np.sqrt(3) if v_sys == 400 else 1.0


        
        # 1. If kVA changed
        if kva_in != st.session_state.val_kva:
            st.session_state.val_kva = kva_in
            st.session_state.val_kw = kva_in * cos_phi
            st.session_state.val_amp = (kva_in * 1000) / (factor_faza * v_sys)
            
        # 2. If kW changed
        elif kw_in != st.session_state.val_kw:
            st.session_state.val_kw = kw_in
            st.session_state.val_kva = kw_in / cos_phi if cos_phi > 0 else 0
            st.session_state.val_amp = (st.session_state.val_kva * 1000) / (factor_faza * v_sys)
            
        # 3. If Amperage changed
        elif amp_in != st.session_state.val_amp:
            st.session_state.val_amp = amp_in
            st.session_state.val_kva = (factor_faza * v_sys * amp_in) / 1000
            st.session_state.val_kw = st.session_state.val_kva * cos_phi
            
        st.rerun()

    # Giant result display in English
    out_conv = f"""
    <div style="background-color: #f0f4f8; padding: 20px; border-radius: 10px; border-left: 5px solid #1a5276;">
        <div style="font-size: 24px; color: #1a5276;"><b>Synchronized Results ({v_sys}V):</b></div>
        <hr>
        <div style="font-size: 30px;">💎 <b>{st.session_state.val_kva:.2f} kVA</b></div>
        <div style="font-size: 30px;">🚀 <b>{st.session_state.val_kw:.2f} kW</b></div>
        <div style="font-size: 30px;">🔥 <span style="color: #a93226;"><b>{st.session_state.val_amp:.1f} A</b></span></div>
    </div>
    """
    st.markdown(out_conv, unsafe_allow_html=True)



# ==========================================
# SUBSOL PAGINA PRINCIPALA (CONTOR INTELIGENT)
# ==========================================
st.markdown("---")

# 1. Verificam daca am descarcat deja contorul in aceasta sesiune
if 'badge_svg' not in st.session_state:
    try:
        # Facem request-ul catre server o singura data
        url = "https://api.visitorbadge.io/api/visitors?path=beregner.streamlit.app&label=VISITS&labelColor=%23000000&countColor=%231e8449"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            # Salvam imaginea SVG direct ca text in memoria Streamlit
            st.session_state.badge_svg = response.read().decode('utf-8')
    except Exception as e:
        # Daca pica serverul lor, nu stricam aplicatia noastra
        st.session_state.badge_svg = ""

# 2. Afisam contorul din memorie, indiferent de cate ori dam "Calculate"
if st.session_state.badge_svg:
    st.markdown(
        f"""
        <style>
        .footer-contor {{
            position: fixed;
            bottom: 15px;
            left: 0;
            width: 100%;
            text-align: center;
            z-index: 100;
        }}
        </style>
        <div class="footer-contor">
            {st.session_state.badge_svg}
        </div>
        """,
        unsafe_allow_html=True
    )
