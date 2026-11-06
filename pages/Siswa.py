import streamlit as st
from utils.sheets import *
from utils.auth import *
from string import capwords

st.set_page_config(
    page_title="Siswa",
    page_icon="🧑🏻‍🎓",
    layout="wide"
)

require_login()

kelas = ambil_kelas()
siswa = ambil_siswa()
siswa["NPM"] = siswa["NPM"].astype(str)
daftar_kelas = kelas["Nama Kelas"].tolist()


@st.dialog("Tambah Siswa")
def dialog_tambah_siswa(nama_kelas):
    st.write("Kelas : ", nama_kelas)
    with st.form(f"form_tambah_{nama_kelas}"):
        npm = st.text_input("NPM")
        nama = st.text_input("Nama")
        submit = st.form_submit_button("Simpan Siswa", width="stretch")

    if submit:
        if not npm.strip() or not nama.strip():
            st.error("Lengkapi NPM dan nama terlebih dahulu!")
        elif npm.strip() in siswa["NPM"].values:
            st.error("NPM sudah terdaftar!")
        else:
            tambah_siswa(npm.strip(), capwords(nama.strip()), nama_kelas)
            st.toast("Siswa berhasil ditambahkan!")
            st.rerun()


@st.dialog("Edit Siswa", position="right")
def dialog_edit_siswa(nama_kelas, item):
    npm_lama = str(item["NPM"])
    st.write("Kelas : ", nama_kelas)

    with st.form(f"form_edit_{nama_kelas}"):
        npm = st.text_input("NPM", value=npm_lama)
        nama = st.text_input("Nama", value=item["Nama"])
        submit = st.form_submit_button("Edit Siswa", width="stretch")

    if submit:
        npm_baru = npm.strip()
        nama_baru = capwords(nama.strip())

        if not npm_baru or not nama_baru:
            st.error("Lengkapi NPM dan nama terlebih dahulu!")
        elif npm_baru != npm_lama and npm_baru in siswa["NPM"].values:
            st.error("NPM sudah dipakai siswa lain!")
        elif npm_baru == npm_lama and nama_baru == item["Nama"]:
            st.error("Tidak ada data yang diedit!")
        else:
            if edit_siswa(npm_lama, npm_baru, nama_baru, nama_kelas):
                st.session_state.pop(f"tabel_{nama_kelas}", None)
                st.toast("Data siswa berhasil diedit!")
                st.rerun()
    if st.button("🔑 Reset password ke NPM", key=f"reset_{nama_kelas}", width="stretch"):
        if ganti_password(npm_lama, ""):
            st.toast("Password direset ke NPM!")
        else:
            st.error("Siswa tidak ditemukan di sheet!")

    st.divider()

    yakin = st.checkbox("Saya yakin ingin menghapus siswa ini", key=f"yakin_{nama_kelas}")
    if st.button("Hapus Siswa", key=f"hapus_{nama_kelas}", width="stretch", disabled=not yakin):
        if hapus_siswa(npm_lama):
            st.session_state.pop(f"tabel_{nama_kelas}", None)
            st.toast("Siswa berhasil dihapus!")
            st.rerun()
        else:
            st.error("Siswa tidak ditemukan di sheet!")


if not daftar_kelas:
    st.info("Belum ada kelas. Tambahkan kelas dulu di halaman Kelas.")
    st.stop()

# ── Ringkasan atas ──
m1, m2 = st.columns(2)
m1.metric("Total Siswa", len(siswa))
m2.metric("Total Kelas", len(daftar_kelas))

tabs = st.tabs([f"🏫 {k}" for k in daftar_kelas])

for nama_kelas, tab in zip(daftar_kelas, tabs):
    with tab:
        siswa_kelas = siswa[
            siswa["Kelas"].astype(str).str.strip().str.upper()
            == nama_kelas.strip().upper()
        ].reset_index(drop=True)

        # ── Pencarian + urutan ──
        f1, f2 = st.columns([3, 2])
        with f1:
            cari = st.text_input(
                "🔍 Cari siswa",
                key=f"cari_{nama_kelas}",
                placeholder="Ketik NPM atau nama...",
            )
        with f2:
            urut = st.segmented_control(
                "Urutkan",
                ["Nama A-Z", "Nama Z-A", "NPM"],
                default="Nama A-Z",
                key=f"urut_{nama_kelas}",
            )

        tampil = siswa_kelas
        if cari.strip():
            q = cari.strip().lower()
            tampil = tampil[
                tampil["NPM"].str.lower().str.contains(q, regex=False)
                | tampil["Nama"].astype(str).str.lower().str.contains(q, regex=False)
            ]

        if urut == "Nama Z-A":
            tampil = tampil.sort_values("Nama", ascending=False)
        elif urut == "NPM":
            tampil = tampil.sort_values("NPM")
        else:
            tampil = tampil.sort_values("Nama")
        tampil = tampil.reset_index(drop=True)

        tabel, aksi = st.columns([3, 1])

        with tabel:
            if tampil.empty:
                st.info("Tidak ada siswa yang cocok." if cari.strip() else "Belum ada siswa di kelas ini.")
            st.caption("💡 Klik satu baris untuk memilih siswa.")
            pilihan = st.dataframe(
                tampil,
                key=f"tabel_{nama_kelas}",
                on_select="rerun",
                selection_mode="single-row",
                hide_index=True,
                width="stretch",
            )

        with aksi:
            st.metric("Jumlah Siswa", len(siswa_kelas))
            if cari.strip():
                st.caption(f"{len(tampil)} cocok dengan pencarian")
            st.divider()

            if st.button("➕ Tambah Siswa", key=f"tambah_{nama_kelas}", width="stretch"):
                dialog_tambah_siswa(nama_kelas)

            if pilihan.selection.rows:
                idx = pilihan.selection.rows[0]
                if idx < len(tampil):
                    item = tampil.iloc[idx]
                    st.divider()
                    with st.container(border=True):
                        st.caption("Siswa terpilih")
                        st.markdown(f"**{item['Nama']}**")
                        st.caption(f"NPM {item['NPM']}")
                    if st.button("✏️ Edit Siswa", key=f"edit_{nama_kelas}", width="stretch"):
                        dialog_edit_siswa(nama_kelas, item)