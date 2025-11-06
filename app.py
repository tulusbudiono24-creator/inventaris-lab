import streamlit as st
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="Inventaris Lab Komputer SMK KY Ageng Giri", page_icon="💻")

st.title("💻 Inventaris Lab Komputer SMK KY Ageng Giri")

# --- Login sederhana ---
password = st.text_input("Masukkan Password:", type="password")
if password == "lab2025":
    st.success("Login berhasil!")

    # Form input data
    st.subheader("Tambah Data Inventaris")
    ruang = st.text_input("Nama Ruangan")
    nama_barang = st.text_input("Nama Barang")
    jumlah = st.number_input("Jumlah", min_value=1)
    penanggung = st.text_input("Penanggung Jawab")

    if st.button("Simpan Data"):
        df = pd.DataFrame([[ruang, nama_barang, jumlah, penanggung]],
                          columns=["Ruang", "Nama Barang", "Jumlah", "Penanggung Jawab"])
        try:
            old = pd.read_csv("data_inventaris.csv")
            df = pd.concat([old, df], ignore_index=True)
        except:
            pass
        df.to_csv("data_inventaris.csv", index=False)
        st.success("✅ Data berhasil disimpan!")

    # Tampilkan data
    st.subheader("📊 Data Inventaris")
    try:
        data = pd.read_csv("data_inventaris.csv")
        st.dataframe(data)
    except:
        st.info("Belum ada data tersimpan.")
else:
    st.warning("Masukkan password untuk akses sistem.")
