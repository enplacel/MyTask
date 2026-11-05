import streamlit as st
from utils.sheets import *
from utils.auth import *


st.set_page_config(
    page_title="FlashCard",
    page_icon="📖",
    layout="wide"
)
# require_login()

# Navigasi halaman — dipertahankan sesuai template.
dashboard = st.Page("pages/Dashboard.py", title="Dashboard", icon="📊")
kelas    = st.Page("pages/Kelas.py",    title="Kelas",    icon="🏫")
siswa = st.Page("pages/Siswa.py", title="Siswa", icon="🧑🏻‍🎓")
tugas   = st.Page("pages/Tugas.py",   title="Tugas",   icon="📃")
history   = st.Page("pages/History.py",   title="History",   icon="📜")

if get_role() == "admin":
    pg = st.navigation([dashboard, kelas, siswa, tugas, history])
else:
    pg = st.navigation([tugas, history])

pg.run()