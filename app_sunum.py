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

# --- VERİ YÜKLEME FONKSİYONU (RESET) ---
def reset_and_populate_data():
    conn = get_connection()
    c = conn.cursor()
    
    tables = ['TETIKLER', 'KAYDEDER', 'VARDIR', 'KULLANICI_EPOSTA', 'ALARM', 'OLAY', 'GUVENLIK_CIHAZI', 'KULLANICI', 'AKILLI_EV']
    for table in tables:
        c.execute(f"DELETE FROM {table}")
        
    # 1. EVLER
    evler = [
        (12, 'Kızıltoprak Sk. No:15 Bandırma/Balıkesir', 'Yunus Özdemir'),
        (25, 'Atatürk Cad. No:78 İstanbul/Kadıköy', 'Süleyman Emre Arlı'),
        (38, 'İnönü Bulvarı No:142 Ankara/Çankaya', 'Ömer Faruk Külçeler')
    ]
    c.executemany("INSERT INTO AKILLI_EV VALUES (?,?,?)", evler)

    # 2. KULLANICILAR
    kullanicilar = [
        (101, 'Umut', 'Uğraşan', 12),
        (102, 'Mehmet', 'Yılmaz', 25),
        (103, 'Ayşe', 'Kara', 38),
        (104, 'Veli', 'Demir', 12)
    ]
    c.executemany("INSERT INTO KULLANICI VALUES (?,?,?,?)", kullanicilar)

    # 3. EPOSTALAR
    epostalar = [
        (101, 'umut@mail.com'),
        (102, 'mehmet.yilmaz@gmail.com'),
        (103, 'ayse.kara@outlook.com'),
        (104, 'veli.demir@yahoo.com')
    ]
    c.executemany("INSERT INTO KULLANICI_EPOSTA VALUES (?,?)", epostalar)

    # 4. CİHAZLAR
    cihazlar = [
        (7, 'Kamera', 'Aktif'),
        (8, 'Hareket Sensörü', 'İnaktif'),
        (9, 'Kapı Kilidi', 'İnaktif'),
        (10, 'Duman Dedektörü', 'Aktif'),
        (11, 'Cam Kırılma Sensörü', 'Aktif')
    ]
    c.executemany("INSERT INTO GUVENLIK_CIHAZI VALUES (?,?,?)", cihazlar)

    # 5. VARDIR
    vardir_data = [(12, 7), (12, 8), (25, 9), (25, 10)]
    c.executemany("INSERT INTO VARDIR VALUES (?,?)", vardir_data)

    # 6. OLAYLAR
    olaylar = [
        (4096, 'Hareket Algılandı', '2025-11-02', '19:29:42'),
        (4097, 'Kapı Açıldı', '2025-11-03', '08:15:20'),
        (4098, 'Duman Tespit Edildi', '2025-11-05', '14:45:10'),
        (4099, 'Cam Kırılması Algılandı', '2025-11-07', '02:30:55')
    ]
    c.executemany("INSERT INTO OLAY VALUES (?,?,?,?)", olaylar)

    # 7. KAYDEDER
    kaydeder_data = [(7, 4096), (8, 4096), (9, 4097), (10, 4098), (11, 4099)]
    c.executemany("INSERT INTO KAYDEDER VALUES (?,?)", kaydeder_data)

    # 8. ALARMLAR
    alarmlar = [
        (6071, 'Kapalı', '2025-11-02', '19:29:48'),
        (6072, 'Kapalı', '2025-11-03', '08:15:25'),
        (6073, 'Açık', '2025-11-05', '14:45:15'),
        (6074, 'Açık', '2025-11-07', '02:31:00')
    ]
    c.executemany("INSERT INTO ALARM VALUES (?,?,?,?)", alarmlar)

    # 9. TETIKLER
    tetikler_data = [(4098, 6073), (4099, 6074)]
    c.executemany("INSERT INTO TETIKLER VALUES (?,?)", tetikler_data)

    conn.commit()
    conn.close()

# --- 2. SAYFA YAPILANDIRMASI & PREMIUM TASARIM ---
st.set_page_config(page_title="SmartHome Admin", page_icon="🛡️", layout="wide")

# MODERN CSS ENJEKSİYONU (DÜZELTİLDİ)
st.markdown("""
<style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Container/Kartlar */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        background-color: #1e232e;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #30363d;
    }

    /* Metric Kutuları */
    [data-testid="stMetric"] {
        background-color: #262c36 !important;
        border: 1px solid #3f4451 !important;
        padding: 15px !important;
        border-radius: 10px !important;
    }

    /* Tablolar */
    .stDataFrame {
        border: 1px solid #30363d;
        border-radius: 8px;
    }

    /* Başlıklar */
    h1, h2, h3 {
        color: #f0f6fc !important;
    }
    
    /* Bilgi Kutuları */
    .info-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #1e3a8a;
        color: white;
        border-left: 5px solid #3b82f6;
        margin-bottom: 10px;
    }
    
    /* Rapor Kutusu */
    .report-card {
        background-color: #1f2937;
        border-left: 5px solid #10b981;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

conn = get_connection()
c = conn.cursor()

# --- YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.title("🛡️ ADMIN PANEL")
    st.caption("v2.0.5 Final")
    st.markdown("---")
    
    # RESET BUTONU
    if st.button("🔄 Rapor Verilerini Yükle", type="primary", use_container_width=True):
        try:
            reset_and_populate_data()
            st.toast("Veriler sıfırlandı ve yüklendi!", icon="✅")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Hata: {e}")
            
    st.markdown("---")
    
    # MENÜ SEÇİMİ
    menu = st.radio("NAVİGASYON", 
        ["📊 Dashboard",
         "🏠 Ev & Kullanıcı", 
         "📹 Cihaz Yönetimi", 
         "⚡ Olay & Alarm", 
         "📈 Analitik Raporlar",
         "📂 Veritabanı Kayıtları"])
         
    st.markdown("---")
    st.info("🟢 Sistem: **Online**")

# =============================================================================
# MODÜL 0: DASHBOARD
# =============================================================================
if menu == "📊 Dashboard":
    st.title("📊 Sistem Genel Bakış")
    
    try:
        total_ev = c.execute("SELECT COUNT(*) FROM AKILLI_EV").fetchone()[0]
        total_user = c.execute("SELECT COUNT(*) FROM KULLANICI").fetchone()[0]
        active_dev = c.execute("SELECT COUNT(*) FROM GUVENLIK_CIHAZI WHERE Durumu='Aktif'").fetchone()[0]
        alarms = c.execute("SELECT COUNT(*) FROM ALARM").fetchone()[0]
    except:
        total_ev, total_user, active_dev, alarms = 0, 0, 0, 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏠 Kayıtlı Evler", total_ev)
    col2.metric("👤 Kullanıcılar", total_user)
    col3.metric("📹 Aktif Cihazlar", active_dev)
    col4.metric("🚨 Alarmlar", alarms)

    st.markdown("### 📝 Son Olay Akışı")
    
    log_query = """
    SELECT O.Tarih, O.Saat, O.Turu as Olay, C.Turu as Cihaz, E.Adres
    FROM KAYDEDER K
    JOIN OLAY O ON K.OlayNumara = O.Numara
    JOIN GUVENLIK_CIHAZI C ON K.GuvenlikCihaziNumara = C.Numara
    JOIN VARDIR V ON C.Numara = V.GuvenlikCihaziNumara
    JOIN AKILLI_EV E ON V.AkilliEvNumara = E.Numara
    ORDER BY O.Tarih DESC, O.Saat DESC LIMIT 7
    """
    try:
        df_log = pd.read_sql(log_query, conn)
        st.dataframe(df_log, use_container_width=True, hide_index=True)
    except:
        st.info("Henüz veri akışı yok.")

# =============================================================================
# MODÜL 1: EV & KULLANICI
# =============================================================================
elif menu == "🏠 Ev & Kullanıcı":
    st.title("🏠 Mülk ve Kullanıcı Yönetimi")
    
    tab_ev, tab_user = st.tabs(["🏠 Ev İşlemleri", "👤 Kullanıcı & E-Posta"])

    # --- TAB 1: EV ---
    with tab_ev:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.subheader("Yeni Ev Ekle")
            with st.form("add_ev", clear_on_submit=True):
                e_no = st.number_input("Ev No (PK)", min_value=1)
                e_adr = st.text_area("Açık Adres")
                e_sahip = st.text_input("Mülk Sahibi")
                if st.form_submit_button("Kaydet"):
                    try:
                        c.execute("INSERT INTO AKILLI_EV VALUES (?,?,?)", (e_no, e_adr, e_sahip))
                        conn.commit()
                        st.success("Ev Eklendi!")
                        time.sleep(0.5)
                        st.rerun()
                    except:
                        st.error("Bu numara kayıtlı.")

        with c2:
            st.subheader("Ev Listesi & İşlemler")
            
            # ARAMA
            search_ev = st.text_input("🔍 Ev Ara", placeholder="Adres...")
            query_ev = "SELECT * FROM AKILLI_EV"
            df_ev = pd.read_sql(query_ev, conn)
            if search_ev:
                df_ev = df_ev[df_ev['Adres'].str.contains(search_ev, case=False)]
            
            st.dataframe(df_ev, use_container_width=True, hide_index=True)
            
            with st.expander("🛠️ Düzenle / Sil"):
                evler = c.execute("SELECT Numara, Adres FROM AKILLI_EV").fetchall()
                if evler:
                    ev_dict = {f"No: {e[0]} - {e[1]}": e[0] for e in evler}
                    sel_ev = st.selectbox("Ev Seç", list(ev_dict.keys()))
                    sel_id = ev_dict[sel_ev]
                    
                    c_up, c_del = st.columns(2)
                    with c_up:
                        new_adr = st.text_input("Yeni Adres")
                        if st.button("Güncelle"):
                            c.execute("UPDATE AKILLI_EV SET Adres=? WHERE Numara=?", (new_adr, sel_id))
                            conn.commit()
                            st.success("Güncellendi")
                            time.sleep(0.5)
                            st.rerun()
                    with c_del:
                        st.write("")
                        st.write("")
                        if st.button("🗑️ Sil"):
                            c.execute("DELETE FROM AKILLI_EV WHERE Numara=?", (sel_id,))
                            conn.commit()
                            st.warning("Silindi")
                            time.sleep(0.5)
                            st.rerun()

    # --- TAB 2: KULLANICI ---
    with tab_user:
        c1, c2 = st.columns([1, 2])
        evler = c.execute("SELECT Numara, Adres FROM AKILLI_EV").fetchall()
        ev_dict = {f"Ev No: {e[0]}": e[0] for e in evler}

        with c1:
            st.subheader("Kullanıcı Ekle")
            with st.form("add_user", clear_on_submit=True):
                u_id = st.number_input("TC Kimlik", min_value=1)
                u_ad = st.text_input("Ad")
                u_soyad = st.text_input("Soyad")
                u_fk = st.selectbox("Bağlı Olduğu Ev", list(ev_dict.keys()) if ev_dict else [])
                
                if st.form_submit_button("Kaydet"):
                    if u_fk:
                        try:
                            c.execute("INSERT INTO KULLANICI VALUES (?,?,?,?)", (u_id, u_ad, u_soyad, ev_dict[u_fk]))
                            conn.commit()
                            st.success("Eklendi")
                            time.sleep(0.5)
                            st.rerun()
                        except:
                            st.error("Hata/Mükerrer ID")
                    else:
                        st.error("Önce Ev Ekleyin")

        with c2:
            st.subheader("Kullanıcı Listesi")
            search_user = st.text_input("🔍 Kullanıcı Ara", placeholder="Ad/Soyad...")
            q_user = "SELECT * FROM KULLANICI"
            df_user = pd.read_sql(q_user, conn)
            if search_user:
                df_user = df_user[df_user['Adi'].str.contains(search_user, case=False) | df_user['Soyadi'].str.contains(search_user, case=False)]
            st.dataframe(df_user, use_container_width=True, hide_index=True)

            with st.expander("🗑️ Kullanıcı Sil"):
                users = c.execute("SELECT KimlikNo, Adi, Soyadi FROM KULLANICI").fetchall()
                if users:
                    u_d = {f"{u[1]} {u[2]} (ID:{u[0]})": u[0] for u in users}
                    s_u = st.selectbox("Silinecek Kişi", list(u_d.keys()))
                    if st.button("Sil"):
                        c.execute("DELETE FROM KULLANICI WHERE KimlikNo=?", (u_d[s_u],))
                        conn.commit()
                        st.warning("Silindi")
                        time.sleep(0.5)
                        st.rerun()

        st.divider()
        
        # E-POSTA YÖNETİMİ
        st.subheader("✉️ E-Posta Yönetimi")
        col_em1, col_em2 = st.columns(2)
        
        with col_em1:
            users_mail = c.execute("SELECT KimlikNo, Adi, Soyadi FROM KULLANICI").fetchall()
            if users_mail:
                u_m_d = {f"{u[1]} {u[2]}": u[0] for u in users_mail}
                sel_m_u = st.selectbox("Kullanıcı Seç", list(u_m_d.keys()))
                new_mail = st.text_input("Yeni E-posta")
                if st.button("E-posta Ekle"):
                    try:
                        c.execute("INSERT INTO KULLANICI_EPOSTA VALUES (?,?)", (u_m_d[sel_m_u], new_mail))
                        conn.commit()
                        st.success("Eklendi")
                        time.sleep(0.5)
                        st.rerun()
                    except:
                        st.error("Hata")
        
        with col_em2:
            if users_mail:
                uid = u_m_d[sel_m_u]
                st.write(f"**{sel_m_u}** kişisinin e-postaları:")
                df_m = pd.read_sql(f"SELECT * FROM KULLANICI_EPOSTA WHERE KullaniciKimlikNo={uid}", conn)
                st.dataframe(df_m, use_container_width=True)

# =============================================================================
# MODÜL 2: CİHAZ YÖNETİMİ
# =============================================================================
elif menu == "📹 Cihaz Yönetimi":
    st.title("📹 Cihaz Yönetimi")
    t1, t2, t3 = st.tabs(["➕ Yeni Cihaz", "🔗 Ev Bağlantısı", "⚙️ İşlemler"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            with st.form("add_dev"):
                d_no = st.number_input("Seri No", min_value=1)
                d_tur = st.selectbox("Tür", ["Kamera", "Hareket Sensörü", "Akıllı Kilit", "Duman Dedektörü", "Cam Kırılma Sensörü"])
                d_dur = st.selectbox("Durum", ["Aktif", "İnaktif"])
                if st.form_submit_button("Ekle"):
                    try:
                        c.execute("INSERT INTO GUVENLIK_CIHAZI VALUES (?,?,?)", (d_no, d_tur, d_dur))
                        conn.commit()
                        st.success("Eklendi")
                    except:
                        st.error("Hata")
        with c2:
            st.markdown("###### Cihaz Listesi")
            search_dev = st.text_input("🔍 Cihaz Ara")
            df_dev = pd.read_sql("SELECT * FROM GUVENLIK_CIHAZI", conn)
            if search_dev:
                df_dev = df_dev[df_dev['Turu'].str.contains(search_dev, case=False)]
            st.dataframe(df_dev, use_container_width=True, hide_index=True)

    with t2:
        c1, c2 = st.columns([1, 2])
        with c1:
            devs = c.execute("SELECT Numara, Turu FROM GUVENLIK_CIHAZI").fetchall()
            homes = c.execute("SELECT Numara, Adres FROM AKILLI_EV").fetchall()
            if devs and homes:
                d_d = {f"{d[1]} (ID:{d[0]})": d[0] for d in devs}
                h_d = {f"Ev No:{h[0]}": h[0] for h in homes}
                s_d = st.selectbox("Cihaz", list(d_d.keys()))
                s_h = st.selectbox("Ev", list(h_d.keys()))
                if st.button("Bağla"):
                    try:
                        c.execute("INSERT INTO VARDIR VALUES (?,?)", (h_d[s_h], d_d[s_d]))
                        conn.commit()
                        st.success("Bağlandı")
                    except:
                        st.warning("Zaten bağlı")
        with c2:
            st.markdown("###### Bağlantılar (VARDIR)")
            q = "SELECT * FROM VARDIR"
            st.dataframe(pd.read_sql(q, conn), use_container_width=True)

    with t3:
        devs = c.execute("SELECT Numara, Turu FROM GUVENLIK_CIHAZI").fetchall()
        if devs:
            d_d = {f"{d[1]} (ID:{d[0]})": d[0] for d in devs}
            t_d = st.selectbox("Cihaz Seç", list(d_d.keys()))
            t_id = d_d[t_d]
            
            c_up, c_del = st.columns(2)
            with c_up:
                n_st = st.selectbox("Yeni Durum", ["Aktif", "İnaktif", "Arızalı"])
                if st.button("Durum Güncelle"):
                    c.execute("UPDATE GUVENLIK_CIHAZI SET Durumu=? WHERE Numara=?", (n_st, t_id))
                    conn.commit()
                    st.success("Güncellendi")
                    time.sleep(0.5)
                    st.rerun()
            with c_del:
                st.write("")
                st.write("")
                if st.button("Sil"):
                    c.execute("DELETE FROM GUVENLIK_CIHAZI WHERE Numara=?", (t_id,))
                    conn.commit()
                    st.warning("Silindi")
                    time.sleep(0.5)
                    st.rerun()

# =============================================================================
# MODÜL 3: OLAY & ALARM
# =============================================================================
elif menu == "⚡ Olay & Alarm":
    st.title("⚡ Olay ve Alarm Yönetimi")
    t1, t2 = st.tabs(["⚡ Olaylar", "🚨 Alarmlar"])

    with t1:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("##### Olay Ekle")
            with st.form("add_olay"):
                o_id = st.number_input("Olay ID", min_value=4000)
                o_typ = st.text_input("Tür", "Hareket Algılandı")
                if st.form_submit_button("Ekle"):
                    now = datetime.now()
                    try:
                        c.execute("INSERT INTO OLAY VALUES (?,?,?,?)", (o_id, o_typ, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")))
                        conn.commit()
                        st.success("Eklendi")
                    except:
                        st.error("Hata")
            
            st.markdown("##### Sil")
            olays = c.execute("SELECT Numara, Turu FROM OLAY").fetchall()
            if olays:
                o_d = {f"{o[1]} (ID:{o[0]})": o[0] for o in olays}
                s_o = st.selectbox("Silinecek Olay", list(o_d.keys()))
                if st.button("Olayı Sil"):
                    c.execute("DELETE FROM OLAY WHERE Numara=?", (o_d[s_o],))
                    conn.commit()
                    st.warning("Silindi")
                    time.sleep(0.5)
                    st.rerun()

        with c2:
            st.markdown("##### Olay Listesi")
            s_olay = st.text_input("🔍 Ara", placeholder="Tür...")
            df_olay = pd.read_sql("SELECT * FROM OLAY ORDER BY Numara DESC", conn)
            if s_olay:
                df_olay = df_olay[df_olay['Turu'].str.contains(s_olay, case=False)]
            st.dataframe(df_olay, use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("##### Cihaza Bağla (KAYDEDER)")
            devs = c.execute("SELECT Numara, Turu FROM GUVENLIK_CIHAZI").fetchall()
            if olays and devs:
                d_d = {f"{d[1]} (ID:{d[0]})": d[0] for d in devs}
                sel_o = st.selectbox("Olay", list(o_d.keys()), key="k_o")
                sel_d = st.selectbox("Cihaz", list(d_d.keys()), key="k_d")
                if st.button("İlişkilendir"):
                    try:
                        c.execute("INSERT INTO KAYDEDER VALUES (?,?)", (d_d[sel_d], o_d[sel_o]))
                        conn.commit()
                        st.success("Bağlandı")
                    except:
                        st.error("Hata")

    with t2:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("##### Alarm Ekle")
            with st.form("add_alarm"):
                a_id = st.number_input("Alarm ID", min_value=6000)
                if st.form_submit_button("Başlat"):
                    now = datetime.now()
                    try:
                        c.execute("INSERT INTO ALARM VALUES (?,?,?,?)", (a_id, "AÇIK", now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")))
                        conn.commit()
                        st.success("Başlatıldı")
                    except:
                        st.error("Hata")
            
            st.markdown("##### Sil")
            alarms = c.execute("SELECT Numara FROM ALARM").fetchall()
            if alarms:
                a_d = {f"Alarm ID:{a[0]}": a[0] for a in alarms}
                s_a = st.selectbox("Silinecek Alarm", list(a_d.keys()))
                if st.button("Alarmı Sil"):
                    c.execute("DELETE FROM ALARM WHERE Numara=?", (a_d[s_a],))
                    conn.commit()
                    st.warning("Silindi")
                    time.sleep(0.5)
                    st.rerun()

        with c2:
            st.markdown("##### Alarm Listesi")
            st.dataframe(pd.read_sql("SELECT * FROM ALARM ORDER BY Numara DESC", conn), use_container_width=True)
            
            st.divider()
            st.markdown("##### Olayla Eşleştir (TETIKLER)")
            olays = c.execute("SELECT Numara, Turu FROM OLAY").fetchall()
            if alarms and olays:
                o_d = {f"{o[1]} (ID:{o[0]})": o[0] for o in olays}
                sel_a = st.selectbox("Alarm", list(a_d.keys()), key="t_a")
                sel_o = st.selectbox("Tetikleyen", list(o_d.keys()), key="t_o")
                if st.button("Eşleştir"):
                    try:
                        c.execute("INSERT INTO TETIKLER VALUES (?,?)", (o_d[sel_o], a_d[sel_a]))
                        conn.commit()
                        st.success("Eşleşti")
                    except:
                        st.error("Hata")

# =============================================================================
# MODÜL 5: ANALİTİK RAPORLAR
# =============================================================================
elif menu == "📈 Analitik Raporlar":
    st.title("📈 Analitik Raporlar")
    
    st.markdown('<div class="report-card">⚡ <b>RAPOR 1: Olay-Cihaz-Ev</b></div>', unsafe_allow_html=True)
    q1 = """
    SELECT O.Tarih, O.Saat, O.Turu AS Olay, C.Turu AS Cihaz, E.Adres
    FROM KAYDEDER K JOIN OLAY O ON K.OlayNumara = O.Numara 
    JOIN GUVENLIK_CIHAZI C ON K.GuvenlikCihaziNumara = C.Numara 
    JOIN VARDIR V ON C.Numara = V.GuvenlikCihaziNumara 
    JOIN AKILLI_EV E ON V.AkilliEvNumara = E.Numara ORDER BY O.Tarih DESC
    """
    st.dataframe(pd.read_sql(q1, conn), use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="report-card">📊 <b>RAPOR 2: Alarm Analizi</b></div>', unsafe_allow_html=True)
    q2 = """
    SELECT A.Numara AS AlarmID, A.Durum, O.Turu AS Tetikleyen, O.Tarih
    FROM ALARM A JOIN TETIKLER T ON A.Numara = T.AlarmNumara
    JOIN OLAY O ON T.OlayNumara = O.Numara
    """
    st.dataframe(pd.read_sql(q2, conn), use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="report-card">🏠 <b>RAPOR 3: Ev Envanteri</b></div>', unsafe_allow_html=True)
    q3 = """
    SELECT E.Adres, COUNT(V.GuvenlikCihaziNumara) AS Cihaz_Sayisi 
    FROM AKILLI_EV E LEFT JOIN VARDIR V ON E.Numara = V.AkilliEvNumara
    GROUP BY E.Numara, E.Adres
    """
    st.dataframe(pd.read_sql(q3, conn), use_container_width=True)

 st.markdown("---")
    st.markdown('<div class="report-card">🚨 <b>RAPOR 4: Aktif Alarmların Konumları</b></div>', unsafe_allow_html=True)
    # DÜZELTME: Durum sorgusunu genişlettik (Açık, AÇIK veya Aktif)
    q4 = """
    SELECT A.Numara AS AlarmID, E.Adres, E.EvSahibi 
    FROM ALARM A 
    JOIN TETIKLER T ON A.Numara = T.AlarmNumara
    JOIN OLAY O ON T.OlayNumara = O.Numara
    JOIN KAYDEDER K ON O.Numara = K.OlayNumara
    JOIN GUVENLIK_CIHAZI C ON K.GuvenlikCihaziNumara = C.Numara
    JOIN VARDIR V ON C.Numara = V.GuvenlikCihaziNumara
    JOIN AKILLI_EV E ON V.AkilliEvNumara = E.Numara
    WHERE A.Durum IN ('Açık', 'AÇIK', 'Aktif')
    """
    try:
        st.dataframe(pd.read_sql(q4, conn), use_container_width=True)
    except:
        st.info("Veri yok.")
        
    st.markdown("---")
    st.markdown('<div class="report-card">📈 <b>RAPOR 5: İstatistikler</b></div>', unsafe_allow_html=True)
    q5 = """SELECT C.Turu, COUNT(O.Numara) as OlaySayisi FROM GUVENLIK_CIHAZI C 
            JOIN KAYDEDER K ON C.Numara = K.GuvenlikCihaziNumara 
            JOIN OLAY O ON K.OlayNumara = O.Numara GROUP BY C.Turu"""
    st.dataframe(pd.read_sql(q5, conn), use_container_width=True)

# =============================================================================
# MODÜL 6: KAYITLAR
# =============================================================================
elif menu == "📂 Veritabanı Kayıtları":
    st.title("📂 Veritabanı Müfettişi")
    tables = ["AKILLI_EV", "KULLANICI", "KULLANICI_EPOSTA", "GUVENLIK_CIHAZI", "VARDIR", "OLAY", "KAYDEDER", "ALARM", "TETIKLER"]
    sel = st.selectbox("Tablo Seç", tables)
    try:
        df = pd.read_sql(f"SELECT * FROM {sel}", conn)
        st.markdown(f"### 📋 {sel} ({len(df)})")
        s_raw = st.text_input("🔍 Ara")
        if s_raw:
            mask = df.astype(str).apply(lambda x: x.str.contains(s_raw, case=False, na=False)).any(axis=1)
            df = df[mask]
        st.dataframe(df, use_container_width=True)
    except:
        st.error("Hata")

conn.close()

