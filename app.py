import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

# ======================================
#  KONFIGURASI AKUN LOGIN
# ======================================
users = {
    "admin": "admin123",
    "petugas1": "petugas123",
    "petugas2": "petugas456"
}

# ======================================
#  FILE PENYIMPANAN
# ======================================
DATA_FILE = "inventaris.csv"

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["ID", "Nama Barang", "Jenis", "Jumlah", "Kondisi", "Ruang", "Penanggung Jawab"])
    df.to_csv(DATA_FILE, index=False)

# ======================================
#  FUNGSI PEMBANTU
# ======================================
def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def generate_pdf(df, filename="Laporan_Inventaris.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Laporan Inventaris SMK KY Ageng Giri", ln=True, align="C")
    pdf.ln(10)
    for index, row in df.iterrows():
        pdf.cell(0, 10, txt=f"{row['ID']}. {row['Nama Barang']} | {row['Jenis']} | {row['Jumlah']} | {row['Kondisi']} | {row['Ruang']} | PJ: {row['Penanggung Jawab']}", ln=True)
    pdf.output(filename)
    return filename

# ======================================
#  HALAMAN LOGIN
# ======================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login Aplikasi Sarpras")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error("Username atau password salah!")
    st.stop()

# ======================================
#  DASHBOARD UTAMA
# ======================================
st.title("🏫 Sistem Manajemen Sarpras SMK KY Ageng Giri")
st.caption(f"👤 Login sebagai: {st.session_state.username}")

menu = st.sidebar.selectbox("Menu", ["Lihat Data", "Tambah Data", "Laporan PDF", "Logout"])

# ======================================
#  MENU LIHAT DATA
# ======================================
if menu == "Lihat Data":
    st.header("📋 Data Inventaris")
    df = load_data()
    ruang_filter = st.selectbox("Filter Ruang", ["Semua"] + sorted(df["Ruang"].unique().tolist()))
    if ruang_filter != "Semua":
        df = df[df["Ruang"] == ruang_filter]
    st.dataframe(df)
    st.download_button("📥 Unduh Data CSV", df.to_csv(index=False), file_name="inventaris.csv", mime="text/csv")

# ======================================
#  MENU TAMBAH DATA
# ======================================
elif menu == "Tambah Data":
    st.header("➕ Tambah Data Inventaris")
    df = load_data()
    id_baru = len(df) + 1
    nama = st.text_input("Nama Barang")
    jenis = st.text_input("Jenis Barang")
    jumlah = st.number_input("Jumlah", min_value=1)
    kondisi = st.selectbox("Kondisi", ["Baik", "Rusak Ringan", "Rusak Berat"])
    ruang = st.text_input("Ruang / Lokasi")
    pj = st.text_input("Penanggung Jawab")
    if st.button("Simpan"):
        new_data = pd.DataFrame([{
            "ID": id_baru,
            "Nama Barang": nama,
            "Jenis": jenis,
            "Jumlah": jumlah,
            "Kondisi": kondisi,
            "Ruang": ruang,
            "Penanggung Jawab": pj
        }])
        df = pd.concat([df, new_data], ignore_index=True)
        save_data(df)
        st.success("✅ Data berhasil disimpan!")
        st.rerun()

# ======================================
#  MENU LAPORAN PDF
# ======================================
elif menu == "Laporan PDF":
    st.header("🖨️ Cetak Laporan PDF")
    df = load_data()
    ruang_filter = st.selectbox("Filter Ruang", ["Semua"] + sorted(df["Ruang"].unique().tolist()))
    if ruang_filter != "Semua":
        df = df[df["Ruang"] == ruang_filter]

    if st.button("Buat Laporan PDF"):
        filename = generate_pdf(df)
        with open(filename, "rb") as f:
            st.download_button("📄 Unduh Laporan PDF", f, file_name=filename)

# ======================================
#  MENU LOGOUT
# ======================================
elif menu == "Logout":
    st.session_state.logged_in = False
    st.rerun()
