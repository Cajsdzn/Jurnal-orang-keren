import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- CONFIG & DECORATION ---
st.set_page_config(page_title="My Journal", page_icon="📝")
st.title("📝 Jurnal 6 Quest Saya")

# --- DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl="0")

# Daftar 6 quest baru
ALL_QUESTS = ["Olahraga", "Belajar", "Journaling", "Tidur", "Screen Time", "Pantangan"]

# Memastikan semua kolom quest ada di DataFrame jika ini database baru
for col in ALL_QUESTS:
    if col not in df.columns:
        df[col] = False

# --- TIMEZONE CHECK (WIB / UTC+7) ---
# Menggunakan timezone offset manual (+7 jam) agar aman di server mana pun
jam_sekarang_wib = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).time()

# Logika penguncian jam
belajar_terkunci = jam_sekarang_wib >= datetime.time(20, 0)
tidur_terkunci = jam_sekarang_wib >= datetime.time(22, 0)

# --- INPUT FORM ---
st.subheader("Quest Hari Ini:")

# Info waktu sekarang untuk user
st.caption(f"Waktu Sekarang (WIB): {jam_sekarang_wib.strftime('%H:%M')}")

# Baris pertama (Quest Lama)
col1, col2, col3 = st.columns(3)
with col1:
    q1 = st.checkbox("🏃 Olahraga")
with col2:
    # Jika sudah lewat jam 20:00 WIB, checkbox akan di-disable
    if belajar_terkunci:
        st.info("🔒 Belajar (Terkunci)")
        q2 = False
    else:
        q2 = st.checkbox("📒 Belajar")
with col3:
    q3 = st.checkbox("📖 Journaling")

# Baris kedua (Quest Baru)
col4, col5, col6 = st.columns(3)
with col4:
    # Jika sudah lewat jam 22:00 WIB, checkbox akan di-disable
    if tidur_terkunci:
        st.info("🔒 Tidur (Terkunci)")
        q4 = False
    else:
        q4 = st.checkbox("🛌 Tidur")
with col5:
    q5 = st.checkbox("📱 Screen Time")
with col6:
    q6 = st.checkbox("🛑 Pantangan")

st.subheader("Log Hari Ini")
catatan = st.text_area("Apa yang terjadi hari ini?", placeholder="Tulis kendala atau ceritamu...")

# --- ACTION: SAVE PROGRESS ---
if st.button("Simpan progress"):
    # Mengambil tanggal hari ini versi WIB
    hari_ini = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime('%Y-%m-%d')
    
    # Cek apakah hari ini sudah pernah isi
    if hari_ini in df["Tanggal"].astype(str).values:
        st.warning("Kamu sudah mengisi jurnal hari ini!")
    else:
        # Hitung skor bulat dibagi 6 quest
        skor_akhir = round(((q1 + q2 + q3 + q4 + q5 + q6) / 6) * 100)
        
        # Buat baris baru mencakup semua 6 quest
        new_row = pd.DataFrame([{
            "Tanggal": hari_ini, 
            "Skor": skor_akhir, 
            "Catatan": catatan,
            "Olahraga": q1,
            "Belajar": q2,
            "Journaling": q3,
            "Tidur": q4,
            "Screen Time": q5,
            "Pantangan": q6
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
    
    # Looping mapping disesuaikan ke 6 quest
    for quest in ALL_QUESTS:
        if quest in df_tabel.columns:
            df_tabel[quest] = df_tabel[quest].apply(lambda x: "✅" if str(x).strip() == "1" or x == 1 or x is True else "❌")
            
    st.dataframe(df_tabel, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Belum ada data nih, progress dulu sana!")
