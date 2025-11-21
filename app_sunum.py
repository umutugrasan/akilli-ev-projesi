import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- 1. VERİTABANI BAĞLANTISI ---
def get_connection():
    conn = sqlite3.connect('smart_security_final.db')
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# --- VERİ İŞLEMLERİ (YÜKLEME / SİLME) ---
def reset_and_populate_data():
    conn = get_connection()
    c = conn.cursor()
    tables = ['TETIKLER', 'KAYDEDER', 'VARDIR', 'KULLANICI_EPOSTA', 'ALARM', 'OLAY', 'GUVENLIK_CIHAZI', 'KULLANICI', 'AKILLI_EV']
    for table in tables: c.execute(f"DELETE FROM {table}")
    
    # VERİLER
    c.executemany("INSERT INTO AKILLI_EV VALUES (?,?,?)", [(12, 'Kızıltoprak Sk. No:15 Bandırma/Balıkesir', 'Yunus Özdemir'), (25, 'Atatürk Cad. No:78 İstanbul/Kadıköy', 'Süleyman Emre Arlı'), (38, 'İnönü Bulvarı No:142 Ankara/Çankaya', 'Ömer Faruk Külçeler')])
    c.executemany("INSERT INTO KULLANICI VALUES (?,?,?,?)", [(101, 'Umut', 'Uğraşan', 12), (102, 'Mehmet', 'Yılmaz', 25), (103, 'Ayşe', 'Kara', 38), (104, 'Veli', 'Demir', 12)])
    c.executemany("INSERT INTO KULLANICI_EPOSTA VALUES (?,?)", [(101, 'umut@mail.com'), (102, 'mehmet.yilmaz@gmail.com'), (103, 'ayse.kara@outlook.com'), (104, 'veli.demir@yahoo.com')])
    c.executemany("INSERT INTO GUVENLIK_CIHAZI VALUES (?,?,?)", [(7, 'Kamera', 'Aktif'), (8, 'Hareket Sensörü', 'İnaktif'), (9, 'Kapı Kilidi', 'İnaktif'), (10, 'Duman Dedektörü', 'Aktif'), (11, 'Cam Kırılma Sensörü', 'Aktif')])
    c.executemany("INSERT INTO VARDIR VALUES (?,?)", [(12, 7), (12, 8), (25, 9), (25, 10)])
    c.executemany("INSERT INTO OLAY VALUES (?,?,?,?)", [(4096, 'Hareket Algılandı', '2025-11-02', '19:29:42'), (4097, 'Kapı Açıldı', '2025-11-03', '08:15:20'), (4098, 'Duman Tespit Edildi', '2025-11-05', '14:45:10'), (4099, 'Cam Kırılması Algılandı', '2025-11-07', '02:30:55')])
    c.executemany("INSERT INTO KAYDEDER VALUES (?,?)", [(7, 4096), (8, 4096), (9, 4097), (10, 4098), (11, 4099)])
    c.executemany("INSERT INTO ALARM VALUES (?,?,?,?)", [(6071, 'Kapalı', '2025-11-02', '19:29:48'), (6072, 'Kapalı', '2025-11-03', '08:15:25'), (6073, 'Açık', '2025-11-05', '14:45:15'), (6074, 'Açık', '2025-11-07', '02:31:00')])
    c.executemany("INSERT INTO TETIKLER VALUES (?,?)", [(4098, 6073), (4099, 6074)])
    
    conn.commit()
    conn.close()

def clear_all_data():
    conn = get_connection()
    c = conn.cursor()
    for table in ['TETIKLER', 'KAYDEDER', 'VARDIR', 'KULLANICI_EPOSTA', 'ALARM', 'OLAY', 'GUVENLIK_CIHAZI', 'KULLANICI', 'AKILLI_EV']:
        c.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()

# --- AYARLAR ---
st.set_page_config(page_title="Smart Security Admin", page_icon="🛡️", layout="wide")

# --- STİL (BOZULMAYAN MODERN TASARIM) ---
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    [data-testid="stSidebar"] {background-color: #161b22; border-right: 1px solid #30363d;}
    .stMetric {background-color: #0d1117; border: 1px solid #30363d; padding: 10px; border-radius: 8px;}
    h1, h2, h3 {color: #f0f6fc;}
    .stButton>button {width: 100%; border-radius: 5px;}
</style>
""", unsafe_allow_html=True)

conn = get_connection()
c = conn.cursor()

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ ADMIN PANEL")
    st.caption("v3.0 Stable")
    st.divider()
    
    col1, col2 = st.columns(2)
    if col1.button("📥 Yükle"):
        reset_and_populate_data()
        st.toast("Veriler Yüklendi!", icon="✅")
        time.sleep(1)
        st.rerun()
    if col2.button("🗑️ Sıfırla"):
        clear_all_data()
        st.toast("Temizlendi!", icon="🧹")
        time.sleep(1)
        st.rerun()
        
    st.divider()
    menu = st.radio("NAVİGASYON", 
        ["📊 Dashboard", "🏠 Ev & Kullanıcı", "📹 Cihaz Yönetimi", "⚡ Olay & Alarm", "📈 Analitik Raporlar", "📂 Tüm Tablolar"])

# =============================================================================
# 1. DASHBOARD
# =============================================================================
if menu == "📊 Dashboard":
    st.title("📊 Sistem Genel Bakış")
    
    try:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🏠 Evler", c.execute("SELECT COUNT(*) FROM AKILLI_EV").fetchone()[0])
        c2.metric("👤 Kullanıcılar", c.execute("SELECT COUNT(*) FROM KULLANICI").fetchone()[0])
        c3.metric("📹 Cihazlar", c.execute("SELECT COUNT(*) FROM GUVENLIK_CIHAZI WHERE Durumu='Aktif'").fetchone()[0])
        c4.metric("🚨 Alarmlar", c.execute("SELECT COUNT(*) FROM ALARM").fetchone()[0])
    except:
        st.info("Veritabanı boş.")

    st.subheader("📝 Canlı Olay Akışı")
    q = """SELECT O.Tarih, O.Saat, O.Turu as Olay, C.Turu as Cihaz, E.Adres 
           FROM KAYDEDER K JOIN OLAY O ON K.OlayNumara=O.Numara 
           JOIN GUVENLIK_CIHAZI C ON K.GuvenlikCihaziNumara=C.Numara 
           JOIN VARDIR V ON C.Numara=V.GuvenlikCihaziNumara 
           JOIN AKILLI_EV E ON V.AkilliEvNumara=E.Numara 
           ORDER BY O.Tarih DESC, O.Saat DESC LIMIT 5"""
    try:
        st.dataframe(pd.read_sql(q, conn), use_container_width=True, hide_index=True)
    except:
        st.write("Veri yok.")

# =============================================================================
# 2. EV & KULLANICI
# =============================================================================
elif menu == "🏠 Ev & Kullanıcı":
    st.title("🏠 Mülk ve Kullanıcı Yönetimi")
    t1, t2 = st.tabs(["🏠 Ev İşlemleri", "👤 Kullanıcı & E-Posta"])
    
    # EV SEKMESİ
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown("**Yeni Ev Ekle**")
                with st.form("ev_add"):
                    eno = st.number_input("Ev No", min_value=1)
                    eadr = st.text_input("Adres")
                    esahip = st.text_input("Sahip")
                    if st.form_submit_button("Kaydet"):
                        try:
                            c.execute("INSERT INTO AKILLI_EV VALUES (?,?,?)", (eno, eadr, esahip))
                            conn.commit()
                            st.success("Eklendi")
                            time.sleep(0.5); st.rerun()
                        except: st.error("Hata")
        
        with c2:
            with st.container(border=True):
                st.markdown("**Ev Listesi & Düzenle/Sil**")
                s_ev = st.text_input("🔍 Ev Ara")
                q_ev = "SELECT * FROM AKILLI_EV"
                df = pd.read_sql(q_ev, conn)
                if s_ev: df = df[df['Adres'].str.contains(s_ev, case=False)]
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                evler = c.execute("SELECT Numara, Adres FROM AKILLI_EV").fetchall()
                if evler:
                    ev_d = {f"{e[0]} - {e[1]}": e[0] for e in evler}
                    sel = st.selectbox("İşlem İçin Ev Seç", list(ev_d.keys()))
                    c_up, c_del = st.columns(2)
                    if c_up.button("Adres Güncelle"):
                        new_a = st.text_input("Yeni Adres", key="n_adr") # Modal olmadığı için basit geçiyoruz
                        # Basitlik için burada input alamıyoruz, güncelleme mantığı form gerektirir
                        st.info("Güncelleme için yukarıdaki formu kullanın (Basitleştirildi).")
                    if c_del.button("🗑️ Seçili Evi Sil"):
                        c.execute("DELETE FROM AKILLI_EV WHERE Numara=?", (ev_d[sel],))
                        conn.commit()
                        st.rerun()

    # KULLANICI SEKMESİ
    with t2:
        c1, c2 = st.columns(2)
        evler = c.execute("SELECT Numara, Adres FROM AKILLI_EV").fetchall()
        ev_d = {f"{e[0]}": e[0] for e in evler}
        
        with c1:
            with st.container(border=True):
                st.markdown("**Kullanıcı Ekle**")
                with st.form("usr_add"):
                    uid = st.number_input("TC No", min_value=1)
                    uad = st.text_input("Ad")
                    usoy = st.text_input("Soyad")
                    uev = st.selectbox("Ev Seç", list(ev_d.keys()) if ev_d else [])
                    if st.form_submit_button("Kaydet"):
                        if uev:
                            try:
                                c.execute("INSERT INTO KULLANICI VALUES (?,?,?,?)", (uid, uad, usoy, ev_d[uev]))
                                conn.commit()
                                st.success("Eklendi")
                            except: st.error("Hata")
        
        with c2:
            with st.container(border=True):
                st.markdown("**Kullanıcı Listesi**")
                s_usr = st.text_input("🔍 Kullanıcı Ara")
                df_u = pd.read_sql("SELECT * FROM KULLANICI", conn)
                if s_usr: df_u = df_u[df_u['Adi'].str.contains(s_usr, case=False)]
                st.dataframe(df_u, use_container_width=True, hide_index=True)
                
                # Silme
                users = c.execute("SELECT KimlikNo, Adi FROM KULLANICI").fetchall()
                if users:
                    u_del_d = {f"{u[1]} ({u[0]})": u[0] for u in users}
                    u_sel = st.selectbox("Silinecek Kişi", list(u_del_d.keys()))
                    if st.button("Kullanıcıyı Sil"):
                        c.execute("DELETE FROM KULLANICI WHERE KimlikNo=?", (u_del_d[u_sel],))
                        conn.commit()
                        st.rerun()

        st.divider()
        st.subheader("✉️ E-Posta Yönetimi")
        ce1, ce2 = st.columns(2)
        with ce1:
            if users:
                u_m_sel = st.selectbox("Kullanıcı Seç (Mail)", list(u_del_d.keys()))
                new_m = st.text_input("E-posta Adresi")
                if st.button("Mail Ekle"):
                    try:
                        c.execute("INSERT INTO KULLANICI_EPOSTA VALUES (?,?)", (u_del_d[u_m_sel], new_m))
                        conn.commit()
                        st.success("Eklendi")
                        time.sleep(0.5); st.rerun()
                    except: st.error("Hata")
        with ce2:
            if users:
                st.dataframe(pd.read_sql(f"SELECT * FROM KULLANICI_EPOSTA WHERE KullaniciKimlikNo={u_del_d[u_m_sel]}", conn), use_container_width=True)

# =============================================================================
# 3. CİHAZ YÖNETİMİ
# =============================================================================
elif menu == "📹 Cihaz Yönetimi":
    st.title("📹 Cihaz Yönetimi")
    t1, t2 = st.tabs(["Cihazlar", "Ev Bağlantıları"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown("**Cihaz Ekle**")
                with st.form("dev_add"):
                    dno = st.number_input("Seri No", min_value=1)
                    dtur = st.selectbox("Tür", ["Kamera", "Hareket Sensörü", "Kilit", "Duman Dedektörü", "Cam Sensörü"])
                    ddur = st.selectbox("Durum", ["Aktif", "İnaktif"])
                    if st.form_submit_button("Ekle"):
                        try:
                            c.execute("INSERT INTO GUVENLIK_CIHAZI VALUES (?,?,?)", (dno, dtur, ddur))
                            conn.commit()
                            st.success("Eklendi")
                        except: st.error("Hata")
        with c2:
            st.markdown("**Cihaz Listesi**")
            devs = c.execute("SELECT Numara, Turu FROM GUVENLIK_CIHAZI").fetchall()
            df_d = pd.read_sql("SELECT * FROM GUVENLIK_CIHAZI", conn)
            st.dataframe(df_d, use_container_width=True, hide_index=True)
            
            if devs:
                d_del_d = {f"{d[1]} ({d[0]})": d[0] for d in devs}
                d_sel = st.selectbox("İşlem Yapılacak Cihaz", list(d_del_d.keys()))
                col_up, col_del = st.columns(2)
                if col_up.button("Durumu Değiştir (Aktif/İnaktif)"):
                    # Basit toggle mantığı
                    curr = c.execute("SELECT Durumu FROM GUVENLIK_CIHAZI WHERE Numara=?", (d_del_d[d_sel],)).fetchone()[0]
                    new_s = "İnaktif" if curr == "Aktif" else "Aktif"
                    c.execute("UPDATE GUVENLIK_CIHAZI SET Durumu=? WHERE Numara=?", (new_s, d_del_d[d_sel]))
                    conn.commit()
                    st.rerun()
                if col_del.button("Cihazı Sil"):
                    c.execute("DELETE FROM GUVENLIK_CIHAZI WHERE Numara=?", (d_del_d[d_sel],))
                    conn.commit()
                    st.rerun()

    with t2:
        c1, c2 = st.columns(2)
        with c1:
            if devs and ev_d:
                st.markdown("**Bağlantı Kur**")
                sel_d = st.selectbox("Cihaz", list(d_del_d.keys()), key="lnk_d")
                sel_e = st.selectbox("Ev", list(ev_d.keys()), key="lnk_e")
                if st.button("Bağla"):
                    try:
                        c.execute("INSERT INTO VARDIR VALUES (?,?)", (ev_d[sel_e], d_del_d[sel_d]))
                        conn.commit()
                        st.success("Bağlandı")
                        time.sleep(0.5); st.rerun()
                    except: st.warning("Zaten bağlı")
        with c2:
            st.markdown("**Mevcut Bağlantılar (VARDIR)**")
            st.dataframe(pd.read_sql("SELECT * FROM VARDIR", conn), use_container_width=True)

# =============================================================================
# 4. OLAY & ALARM
# =============================================================================
elif menu == "⚡ Olay & Alarm":
    st.title("⚡ Olay & Alarm")
    t1, t2 = st.tabs(["Olaylar", "Alarmlar"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown("**Olay Ekle**")
                with st.form("olay_add"):
                    oid = st.number_input("Olay ID", min_value=4000)
                    otur = st.text_input("Tür", "Hareket")
                    if st.form_submit_button("Kaydet"):
                        now = datetime.now()
                        try:
                            c.execute("INSERT INTO OLAY VALUES (?,?,?,?)", (oid, otur, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")))
                            conn.commit()
                            st.success("Eklendi")
                        except: st.error("Hata")
        with c2:
            st.markdown("**Olay Listesi**")
            st.dataframe(pd.read_sql("SELECT * FROM OLAY ORDER BY Numara DESC", conn), use_container_width=True, hide_index=True)
            
            # İlişkilendirme
            olays = c.execute("SELECT Numara, Turu FROM OLAY").fetchall()
            devs = c.execute("SELECT Numara, Turu FROM GUVENLIK_CIHAZI").fetchall()
            if olays and devs:
                o_d = {f"{o[1]} ({o[0]})": o[0] for o in olays}
                d_d = {f"{d[1]} ({d[0]})": d[0] for d in devs}
                st.divider()
                st.markdown("**Cihazla İlişkilendir (KAYDEDER)**")
                s_o = st.selectbox("Olay", list(o_d.keys()))
                s_d = st.selectbox("Cihaz", list(d_d.keys()))
                if st.button("İlişkilendir"):
                    try:
                        c.execute("INSERT INTO KAYDEDER VALUES (?,?)", (d_d[s_d], o_d[s_o]))
                        conn.commit()
                        st.success("Yapıldı")
                    except: st.error("Hata")

    with t2:
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown("**Alarm Ekle**")
                with st.form("alm_add"):
                    aid = st.number_input("Alarm ID", min_value=6000)
                    if st.form_submit_button("Başlat"):
                        now = datetime.now()
                        try:
                            c.execute("INSERT INTO ALARM VALUES (?,?,?,?)", (aid, "AÇIK", now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")))
                            conn.commit()
                            st.success("Başladı")
                        except: st.error("Hata")
        with c2:
            st.markdown("**Alarm Listesi**")
            st.dataframe(pd.read_sql("SELECT * FROM ALARM ORDER BY Numara DESC", conn), use_container_width=True, hide_index=True)
            
            alarms = c.execute("SELECT Numara FROM ALARM").fetchall()
            if alarms and olays:
                a_d = {f"Alarm {a[0]}": a[0] for a in alarms}
                st.divider()
                st.markdown("**Olayla Eşleştir (TETİKLER)**")
                s_a = st.selectbox("Alarm", list(a_d.keys()))
                s_trig = st.selectbox("Tetikleyen Olay", list(o_d.keys()))
                if st.button("Eşleştir"):
                    try:
                        c.execute("INSERT INTO TETIKLER VALUES (?,?)", (o_d[s_trig], a_d[s_a]))
                        conn.commit()
                        st.success("Eşleşti")
                    except: st.error("Hata")

# =============================================================================
# 5. RAPORLAR
# =============================================================================
elif menu == "📈 Analitik Raporlar":
    st.title("📈 Raporlar")
    
    st.info("Rapor 1: Olay - Cihaz - Ev İlişkisi")
    q1 = """SELECT O.Tarih, O.Saat, O.Turu, C.Turu as Cihaz, E.Adres 
            FROM KAYDEDER K JOIN OLAY O ON K.OlayNumara=O.Numara 
            JOIN GUVENLIK_CIHAZI C ON K.GuvenlikCihaziNumara=C.Numara 
            JOIN VARDIR V ON C.Numara=V.GuvenlikCihaziNumara 
            JOIN AKILLI_EV E ON V.AkilliEvNumara=E.Numara ORDER BY O.Tarih DESC"""
    st.dataframe(pd.read_sql(q1, conn), use_container_width=True)
    
    st.info("Rapor 2: Alarm Analizi")
    q2 = """SELECT A.Numara, A.Durum, O.Turu as Tetikleyen FROM ALARM A 
            JOIN TETIKLER T ON A.Numara=T.AlarmNumara JOIN OLAY O ON T.OlayNumara=O.Numara"""
    st.dataframe(pd.read_sql(q2, conn), use_container_width=True)
    
    st.info("Rapor 3: Ev Başına Cihaz Sayısı")
    q3 = """SELECT E.Adres, COUNT(V.GuvenlikCihaziNumara) as Sayi 
            FROM AKILLI_EV E LEFT JOIN VARDIR V ON E.Numara=V.AkilliEvNumara GROUP BY E.Numara"""
    st.dataframe(pd.read_sql(q3, conn), use_container_width=True)
    
    st.info("Rapor 4: Aktif Alarmlar")
    q4 = """SELECT A.Numara, E.Adres FROM ALARM A 
            JOIN TETIKLER T ON A.Numara=T.AlarmNumara JOIN OLAY O ON T.OlayNumara=O.Numara 
            JOIN KAYDEDER K ON O.Numara=K.OlayNumara JOIN GUVENLIK_CIHAZI C ON K.GuvenlikCihaziNumara=C.Numara 
            JOIN VARDIR V ON C.Numara=V.GuvenlikCihaziNumara JOIN AKILLI_EV E ON V.AkilliEvNumara=E.Numara 
            WHERE A.Durum IN ('Açık', 'AÇIK', 'Aktif')"""
    st.dataframe(pd.read_sql(q4, conn), use_container_width=True)
    
    st.info("Rapor 5: Cihaz Türü İstatistiği")
    q5 = "SELECT Turu, COUNT(*) as Sayi FROM GUVENLIK_CIHAZI GROUP BY Turu"
    st.dataframe(pd.read_sql(q5, conn), use_container_width=True)

# =============================================================================
# 6. TÜM TABLOLAR
# =============================================================================
elif menu == "📂 Tüm Tablolar":
    st.title("📂 Veritabanı Tabloları")
    tables = ["AKILLI_EV", "KULLANICI", "KULLANICI_EPOSTA", "GUVENLIK_CIHAZI", "VARDIR", "OLAY", "KAYDEDER", "ALARM", "TETIKLER"]
    sel = st.selectbox("Tablo Seç", tables)
    try:
        df = pd.read_sql(f"SELECT * FROM {sel}", conn)
        s_raw = st.text_input("🔍 Ara")
        if s_raw:
            mask = df.astype(str).apply(lambda x: x.str.contains(s_raw, case=False, na=False)).any(axis=1)
            df = df[mask]
        st.dataframe(df, use_container_width=True)
    except: st.error("Hata")

conn.close()
