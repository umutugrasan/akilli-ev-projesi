import sqlite3
import os

# Eğer hatalı/boş bir veritabanı varsa önce onu silelim ki temiz olsun
db_name = 'smart_security_final.db'
if os.path.exists(db_name):
    os.remove(db_name)
    print("Eski/Hatalı veritabanı silindi.")

conn = sqlite3.connect(db_name)
c = conn.cursor()

# Foreign Key desteğini aç
c.execute("PRAGMA foreign_keys = ON")

# --- TABLOLARI OLUŞTUR ---

# 1. AKILLI_EV
c.execute('''CREATE TABLE IF NOT EXISTS AKILLI_EV (
                Numara INTEGER PRIMARY KEY,
                Adres TEXT,
                EvSahibi TEXT
            )''')

# 2. KULLANICI
c.execute('''CREATE TABLE IF NOT EXISTS KULLANICI (
                KimlikNo INTEGER PRIMARY KEY,
                Adi TEXT,
                Soyadi TEXT,
                AkilliEvNumara INTEGER,
                FOREIGN KEY(AkilliEvNumara) REFERENCES AKILLI_EV(Numara) ON DELETE CASCADE
            )''')

# 3. KULLANICI_EPOSTA
c.execute('''CREATE TABLE IF NOT EXISTS KULLANICI_EPOSTA (
                KullaniciKimlikNo INTEGER,
                Eposta TEXT,
                PRIMARY KEY (KullaniciKimlikNo, Eposta),
                FOREIGN KEY(KullaniciKimlikNo) REFERENCES KULLANICI(KimlikNo) ON DELETE CASCADE
            )''')

# 4. GÜVENLİK CİHAZI
c.execute('''CREATE TABLE IF NOT EXISTS GUVENLIK_CIHAZI (
                Numara INTEGER PRIMARY KEY,
                Turu TEXT,
                Durumu TEXT
            )''')

# 5. OLAY
c.execute('''CREATE TABLE IF NOT EXISTS OLAY (
                Numara INTEGER PRIMARY KEY,
                Turu TEXT,
                Tarih TEXT,
                Saat TEXT
            )''')

# 6. ALARM
c.execute('''CREATE TABLE IF NOT EXISTS ALARM (
                Numara INTEGER PRIMARY KEY,
                Durum TEXT,
                Tarih TEXT,
                Saat TEXT
            )''')

# --- İLİŞKİ TABLOLARI ---

# VARDIR
c.execute('''CREATE TABLE IF NOT EXISTS VARDIR (
                AkilliEvNumara INTEGER,
                GuvenlikCihaziNumara INTEGER,
                PRIMARY KEY (AkilliEvNumara, GuvenlikCihaziNumara),
                FOREIGN KEY(AkilliEvNumara) REFERENCES AKILLI_EV(Numara) ON DELETE CASCADE,
                FOREIGN KEY(GuvenlikCihaziNumara) REFERENCES GUVENLIK_CIHAZI(Numara) ON DELETE CASCADE
            )''')

# KAYDEDER
c.execute('''CREATE TABLE IF NOT EXISTS KAYDEDER (
                GuvenlikCihaziNumara INTEGER,
                OlayNumara INTEGER,
                PRIMARY KEY (GuvenlikCihaziNumara, OlayNumara),
                FOREIGN KEY(GuvenlikCihaziNumara) REFERENCES GUVENLIK_CIHAZI(Numara) ON DELETE CASCADE,
                FOREIGN KEY(OlayNumara) REFERENCES OLAY(Numara) ON DELETE CASCADE
            )''')

# TETIKLER
c.execute('''CREATE TABLE IF NOT EXISTS TETIKLER (
                OlayNumara INTEGER,
                AlarmNumara INTEGER,
                PRIMARY KEY (OlayNumara, AlarmNumara),
                FOREIGN KEY(OlayNumara) REFERENCES OLAY(Numara) ON DELETE CASCADE,
                FOREIGN KEY(AlarmNumara) REFERENCES ALARM(Numara) ON DELETE CASCADE
            )''')

conn.commit()
conn.close()
print("✅ VERİTABANI VE TABLOLAR BAŞARIYLA KURULDU!")