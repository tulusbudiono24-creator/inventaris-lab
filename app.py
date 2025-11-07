import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Inventaris Sekolah", layout="wide")

# --- LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Login Admin")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == st.secrets["general"]["username"] and password == st.secrets["general"]["password"]:
            st.session_state.logged_in = True
            st.success("Login berhasil ✅")
            st.experimental_rerun()
        else:
            st.error("Username atau password salah ❌")

def logout():
    st.session_state.logged_in = False
    st.experimental_rerun()

if not st.session_state.logged_in:
    login()
    st.stop()

# --- LOGOUT BUTTON ---
st.sidebar.button("Logout", on_click=logout)
st.sidebar.success("Login sebagai admin ✅")

# --- DATA STORAGE ---
if "ruang_data" not in st.session_state:
    st.session_state.ruang_data = []
if "barang_data" not in st.session_state:
    st.session_state.barang_data = []

st.title("🏫 Aplikasi Inventaris Sekolah")

menu = st.sidebar.radio("Menu", ["Input Ruang & Penanggung Jawab", "Input Barang", "Lihat Data per Ruang"])

# --- MENU 1: INPUT RUANG ---
if menu == "Input Ruang & Penanggung Jawab":
    st.header("🏢 Tambah Ruang dan Penanggung Jawab")
    ruang = st.text_input("Nama Ruang")
    pj = st.text_input("Nama Penanggung Jawab")

    if st.button("Simpan Ruang"):
        if ruang and pj:
            st.session_state.ruang_data.append({"Ruang": ruang, "Penanggung Jawab": pj})
            st.success(f"✅ Data {ruang} berhasil disimpan!")
        else:
            st.warning("⚠️ Lengkapi semua kolom!")

    if st.session_state.ruang_data:
        st.subheader("📋 Daftar Ruang dan Penanggung Jawab")
        ruang_df = pd.DataFrame(st.session_state.ruang_data)
        st.dataframe(ruang_df, use_container_width=True)

        hapus = st.selectbox("Pilih Ruang yang akan dihapus", ["-"] + [r["Ruang"] for r in st.session_state.ruang_data])
        if hapus != "-":
            if st.button("Hapus Ruang"):
                st.session_state.ruang_data = [r for r in st.session_state.ruang_data if r["Ruang"] != hapus]
                st.success(f"🗑️ Ruang {hapus} telah dihapus!")

# --- MENU 2: INPUT BARANG ---
elif menu == "Input Barang":
    st.header("📦 Input Barang Inventaris")
    if not st.session_state.ruang_data:
        st.warning("⚠️ Tambahkan dulu Ruang dan Penanggung Jawab di menu pertama!")
    else:
        ruang_terpilih = st.selectbox("Pilih Ruang", [r["Ruang"] for r in st.session_state.ruang_data])
        pj_terpilih = next((r["Penanggung Jawab"] for r in st.session_state.ruang_data if r["Ruang"] == ruang_terpilih), "")
        st.info(f"Penanggung Jawab: **{pj_terpilih}**")

        nama_barang = st.text_input("Nama Barang")
        jumlah = st.number_input("Jumlah", min_value=1)
        kondisi = st.selectbox("Kondisi", ["Baik", "Rusak", "Perlu Perbaikan"])
        tahun = st.number_input("Tahun Pembelian", min_value=2000, max_value=2100, step=1)

        if st.button("Simpan Barang"):
            st.session_state.barang_data.append({
                "Ruang": ruang_terpilih,
                "Penanggung Jawab": pj_terpilih,
                "Nama Barang": nama_barang,
                "Jumlah": jumlah,
                "Kondisi": kondisi,
                "Tahun": tahun
            })
            st.success("✅ Data barang berhasil disimpan!")

        if st.session_state.barang_data:
            st.subheader("📋 Daftar Barang")
            df_barang = pd.DataFrame(st.session_state.barang_data)
            st.dataframe(df_barang, use_container_width=True)

            hapus_brg = st.selectbox("Pilih Barang yang akan dihapus", ["-"] + [b["Nama Barang"] for b in st.session_state.barang_data])
            if hapus_brg != "-":
                if st.button("Hapus Barang"):
                    st.session_state.barang_data = [b for b in st.session_state.barang_data if b["Nama Barang"] != hapus_brg]
                    st.success(f"🗑️ Barang {hapus_brg} telah dihapus!")

# --- MENU 3: LIHAT DATA PER RUANG ---
elif menu == "Lihat Data per Ruang":
    st.header("📊 Laporan Data Inventaris per Ruang")

    if not st.session_state.barang_data:
        st.info("Belum ada data barang yang tersimpan.")
    else:
        ruang_unik = sorted(set(b["Ruang"] for b in st.session_state.barang_data))
        pilih_ruang = st.selectbox("Pilih Ruang", ruang_unik)

        df_laporan = pd.DataFrame([b for b in st.session_state.barang_data if b["Ruang"] == pilih_ruang])
        st.dataframe(df_laporan, use_container_width=True)

        # Ekspor ke Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df_laporan.to_excel(writer, index=Fals
