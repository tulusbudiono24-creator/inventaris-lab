import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="Inventaris Sekolah - V8",
    page_icon="🧰",
    layout="wide",
)

st.title("🧰 Aplikasi Inventaris Sekolah - Versi 8")

# CSS Responsif
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        padding: 1rem;
    }
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 0.5rem !important;
        }
        [data-testid="stSidebar"] {
            display: none;
        }
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# DATA AWAL (SESSION STATE)
# =========================
if "ruang_df" not in st.session_state:
    st.session_state["ruang_df"] = pd.DataFrame(columns=["Ruang", "Penanggung Jawab"])

if "barang_df" not in st.session_state:
    st.session_state["barang_df"] = pd.DataFrame(
        columns=["Ruang", "Penanggung Jawab", "Nama Barang", "Jumlah", "Kondisi", "Tahun Pembelian"]
    )

# =========================
# FUNGSI BANTU
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
    st.experimental_rerun()

def export_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Inventaris")
    st.download_button(
        label="📊 Unduh Laporan Excel",
        data=output.getvalue(),
        file_name="laporan_inventaris.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# =========================
# MENU NAVIGASI
# =========================
menu = st.sidebar.radio("📋 Menu", ["Input Ruang", "Input Barang", "Lihat Data Per Ruang", "Laporan Excel (Semua)"])

# =========================
# 1️⃣ INPUT RUANG
# =========================
if menu == "Input Ruang":
    st.header("🏫 Input Ruang & Penanggung Jawab")
    ruang = st.text_input("Nama Ruang (contoh: Lab Komputer 1)")
    pj = st.text_input("Nama Penanggung Jawab (contoh: Tulus Budiono)")
    if st.button("💾 Simpan Ruang"):
        simpan_ruang(ruang, pj)
    if not st.session_state["ruang_df"].empty:
        st.subheader("📘 Daftar Ruang Terdaftar")
        st.dataframe(st.session_state["ruang_df"], use_container_width=True)

# =========================
# 2️⃣ INPUT BARANG
# =========================
elif menu == "Input Barang":
    st.header("🖥️ Input Data Barang Inventaris")
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
# 3️⃣ LIHAT DATA PER RUANG
# =========================
elif menu == "Lihat Data Per Ruang":
    st.header("📋 Lihat Data Barang Per Ruang")

    if st.session_state["barang_df"].empty:
        st.info("Belum ada data barang tersimpan.")
    else:
        ruang_list = st.session_state["barang_df"]["Ruang"].unique().tolist()
        ruang_terpilih = st.selectbox("Pilih Ruang", ruang_list)

        df_ruang = st.session_state["barang_df"][st.session_state["barang_df"]["Ruang"] == ruang_terpilih]

        st.subheader(f"🏠 Data Barang di Ruang: {ruang_terpilih}")
        st.dataframe(df_ruang, use_container_width=True)

        # Unduh Excel per ruang
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_ruang.to_excel(writer, index=False, sheet_name=f"{ruang_terpilih}")
        st.download_button(
            label="📥 Unduh Excel Ruang Ini",
            data=output.getvalue(),
            file_name=f"Laporan_{ruang_terpilih}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # Tabel dengan tombol hapus per data
        st.markdown("### 🗑️ Hapus Data Barang di Ruang Ini")
        for i, row in df_ruang.iterrows():
            cols = st.columns([3, 1])
            with cols[0]:
                st.write(f"**{row['Nama Barang']}** — {row['Kondisi']} ({row['Jumlah']} unit, {row['Tahun Pembelian']})")
            with cols[1]:
                if st.button("Hapus", key=f"hapus_{i}"):
                    hapus_barang(i)

# =========================
# 4️⃣ LAPORAN SEMUA DATA
# =========================
elif menu == "Laporan Excel (Semua)":
    st.header("📊 Laporan Semua Data Inventaris")
    if st.session_state["barang_df"].empty:
        st.info("Tidak ada data yang bisa diekspor.")
    else:
        export_excel(st.session_state["barang_df"])
        st.dataframe(st.session_state["barang_df"], use_container_width=True)
