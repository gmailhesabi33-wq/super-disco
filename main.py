import os
import subprocess
import sys


def main():
    print("========================================================")
    print("Discord Hatırlatıcı Botu Başlatılıyor...")
    print("========================================================")

    # 1. .env dosyası kontrolü
    if not os.path.exists(".env"):
        print("[HATA] .env dosyası bulunamadı!")
        print(
            "Lütfen .env.example dosyasını .env olarak kopyalayıp"
            " DISCORD_TOKEN bilginizi girin."
        )
        input("Devam etmek için Enter'a basın...")
        sys.exit(1)

    # 2. Gerekli kütüphanelerin yüklenmesi
    if os.path.exists("requirements.txt"):
        print("Gerekli kütüphaneler kontrol ediliyor ve yükleniyor...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
        )

    # 3. bot.py dosyasının çalıştırılması
    if os.path.exists("bot.py"):
        print("bot.py başlatılıyor...\n")
        subprocess.run([sys.executable, "bot.py"])
    else:
        print("[HATA] bot.py dosyası bulunamadı!")
        input("Devam etmek için Enter'a basın...")


if __name__ == "__main__":
    main()