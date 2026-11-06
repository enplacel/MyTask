import streamlit as st
from utils.sheets import *
from utils.auth import *

st.set_page_config(page_title="Profil", page_icon="👤", layout="wide")
require_role("murid")

npm = st.session_state["npm"]

st.subheader("👤 Profil Saya")
c1, c2, c3 = st.columns(3)
c1.metric("Nama", st.session_state["nama"])
c2.metric("NPM", npm)
c3.metric("Kelas", st.session_state["kelas"])

if st.session_state.get("pw_default"):
    st.warning("Password kamu masih sama dengan NPM. Segera ganti supaya akunmu aman!")

with st.container(border=True):
    st.markdown("**Ganti Password**")
    with st.form("form_ganti_pw", clear_on_submit=True):
        lama = st.text_input("Password saat ini", type="password")
        baru = st.text_input("Password baru", type="password")
        ulang = st.text_input("Ulangi password baru", type="password")
        submit = st.form_submit_button("Simpan Password", width="stretch")

    if submit:
        if not lama or not baru or not ulang:
            st.error("Lengkapi semua kolom!")
        elif len(baru) < 6:
            st.error("Password baru minimal 6 karakter!")
        elif baru == npm:
            st.error("Password baru tidak boleh sama dengan NPM!")
        elif baru != ulang:
            st.error("Konfirmasi password tidak cocok!")
        elif not verifikasi_login(npm, lama):
            st.error("Password saat ini salah!")
        else:
            with st.spinner("Menyimpan..."):
                ok = ganti_password(npm, baru)
            if ok:
                st.session_state["pw_default"] = False
                st.toast("Password berhasil diganti!")
                st.rerun()
            else:
                st.error("Akun tidak ditemukan di sheet!")