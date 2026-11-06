import html
import streamlit as st
from utils.sheets import *
from utils.auth import *
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)
require_login()

kelas = ambil_kelas()
tugas = ambil_tugas()
siswa = ambil_siswa()


def now_wib():
    return datetime.now(ZoneInfo("Asia/Jakarta")).replace(tzinfo=None)


def parse_deadline(df):
    return pd.to_datetime(
        df["Deadline"].astype(str).str.replace(".", ":", regex=False),
        format="%Y-%m-%d %H:%M",
        errors="coerce"
    )


def filter_kelas(df, nama):
    return df[
        df["Kelas"].astype(str).str.strip().str.upper() == nama.strip().upper()
    ]


def format_sisa(delta):
    total = int(delta.total_seconds())
    jam = total // 3600
    hari = jam // 24
    if hari >= 1:
        return f"{hari} hari {jam % 24} jam"
    if jam >= 1:
        return f"{jam} jam {(total % 3600) // 60} mnt"
    return f"{max(total // 60, 1)} mnt"


# ── CSS khusus Dashboard (animasi) ──
PAGE_CSS = """
<style>
@property --n { syntax: '<integer>'; initial-value: 0; inherits: false; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
@keyframes floatA { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-14px); } }
@keyframes floatB { 0%, 100% { transform: translateX(0); } 50% { transform: translateX(-16px); } }
@keyframes gradShift { 0%, 100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(248,113,113,0.6); } 70% { box-shadow: 0 0 0 8px rgba(248,113,113,0); } 100% { box-shadow: 0 0 0 0 rgba(248,113,113,0); } }

.hero {
    background: linear-gradient(135deg, #0F766E 0%, #1D4ED8 50%, #6D28D9 100%);
    background-size: 200% 200%;
    animation: gradShift 14s ease-in-out infinite;
    border-radius: 24px;
    padding: 2rem 2.25rem;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 24px 60px -24px rgba(45,212,191,0.5);
    position: relative;
    overflow: hidden;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.hero .c1 { position:absolute; top:-60px; right:-40px; width:220px; height:220px; border-radius:50%; background:rgba(244,114,182,0.5); animation: floatA 8s ease-in-out infinite; }
.hero .c2 { position:absolute; bottom:-70px; right:150px; width:150px; height:150px; border-radius:50%; background:rgba(255,255,255,0.12); animation: floatB 10s ease-in-out infinite; }
.hero .row { position:relative; z-index:1; display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
.hero .hi { font-size:13px; color:rgba(255,255,255,0.88); font-weight:500; margin-bottom:4px; }
.hero .nm { font-size:34px; font-weight:800; letter-spacing:-0.03em; color:#FFFFFF; margin-bottom:4px; }
.hero .sub { font-size:14px; color:rgba(255,255,255,0.9); }
.hero .chip { background:rgba(255,255,255,0.16); border:1px solid rgba(255,255,255,0.3); color:#FFFFFF; font-size:12px; font-weight:600; padding:7px 16px; border-radius:999px; backdrop-filter:blur(6px); }

.stat-grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(190px, 1fr)); gap:16px; font-family:'Plus Jakarta Sans', sans-serif; }
.stat-card {
    position:relative; overflow:hidden; display:flex; align-items:center; gap:16px;
    background: radial-gradient(circle at 100% 0%, rgba(45,212,191,0.10), transparent 55%), #131A2E;
    border:1px solid #243049; border-radius:18px; padding:20px 22px;
    animation: fadeUp 0.55s cubic-bezier(0.2,0.7,0.2,1) backwards;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}
.stat-card::before { content:""; position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg,#2DD4BF,#38BDF8,#A78BFA); }
.stat-card:hover { transform:translateY(-3px); border-color:rgba(45,212,191,0.55); box-shadow:0 16px 36px -14px rgba(45,212,191,0.45); }
.stat-ic { width:46px; height:46px; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:22px; background:rgba(45,212,191,0.12); border:1px solid rgba(45,212,191,0.3); border-radius:14px; transition: transform 0.25s ease; }
.stat-card:hover .stat-ic { transform: scale(1.12) rotate(-6deg); }
.stat-label { font-size:13px; font-weight:500; color:#8B95B0; margin-bottom:2px; }
.stat-num {
    --n: var(--t);
    counter-reset: n var(--n);
    font-size:34px; font-weight:800; letter-spacing:-0.03em; line-height:1.1;
    color:#E6EAF5;
    background: linear-gradient(135deg, #FFFFFF 20%, #5EEAD4 100%);
    -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
    animation-duration:1.3s; animation-timing-function:cubic-bezier(0.2,0.8,0.2,1); animation-fill-mode:both; animation-delay:0.35s;
}
.stat-num::after { content: counter(n); }

.dl-wrap { font-family:'Plus Jakarta Sans', sans-serif; display:flex; flex-direction:column; gap:8px; }
.dl-row { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:10px 12px; border-radius:12px; background:rgba(11,16,32,0.5); border:1px solid #243049; animation: fadeUp 0.45s ease backwards; transition: border-color 0.2s ease, transform 0.2s ease; }
.dl-row:nth-child(2) { animation-delay: 0.06s; }
.dl-row:nth-child(3) { animation-delay: 0.12s; }
.dl-row:nth-child(4) { animation-delay: 0.18s; }
.dl-row:nth-child(5) { animation-delay: 0.24s; }
.dl-row:hover { border-color: rgba(45,212,191,0.45); transform: translateX(3px); }
.dl-title { font-size:14px; font-weight:600; color:#E6EAF5; }
.dl-meta { font-size:12px; color:#8B95B0; margin-top:2px; }
.dl-badge { font-size:12px; font-weight:600; padding:5px 12px; border-radius:999px; white-space:nowrap; }
.dl-badge.urgent { background:rgba(248,113,113,0.14); color:#F87171; animation: pulse 2s infinite; }
.dl-badge.soon { background:rgba(251,191,36,0.14); color:#FBBF24; }
.dl-badge.ok { background:rgba(45,212,191,0.14); color:#5EEAD4; }

@media (prefers-reduced-motion: reduce) {
    .hero, .hero .c1, .hero .c2, .stat-card, .dl-row, .dl-badge { animation: none !important; }
    .stat-num { animation: none !important; }
}
</style>
"""

# ── Hero ──
jam_sekarang = now_wib().hour
if jam_sekarang < 11:
    sapaan = "Selamat pagi"
elif jam_sekarang < 15:
    sapaan = "Selamat siang"
elif jam_sekarang < 18:
    sapaan = "Selamat sore"
else:
    sapaan = "Selamat malam"

st.markdown(
    PAGE_CSS
    + f"""<div class="hero"><div class="c1"></div><div class="c2"></div><div class="row"><div><div class="hi">{sapaan}! 👋</div><div class="nm">Admin!</div><div class="sub">Yuk pantau tugas kamu</div></div></div></div>""",
    unsafe_allow_html=True
)

# ── Filter kelas (interaktif) ──
daftar_kelas = kelas["Nama Kelas"].tolist()
pilihan = st.segmented_control(
    "Filter kelas",
    ["Semua"] + daftar_kelas,
    default="Semua",
    key="dash_kelas",
    label_visibility="collapsed"
)

if not pilihan or pilihan == "Semua":
    siswa_f = siswa
    tugas_f = tugas
    jumlah_kelas = len(kelas)
else:
    siswa_f = filter_kelas(siswa, pilihan)
    tugas_f = filter_kelas(tugas, pilihan)
    jumlah_kelas = 1

aktif = int((parse_deadline(tugas_f) > now_wib()).sum()) if not tugas_f.empty else 0

# ── Kartu statistik (angka menghitung naik) ──
data_kartu = [
    ("🏫", "Total Kelas", jumlah_kelas),
    ("🧑🏻‍🎓", "Total Siswa", len(siswa_f)),
    ("📃", "Total Tugas", len(tugas_f)),
    ("⏳", "Tugas Aktif", aktif),
]

keyframes = ""
kartu = ""
for i, (ikon, label, nilai) in enumerate(data_kartu):
    nama_anim = f"cnt_{i}_{nilai}"
    keyframes += f"@keyframes {nama_anim}{{from{{--n:0;}}to{{--n:{nilai};}}}}"
    kartu += (
        f'<div class="stat-card" style="animation-delay:{0.08 * i:.2f}s">'
        f'<div class="stat-ic">{ikon}</div>'
        f'<div><div class="stat-label">{label}</div>'
        f'<div class="stat-num" style="--t:{nilai};animation-name:{nama_anim}"></div></div>'
        f'</div>'
    )

st.markdown(
    f"<style>{keyframes}</style><div class='stat-grid'>{kartu}</div>",
    unsafe_allow_html=True
)

st.write("")

# ── Panel ringkasan ──
kiri, kanan = st.columns([3, 2])

with kiri:
    with st.container(border=True):
        st.markdown("**Tugas per Kelas**")
        if tugas.empty:
            st.caption("Belum ada tugas.")
        else:
            per_kelas = tugas.groupby("Kelas").size().rename("Jumlah Tugas")
            st.bar_chart(per_kelas, color="#2DD4BF")


@st.fragment(run_every="60s")
def panel_deadline():
    with st.container(border=True):
        judul_panel = "**Deadline Terdekat**"
        if pilihan and pilihan != "Semua":
            judul_panel += f" · {html.escape(pilihan)}"
        st.markdown(judul_panel)

        sekarang = now_wib()
        mendatang = pd.DataFrame()
        if not tugas_f.empty:
            tmp = tugas_f.copy()
            tmp["_dl"] = parse_deadline(tmp)
            mendatang = tmp[tmp["_dl"] > sekarang].sort_values("_dl").head(5)

        if mendatang.empty:
            st.caption("Tidak ada deadline mendatang.")
            return

        baris = ""
        for _, r in mendatang.iterrows():
            sisa = r["_dl"] - sekarang
            jam_sisa = sisa.total_seconds() / 3600
            nada = "urgent" if jam_sisa < 24 else "soon" if jam_sisa < 72 else "ok"
            baris += (
                '<div class="dl-row">'
                f'<div><div class="dl-title">{html.escape(str(r["Judul"]))}</div>'
                f'<div class="dl-meta">{html.escape(str(r["Kelas"]))} · {r["_dl"].strftime("%d %b, %H:%M")}</div></div>'
                f'<div class="dl-badge {nada}">{format_sisa(sisa)}</div>'
                '</div>'
            )
        st.markdown(f'<div class="dl-wrap">{baris}</div>', unsafe_allow_html=True)


with kanan:
    panel_deadline()