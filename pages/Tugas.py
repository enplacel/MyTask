import streamlit as st
from utils.sheets import *
from utils.auth import *
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.drive import upload_pdf, FOLDER_ID
import pandas as pd


def now_wib():
    return datetime.now(ZoneInfo("Asia/Jakarta")).replace(tzinfo=None)


def parse_deadline(df):
    return pd.to_datetime(
        df["Deadline"].astype(str).str.replace(".", ":", regex=False),
        format="%Y-%m-%d %H:%M",
        errors="coerce"
    )


def format_sisa(delta):
    total = int(delta.total_seconds())
    jam = total // 3600
    hari = jam // 24
    if hari >= 1:
        return f"{hari} hari {jam % 24} jam"
    if jam >= 1:
        return f"{jam} jam {(total % 3600) // 60} mnt"
    return f"{max(total // 60, 1)} mnt"


def label_sisa(dl, sekarang):
    if pd.isna(dl):
        return "-"
    if dl <= sekarang:
        return "Berakhir"
    return format_sisa(dl - sekarang)


def warna_sisa(dl, sekarang):
    if pd.isna(dl) or dl <= sekarang:
        return "gray"
    jam = (dl - sekarang).total_seconds() / 3600
    return "red" if jam < 24 else "orange" if jam < 72 else "green"


def filter_tugas_aktif(tugas):
    deadline = parse_deadline(tugas)
    return tugas.loc[deadline > now_wib()].copy()


def tambah_info_waktu(df):
    """Tambah kolom _dl, Status, Sisa Waktu."""
    df = df.copy()
    sekarang = now_wib()
    df["_dl"] = parse_deadline(df)
    df["Status"] = df["_dl"].apply(lambda d: "⏳ Aktif" if d > sekarang else "⌛ Berakhir")
    df["Sisa Waktu"] = df["_dl"].apply(lambda d: label_sisa(d, sekarang))
    return df


st.set_page_config(
    page_title="Tugas",
    page_icon="📃",
    layout="wide"
)

require_login()

role = get_role()
user = st.session_state["user"]

if role == "murid":
    tugas = ambil_tugas(st.session_state["kelas"])
else:
    tugas = ambil_tugas()
daftar_kelas = ambil_kelas()["Nama Kelas"].tolist()


# Dialog Edit Tugas
@st.dialog("Edit Tugas", position="right")
def dialog_edit_tugas(item):
    with st.container(border=True):
        judul_baru = st.text_input("Judul", value=item["Judul"])
        deskripsi_baru = st.text_area("Deskripsi", value=item["Deskripsi"])
        file_baru = st.file_uploader("File (kosongkan jika tidak diganti)", type=["pdf"])
        deadline_lama = datetime.strptime(
            str(item["Deadline"]).replace(".", ":"),
            "%Y-%m-%d %H:%M"
        )

        c1, c2 = st.columns(2)
        tanggal_baru = c1.date_input(
            "Tanggal Deadline",
            value=deadline_lama.date(),
            format="DD/MM/YYYY"
        )
        jam_baru = c2.time_input("Jam Deadline", value=deadline_lama.time())
        deadline_baru = datetime.combine(tanggal_baru, jam_baru)

        kelas_baru = st.selectbox(
            "Kelas",
            daftar_kelas,
            index=None,
            placeholder=item["Kelas"]
        )

        if st.button("Simpan Perubahan", width="stretch"):
            judul_lama = item["Judul"]
            judul_baru = judul_baru.strip()
            kelas_final = kelas_baru or item["Kelas"]

            if not judul_baru:
                st.error("Judul tidak boleh kosong!")
            elif judul_baru != judul_lama and judul_baru in tugas["Judul"].values:
                st.error("Judul sudah dipakai tugas lain!")
            else:
                with st.spinner("Menyimpan..."):
                    link_file = upload_pdf(file_baru, FOLDER_ID) if file_baru else item["File"]
                    update_tugas = edit_tugas(
                        judul_lama,
                        judul_baru,
                        deskripsi_baru,
                        link_file,
                        deadline_baru,
                        kelas_final
                    )
                if update_tugas:
                    st.toast("Tugas berhasil di edit!")
                    st.rerun()
                else:
                    st.error("Tugas tidak ditemukan di sheet!")

    with st.container(border=True):
        yakin = st.checkbox("Saya yakin ingin menghapus tugas ini")
        if st.button("🗑️ Hapus Tugas", width="stretch", disabled=not yakin):
            if hapus_tugas(item["Judul"]):
                st.toast("Tugas berhasil dihapus!")
                st.rerun()
            else:
                st.error("Tugas tidak ditemukan di sheet!")


# ═════════════════════════ Admin ═════════════════════════
if role == "admin":
    daftar_tugas, monitoring, form_tambah_tugas = st.tabs(
        ["📃 Daftar Tugas", "📊 Monitoring Tugas", "➕ Tambah Tugas"]
    )

    # ── Tab Daftar Tugas ──
    with daftar_tugas:
        tugas_v = tambah_info_waktu(tugas) if not tugas.empty else tugas.assign(
            _dl=pd.NaT, Status="", **{"Sisa Waktu": ""}
        )

        k1, k2, k3 = st.columns(3)
        k1.metric("Total Tugas", len(tugas_v))
        k2.metric("Aktif", int((tugas_v["Status"] == "⏳ Aktif").sum()))
        k3.metric("Berakhir", int((tugas_v["Status"] == "⌛ Berakhir").sum()))

        f1, f2, f3 = st.columns([2, 2, 2])
        with f1:
            cari = st.text_input("🔍 Cari tugas", placeholder="Judul atau deskripsi...", key="cari_tugas")
        with f2:
            pilih_kelas = st.segmented_control(
                "Kelas", ["Semua"] + daftar_kelas, default="Semua", key="flt_kelas_tugas"
            ) or "Semua"
        with f3:
            pilih_status = st.segmented_control(
                "Status", ["Semua", "Aktif", "Berakhir"], default="Semua", key="flt_status_tugas"
            ) or "Semua"

        tampil = tugas_v
        if cari.strip():
            q = cari.strip().lower()
            tampil = tampil[
                tampil["Judul"].astype(str).str.lower().str.contains(q, regex=False)
                | tampil["Deskripsi"].astype(str).str.lower().str.contains(q, regex=False)
            ]
        if pilih_kelas != "Semua":
            tampil = tampil[tampil["Kelas"].astype(str).str.strip().str.upper() == pilih_kelas.strip().upper()]
        if pilih_status != "Semua":
            tampil = tampil[tampil["Status"].str.contains(pilih_status)]
        tampil = tampil.sort_values("_dl").reset_index(drop=True)

        tabel_daftar_tugas, crud_tugas = st.columns([3, 1])
        with tabel_daftar_tugas:
            if tampil.empty:
                st.info("Tidak ada tugas yang cocok dengan filter.")
            st.caption("💡 Klik satu baris untuk memilih tugas.")
            table_edit_tugas = st.dataframe(
                tampil[["Judul", "Deskripsi", "File", "Deadline", "Kelas", "Status", "Sisa Waktu"]],
                on_select="rerun",
                selection_mode="single-row",
                hide_index=True,
                width="stretch",
                column_config={
                    "File": st.column_config.LinkColumn("File", display_text="⬇️ Download")
                },
            )

        with crud_tugas:
            st.write(f"Menampilkan **{len(tampil)}** tugas")
            st.download_button(
                "⬇️ Unduh CSV",
                data=tampil.drop(columns=["_dl"]).to_csv(index=False).encode("utf-8"),
                file_name="daftar_tugas.csv",
                mime="text/csv",
                width="stretch",
                disabled=tampil.empty,
            )

            if table_edit_tugas.selection.rows:
                i = table_edit_tugas.selection.rows[0]
                if i < len(tampil):
                    item = tampil.iloc[i]
                    st.divider()
                    with st.container(border=True):
                        st.caption("Tugas terpilih")
                        st.markdown(f"**{item['Judul']}**")
                        st.caption(f"🏫 {item['Kelas']} · ⏰ {item['Deadline']}")
                        st.caption(f"{item['Status']} · {item['Sisa Waktu']}")
                    if st.button("✏️ Edit Tugas", width="stretch"):
                        dialog_edit_tugas(item)

    # ── Tab Monitoring Tugas ──
    with monitoring:
        st.subheader("📊 Monitoring Pengumpulan Tugas")

        daftar_judul = tugas["Judul"].dropna().tolist()

        if not daftar_judul:
            st.info("Belum ada tugas yang tersedia.")
        else:
            pilihan_tugas = st.selectbox("Pilih Tugas", daftar_judul)

            data_tugas = tugas[tugas["Judul"] == pilihan_tugas]

            if not data_tugas.empty:
                kelas_tugas = data_tugas["Kelas"].iloc[0]
                dl_tugas = parse_deadline(data_tugas).iloc[0]
                st.caption(
                    f"🏫 {kelas_tugas} · ⏰ {data_tugas['Deadline'].iloc[0]} · "
                    f"{label_sisa(dl_tugas, now_wib())}"
                )

                pengumpulan = ambil_pengumpulan(npm=None, limit=None)

                data_pengumpulan = pengumpulan[
                    (pengumpulan["Judul"] == pilihan_tugas)
                    & (pengumpulan["Kelas"] == kelas_tugas)
                ].copy()

                siswa = ambil_siswa()
                siswa["NPM"] = siswa["NPM"].astype(str)
                siswa_kelas = siswa[
                    siswa["Kelas"].astype(str).str.strip() == str(kelas_tugas).strip()
                ].copy()

                npm_sudah = data_pengumpulan["NPM"].astype(str).str.strip().tolist()

                siswa_kelas["Status"] = siswa_kelas["NPM"].astype(str).str.strip().apply(
                    lambda npm: "Sudah Mengumpulkan" if npm in npm_sudah else "Belum Mengumpulkan"
                )

                total_siswa = len(siswa_kelas)
                sudah = (siswa_kelas["Status"] == "Sudah Mengumpulkan").sum()
                belum = total_siswa - sudah

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Murid", total_siswa)
                col2.metric("Sudah Mengumpulkan", sudah)
                col3.metric("Belum Mengumpulkan", belum)

                progress = sudah / total_siswa if total_siswa > 0 else 0
                st.progress(progress, text=f"Progres Pengumpulan: {progress:.0%}")

                st.divider()

                data_tabel = siswa_kelas.merge(
                    data_pengumpulan[["NPM", "Waktu", "File"]].drop_duplicates(
                        subset=["NPM"], keep="last"
                    ),
                    on="NPM",
                    how="left"
                )

                m1, m2 = st.columns([2, 3])
                with m1:
                    cari_m = st.text_input("🔍 Cari murid", placeholder="NPM atau nama...", key="cari_monitor")
                with m2:
                    status_m = st.segmented_control(
                        "Status",
                        ["Semua", "Sudah Mengumpulkan", "Belum Mengumpulkan"],
                        default="Semua",
                        key="flt_monitor",
                    ) or "Semua"

                if cari_m.strip():
                    q = cari_m.strip().lower()
                    data_tabel = data_tabel[
                        data_tabel["NPM"].astype(str).str.lower().str.contains(q, regex=False)
                        | data_tabel["Nama"].astype(str).str.lower().str.contains(q, regex=False)
                    ]
                if status_m != "Semua":
                    data_tabel = data_tabel[data_tabel["Status"] == status_m]

                data_tabel = data_tabel[["NPM", "Nama", "Status", "Waktu", "File"]]

                st.dataframe(
                    data_tabel,
                    column_config={
                        "File": st.column_config.LinkColumn(
                            "File Pengumpulan", display_text="📄 Lihat PDF"
                        )
                    },
                    hide_index=True,
                    width="stretch"
                )
                st.download_button(
                    "⬇️ Unduh rekap CSV",
                    data=data_tabel.to_csv(index=False).encode("utf-8"),
                    file_name=f"monitoring_{pilihan_tugas}.csv",
                    mime="text/csv",
                    disabled=data_tabel.empty,
                )

    # ── Tab Tambah Tugas ──
    with form_tambah_tugas:
        with st.form("Form Tambah Tugas", clear_on_submit=True):
            judul_tugas = st.text_input("*Judul Tugas")
            deskripsi_tugas = st.text_area("Deskripsi")
            file_tugas = st.file_uploader("*File Tugas", type="pdf")
            c1, c2 = st.columns(2)
            tanggal_deadline = c1.date_input("*Tanggal Deadline", value=None, format="DD/MM/YYYY")
            jam_deadline = c2.time_input("*Jam Deadline", value=None)
            kelas_dipilih = st.selectbox(
                "*Pilih Kelas", daftar_kelas, index=None, placeholder="Pilih Kelas"
            )
            submit = st.form_submit_button("Simpan Tugas", width="stretch")

        if submit:
            if not judul_tugas.strip() or not file_tugas or not kelas_dipilih:
                st.warning("Lengkapi form terlebih dahulu!")
            elif tanggal_deadline is None or jam_deadline is None:
                st.warning("Tanggal dan jam deadline wajib diisi!")
            else:
                deadline = datetime.combine(tanggal_deadline, jam_deadline)
                with st.spinner("Mengunggah file..."):
                    link_file = upload_pdf(file_tugas, FOLDER_ID)
                    tambah_tugas(
                        judul_tugas,
                        deskripsi_tugas,
                        link_file,
                        deadline,
                        kelas_dipilih
                    )
                st.toast("Tugas berhasil ditambahkan!")
                st.rerun()

# ═════════════════════════ Murid ═════════════════════════
else:
    npm_murid = st.session_state["npm"]
    nama_murid = st.session_state["nama"]
    kelas_murid = st.session_state["kelas"]

    tugas = filter_tugas_aktif(ambil_tugas(kelas_murid))
    pengumpulan = ambil_pengumpulan(npm_murid)

    tugas_selesai = pengumpulan[
        pengumpulan["NPM"].astype(str) == str(npm_murid)
    ]["Judul"].astype(str).tolist()

    tugas = tambah_info_waktu(tugas) if not tugas.empty else tugas.assign(_dl=pd.NaT)
    tugas["Selesai"] = tugas["Judul"].astype(str).isin(tugas_selesai)
    tugas = tugas.sort_values("_dl").reset_index(drop=True)

    @st.dialog("Kerjakan Tugas", position="right")
    def dialog_kerjakan(item):
        st.write("**Judul :**", item["Judul"])
        st.write("**Deskripsi :**", item["Deskripsi"] or "-")
        st.write("**Deadline :**", item["Deadline"])
        st.write("**Kelas :**", item["Kelas"])
        if item["File"]:
            st.link_button("⬇️ Download Soal", item["File"])

        file_jawaban = st.file_uploader("Upload Jawaban (PDF)", type=["pdf"])

        if st.button("Kumpulkan", width="stretch"):
            try:
                batas = datetime.strptime(
                    str(item["Deadline"]).replace(".", ":"), "%Y-%m-%d %H:%M"
                )
                lewat = now_wib() > batas
            except ValueError:
                lewat = False

            if not file_jawaban:
                st.error("Upload file jawaban terlebih dahulu!")
            elif lewat:
                st.error("Deadline sudah lewat!")
            else:
                with st.spinner("Mengunggah jawaban..."):
                    link = upload_pdf(
                        file_jawaban,
                        FOLDER_ID,
                        nama_file=f"{npm_murid}_{kelas_murid}_{item['Judul']}.pdf"
                    )
                    kumpul_tugas(npm_murid, nama_murid, kelas_murid, item["Judul"], link)
                st.toast("Tugas berhasil dikumpulkan!")
                st.rerun()

    total_aktif = len(tugas)
    sudah = int(tugas["Selesai"].sum()) if total_aktif else 0
    belum = total_aktif - sudah

    st.caption(f"Kelas : {kelas_murid}")
    m1, m2, m3 = st.columns(3)
    m1.metric("Tugas Aktif", total_aktif)
    m2.metric("Belum Dikerjakan", belum)
    m3.metric("Sudah Dikumpulkan", sudah)
    st.progress(
        sudah / total_aktif if total_aktif else 0,
        text=f"Progres: {sudah}/{total_aktif} tugas"
    )

    f1, f2 = st.columns([2, 3])
    with f1:
        cari = st.text_input("🔍 Cari tugas", placeholder="Judul atau deskripsi...", key="cari_murid")
    with f2:
        tampilan = st.segmented_control(
            "Tampilkan",
            ["Belum dikerjakan", "Sudah dikumpulkan", "Semua"],
            default="Belum dikerjakan",
            key="flt_murid",
        ) or "Belum dikerjakan"

    tampil = tugas
    if tampilan == "Belum dikerjakan":
        tampil = tampil[~tampil["Selesai"]]
    elif tampilan == "Sudah dikumpulkan":
        tampil = tampil[tampil["Selesai"]]
    if cari.strip() and not tampil.empty:
        q = cari.strip().lower()
        tampil = tampil[
            tampil["Judul"].astype(str).str.lower().str.contains(q, regex=False)
            | tampil["Deskripsi"].astype(str).str.lower().str.contains(q, regex=False)
        ]

    if tampil.empty:
        if total_aktif and tampilan == "Belum dikerjakan" and not cari.strip():
            st.success("🎉 Semua tugas aktif sudah kamu kumpulkan!")
        else:
            st.info("Tidak ada tugas untuk ditampilkan.")

    sekarang = now_wib()
    for idx, row in tampil.iterrows():
        with st.container(border=True):
            kiri, kanan = st.columns([4, 1])
            with kiri:
                st.markdown(f"**{row['Judul']}**")
                st.caption(f"⏰ {row['Deadline']}")
                if row["Deskripsi"]:
                    with st.expander("Lihat deskripsi"):
                        st.write(row["Deskripsi"])
            with kanan:
                if row["Selesai"]:
                    st.badge("Terkumpul", icon="✅", color="green")
                else:
                    st.badge(f"Sisa {row['Sisa Waktu']}", icon="⏳", color=warna_sisa(row["_dl"], sekarang))

            b1, b2, _ = st.columns([1, 1, 3])
            if row["File"]:
                b1.link_button("⬇️ Soal", row["File"], width="stretch")
            if not row["Selesai"]:
                if b2.button("📤 Kerjakan", key=f"kerjakan_{idx}", width="stretch"):
                    dialog_kerjakan(row)