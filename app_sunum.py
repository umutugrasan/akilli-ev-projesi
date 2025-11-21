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

# --- 2. AYARLAR VE TASARIM ---
st.set_page_config(page_title="DB Sunum Paneli", page_icon="🎓", layout="wide")

# CSS TASARIMI
st.markdown("""
<style>
    .stApp {background-color: #0E1117;}
    div[data-testid="stMetric"] {
        background-color: #262730; border: 1px solid #3d3d3d; 
        padding: 15px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    .stDataFrame {border: 1px solid #374151; border-radius: 5px;}
    h1, h2, h3 {color: #e5e7eb; font-family: 'Helvetica Neue', sans-serif;}
    .info-box {
        padding: 10px; border-radius: 5px; background-color: #172554; color: #dbeafe;
        border-left: 5px solid #3b82f6; margin-bottom: 10px; font-size: 0.9em;
    }
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
# MODÜL 0: DASHBOARD
# =============================================================================
if menu == "📊 Dashboard (Özet)":
    st.title("📊 Sistem Genel Bakış")
    
    try:
        total_ev = c.execute("SELECT COUNT(*) FROM AKILLI_EV").fetchone()[0]
        total_user = c.execute("SELECT COUNT(*) FROM KULLANICI").fetchone()[0]
        active_dev = c.execute("SELECT COUNT(*) FROM GUVENLIK_CIHAZI WHERE Durumu='Aktif'").fetchone()[0]
        alarms = c.execute("SELECT COUNT(*) FROM ALARM").fetchone()[0]
    except:
        total_ev, total_user, active_dev, alarms = 0, 0, 0, 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏠 Kayıtlı Evler", total_ev, "Aktif")
    col2.metric("👤 Toplam Kullanıcı", total_user, "+Yeni")
    col3.metric("📹 Aktif Cihazlar", active_dev, "Online")
    col4.metric("🚨 Tetiklenen Alarmlar", alarms, "Kritik", delta_color="inverse")

    st.markdown("---")
    st.markdown("### 📝 Son Olay Akışı (Canlı Log)")
    st.caption("KAYDEDER, VARDIR ve AKILLI_EV tablolarının JOIN görünümü.")
    
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
# MODÜL 1: EV & KULLANICI (CRUD EKLENDİ)
# =============================================================================
elif menu == "1. AKILLI_EV & KULLANICI":
    st.title("🏠 Akıllı Ev ve Kullanıcı Yönetimi")
    
    # Sekmelerle Ekleme ve Düzenleme İşlemlerini Ayırdık
    tab_ev, tab_user = st.tabs(["🏠 Ev İşlemleri (Ekle/Sil/Düzenle)", "👤 Kullanıcı İşlemleri (Ekle/Sil/Düzenle)"])

    # --- TAB 1: EV YÖNETİMİ ---
    with tab_ev:
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown('<div class="info-box"><b>YENİ EV EKLE</b> (INSERT)</div>', unsafe_allow_html=True)
            with st.form("add_ev"):
                e_no = st.number_input("Ev Numara (PK)", min_value=1)
                e_adr = st.text_input("Adres")
                e_sahip = st.text_input("Ev Sahibi")
                if st.form_submit_button("Kaydet"):
                    try:
                        c.execute("INSERT INTO AKILLI_EV VALUES (?,?,?)", (e_no, e_adr, e_sahip))
                        conn.commit()
                        st.success("Ev Eklendi!")
                        time.sleep(0.5)
                        st.rerun()
                    except:
                        st.error("Bu Numara Zaten Var!")

        with c2:
            st.markdown('<div class="info-box"><b>DÜZENLE / SİL</b> (UPDATE/DELETE)</div>', unsafe_allow_html=True)
            evler = c.execute("SELECT Numara, Adres FROM AKILLI_EV").fetchall()
            if evler:
                ev_dict = {f"No: {e[0]} - {e[1]}": e[0] for e in evler}
                sel_ev = st.selectbox("İşlem Yapılacak Ev", list(ev_dict.keys()))
                sel_id = ev_dict[sel_ev]
                
                # Güncelleme Alanı
                new_adr = st.text_input("Adresi Güncelle", key="new_adr")
                col_up, col_del = st.columns(2)
                
                if col_up.button("Güncelle"):
                    if new_adr:
                        c.execute("UPDATE AKILLI_EV SET Adres=? WHERE Numara=?", (new_adr, sel_id))
                        conn.commit()
                        st.success("Adres Güncellendi!")
                        time.sleep(0.5)
                        st.rerun()
                
                if col_del.button("🗑️ Evi Sil"):
                    c.execute("DELETE FROM AKILLI_EV WHERE Numara=?", (sel_id,))
                    conn.commit()
                    st.warning("Ev ve bağlı kullanıcılar silindi (CASCADE)!")
                    time.sleep(0.5)
                    st.rerun()
            else:
                st.info("Düzenlenecek ev yok.")
        
        st.markdown("---")
        st.dataframe(pd.read_sql("SELECT * FROM AKILLI_EV", conn), use_container_width=True)

    # --- TAB 2: KULLANICI YÖNETİMİ ---
    with tab_user:
        c1, c2 = st.columns(2)
        
        # Ev listesi (FK için)
        evler = c.execute("SELECT Numara, Adres FROM AKILLI_EV").fetchall()
        ev_dict = {f"Ev No: {e[0]}": e[0] for e in evler}

        with c1:
            st.markdown('<div class="info-box"><b>KULLANICI EKLE</b> (FK Seçimli)</div>', unsafe_allow_html=True)
            with st.form("add_user"):
                u_id = st.number_input("Kimlik No (PK)", min_value=1)
                u_ad = st.text_input("Ad")
                u_soyad = st.text_input("Soyad")
                if ev_dict:
                    u_fk = st.selectbox("Hangi Ev? (Foreign Key)", list(ev_dict.keys()))
                else:
                    u_fk = None
                
                if st.form_submit_button("Kullanıcıyı Kaydet"):
                    if u_fk:
                        try:
                            fk_val = ev_dict[u_fk]
                            c.execute("INSERT INTO KULLANICI VALUES (?,?,?,?)", (u_id, u_ad, u_soyad, fk_val))
                            conn.commit()
                            st.success("Kullanıcı Eklendi!")
                            time.sleep(0.5)
                            st.rerun()
                        except:
                            st.error("Hata!")
                    else:
                        st.error("Önce Ev Ekleyin!")

        with c2:
            st.markdown('<div class="info-box"><b>KULLANICI SİL</b> (DELETE)</div>', unsafe_allow_html=True)
            users = c.execute("SELECT KimlikNo, Adi, Soyadi FROM KULLANICI").fetchall()
            if users:
                u_d = {f"{u[1]} {u[2]} (ID:{u[0]})": u[0] for u in users}
                s_u = st.selectbox("Silinecek Kullanıcı", list(u_d.keys()))
                if st.button("🗑️ Kullanıcıyı Sil"):
                    c.execute("DELETE FROM KULLANICI WHERE KimlikNo=?", (u_d[s_u],))
                    conn.commit()
                    st.warning("Kullanıcı Silindi!")
                    time.sleep(0.5)
                    st.rerun()
            else:
                st.info("Kullanıcı yok.")

        st.markdown("---")
        st.dataframe(pd.read_sql("SELECT * FROM KULLANICI", conn), use_container_width=True)

# =============================================================================
# MODÜL 2: CİHAZ (CRUD EKLENDİ)
# =============================================================================
elif menu == "2. CİHAZ & VARDIR (M:N)":
    st.title("📹 Cihaz Yönetimi")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown('<div class="info-box">1. <b>CİHAZ EKLE / GÜNCELLE</b></div>', unsafe_allow_html=True)
        tab_add, tab_up = st.tabs(["Ekle", "Durum Güncelle"])
        
        with tab_add:
            with st.form("add_dev"):
                d_no = st.number_input("Cihaz No (PK)", min_value=1)
                d_tur = st.selectbox("Türü", ["Kamera", "Sensör", "Kilit"])
                d_dur = st.selectbox("Durum", ["Aktif", "İnaktif"])
                if st.form_submit_button("Ekle"):
                    try:
                        c.execute("INSERT INTO GUVENLIK_CIHAZI VALUES (?,?,?)", (d_no, d_tur, d_dur))
                        conn.commit()
                        st.success("Eklendi")
                        time.sleep(0.5)
                        st.rerun()
                    except:
                        st.error("Hata")
        
        with tab_up:
            devs = c.execute("SELECT Numara, Turu, Durumu FROM GUVENLIK_CIHAZI").fetchall()
            if devs:
                d_d = {f"{d[1]} (No:{d[0]}) - {d[2]}": d[0] for d in devs}
                s_d = st.selectbox("Cihaz Seç", list(d_d.keys()))
                new_st = st.selectbox("Yeni Durum", ["Aktif", "İnaktif", "Arızalı"])
                if st.button("Durumu Güncelle"):
                    c.execute("UPDATE GUVENLIK_CIHAZI SET Durumu=? WHERE Numara=?", (new_st, d_d[s_d]))
                    conn.commit()
                    st.success("Güncellendi!")
                    time.sleep(0.5)
                    st.rerun()

    with c2:
        st.markdown('<div class="info-box">2. <b>VARDIR TABLOSU</b> (İlişkilendir)</div>', unsafe_allow_html=True)
        devs = c.execute("SELECT Numara, Turu FROM GUVENLIK_CIHAZI").fetchall()
        homes = c.execute("SELECT Numara, Adres FROM AKILLI_EV").fetchall()
        
        if devs and homes:
            d_dict = {f"{d[1]} (ID: {d[0]})": d[0] for d in devs}
            h_dict = {f"Ev No: {h[0]}": h[0] for h in homes}
            sel_dev = st.selectbox("Cihaz Seç (FK)", list(d_dict.keys()))
            sel_home = st.selectbox("Ev Seç (FK)", list(h_dict.keys()))
            
            if st.button("İlişkilendir (VARDIR)"):
                try:
                    c.execute("INSERT INTO VARDIR VALUES (?,?)", (h_dict[sel_home], d_dict[sel_dev]))
                    conn.commit()
                    st.success("İlişki Kuruldu")
                    time.sleep(0.5)
                    st.rerun()
                except:
                    st.warning("Zaten Var")
        
        st.markdown("**VARDIR Tablosu (Raw Data):**")
        st.dataframe(pd.read_sql("SELECT * FROM VARDIR", conn), use_container_width=True)

# =============================================================================
# MODÜL 3: OLAY & KAYDEDER
# =============================================================================
elif menu == "3. OLAY & KAYDEDER (M:N)":
    st.title("⚡ Olay Yönetimi")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="info-box"><b>OLAY YARAT</b></div>', unsafe_allow_html=True)
        with st.form("add_olay"):
            o_no = st.number_input("Olay No (PK)", min_value=5000)
            o_tur = st.text_input("Türü", "Hareket Algılandı")
            if st.form_submit_button("Olay Ekle"):
                now = datetime.now()
                try:
                    c.execute("INSERT INTO OLAY VALUES (?,?,?,?)", (o_no, o_tur, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")))
                    conn.commit()
                    st.success("Olay Eklendi")
                    time.sleep(0.5)
                    st.rerun()
                except:
                    st.error("Hata")
        st.dataframe(pd.read_sql("SELECT * FROM OLAY ORDER BY Numara DESC", conn), use_container_width=True)

    with c2:
        st.markdown('<div class="info-box"><b>KAYDEDER İLİŞKİSİ</b></div>', unsafe_allow_html=True)
        olays = c.execute("SELECT Numara, Turu FROM OLAY").fetchall()
        devs = c.execute("SELECT Numara, Turu FROM GUVENLIK_CIHAZI").fetchall()
        
        if olays and devs:
            o_d = {f"{o[1]} (ID:{o[0]})": o[0] for o in olays}
            d_d = {f"{d[1]} (ID:{d[0]})": d[0] for d in devs}
            s_o = st.selectbox("Olay (FK)", list(o_d.keys()))
            s_d = st.selectbox("Cihaz (FK)", list(d_d.keys()))
            
            if st.button("KAYDEDER'e İşle"):
                try:
                    c.execute("INSERT INTO KAYDEDER VALUES (?,?)", (d_d[s_d], o_d[s_o]))
                    conn.commit()
                    st.success("İlişki Eklendi")
                    time.sleep(0.5)
                    st.rerun()
                except:
                    st.error("Hata")
        st.dataframe(pd.read_sql("SELECT * FROM KAYDEDER", conn), use_container_width=True)

# =============================================================================
# MODÜL 4: ALARM & TETIKLER
# =============================================================================
elif menu == "4. ALARM & TETİKLER (M:N)":
    st.title("🚨 Alarm Yönetimi")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="info-box"><b>ALARM OLUŞTUR</b></div>', unsafe_allow_html=True)
        with st.form("add_alarm"):
            a_no = st.number_input("Alarm No (PK)", min_value=9000)
            if st.form_submit_button("Alarm Ekle"):
                now = datetime.now()
                try:
                    c.execute("INSERT INTO ALARM VALUES (?,?,?,?)", (a_no, "AÇIK", now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")))
                    conn.commit()
                    st.success("Alarm Eklendi")
                    time.sleep(0.5)
                    st.rerun()
                except:
                    st.error("Hata")
        st.dataframe(pd.read_sql("SELECT * FROM ALARM ORDER BY Numara DESC", conn), use_container_width=True)

    with c2:
        st.markdown('<div class="info-box"><b>TETİKLER İLİŞKİSİ</b></div>', unsafe_allow_html=True)
        alarms = c.execute("SELECT Numara FROM ALARM").fetchall()
        olays = c.execute("SELECT Numara, Turu FROM OLAY").fetchall()
        
        if alarms and olays:
            a_d = {f"Alarm ID: {a[0]}": a[0] for a in alarms}
            o_d = {f"{o[1]} (ID:{o[0]})": o[0] for o in olays}
            s_a = st.selectbox("Alarm (FK)", list(a_d.keys()))
            s_o = st.selectbox("Tetikleyen Olay (FK)", list(o_d.keys()))
            
            if st.button("TETİKLER'e İşle"):
                try:
                    c.execute("INSERT INTO TETIKLER VALUES (?,?)", (o_d[s_o], a_d[s_a]))
                    conn.commit()
                    st.success("İlişki Eklendi")
                    time.sleep(0.5)
                    st.rerun()
                except:
                    st.error("Hata")
        st.dataframe(pd.read_sql("SELECT * FROM TETIKLER", conn), use_container_width=True)

# =============================================================================
# MODÜL 5: MÜFETTİŞ (TÜM TABLOLAR)
# =============================================================================
elif menu == "5. TÜM TABLOLARI İNCELE":
    st.title("📂 Veritabanı Müfettişi")
    tab_names = ["AKILLI_EV", "KULLANICI", "KULLANICI_EPOSTA", "GUVENLIK_CIHAZI", "VARDIR", "OLAY", "KAYDEDER", "ALARM", "TETIKLER"]
    selected_table = st.selectbox("Tablo Seçin:", tab_names)
    
    st.markdown(f"### 📋 {selected_table}")
    try:
        df = pd.read_sql(f"SELECT * FROM {selected_table}", conn)
        st.dataframe(df, use_container_width=True)
        
        # Hızlı Silme Özelliği (Bonus)
        if not df.empty:
            with st.expander("⚠️ Buradan Satır Sil (Dikkat!)"):
                pk_col = df.columns[0] # İlk sütunu PK varsayalım
                val_to_del = st.selectbox("Silinecek ID'yi Seç", df[pk_col].tolist())
                if st.button("Seçili Satırı SİL"):
                    # Basit bir silme sorgusu (String/Int ayrımına dikkat edilmeli normalde ama proje için yeterli)
                    try:
                        c.execute(f"DELETE FROM {selected_table} WHERE {pk_col}=?", (val_to_del,))
                        conn.commit()
                        st.warning("Silindi!")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Silinemedi: {e}")

    except:
        st.error("Tablo okunamadı.")

conn.close()
