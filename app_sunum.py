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

# --- 2. SAYFA YAPILANDIRMASI & PREMIUM TASARIM ---
st.set_page_config(page_title="SmartHome Admin", page_icon="🛡️", layout="wide")

# MODERN CSS ENJEKSİYONU
st.markdown("""
<style>
    .stApp {background-color: #0f1116; font-family: 'Inter', sans-serif;}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {background-color: #161b22; border-right: 1px solid #30363d;}
    
    /* Kartlar */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        background-color: #1e232e; padding: 20px; border-radius: 12px; border: 1px solid #30363d;
    }

    /* Metric Kutuları */
    div[data-testid="stMetric"] {
        background-color: #262c36 !important; border: 1px solid #3f4451 !important;
        padding: 15px !important; border-radius: 10px !important; transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover {transform: translateY(-5px); border-color: #58a6ff !important;}

    /* Tablolar */
    .stDataFrame {border: 1px solid #30363d; border-radius: 8px; overflow: hidden;}

    /* Butonlar */
    .stButton>button {
        background: linear-gradient(45deg, #238636, #2ea043); color: white; border: none;
        border-radius: 8px; font-weight: bold; transition: all 0.3s ease;
    }
    .stButton>button:hover {opacity: 0.9; transform: scale(1.02);}
    
    /* Başlıklar */
    h1, h2, h3 {color: #f0f6fc !important; font-weight: 700;}
    p, label {color: #c9d1d9 !important;}
    
    /* Rapor Kutusu */
    .report-card {
        background-color: #1f2937; border-left: 5px solid #10b981;
        padding: 15px; border-radius: 5px; margin-bottom: 15px; color: white;
    }
</style>
""", unsafe_allow_html=True)

conn = get_connection()
c = conn.cursor()

# --- YAN MENÜ ---
with st.sidebar:
    st.title("🛡️ ADMIN PANEL")
    st.caption("Smart Home Security System v2.0")
    st.markdown("---")
    menu = st.radio("NAVİGASYON", 
        ["📊 Dashboard",
         "🏠 Ev & Kullanıcı", 
         "📹 Cihaz Yönetimi", 
         "⚡ Olay & Alarm", 
         "📈 Analitik Raporlar",
         "📂 Veritabanı Kayıtları"])
    st.markdown("---")
    st.info("🟢 Sistem Durumu: **Aktif**")

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
    col1.metric("🏠 Kayıtlı Mülk", total_ev, "Aktif")
    col2.metric("👤 Kullanıcılar", total_user, "+Yeni")
    col3.metric("📹 Online Cihaz", active_dev, "Güvenli")
    col4.metric("🚨 Alarm Durumu", alarms, "Kritik", delta_color="inverse")

    st.markdown("### 📝 Canlı Olay Akışı")
    
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
# MODÜL 1: EV & KULLANICI (E-POSTA EKLENDİ)
# =============================================================================
elif menu == "🏠 Ev & Kullanıcı":
    st.title("🏠 Mülk ve Kullanıcı Yönetimi")
    tab_ev, tab_user = st.tabs(["🏠 Ev İşlemleri", "👤 Kullanıcı & E-Posta İşlemleri"])

    # --- TAB 1: EV ---
    with tab_ev:
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.subheader("Yeni Ev Kaydı")
            with st.form("add_ev", clear_on_submit=True):
                e_no = st.number_input("Ev No (PK)", min_value=1)
                e_adr = st.text_area("Açık Adres")
                e_sahip = st.text_input("Mülk Sahibi")
                if st.form_submit_button("Kaydet"):
                    try:
                        c.execute("INSERT INTO AKILLI_EV VALUES (?,?,?)", (e_no, e_adr, e_sahip))
                        conn.commit()
                        st.toast("Ev başarıyla eklendi!", icon="✅")
                        time.sleep(0.5)
                        st.rerun()
                    except:
                        st.error("Bu numara zaten kayıtlı.")

        with c2:
            st.subheader("Ev Listesi & Arama")
            
            # SEARCH BAR (ARAMA)
            search_ev = st.text_input("🔍 Ev Ara (Adres veya Sahip)", placeholder="Örn: Kadıköy...")
            
            query_ev = "SELECT * FROM AKILLI_EV"
            df_ev = pd.read_sql(query_ev, conn)
            
            # Pandas ile filtreleme
            if search_ev:
                df_ev = df_ev[df_ev['Adres'].str.contains(search_ev, case=False) | df_ev['EvSahibi'].str.contains(search_ev, case=False)]
            
            st.dataframe(df_ev, use_container_width=True, hide_index=True)
            
            with st.expander("🛠️ Düzenle / Sil"):
                evler = c.execute("SELECT Numara, Adres FROM AKILLI_EV").fetchall()
                if evler:
                    ev_dict = {f"No: {e[0]} - {e[1]}": e[0] for e in evler}
                    sel_ev = st.selectbox("İşlem Yapılacak Evi Seçin", list(ev_dict.keys()))
                    sel_id = ev_dict[sel_ev]
                    
                    col_up, col_del = st.columns(2)
                    with col_up:
                        new_adr = st.text_input("Adresi Güncelle", key="new_adr_in")
                        if st.button("Güncelle", key="btn_up_ev"):
                            if new_adr:
                                c.execute("UPDATE AKILLI_EV SET Adres=? WHERE Numara=?", (new_adr, sel_id))
                                conn.commit()
                                st.toast("Güncellendi!", icon="🔄")
                                time.sleep(0.5)
                                st.rerun()
                    
                    with col_del:
                        st.write("") 
                        st.write("") 
                        if st.button("🗑️ Evi Sil (CASCADE)", key="btn_del_ev", type="secondary"):
                            c.execute("DELETE FROM AKILLI_EV WHERE Numara=?", (sel_id,))
                            conn.commit()
                            st.toast("Ev silindi!", icon="🗑️")
                            time.sleep(0.5)
                            st.rerun()

    # --- TAB 2: KULLANICI & E-POSTA (GÜNCELLENDİ) ---
    with tab_user:
        # ÜST KISIM: KULLANICI EKLEME VE SİLME
        c1, c2 = st.columns([1, 2])
        evler = c.execute("SELECT Numara, Adres FROM AKILLI_EV").fetchall()
        ev_dict = {f"Ev No: {e[0]}": e[0] for e in evler}

        with c1:
            st.markdown("#### 👤 Kullanıcı Ekle")
            with st.form("add_user", clear_on_submit=True):
                u_id = st.number_input("TC Kimlik No", min_value=1)
                u_ad = st.text_input("Ad")
                u_soyad = st.text_input("Soyad")
                u_fk = st.selectbox("Bağlı Olduğu Ev (FK)", list(ev_dict.keys()) if ev_dict else [])
                
                if st.form_submit_button("Kullanıcıyı Kaydet"):
                    if u_fk:
                        try:
                            c.execute("INSERT INTO KULLANICI VALUES (?,?,?,?)", (u_id, u_ad, u_soyad, ev_dict[u_fk]))
                            conn.commit()
                            st.toast("Kullanıcı eklendi!", icon="👤")
                            time.sleep(0.5)
                            st.rerun()
                        except:
                            st.error("Hata oluştu.")
                    else:
                        st.warning("Önce ev ekleyin.")

        with c2:
            st.markdown("#### 📋 Kullanıcı Listesi & Arama")
            search_user = st.text_input("🔍 Kullanıcı Ara", placeholder="Ad veya Soyad...")
            q_user = "SELECT * FROM KULLANICI"
            df_user = pd.read_sql(q_user, conn)
            if search_user:
                df_user = df_user[df_user['Adi'].str.contains(search_user, case=False) | df_user['Soyadi'].str.contains(search_user, case=False)]
            st.dataframe(df_user, use_container_width=True, hide_index=True)

            with st.expander("🗑️ Kullanıcı Sil"):
                users = c.execute("SELECT KimlikNo, Adi, Soyadi FROM KULLANICI").fetchall()
                if users:
                    u_d = {f"{u[1]} {u[2]} (ID:{u[0]})": u[0] for u in users}
                    s_u = st.selectbox("Silinecek Kullanıcı", list(u_d.keys()))
                    if st.button("Kullanıcıyı Sil", key="del_user"):
                        c.execute("DELETE FROM KULLANICI WHERE KimlikNo=?", (u_d[s_u],))
                        conn.commit()
                        st.toast("Kullanıcı silindi.", icon="🗑️")
                        time.sleep(0.5)
                        st.rerun()

        # --- ALT KISIM: E-POSTA YÖNETİMİ (YENİ EKLENDİ) ---
        st.divider()
        st.subheader("✉️ E-Posta Yönetimi (Çok Değerli Nitelik)")
        
        ce1, ce2 = st.columns(2)
        
        with ce1:
            st.info("Bir kullanıcının birden fazla e-postası olabilir. Buradan ekleyebilirsiniz.")
            users_mail = c.execute("SELECT KimlikNo, Adi, Soyadi FROM KULLANICI").fetchall()
            if users_mail:
                u_mail_dict = {f"{u[1]} {u[2]} (ID:{u[0]})": u[0] for u in users_mail}
                sel_user_mail = st.selectbox("Kullanıcı Seçin", list(u_mail_dict.keys()), key="sel_u_mail")
                new_email = st.text_input("E-Posta Adresi Girin")
                
                if st.button("E-Postayı Ekle", key="btn_add_mail"):
                    if new_email:
                        try:
                            c.execute("INSERT INTO KULLANICI_EPOSTA VALUES (?,?)", (u_mail_dict[sel_user_mail], new_email))
                            conn.commit()
                            st.toast("E-posta eklendi!", icon="📧")
                            time.sleep(0.5)
                            st.rerun()
                        except:
                            st.error("Bu e-posta zaten kayıtlı.")
                    else:
                        st.warning("Lütfen e-posta yazın.")
            else:
                st.warning("Kullanıcı yok.")

        with ce2:
            if users_mail:
                sel_id_mail = u_mail_dict[sel_user_mail]
                st.markdown(f"**{sel_user_mail}** kişisine ait e-postalar:")
                df_mail = pd.read_sql(f"SELECT * FROM KULLANICI_EPOSTA WHERE KullaniciKimlikNo={sel_id_mail}", conn)
                st.dataframe(df_mail, use_container_width=True, hide_index=True)

# =============================================================================
# MODÜL 2: CİHAZ YÖNETİMİ
# =============================================================================
elif menu == "📹 Cihaz Yönetimi":
    st.title("📹 Cihaz Envanter & Yönetimi")
    
    t1, t2, t3 = st.tabs(["➕ Yeni Cihaz", "🔗 Ev Bağlantısı", "⚙️ Düzenle / Sil"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            with st.form("add_dev", clear_on_submit=True):
                d_no = st.number_input("Cihaz Seri No", min_value=1)
                d_tur = st.selectbox("Cihaz Türü", ["Kamera", "Hareket Sensörü", "Akıllı Kilit", "Duman Dedektörü"])
                d_dur = st.selectbox("Başlangıç Durumu", ["Aktif", "İnaktif"])
                if st.form_submit_button("Envantere Ekle"):
                    try:
                        c.execute("INSERT INTO GUVENLIK_CIHAZI VALUES (?,?,?)", (d_no, d_tur, d_dur))
                        conn.commit()
                        st.toast("Cihaz eklendi!", icon="📹")
                    except:
                        st.error("Bu seri no zaten var.")
        with c2:
            st.markdown("###### Cihaz Listesi & Arama")
            search_dev = st.text_input("🔍 Cihaz Ara", placeholder="Cihaz Türü...")
            df_dev = pd.read_sql("SELECT * FROM GUVENLIK_CIHAZI", conn)
            
            if search_dev:
                df_dev = df_dev[df_dev['Turu'].str.contains(search_dev, case=False)]
                
            st.dataframe(df_dev, use_container_width=True, hide_index=True)

    with t2:
        col_a, col_b = st.columns([1, 2])
        with col_a:
            devs = c.execute("SELECT Numara, Turu FROM GUVENLIK_CIHAZI").fetchall()
            homes = c.execute("SELECT Numara, Adres FROM AKILLI_EV").fetchall()
            if devs and homes:
                d_dict = {f"{d[1]} (ID: {d[0]})": d[0] for d in devs}
                h_dict = {f"Ev No: {h[0]}": h[0] for h in homes}
                sel_dev = st.selectbox("Hangi Cihaz?", list(d_dict.keys()))
                sel_home = st.selectbox("Hangi Eve?", list(h_dict.keys()))
                if st.button("Bağlantıyı Kur (VARDIR Tablosu)"):
                    try:
                        c.execute("INSERT INTO VARDIR VALUES (?,?)", (h_dict[sel_home], d_dict[sel_dev]))
                        conn.commit()
                        st.toast("Bağlantı başarılı!", icon="🔗")
                        time.sleep(0.5)
                        st.rerun()
                    except:
                        st.warning("Bu cihaz zaten bu evde.")
        
        with col_b:
            st.markdown("###### Aktif Bağlantılar (VARDIR)")
            q = """SELECT V.AkilliEvNumara as EvID, E.Adres, V.GuvenlikCihaziNumara as CihazID, C.Turu 
                   FROM VARDIR V JOIN AKILLI_EV E ON V.AkilliEvNumara = E.Numara 
                   JOIN GUVENLIK_CIHAZI C ON V.GuvenlikCihaziNumara = C.Numara"""
            st.dataframe(pd.read_sql(q, conn), use_container_width=True, hide_index=True)

    with t3:
        devs = c.execute("SELECT Numara, Turu, Durumu FROM GUVENLIK_CIHAZI").fetchall()
        if devs:
            d_d = {f"{d[1]} (ID:{d[0]}) - {d[2]}": d[0] for d in devs}
            target_d = st.selectbox("İşlem Yapılacak Cihazı Seç", list(d_d.keys()))
            target_id = d_d[target_d]
            
            c_edit, c_del = st.columns(2)
            with c_edit:
                new_st = st.selectbox("Yeni Durum", ["Aktif", "İnaktif", "Arızalı"])
                if st.button("Durumu Güncelle"):
                    c.execute("UPDATE GUVENLIK_CIHAZI SET Durumu=? WHERE Numara=?", (new_st, target_id))
                    conn.commit()
                    st.toast("Durum güncellendi!", icon="🔄")
                    time.sleep(0.5)
                    st.rerun()
            with c_del:
                st.write("")
                st.write("")
                if st.button("🗑️ Cihazı Tamamen Sil"):
                    c.execute("DELETE FROM GUVENLIK_CIHAZI WHERE Numara=?", (target_id,))
                    conn.commit()
                    st.toast("Cihaz silindi!", icon="🗑️")
                    time.sleep(0.5)
                    st.rerun()

# =============================================================================
# MODÜL 3: OLAY & ALARM
# =============================================================================
elif menu == "⚡ Olay & Alarm":
    st.title("⚡ Güvenlik Olayları ve Alarmlar")
    t_olay, t_alarm = st.tabs(["⚡ Olay Yönetimi", "🚨 Alarm Yönetimi"])
    
    with t_olay:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("##### Olay Kaydet")
            with st.form("add_olay"):
                o_no = st.number_input("Olay ID", min_value=5000)
                o_tur = st.text_input("Olay Tipi", "Hareket Algılandı")
                if st.form_submit_button("Olayı Oluştur"):
                    now = datetime.now()
                    try:
                        c.execute("INSERT INTO OLAY VALUES (?,?,?,?)", (o_no, o_tur, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")))
                        conn.commit()
                        st.toast("Olay kaydedildi!", icon="⚡")
                        time.sleep(0.5)
                        st.rerun()
                    except:
                        st.error("Hata.")
            
            st.markdown("##### 🗑️ Olay Sil")
            olays = c.execute("SELECT Numara, Turu FROM OLAY").fetchall()
            if olays:
                o_dict = {f"{o[1]} (ID:{o[0]})": o[0] for o in olays}
                del_o = st.selectbox("Silinecek Olay", list(o_dict.keys()))
                if st.button("Seçili Olayı Sil"):
                    c.execute("DELETE FROM OLAY WHERE Numara=?", (o_dict[del_o],))
                    conn.commit()
                    st.toast("Olay silindi.", icon="🗑️")
                    time.sleep(0.5)
                    st.rerun()

        with c2:
            st.markdown("##### Olay Geçmişi & Arama")
            search_olay = st.text_input("🔍 Olay Ara", placeholder="Olay Tipi...")
            df_olay = pd.read_sql("SELECT * FROM OLAY ORDER BY Numara DESC", conn)
            if search_olay:
                df_olay = df_olay[df_olay['Turu'].str.contains(search_olay, case=False)]
            
            st.dataframe(df_olay, use_container_width=True, hide_index=True)
            
            st.divider()
            st.markdown("##### Olayı Cihaza Bağla (KAYDEDER)")
            devs = c.execute("SELECT Numara, Turu FROM GUVENLIK_CIHAZI").fetchall()
            if olays and devs:
                d_d = {f"{d[1]} (ID:{d[0]})": d[0] for d in devs}
                s_o = st.selectbox("Olay Seç", list(o_dict.keys()), key="sel_o_kay")
                s_d = st.selectbox("Kaydeden Cihaz", list(d_d.keys()), key="sel_d_kay")
                if st.button("İlişkiyi Kaydet"):
                    try:
                        c.execute("INSERT INTO KAYDEDER VALUES (?,?)", (d_d[s_d], o_dict[s_o]))
                        conn.commit()
                        st.toast("İlişki kuruldu!", icon="✅")
                    except:
                        st.error("Hata.")

    with t_alarm:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("##### Alarm Oluştur")
            with st.form("add_alarm"):
                a_no = st.number_input("Alarm ID", min_value=9000)
                if st.form_submit_button("Alarm Başlat"):
                    now = datetime.now()
                    try:
                        c.execute("INSERT INTO ALARM VALUES (?,?,?,?)", (a_no, "AÇIK", now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")))
                        conn.commit()
                        st.toast("Alarm başladı!", icon="🚨")
                        time.sleep(0.5)
                        st.rerun()
                    except:
                        st.error("Hata.")
            st.markdown("##### 🗑️ Alarm Sil")
            alarms = c.execute("SELECT Numara, Durum FROM ALARM").fetchall()
            if alarms:
                a_dict = {f"Alarm ID:{a[0]} ({a[1]})": a[0] for a in alarms}
                del_a = st.selectbox("Silinecek Alarm", list(a_dict.keys()))
                if st.button("Alarmı Sil"):
                    c.execute("DELETE FROM ALARM WHERE Numara=?", (a_dict[del_a],))
                    conn.commit()
                    st.toast("Alarm silindi.", icon="🗑️")
                    time.sleep(0.5)
                    st.rerun()

        with c2:
            st.markdown("##### Alarm Listesi")
            st.dataframe(pd.read_sql("SELECT * FROM ALARM ORDER BY Numara DESC", conn), use_container_width=True, hide_index=True)
            
            st.divider()
            st.markdown("##### Tetikleyen Olayı Seç (TETİKLER)")
            olays = c.execute("SELECT Numara, Turu FROM OLAY").fetchall()
            if alarms and olays:
                o_d = {f"{o[1]} (ID:{o[0]})": o[0] for o in olays}
                s_a = st.selectbox("Hangi Alarm?", list(a_dict.keys()), key="sel_a_tet")
                s_o = st.selectbox("Tetikleyen Olay", list(o_d.keys()), key="sel_o_tet")
                if st.button("TETİKLER Tablosuna İşle"):
                    try:
                        c.execute("INSERT INTO TETIKLER VALUES (?,?)", (o_d[s_o], a_dict[s_a]))
                        conn.commit()
                        st.toast("Bağlantı yapıldı!", icon="🔗")
                    except:
                        st.error("Hata.")

# =============================================================================
# MODÜL 5: ANALİTİK RAPORLAR
# =============================================================================
elif menu == "📈 Analitik Raporlar":
    st.title("📈 Gelişmiş Veri Analizi ve SQL Raporları")
    
    st.markdown('<div class="report-card">⚡ <b>RAPOR 1: Olay - Cihaz - Ev İlişkisi Analizi</b></div>', unsafe_allow_html=True)
    st.caption("Sistemde kaydedilen olayların mekânsal ve donanımsal kökenini uçtan uca takip eder. (5 Tablolu JOIN İşlemi)")
    q1 = """
    SELECT O.Tarih, O.Saat, O.Turu AS Olay_Turu, C.Turu AS Cihaz, E.Adres
    FROM KAYDEDER K 
    JOIN OLAY O ON K.OlayNumara = O.Numara 
    JOIN GUVENLIK_CIHAZI C ON K.GuvenlikCihaziNumara = C.Numara 
    JOIN VARDIR V ON C.Numara = V.GuvenlikCihaziNumara 
    JOIN AKILLI_EV E ON V.AkilliEvNumara = E.Numara
    ORDER BY O.Tarih DESC
    """
    try:
        st.dataframe(pd.read_sql(q1, conn), use_container_width=True)
    except:
        st.info("Veri yok.")

    st.markdown("---")
    st.markdown('<div class="report-card">📊 <b>RAPOR 2: Alarm ve Tetikleyici Olay Analizi</b></div>', unsafe_allow_html=True)
    q2 = """
    SELECT A.Numara AS AlarmID, A.Durum, O.Turu AS Tetikleyen_Olay, O.Tarih
    FROM ALARM A
    JOIN TETIKLER T ON A.Numara = T.AlarmNumara
    JOIN OLAY O ON T.OlayNumara = O.Numara
    """
    try:
        st.dataframe(pd.read_sql(q2, conn), use_container_width=True)
    except:
        st.info("Veri yok.")

    st.markdown("---")
    st.markdown('<div class="report-card">🏠 <b>RAPOR 3: Ev Başına Cihaz İstatistiği</b></div>', unsafe_allow_html=True)
    q3 = """
    SELECT E.Adres, COUNT(V.GuvenlikCihaziNumara) AS Toplam_Cihaz 
    FROM AKILLI_EV E 
    LEFT JOIN VARDIR V ON E.Numara = V.AkilliEvNumara
    GROUP BY E.Numara, E.Adres
    """
    try:
        st.dataframe(pd.read_sql(q3, conn), use_container_width=True)
    except:
        st.info("Veri yok.")
        
    st.markdown("---")
    st.markdown('<div class="report-card">🚨 <b>RAPOR 4: Aktif Alarmların Konumları</b></div>', unsafe_allow_html=True)
    q4 = """
    SELECT A.Numara AS Alarm_ID, O.Turu AS Sebep, E.Adres, E.EvSahibi 
    FROM ALARM A
    JOIN TETIKLER T ON A.Numara = T.AlarmNumara
    JOIN OLAY O ON T.OlayNumara = O.Numara
    JOIN KAYDEDER K ON O.Numara = K.OlayNumara
    JOIN GUVENLIK_CIHAZI C ON K.GuvenlikCihaziNumara = C.Numara
    JOIN VARDIR V ON C.Numara = V.GuvenlikCihaziNumara
    JOIN AKILLI_EV E ON V.AkilliEvNumara = E.Numara
    WHERE A.Durum = 'AÇIK'
    """
    try:
        st.dataframe(pd.read_sql(q4, conn), use_container_width=True)
    except:
        st.info("Veri yok.")

    st.markdown("---")
    st.markdown('<div class="report-card">📈 <b>RAPOR 5: Cihaz Türü İstatistikleri</b></div>', unsafe_allow_html=True)
    q5 = """
    SELECT C.Turu, COUNT(O.Numara) AS Toplam_Olay 
    FROM GUVENLIK_CIHAZI C
    JOIN KAYDEDER K ON C.Numara = K.GuvenlikCihaziNumara
    JOIN OLAY O ON K.OlayNumara = O.Numara
    GROUP BY C.Turu
    """
    try:
        st.dataframe(pd.read_sql(q5, conn), use_container_width=True)
    except:
        st.info("Veri yok.")

# =============================================================================
# MODÜL 6: KAYITLAR
# =============================================================================
elif menu == "📂 Veritabanı Kayıtları":
    st.title("📂 Veritabanı Müfettişi")
    
    tables = ["AKILLI_EV", "KULLANICI", "KULLANICI_EPOSTA", "GUVENLIK_CIHAZI", "VARDIR", "OLAY", "KAYDEDER", "ALARM", "TETIKLER"]
    sel_tab = st.selectbox("İncelemek İstediğiniz Tabloyu Seçin:", tables)
    
    try:
        df = pd.read_sql(f"SELECT * FROM {sel_tab}", conn)
        st.markdown(f"### 📋 {sel_tab} ({len(df)} Kayıt)")
        
        # Bu sayfaya da arama koyalım tam olsun
        search_raw = st.text_input("🔍 Tablo İçinde Ara")
        if search_raw and not df.empty:
            # Tüm sütunlarda arama yapma
            mask = df.astype(str).apply(lambda x: x.str.contains(search_raw, case=False, na=False)).any(axis=1)
            df = df[mask]
            
        st.dataframe(df, use_container_width=True)
    except:
        st.error("Tablo okunamadı.")

conn.close()
