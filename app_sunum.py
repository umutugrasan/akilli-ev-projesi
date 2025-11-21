import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. VERİTABANI BAĞLANTISI ---
def get_connection():
    conn = sqlite3.connect('smart_security_final.db')
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# --- 2. AYARLAR VE TASARIM ---
st.set_page_config(page_title="DB Sunum Paneli", page_icon="🎓", layout="wide")

# CSS TASARIMI (DASHBOARD İÇİN GÜZELLEŞTİRME)
st.markdown("""
<style>
    .stApp {background-color: #0E1117;}
    
    /* Metric Kartları (Dashboard Kutuları) */
    div[data-testid="stMetric"] {
        background-color: #262730; 
        border: 1px solid #3d3d3d; 
        padding: 15px; 
        border-radius: 10px;
        color: white;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    
    /* Tablolar */
    .stDataFrame {border: 1px solid #374151; border-radius: 5px;}
    
    /* Başlıklar */
    h1, h2, h3 {color: #e5e7eb; font-family: 'Helvetica Neue', sans-serif;}
    
    /* Bilgi Kutuları (Akademik Açıklamalar) */
    .info-box {
        padding: 10px; border-radius: 5px; background-color: #172554; color: #dbeafe;
        border-left: 5px solid #3b82f6; margin-bottom: 10px; font-size: 0.9em;
    }
    
    /* Tablo Başlıkları */
    .table-title {
        font-size: 16px; font-weight: bold; color: #fca5a5; margin-top: 10px; margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

conn = get_connection()
c = conn.cursor()

# --- YAN MENÜ ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/900/900782.png", width=80)
    st.title("🗄️ DB Sunum Paneli")
    st.markdown("---")
    menu = st.radio("Menü Seçiniz:", 
        ["📊 Dashboard (Özet)",
         "1. AKILLI_EV & KULLANICI", 
         "2. CİHAZ & VARDIR (M:N)", 
         "3. OLAY & KAYDEDER (M:N)", 
         "4. ALARM & TETİKLER (M:N)",
         "5. TÜM TABLOLARI İNCELE"])
    st.markdown("---")
    st.caption("Veritabanı Yönetim Sistemleri Dersi Projesi")

# =============================================================================
# MODÜL 0: DASHBOARD (SİSTEM ÖZETİ)
# =============================================================================
if menu == "📊 Dashboard (Özet)":
    st.title("📊 Sistem Genel Bakış")
    st.markdown("Veritabanındaki anlık durum ve son olay akışı.")
    
    # İstatistikleri Çek
    try:
        total_ev = c.execute("SELECT COUNT(*) FROM AKILLI_EV").fetchone()[0]
        total_user = c.execute("SELECT COUNT(*) FROM KULLANICI").fetchone()[0]
        active_dev = c.execute("SELECT COUNT(*) FROM GUVENLIK_CIHAZI WHERE Durumu='Aktif'").fetchone()[0]
        alarms = c.execute("SELECT COUNT(*) FROM ALARM").fetchone()[0]
    except:
        total_ev, total_user, active_dev, alarms = 0, 0, 0, 0

    # Kartlar
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏠 Kayıtlı Evler", total_ev, "Aktif")
    col2.metric("👤 Toplam Kullanıcı", total_user, "+Yeni")
    col3.metric("📹 Aktif Cihazlar", active_dev, "Online")
    col4.metric("🚨 Tetiklenen Alarmlar", alarms, "Kritik", delta_color="inverse")

    st.markdown("---")
    st.markdown("### 📝 Son Olay Akışı (Canlı Log)")
    st.caption("Bu tablo; KAYDEDER, VARDIR ve AKILLI_EV tablolarının JOIN işlemi ile oluşturulmuştur.")
    
    # JOIN SORGUSU (LOG)
    log_query = """
    SELECT O.Tarih, O.Saat, O.Turu as Olay, C.Turu as Cihaz, E.Adres
    FROM KAYDEDER K
    JOIN OLAY O ON K.OlayNumara = O.Numara
    JOIN GUVENLIK_CIHAZI C ON K.GuvenlikCihaziNumara = C.Numara
    JOIN VARDIR V ON C.Numara = V.GuvenlikCihaziNumara
    JOIN AKILLI_EV E ON V.AkilliEvNumara = E.Numara
    ORDER BY O.Tarih DESC, O.Saat DESC LIMIT 5
    """
    try:
        df_log = pd.read_sql(log_query, conn)
        st.dataframe(df_log, use_container_width=True, hide_index=True)
    except:
        st.info("Henüz kayıtlı bir olay yok.")

# =============================================================================
# MODÜL 1: TEMEL VARLIKLAR (EV VE KULLANICI)
# =============================================================================
elif menu == "1. AKILLI_EV & KULLANICI":
    st.title("🏠 Akıllı Ev ve Kullanıcı Yönetimi")
    
    col1, col2 = st.columns(2)
    
    # --- SOL: AKILLI_EV ---
    with col1:
        st.markdown('<div class="info-box">TABLO: <b>AKILLI_EV</b><br>PK: Numara</div>', unsafe_allow_html=True)
        with st.form("add_ev"):
            e_no = st.number_input("Ev Numara (PK)", min_value=1)
            e_adr = st.text_input("Adres")
            e_sahip = st.text_input("Ev Sahibi")
            if st.form_submit_button("AKILLI_EV Tablosuna Ekle"):
                try:
                    c.execute("INSERT INTO AKILLI_EV VALUES (?,?,?)", (e_no, e_adr, e_sahip))
                    conn.commit()
                    st.success(f"✅ Kayıt Eklendi: Ev No {e_no}")
                except Exception as e:
                    st.error(f"Hata: {e}")
        
        st.markdown('<p class="table-title">AKILLI_EV Tablosu</p>', unsafe_allow_html=True)
        st.dataframe(pd.read_sql("SELECT * FROM AKILLI_EV", conn), use_container_width=True)

    # --- SAĞ: KULLANICI ---
    with col2:
        st.markdown('<div class="info-box">TABLO: <b>KULLANICI</b><br>PK: KimlikNo | FK: AkilliEvNumara</div>', unsafe_allow_html=True)
        
        evler = c.execute("SELECT Numara, Adres FROM AKILLI_EV").fetchall()
        ev_dict = {f"Ev No: {e[0]}": e[0] for e in evler}
        
        with st.form("add_user"):
            u_id = st.number_input("Kimlik No (PK)", min_value=1)
            u_ad = st.text_input("Ad")
            u_soyad = st.text_input("Soyad")
            
            if ev_dict:
                u_fk = st.selectbox("Hangi Evde Oturuyor? (Foreign Key)", list(ev_dict.keys()))
            else:
                u_fk = None
                st.warning("Önce Ev Eklemelisiniz!")
            
            if st.form_submit_button("KULLANICI Tablosuna Ekle"):
                if u_fk:
                    try:
                        fk_value = ev_dict[u_fk]
                        c.execute("INSERT INTO KULLANICI VALUES (?,?,?,?)", (u_id, u_ad, u_soyad, fk_value))
                        conn.commit()
                        st.success(f"✅ Kullanıcı Eklendi (FK: {fk_value})")
                    except Exception as e:
                        st.error(f"Hata: {e}")
        
        st.markdown('<p class="table-title">KULLANICI Tablosu</p>', unsafe_allow_html=True)
        st.dataframe(pd.read_sql("SELECT * FROM KULLANICI", conn), use_container_width=True)

    st.markdown("---")
    st.subheader("Çok Değerli Nitelik (Multi-Valued Attribute): E-Posta")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        users = c.execute("SELECT KimlikNo, Adi FROM KULLANICI").fetchall()
        u_d = {f"{u[1]} (ID: {u[0]})": u[0] for u in users}
        if u_d:
            s_u = st.selectbox("Kullanıcı Seç (PK->FK)", list(u_d.keys()))
            mail = st.text_input("E-posta Adresi")
            if st.button("E-POSTA Tablosuna Ekle"):
                try:
                    c.execute("INSERT INTO KULLANICI_EPOSTA VALUES (?,?)", (u_d[s_u], mail))
                    conn.commit()
                    st.success("Eklendi")
                except:
                    st.error("Hata")
    with c2:
        st.markdown('<p class="table-title">KULLANICI_EPOSTA Tablosu</p>', unsafe_allow_html=True)
        st.dataframe(pd.read_sql("SELECT * FROM KULLANICI_EPOSTA", conn), use_container_width=True)

# =============================================================================
# MODÜL 2: CİHAZ VE VARDIR (ARA TABLO)
# =============================================================================
elif menu == "2. CİHAZ & VARDIR (M:N)":
    st.title("📹 Güvenlik Cihazı ve İlişki Yönetimi")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="info-box">1. Adım: <b>GÜVENLİK_CİHAZI</b> Tablosuna Veri Gir</div>', unsafe_allow_html=True)
        with st.form("add_dev"):
            d_no = st.number_input("Cihaz Numara (PK)", min_value=1)
            d_tur = st.selectbox("Türü", ["Kamera", "Sensör", "Kilit"])
            d_dur = st.selectbox("Durumu", ["Aktif", "İnaktif"])
            if st.form_submit_button("Cihaz Ekle"):
                try:
                    c.execute("INSERT INTO GUVENLIK_CIHAZI VALUES (?,?,?)", (d_no, d_tur, d_dur))
                    conn.commit()
                    st.success("Cihaz Envantere Eklendi")
                except:
                    st.error("PK Hatası: Bu numara var.")
        
        st.dataframe(pd.read_sql("SELECT * FROM GUVENLIK_CIHAZI", conn), use_container_width=True)

    with col2:
        st.markdown('<div class="info-box">2. Adım: <b>VARDIR</b> Tablosunda İlişkilendir (M:N)</div>', unsafe_allow_html=True)
        st.write("Bir Cihaz ID ile bir Ev ID'yi bu tabloda eşleştiriyoruz.")
        
        devs = c.execute("SELECT Numara, Turu FROM GUVENLIK_CIHAZI").fetchall()
        homes = c.execute("SELECT Numara, Adres FROM AKILLI_EV").fetchall()

        if devs and homes:
            d_dict = {f"{d[1]} (ID: {d[0]})": d[0] for d in devs}
            h_dict = {f"Ev No: {h[0]} ({h[1]})": h[0] for h in homes}

            sel_dev = st.selectbox("Cihaz Seç (FK)", list(d_dict.keys()))
            sel_home = st.selectbox("Ev Seç (FK)", list(h_dict.keys()))

            if st.button("VARDIR Tablosuna Kayıt At"):
                dev_id = d_dict[sel_dev]
                home_id = h_dict[sel_home]
                try:
                    c.execute("INSERT INTO VARDIR VALUES (?,?)", (home_id, dev_id))
                    conn.commit()
                    st.success(f"✅ İlişki Kuruldu: Ev {home_id} <-> Cihaz {dev_id}")
                except:
                    st.warning("Bu ilişki zaten var.")
        
        st.markdown('<p class="table-title">VARDIR Tablosu (Saf İlişki Verisi)</p>', unsafe_allow_html=True)
        st.dataframe(pd.read_sql("SELECT * FROM VARDIR", conn), use_container_width=True)

# =============================================================================
# MODÜL 3: OLAY VE KAYDEDER (ARA TABLO)
# =============================================================================
elif menu == "3. OLAY & KAYDEDER (M:N)":
    st.title("⚡ Olay Yönetimi ve KAYDEDER İlişkisi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="info-box">1. Adım: <b>OLAY</b> Tablosuna Veri Gir</div>', unsafe_allow_html=True)
        with st.form("add_olay"):
            o_no = st.number_input("Olay Numara (PK)", min_value=5000)
            o_tur = st.text_input("Türü", "Hareket Algılandı")
            o_date = datetime.now().strftime("%Y-%m-%d")
            o_time = datetime.now().strftime("%H:%M:%S")
            
            if st.form_submit_button("Olay Yarat"):
                try:
                    c.execute("INSERT INTO OLAY VALUES (?,?,?,?)", (o_no, o_tur, o_date, o_time))
                    conn.commit()
                    st.success(f"Olay {o_no} oluşturuldu.")
                except:
                    st.error("Hata")
        st.dataframe(pd.read_sql("SELECT * FROM OLAY ORDER BY Numara DESC", conn), use_container_width=True)

    with col2:
        st.markdown('<div class="info-box">2. Adım: <b>KAYDEDER</b> Tablosu (Cihaz <-> Olay)</div>', unsafe_allow_html=True)
        
        olays = c.execute("SELECT Numara, Turu FROM OLAY").fetchall()
        devs = c.execute("SELECT Numara, Turu FROM GUVENLIK_CIHAZI").fetchall()
        
        if olays and devs:
            o_d = {f"{o[1]} (ID: {o[0]})": o[0] for o in olays}
            d_d = {f"{d[1]} (ID: {d[0]})": d[0] for d in devs}
            
            s_o = st.selectbox("Hangi Olay? (FK)", list(o_d.keys()))
            s_d = st.selectbox("Hangi Cihaz Kaydetti? (FK)", list(d_d.keys()))
            
            if st.button("KAYDEDER Tablosuna İşle"):
                try:
                    c.execute("INSERT INTO KAYDEDER VALUES (?,?)", (d_d[s_d], o_d[s_o]))
                    conn.commit()
                    st.success(f"✅ İlişki: Cihaz {d_d[s_d]} -> Olay {o_d[s_o]}")
                except:
                    st.error("Hata")

        st.markdown('<p class="table-title">KAYDEDER Tablosu (Raw Data)</p>', unsafe_allow_html=True)
        st.dataframe(pd.read_sql("SELECT * FROM KAYDEDER", conn), use_container_width=True)

# =============================================================================
# MODÜL 4: ALARM VE TETIKLER (ARA TABLO) - DÜZELTİLDİ
# =============================================================================
elif menu == "4. ALARM & TETİKLER (M:N)":
    st.title("🚨 Alarm Yönetimi ve TETİKLER İlişkisi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="info-box">1. Adım: <b>ALARM</b> Tablosuna Veri Gir</div>', unsafe_allow_html=True)
        with st.form("add_alarm"):
            a_no = st.number_input("Alarm Numara (PK)", min_value=9000)
            a_dur = "AÇIK"
            a_date = datetime.now().strftime("%Y-%m-%d")
            a_time = datetime.now().strftime("%H:%M:%S")
            
            if st.form_submit_button("Alarm Oluştur"):
                try:
                    c.execute("INSERT INTO ALARM VALUES (?,?,?,?)", (a_no, a_dur, a_date, a_time))
                    conn.commit()
                    st.success(f"Alarm {a_no} oluşturuldu.")
                except:
                    st.error("Hata: Bu ID zaten var.")
        st.dataframe(pd.read_sql("SELECT * FROM ALARM ORDER BY Numara DESC", conn), use_container_width=True)

    with col2:
        st.markdown('<div class="info-box">2. Adım: <b>TETİKLER</b> Tablosu (Olay <-> Alarm)</div>', unsafe_allow_html=True)
        
        alarms = c.execute("SELECT Numara FROM ALARM").fetchall()
        olays = c.execute("SELECT Numara, Turu FROM OLAY").fetchall()
        
        if alarms and olays:
            a_d = {f"Alarm ID: {a[0]}": a[0] for a in alarms}
            o_d = {f"{o[1]} (ID: {o[0]})": o[0] for o in olays}
            
            s_a = st.selectbox("Hangi Alarm? (FK)", list(a_d.keys()))
            s_o = st.selectbox("Hangi Olay Tetikledi? (FK)", list(o_d.keys()))
            
            if st.button("TETİKLER Tablosuna İşle"):
                try:
                    # DÜZELTİLEN KISIM: TETIKLER (I ile)
                    c.execute("INSERT INTO TETIKLER VALUES (?,?)", (o_d[s_o], a_d[s_a]))
                    conn.commit()
                    st.success(f"✅ İlişki: Olay {o_d[s_o]} -> Alarm {a_d[s_a]}")
                except:
                    st.error("Hata: Bu ilişki zaten var.")

        st.markdown('<p class="table-title">TETİKLER Tablosu (Raw Data)</p>', unsafe_allow_html=True)
        st.dataframe(pd.read_sql("SELECT * FROM TETIKLER", conn), use_container_width=True)

# =============================================================================
# MODÜL 5: TÜM TABLOLAR
# =============================================================================
elif menu == "5. TÜM TABLOLARI İNCELE":
    st.title("📂 Veritabanı Müfettişi")
    st.markdown("Veritabanındaki tüm tabloların ham hallerini buradan inceleyebilirsiniz.")

    tab_names = ["AKILLI_EV", "KULLANICI", "KULLANICI_EPOSTA", "GUVENLIK_CIHAZI", "VARDIR", "OLAY", "KAYDEDER", "ALARM", "TETIKLER"]
    selected_table = st.selectbox("Tablo Seçin:", tab_names)
    
    st.markdown(f"### 📋 {selected_table}")
    try:
        # Tetikler hatası olmaması için safe query
        df = pd.read_sql(f"SELECT * FROM {selected_table}", conn)
        st.dataframe(df, use_container_width=True)
    except:
        st.error("Tablo okunamadı.")

conn.close()