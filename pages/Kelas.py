import streamlit as st
from utils.sheets import *
from utils.auth import *
import pandas as pd


st.set_page_config(
    page_title="Kelas",
    page_icon="🏫",
    layout="wide"
)

require_login()

kelas = ambil_kelas()
siswa = ambil_siswa()
tugas = ambil_tugas()


def norm(seri):
    return seri.astype(str).str.strip().str.upper()


# ── Statistik per kelas ──
hitung_siswa = norm(siswa["Kelas"]).value_counts()
hitung_tugas = norm(tugas["Kelas"]).value_counts()

kelas_info = kelas.copy()
kunci = norm(kelas_info["Nama Kelas"])
kelas_info["Jumlah Siswa"] = kunci.map(hitung_siswa).fillna(0).astype(int)
kelas_info["Jumlah Tugas"] = kunci.map(hitung_tugas).fillna(0).astype(int)


@st.dialog("Tambah Kelas")
def dialog_tambah_kelas():
    with st.form("Form Tambah Kelas"):
        nama_kelas = st.text_input("Nama Kelas")
        submit = st.form_submit_button("Simpan Kelas", width="stretch")

        if submit:
            if not nama_kelas.strip():
                st.error("Lengkapi nama kelas dahulu!")
            elif nama_kelas.strip().upper() in kelas["Nama Kelas"].str.upper().values:
                st.error("Kelas sudah terdaftar!")
            else:
                tambah_kelas(nama_kelas.strip().upper())
                st.toast("Kelas telah di tambahkan!")
                st.rerun()


@st.dialog("Edit Kelas", position="right")
def detail(item_kelas):
    kelas_lama = item_kelas["Nama Kelas"]

    c1, c2 = st.columns(2)
    c1.metric("Siswa", int(item_kelas["Jumlah Siswa"]))
    c2.metric("Tugas", int(item_kelas["Jumlah Tugas"]))

    with st.container(border=True):
        kelas_baru = st.text_input("Nama Kelas", value=kelas_lama)

        if st.button("Simpan Perubahan", width="stretch"):
            kelas_baru = kelas_baru.strip().upper()

            if not kelas_baru:
                st.error("Nama kelas tidak boleh kosong!")
            elif (
                kelas_baru != kelas_lama
                and kelas_baru in kelas["Nama Kelas"].str.upper().values
            ):
                st.error("Nama kelas sudah dipakai kelas lain!")
            elif kelas_baru == kelas_lama:
                st.error("Tidak ada data yang diedit!")
            else:
                if edit_kelas(kelas_lama, kelas_baru):
                    st.toast("Kelas berhasil diedit!")
                    st.rerun()
                else:
                    st.error("Kelas tidak ditemukan di sheet!")

    with st.container(border=True):
        if item_kelas["Jumlah Siswa"] or item_kelas["Jumlah Tugas"]:
            st.warning(
                "Kelas ini masih punya siswa/tugas. "
                "Menghapus kelas tidak ikut menghapus data tersebut."
            )
        yakin = st.checkbox("Saya yakin ingin menghapus kelas ini")
        if st.button("🗑️ Hapus Kelas", width="stretch", disabled=not yakin):
            if hapus_kelas(kelas_lama):
                st.toast("Kelas berhasil dihapus!")
                st.rerun()
            else:
                st.error("Kelas tidak ditemukan di sheet!")


# ── Ringkasan atas ──
m1, m2, m3 = st.columns(3)
m1.metric("Total Kelas", len(kelas_info))
m2.metric("Total Siswa", int(kelas_info["Jumlah Siswa"].sum()))
m3.metric("Total Tugas", int(kelas_info["Jumlah Tugas"].sum()))

st.write("")

tabel_kelas, crud_kelas = st.columns([3, 1])

with tabel_kelas:
    cari = st.text_input("🔍 Cari kelas", placeholder="Ketik nama kelas...")

    tampil = kelas_info
    if cari.strip():
        tampil = tampil[
            tampil["Nama Kelas"].astype(str).str.lower().str.contains(cari.strip().lower(), regex=False)
        ]
    tampil = tampil.reset_index(drop=True)

    if tampil.empty:
        st.info("Tidak ada kelas yang cocok." if cari.strip() else "Belum ada kelas.")

    st.caption("💡 Klik satu baris untuk memilih kelas.")
    maks_siswa = max(int(kelas_info["Jumlah Siswa"].max()) if not kelas_info.empty else 1, 1)
    df_kelas = st.dataframe(
        tampil,
        on_select="rerun",
        selection_mode="single-row",
        hide_index=True,
        width="stretch",
        column_config={
            "Jumlah Siswa": st.column_config.ProgressColumn(
                "Jumlah Siswa", min_value=0, max_value=maks_siswa, format="%d"
            ),
            "Jumlah Tugas": st.column_config.NumberColumn("Jumlah Tugas"),
        },
    )

with crud_kelas:
    st.write("")
    if st.button("➕ Tambah Kelas", width="stretch"):
        dialog_tambah_kelas()

    if df_kelas.selection.rows:
        i = df_kelas.selection.rows[0]
        if i < len(tampil):
            item_kelas = tampil.iloc[i]
            st.divider()
            with st.container(border=True):
                st.caption("Kelas terpilih")
                st.markdown(f"**{item_kelas['Nama Kelas']}**")
                st.caption(
                    f"🧑🏻‍🎓 {int(item_kelas['Jumlah Siswa'])} siswa · "
                    f"📃 {int(item_kelas['Jumlah Tugas'])} tugas"
                )
            if st.button("✏️ Edit Kelas", width="stretch"):
                detail(item_kelas)