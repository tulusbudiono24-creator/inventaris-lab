import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# Konfigurasi Halaman
# =========================
st.set_page_config(
    page_title="Inventaris Sekolah - V7",
    page_icon="🧰",
    layout="wide",
)

st.title("🧰 Aplikasi Inventaris Sekolah - Versi 7")

# CSS responsif untuk HP & desktop
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        padding: 1rem;
    }
    [data-testid="stSidebar"] {
        width: 280px;
    }
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            display: none;
        }
        .block-container {
            padding: 1rem 0.5rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# Inisialisasi Session State
# =========================
if "ruang_df" not in st.session_state:
    st.session_state["ruang_df"] = pd.DataFrame(columns=["Ruang", "Penanggung Jawab"])
if "barang_df" not in st.session_state:
    st.session_state["barang_df"] = pd.DataFrame(
        columns=["Ruang", "Penanggung Jawab", "Nama Barang", "Jumlah", "Kondisi", "Tahun Pembelian"]
    )

# =========================
# Fungsi bantu
# =========================
def simpan_ruang(ruang, pj):
    if ruang and pj:
        st.session_state["ruang_df"] = pd.concat(
            [st.session_state["ruang_df"], pd.DataFrame([[ruang, pj]], columns=["Ruang", "Penanggung Jawab"])],
            ignore_index=True,
        )
        st.success("✅ Data ruang berhasil disimpan!")
    else:
        st.warning("⚠️ Isi semua kolom sebelum menyimpan!")

def simpan_barang(ruang, pj, nama, jumlah, kondisi, tahun):
    if not ruang or not pj:
        st.warning("⚠️ Harap pilih Ruang dan Penanggung Jawab!")
    elif nama and jumlah and kondisi and tahun:
        st.session_state["barang_df"] = pd.concat([
            st.session_state["barang_df"],
            pd.DataFrame([[ruang, pj, nama, jumlah, kondisi, tahun]],
                         columns=["Ruang", "Penanggung Jawab", "Nama Barang", "Jumlah", "Kondisi", "Tahun Pembelian"])
        ], ignore_index=True)
        st.success("✅ Barang berhasil disimpan!")
    else:
        st.warning("⚠️ Lengkapi semua kolom!")

def hapus_barang(index):
    st.session_state["barang_df"].drop(index, inplace=True)
    st.session_state["barang_df"].reset_index(drop=True, inplace=True)
    st.success("🗑️ Data berhasil dihapus.")

def export_excel():
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        st.session_state["barang_df"].to_excel(writer, index=False, sheet_name="Inventaris")
    st.download_button(
        label="📊 Unduh Laporan Excel",
        data=output.getvalue(),
        file_name="laporan_inventaris.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# =========================
# Menu Navigasi
# =========================
menu = st.sidebar.radio("📋 Menu", ["Input Ruang", "Input Barang", "Lihat Data", "Laporan Excel"])

# =========================
# 1️⃣ Input Ruang
# =========================
if menu == "Input Ruang":
    st.header("🏫 Input Ruang & Penanggung Jawab")
    ruang = st.text_input("Nama Ruang (contoh: Lab DKV)")
    pj = st.text_input("Nama Penanggung Jawab (contoh: Tulus Budiono)")
    if st.button("💾 Simpan Ruang"):
        simpan_ruang(ruang, pj)
    if not st.session_state["ruang_df"].empty:
        st.subheader("📘 Daftar Ruang")
        st.dataframe(st.session_state["ruang_df"], use_container_width=True)

# =========================
# 2️⃣ Input Barang
# =========================
elif menu == "Input Barang":
    st.header("🖥️ Input Data Barang")
    if st.session_state["ruang_df"].empty:
        st.warning("⚠️ Harap isi data Ruang & Penanggung Jawab terlebih dahulu di menu Input Ruang.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            ruang = st.selectbox("Pilih Ruang", st.session_state["ruang_df"]["Ruang"].unique())
        with col2:
            pj = st.session_state["ruang_df"][st.session_state["ruang_df"]["Ruang"] == ruang]["Penanggung Jawab"].values[0]
            st.info(f"Penanggung Jawab: **{pj}**")

        nama = st.text_input("Nama Barang")
        jumlah = st.number_input("Jumlah Barang", min_value=1, step=1)
        kondisi = st.selectbox("Kondisi Barang", ["Baik", "Rusak Ringan", "Rusak Berat"])
        tahun = st.number_input("Tahun Pembelian", min_value=2000, max_value=2030, step=1)

        if st.button("💾 Simpan Barang"):
            simpan_barang(ruang, pj, nama, jumlah, kondisi, tahun)

# =========================
# 3️⃣ Lihat Data
# =========================
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
                st.write(f"📅 Tahun Pembelian: {row['Tahun Pembelian']}")
                if st.button("🗑️ Hapus", key=f"hapus_{i}"):
                    hapus_barang(i)
                    st.experimental_rerun()

# =========================
# 4️⃣ Laporan Excel
# =========================
elif menu == "Laporan Excel":
    st.header("📊 Laporan Inventaris (Excel)")
    if st.session_state["barang_df"].empty:
        st.info("Tidak ada data untuk diekspor.")
    else:
        export_excel()
        st.dataframe(st.session_state["barang_df"], use_container_width=True)
