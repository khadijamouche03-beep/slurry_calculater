"""
Slurry Transport Hydraulic Calculator
======================================
A complete multi-step hydraulic engineering tool for slurry pipeline design.
Organized into 6 sequential steps with persistent session state.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import math
import pandas as pd
from scipy.interpolate import PchipInterpolator
from plotly.subplots import make_subplots




# ─────────────────────────────────────────────
#  PAGE CONFIG & GLOBAL THEME
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Slurry Transport Hydraulic Calculator",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DARK_BG     = "#0D1117"
PANEL_BG    = "#161B22"
BORDER_COL  = "#30363D"
ACCENT      = "#00C8FF"
ACCENT2     = "#FF6B35"
SUCCESS     = "#3FB950"
WARNING     = "#D29922"
TEXT_MAIN   = "#E6EDF3"
TEXT_MUTED  = "#8B949E"
GRID_COL    = "#21262D"

CUSTOM_CSS = f"""
<style>
  /* ── Root & body ── */
  :root {{
    --accent:    {ACCENT};
    --accent2:   {ACCENT2};
    --success:   {SUCCESS};
    --warning:   {WARNING};
    --bg:        {DARK_BG};
    --panel:     {PANEL_BG};
    --border:    {BORDER_COL};
    --text:      {TEXT_MAIN};
    --muted:     {TEXT_MUTED};
  }}
  html, body, [class*="css"] {{
    background-color: {DARK_BG} !important;
    color: {TEXT_MAIN} !important;
    font-family: 'IBM Plex Mono', 'Courier New', monospace;
  }}
  /* ── Sidebar ── */
  section[data-testid="stSidebar"] > div {{
    background: {PANEL_BG} !important;
    border-right: 1px solid {BORDER_COL};
  }}
  /* ── Main header ── */
  .main-header {{
    background: linear-gradient(135deg, {PANEL_BG} 0%, #1C2333 100%);
    border: 1px solid {BORDER_COL};
    border-left: 4px solid {ACCENT};
    border-radius: 8px;
    padding: 20px 28px;
    margin-bottom: 24px;
  }}
  .main-header h1 {{
    color: {ACCENT};
    font-size: 1.7rem;
    letter-spacing: 2px;
    margin: 0;
    text-transform: uppercase;
  }}
  .main-header p {{
    color: {TEXT_MUTED};
    font-size: 0.78rem;
    margin: 4px 0 0 0;
    letter-spacing: 1px;
  }}
  /* ── Step badge ── */
  .step-badge {{
    display: inline-block;
    background: linear-gradient(90deg, {ACCENT}22, transparent);
    border: 1px solid {ACCENT}66;
    border-radius: 4px;
    padding: 4px 12px;
    color: {ACCENT};
    font-size: 0.72rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 12px;
  }}
  /* ── KPI cards ── */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin: 16px 0;
  }}
  .kpi-card {{
    background: {PANEL_BG};
    border: 1px solid {BORDER_COL};
    border-top: 3px solid {ACCENT};
    border-radius: 6px;
    padding: 14px 16px;
    text-align: center;
  }}
  .kpi-card.accent2  {{ border-top-color: {ACCENT2}; }}
  .kpi-card.success  {{ border-top-color: {SUCCESS}; }}
  .kpi-card.warning  {{ border-top-color: {WARNING}; }}
  .kpi-val  {{ font-size: 1.5rem; font-weight: 700; color: {ACCENT}; }}
  .kpi-val.accent2 {{ color: {ACCENT2}; }}
  .kpi-val.success {{ color: {SUCCESS}; }}
  .kpi-val.warning {{ color: {WARNING}; }}
  .kpi-unit {{ font-size: 0.65rem; color: {TEXT_MUTED}; letter-spacing: 1px; }}
  .kpi-lbl  {{ font-size: 0.70rem; color: {TEXT_MUTED}; margin-top: 4px; letter-spacing: 1px; text-transform: uppercase; }}
  /* ── Section panels ── */
  .section-panel {{
    background: {PANEL_BG};
    border: 1px solid {BORDER_COL};
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 16px;
  }}
  .section-title {{
    color: {ACCENT};
    font-size: 0.8rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    border-bottom: 1px solid {BORDER_COL};
    padding-bottom: 8px;
    margin-bottom: 14px;
  }}
  /* ── Formula box ── */
  .formula-box {{
    background: {DARK_BG};
    border: 1px dashed {BORDER_COL};
    border-left: 3px solid {WARNING};
    border-radius: 4px;
    padding: 12px 16px;
    margin: 10px 0;
    font-size: 0.78rem;
    color: {WARNING};
    font-family: 'IBM Plex Mono', monospace;
  }}
  /* ── Result row ── */
  .result-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 7px 0;
    border-bottom: 1px solid {GRID_COL};
    font-size: 0.82rem;
  }}
  .result-row:last-child {{ border-bottom: none; }}
  .result-label {{ color: {TEXT_MUTED}; }}
  .result-value {{ color: {TEXT_MAIN}; font-weight: 600; }}

  /* ── Nav buttons ── */
  .stButton > button {{
    background: linear-gradient(135deg, {ACCENT}22, {ACCENT}11) !important;
    border: 1px solid {ACCENT}55 !important;
    color: {ACCENT} !important;
    font-family: 'IBM Plex Mono', monospace !important;
    letter-spacing: 1px !important;
    font-size: 0.78rem !important;
    border-radius: 4px !important;
    transition: all 0.2s !important;
  }}
  .stButton > button:hover {{
    background: {ACCENT}33 !important;
    border-color: {ACCENT} !important;
    box-shadow: 0 0 12px {ACCENT}44 !important;
  }}
  /* ── Inputs ── */
  .stNumberInput > div > div > input,
  .stSelectbox > div > div,
  .stTextInput > div > div > input {{
    background: {DARK_BG} !important;
    border: 1px solid {BORDER_COL} !important;
    color: {TEXT_MAIN} !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    border-radius: 4px !important;
  }}
  .stNumberInput > div > div > input:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 2px {ACCENT}33 !important;
  }}
  /* ── Expander ── */
  .streamlit-expanderHeader {{
    background: {PANEL_BG} !important;
    border: 1px solid {BORDER_COL} !important;
    border-radius: 4px !important;
    color: {TEXT_MAIN} !important;
    font-size: 0.82rem !important;
  }}
  .streamlit-expanderContent {{
    background: {DARK_BG} !important;
    border: 1px solid {BORDER_COL} !important;
    border-top: none !important;
  }}
  /* ── Progress bar ── */
  .progress-bar-outer {{
    background: {GRID_COL};
    border-radius: 4px;
    height: 6px;
    margin: 8px 0 16px 0;
  }}
  .progress-bar-inner {{
    background: linear-gradient(90deg, {ACCENT}, {ACCENT2});
    border-radius: 4px;
    height: 6px;
    transition: width 0.4s ease;
  }}
  /* ── Status pill ── */
  .status-pill {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.68rem;
    letter-spacing: 1px;
    text-transform: uppercase;
  }}
  .status-ok  {{ background: {SUCCESS}22; border:1px solid {SUCCESS}55; color:{SUCCESS}; }}
  .status-warn{{ background: {WARNING}22; border:1px solid {WARNING}55; color:{WARNING}; }}
  .status-err {{ background: {ACCENT2}22; border:1px solid {ACCENT2}55; color:{ACCENT2}; }}
  /* ── Sidebar nav item ── */
  .nav-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-radius: 4px;
    margin: 3px 0;
    cursor: pointer;
    font-size: 0.78rem;
    letter-spacing: 0.5px;
    border: 1px solid transparent;
    transition: all 0.15s;
  }}
  .nav-item.active {{
    background: {ACCENT}18;
    border-color: {ACCENT}44;
    color: {ACCENT};
  }}
  .nav-item.done {{
    background: {SUCCESS}10;
    border-color: {SUCCESS}33;
    color: {SUCCESS};
  }}
  .nav-item.inactive {{
    color: {TEXT_MUTED};
  }}
  /* ── Divider ── */
  hr {{ border-color: {BORDER_COL} !important; }}
  /* ── Label ── */
  label {{ color: {TEXT_MUTED} !important; font-size: 0.78rem !important; letter-spacing: 0.5px !important; }}
</style>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;600;700&display=swap" rel="stylesheet">
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SESSION STATE INITIALISATION
# ─────────────────────────────────────────────
def init_session():
    defaults = {
        "current_step": 1,
        "step1_done": False,
        "step2_done": False,
        "step3_done": False,
        "step4_done": False,
        "step5_done": False,
        "step6_done": False,
        
        # --- Step 1: Slurry Properties (Valeurs par défaut cohérentes) ---
        "rho_s": 2330.0,    # Densité solide
        "mu_s": 0.0014,
        "rho_l": 1000.0,    # Densité liquide (eau)
        "Cw": 0.25,         # Concentration massique (25%)
        "mu_l": 0.001,      # Viscosité eau (1 mPa.s)
        "d50": 36.3e-6,     # Taille particule (36 microns)
        
        # --- Step 2: Hydraulic Parameters ---
        "pipe_length": 3887.0,
        "Q": 250.0,         # Changé 0.0 -> 350.0 (Débit par défaut pour éviter le crash)
        "Vm": 2.5,          # Vitesse moyenne par défaut
        "D": 0.2032,        # Diamètre par défaut (ex: 8 inches)
        
        # --- Variables de calcul (On les initialise à des valeurs minimes pour éviter div/0) ---
        "rho_m": 1166.5,
        "mu_m": 0.0014,
        "Cv": 0.125,        # Concentration volumique
       
        
        # --- Step 3 & 4 Results ---
        "pc_m": 0.001,      # Éviter 0 absolu
        "pc_mf": 0.001,
        "Cvf_final": 0.1,
        "fi_total": 0.0,
        "h_m": 0.0,
        
        # --- Step 5: Topology ---
        "topo_data": None    # Pour stocker le profil topographique
    }
    
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# N'oubliez pas d'appeler la fonction
init_session()

def slurry_density(rho_s, rho_l, Cw):
    """Mixture density by volume concentration."""
    return 1 / ((Cw / rho_s) + ((1 - Cw) / rho_l))

def concentration(Cw, rho_m, rho_s):
    return Cw * rho_m / rho_s

def slurry_dynamic_viscosity(mu_l, Cv):
    """
    Thomas (1965) effective slurry viscosity.
    mu_m = mu_l * (1 + 2.5*Cv + 10.05*Cv^2 + 0.00273*exp(16.6*Cv))
    # TODO: replace with project-specific rheological model
    """
    return mu_l * (1 + 2.5*Cv + 10.05*Cv**2 + 0.00273*math.exp(16.6*Cv))


#Critical Velocity & Diameter
def calculate_critical_velocity_and_diameter(Q, d50, rho_s, rho_l, rho_m, mu_m, Cv, mu_s):
    """
    Arbitrage automatique entre MTI, Durand et Wilson pour trouver 
    le diamètre optimal D et la vitesse critique Vc.
    """
    g = 9.81
    Ss = rho_s / rho_l
    d_50 = d50 * 1000
    diam_list = np.linspace(0.2, 2, 40).tolist() # Plage de diamètres à tester
    
    V_crit, D_final, Vm, model_used = 0.0, 0.0, 0.0, "Solution non trouvée"
    res_Du, res_W = None, None

    # 1. CHOIX DU MODÈLE RECOMMANDÉ
    recommended_model = "MTI" if 63e-6 <= d50 <= 16e-3 else "Auto"

    if recommended_model == "MTI":
        model_used = "MTI"
        list_D = []
        list_Q_crit = []
        list_V= []
        for d in diam_list:
            v = 1.7 * (5-(1/math.sqrt(d_50))) * math.sqrt(d)*(Cv/(Cv+0.1)**(1/6)) * math.sqrt(abs(Ss-1)/(1.65))
            q = math.pi * (d**2) * v * 3600/ 4
            list_V.append(v)
            list_Q_crit.append(q)
            list_D.append(d)
           
        for i in range(len(list_Q_crit)):
            if list_Q_crit[i] > Q :
                V_crit, D_final, model_used = list_V[i-1], diam_list[i-1], "MTI"
                break
           
           
    else:
        # 2. LOGIQUE DURAND
        Ar = 4 * g * d_50**3 * rho_m * abs(rho_s - rho_m)/(3 * mu_m**2)
        def get_Fl(Ar):
            if Ar > 86000: return  1.35 / math.sqrt(2)
            elif 2690 < Ar < 86000: return (2.35 - 0.088 * math.log(Ar)) / math.sqrt(2)
            elif 125 < Ar < 2690: return (1.27 + 0.049 * math.log(Ar)) / math.sqrt(2)
            else: return None
            
        
        Fl = get_Fl(Ar)
        res_Du = None
        list_D_Du = []
        list_Q_crit_Du = []
        list_V_Du= []

        for d in diam_list:

            v_Du = Fl * math.sqrt(2 * g * d * (rho_s - rho_m)/rho_m)
            q_Du = math.pi * (d**2) * v_Du * 3600 / 4
            list_V_Du.append(v_Du)
            list_Q_crit_Du.append(q_Du)
            list_D_Du.append(d)
           
        for i in range(len(list_Q_crit_Du)):
            if list_Q_crit_Du[i] > Q :
                res_Du = (list_V_Du[i-1] , list_D_Du[i-1])
                break

        # 3. LOGIQUE WILSON     
        res_W = None
        Cr, Sl = Cv/0.60, 1
        list_D_W = []
        list_Q_crit_W = []
        list_V_W= []
        for d in diam_list:
            V_sm = 8.8 * (mu_s *(Ss-Sl)/0.66)**0.55 *(d**0.7) *(d_50**1.75) / (d_50**2 + 0.11*(d)**0.7)
            Crm = 0.16*(d**0.40)*(d_50**(-0.84))*((Ss-Sl)/1.65)**(-0.17)
            C_r = max(min(Crm, 0.99), 0.01)
            a = math.log(0.333)/math.log(C_r)
            if Crm <= 0.33: v_W = V_sm * 6.75 * (Cr**a)*(1-Cr**a)**2
            else:
                b = math.log(0.666)/math.log(1-C_r)
                v_W = V_sm * 6.75 * (1-Cr)**(2*b)*(1-(1-Cr)**b)

            
            q_W = math.pi*(d**2)*v_W * 3600 / 4
            list_V_W.append(v_W)
            list_Q_crit_W.append(q_W)
            list_D_W.append(d)

        for i in range(len(list_Q_crit_W)):
            if list_Q_crit_W[i] > Q :
                res_W = (list_V_W[i-1] , list_D_W[i-1])
                break


        # COMPARISON FINALE DURAND vs WILSON
        if res_Du and res_W:
            if res_W[0] > res_Du[0]: 
                V_crit, D_final, model_used = res_W[0], res_W[1], "Wilson"
            else: 
                V_crit, D_final, model_used = res_Du[0], res_Du[1], "Durand"
        elif res_Du: 
            V_crit, D_final, model_used = res_Du[0], res_Du[1], "Durand"
        # ✅ SUPPRIMÉ: elif res_Du dupliqué
        elif res_W: 
            V_crit, D_final, model_used = res_W[0], res_W[1], "Wilson"

    if D_final > 0:
        Vm = 4 * Q / (math.pi * (D_final**2) * 3600)
    return V_crit, D_final, Vm, model_used

def reynolds_number(rho_m, Vm, D_pipe, mu_m):
    """Re_m = ρVD/μ"""
    return (rho_m * Vm * D_pipe) / mu_m

def pipe_area(D):
    return math.pi * D**2 / 4


def calculate_wasp_losses(D_pipe, Vm, rho_l, rho_s, mu_l, Cv, di, mi, k_rug, p_shape, p_volume, Cv_max, mineral_choice):
    """
    Moteur de calcul WASP (Wasp, 1963) pour les pertes de charge hydrauliques.
    Calcul de la portion véhiculante (fines) et sédimentaire (settling).
    """
    ki_vol_dict = {
                "Sand": 0.26,
                "Sillimanite, Bituminous coal": 0.23,
                "Blast furnace slag": 0.19,
                "Limestone, Talc, Plumbago": 0.16,
                "Gypsum": 0.13,
                "Flake graphite": 0.023,
                "Mica": 0.003,
                "Other (Manual input)": None
            }
    g = 9.81
    di_m = [d/1e6 for d in di]  # Conversion des microns en mètres pour la physique
    Cvf_trial = Cv
     

    # --- 1. Fonctions de base du véhicule ---
    def rho_mf_function(rho_l, rho_s, Cvf_trial):
        return rho_l + Cvf_trial * (rho_s - rho_l)

    def mu_mf_function(mu_l, Cvf_trial, Cv_max):
        # Évite division par zéro si cvf approche cm
        return mu_l * (1 - Cvf_trial / Cv_max)**-2.5

    def Re_mf_function(rho_mf, mu_mf, D_pipe, Vm):
        return (rho_mf * Vm * D_pipe) / mu_mf

    def fm_function(k_rug, D_pipe, Re_mf):
        """Calcule le facteur de friction f_m (Colebrook-White)."""
        return 0.33125 / (math.log10(k_rug/(3.7 * D_pipe)) + 5.74/(Re_mf**0.9))**2

    def beta_value_function(rho_l, Vm, D_pipe, mu_l):
        # Reynolds particule approché pour l'exposant Beta
        Re_p = (rho_l * Vm * D_pipe) / mu_l
        if Re_p <= 0.2: return 4.6
        elif 0.2 < Re_p <= 1: return 4.4 * (Re_p**-0.03)
        elif 1 < Re_p <= 500: return 4.4 * (Re_p**-0.1)
        else: return 2.4

    # --- 2. Vitesse de chute (Vti) ---
    list_Vti = []
    di_star_list = []

    if p_shape == "Sphérique":
        di_star_list = [((rho_l * (rho_s - rho_l) * g / (mu_l**2))**(1/3)) * d for d in di_m]
        for d_star in di_star_list:
            if d_star <= 4: v_star = 0.0556 * d_star**2
            elif 4 < d_star < 70: v_star = 0.21 * d_star
            else: v_star = 1.739 * d_star**0.5
            v_ti = v_star * ((mu_l * g * (rho_s - rho_l)) / (rho_l**2))**(1/3)
            list_Vti.append(v_ti)

    else:  # Non-sphérique
        di_star_list = [0.80 * d for d in di_m]
        for d_star in di_star_list:
            if d_star <= 4: v_stsi = 0.0556 * d_star**2
            elif 4 < d_star < 70: v_stsi = 0.21 * d_star
            else: v_stsi = 1.739 * d_star**0.5
            v_tsi = v_stsi * ((mu_l * g * (rho_s - rho_l)) / (rho_l**2))**(1/3)

            if mineral_choice == "Other (Manual input)":
                computed_k = p_volume / ((d_star)**3)
                ki_vol = computed_k
            else: 
                ki_vol = ki_vol_dict.get(mineral_choice)

            xi = math.exp(-0.55 + ki_vol - 0.0015*ki_vol + 0.03*(1000**(ki_vol-0.524)) + 
                          (-0.045 + 0.05*ki_vol**-0.6 - 0.0287*55000**(ki_vol-0.524)) / 
                          math.cosh(2.55 * math.log(d_star) - 1.114))
            list_Vti.append(xi * v_tsi)

    # --- 3. Vitesse entravée et Préparation Convergence ---
    beta_val = beta_value_function(rho_l, Vm, D_pipe, mu_l)
    list_Vti_prime = [v * (1 - Cvf_trial)**beta_val for v in list_Vti]
    
    van_karman = 0.4
    beta_const = 1 

    #b_i = log(C/Ca)_i
    def b_i_function(vt_prime_list, Vm, fm):
        f_sqrt = math.sqrt(fm )
        return [(-1.8 * vt) / (van_karman * beta_const * Vm * f_sqrt) for vt in vt_prime_list]

    def Cvf_function(bi_list, mi, Cv):
        # Cvf = Somme[(10^bi) * mi * Cv]
        return sum([(10**b) * m * Cv for b, m in zip(bi_list, mi)])

    # --- 4. Boucle de Convergence WASP ---
    max_iter = 100
    iter_count = 0
    diff = 1.0
    Cvf_current = Cv  # Initialisation trial
    
    while diff > 1e-5 and iter_count < max_iter:
        Cvf_old = Cvf_current
        
        rho_mf_iter = rho_mf_function(rho_l, rho_s, Cvf_old)
        mu_mf_iter = mu_mf_function(mu_l, Cvf_old, Cv_max)
        Re_mf_iter = Re_mf_function(rho_mf_iter, mu_mf_iter, D_pipe, Vm)
        fm_iter = fm_function(k_rug, D_pipe, Re_mf_iter)
        
        bi_list_iter = b_i_function(list_Vti_prime, Vm, fm_iter)
        Cvf_current = Cvf_function(bi_list_iter, mi, Cv)
        
        diff = abs(Cvf_current - Cvf_old)
        iter_count += 1

    # --- 5. Calcul des Pertes Finales ---
    # Propriétés finales après convergence
    rho_mf_fin = rho_mf_function(rho_l, rho_s, Cvf_current)
    mu_mf_fin = mu_mf_function(mu_l, Cvf_current, Cv_max)
    Re_mf_fin = Re_mf_function(rho_mf_fin, mu_mf_fin, D_pipe, Vm)
    fm_fin = fm_function(k_rug, D_pipe, Re_mf_fin)
    
    # Contribution Tranche Véhiculante (PC_mf)
    pc_mf = 2 * fm_fin * rho_mf_fin * Vm**2 / D_pipe

    # Contribution Portion Sédimentaire
    # Calcul de u_etoile
    rho_v = rho_l * (1 + (rho_s - rho_l) * Cvf_current / rho_l)
    mu_v = mu_l * (1 + 2.5*Cvf_current + 10.5*Cvf_current**2 + 0.00273*math.exp(16.6*Cvf_current))
    Re_v = (rho_v * Vm * D_pipe) / mu_v
    lambda_v = 1.325 / (math.log10(k_rug/(3.7*D_pipe)) + 5.75/(Re_v**0.9))**2
    u_et = math.sqrt(abs(lambda_v) / 8) * Vm

    # Alpha et Cvs_vi
    u_et_safe = u_et
    alpha_list = [math.exp((-4.14 * v)/(van_karman * beta_const * u_et_safe)) for v in list_Vti_prime]
    list_Cvs_vi = [10**((-14) * v / (van_karman * beta_const * u_et_safe)) for v in list_Vti_prime]
    list_Cvb_i = [cvs * (1/a - 1) for cvs, a in zip(list_Cvs_vi, alpha_list)]

    # Fi factor (Settling portion contribution)
    list_vtv_i = []
    nu_v = mu_v / rho_v
    rsdv = (rho_s - rho_l) / rho_l
    for dm in di_m:
        # Vtv_i formula
        val_vtv = (10 * nu_v* (math.sqrt(1 + rsdv * g * dm**3/(100 * nu_v)) - 1))/ dm
        list_vtv_i.append(val_vtv)

    list_inv_sqrt_cdi = [v / math.sqrt(g * dm) for v, dm in zip(list_vtv_i, di_m)]
    
    # fi = 82 * Cvbi * (g*D*(rho_s-rho_mf)*cd / Vm^2)^1.5
    list_fi = [82 * c * (g * D_pipe * ((rho_s - rho_mf_fin)/1000) * cd / (Vm**2))**1.5 for c, cd in zip(list_Cvb_i, list_inv_sqrt_cdi)]
    fi_total = sum(list_fi)

    # pc_l (Perte eau pure)
    Re_l = (rho_l * Vm * D_pipe) / mu_l
    fl = 0.33125 / (math.log10(k_rug/(3.7 * D_pipe)) + 5.74/(Re_l**0.9))**2
    pc_l = 2 * fl * rho_l * Vm**2 / D_pipe

    # pc_m finale (Pertes de charge mélange)
    pc_m = pc_mf + (fi_total * pc_l)

    return pc_m, pc_mf, fi_total, iter_count, Cvf_current

# ==========================================
#  SINGULAR LOSSES ENGINE & DATA
# ==========================================

# A. Les données (Base de données hardcodée)
KS_CONSTANTS = {
    "EB": 0.5, "RP": 0.0, "ES": 1.0, "EP": 0.5,
    "AQ": 1.0, "CB_av": 0.37, "CB_ar": 0.012,
}

# Correspond à l'onglet 'Ks_interpolation'
KS_INTERP_TABLES = {

    "VM": { # Vanne à membrane
        "x": [1, 0.75, 0.5, 0.25],
        "y": [2.3, 2.6, 4.3, 21]},

    "VS": { # Vanne à souppage
        "x": [1, 0.25],
        "y": [6.4, 9.5]},

    "VP": {# Vanne à pointeau
        "x": [1, 0.75, 0.5, 0.25],
        "y": [9, 13, 36, 112]},

    "VO": {#Vanne à opércule
        "x": [0.2, 0.4, 0.6, 0.8, 1],
        "y": [23, 4.5, 1, 0.4, 0]},

    "RBs": {#Robinet à boisseau sphérique
        "param_label": "Opening Angle (α)", # AJOUT D'UNE CLÉ ICI
        "unit": "°",                       # VÉRIFIEZ LA VIRGULE ICI
        "x": [10, 20, 30, 40],
        "y": [0.6, 2.6, 6.8, 24]}
}
KS_FORMULA_CONFIG = {
    "D1": {
        "label": "Débimètre à Venturi",
        "params": ["d", "D"], # Les noms des variables à demander
        "labels": ["Small Diameter d (m)", "Large Diameter D (m)"]},
    "C2": {
        "label": "Smooth Rounded Bend (Coude arrondie lisse)",
        "params": ["D", "R", "alpha"],
        "labels": ["Pipe Diameter D (m)", "Bending Radius R (m)", "Angle alpha (°)"]},
    "R1": {
        "label": "Rétrecissement de section",
        "params": ["s", "S", "theta"],
        "labels": ["Opening Width s (m)", "Total Width S (m)", "Angle theta (°)"]},

    "E1": {
        "label": "Sudden Expansion (Élargissement brusque)",
        "params": ["S1", "S2"],
        "labels": ["Entry section S1 [m²]", "Exit section S2 [m²]"]},
    "V1": {
        "label": "Butterfly Valve (Vanne papillon)",
        "params": ["alpha"],
        "labels": ["Opening angle alpha [°]"]},
    "C1": {
        "label": "Sharp Bend (Coude brusque)",
        "params": ["alpha"],
        "labels": ["Angle alpha [°]"]},
    "C3": {
        "label": "Rough Rounded Bend (Coude arrondie rugueux)",
        "params": ["D", "R", "alpha"],
        "labels": ["Pipe diameter D [m]", "Radius R [m]", "Angle alpha [°]"]},
    "D1": {
        "label": "Venturi Meter (Débitmètre à Venturi)",
        "params": ["d", "D"],
        "labels": ["Throat diameter d [m]", "Pipe diameter D [m]"]},
    "D2": {
        "label": "Diaphragm Meter (Débitmètre à diaphragme)",
        "params": ["d", "D"],
        "labels": ["Orifice diameter d [m]", "Pipe diameter D [m]"]},
    
    "K13_conf_sym": {
        "label": "Jonction à confluent symétrique",
        "params": ["Q_v1", "Q_v3"]},
    
    "K23_conf_sym": {
        "label": "Jonction à confluent symétrique",
        "params": ["Q_v2", "Q_v3"]},
    
    "K31_sep_sym": {
        "label": "Jonction à séparation symétrique",
        "params": ["Q_v1", "Q_v3"]},
    
    "K32_sep_sym": {
        "label": "Jonction à séparation symétrique",
        "params": ["Q_v2", "Q_v3"]},
        
    "K12_conf_lat": {
        "label": "Jonction à confluent latérale",
        "params": ["Q_v2", "Q_v3"]},

    "K32_conf_lat": {
        "label": "Jonction à confluent latérale",
        "params": ["Q_v2", "Q_v3"]},
    
    "K13_sep_lat": {
        "label": "Jonction à séparation latérale",
        "params": ["Q_v1", "Q_v3"]},
    
    "K12_sep_lat": {
        "label": "Jonction à séparation latérale",
        "params": ["Q_v1", "Q_v3"]}
}


def get_final_Ks(chock_id, params):
    if params is None :
        params = {}
    
    # --- AJOUT POUR LE CAS CUSTOM ---
    if chock_id == "CUSTOM":
        return params.get('Ks_custom', 0.0), "Vm"

    # ÉTAPE A : Le robot regarde si la valeur est FIXE (Constante)
    if chock_id in KS_CONSTANTS:
        return KS_CONSTANTS[chock_id], "Vm"  # Il renvoie direct 0.5, 1.0, etc.
    
    # ÉTAPE B : Le robot regarde si c'est une COURBE (Interpolation)
    elif chock_id in KS_INTERP_TABLES:
        table = KS_INTERP_TABLES[chock_id]
        x_data, y_data = table["x"], table["y"]
        if x_data[0] > x_data[-1]: # Si [1, 0.75...]
            x_data = x_data[::-1]
            y_data = y_data[::-1]
            
        Ks = float(np.interp(params.get('x_user', 0), x_data, y_data))
        return Ks, "Vm"
    
    else: #chock_id in KS_FORMULA_CONFIG
        try : 
            if chock_id == "E1": # Élargissement brusque
                S1 = params['S1']
                S2 = params['S2']
                return (1 - S1/S2)**2 ,"Vm"
                
            elif chock_id == "R1": # Rétrécissement de section (Vanne papillon/Grille)
                s = params['s']
                S = params['S']
                theta_rad = math.radians(params['theta'])
                Cc = 0.59 + 0.41 * (s/S)**3
                if theta_rad > math.pi/2 :
                    return (1 / (Cc -1))**2 * math.sin(theta_rad) ,"Vm"
                else :
                    return (1 / (Cc -1))**2 ,"Vm"
            
            elif chock_id == "D2": # Débitmètre à diaphragme
                ratio = params['d']/params['D']
                # Formule complexe de votre Excel
                return (1 + 0.707 * math.sqrt(1 - ratio**2) - ratio**2) * (1/ratio)**4 ,"Vm"
            
            elif chock_id =="C1": #Coude brusque
                alpha_rad = math.radians(params['alpha'])
                return 1.3 * (1 - math.cos(alpha_rad)) ,"Vm"
            
            elif chock_id =="C2": #Coude arrondie lisse  
                alpha_rad = math.radians(params['alpha'])
                D = params['D']
                R = params['R']
                return (0.13 + 1.85 * (D / (2 * R))**3.5) * alpha_rad / math.pi/2 ,"Vm"
            
            elif chock_id =="C3": #Coude arrondie rugueux  
                D = params['D']
                R = params['R']
                return 0.42 * (D/R)**0.5 ,"Vm"
            
            elif chock_id =="V1": #Vanne à papillon  
                alpha_rad = math.radians(params['alpha'])
                return (3.2 * 10**7) / (math.pi/2 - alpha_rad) ,"Vm"
            
            elif chock_id =="D1": #Débimètre à Venturi 
                ratio = params['d']/params['D']
                return 0.25 * (ratio**4 -1 ) ,"Vm"
            # --- JONCTIONS (Exemple de réécriture propre) ---
            
            elif chock_id == "K13_conf_sym":
                # Référence V3 d'après votre image
                Q_v1, Q_v3 = params["Q_v1"], params["Q_v3"]
                Ks_val = 2 + 3 * ((Q_v1 / Q_v3)**2 - (Q_v1 / Q_v3)) 
                return Ks_val, "V3" 
            
            elif chock_id == "K23_conf_sym":
                # Référence V3 d'après votre image
                Q_v2, Q_v3 = params["Q_v1"], params["Q_v3"]
                Ks_val = 2 + 3 * ((Q_v2 / Q_v3)**2 - (Q_v2 / Q_v3)) 
                return Ks_val, "V3" 
            
            elif chock_id == "K32_sep_sym":
                # Référence V3 d'après votre image
                Q_v2, Q_v3 = params["Q_v2"], params["Q_v3"]
                Ks_val = 1 + 0.3 * (Q_v2 / Q_v3)**2 
                return Ks_val, "V3"
            
            elif chock_id == "K31_sep_sym":
                # Référence V3 d'après votre image
                Q_v1, Q_v3 = params["Q_v1"], params["Q_v3"]
                Ks_val = 1 + 0.3 * (Q_v1 / Q_v3)**2 
                return Ks_val, "V3"
            
            elif chock_id == "K32_conf_lat":
                # Référence V3 d'après votre image
                Q_v2, Q_v3 = params["Q_v2"], params["Q_v3"]
                Ks_val = 0.6 * ((-1) + 5 * Q_v3 / Q_v2 - 2*(Q_v3 / Q_v2)**2) 
                return Ks_val, "V2"
            
            elif chock_id == "K13_sep_lat":
                # Référence V3 d'après votre image
                Q_v1, Q_v3 = params["Q_v1"], params["Q_v3"]
                Ks_val = 1 + ( Q_v3 / Q_v1)**2 
                return Ks_val, "V1"
            
            elif chock_id == "K12_con_lat":
                # Référence V2 d'après votre image
                Q_v3, Q_v2 = params["Q_v3"], params["Q_v2"]
                Ks_val = 2 * (Q_v3 / Q_v2) - (Q_v3 / Q_v2)**2 
                return Ks_val, "V2"
            
            elif chock_id == "K12_sep_lat":
                # Référence V1 d'après votre image
                Q_v1, Q_v3 = params["Q_v1"], params["Q_v3"]
                Ks_val = 0.4 * (Q_v3 / Q_v1)**2
                return Ks_val, "V1"
            # etc... pour C1, C2, C3
        except Exception as e:
            return 0.0, "Vm"
    return 0.0, "Vm"

def total_sing(elements, rho_m, Vm_default):
    """
    Calcule la somme de toutes les pertes singulières.
    elements: liste de dictionnaires (le panier d'achat).
    """
    total = 0.0
    
    for e in elements:
        # On calcule la perte pour cet élément (en tenant compte de sa quantité)
        chock_id = e["id"]
        params = e.get("params", {})
        qty = e.get("quantity", 1)

        Ks, v_ref_name = get_final_Ks(chock_id, params)
        # 2. SELECTION DE LA VITESSE DE REFERENCE
        # Si c'est une jonction, on cherche V1, V2 ou V3 dans les paramètres
        # Sinon, on utilise la vitesse par défaut Vm
        
        V_ref = params.get(v_ref_name, Vm_default)
        # Récupération de la vitesse réelle du système
        if v_ref_name == "V1":
            V_ref = st.session_state.get('V1', Vm_default)
        elif v_ref_name == "V2":
            V_ref = st.session_state.get('V2', Vm_default)
        elif v_ref_name == "V3":
            V_ref = st.session_state.get('V3', Vm_default)
        else:
            V_ref = Vm_default
        
        if V_ref is None: V_ref = Vm_default 
        
        # 3. CALCUL FINAL (en Pascals)
        dp_unitaire = Ks * (rho_m * V_ref**2 / 2) 

        e["Ks_calculated"] = Ks

        dp_total_item = dp_unitaire * qty

        # On stocke le résultat dans le dictionnaire pour l'affichage tableau
        h_m_item = dp_total_item / (rho_m * 9.81) if (rho_m * 9.81) > 0 else 0
        
        e["deltaP_total"] = dp_total_item
        e["h_m_item"] = h_m_item
        

        total += dp_total_item
        
    return total
def calculer_HMT_physique(hf_linear, h_m, Z_start, Z_end, p_final_val, p_start_val, rho_m):
    """
    Calcule la HMT totale nécessaire pour vaincre les pertes et le dénivelé.
    """
    g = 9.81
    
    # Hauteur associée aux pertes totales
    h_total = hf_linear + h_m
    
    # Hauteur associée au dénivelé (Géodésique)
    delta_Z = Z_end - Z_start
    
    h_pression_finale = (p_final_val - p_start_val) / (rho_m * g)
    
    # HMT Totale
    HMT = delta_Z + h_total + h_pression_finale
    
    return HMT

def pump_hydraulic_power(rho_m, g, Q, HMT):
    """P_hyd = ρ_mgQH  [W]"""
    Q_s = Q / 3600
    g = 9.81
    return rho_m * g * Q_s * HMT / 1000   # Conversion de W en KW

def pump_shaft_power(P_hyd, eta_pump):
    """Calcule la puissance sur l'arbre de la pompe (KW) """
    return P_hyd / eta_pump if eta_pump > 0 else 0

def motor_power(P_shaft, eta_motor):
    """Calcule de la puissance électrique absorbée (KW)"""
    return P_shaft / eta_motor if eta_motor > 0 else 0


# ─────────────────────────────────────────────
#  UI BUILDING BLOCKS
# ─────────────────────────────────────────────

def kpi_card(val, unit, label, style=""):
    return f"""
    <div class="kpi-card {style}">
      <div class="kpi-val {style}">{val}</div>
      <div class="kpi-unit">{unit}</div>
      <div class="kpi-lbl">{label}</div>
    </div>"""

def kpi_row(cards_html):
    return f'<div class="kpi-grid">{"".join(cards_html)}</div>'

def formula_box(text):
    st.markdown(f'<div class="formula-box">📐 {text}</div>', unsafe_allow_html=True)

def result_row(label, value):
    return f"""
    <div class="result-row">
      <span class="result-label">{label}</span>
      <span class="result-value">{value}</span>
    </div>"""

def section_header(title):
    st.markdown(f'<div class="section-title">▸ {title}</div>', unsafe_allow_html=True)

def step_badge(step_num, title):
    st.markdown(
        f'<div class="step-badge">STEP {step_num} — {title}</div>',
        unsafe_allow_html=True
    )

def progress_bar(pct):
    st.markdown(
        f'<div class="progress-bar-outer">'
        f'<div class="progress-bar-inner" style="width:{pct}%"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def make_plotly_layout(title="", xaxis_title="", yaxis_title=""):
    return dict(
        template="plotly_dark",
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=DARK_BG,
        font=dict(family="IBM Plex Mono, monospace", color=TEXT_MAIN, size=11),
        title=dict(text=title, font=dict(color=ACCENT, size=13)),
        xaxis=dict(
            title=xaxis_title,
            gridcolor=GRID_COL,
            linecolor=BORDER_COL,
            title_font=dict(color=TEXT_MUTED),
        ),
        yaxis=dict(
            title=yaxis_title,
            gridcolor=GRID_COL,
            linecolor=BORDER_COL,
            title_font=dict(color=TEXT_MUTED),
        ),
        margin=dict(l=50, r=20, t=40, b=50),
    )


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────

STEPS = [
    (1, "Slurry Inputs"),
    (2, "Critical Velocity & D"),
    (3, "Linear Head Losses"),
    (4, "Singular Head Losses"),
    (5, "Hydraulic Grade Line"),
    (6, "Pump Power"),
]
DONE_FLAGS = ["step1_done","step2_done","step3_done","step4_done","step5_done","step6_done"]
STEP_ICONS = ["⬡", "◈", "∿", "⊕", "〰", "⚡"]

with st.sidebar:
    st.markdown(
        f"""
        <div style="padding:16px 0 8px 0; border-bottom:1px solid {BORDER_COL}; margin-bottom:12px;">
          <div style="color:{ACCENT}; font-size:0.65rem; letter-spacing:3px; text-transform:uppercase;">
            ⚙ HYDRAULIC CALCULATOR
          </div>
          <div style="color:{TEXT_MUTED}; font-size:0.60rem; margin-top:4px;">
            Slurry Pipeline Design Tool v1.0
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div style="color:{TEXT_MUTED}; font-size:0.68rem; letter-spacing:1px; margin-bottom:8px;">WORKFLOW NAVIGATION</div>',
        unsafe_allow_html=True,
    )

    completed = sum(st.session_state[f] for f in DONE_FLAGS)
    progress_bar(int(completed / len(STEPS) * 100))
    st.markdown(
        f'<div style="color:{TEXT_MUTED}; font-size:0.68rem;">{completed}/{len(STEPS)} steps completed</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    for (num, title), icon, flag in zip(STEPS, STEP_ICONS, DONE_FLAGS):
        is_active = st.session_state.current_step == num
        is_done   = st.session_state[flag]
        css_class = "active" if is_active else ("done" if is_done else "inactive")
        indicator = "✓" if is_done else (f"{num}" if not is_active else "▶")
        if st.button(
            f"{icon}  STEP {num}  |  {title}",
            key=f"nav_{num}",
            use_container_width=True,
        ):
            st.session_state.current_step = num

    st.markdown(
        f"""
        <div style="margin-top:24px; border-top:1px solid {BORDER_COL}; padding-top:14px;">
          <div style="color:{TEXT_MUTED}; font-size:0.62rem; line-height:1.6;">
            <div style="color:{ACCENT}; margin-bottom:4px; font-size:0.65rem; letter-spacing:1px;">
              SYSTEM STATUS
            </div>
            ρ_s: {st.session_state.rho_s:.0f} kg/m³<br>
            ρ_l: {st.session_state.rho_l:.0f} kg/m³<br>
            d₅₀: {st.session_state.d50*1000:.4f} mm<br>

            
            μ_l: {st.session_state.mu_l:.4f} Pa·s<br>
            μ_s: {st.session_state.mu_s:.4f} Pa·s<br>
            ρ_mixture: {st.session_state.rho_m:.1f} kg/m³<br>

            Cv: {st.session_state.get('Cv')*100:.1f} %<br>
            Q: {st.session_state.get('Q'):.1f} m³/h<br>
            Pipe L: {st.session_state.pipe_length:.0f} m<br>
            ρ_mixture: {st.session_state.rho_m:.1f} kg/m³<br>
            Cv: {st.session_state.Cv*100:.1f} %<br>
            
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



# ─────────────────────────────────────────────
#  MAIN HEADER
# ─────────────────────────────────────────────
st.markdown(
    """
    <div class="main-header">
      <h1>⚙ Slurry Transport Hydraulic Calculator</h1>
      <p>INDUSTRIAL PIPELINE DESIGN  ·  SEQUENTIAL HYDRAULIC ANALYSIS  ·  6-STEP WORKFLOW</p>
    </div>
    """,
    unsafe_allow_html=True,
)





# ─────────────────────────────────────────────
#  STEP 1 – SLURRY INPUTS
# ─────────────────────────────────────────────

def render_step1():
    step_badge(1, "SLURRY INPUTS")
    st.markdown("Define the physical properties of the slurry and pipeline geometry.")
    # --- BARRE D'OUTILS PRO (Import Excel) ---
    with st.expander("📥 IMPORTER DEPUIS EXCEL"):
        # 1. Zone de collage
        raw_paste = st.text_area("Copiez les cellules Excel (nom et valeur) et collez-les ici :", height=100,
                                 placeholder="rho_s    2430\nmu_s    0.0014")
        # 2. Bouton magique
        if st.button("🚀 Remplir les cases automatiquement", type="primary"):
            if raw_paste:
                # On sépare le texte par lignes
                lines = raw_paste.strip().split('\n')
                updates_count = 0

                for line in lines:
                    # Excel utilise la tabulation pour séparer les colonnes A et B
                    parts = line.split()

                    if len(parts) >= 2:
                        nom_param = parts[0].strip().lower().replace(" ", "").replace("_", "")   # Ex: "rho_s"
                        valeur_str = parts[-1].strip().replace(',', '.')  # Ex: "2430"
                        
                        
                        for session_key in st.session_state.keys():
                            clean_key = session_key.lower().replace(" ", "").replace("_", "")
                            
                            if clean_key == nom_param:
                                try:
                                    st.session_state[session_key] = float(valeur_str)
                                    updates_count += 1
                                except:
                                    pass # On ignore si ce n'est pas un chiffre
                if updates_count > 0:
                    st.success(f"✅ {updates_count} paramètres mis à jour !")
                    st.rerun()
                else : 
                    st.error("❌ Aucun paramètre reconnu. Vérifiez le nom des colonnes.") 
    
    
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.expander("🧪  SOLID PHASE PROPERTIES", expanded=True):
            section_header("Solid Properties")
            st.number_input("Solid Density ρₛ [kg/m³]", key="rho_s", step=10.0)
            st.number_input("Median Particle Size d₅₀ [m]", key="d50", format="%.7f", step=0.000001)
            st.number_input("Mass Concentration Cw [-]", key="Cw", step=0.01)
            st.number_input("Solid Viscosity μₛ [Pa·s]", key="mu_s", format="%.4f")


            formula_box("ρ_m = 1 / (Cw / ρ_s) + (1 - Cw) / ρ_l     [mixture density]")

    with col2:
        with st.expander("💧  LIQUID CARRIER PROPERTIES", expanded=True):
            section_header("Liquid Properties")
            st.number_input("Liquid Density ρₗ [kg/m³]", key="rho_l")
            st.number_input("Liquid Viscosity μₗ [Pa·s]", key="mu_l", format="%.5f")

            #Calcul automatique de Cv 
            formula_box("ρ_m = 1 / Cw/rho_s + (1 - Cw) /rho_l")
            formula_box("Cv = Cw * ρ_m / ρ_s")
            formula_box("μ_m = μ_l·(1 + 2.5Cv + 10.05Cv² + ...)   [Thomas 1965]")
            formula_box("ρ_s / ρ_l")

    with col3:
        with st.expander("🔧  PIPELINE GEOMETRY", expanded=True):
            section_header("Pipe Parameters")
            st.number_input("Flow Rate Q [m³/h]", key="Q", value=float(st.session_state.Q))
            st.number_input("Line Length L [m]", key="pipe_length", value=float(st.session_state.pipe_length))

    # Compute derived values
    s_rho_s = st.session_state.get('rho_s')
    s_rho_l = st.session_state.get('rho_l', 1000.0)
    s_Cw    = st.session_state.get('Cw')
    s_mu_l  = st.session_state.get('mu_l', 0.001)

    # Calcul uniquement si les densités sont valides (> 0) pour éviter ZeroDivisionError
    if s_rho_s > 0 and s_rho_l > 0:
        rho_m = slurry_density(s_rho_s, s_rho_l, s_Cw)
        Cv = concentration(s_Cw, rho_m, s_rho_s)
        mu_m = slurry_dynamic_viscosity(s_mu_l, Cv)
        Ss = s_rho_s / s_rho_l
    

    
    st.markdown("---")
    section_header("COMPUTED SLURRY PROPERTIES")
    cards = [
        kpi_card(f"{rho_m:.1f}", "kg/m³", "Mixture Density"),
        kpi_card(f"{mu_m*1000:.3f}", "mPa·s", "Effective Viscosity", "accent2"),
        kpi_card(f"{Ss:.3f}", "—", "Specific Gravity (Sₛ)", "warning"), 
        kpi_card(f"{Cv*100:.1f}", "%", "Volume Concentration", "success"),
        kpi_card(f"{st.session_state.d50*1000:.4f}", "mm", "d₅₀ Particle Size"),
        kpi_card(f"{st.session_state.Q:.2f}", "m³/h", "Flow"),
    ]
    
    st.markdown(kpi_row(cards), unsafe_allow_html=True)
    
    col_a, col_b = st.columns([3, 1])
    with col_b:
        if st.button("SAVE & CONTINUE →", key="s1_save", use_container_width=True):
            if st.session_state.rho_m <= 1000:
                st.error("La densité solide doit être supérieure à la densité du liquide !")
            if st.session_state.Cw > 0.25:
                st.error("La concentration ne doit pas dépasser la limite newtonienne !")
            if st.session_state.Q <= 0 :
                st.error("Le débit (Flow) ne peut pas être nul.")
            else : 
                st.session_state.Cv = Cv 
                st.session_state.step1_done = True
                st.session_state.current_step = 2
                st.rerun()

# ─────────────────────────────────────────────
#  STEP 2 – CRITICAL VELOCITY & PIPE DIAMETER
# ─────────────────────────────────────────────

def render_step2():
    step_badge(2, "CRITICAL VELOCITY & PIPE DIAMETER")

    if not st.session_state.step1_done:
        st.warning("⚠ Complete Step 1 first.")
        return

    rho_s = st.session_state.rho_s
    rho_l = st.session_state.rho_l
    mu_s = st.session_state.mu_s
    Cv    = st.session_state.Cv
    Cw = st.session_state.Cw
    mu_l  = st.session_state.mu_l
    d50   = st.session_state.d50
    Q = st.session_state.get('Q')

    rho_m = slurry_density(rho_s, rho_l, Cw)
    mu_m  = slurry_dynamic_viscosity(mu_l, Cv)
    
    Vc, D_pipe, Vm, model = calculate_critical_velocity_and_diameter(
        Q, d50, rho_s, rho_l, rho_m, mu_m, Cv, mu_s
    )

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("⚙  PIPE DESIGN PARAMETERS", expanded=True):
            section_header("Pipe Selection")
            st.metric("Recommended Internal Diameter", f"{D_pipe*1000:.1f} mm", help="Optimum diameter calculated by the model")

            st.metric("Design Flow Velocity Vm [m/s]",f"{Vm:2f} m/s", help="Optimum velocuty calculated by the model" )
            
            formula_box(f"Model Selected: **{model}**")
            formula_box("Calculated using MTI, Durand or Wilson arbitration logic.")

    with col2:
        with st.expander("📊  COMPUTED VELOCITY ANALYSIS", expanded=True):
            Re_m = reynolds_number(rho_m, Vm, D_pipe, mu_m)

            flow_regime = "TURBULENT" if Re_m > 4000 else ("TRANSITIONAL" if Re_m > 2300 else "LAMINAR")
            transport_status = "✓ FULLY TURBULENT" if Vm > Vc else "⚠ BELOW CRITICAL"
            status_css = "status-ok" if Vm > Vc else "status-err"

            st.markdown(
                "".join([
                    result_row("Critical Velocity Vc", f"{Vc:.3f} m/s"),
                    result_row("Design Velocity V", f"{Vm:.3f} m/s"),
                    result_row("Reynolds Number Re_m", f"{Re_m:.0f}"),
                    result_row("Flow Regime", flow_regime),
                ]),
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="margin-top:10px;">Transport status: '
                f'<span class="status-pill {status_css}">{transport_status}</span></div>',
                unsafe_allow_html=True,
            )

   

    # KPIs
    cards = [
        kpi_card(f"{Vc:.2f}", "m/s", "Critical Velocity", "accent2"),
        kpi_card(f"{Vm:.2f}", "m/s", "Design Velocity"),
        kpi_card(f"{Re_m:.0f}k", "—", "Reynolds No.", "warning"),
        kpi_card(f"{Q:.2f}", "m³/h", "desired flow rate"),
        kpi_card(f"{D_pipe*1000:.0f}", "mm", "Pipe Diameter", "accent2"),
    ]
    st.markdown(kpi_row(cards), unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_a:
        if st.button("← BACK", key="s2_back"):
            st.session_state.current_step = 1; st.rerun()
    with col_c:
        if st.button("SAVE & CONTINUE →", key="s2_save", use_container_width=True):
            st.session_state.update({
                "D_pipe": D_pipe, "Vm": Vm, "rho_m":rho_m, "Re_m": Re_m,
                "step2_done": True, "current_step": 3,
            })
            st.rerun()


# ─────────────────────────────────────────────
#  STEP 3 – LINEAR HEAD LOSSES
# ─────────────────────────────────────────────
def render_step3():
    step_badge(3, "LINEAR HEAD LOSSES")
    
    if not st.session_state.step2_done:
        st.warning("⚠ Complete Step 2 first.")
        return

    with st.expander("📊  WASP MODEL: GRANULOMETRY & RHEOLOGY", expanded=False):
        section_header("Particle Size Distribution")
    
    # 1. Saisie des tranches (di) et fractions (mi)
    if "psd_data" not in st.session_state:
        st.session_state.psd_data = pd.DataFrame({
            "Sizes dᵢ [µm]": [37, 75, 150, 300, 600],
            "Mass Fractions mᵢ [-]": [0.1, 0.2, 0.4, 0.2, 0.1]
        })

    with st.expander("📝 EDIT GRANULOMETRY (PSD)", expanded=True):
        col_t1, col_t2 = st.columns([2, 1])
        with col_t1:
            # Le tableau éditable
            edited_df = st.data_editor(
                st.session_state.psd_data,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key="psd_editor"
            )
        with col_t2:
            # Validation en temps réel pour le VP
            total_m = edited_df["Mass Fractions mᵢ [-]"].sum()
            st.metric("Total Fraction", f"{total_m:.2f}")
            if abs(total_m - 1.0) > 0.01:
                st.error("Sum must be 1.0")
            else:
                st.success("PSD Validated")

    # --- SECTION PARAMÈTRES DE FORME ---
    ki_vol_dict = {
        "Sand": 0.26, "Sillimanite, Bituminous coal": 0.23,
        "Blast furnace slag": 0.19, "Limestone, Talc, Plumbago": 0.16,
        "Gypsum": 0.13, "Flake graphite": 0.023, "Mica": 0.003,
        "Other (Manual input)": None
    }


    mineral_choice = "Other (Manual input)"
    p_vol = 0.0 # Valeur par défaut

    k_rug = roughness_map = {
            "Steel (New)": 0.000045,
            "PEHD/HDPE neuf": 0.000007,
            "PEHD vieilli(service > 5 ans)": 0.000020,
            "Acier commercial neuf": 0.000046,
            "Steel (Slightly Corroded)": 0.00015,
            "Acier galvanisé neuf": 0.00015,
            "Fonte grise neuve": 0.00026,
            "HDPE / Plastic": 0.000007,
            "PVC": 0.0000015,
            "Concrete Pipe": 0.0015,
            "Other (Manual)": 0.000046
        }

    col_g3, col_g4 = st.columns(2)
    with col_g3:
        p_shape = st.selectbox("Particle Shape", ["Sphérique", "Non-sphérique"], index=1)
        mineral_choice == "Other (Manual input)"

        if p_shape == "Non-sphérique" :
            mineral_choice = st.selectbox(
            "Mineral Type (Shape Factor K)", options=list(ki_vol_dict.keys()),
            index=4  # Par défaut sur Gypsum (indice 4)
            )

    with col_g4:
        if mineral_choice == "Other (Manual input)":
            p_vol = st.number_input("Particle Volume (if non-spherical)", 
                value=0.00009, 
                format="%.9f",
                help="0.000260")
            st.info("Le ki_vol sera calculé par la relation: p_vol / d_star³")

            
        else:
            # On capte directement le K du tableau
            current_k = ki_vol_dict[mineral_choice]
            st.info(f"Automatically set ki_vol = {current_k}")

        mat_choice = st.selectbox("Pipe Material (Auto-fill rugosity)", options=list(roughness_map.keys()))

        default_rug = roughness_map[mat_choice]
        k_rug = st.number_input("Pipe Roughness k_rug [m]",
                                value=default_rug,
                                format="%.6f",
                                help="Typical steel: 45µm. HDPE: 7µm.")
        
        
        Cv_max = st.number_input("Max Packing Concentration Cv_max", value=0.60, step=0.01,help="Standard: 0.60 to 0.64. For very fine particles, it can be lower.")
        if Cv_max > 0.70:
            st.warning("⚠️ High Cv_max: Values above 0.70 are physically unlikely for slurries.")

    # 3. Conversion des chaînes de caractères en listes numériques pour le moteur WASP
   # Extraction des listes pour le calcul
    di = edited_df["Sizes dᵢ [µm]"].tolist()
    mi = edited_df["Mass Fractions mᵢ [-]"].tolist()
        
    
    #======BOUTON DE CALCUL================================
    st.markdown("---")
    if st.button("RUN WASP CALCULATION 🚀", use_container_width=True, type="primary"):
        if abs(sum(mi) - 1.0) > 0.05:
            st.error("Calculation aborted: Sum of fractions is too far from 100.0")
            return

        try:
            # --- 1. PRÉPARATION DES DONNÉES DES ETAPES PRECEDENTES---
            D_pipe = st.session_state.get('D_pipe')
            Vm     = st.session_state.get('Vm')
            rho_s  = st.session_state.get('rho_s') # .get au lieu de .rho_s
            rho_l  = st.session_state.get('rho_l')
            rho_m  = st.session_state.get('rho_m')
            mu_l   = st.session_state.get('mu_l')
            Cv     = st.session_state.get('Cv')
            L      = st.session_state.get('pipe_length')

            # Appel de votre fonction de calcul
            pc_m, pc_mf, fi_total, iters, Cvf_fin = calculate_wasp_losses(
                D_pipe, Vm, rho_l, rho_s, mu_l, Cv, di, mi, 
                k_rug, p_shape, p_vol, Cv_max, mineral_choice)
            
            # RÉCUPÉRATION DE LA DENSITÉ DÉJÀ CALCULÉE (Cohérence session_state)
            # CALCUL DES PERTES LINÉAIRES UNIQUEMENT EN REMPLAçANT hf_total PAR hf_linear
            hf_linear = (pc_m * L) / (rho_m * 9.81) # les pertes de charges linéaire 
            i_gradient = pc_m / (rho_m * 9.81) # m/m

            # SAUVEGARDE DANS LA SESSION POUR L'AFFICHAGE
            st.session_state.update({
                "iters_calculated": iters,
                "Cvf_calculated": Cvf_fin,
                "fi_calculated": fi_total,
                "pc_m_calculated": pc_m,
                "pc_mf_calculated": pc_mf,
                "hf_linear_calculated": hf_linear,
                "i_gradient_calculated": i_gradient,
            })
            st.session_state.step3_done = True
        except Exception as e:
            st.error(f"Calculation Error: {e}")
            return
        
    if st.session_state.get('step3_done'):
        hf_v   = st.session_state.get('hf_linear_calculated')
        i_v    = st.session_state.get('i_gradient_calculated')
        pc_m_v  = st.session_state.get('pc_m_calculated')
        L_v    = st.session_state.get('pipe_length')

        col1, col2 = st.columns([1, 1])
        with col1:
            with st.expander("∿  WASP CONVERGENCE PARAMETERS", expanded=True):
                section_header("Solid-Liquid Interaction")
                st.markdown(
                    result_row("Iterations", f"{st.session_state.get('iters_calculated')}"),
                    unsafe_allow_html=True,)
                st.markdown(
                    result_row("Vehicle Conc. (Cvf)", f"{st.session_state.get('Cvf_calculated'):.3f} m³/m³"),
                    unsafe_allow_html=True)
                st.markdown(
                    result_row("Settling Factor (Fi)", f"{st.session_state.get('fi_calculated'):.4f}"),
                    unsafe_allow_html=True)
                st.markdown(
                    result_row("Vehicle Loss (pc_mf)", f"{st.session_state.get('pc_mf_calculated'):.1f} Pa/m"),
                    unsafe_allow_html=True)
                
                # Correction de la ligne 1033
                pc_m_val = st.session_state.get('pc_m_calculated')
                pc_mf_val = st.session_state.get('pc_mf_calculated')
                pc_s = pc_m_val - pc_mf_val
                st.markdown(
                    result_row("Settled Loss (pc_s)", f"{pc_s:.1f} Pa/m"),
                    unsafe_allow_html=True)
                
        with col2:
            st.markdown('<div class="section-panel">', unsafe_allow_html=True)
                 # On récupère les valeurs depuis le "coffre-fort" session_state
            
            st.markdown(
                result_row("Total Head Loss (hf)", f"<strong>{hf_v:.2f} m</strong>"), 
                unsafe_allow_html=True)
            
            st.markdown(
                result_row("Unit Pressure Drop", f"{pc_m_v:.1f} Pa/m"),
                unsafe_allow_html=True)
            
            st.markdown(
                result_row("Pressure Drop (ΔP)", f"<strong>{pc_m_v * L_v / 1000:.1f} kPa</strong>"), 
                unsafe_allow_html=True)
            
            st.markdown(
                result_row("Hydraulic Gradient (i)", f"<strong>{i_v:.4f} m/m</strong>"), 
                unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

        cards = [
          # Cartes KPI avec le nom correct
            kpi_card(f"{hf_v:.2f}", "m", "Linear Head Loss"), # Changement de nom ici
            kpi_card(f"{i_v*1000:.2f}", "m/km", "Hydr. Gradient", "accent2"),
            kpi_card(f"{(pc_m_v * L_v)/1000:.1f}", "kPa", "Pressure Drop (ΔP_L)", "success"),
        ]
        st.markdown(kpi_row(cards), unsafe_allow_html=True)

    col_a, _, col_c = st.columns([1, 2, 1])
    with col_a:
        if st.button("← BACK", key="s3_back"):
            st.session_state.current_step = 2; st.rerun()
    with col_c:
        if st.button("SAVE & CONTINUE →", key="s3_save", use_container_width=True):
            hf_final = st.session_state.get('hf_linear_calculated', 0)
            i_final = st.session_state.get('i_gradient_calculated', 0)

            st.session_state.update({
                "hf_linear": hf_final,
                "i_gradient": i_final,
                "step3_done": True, "current_step": 4,
            })
            st.rerun()
# ─────────────────────────────────────────────
#  STEP 4 – SINGULAR HEAD LOSSES
# ─────────────────────────────────────────────

def render_step4():
    step_badge(4, "SINGULAR HEAD LOSSES")
    if not st.session_state.get('step3_done'):
        st.error("⚠️ Veuillez compléter l'étape 3 d'abord.")
        return

    V_default = st.session_state.get('Vm')
    rho_m = st.session_state.get('rho_m')
    hf_linear = st.session_state.get('hf_linear')
    h_m = st.session_state.get('h_m')
    L = st.session_state.get('pipe_length')
            
    # Liste organisée avec headers
    display_options = {

        "-- VALVES (VANNES) --": "HEADER",
        "Gate Valve (Vanne à opercule)": "VO",
        "Diaphragm Valve (Vanne à membrane)": "VM",
        "Butterfly Valve (Vanne papillon)": "V1",
        "Ball Valve (Boiseau sphérique)": "RBs",
        "Vanne à Pointeau": "VP",
        "Vanne à Souppage": "VS",
                
        "-- BENDS (COUDES) --": "HEADER",
        "Sharp Bend (Coude brusque)": "C1",
        "Smooth Rounded Bend (Lisse)": "C2",
        "Coude arrondie (rugueux)": "C3",
                
        "-- OTHERS (AUTRES) --": "HEADER",
        "Sudden Expansion (Élargissement brusque)": "E1",
        "Entrance (Entrée brusque)": "EB",
        "Exit (Sortie de conduite)": "ES",
        "Entrée Profilée": "EP",
        "Arrivée quelquonque": "AQ",
        "Contraction Brusque arrêt vif": "CB_av",
        "Contraction Brusque arrondie": "CB_ar",
        "Retrecissement de section": "R1",
        "Diaphragm Meter (Débimètre à Diaphragme)": "D2",
        "Retrecissement Progressif": "RP",
        "Débimètre à Venturi": "D1",
        "Jonction à Confluent Symétrique K13": "K13_conf_sym",
        "Jonction à Confluent Symétrique K23": "K23_conf_sym",
        "Jonction à Séparation Symétrique K32": "K32_sep_sym",
        "Jonction à Séparation Symétrique K31": "K31_sep_sym",
        "Jonction à Confluent Latéral K12": "K12_conf_lat",
        "Jonction à Confluent Latéral K32": "K32_conf_lat",
        "Jonction à Séparation latérale K12": "K12_sep_lat",
        "Jonction à Séparation latérale K13": "K13_sep_lat",
                
        "-- SPECIAL --": "HEADER",
        "AUTRE ACCESSOIRE (Saisie manuelle Ks)": "CUSTOM"
            
    }

    st.markdown(f"### ⚙️ Étape 4 : Pertes de Charge Singulières")

    if "accident_list" not in st.session_state:
        st.session_state.accident_list = []

    # --- ZONE D'AJOUT (FORMULAIRE) ---
    with st.expander("➕ Ajouter un accessoire (Auto-calculé ou Manuel)", expanded=True):
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            choice_label = st.selectbox("Sélectionner un type", options=list(display_options.keys()))
            choice_id = display_options[choice_label]

        if choice_id == "HEADER":
            st.warning("Veuillez choisir un accessoire valide.")
            add_disabled = True
        else:
            add_disabled = False
            with col2 : 
                qty = st.number_input("Quantité", min_value=1, value=1, key="add_qty")
            with col3:
                 # CORRECTION 2 : Le tableau de positions remplace le number_input unique
                st.write("Positions x (m)")
                pos_df = st.data_editor(
                    [{"Pos. (m)": 0.0} for _ in range(qty)],
                    hide_index=True, # Plus pro sans l'index
                    column_config={
                        "Pos. (m)": st.column_config.NumberColumn(
                            "Position x", min_value=0.0, format="%.1f m"
                        )
                    },
                    key="pos_editor",
                    use_container_width=True
                )
                # On extrait la liste des positions saisies
                pos_list = [row["Pos. (m)"] for row in pos_df]



           # --- GESTION DU CAS MANUEL (CUSTOM) ---
            params = {}
            final_label = choice_label
            manual_Ks = 0.0

            if choice_id == "CUSTOM":
                st.markdown("---")
                c1, c2 = st.columns(2)
                with c1:
                    final_label = st.text_input("Accessory name (optional)", placeholder="Ex: Filtre spécial")
                with c2:
                    manual_Ks = st.number_input("Entrer Ks (ζ) coefficient", min_value=0.0, format="%.5f")
                params['Ks_custom'] = manual_Ks

            elif choice_id in KS_CONSTANTS:
                st.success(f"Fixed Coefficient: Ks = {KS_CONSTANTS[choice_id]}")

            elif choice_id in KS_FORMULA_CONFIG:
                st.info("Saisie des paramètres géométriques :")
                config = KS_FORMULA_CONFIG[choice_id]
                # On crée les colonnes selon le nombre de paramètres
                cols = st.columns(len(config['params']))
                # On itère sur les paramètres ET les labels en même temps
                for i, (p, lbl) in enumerate(zip(config['params'], config.get('labels', config['params']))):
                    # On utilise le label complet "lbl" pour l'affichage
                    # Et on sécurise la clé avec l'ID du composant
                    params[p] = cols[i].number_input(label=lbl, value=0.1, format="%.4f", key=f"input_{choice_id}_{p}")
             
            elif choice_id in KS_INTERP_TABLES:
                label = KS_INTERP_TABLES[choice_id].get("param_label", "Opening Setting")
                params['x_user'] = st.number_input(f"{label}", value=1.0, format="%.2f")

            # --- BOUTON D'AJOUT ---
            if st.button("ADD TO LIST ➕", use_container_width=True, disabled=add_disabled):
                    final_label= params.get('name_custom', choice_label)
                    
                    for p in pos_list:
                        new_item = {
                            "id": choice_id,
                            "label": final_label,
                            "x": p,
                            "quantity": 1, #Pour chaque position
                            "params": params.copy()
                        }
                        st.session_state.accident_list.append(new_item)
                    st.session_state.accident_list.sort(key=lambda x: x['x'])
                    st.success(f"Ajouté : {len(pos_list)} x {final_label}")
                    st.rerun()


    h_m = 0
    # Lancement du moteur de calcul si la liste n'est pas vide
    if len(st.session_state.accident_list) > 0:
        # On appelle votre fonction moteur total_sing
        total_dp_pa = total_sing(st.session_state.accident_list, rho_m, V_default)
        h_m = total_dp_pa / (rho_m * 9.81) if (rho_m * 9.81) > 0 else 0
    
    # Perte totale combinée
    h_total = hf_linear + h_m

    # --- Zone de Récapitulatif ---
    with st.expander("📋 Loss (m)", expanded=True):
        if not st.session_state.accident_list:
            st.info("No fittings added yet. Use the form above to build your system.")
        else:
            # Affichage du tableau stylisé
            rows = []
   
            for i, e in enumerate(st.session_state.accident_list):
                # Récupération de la perte calculée par le moteur pour cet élément
                # On utilise e.get car deltaP_total est créé à l'intérieur de total_sing
                val_h = e.get('h_m_item', 0.0) 

                rows.append({
                    "ID": i + 1,
                    "Pos. (m)": f"{float(e['x']):.1f}",
                    "Accessory Type": e['label'],
                    "Qty": int(e['quantity']),
                    "Loss (m)": f"{val_h:.3f}"
                })
            # 2. Affichage du tableau professionnel (Remplace le Markdown)
            st.dataframe(
                rows, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "ID": st.column_config.TextColumn("#", width="small"),
                    "Pos. (m)": st.column_config.TextColumn("Position (m)", width="small"),
                    "Accessory Type": st.column_config.TextColumn("Accessory", width="large"),
                    "Qty": st.column_config.TextColumn("Quantity", width="small"),
                    "Loss (m)": st.column_config.TextColumn("Total Loss (m)", width="medium"),
                }
            )
            st.markdown("---")
            # Affichage des totaux (vos fonctions CSS restent inchangées)
            st.markdown(result_row("Singular Loss (hm)", f"**{h_m:.3f} m**"), unsafe_allow_html=True)
            st.markdown(result_row("Linear Loss (hf)", f"{hf_linear:.3f} m"), unsafe_allow_html=True)
            st.markdown(result_row("TOTAL HEAD LOSS", f"<strong style='color:#00C8FF'>{h_total:.3f} m</strong>"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True) # Petit espace

            # Bouton Reset aligné
            col_del, col_reset = st.columns([2, 1])

            with col_del:
                # Sélecteur pour choisir quelle ligne supprimer
                delete_options = [f"{r['ID']}. {r['Accessory Type']} ({r['Pos. (m)']}m)" for r in rows]
                item_to_del = st.selectbox("Supprimer un accessoire spécifique :", options=delete_options, label_visibility="collapsed")
                
                if st.button("❌ REMOVE SELECTED", use_container_width=True):
                    idx = int(item_to_del.split(".")[0]) - 1
                    st.session_state.accident_list.pop(idx)
                    total_sing(st.session_state.accident_list, rho_m, V_default)
                    st.rerun()


            with col_reset:
                if st.button("RESET LIST 🗑️", use_container_width=True):
                    st.session_state.accident_list = []
                    st.rerun()


    # --- Cartes KPI et Graphique ---
    st.markdown(kpi_row([
        kpi_card(f"{h_m:.3f}", "m", "Singular Loss", "accent2"),
        kpi_card(f"{h_total:.3f}", "m", "Total H", "success")
    ]), unsafe_allow_html=True)

    # Petit graphique croisé pour voir l'impact relatif des pertes
    if h_total > 0:
        fig = go.Figure(go.Pie(
            labels=["Linear Loss (Pipe)", "Singular Loss (Fittings)"], 
            values=[hf_linear, h_m], 
            hole=0.5,
            marker=dict(colors=["#00C8FF", "#FF6B35"])
        ))
        # Utilisation de votre fonction de layout Plotly habituelle
        fig.update_layout(**make_plotly_layout("Loss Distribution"))
        st.plotly_chart(fig, use_container_width=True)

    # --- Boutons de Navigation ---
    st.markdown("---")
    col_a, _, col_c = st.columns([1, 2, 1])
    with col_a:
        if st.button("← BACK"):
            st.session_state.current_step = 3
            st.rerun()
    with col_c:
        if st.button("SAVE & CONTINUE →", use_container_width=True, type="primary"):
            # Sauvegarde finale pour les calculs de pompes du Step 5
            st.session_state.hf_singular = h_m
            st.session_state.h_total = h_total
            st.session_state.step4_done = True
            st.session_state.current_step = 5
            st.rerun()




# ─────────────────────────────────────────────
#  STEP 5 – HYDRAULIC GRADE LINE (HGL)
# ─────────────────────────────────────────────

def render_step5():
    step_badge(5, "HYDRAULIC GRADE LINE (HGL)")

    # Vérification de sécurité
    if not st.session_state.get('step4_done', False):
        st.warning("⚠ Complete Step 4 first.")
        return

    # --- RÉCUPÉRATION DES PARAMÈTRES (Adapté à votre nomenclature) ---
    L       = st.session_state.get('pipe_length')
    hf_lin  = st.session_state.get('hf_linear')
    h_m = st.session_state.get('h_m')
    h_total = st.session_state.get('h_total') 
    rho_m   = st.session_state.get('rho_m')
    g       = 9.81
    
    if hf_lin is None: hf_lin = 0.0
    if h_m is None: h_m = 0.0
    
    # Récupération des accessoires localisés du Step 4
    accident_list = st.session_state.get('accident_list' , [])
    
    # Transformation de votre liste en tableaux pour le calcul du tracé
    if accident_list:
        xs_acc = np.array([a["x"] for a in accident_list], dtype=float)
        # On convertit les Pa stockés par votre moteur en mètres (hm)
        hm_acc = np.array([a.get("deltaP_total", 0) / (rho_m * 9.81) for a in accident_list], dtype=float)


        lbl_acc = [a["label"] for a in accident_list]
    else:
        xs_acc = np.array([])
        hm_acc = np.array([])
        lbl_acc = ["Aucun accessoire"]
    
    # 1. SAISIE TOPOGRAPHIQUE
    section_header("1. Topographic Survey (Profile)")
    st.info("💡 Edit the table to define the terrain. PCHIP interpolation handles hills/valleys.")

    # ── ① SAISIE TOPOGRAPHIQUE ─────────────────────────────
    st.markdown("### ① Profil Topographique — Levé du Terrain")
    st.caption("Instructions : Copiez vos données (2 colonnes) depuis Excel ou CSV et collez-les ici avec Ctrl+V.")

    # Points par défaut (départ et arrivée)
    topo_default = pd.DataFrame({
        "x (m)":  [0.0, 3887.0],
        "Z (m)":  [58.5, 65.5],
    })

    
    edited_df = st.data_editor(
        topo_default,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "x (m)": st.column_config.NumberColumn("Distance (m)", min_value=0.0, max_value=float(L), format="%.1f"),
            "Z (m)": st.column_config.NumberColumn("Elevation (m)", format="%.3f"),
        },
        key="topo_editor_final",
    )

    # Validation & Interpolation
    try: 
        topo_pts = edited_df.dropna(subset=["x (m)", "Z (m)"]).copy()

        topo_pts["x (m)"] = pd.to_numeric(topo_pts["x (m)"])
        topo_pts["Z (m)"] = pd.to_numeric(topo_pts["Z (m)"])

        topo_pts = topo_pts.sort_values("x (m)").reset_index(drop=True)


        x_pts = topo_pts["x (m)"].values
        z_pts = topo_pts["Z (m)"].values

    except Exception as e:
        st.error("Erreur de format : Assurez-vous que vos données collées sont bien des nombres.")
    
    st.markdown("**Parametres de la charge initiale**")
     
    P0_bar = st.number_input(
        "Pression d'aspiration P_0 (bar)",
        min_value=0.0, max_value=50.0,
        value=float(st.session_state.get("P0_bar", 5.0)),
        step=0.5,
        help="Pression disponible a l'entree de la conduite (refoulement pompe). "
        "Augmenter si la pression P(x) devient insuffisante en un point.",
    )
    st.session_state["P0_bar"] = P0_bar

    P_secu_bar = st.number_input(
        "Pression de securite P_sec (bar)",
        min_value=0.0, max_value=10.0,
        value=float(st.session_state.get("P_secu_bar", 0.5)),
        step=0.1,
        help="Pression minimale acceptable partout : P_vapeur(0.023 bar) + marge slurry.",
    )
    st.session_state["P_secu_bar"] = P_secu_bar
    
    P_max_bar = st.number_input(
        "Pression maximale PN conduite (bar)",
        min_value=1.0, max_value=100.0,
        value=float(st.session_state.get("P_max_bar", 16.0)),
        step=1.0,
        help="Pression nominale de la tuyauterie (PN 10, PN 16, etc.)",
    )
    st.session_state["P_max_bar"] = P_max_bar


    #===Interpolation sur 500 points pour un tracé lisse===================================
    N = 500
    x_profile = np.linspace(x_pts[0], x_pts[-1], N)
    interp  = PchipInterpolator(x_pts, z_pts) # Pchip évite les ondulations bizarres
    Z_profile = interp(x_profile)
    x_plot   = x_profile - x_profile[0]   # always start at 0


    Z_start = float(Z_profile[0])
    Z_max   = float(np.max(Z_profile))
    Z_end   = float(Z_profile[-1])
    idx_zmax = int(np.argmax(Z_profile))
    
    # === VISUALISATION DU TERRAIN SEUL ===================================
    st.markdown("### ② Profil Topographique du Terrain")
    fig_topo = go.Figure()
    # Terrain rempli
    fig_topo.add_trace(go.Scatter(
        x=x_plot, y=Z_profile,
        name="Terrain interpolé (PCHIP)",
        line=dict(color="#8b949e", width=2),
        fill="tozeroy", 
        fillcolor="rgba(110,118,129,0.15)",
        mode="lines"
    ))
    # Points réels saisis
    fig_topo.add_trace(go.Scatter(
        x=x_pts - x_pts[0], y=z_pts,
        name="Points relevés",
        mode="markers",
        marker=dict(color="#f0a500", size=10, symbol="circle")
    ))
    
    fig_topo.update_layout(
        template="plotly_dark",
        height=350,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title="Distance (m)",
        yaxis_title="Altitude Z (m)",
        showlegend=True
    )                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
    st.plotly_chart(fig_topo, use_container_width=True)

    st.markdown("---")
 
    # ── 3. CALCUL HGL DISCRETE ───────────────
    st.markdown("### 3 · Equation de la Ligne de Charge")

    # Scalar HGL_0
    HGL_0 = Z_start + P0_bar * 1e5 / (rho_m * g)
    J_linear_pur = hf_lin / L

    # Build HGL at each dense x point
    HGL_profile = np.zeros(N)
    for k, xk in enumerate(x_plot):
        # Linear friction loss up to xk
        loss_lin = J_linear_pur * xk
        # Cumulated singular losses for all fittings at positions <= xk
        #x_acc_shifted = xs_acc - x_pts[0]   shift same as x_plot
        loss_sing = float(np.sum(hm_acc[xs_acc <= xk]))
        HGL_profile[k] = HGL_0 - loss_lin - loss_sing

    # Pressure at each point
    P_profile = (HGL_profile - Z_profile) * rho_m * g / 1e5   # bar
    
    st.session_state['p_start_val'] = float(P_profile[0])
    st.session_state['p_final_val'] = float(P_profile[-1])
    st.session_state['Z_start'] = float(Z_profile[0])
    st.session_state['Z_end'] = float(Z_profile[-1])
    
    with st.expander("📊 Consulter le tableau des résultats détaillés (500 points)"):
        # On crée un DataFrame propre pour l'affichage
        df_results = pd.DataFrame({
            "Abscisse x (m)": x_plot,
            "Altitude Z (m)": Z_profile,
            "Charge HGL (m)": HGL_profile,
            "Pression P (bar)": P_profile
        })
        
        # Affichage du tableau (st.dataframe est plus léger que st.table ici)
        st.dataframe(
            df_results,
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Abscisse x (m)": st.column_config.NumberColumn(format="%.1f"),
                "Altitude Z (m)": st.column_config.NumberColumn(format="%.2f"),
                "Charge HGL (m)": st.column_config.NumberColumn(format="%.2f"),
                "Pression P (bar)": st.column_config.NumberColumn(format="%.3f")
            }
        )
        # Option "Ultra-Pro" : Bouton de téléchargement CSV
        csv_data = df_results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger les résultats complets (.csv)",
            data=csv_data,
            file_name='resultats_hgl_pression.csv',
            mime='text/csv',
        )


    st.markdown("---")
    # ── ② GRADIENT LINEAIRE J_linear_pur ─────────────────────────────
    st.markdown("### ② Hydraulic Gradient J_linear_pur")

    col1, col2, col3 = st.columns(3)
    col1.metric("hf lineaire",   f"{hf_lin:.3f} m",  f"{hf_lin/L*1000} m/km")
    col2.metric("h_m singulieres",f"{h_m:.3f} m",  f"{h_m/L*1000:.2f} m/km")
    col3.metric("J_linear_pur (gradient)",  f"{J_linear_pur:.3f} m/m",   f"{J_linear_pur*1000:.3f} m/km")
 

    
    # ── Pression residuelle entre deux points ───────────────
    st.markdown("#### Verification pression residuelle P2 − P1 entre deux abscisses")
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        x1_check = st.number_input(
            "Abscisse x1 (m)", 0.0, float(L),
            value=0.0, step=10.0, key="x1_check")
    with col_r2:
        x2_check = st.number_input(
            "Abscisse x2 (m)", 0.0, float(L),
            value=float(L), step=10.0, key="x2_check")

    # Interpolate P at x1 and x2
    idx1 = int(np.argmin(np.abs(x_plot - x1_check)))
    idx2 = int(np.argmin(np.abs(x_plot - x2_check)))
    z1, z2 = Z_profile[idx1], Z_profile[idx2]


    P_x1 = float(P_profile[idx1])
    P_x2 = float(P_profile[idx2])
    dP   = P_x2 - P_x1
    dz = z2 - z1
    # --- Affichage des résultats sous forme de tableau comparatif ---
    comparison_data = {
        "Paramètre": ["Abscisse (m)", "Altitude Z (m)", "Pression P (bar)"],
        "Point A": [round(x_plot[idx1], 1), round(z1, 2), round(P_x1, 3)],
        "Point B": [round(x_plot[idx2], 1), round(z2, 2), round(P_x2, 3)],
        "Différence (B-A)": [round(x_plot[idx2]-x_plot[idx1], 1), round(dz, 2), round(dP, 3)]
    }
    
    df_diff = pd.DataFrame(comparison_data)
    st.table(df_diff)

    # --- Diagnostic Automatique ---
    if dP > 0:
        st.info(f"📈 **Surpression de {abs(dP):.2f} bar** entre A et B. (L'altitude descend ou la pompe pousse fort)")
    elif dP < 0:
        st.warning(f"📉 **Dépression de {abs(dP):.2f} bar** entre A et B. (Montée ou frottement élevé)")
    else:
        st.write("Équilibre de pression.")

    # Optionnel: Stockage dans un historique de session
    if st.button("💾 Enregistrer cette comparaison"):
        new_entry = {"Point A": x1_check, "Point B": x1_check, "P_A": P_x1, "P_B": P_x2, "Delta_P": dP}
        if 'history_dp' not in st.session_state:
            st.session_state.history_dp = []
        st.session_state.history_dp.append(new_entry)
        st.success("Comparaison ajoutée à l'historique.")

    

    st.markdown("---")

        # ── ④ DECOMPOSITION DES CHARGES (KPIs) ─────────────────
    st.markdown("### ④ Decomposition des Charges")

    dH_statique  = Z_max - Z_start
    dH_dynamique = hf_lin + float(hm_acc.sum())
    dH_total_kpi = dH_statique + dH_dynamique

    P_min_val = float(np.min(P_profile))
    P_max_val = float(np.max(P_profile))
    x_at_Pmin = float(x_plot[np.argmin(P_profile)])
    x_at_Pmax = float(x_plot[np.argmax(P_profile)])

    n_unsafe  = int(np.sum(P_profile < P_secu_bar))
    n_overpr  = int(np.sum(P_profile > P_max_bar))
    safe_ok   = (P_min_val >= P_secu_bar) and (P_max_val <= P_max_bar)

    kpi_cols = st.columns(5)
    kpi_cols[0].metric("ΔZ statique",
                       f"{dH_statique:.2f} m",
                       f"Z_max={Z_max:.1f} − Z0={Z_start:.1f}")
    kpi_cols[1].metric("H_friction (dyn.)",
                       f"{dH_dynamique:.2f} m",
                       f"hf={hf_lin:.2f} + hm={float(hm_acc.sum()):.3f}")
    kpi_cols[2].metric("H_pompe totale",
                       f"{dH_total_kpi:.2f} m",
                       "stat. + dyn.")
    kpi_cols[3].metric("P min rencontree",
                       f"{P_min_val:.3f} bar",
                       f"a x = {x_at_Pmin:.0f} m",
                       delta_color="inverse" if P_min_val < P_secu_bar else "normal")
    kpi_cols[4].metric("P max rencontree",
                       f"{P_max_val:.2f} bar",
                       f"a x = {x_at_Pmax:.0f} m",
                       delta_color="inverse" if P_max_val > P_max_bar else "normal")

    if safe_ok:
        st.markdown(
            '<div class="success-box" style="font-size:.9rem">'
            '✓ SECURITE VALIDEE — P(x) respecte les seuils minimal et maximal sur l\'integralite du trace.'
            '</div>', unsafe_allow_html=True)
    else:
        if P_min_val < P_secu_bar:
            frac = n_unsafe / N * 100
            st.markdown(
                f'<div class="warning-box">⚠ SOUS-PRESSION sur {n_unsafe} points ({frac:.1f}% du trace) — '
                f'P_min = {P_min_val:.3f} bar &lt; P_sec = {P_secu_bar:.2f} bar a x ≈ {x_at_Pmin:.0f} m. '
                f'Action : augmenter P_0 (pression de refoulement pompe) '
                f'ou installer une station de pompage intermediaire vers x = {x_at_Pmin:.0f} m.</div>',
                unsafe_allow_html=True)
        if P_max_val > P_max_bar:
            st.markdown(
                f'<div class="warning-box">⚠ SURPRESSION sur {n_overpr} points — '
                f'P_max = {P_max_val:.2f} bar &gt; PN = {P_max_bar:.0f} bar. '
                f'Verifier la classe PN de la tuyauterie ou installer un limiteur de pression.</div>',
                unsafe_allow_html=True)

    st.markdown("---")

        # ── ⑤ VISUALISATION PLOTLY ─────────────────────────────
    st.markdown("### ⑤ Visualisation — HGL discrete, Terrain Z(x) et Pression P(x)")

    unsafe_mask = P_profile < P_secu_bar
    overpr_mask = P_profile > P_max_bar

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            "Ligne de Charge HGL(x) & Profil Topographique Z(x)",
        ),
    )

    # ── Sous-plot 1 : terrain + HGL ──
    # Terrain rempli
    fig.add_trace(go.Scatter(
        x=x_plot, y=Z_profile,
        name="Profil terrain Z(x)",
        line=dict(color="#8b949e", width=1.8),
        fill="tozeroy", fillcolor="rgba(110,118,129,0.10)",
        mode="lines",
        hovertemplate="x=%{x:.1f} m | Z=%{y:.2f} m<extra>Terrain</extra>",
    ), row=1, col=1)

    # Points de levé
    fig.add_trace(go.Scatter(
        x=x_pts - x_pts[0], y=z_pts,
        name="Points de leve",
        mode="markers",
        marker=dict(color="#f0a500", size=8, symbol="circle-open",
                    line=dict(color="#f0a500", width=2)),
        hovertemplate="x=%{x:.1f} m | Z=%{y:.3f} m<extra>Leve</extra>",
    ), row=1, col=1)

    # HGL sécurisée
    H_ok = np.where(~unsafe_mask, HGL_profile, np.nan)
    fig.add_trace(go.Scatter(
        x=x_plot, y=H_ok,
        name="HGL — pression OK",
        line=dict(color="#00bcd4", width=2.8),
        mode="lines",
        hovertemplate="x=%{x:.1f} m | HGL=%{y:.2f} m<extra>HGL OK</extra>",
    ), row=1, col=1)

    # HGL en zone de sous-pression
    H_bad = np.where(unsafe_mask, HGL_profile, np.nan)
    if np.any(unsafe_mask):
        fig.add_trace(go.Scatter(
            x=x_plot, y=H_bad,
            name="HGL — sous-pression",
            line=dict(color="#f85149", width=2.8, dash="dash"),
            mode="lines",
            hovertemplate="x=%{x:.1f} m | HGL=%{y:.2f} m<extra>SOUS-PRESSION</extra>",
        ), row=1, col=1)

    # Sauts discrets aux accessoires — traits verticaux
    for i_a, (xa, hma, lbl) in enumerate(zip(xs_acc, hm_acc, lbl_acc)):
        idx_a = int(np.argmin(np.abs(x_plot - xa)))
        hgl_before = float(HGL_profile[idx_a])
        hgl_after  = hgl_before - hma
        fig.add_trace(go.Scatter(
            x=[xa, xa],
            y=[hgl_before, hgl_after],
            mode="lines",
            line=dict(color="#f0a500", width=1.5, dash="dot"),
            showlegend=(i_a == 0),
            name="Saut hm_i accessoire" if i_a == 0 else None,
            hovertemplate=f"{lbl}<br>x={xa:.1f} m<br>hm={hma:.4f} m<extra>Singulier</extra>",
        ), row=1, col=1)

    # Symbole accessoire sur la HGL
    hgl_at_acc = []
    for xa in xs_acc:
        idx_a = int(np.argmin(np.abs(x_plot - xa)))
        hgl_at_acc.append(float(HGL_profile[idx_a]))
        # On ajoute les marques sur le graphique
    fig.add_trace(go.Scatter(
        x=xs_acc, y=hgl_at_acc,
        mode="markers",
        marker=dict(color="#f0a500", size=9, symbol="triangle-down",
                    line=dict(color="#0d1117", width=1)),
        name="Position accessoire",
        hovertemplate=[
            f"{lbl}<br>x={xa:.1f} m<br>perte local={h:.3f}<extra></extra>"
            for lbl, xa, h in zip(lbl_acc, xs_acc, hm_acc)
        ],
    ), row=1, col=1)

    # Annotation gradient Jm
    xm = float(x_plot[N//3])
    ym = float(HGL_profile[N//3])
    fig.add_annotation(
        x=xm, y=ym + 1.5,
        text=f"Jm = {J_linear_pur*1000:.2f} m/km",
        font=dict(color="#00bcd4", family="Share Tech Mono", size=10),
        bgcolor="rgba(13,17,23,0.75)",
        showarrow=True, arrowhead=1, arrowcolor="#00bcd4",
        row=1, col=1,
    )

    # Annotation Z_max
    fig.add_annotation(
        x=float(x_plot[idx_zmax]), y=Z_max + 1.2,
        text=f"Z_max = {Z_max:.1f} m",
        font=dict(color="#f0a500", family="Share Tech Mono", size=9),
        bgcolor="rgba(13,17,23,0.75)",
        showarrow=True, arrowhead=1, arrowcolor="#f0a500",
        row=1, col=1,
    )
    fig.update_layout(
        template="plotly_dark", 
        height=500,               # Hauteur optimisée pour un seul graphique
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10, family="Share Tech Mono"),
            orientation="h", x=0, y=-0.15,
        ),
    )

    # Nettoyage des titres d'axes pour le graphique restant
    fig.update_yaxes(
        title_text="Cote / Charge HGL (m)", 
        row=1, col=1,
        gridcolor="#21262d", 
        linecolor="#30363d"
    )
    fig.update_xaxes(
        title_text="Abscisse x (m)", 
        row=1, col=1,
        gridcolor="#21262d", 
        linecolor="#30363d"
    )

    # Affichage final dans Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    

    col_a, _, col_c = st.columns([1, 2, 1])
    with col_a:
        if st.button("← BACK"):
            st.session_state.current_step = 4
            st.rerun()
    with col_c:
        if st.button("SAVE & CONTINUE →", use_container_width=True, type="primary"):
            # Sauvegarde finale pour les calculs de pompes du Step 5
            st.session_state.hf_singular = h_m
            st.session_state.h_total = h_total
            st.session_state.step4_done = True
            st.session_state.current_step = 6
            st.rerun()


#==============================================
#STEP 6 : Pump Power
#================================================

def render_step6():
    step_badge(6, "Pump Power")


    # --- 1. RÉCUPÉRATION DES DONNÉES PRÉCÉDENTES ---
    # On récupère les valeurs calculées à l'étape 4 (ou valeurs par défaut pour test)
    h_linear = st.session_state.get('hf_linear')
    h_m = st.session_state.get('h_m')
    h_total = st.session_state.get('h_total')
    rho_m = st.session_state.get('rho_m')
    Q = st.session_state.get('Q') # en m3/h
    HMT = st.session_state.get('HMT')
    
    p_start_val = st.session_state['p_start_val'] 
    p_final_val = st.session_state['p_final_val'] 
    Z_start = st.session_state['Z_start'] 
    Z_end = st.session_state['Z_end'] 
    
    st.markdown("### 📍 Conditions aux extrémités")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1: st.metric("Altitude Départ", f"{Z_start:.2f} m")
    with col2: st.metric("Pression Départ", f"{p_start_val:.3f} bar", delta="x = 0")
    with col3: st.metric("Altitude Arrivée", f"{Z_end:.2f} m")
    with col4:
        delta_color = "normal" if p_final_val > 0 else "inverse"
        st.metric("Pression Arrivée", f"{p_final_val:.3f} bar", delta="x = L", delta_color=delta_color)
    if p_final_val < 0.2:
        st.warning(f"⚠️ **Attention :** La pression à l'arrivée ({p_final_val:.3f} bar) est très faible ou négative. Risque de bouchage ou d'arrêt du flux.")

    st.info(f"💾 **Données de l'étude :** Débit = {Q} m³/h | HMT = {h_total:.2f} m | Densité = {rho_m} kg/m³")

    st.markdown("---")

    # --- 2. SAISIE DES RENDEMENTS ---
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        st.subheader("⚙️ Rendements")
        eta_pump = st.slider("Rendement de la pompe (η_pompe)", 0.10, 0.95, 0.75, 0.05, 
                             help="Efficacité hydraulique de la pompe choisie.")
        eta_motor = st.slider("Rendement du moteur (η_moteur)", 0.50, 0.98, 0.90, 0.01,
                              help="Efficacité électrique du moteur (IE2, IE3, etc.).")

    with col_input2:
        st.subheader("🛡️ Sécurité")
        safety_factor = st.number_input("Marge de sécurité (%)", 0, 50, 15) / 100
        st.caption("Ajoute une marge de puissance pour éviter les surcharges moteur.")

    # --- 3. CALCULS (Utilisation de vos fonctions moteur) ---
    # Calcul de la puissance hydraulique
    HMT = calculer_HMT_physique(hf_linear, h_m, Z_start, Z_end, p_final_bar, rho_m)
    p_hyd_kw = pump_hydraulic_power(rho_m, 9.81, Q, h_total)
    
    # Calcul de la puissance à l'arbre
    p_shaft_kw = pump_shaft_power(p_hyd_kw, eta_pump)
    
    # Calcul de la puissance électrique absorbée mensuelle
    p_elec_kw = motor_power(p_shaft_kw, eta_motor)
    
    # Puissance moteur recommandée avec marge
    p_recommended = p_elec_kw * (1 + safety_factor)

    # --- 4. AFFICHAGE DES RÉSULTATS ---
    st.markdown("### 📊 Résultats des Puissances")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric(label="Puissance Hydraulique", value=f"{p_hyd_kw:.2f} kW")
        st.caption("Puissance nette de l'eau")

    with c2:
        st.metric(label="Puissance à l'Arbre", value=f"{p_shaft_kw:.2f} kW")
        st.caption("Puissance mécanique requise")

    with c3:
        st.metric(label="Puissance Électrique", value=f"{p_elec_kw:.2f} kW")
        st.caption("Consommation réseau")

    # Mise en évidence du choix du moteur
    st.success(f"✅ **Puissance moteur suggérée : {p_recommended:.2f} kW**")
    
    # Aide au choix du moteur de catalogue
    standard_motors = [0.37, 0.55, 0.75, 1.1, 1.5, 2.2, 3, 4, 5.5, 7.5, 11, 15, 18.5, 22, 30, 37, 45, 55, 75]
    closest_motor = min([m for m in standard_motors if m >= p_recommended] or [max(standard_motors)])
    
    st.write(f"👉 Prochain moteur standard disponible : **{closest_motor} kW**")

    # --- 5. NAVIGATION ---
    st.markdown("---")
    col_a, _, col_c = st.columns([1, 2, 1])
    with col_a:
        if st.button("← RETOUR HGL"):
            st.session_state.current_step = 4
            st.rerun()
    with col_c:
        if st.button("TERMINER L'ÉTUDE ✅"):
            st.session_state.p_final = p_recommended
            st.balloons()
            # Logique pour générer le rapport PDF par exemple

# À rajouter tout à la fin du fichier
if st.session_state.current_step == 1:
    render_step1()
elif st.session_state.current_step == 2:
    render_step2()
elif st.session_state.current_step == 3:
    render_step3()
elif st.session_state.current_step == 4:
    render_step4()
elif st.session_state.current_step == 5:
    render_step5()
elif st.session_state.current_step == 6:
    render_step6()
