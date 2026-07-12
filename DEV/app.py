"""Premium Data Analysis Platform - Streamlit Web UI.

Integrates custom dark glassmorphic layouts, smart fleet log autodetection,
high-end metric tiles, customized Plotly visual outputs, and advanced export bundles.
"""

from __future__ import annotations

import base64
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.chart_engine import generate_all_charts, generate_fleet_charts
from src.column_profiler import profile_dataframe
from src.data_cleaner import clean_dataframe
from src.data_loader import load_from_upload
from src.export_service import create_export_zip, figure_to_html, figure_to_png, generate_fleet_text_report
from src.fleet_analyzer import is_fleet_dataframe, analyze_fleet_data

def render_custom_html(html_content: str):
    """Renders custom HTML/CSS safely without triggering Markdown indented code block parsing."""
    clean_html = "\n".join([line.strip() for line in html_content.splitlines() if line.strip()])
    st.markdown(clean_html, unsafe_allow_html=True)

def get_login_bg_base64() -> str:
    """Carrega a imagem de fundo e retorna como string Base64 para injeção CSS."""
    img_path = ROOT / "assets" / "loguin_fundo.png"
    if img_path.exists():
        try:
            with open(img_path, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
        except Exception:
            pass
    return ""

# ------------------------------------------------------------
# CONFIGURAÇÕES GLOBAIS DE ACESSO E SEGURANÇA
# ------------------------------------------------------------
ENABLE_LOGIN = True        # Defina como False ou True para ativar a tela de login restrito
LOGIN_USER = "admin"
LOGIN_PASS = "frota2026"

# Page configuration with premium layout
st.set_page_config(
    page_title="Plataforma de Análise de Dados",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Slate & Neon Dark Glassmorphism CSS injection
st.markdown(
    """
    <style>
    /* Premium Dark Slate Background */
    [data-testid="stAppViewContainer"] {
        background-color: #0F172A;
        color: #F8FAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Clean Sidebar */
    [data-testid="stSidebar"] {
        background-color: #090D1A;
        border-right: 1px solid #1E293B;
    }
    
    /* Hide native Streamlit headers and footers for stand-alone feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tab Styling Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(15, 23, 42, 0.8);
        padding: 6px 12px;
        border-radius: 10px;
        border: 1px solid #1E293B;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94A3B8 !important;
        font-weight: 600;
        background-color: transparent;
        border-radius: 6px;
        padding: 6px 16px;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        color: #F8FAFC !important;
        background-color: #1E293B !important;
        border-bottom: 2px solid #3B82F6 !important;
    }
    
    /* KPI Card Matrix Styling */
    .kpi-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1.2rem;
        margin-bottom: 2rem;
        width: 100%;
    }
    .kpi-card {
        flex: 1 1 200px;
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
    }
    .kpi-card.blue { border-left: 4px solid #3B82F6; border-right: 1px solid rgba(59, 130, 246, 0.2); }
    .kpi-card.green { border-left: 4px solid #10B981; border-right: 1px solid rgba(16, 185, 129, 0.2); }
    .kpi-card.red { border-left: 4px solid #EF4444; border-right: 1px solid rgba(239, 68, 68, 0.2); }
    .kpi-card.orange { border-left: 4px solid #F59E0B; border-right: 1px solid rgba(245, 158, 11, 0.2); }
    
    .kpi-title {
        font-size: 0.75rem;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-size: 2.1rem;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.1;
    }
    .kpi-desc {
        font-size: 0.72rem;
        color: #64748B;
        margin-top: 0.3rem;
    }
    
    /* Styled Info Cards */
    .anomaly-row {
        background: rgba(30, 41, 59, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }
    .anomaly-row:hover {
        background: rgba(30, 41, 59, 0.5);
        border-color: rgba(239, 68, 68, 0.3);
    }
    
    /* Badges */
    .badge {
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge.critica {
        background-color: rgba(239, 68, 68, 0.15);
        color: #FCA5A5;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .badge.alta {
        background-color: rgba(245, 158, 11, 0.15);
        color: #FDE047;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    /* Title area styling */
    .title-area {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.6) 100%);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# SECURITY & AUTHENTICATION (PREMIUM INTEGRATED LOGIN SYSTEM)
# ------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Auto-login se a segurança estiver globalmente desativada
if not ENABLE_LOGIN:
    st.session_state.authenticated = True

# Sincronização automática pós-refresh (F5) usando query parameters
if st.query_params.get("auth") == "true":
    st.session_state.authenticated = True

if ENABLE_LOGIN and not st.session_state.authenticated:
    bg_base64 = get_login_bg_base64()
    
    # Render layout elements (Logo and anti-inspect script)
    render_custom_html(
        f"""<div style="text-align: center; margin-bottom: 2rem; animation: fadeInLogo 1.2s ease-out forwards;">
    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="url(#blueGrad)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0 0 15px rgba(0, 198, 255, 0.5)); margin-bottom: 16px; animation: pulseLock 2s infinite ease-in-out;">
        <defs>
            <linearGradient id="blueGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#00C6FF" />
                <stop offset="100%" stop-color="#0052D4" />
            </linearGradient>
        </defs>
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
        <circle cx="12" cy="16" r="1.5"></circle>
    </svg>
    <h2 style="margin: 5px 0; font-size: 1.85rem; font-weight: 900; background: linear-gradient(90deg, #FFFFFF, #00C6FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-family: 'Inter', sans-serif; letter-spacing: 0.1em; text-transform: uppercase;">
        F2M Analytics
    </h2>
    <p style="margin: 0; color: #7DD3FC; font-size: 0.78rem; font-family: 'Inter', sans-serif; letter-spacing: 0.08em; font-weight: 600; text-transform: uppercase; opacity: 0.85;">
        Plataforma de Inteligência Operacional
    </p>
</div>

<script>
// 1. Limpeza de listeners de refresh ao carregar a tela de login
try {{
    const parentWin = window.parent;
    let isSame = false;
    try {{ isSame = !!parentWin.location.href; }} catch(e) {{}}
    const targetWin = isSame ? parentWin : window;
    
    if (targetWin.hasAntiRefresh) {{
        targetWin.removeEventListener('keydown', targetWin.antiRefreshKeydown);
        targetWin.removeEventListener('beforeunload', targetWin.antiRefreshBeforeUnload);
        targetWin.hasAntiRefresh = false;
    }}
}} catch(e) {{}}

// 2. Proteção Anti-Inspect Global no Cliente
(function() {{
    try {{
        const parentWin = window.parent;
        const windowsToProtect = [window, parentWin];
        const alertMessage = "🔒 Acesso protegido! Esta plataforma opera sob políticas de segurança de dados de frota.";

        const preventContextMenu = function(e) {{
            e.preventDefault();
            return false;
        }};

        const preventInspectKeys = function(e) {{
            if (e.key === 'F12' || e.keyCode === 123) {{
                e.preventDefault();
                alert(alertMessage);
                return false;
            }}
            if ((e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'i' || e.keyCode === 73)) || 
                (e.metaKey && e.altKey && (e.key === 'I' || e.key === 'i' || e.keyCode === 73))) {{
                e.preventDefault();
                alert(alertMessage);
                return false;
            }}
            if ((e.ctrlKey && e.shiftKey && (e.key === 'J' || e.key === 'j' || e.keyCode === 74)) || 
                (e.metaKey && e.altKey && (e.key === 'J' || e.key === 'j' || e.keyCode === 74))) {{
                e.preventDefault();
                alert(alertMessage);
                return false;
            }}
            if ((e.ctrlKey && (e.key === 'U' || e.key === 'u' || e.keyCode === 85)) || 
                (e.metaKey && e.altKey && (e.key === 'U' || e.key === 'u' || e.keyCode === 85))) {{
                e.preventDefault();
                alert(alertMessage);
                return false;
            }}
            if (e.ctrlKey && e.shiftKey && (e.key === 'C' || e.key === 'c' || e.keyCode === 67)) {{
                e.preventDefault();
                alert(alertMessage);
                return false;
            }}
        }};

        windowsToProtect.forEach(w => {{
            if (w) {{
                let isSame = false;
                try {{ isSame = (w === window) || !!w.location.href; }} catch(e) {{}}
                if (isSame) {{
                    w.document.addEventListener('contextmenu', preventContextMenu, true);
                    w.addEventListener('keydown', preventInspectKeys, true);
                }}
            }}
        }});
    }} catch(err) {{}}
}})();
</script>

<style>
/* Reset de backgrounds para expor a imagem de fundo */
[data-testid="stAppViewContainer"] {{
    background-image: url('{bg_base64}') !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
    background-color: #020b18 !important; /* Fallback em cor escura */
    transition: background-image 0.5s ease-in-out !important;
}}

[data-testid="stMain"] {{
    background: transparent !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-height: 100vh !important;
    padding: 0 !important;
}}

/* Ocultar barra lateral e cabeçalho na tela de login */
[data-testid="stSidebar"], header, [data-testid="stHeader"] {{
    display: none !important;
}}

/* Painel de Login centralizado com Glassmorphism Premium */
div.block-container {{
    background: rgba(10, 25, 47, 0.18) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 20px !important;
    padding: 3rem 2.5rem !important;
    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.45), inset 0 1px 1px rgba(255, 255, 255, 0.15) !important;
    width: 420px !important;
    max-width: 90vw !important;
    margin: 0 !important; /* Removido margem superior fixa */
    animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}}

@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes pulseLock {{
    0%, 100% {{ filter: drop-shadow(0 0 10px rgba(0, 198, 255, 0.4)); transform: scale(1); }}
    50% {{ filter: drop-shadow(0 0 20px rgba(0, 198, 255, 0.7)); transform: scale(1.05); }}
}}

@keyframes fadeInLogo {{
    from {{ opacity: 0; transform: scale(0.96); }}
    to {{ opacity: 1; transform: scale(1); }}
}}

/* Rótulos de inputs */
div[data-testid="stTextInput"] label {{
    color: rgba(255, 255, 255, 0.9) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em !important;
    margin-bottom: 6px !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.4);
}}

/* Customização dos Inputs */
div[data-testid="stTextInput"] input {{
    background-color: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
    font-size: 0.95rem !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1) !important;
}}

div[data-testid="stTextInput"] input::placeholder {{
    color: rgba(125, 211, 252, 0.7) !important; /* Azul claro suave */
}}

div[data-testid="stTextInput"] input:focus {{
    border-color: #38BDF8 !important; /* Glow azul */
    background-color: rgba(255, 255, 255, 0.07) !important;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.45), inset 0 1px 2px rgba(0, 0, 0, 0.1) !important;
}}

/* Botão de Login com Gradiente Premium e Elevação */
button[kind="primary"] {{
    background: linear-gradient(135deg, #0052d4 0%, #00c6ff 100%) !important;
    border: none !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    padding: 14px 28px !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    text-transform: uppercase;
    box-shadow: 0 0 20px rgba(0, 198, 255, 0.45), 0 4px 12px rgba(0, 82, 212, 0.3) !important;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
}}

button[kind="primary"]:hover {{
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 0 25px rgba(0, 198, 255, 0.65), 0 6px 18px rgba(0, 82, 212, 0.45) !important;
}}

button[kind="primary"]:active {{
    transform: translateY(-1px) scale(0.99) !important;
}}

/* Estilização suave de alertas (error/success) estilo glass */
div[data-testid="stAlert"] {{
    border-radius: 10px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
    margin-top: 15px !important;
}}

/* Responsividade Mobile */
@media (max-width: 480px) {{
    div.block-container {{
        padding: 2rem 1.5rem !important;
        border-radius: 16px !important;
    }}
}}
</style>"""
    )
    
    username = st.text_input("Usuário", placeholder="Nome de usuário", key="user_val")
    password = st.text_input("Senha", type="password", placeholder="Sua senha secreta", key="pass_val")
    st.write("")
    login_btn = st.button("Entrar no Painel ➔", type="primary", use_container_width=True)
    
    if login_btn:
        if username == LOGIN_USER and password == LOGIN_PASS:
            st.session_state.authenticated = True
            st.query_params["auth"] = "true"  # Persistir estado
            st.success("Autenticação bem-sucedida! Carregando...")
            st.rerun()
        else:
            st.error("Credenciais inválidas. Tente novamente.")
            
    st.stop()

# Header Title Block
render_custom_html(
    """
    <div class="title-area">
        <h1 style="margin: 0; padding: 0; font-size: 2.2rem; font-weight: 800; background: linear-gradient(90deg, #F8FAFC, #3B82F6, #10B981); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            📊 Plataforma de Análise de Dados
        </h1>
        <p style="margin: 6px 0 0 0; padding: 0; color: #94A3B8; font-size: 0.95rem;">
            Upload inteligente de planilhas · Gráficos interativos Slate & Neon · Auditoria Operacional de Frota · Power BI Integrado
        </p>
    </div>
    """
)

# Sidebar Configuration
with st.sidebar:
    st.markdown("<h3 style='margin-bottom: 15px; color: #F8FAFC;'>⚙️ Ajustes Globais</h3>", unsafe_allow_html=True)
    max_charts = 10  # Limite fixo e otimizado internamente, removendo slider secundário da UI
    export_html = st.checkbox("Incluir HTML interativo no ZIP", value=True)
    export_png = st.checkbox("Incluir PNG estático no ZIP", value=True)
    st.divider()
    
    st.markdown(
        """
        <div style="background-color: rgba(30, 41, 59, 0.3); border: 1px solid #1E293B; border-radius: 8px; padding: 12px; font-size: 0.8rem; color: #94A3B8;">
            <b>🤖 Detector Inteligente Ativo</b><br>
            A plataforma analisa a planilha e seleciona automaticamente entre:<br>
            1. 🚚 <b>Inteligência de Frota:</b> Se houver dados operacionais de ciclos.<br>
            2. 📊 <b>Explorador Geral:</b> Para qualquer outra planilha comercial/operacional.
        </div>
        """,
        unsafe_allow_html=True,
    )
    if ENABLE_LOGIN:
        st.divider()
        if st.button("🚪 Encerrar Sessão", use_container_width=True, help="Deslogar da plataforma com segurança."):
            st.session_state.authenticated = False
            st.query_params.clear()  # Clear auth state on logout
            st.rerun()

# Session state initialization
if "df_clean" not in st.session_state:
    st.session_state.df_clean = None
    st.session_state.charts = []
    st.session_state.profile = None
    st.session_state.fleet_analysis = None
    st.session_state.is_fleet = False
    st.session_state.filename = ""

# Spreadsheet Upload
uploaded = st.file_uploader(
    "Arraste ou selecione sua planilha (CSV ou Excel)",
    type=["csv", "xlsx", "xls"],
    help="Compatível com arquivos locais de movimento de frota (Excel/CSV) e planilhas gerais de vendas, RH ou ERP.",
)

# Process file on upload
if uploaded:
    # Reset state if a new file is uploaded
    if st.session_state.filename != uploaded.name:
        st.session_state.df_clean = None
        st.session_state.charts = []
        st.session_state.profile = None
        st.session_state.fleet_analysis = None
        st.session_state.is_fleet = False
        st.session_state.filename = uploaded.name

    if st.session_state.df_clean is None:
        try:
            with st.spinner("Decodificando, limpando e analisando dados..."):
                df_raw = load_from_upload(uploaded, uploaded.name)
                df_clean = clean_dataframe(df_raw)
                
                # Check for specialized fleet column signatures
                is_fleet = is_fleet_dataframe(df_clean)
                st.session_state.is_fleet = is_fleet
                
                if is_fleet:
                    # Run deep fleet investigation
                    fleet_analysis = analyze_fleet_data(df_clean)
                    st.session_state.fleet_analysis = fleet_analysis
                    st.session_state.df_clean = fleet_analysis["processed_df"]
                    st.session_state.charts = generate_fleet_charts(st.session_state.df_clean)
                    st.session_state.profile = None
                else:
                    # Run generic profile explorer
                    profile = profile_dataframe(df_clean)
                    st.session_state.profile = profile
                    st.session_state.df_clean = df_clean
                    st.session_state.charts = generate_all_charts(df_clean, profile)[:max_charts]
                    st.session_state.fleet_analysis = None
                
            st.success(
                f"✅ Carregamento bem-sucedido: **{uploaded.name}** — "
                f"{len(st.session_state.df_clean):,} linhas × {len(st.session_state.df_clean.columns)} colunas".replace(",", ".")
            )
        except Exception as exc:
            st.error(f"Erro ao processar planilha: {exc}")

# Active state variables
df = st.session_state.df_clean
charts = st.session_state.charts
profile = st.session_state.profile
fleet_analysis = st.session_state.fleet_analysis
is_fleet = st.session_state.is_fleet

if df is not None:
    # Obter o nome do arquivo de forma segura a partir do estado da sessão
    uploaded_name = st.session_state.get("filename", "dados") or "dados"
    base_name = uploaded_name.split('.')[0] if '.' in uploaded_name else uploaded_name
    # Injeção JavaScript de segurança para interceptar recarregamento de página acidental (F5/Ctrl+R/beforeunload)
    import streamlit.components.v1 as components
    components.html(
        """
        <script>
        try {
            const parentWin = window.parent;
            
            // Verificar Same-Origin de forma segura para evitar erros CORS
            let isSame = false;
            try {
                isSame = !!parentWin.location.href;
            } catch (e) {
                isSame = false;
            }
            
            const targetWin = isSame ? parentWin : window;
            
            // Evita múltiplas adições de escuta no ciclo de rerun do Streamlit
            if (!targetWin.hasAntiRefresh) {
                targetWin.hasAntiRefresh = true;
                
                // Função para interceptar teclas físicas de recarga (F5, Ctrl+R, Cmd+R)
                targetWin.antiRefreshKeydown = function(e) {
                    if (e.key === 'F5' || 
                        (e.ctrlKey && (e.key === 'r' || e.key === 'R')) || 
                        (e.metaKey && (e.key === 'r' || e.key === 'R'))) {
                        
                        e.preventDefault();
                        
                        const msg = "DESEJA REALMENTE ALTERAR A PAGINA?\\n\\nTODOS OS DADOS SERÃO PERDIDOS E SERA NECESSARIO LOGAR NOVAMENTE.\\n\\nMAS É SO SUBIR OUTRA BASE DE DADOS.";
                        if (targetWin.confirm(msg)) {
                            targetWin.removeEventListener('keydown', targetWin.antiRefreshKeydown);
                            targetWin.removeEventListener('beforeunload', targetWin.antiRefreshBeforeUnload);
                            targetWin.hasAntiRefresh = false;
                            targetWin.location.reload();
                        }
                    }
                };
                
                // Função para capturar fechamento acidental de aba ou clique no botão de recarregar do navegador
                targetWin.antiRefreshBeforeUnload = function(e) {
                    e.preventDefault();
                    e.returnValue = 'DESEJA REALMENTE ALTERAR A PAGINA? TODOS OS DADOS SERÃO PERDIDOS E SERA NECESSARIO LOGAR NOVAMENTE. MAS É SO SUBIR OUTRA BASE DE DADOS.';
                    return e.returnValue;
                };
                
                targetWin.addEventListener('keydown', targetWin.antiRefreshKeydown);
                targetWin.addEventListener('beforeunload', targetWin.antiRefreshBeforeUnload);
            }
        } catch (err) {
            console.warn("Segurança do frame limitada ao tentar injetar listeners de refresh:", err);
        }
        </script>
        """,
        height=0,
        width=0,
    )
    # ------------------------------------------------------------
    # SPECIALIZED MODE: FLEET OPERATIONAL AUDIT & ANALYSIS
    # ------------------------------------------------------------
    if is_fleet and fleet_analysis:
        summary = fleet_analysis["summary"]
        etapas_stats = fleet_analysis["etapas_stats"]
        rankings = fleet_analysis["operators_ranking"]
        anom_counts = fleet_analysis["anomaly_counts"]
        anom_events = fleet_analysis["anomalous_events"]

        st.markdown(
            f"""
            <div style="background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 10px; margin-bottom: 20px; font-weight: 600; color: #A7F3D0; font-size: 0.9rem; text-align: center;">
                🚚 MÓDULO ATIVO: Inteligência de Frota & Análise de Anomalias de Apontamento
            </div>
            """,
            unsafe_allow_html=True
        )

        tab_dash, tab_graficos, tab_auditoria, tab_dados, tab_export = st.tabs([
            "🖥️ Painel Operacional",
            "📊 Dashboard Interativo",
            "🚨 Auditoria de Anomalias",
            "📋 Dados Limpos",
            "💾 Exportar Relatórios & Power BI"
        ])

        # TAB 1: Painel Operacional (KPI tiles + rankings)
        with tab_dash:
            st.markdown("### 📈 Indicadores de Performance (KPIs)")
            
            # HTML Row of custom metrics
            ok_desc = f"{summary['ok_cycles']:,} ciclos perfeitos".replace(",", ".")
            err_desc = f"{summary['error_cycles']:,} ciclos com falhas".replace(",", ".")
            gps_desc = f"{anom_counts['gps_coords_zero']} apontamentos zerados"
            
            st.markdown(
                f"""
                <div class="kpi-container">
                    <div class="kpi-card blue">
                        <div class="kpi-title">Volume Total</div>
                        <div class="kpi-value">{summary['total_cycles']:,}</div>
                        <div class="kpi-desc">Ciclos operacionais processados</div>
                    </div>
                    <div class="kpi-card green">
                        <div class="kpi-title">Confiabilidade</div>
                        <div class="kpi-value">{summary['reliability_rate']:.1f}%</div>
                        <div class="kpi-desc">{ok_desc}</div>
                    </div>
                    <div class="kpi-card red">
                        <div class="kpi-title">Inconsistência</div>
                        <div class="kpi-value">{summary['inconsistency_rate']:.1f}%</div>
                        <div class="kpi-desc">{err_desc}</div>
                    </div>
                    <div class="kpi-card orange">
                        <div class="kpi-title">Perda de GPS</div>
                        <div class="kpi-value">{summary['gps_loss_rate']:.1f}%</div>
                        <div class="kpi-desc">{gps_desc}</div>
                    </div>
                </div>
                """.replace(",", "."),
                unsafe_allow_html=True
            )

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 🚚 Distribuição de Ciclos e Automação")
                st.write("")
                # Show neat bars for cycle types
                total = summary['total_cycles']
                if total > 0:
                    auto_p = (summary['auto_100_percent'] / total) * 100
                    manual_p = (summary['manual_100_percent'] / total) * 100
                    mixed_p = (summary['mixed_cycles'] / total) * 100
                else:
                    auto_p = manual_p = mixed_p = 0
                
                st.markdown(
                    f"""
                    <div style="background-color: rgba(30, 41, 59, 0.25); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 20px;">
                        <p style="margin: 0 0 5px 0; font-size: 0.85rem; color: #94A3B8;">Apontamentos 100% Automáticos: <b>{summary['auto_100_percent']}</b> ({auto_p:.1f}%)</p>
                        <div style="background-color: #1E293B; border-radius: 4px; height: 10px; width: 100%; margin-bottom: 15px; overflow: hidden;">
                            <div style="background-color: #10B981; height: 100%; width: {auto_p}%;"></div>
                        </div>
                        <p style="margin: 0 0 5px 0; font-size: 0.85rem; color: #94A3B8;">Intervenções Parciais (Ciclos Mistos): <b>{summary['mixed_cycles']}</b> ({mixed_p:.1f}%)</p>
                        <div style="background-color: #1E293B; border-radius: 4px; height: 10px; width: 100%; margin-bottom: 15px; overflow: hidden;">
                            <div style="background-color: #F59E0B; height: 100%; width: {mixed_p}%;"></div>
                        </div>
                        <p style="margin: 0 0 5px 0; font-size: 0.85rem; color: #94A3B8;">Apontamentos Completamente Manuais: <b>{summary['manual_100_percent']}</b> ({manual_p:.1f}%)</p>
                        <div style="background-color: #1E293B; border-radius: 4px; height: 10px; width: 100%; overflow: hidden;">
                            <div style="background-color: #EF4444; height: 100%; width: {manual_p}%;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            with col2:
                st.markdown("#### 🏆 Ranking de Adesão dos Operadores")
                sub1, sub2 = st.tabs(["🚀 Top Automático", "⚠️ Maior Uso do Manual"])
                with sub1:
                    for i, op in enumerate(rankings["top_auto"], 1):
                        st.markdown(
                            f"""
                            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding: 6px 0; font-size: 0.85rem;">
                                <span>🏆 <b>{i}. {op['operator']}</b> <span style='color: #64748B;'>({op['truck']} - Turma: {op.get('turma', 'N/A')})</span></span>
                                <span style='color: #10B981; font-weight: 700;'>{op['cycles']} ciclos auto</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    if not rankings["top_auto"]:
                        st.info("Nenhuma ocorrência registrada.")
                with sub2:
                    for i, op in enumerate(rankings["top_manual"], 1):
                        st.markdown(
                            f"""
                            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding: 6px 0; font-size: 0.85rem;">
                                <span>⚠️ <b>{i}. {op['operator']}</b> <span style='color: #64748B;'>({op['truck']} - Turma: {op.get('turma', 'N/A')})</span></span>
                                <span style='color: #EF4444; font-weight: 700;'>{op['cycles']} ciclos manuais</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    if not rankings["top_manual"]:
                        st.info("Nenhuma ocorrência registrada.")

        # TAB 2: Dashboard de Gráficos (Power BI)
        with tab_graficos:
            st.markdown("### 📊 Dashboard de Gráficos (Estilo Power BI)")
            
            # Row 1: Pizza + Grouped Bar
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(charts[0].figure, use_container_width=True)
            with c2:
                st.plotly_chart(charts[1].figure, use_container_width=True)
                
            st.divider()
            
            # Row 2: Quality metric + Truck volume
            c3, c4 = st.columns(2)
            with c3:
                st.plotly_chart(charts[2].figure, use_container_width=True)
            with c4:
                st.plotly_chart(charts[3].figure, use_container_width=True)
                
            st.divider()
            
            # Row 3: Destination volume
            st.plotly_chart(charts[4].figure, use_container_width=True)

            # Export options for charts
            st.markdown("#### 📂 Exportar Gráficos Individuais")
            cols = st.columns(5)
            for idx, chart in enumerate(charts):
                with cols[idx]:
                    st.caption(f"**{idx+1}. {chart.title}**")
                    html_snippet = figure_to_html(chart.figure)
                    st.download_button(
                        "Baixar HTML",
                        data=html_snippet,
                        file_name=f"{chart.chart_id}.html",
                        mime="text/html",
                        key=f"html_dl_{chart.chart_id}"
                    )
                    try:
                        png_bytes = figure_to_png(chart.figure)
                        st.download_button(
                            "Baixar PNG",
                            data=png_bytes,
                            file_name=f"{chart.chart_id}.png",
                            mime="image/png",
                            key=f"png_dl_{chart.chart_id}"
                        )
                    except Exception:
                        pass

        # TAB 3: Auditoria & Eventos Críticos
        with tab_auditoria:
            st.markdown("### 🚨 Auditoria Operacional - Eventos Críticos (Severidade ALTA/CRÍTICA)")
            st.write("Abaixo estão listadas as ocorrências que requerem atenção da equipe de manutenção ou supervisão:")
            
            if not anom_events:
                st.success("✅ Nenhuma anomalia de alta severidade identificada nos ciclos analisados!")
            else:
                # Add simple paging or show top 20
                for idx, ev in enumerate(anom_events[:20], 1):
                    badge_class = "critica" if ev["severity"] == "CRÍTICA" else "alta"
                    st.markdown(
                        f"""
                        <div class="anomaly-row">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span>
                                    <span class="badge {badge_class}">{ev['severity']}</span>
                                    <span style="font-weight: 700; margin-left: 10px; font-size: 0.95rem; color: #F8FAFC;">Caminhão {ev['truck']}</span>
                                    <span style="color: #64748B; font-size: 0.85rem; margin-left: 6px;">| Operador: {ev['operator']}</span>
                                </span>
                                <span style="color: #94A3B8; font-size: 0.8rem; font-weight: 500;">⏱️ {ev['date']} {ev['time_start']}</span>
                            </div>
                            <div style="font-size: 0.85rem; color: #CBD5E1; margin-bottom: 6px;">
                                <b>Hipótese da Anomalia:</b> <span style="color: #F87171;">{ev['hypothesis']}</span>
                            </div>
                            <div style="font-size: 0.8rem; color: #94A3B8; display: flex; flex-wrap: wrap; gap: 15px;">
                                <span><b>Trajeto:</b> {ev['origin']} ➔ {ev['destination']}</span>
                                <span><b>Basculamento:</b> {ev['time_basculamento']:.1f} min</span>
                                <span><b>Distância:</b> {ev['distance']:.1f} m</span>
                                <span><b>Coordenadas:</b> {ev['latitude']}, {ev['longitude']}</span>
                            </div>
                            <div style="margin-top: 8px; font-size: 0.8rem;">
                                🗺️ <b>Trajeto GPS:</b> <a href="{ev['gps_link']}" target="_blank" style="color: #3B82F6; text-decoration: none; font-weight: 600;">Abrir no Google Maps ➔</a>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                if len(anom_events) > 20:
                    st.caption(f"Mostrando as top 20 ocorrências críticas de um total de {len(anom_events)}.")

        # TAB 4: Dados Limpos
        with tab_dados:
            st.markdown("### 📋 Visualização de Dados Limpos")
            st.write("Colunas numéricas e de data normalizadas de acordo com o padrão internacional.")
            st.dataframe(df.head(100), use_container_width=True)

        # TAB 5: Exportação
        with tab_export:
            st.markdown("### 💾 Baixar Relatórios & Pacotes Corporativos")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 📄 Relatório Master de Frota (Texto)")
                st.write("Gera o arquivo de texto investigativo completo formatado com o sumário de anomalias, severidades e hipóteses de falha operacional.")
                report_text = generate_fleet_text_report(fleet_analysis)
                st.download_button(
                    "Baixar Relatório Investigativo (.txt)",
                    data=report_text,
                    file_name=f"RELATORIO_MASTER_AUDITORIA_{base_name}.txt",
                    mime="text/plain",
                    type="primary"
                )
                
                with st.expander("Ver prévia do relatório"):
                    st.text(report_text[:1000] + "\n...")

            with c2:
                st.markdown("#### 📦 Pacote Consolidado de Análise e Power BI")
                st.write("Monta um arquivo ZIP pronto contendo tudo o que você precisa:")
                st.markdown(
                    """
                    - Planilha limpa normalizada (Excel e CSV)
                    - Gráficos prontos exportados em HTML e PNG
                    - Metadados JSON estruturados (`powerbi_modelo.json`)
                    - Relatório de Auditoria textual de Frota
                    - Instruções de importação do Power BI
                    """
                )
                
                if st.button("Gerar Pacote Power BI e Análise", type="primary", key="fleet_zip_btn"):
                    with st.spinner("Gerando gráficos e montando pacote ZIP..."):
                        zip_bytes = create_export_zip(
                            df,
                            charts,
                            include_html=export_html,
                            include_png=export_png,
                            fleet_stats=fleet_analysis
                        )
                    st.download_button(
                        "💾 Baixar Pacote Completo (.zip)",
                        data=zip_bytes,
                        file_name=f"pacote_analise_frota_{base_name}.zip",
                        mime="application/zip"
                    )
                    st.success("Pacote gerado com sucesso!")

    # ------------------------------------------------------------
    # GENERIC MODE: DATASET PROFILER & EXPLORER
    # ------------------------------------------------------------
    else:
        st.markdown(
            f"""
            <div style="background-color: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 8px; padding: 10px; margin-bottom: 20px; font-weight: 600; color: #93C5FD; font-size: 0.9rem; text-align: center;">
                📊 MÓDULO ATIVO: Explorador de Dados Geral & Classificação Automática
            </div>
            """,
            unsafe_allow_html=True
        )

        tab_dados, tab_graficos, tab_export = st.tabs(["📋 Dados & Perfil", "📊 Gráficos Automáticos", "💾 Exportação"])

        with tab_dados:
            col1, col2, col3 = st.columns(3)
            col1.metric("Linhas carregadas", len(df))
            col2.metric("Colunas detectadas", len(df.columns))
            col3.metric("Gráficos gerados", len(charts))

            if profile:
                st.subheader("Perfil das colunas")
                perfil_df = [
                    {
                        "Coluna": c.name,
                        "Tipo detectado": c.kind,
                        "Valores únicos": c.unique_count,
                        "Nulos %": f"{c.null_ratio * 100:.1f}",
                    }
                    for c in profile.columns
                ]
                st.dataframe(perfil_df, use_container_width=True, hide_index=True)

            st.subheader("Prévia dos dados limpos (Top 100)")
            st.dataframe(df.head(100), use_container_width=True)

        with tab_graficos:
            if not charts:
                st.warning(
                    "Nenhum gráfico pôde ser gerado automaticamente. "
                    "Verifique se há colunas de data, categorias e números na planilha."
                )
            else:
                for idx, chart in enumerate(charts):
                    st.subheader(f"{idx+1}. {chart.title}")
                    st.plotly_chart(chart.figure, use_container_width=True)

                    c1, c2 = st.columns(2)
                    with c1:
                        html_snippet = figure_to_html(chart.figure)
                        st.download_button(
                            f"Baixar HTML — {chart.chart_id}",
                            data=html_snippet,
                            file_name=f"{chart.chart_id}.html",
                            mime="text/html",
                            key=f"html_{chart.chart_id}",
                        )
                        with st.expander(f"Ver código HTML"):
                            st.code(html_snippet[:8000] + ("..." if len(html_snippet) > 8000 else ""), language="html")
                    with c2:
                        try:
                            png_bytes = figure_to_png(chart.figure)
                            st.download_button(
                                f"Baixar PNG — {chart.chart_id}",
                                data=png_bytes,
                                file_name=f"{chart.chart_id}.png",
                                mime="image/png",
                                key=f"png_{chart.chart_id}",
                            )
                        except Exception:
                            st.info("Kaleido não disponível no momento para geração local de PNG.")

        with tab_export:
            st.subheader("Pacote completo")
            st.markdown(
                """
                O pacote ZIP inclui:
                - Planilha limpa (CSV e Excel)
                - Gráficos em HTML e PNG
                - Metadados para Power BI (`powerbi_modelo.json`)
                - Instruções de importação
                - Template `.pbit` (se configurado em `assets/powerbi/`)
                """
            )
            if st.button("Gerar pacote de exportação", type="primary", key="generic_zip_btn"):
                with st.spinner("Montando pacote..."):
                    zip_bytes = create_export_zip(
                        df,
                        charts,
                        include_html=export_html,
                        include_png=export_png,
                    )
                st.download_button(
                    "Baixar Pacote Power BI e Gráficos (.zip)",
                    data=zip_bytes,
                    file_name=f"pacote_analise_{base_name}.zip",
                    mime="application/zip",
                )
                st.success("Pacote pronto para download.")

else:
    # Landing page message when no file is uploaded
    st.markdown(
        """
        <div style="background-color: rgba(30, 41, 59, 0.45); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 25px; margin-top: 20px; box-shadow: 0 4px 30px rgba(0,0,0,0.25);">
            <h3 style="margin-top: 0; color: #F8FAFC;">🚀 Como começar</h3>
            <ol style="color: #CBD5E1; line-height: 1.6;">
                <li><b>Envie uma planilha:</b> Selecione um arquivo do tipo Excel (.xlsx) ou CSV acima.</li>
                <li><b>Detecção Automática:</b> O sistema aplicará a limpeza inteligente (resolvendo formatos de números brasileiros) e definirá a interface específica caso seja um log de frota.</li>
                <li><b>Exploração e Downloads:</b> Explore visualizações, mapas interativos, rankings de operadores e exporte gráficos ou relatórios prontos em ZIP para conectar no Power BI.</li>
            </ol>
            <div style="margin-top: 15px; font-size: 0.82rem; color: #94A3B8; border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 15px;">
                💡 <i>Baseado nos algoritmos corporativos de análise de frota locais (relatorio_master.py e gerar_graficos_master.py).</i>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
