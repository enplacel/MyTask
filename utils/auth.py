import streamlit as st
from utils.sheets import cari_siswa

# ─────────────────────────────────────────────
# Palet J+ — Midnight Navy + Teal, dengan highlight gradient
#   Background  #0B1020   Surface  #131A2E   Sidebar #0E1426
#   Primary     #2DD4BF   Sky #38BDF8   Violet #A78BFA   Pink #F472B6
#   Hero        #0F766E → #1D4ED8 → #6D28D9  (teks putih)
#   Teks        #E6EAF5   Teks muted #8B95B0
#   Border      #243049
#   Sukses #34D399 · Peringatan #FBBF24 · Bahaya #F87171
# ─────────────────────────────────────────────

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── Background aurora ── */
.stApp, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(800px 480px at 88% -8%, rgba(45,212,191,0.13), transparent 60%),
        radial-gradient(700px 480px at -8% 12%, rgba(124,58,237,0.13), transparent 60%),
        radial-gradient(600px 400px at 60% 110%, rgba(56,189,248,0.08), transparent 60%),
        #0B1020 !important;
    background-attachment: fixed !important;
}
header[data-testid="stHeader"] { background: transparent !important; }

/* ── Keyframes ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    0%   { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* ── Entrance halaman (satu kali, berurutan) ── */
.block-container > div[data-testid="stVerticalBlock"] > div {
    animation: fadeUp 0.55s cubic-bezier(0.2, 0.7, 0.2, 1) backwards;
}
.block-container > div[data-testid="stVerticalBlock"] > div:nth-child(2) { animation-delay: 0.06s; }
.block-container > div[data-testid="stVerticalBlock"] > div:nth-child(3) { animation-delay: 0.12s; }
.block-container > div[data-testid="stVerticalBlock"] > div:nth-child(4) { animation-delay: 0.18s; }
.block-container > div[data-testid="stVerticalBlock"] > div:nth-child(5) { animation-delay: 0.24s; }
.block-container > div[data-testid="stVerticalBlock"] > div:nth-child(6) { animation-delay: 0.30s; }
.block-container > div[data-testid="stVerticalBlock"] > div:nth-child(n+7) { animation-delay: 0.36s; }

/* ── Hormati pengaturan "kurangi gerakan" ── */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
    }
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: #243049; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #2DD4BF; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0E1426 0%, #0B1020 100%) !important;
    border-right: 1px solid #243049 !important;
    color: #E6EAF5 !important;
}
section[data-testid="stSidebar"] a {
    color: #8B95B0 !important;
    text-decoration: none !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #243049 !important;
}

/* Nav links: pill + glow saat aktif */
div[data-testid="stSidebarNav"] a,
a[data-testid="stSidebarNavLink"] {
    border-radius: 999px !important;
    padding: 7px 14px !important;
    transition: background 0.15s ease, box-shadow 0.15s ease !important;
}
div[data-testid="stSidebarNav"] a:hover,
a[data-testid="stSidebarNavLink"]:hover {
    background: #131A2E !important;
}
div[data-testid="stSidebarNav"] a:hover span,
a[data-testid="stSidebarNavLink"]:hover span {
    color: #E6EAF5 !important;
}
div[data-testid="stSidebarNav"] a[aria-current="page"],
a[data-testid="stSidebarNavLink"][aria-current="page"] {
    background: linear-gradient(90deg, rgba(45,212,191,0.22), rgba(56,189,248,0.06)) !important;
    box-shadow: 0 0 0 1px rgba(45,212,191,0.35), 0 6px 18px -8px rgba(45,212,191,0.5) !important;
}
div[data-testid="stSidebarNav"] a[aria-current="page"] span,
a[data-testid="stSidebarNavLink"][aria-current="page"] span {
    color: #5EEAD4 !important;
    font-weight: 600 !important;
}

/* ── Metric cards ── */
div[data-testid="stMetric"] {
    position: relative !important;
    overflow: hidden !important;
    background:
        radial-gradient(circle at 100% 0%, rgba(45,212,191,0.10), transparent 55%),
        #131A2E !important;
    padding: 20px 22px !important;
    border-radius: 18px !important;
    border: 1px solid #243049 !important;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease !important;
}
div[data-testid="stMetric"]::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #2DD4BF, #38BDF8, #A78BFA);
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px) !important;
    border-color: rgba(45,212,191,0.5) !important;
    box-shadow: 0 14px 34px -14px rgba(45,212,191,0.4) !important;
}
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] label p {
    color: #8B95B0 !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}
div[data-testid="stMetricValue"] {
    color: #E6EAF5 !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
}
div[data-testid="stMetricValue"] > div {
    background: linear-gradient(135deg, #FFFFFF 20%, #5EEAD4 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ── Progress bar ── */
div[data-testid="stProgressBar"] > div {
    background: linear-gradient(90deg, #2DD4BF, #38BDF8, #A78BFA, #38BDF8, #2DD4BF) !important;
    background-size: 200% 100% !important;
    animation: shimmer 3s linear infinite !important;
    border-radius: 99px !important;
    box-shadow: 0 0 14px rgba(45,212,191,0.5) !important;
}
div[data-testid="stProgressBar"] {
    background: #243049 !important;
    border-radius: 99px !important;
    height: 10px !important;
}

/* ── Buttons (gradient, teks gelap) ── */
div[data-testid="stButton"] > button,
div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #2DD4BF 0%, #38BDF8 100%) !important;
    color: #04141A !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease !important;
}
div[data-testid="stButton"] > button p,
div[data-testid="stFormSubmitButton"] > button p {
    color: #04141A !important;
}
div[data-testid="stButton"] > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    filter: brightness(1.08) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 10px 24px -8px rgba(45,212,191,0.55) !important;
}
div[data-testid="stButton"] > button:focus-visible,
div[data-testid="stFormSubmitButton"] > button:focus-visible {
    outline: 3px solid rgba(45,212,191,0.4) !important;
    outline-offset: 2px !important;
}

div[data-testid="stButton"] > button:active,
div[data-testid="stFormSubmitButton"] > button:active {
    transform: translateY(0) scale(0.97) !important;
    filter: brightness(0.95) !important;
}
div[data-testid="stSidebarNav"] a:hover,
a[data-testid="stSidebarNavLink"]:hover {
    transform: translateX(3px) !important;
}

/* ── Form inputs ── */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea {
    border-radius: 12px !important;
    border-color: #243049 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #2DD4BF !important;
    box-shadow: 0 0 0 3px rgba(45,212,191,0.2) !important;
}

/* ── Selectbox ── */
div[data-testid="stSelectbox"] > div {
    border-radius: 12px !important;
    border-color: #243049 !important;
}

/* ── Tabs ── */
button[data-baseweb="tab"] p {
    color: #8B95B0 !important;
    font-weight: 500 !important;
}
button[data-baseweb="tab"][aria-selected="true"] p {
    color: #5EEAD4 !important;
    font-weight: 600 !important;
}
div[data-baseweb="tab-highlight"] {
    background: linear-gradient(90deg, #2DD4BF, #38BDF8) !important;
    height: 3px !important;
    border-radius: 99px !important;
}
div[data-baseweb="tab-border"] {
    background-color: #243049 !important;
}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {
    border-radius: 16px !important;
    overflow: hidden !important;
    border: 1px solid #243049 !important;
}

/* ── Containers (kartu panel) ── */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px !important;
    border-color: #243049 !important;
    background: rgba(19,26,46,0.6) !important;
}

/* ── Dialog ── */
div[data-testid="stDialog"] div[role="dialog"] {
    background:
        radial-gradient(circle at 100% 0%, rgba(45,212,191,0.12), transparent 50%),
        #131A2E !important;
    border-radius: 22px !important;
    border: 1px solid #243049 !important;
    box-shadow: 0 30px 80px -20px rgba(0,0,0,0.6) !important;
}

/* ── Divider ── */
hr {
    border-color: #243049 !important;
}

/* ── Toast ── */
div[data-testid="stToast"] {
    border-radius: 14px !important;
    border: 1px solid #243049 !important;
    border-left: 4px solid #2DD4BF !important;
}

/* Hide streamlit branding */
#MainMenu, footer { visibility: hidden; }
</style>
"""

LOGIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.stApp, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(800px 480px at 90% -10%, rgba(45,212,191,0.16), transparent 60%),
        radial-gradient(700px 480px at -10% 15%, rgba(124,58,237,0.16), transparent 60%),
        #0B1020 !important;
    background-attachment: fixed !important;
}

#MainMenu, header, footer { visibility: hidden; }
section[data-testid="stSidebar"] { display: none !important; }

.block-container {
    max-width: 440px !important;
    padding-top: 8vh !important;
    margin: 0 auto !important;
}

.login-header {
    background: linear-gradient(135deg, #0F766E 0%, #1D4ED8 55%, #6D28D9 100%);
    border-radius: 22px 22px 0 0;
    padding: 2.25rem 2rem 1.75rem;
    border: 1px solid rgba(255,255,255,0.12);
    border-bottom: none;
    position: relative;
    overflow: hidden;
}

.login-header::before {
    content: '';
    position: absolute;
    top: -50px; right: -40px;
    width: 170px; height: 170px;
    border-radius: 50%;
    background: rgba(244,114,182,0.55);
    filter: blur(2px);
}

.login-header::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 30px;
    width: 110px; height: 110px;
    border-radius: 50%;
    background: rgba(255,255,255,0.14);
}

.login-icon {
    width: 56px; height: 56px;
    display: inline-flex;
    align-items: center; justify-content: center;
    font-size: 28px;
    margin-bottom: 14px;
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 16px;
    position: relative; z-index: 1;
}

.login-title {
    font-size: 26px !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
    color: #FFFFFF !important;
    margin: 0 0 4px !important;
    position: relative; z-index: 1;
}

.login-subtitle {
    font-size: 14px !important;
    color: rgba(255,255,255,0.88) !important;
    margin: 0 !important;
    font-weight: 400 !important;
    position: relative; z-index: 1;
}

.st-key-login_body {
    background: #131A2E !important;
    border-radius: 0 0 22px 22px !important;
    border: 1px solid #243049 !important;
    border-top: none !important;
    padding: 1.25rem 2rem 2rem !important;
    box-shadow: 0 30px 60px -20px rgba(45,212,191,0.25), 0 16px 40px rgba(0,0,0,0.4) !important;
}

div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #8B95B0 !important;
}

div[data-testid="stSelectbox"] > div,
div[data-testid="stTextInput"] > div > div {
    border-radius: 12px !important;
    border-color: #243049 !important;
}

div[data-testid="stSelectbox"] > div:focus-within,
div[data-testid="stTextInput"] > div > div:focus-within {
    border-color: #2DD4BF !important;
    box-shadow: 0 0 0 3px rgba(45,212,191,0.2) !important;
}

div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #2DD4BF 0%, #38BDF8 100%) !important;
    color: #04141A !important;
    border: none !important;
    border-radius: 12px !important;
    height: 48px !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    width: 100% !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease !important;
}
div[data-testid="stButton"] > button p {
    color: #04141A !important;
}

div[data-testid="stButton"] > button:hover {
    filter: brightness(1.08) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 10px 24px -8px rgba(45,212,191,0.55) !important;
}

div[data-testid="stButton"] > button:focus-visible {
    outline: 3px solid rgba(45,212,191,0.4) !important;
    outline-offset: 2px !important;
}
div[data-testid="stButton"] > button:active {
    transform: translateY(0) scale(0.98) !important;
}

/* ── Animasi login ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes popIn {
    0%   { opacity: 0; transform: scale(0.6) rotate(-8deg); }
    70%  { opacity: 1; transform: scale(1.1) rotate(2deg); }
    100% { opacity: 1; transform: scale(1) rotate(0); }
}
@keyframes floaty {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-12px); }
}
@keyframes gradShift {
    0%, 100% { background-position: 0% 50%; }
    50%      { background-position: 100% 50%; }
}
.login-header {
    background-size: 200% 200% !important;
    animation: fadeUp 0.6s cubic-bezier(0.2, 0.7, 0.2, 1) backwards,
               gradShift 14s ease-in-out infinite;
}
.login-header::before { animation: floaty 7s ease-in-out infinite; }
.login-header::after  { animation: floaty 9s ease-in-out infinite reverse; }
.login-icon { animation: popIn 0.7s cubic-bezier(0.2, 0.9, 0.3, 1.2) 0.25s backwards; }
.st-key-login_body {
    animation: fadeUp 0.6s cubic-bezier(0.2, 0.7, 0.2, 1) 0.12s backwards;
}
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation: none !important; transition: none !important; }
}
</style>
"""
roles = {
    "Admin" : "admin",
    "Murid" : "murid",
}

def require_login():
    if st.session_state.get("logged_in", False):
        _render_sidebar()
        return True

    st.markdown(LOGIN_CSS, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-header">
        <div class="login-icon">📖</div>
        <div class="login-title">MyTask</div>
        <div class="login-subtitle">Ayo kerjakan soal mu!</div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(key="login_body"):
        akun = st.selectbox(
            "Pilih akun",
            ("Admin", "Murid"),
            index=None,
            placeholder="Pilih akun kamu..."
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Masukkan password kamu..."
        )

        if st.button("Masuk", use_container_width=True):
            if not akun:
                st.error("Pilih akun dulu ya!")
            elif not password:
                st.error("Password tidak boleh kosong!")
            elif akun == "Admin":
                if st.secrets["passwords"]["Admin"] == password:
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = "Admin"
                    st.session_state["role"] = "admin"
                    st.toast("Login berhasil. Selamat datang, Admin!", icon="👋")
                    st.rerun()
                else:
                    st.error("Password salah. Coba lagi!")
            else:
                # Murid: password = NPM
                with st.spinner("Memeriksa data..."):
                    siswa = cari_siswa(password)
                if siswa:
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = "Murid"
                    st.session_state["role"] = "murid"
                    st.session_state["npm"] = str(siswa["NPM"])
                    st.session_state["nama"] = siswa["Nama"]
                    st.session_state["kelas"] = siswa["Kelas"]
                    st.toast(f"Halo, {siswa['Nama']}! Semangat ya 🚀")
                    st.rerun()
                else:
                    st.error("NPM tidak ditemukan. Coba lagi!")

    st.markdown("""
    <p style="text-align:center;color:#8B95B0;font-size:12px;margin-top:1.5rem;font-family:'Plus Jakarta Sans',sans-serif;">
        FlashCard · Kelompok 2 
    </p>
    """, unsafe_allow_html=True)

    st.stop()


def _render_sidebar():
    user = st.session_state.get("user", "User")
    peran = st.session_state.get("role")
    initials = user[:2].upper()

    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    with st.sidebar:
        # Avatar + info user
        user = st.session_state.get("user", "User")
        nama_tampil = st.session_state.get("nama") or user
        peran = st.session_state.get("role")
        initials = nama_tampil[:2].upper()
        st.markdown(f"""
        <div style="padding: 1.25rem 0.5rem 1rem; border-bottom: 1px solid #243049; margin-bottom: 0.75rem;">
            <div style="display:flex; align-items:center; gap:12px;">
                <div style="
                    width:44px; height:44px; border-radius:50%;
                    background: linear-gradient(135deg, #2DD4BF, #A78BFA);
                    box-shadow: 0 6px 18px -6px rgba(45,212,191,0.6);
                    display:flex; align-items:center; justify-content:center;
                    font-size:15px; font-weight:800; color:#04141A;
                    flex-shrink:0;
                    font-family:'Plus Jakarta Sans',sans-serif;
                ">{initials}</div>
                <div>
                    <div style="font-size:14px; font-weight:600; color:#E6EAF5; font-family:'Plus Jakarta Sans',sans-serif;">{user}</div>
                <div style="font-size:11px; color:#8B95B0; font-family:'Plus Jakarta Sans',sans-serif;">Halo, {peran}👋🏻</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div style="font-size:12px; color:#8B95B0; font-family:'Plus Jakarta Sans',sans-serif; padding: 4px 0;">
                Log Out sebagai <strong style="color:#5EEAD4;">{user}</strong>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("↩", help="Logout"):
                do_logout()


def do_logout():
    st.session_state["logged_in"] = False
    st.session_state["user"] = None
    st.session_state["role"] = None
    st.rerun()
    
def get_role():
    return st.session_state.get("role")

def require_role(*allowed_roles):
    """Panggil setelah require_login(). Hentikan halaman jika role tidak sesuai."""
    require_login()
    if get_role() not in allowed_roles:
        st.error("🚫 Kamu tidak punya akses ke halaman ini.")
        st.stop()