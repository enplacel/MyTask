import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

TTL = 30  # detik


def now_wib():
  return datetime.now(ZoneInfo("Asia/Jakarta")).replace(tzinfo=None)


def _stamp():
  return now_wib().strftime("%Y-%m-%d %H:%M:%S")


@st.cache_resource
def _buka_sheets():
  gc = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
  ss = gc.open("Tubes Sisfor DB")
  return {
    "kelas": ss.worksheet("Kelas"),
    "tugas": ss.worksheet("Tugas"),
    "siswa": ss.worksheet("Siswa"),
    "history_tugas": ss.worksheet("History_Tugas"),
    "history_siswa": ss.worksheet("History_Siswa"),
    "history_kelas": ss.worksheet("History_Kelas"),
    "pengumpulan": ss.worksheet("Pengumpulan"),
  }


_ws = _buka_sheets()
sheet_kelas = _ws["kelas"]
sheet_tugas = _ws["tugas"]
sheet_siswa = _ws["siswa"]
sheet_history_tugas = _ws["history_tugas"]
sheet_history_siswa = _ws["history_siswa"]
sheet_history_kelas = _ws["history_kelas"]
sheet_pengumpulan = _ws["pengumpulan"]


def _records(sheet):
  return sheet.get_all_records(numericise_ignore=["all"])


# ───────────────────────── KELAS ─────────────────────────
@st.cache_data(ttl=TTL, show_spinner=False)
def ambil_kelas():
  data_kelas = _records(sheet_kelas)
  kolom_kelas = ["Nama Kelas"]
  if not data_kelas:
    return pd.DataFrame(columns=kolom_kelas)
  return pd.DataFrame(data_kelas, columns=kolom_kelas)


def tambah_kelas(nama_kelas):
  sheet_kelas.append_row([nama_kelas], value_input_option="USER_ENTERED")
  catat_history_kelas("Tambah", nama_kelas)
  st.cache_data.clear()


def edit_kelas(kelas_lama, kelas_baru):
  daftar_kelas = sheet_kelas.col_values(1)
  try:
    baris = daftar_kelas.index(kelas_lama) + 1
  except ValueError:
    return False

  sheet_kelas.update(range_name=f"A{baris}", values=[[kelas_baru]])
  catat_history_kelas("Edit", kelas_baru)
  st.cache_data.clear()
  return True


def hapus_kelas(nama_kelas):
  daftar_kelas = sheet_kelas.col_values(1)
  try:
    baris = daftar_kelas.index(nama_kelas) + 1
  except ValueError:
    return False
  sheet_kelas.delete_rows(baris)
  catat_history_kelas("Hapus", nama_kelas)
  st.cache_data.clear()
  return True


# ───────────────────────── TUGAS ─────────────────────────
@st.cache_data(ttl=TTL, show_spinner=False)
def ambil_tugas(kelas=None):
  data_tugas = _records(sheet_tugas)
  kolom_tugas = ["Judul", "Deskripsi", "File", "Deadline", "Kelas"]
  if not data_tugas:
    return pd.DataFrame(columns=kolom_tugas)

  df = pd.DataFrame(data_tugas, columns=kolom_tugas)
  if kelas:
    df = df[
      df["Kelas"].astype(str).str.strip().str.upper()
      == str(kelas).strip().upper()
    ].reset_index(drop=True)
  return df


def tambah_tugas(judul, deskripsi, file, deadline, kelas):
  sheet_tugas.append_row(
    [judul, deskripsi, file, deadline.strftime("%Y-%m-%d %H:%M"), kelas],
    value_input_option="USER_ENTERED"
  )
  catat_history_tugas("Tambah", judul, kelas)
  st.cache_data.clear()


def edit_tugas(judul_lama, judul_baru, deskripsi_baru, file_baru, deadline_baru, kelas_baru):
  daftar_tugas = sheet_tugas.col_values(1)
  try:
    baris = daftar_tugas.index(judul_lama) + 1
  except ValueError:
    return False

  if hasattr(deadline_baru, "strftime"):
    deadline_baru = deadline_baru.strftime("%Y-%m-%d %H:%M")

  # Data lama (untuk log / history)
  lama = sheet_tugas.row_values(baris) + [""] * 5
  baru = [judul_baru, deskripsi_baru, file_baru, deadline_baru, kelas_baru]
  nama_kolom = ["Judul", "Deskripsi", "File", "Deadline", "Kelas"]
  berubah = [nama_kolom[i] for i in range(5) if str(lama[i]) != str(baru[i])]

  sheet_tugas.update(
    range_name=f"A{baris}:E{baris}",
    values=[baru],
    value_input_option="USER_ENTERED"
  )
  catat_history_tugas("Edit", judul_baru, kelas_baru, ", ".join(berubah))
  st.cache_data.clear()
  return True


def hapus_tugas(judul):
  daftar_tugas = sheet_tugas.col_values(1)
  try:
    baris = daftar_tugas.index(judul) + 1
  except ValueError:
    return False

  kelas = (sheet_tugas.row_values(baris) + [""] * 5)[4]
  sheet_tugas.delete_rows(baris)
  catat_history_tugas("Hapus", judul, kelas)
  st.cache_data.clear()
  return True


# ───────────────────────── SISWA ─────────────────────────
@st.cache_data(ttl=TTL, show_spinner=False)
def ambil_siswa():
  data_siswa = _records(sheet_siswa)
  kolom_siswa = ["NPM", "Nama", "Kelas"]
  if not data_siswa:
    return pd.DataFrame(columns=kolom_siswa)
  return pd.DataFrame(data_siswa, columns=kolom_siswa)


def cari_siswa(npm):
  """Login murid: selalu baca data terbaru (tanpa cache)."""
  npm = str(npm).strip()
  if not npm:
    return None

  data = _records(sheet_siswa)
  siswa = pd.DataFrame(data, columns=["NPM", "Nama", "Kelas"])
  siswa["NPM"] = siswa["NPM"].astype(str).str.strip()
  hasil = siswa[siswa["NPM"] == npm]

  if hasil.empty:
    return None
  return hasil.iloc[0].to_dict()


def tambah_siswa(npm, nama, kelas):
  npm = str(npm)
  sheet_siswa.append_row([npm, nama, kelas], value_input_option="RAW")
  catat_history_siswa("Tambah", npm, kelas)
  st.cache_data.clear()


def edit_siswa(npm_lama, npm_baru, nama_baru, kelas):
  daftar_siswa = sheet_siswa.col_values(1)
  try:
    baris = daftar_siswa.index(npm_lama) + 1
  except ValueError:
    return False

  lama = sheet_siswa.row_values(baris) + [""] * 3
  baru = [npm_baru, nama_baru, kelas]
  nama_kolom = ["NPM", "Nama", "Kelas"]
  berubah = [nama_kolom[i] for i in range(3) if str(lama[i]) != str(baru[i])]

  sheet_siswa.update(
    range_name=f"A{baris}:C{baris}",
    values=[[npm_baru, nama_baru, kelas]],
    value_input_option="RAW"
  )
  catat_history_siswa("Edit", nama_baru, kelas, ", ".join(berubah))
  st.cache_data.clear()
  return True


def hapus_siswa(npm):
  daftar_npm = sheet_siswa.col_values(1)
  try:
    baris = daftar_npm.index(str(npm)) + 1
  except ValueError:
    return False
  kelas = (sheet_siswa.row_values(baris) + [""] * 3)[2]
  sheet_siswa.delete_rows(baris)
  catat_history_siswa("Hapus", npm, kelas)
  st.cache_data.clear()
  return True


# ───────────────────────── HISTORY ─────────────────────────
@st.cache_data(ttl=TTL, show_spinner=False)
def ambil_history_tugas(limit=30):
  data = _records(sheet_history_tugas)
  kolom = ["Waktu", "Aksi", "Judul", "Kelas", "Detail"]
  if not data:
    return pd.DataFrame(columns=kolom)
  df = pd.DataFrame(data, columns=kolom)
  return df.tail(limit).iloc[::-1].reset_index(drop=True)


@st.cache_data(ttl=TTL, show_spinner=False)
def ambil_history_siswa(limit=30):
  data = _records(sheet_history_siswa)
  kolom = ["Waktu", "Aksi", "NPM", "Kelas", "Detail"]
  if not data:
    return pd.DataFrame(columns=kolom)
  df = pd.DataFrame(data, columns=kolom)
  return df.tail(limit).iloc[::-1].reset_index(drop=True)


@st.cache_data(ttl=TTL, show_spinner=False)
def ambil_history_kelas(limit=30):
  data = _records(sheet_history_kelas)
  kolom = ["Waktu", "Aksi", "Kelas"]
  if not data:
    return pd.DataFrame(columns=kolom)
  df = pd.DataFrame(data, columns=kolom)
  return df.tail(limit).iloc[::-1].reset_index(drop=True)


def catat_history_tugas(aksi, judul, kelas, detail=""):
  sheet_history_tugas.append_row(
    [_stamp(), aksi, judul, kelas, detail],
    value_input_option="RAW"
  )


def catat_history_siswa(aksi, npm, kelas, detail=""):
  sheet_history_siswa.append_row(
    [_stamp(), aksi, npm, kelas, detail],
    value_input_option="RAW"
  )


def catat_history_kelas(aksi, kelas):
  sheet_history_kelas.append_row(
    [_stamp(), aksi, kelas],
    value_input_option="RAW"
  )


# ───────────────────────── PENGUMPULAN ─────────────────────────
def kumpul_tugas(npm, nama, kelas, judul, file):
  sheet_pengumpulan.append_row(
    [_stamp(), str(npm), nama, kelas, judul, file],
    value_input_option="RAW"
  )
  st.cache_data.clear()


@st.cache_data(ttl=TTL, show_spinner=False)
def ambil_pengumpulan(npm=None, limit=10):
  data = _records(sheet_pengumpulan)
  kolom = ["Waktu", "NPM", "Nama", "Kelas", "Judul", "File"]
  if not data:
    return pd.DataFrame(columns=kolom)

  df = pd.DataFrame(data, columns=kolom)
  if npm is not None:
    df = df[df["NPM"].astype(str).str.strip() == str(npm).strip()]
  if limit is not None:
    df = df.tail(limit)
  return df.iloc[::-1].reset_index(drop=True)


# ───────────────────────── ARSIP (belum dipakai) ─────────────────────────
def arsipkan_tugas_kedaluwarsa(role):
  if role != "murid":
    return 0

  data_tugas = _records(sheet_tugas)
  sekarang = now_wib()

  baris_dihapus = []
  for i, item in enumerate(data_tugas, start=2):
    try:
      deadline = datetime.strptime(
        str(item["Deadline"]).replace(".", ":"), "%Y-%m-%d %H:%M"
      )
    except (ValueError, TypeError):
      continue

    if sekarang >= deadline:
      catat_history_tugas("Hapus", item["Judul"], item["Kelas"], "Tugas Kadaluarsa")
      baris_dihapus.append(i)

  # hapus dari bawah supaya nomor baris tidak bergeser
  for baris in reversed(baris_dihapus):
    sheet_tugas.delete_rows(baris)

  if baris_dihapus:
    st.cache_data.clear()
  return len(baris_dihapus)