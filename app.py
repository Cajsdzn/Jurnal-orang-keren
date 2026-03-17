import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
st.set_page_config(page_title="My Journal", page_icon="📝")
st.title("📝 Jurnal 3 Quest Saya")
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl="0")
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
total_selesai = q1 + q2 + q3
skor_hari_ini = (total_selesai / 3) * 100
if st.button("Simpan progress"):
    import datetime
    hari_ini = datetime.date.today().strftime('%Y-%m-%d')
    if hari_ini in df["Tanggal"].astype(str).values:
            st.warning("Kamu sudah mengisi jurnal hari ini!")
    else:
        skor_akhir = round(( (q1 + q2 + q3) / 3 ) * 100)
        new_row = pd.DataFrame([{"Tanggal": hari_ini, "Skor": skor_akhir, "Catatan": catatan}])
        df_update = pd.concat([df, new_row], ignore_index=True)
        st.success(f"Saved! Skor kamu hari ini: {skor_akhir}%")
        conn.update(data=df_update)
        st.balloons
        st.rerun()
st.divider()
st.subheader("Grafik Progress Kamu")
try:
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    df["Skor"] = pd.to_numeric(df["Skor"])
    opsi_waktu = st.radio("Lihat Progress:",["Seminggu", "Sebulan", "6 Bulan", "1 Tahun", "Semua"], horizontal=True)
    hari_ini = pd.Timestamp.now().normalize()
    if opsi_waktu == "Seminggu":
        batas = hari_ini - pd.Timedelta(days=7)
    elif opsi_waktu == "Sebulan":
        batas = hari_ini - pd.Timedelta(days=30)
    elif opsi_waktu == "6 Bulan":
        batas = hari_ini - pd.Timedelta(days=180)
    elif opsi_waktu == "1 Tahun":
        batas =  hari_ini - pd.Timedelta(days=365)
    else:
        batas = df["Tanggal"].min()
    df_filtered = df[df["Tanggal"]>= batas].copy()
    st.subheader (f"Grafik Progress({opsi_waktu})")
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
    df_tabel["Tanggal"] = df_tabel["Tanggal"] = df_tabel["Tanggal"].dt.date
    st.dataframe(df_tabel,use_container_width=True)
except Exception as e:
    st.error(f"Error:{e}")
    st.info("Belum ada data nih, progress dulu sana!")}")
    st.info("Belum ada data nih, progress dulu sana!")
