import streamlit as st
st.set_page_config(page_title="Produksi Harian", layout="wide")

import pandas as pd
import os, json
from datetime import date
from utils_pdf import generate_report

# ---------- PATH ----------
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
LIST_FILE   = os.path.join(BASE_DIR, "produk_list.csv")
LAPORAN_DIR = os.path.join(BASE_DIR, "laporan")
os.makedirs(LAPORAN_DIR, exist_ok=True)

# ---------- LOAD MASTER LIST ----------
@st.cache_data
def load_products():
    return pd.read_csv(LIST_FILE)

df = load_products()
kategori_order = df["Kategori"].unique().tolist()

# ---------- UI ----------
tab_input, tab_dash = st.tabs(["📋 Produksi Harian", "📊 Dashboard Historis"])

# ---------- TAB 1: INPUT PRODUKSI ----------
with tab_input:
    st.header("Input Produksi Harian")
    today = date.today().isoformat()
    st.subheader(f"Tanggal: {today}")

    selected = []

    for kategori in kategori_order:
        with st.expander(kategori):
            sub = df[df["Kategori"] == kategori]
            for idx, row in sub.iterrows():
                cols = st.columns([0.4, 0.3, 0.3])
                cek = cols[0].checkbox(row["Nama"], key=f"cek{idx}")

                if cek:
                    masuk  = cols[1].number_input("Masuk",  min_value=0, step=1, key=f"in{idx}")
                    keluar = cols[2].number_input("Keluar", min_value=0, step=1, key=f"out{idx}")
                    selected.append({
                        "Tanggal": today,
                        "Kategori": row["Kategori"],
                        "Nama Barang": row["Nama"],
                        "Masuk": int(masuk),
                        "Keluar": int(keluar)
                    })

    if st.button("💾 Simpan & Export PDF"):
        if not selected:
            st.warning("Belum ada item dipilih.")
        else:
            pdf_bytes = generate_report(selected, kategori_order)
            fname_base = f"produksi_{today}"
            pdf_path   = os.path.join(LAPORAN_DIR, f"{fname_base}.pdf")

            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)

            with open(os.path.join(LAPORAN_DIR, f"{fname_base}.json"), "w") as j:
                json.dump(selected, j)

            st.balloons()
            st.success("✅ PDF berhasil dibuat dan disimpan!")
            st.info(f"📄 File disimpan di: `{pdf_path}`")
            st.download_button("⬇️ Download PDF",
                               data=pdf_bytes,
                               file_name=f"{fname_base}.pdf",
                               mime="application/pdf")

# ---------- TAB 2: DASHBOARD HISTORIS ----------
with tab_dash:
    st.header("Dashboard Historis")

    all_json = [f for f in os.listdir(LAPORAN_DIR) if f.endswith(".json")]
    if not all_json:
        st.info("Belum ada data historis.")
    else:
        recs = []
        for jf in all_json:
            with open(os.path.join(LAPORAN_DIR, jf)) as f:
                recs.extend(json.load(f))

        hist = pd.DataFrame(recs)
        st.subheader("📋 Rekap Tabel")
        st.dataframe(hist)

        st.subheader("📊 Total Masuk vs Keluar per Barang")
        agg = hist.groupby("Nama Barang")[["Masuk", "Keluar"]].sum().reset_index()

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(agg["Nama Barang"], agg["Masuk"], label="Masuk")
        ax.bar(agg["Nama Barang"], agg["Keluar"], bottom=agg["Masuk"], label="Keluar")
        plt.xticks(rotation=90, fontsize=8)
        plt.legend()
        st.pyplot(fig)
