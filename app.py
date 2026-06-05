import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- CONFIG & DECORATION ---
st.set_page_config(page_title="My Journal", page_icon="📝")
st.title("📝 Jurnal 3 Quest Saya")

# --- DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl="0")

# Memastikan kolom quest ada di DataFrame jika ini database baru
for col in ["Olahraga", "Belajar", "Journaling"]:
    if col not in df.columns:
        df[col] = False

# --- INPUT FORM ---
st.subheader("Quest Hari Ini:")
col1, col2, col3 = st.columns(3)
with col1:
    q1 = st.checkbox("🏃 Olahraga")
with col2:
    q2 = st.checkbox("📒 Belajar")
with col3:
    q3 = st.checkbox("📖 journaling")

st.subheader("Log Hari Ini")
catatan = st.text_area("Apa yang terjadi hari ini?", placeholder="Tulis kendala atau ceritamu...")

# --- ACTION: SAVE PROGRESS ---
if st.button("Simpan progress"):
    hari_ini = datetime.date.today().strftime('%Y-%m-%d')
    
    # Cek apakah hari ini sudah pernah isi
    if hari_ini in df["Tanggal"].astype(str).values:
        st.warning("Kamu sudah mengisi jurnal hari ini!")
    else:
        # Hitung skor bulat
        skor_akhir = round(((q1 + q2 + q3) / 3) * 100)
        
        # Buat baris baru yang mencakup status masing-masing quest
        new_row = pd.DataFrame([{
            "Tanggal": hari_ini, 
            "Skor": skor_akhir, 
            "Catatan": catatan,
            "Olahraga": q1,
            "Belajar": q2,
            "Journaling": q3
        }])
        
        df_update = pd.concat([df, new_row], ignore_index=True)
        conn.update(data=df_update)
        
        st.success(f"Saved! Skor kamu hari ini: {skor_akhir}%")
        st.balloons()
        st.rerun()

st.divider()
st.subheader("Grafik Progress Kamu")
try:
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    df["Skor"] = pd.to_numeric(df["Skor"])
    
    opsi_waktu = st.radio("Lihat Progress:", ["Seminggu", "Sebulan", "6 Bulan", "1 Tahun", "Semua"], horizontal=True)
    hari_ini_ts = pd.Timestamp.now().normalize()
    
    if opsi_waktu == "Seminggu":
        batas = hari_ini_ts - pd.Timedelta(days=7)
    elif opsi_waktu == "Sebulan":
        batas = hari_ini_ts - pd.Timedelta(days=30)
    elif opsi_waktu == "6 Bulan":
        batas = hari_ini_ts - pd.Timedelta(days=180)
    elif opsi_waktu == "1 Tahun":
        batas = hari_ini_ts - pd.Timedelta(days=365)
    else:
        batas = df["Tanggal"].min()
        
    df_filtered = df[df["Tanggal"] >= batas].copy()
    st.subheader(f"Grafik Progress({opsi_waktu})")
    
    if not df_filtered.empty:
        chart_data = df_filtered.set_index("Tanggal")["Skor"]
        if opsi_waktu == "Semua":
            chart_data = chart_data.resample('ME').mean()
        elif opsi_waktu in ["6 Bulan", "1 Tahun"]:
            chart_data = chart_data.resample('W').mean()
        st.line_chart(chart_data, use_container_width=True)
    else:
        st.info(f"Belum ada data untuk rentang {opsi_waktu}")

    st.divider()
    st.subheader("Detail Jurnal Kamu")
    
    df_tabel = df.copy().iloc[::-1]
    df_tabel["Tanggal"] = pd.to_datetime(df_tabel["Tanggal"]).dt.date
    
    # Bagian perulangan FOR mapping (Sudah disesuaikan dengan angka 1 dan 0)
    for quest in ["Olahraga", "Belajar", "Journaling"]:
        if quest in df_tabel.columns:
            # Kita cek: kalau datanya 1, atau teks "1", atau True murni -> ✅ Selesai. Selain itu ❌ Belum.
            df_tabel[quest] = df_tabel[quest].apply(lambda x: "✅" if str(x).strip() == "1" or x == 1 or x is True else "❌")
            
    st.dataframe(df_tabel, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Belum ada data nih, progress dulu sana!")
