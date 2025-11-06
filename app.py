import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

st.set_page_config(page_title="Inventaris Sekolah", page_icon="🧰", layout="centered")

st.title("🧰 Aplikasi Inventaris Sekolah - Versi 6")

# =======================
# Inisialisasi Session
# =======================
if "ruang_df" not in st.session_state:
    st.session_state["ruang_df"] = pd.DataFrame(columns=["Ruang", "Penanggung Jawab"])
if "barang_df" not in st.session_state:
    st.session_state["barang_df"] = pd.DataFrame(columns=["Ruang", "Penanggung Jawab", "Nama Barang", "Jumlah", "Kondisi"])

# =======================
# Fungsi bantu
# =======================
def simpan_ruang(ruang, pj):
    if ruang and pj:
        st.session_state["ruang_df"] = pd.concat([st.session_state["ruang_df"], pd.DataFrame([[ruang, pj]], columns=["Ruang", "Penanggung Jawab"])], ignore_index=True)
        st.success("✅ Data ruang berhasil disimpan!")
    else:
        st.warning("⚠️ Harap isi Ruang dan Penanggung Jawab terlebih dahulu.")

def simpan_barang(ruang, pj, nama, jumlah, kondisi):
    if not ruang or not pj:
        st.warning("⚠️ Harap pilih Ruang dan Penanggung Jawab!")
    elif nama and jumlah and kondisi:
        st.session_state["barang_df"] = pd.concat([
            st.session_state["barang_df"],
            pd.DataFrame([[ruang, pj, nama, jumlah, kondisi]], columns=["Ruang", "Penanggung Jawab", "Nama Barang", "Jumlah", "Kondisi"])
        ], ignore_index=True)
        st.success("✅ Barang berhasil disimpan!")
    else:
        st.warning("⚠️ Lengkapi semua kolom!")

def hapus_barang(index):
    st.session_state["barang_df"].drop(index, inplace=True)
    st.session_state["barang_df"].reset_index(drop=True, inplace=True)
    st.success("🗑️ Data berhasil dihapus.")

def buat_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Laporan Inventaris Sekolah", ln=True, align="C")
    pdf.ln(10)

    for ruang, group in st.session_state["barang_df"].groupby(["Ruang", "Penanggung Jawab"]):
        ruang_nama, pj = ruang
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Ruang: {ruang_nama} | PJ: {pj}", ln=True)
        pdf.set_font("Arial", "", 11)
        for i, row in group.iterrows():
            pdf.cell(0, 6, f"- {row['Nama Barang']} ({row['Jumlah']}) [{row['Kondisi']}]", ln=True)
        pdf.ln(5)

    buffer = io.BytesIO()
    pdf.output(buffer)
    st.download_button("📄 Unduh Laporan PDF", buffer.getvalue(), file_name="laporan_inventaris.pdf")

# =======================
# Menu Aplikasi
# =======================
menu = st.sidebar.radio("📋 Menu", ["Input Ruang", "Input Barang", "Lihat Data", "Laporan PDF"])

# -----------------------
# 1️⃣ Input Ruang
# -----------------------
if menu == "Input Ruang":
    st.header("🏫 Input Ruang & Penanggung Jawab")
    ruang = st.text_input("Nama Ruang (contoh: Lab DKV)")
    pj = st.text_input("Nama Penanggung Jawab (contoh: Tulus Budiono)")
    if st.button("💾 Simpan Ruang"):
        simpan_ruang(ruang, pj)
    if not st.session_state["ruang_df"].empty:
        st.subheader("📘 Data Ruang Tersimpan")
        st.dataframe(st.session_state["ruang_df"])

# -----------------------
# 2️⃣ Input Barang
# -----------------------
elif menu == "Input Barang":
    st.header("🖥️ Input Barang")
    if st.session_state["ruang_df"].empty:
        st.warning("⚠️ Harap isi data Ruang & Penanggung Jawab terlebih dahulu di menu sebelah kiri.")
    else:
        ruang = st.selectbox("Pilih Ruang", st.session_state["ruang_df"]["Ruang"].unique())
        pj_filter = st.session_state["ruang_df"][st.session_state["ruang_df"]["Ruang"] == ruang]["Penanggung Jawab"].values[0]
        st.info(f"Penanggung Jawab Otomatis: {pj_filter}")
        nama = st.text_input("Nama Barang")
        jumlah = st.number_input("Jumlah", min_value=1, step=1)
        kondisi = st.selectbox("Kondisi", ["Baik", "Rusak Ringan", "Rusak Berat"])
        if st.button("💾 Simpan Barang"):
            simpan_barang(ruang, pj_filter, nama, jumlah, kondisi)

# -----------------------
# 3️⃣ Lihat Data
# -----------------------
elif menu == "Lihat Data":
    st.header("📋 Data Inventaris Barang")
    if st.session_state["barang_df"].empty:
        st.info("Belum ada data barang tersimpan.")
    else:
        for i, row in st.session_state["barang_df"].iterrows():
            with st.expander(f"{row['Nama Barang']} - {row['Ruang']}"):
                st.write(f"📦 Jumlah: {row['Jumlah']}")
                st.write(f"🧍 Penanggung Jawab: {row['Penanggung Jawab']}")
                st.write(f"🏠 Ruang: {row['Ruang']}")
                st.write(f"⚙️ Kondisi: {row['Kondisi']}")
                if st.button("🗑️ Hapus", key=f"hapus_{i}"):
                    hapus_barang(i)
                    st.experimental_rerun()

# -----------------------
# 4️⃣ Laporan PDF
# -----------------------
elif menu == "Laporan PDF":
    st.header("📄 Cetak Laporan Inventaris")
    if st.session_state["barang_df"].empty:
        st.info("Tidak ada data untuk dibuat laporan.")
    else:
        buat_pdf()
