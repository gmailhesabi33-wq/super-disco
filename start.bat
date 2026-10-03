@echo off
chcp 65001 > nul
title Discord Hatırlatıcı Botu (Yetkili Uygulama)
echo ========================================================
echo Discord Hatirlatici Botu Baslatiliyor...
echo ========================================================

if not exist .env (
    echo [HATA] .env dosyasi bulunamadi!
    echo Lutfen .env.example dosyasini .env olarak kopyalayip DISCORD_TOKEN bilginizi girin.
    pause
    exit /b
)

py -m pip install -r requirements.txt
py bot.py
pause
