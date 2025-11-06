import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

# ======================================
#  KONFIGURASI LOGIN
# ======================================
users = {
    "admin": "admin123",
    "petugas1": "petugas123",
    "petugas2": "petugas456"
}

# ======================================
#  FILE DATA
# ======================================
DATA_FILE = "inventaris.csv"

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["ID", "Nama Barang", "Jenis", "Jumlah", "Kondisi", "Ruang", "Penanggung Jawab"])
    df.to_csv(DATA_FILE, index=False)

# ======================================
#  FUNGSI DATA
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
#  LOGIN SISTEM
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
#  DASHBOARD
# ======================================
st.title("🏫 Sistem Manajemen Sarpras SMK KY Ageng Giri")
st.caption(f"👤 Login sebagai: {st.session_state.username}")

menu = st.sidebar.selectbox("Menu", ["Data Ruang & PJ", "Input Barang", "Lihat Data", "Laporan PDF", "Logout"])

# ======================================
#  1️⃣ INPUT RUANG DAN PENANGGUNG JAWAB
# ======================================
if menu == "Data Ruang & PJ":
    st.header("🏠 Data Ruang & Penanggung Jawab")

    if "ruang_aktif" not in st.session_state:
        st.session_state.ruang_aktif = None
        st.session_state.pj_aktif = None

    ruang = st.text_input("Nama Ruang / Lokasi (contoh: Lab Komputer 1, Ruang Guru)")
    pj = st.text_input("Penanggung Jawab Ruang (nama guru/staf)")

    if st.button("Simpan dan Gunakan Ruang Ini"):
        if ruang and pj:
            st.session_state.ruang_aktif = ruang
            st.session_state.pj_aktif = pj
            st.success(f"✅ Ruang '{ruang}' dengan PJ '{pj}' aktif untuk input data.")
            st.balloons()
        else:
            st.warning("⚠️ Harap isi keduanya terlebih dahulu.")

    if st.session_state.ruang_aktif:
        st.info(f"Ruang aktif: **{st.session_state.ruang_aktif}** (PJ: **{st.session_state.pj_aktif}**)")

# ======================================
#  2️⃣ INPUT BARANG SESUAI RUANG AKTIF
# ======================================
elif menu == "Input Barang":
    st.header("➕ Tambah Data Barang")
    df = load_data()

    if not st.session_state.get("ruang_aktif"):
        st.warning("⚠️ Harap tentukan Ruang dan Penanggung Jawab dulu di menu 'Data Ruang & PJ'")
        st.stop()

    id_baru = len(df) + 1
    nama = st.text_input("Nama Barang")
    jenis = st.text_input("Jenis Barang")
    jumlah = st.number_input("Jumlah", min_value=1)
    kondisi = st.selectbox("Kondisi", ["Baik", "Rusak Ringan", "Rusak Berat"])

    if st.button("💾 Simpan Barang"):
        if nama and jenis:
            new_data = pd.DataFrame([{
                "ID": id_baru,
                "Nama Barang": nama,
                "Jenis": jenis,
                "Jumlah": jumlah,
                "Kondisi": kondisi,
                "Ruang": st.session_state.ruang_aktif,
                "Penanggung Jawab": st.session_state.pj_aktif
            }])
            df = pd.concat([df, new_data], ignore_index=True)
            save_data(df)
            st.success("✅ Data barang berhasil disimpan!")
            st.balloons()
            st.rerun()
        else:
            st.warning("⚠️ Lengkapi semua kolom sebelum menyimpan.")

# ======================================
#  3️⃣ LIHAT DAN HAPUS DATA
# ======================================
elif menu == "Lihat Data":
    st.header("📋 Data Inventaris")
    df = load_data()

    if df.empty:
        st.info("Belum ada data inventaris.")
        st.stop()

    ruang_filter = st.selectbox("Filter Ruang", ["Semua"] + sorted(df["Ruang"].unique().tolist()))
    if ruang_filter != "Semua":
        df = df[df["Ruang"] == ruang_filter]

    st.write("Klik tombol 🗑️ di samping untuk menghapus data yang salah:")

    for i, row in df.iterrows():
        col1, col2 = st.columns([5, 1])
        col1.write(f"**{row['ID']}. {row['Nama Barang']}** — {row['Jenis']} ({row['Jumlah']} unit, {row['Kondisi']}) • {row['Ruang']} • PJ: {row['Penanggung Jawab']}")
        if col2.button("🗑️", key=row["ID"]):
            df = df[df["ID"] != row["ID"]]
            save_data(df)
            st.success(f"✅ Data ID {row['ID']} berhasil dihapus!")
            st.balloons()
            st.rerun()

# ======================================
#  4️⃣ LAPORAN PDF
# ======================================
elif menu == "Laporan PDF":
    st.header("🖨️ Cetak Laporan PDF")
    df = load_data()
    if df.empty:
        st.warning("Belum ada data inventaris untuk dicetak.")
        st.stop()

    ruang_filter = st.selectbox("Filter Ruang", ["Semua"] + sorted(df["Ruang"].unique().tolist()))
    if ruang_filter != "Semua":
        df = df[df["Ruang"] == ruang_filter]

    if st.button("📄 Buat Laporan PDF"):
        filename = generate_pdf(df)
        with open(filename, "rb") as f:
            st.download_button("📥 Unduh Laporan PDF", f, file_name=filename)

# ======================================
#  5️⃣ LOGOUT
# ======================================
elif menu == "Logout":
    st.session_state.logged_in = False
    st.session_state.ruang_aktif = None
    st.session_state.pj_aktif = None
    st.rerun()
