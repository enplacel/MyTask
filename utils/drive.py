import re
import uuid
import streamlit as st
from supabase import create_client

# Dipertahankan supaya `from utils.drive import upload_pdf, FOLDER_ID` di Tugas.py tetap jalan.
# Artinya sekarang: nama folder (prefix path) di dalam bucket.
FOLDER_ID = "uploads"


@st.cache_resource
def get_client():
    cfg = st.secrets["supabase"]
    return create_client(cfg["url"], cfg["key"])


def _aman(nama):
    """Supabase menolak spasi/karakter aneh di key, jadi dibersihkan dulu."""
    nama = re.sub(r"[^A-Za-z0-9._-]+", "_", str(nama)).strip("._")
    return nama or "file.pdf"


def upload_pdf(file, folder_id, nama_file=None):
    bucket = st.secrets["supabase"]["bucket"]
    nama = _aman(nama_file or file.name)
    if not nama.lower().endswith(".pdf"):
        nama += ".pdf"

    # uuid: nama nggak bentrok dan link nggak bisa ditebak
    path = f"{folder_id}/{uuid.uuid4().hex[:12]}_{nama}"

    storage = get_client().storage.from_(bucket)
    storage.upload(
        path=path,
        file=file.getvalue(),
        file_options={"content-type": "application/pdf"},
    )
    return storage.get_public_url(path)