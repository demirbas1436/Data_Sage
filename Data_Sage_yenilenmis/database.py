import sqlite3

# Veritabanına bağlan
veritabani_yolu = "sakila.db"  # Buraya kendi dosya adını yaz
conn = sqlite3.connect(veritabani_yolu)
cursor = conn.cursor()

# Mevcut tabloları al
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablolar = cursor.fetchall()

print("Mevcut Tablolar:")
for tablo in tablolar:
    print(f"- {tablo[0]}")

    # Her tablo için sütunları al
    cursor.execute(f"PRAGMA table_info({tablo[0]});")
    sutunlar = cursor.fetchall()

    print("  Sütunlar:")
    for sutun in sutunlar:
        print(f"    - {sutun[1]} ({sutun[2]})")  # Sütun adı ve veri tipi

# Bağlantıyı kapat
conn.close()
