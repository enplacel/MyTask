import streamlit as st
import pandas as pd
from utils.sheets import *
from utils.auth import *

st.set_page_config(
    page_title="history_tugas",
    page_icon="📜",
    layout="wide"
)

require_login()

IKON = {"Tambah": "🟢 Tambah", "Edit": "🟡 Edit", "Hapus": "🔴 Hapus"}


def cari_df(df, q):
    if not q.strip():
        return df
    gabung = df.astype(str).agg(" ".join, axis=1).str.lower()
    return df[gabung.str.contains(q.strip().lower(), regex=False)]


def tampil_history(df, key, kosong):
    if df.empty:
        st.info(kosong)
        return

    # Ringkasan aksi
    hitung = df["Aksi"].value_counts()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total", len(df))
    m2.metric("🟢 Tambah", int(hitung.get("Tambah", 0)))
    m3.metric("🟡 Edit", int(hitung.get("Edit", 0)))
    m4.metric("🔴 Hapus", int(hitung.get("Hapus", 0)))

    # Filter
    f1, f2 = st.columns([2, 3])
    with f1:
        q = st.text_input("🔍 Cari", key=f"cari_{key}", placeholder="Ketik kata kunci...")
    with f2:
        aksi = st.pills(
            "Aksi",
            list(IKON.keys()),
            selection_mode="multi",
            default=list(IKON.keys()),
            format_func=lambda a: IKON[a],
            key=f"aksi_{key}",
        )

    tampil = df
    if aksi:
        tampil = tampil[tampil["Aksi"].isin(aksi)]
    tampil = cari_df(tampil, q).reset_index(drop=True)

    st.caption(f"Menampilkan {len(tampil)} dari {len(df)} aktivitas")

    if tampil.empty:
        st.info("Tidak ada aktivitas yang cocok dengan filter.")
        return

    unduh = tampil.copy()
    tampil["Aksi"] = tampil["Aksi"].map(IKON).fillna(tampil["Aksi"])
    st.dataframe(tampil, hide_index=True, width="stretch")
    st.download_button(
        "⬇️ Unduh CSV",
        data=unduh.to_csv(index=False).encode("utf-8"),
        file_name=f"history_{key}.csv",
        mime="text/csv",
        key=f"csv_{key}",
    )


jumlah = st.slider("Jumlah data ditampilkan", min_value=5, max_value=30, value=10)

if get_role() == "admin":
    tugas, siswa, kelas = st.tabs(["📃 Tugas", "🧑🏻‍🎓 Siswa", "🏫 Kelas"])
    with tugas:
        st.subheader("History Data Tugas")
        tampil_history(ambil_history_tugas(jumlah), "tugas", "Belum ada aktivitas tugas.")
    with siswa:
        st.subheader("History Data Siswa")
        tampil_history(ambil_history_siswa(jumlah), "siswa", "Belum ada aktivitas siswa.")
    with kelas:
        st.subheader("History Data Kelas")
        tampil_history(ambil_history_kelas(jumlah), "kelas", "Belum ada aktivitas kelas.")

else:
    st.subheader("History Pengumpulan Tugas")
    riwayat = ambil_pengumpulan(st.session_state["npm"], jumlah)

    if riwayat.empty:
        st.info("Kamu belum mengumpulkan tugas.")
    else:
        m1, m2 = st.columns(2)
        m1.metric("Tugas Terkumpul", len(riwayat))
        m2.metric("Terakhir Mengumpulkan", str(riwayat["Waktu"].iloc[0]))

        q = st.text_input("🔍 Cari tugas", placeholder="Judul tugas...", key="cari_riwayat")
        tampil = cari_df(riwayat[["Waktu", "Judul", "Kelas", "File"]], q).reset_index(drop=True)

        if tampil.empty:
            st.info("Tidak ada tugas yang cocok.")
        else:
            st.dataframe(
                tampil,
                hide_index=True,
                width="stretch",
                column_config={
                    "File": st.column_config.LinkColumn("File", display_text="📄 Lihat")
                },
            )