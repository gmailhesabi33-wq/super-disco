# ⏰ Discord Yetkili Uygulama (User-Installable) Hatırlatıcı Botu

Bu bot, Discord'un **Yetkili Uygulama (User App / User Install)** özelliğini kullanarak doğrudan **Discord hesabınıza** eklenir. Botu herhangi bir sunucuya davet etmenize gerek kalmadan; istediğiniz sunucuda, özel mesajlarda (DM) veya grup sohbetlerinde `/hatırlatıcı` komutunu kullanabilir ve tam belirttiğiniz zamanda **DM (Özel Mesaj)** üzerinden bildirim alabilirsiniz.

---

## 🚀 Özellikler

- **Yetkili Uygulama Desteği (User Install):** Hesabınıza bir kez yetkilendirirsiniz, Discord'da bulunduğunuz her yerde çalışır!
- **Doğal Türkçe Tarih & Saat Desteği:**
  - `5 Ekim 2026 17:00`
  - `15.11.2026 14:30`
  - `10 dakika sonra`, `2 saat sonra`, `3 gün sonra`
  - `15dk`, `30sn`, `2sa`, `1gün`
  - `yarın 15:30`
- **Kalıcı SQLite Veritabanı:** Bot veya bilgisayar kapansa bile hatırlatıcılarınız kaybolmaz (`reminders.db`).
- **Aktif Liste ve İptal Etme:** `/hatırlatıcılar` ile bekleyenleri görebilir, `/hatırlatıcı-sil` ile silebilirsiniz.
- **Discord Zaman Göstergesi:** Hatırlatıcı kurulduğunda Discord'un `<t:zaman:R>` formatı sayesinde dinamik geri sayım gösterilir.

---

## 🛠️ Discord Developer Portal Kurulumu (Yetkili Uygulama Ayarları)

Botun hesabınıza **"Yetkili Uygulama"** olarak eklenebilmesi için şu adımları uygulayın:

### 1. Bot Oluşturma
1. [Discord Developer Portal](https://discord.com/developers/applications) adresine gidin.
2. Sağ üstten **New Application** butonuna tıklayın, bota bir isim verin (örn: `Hatırlatıcı Bot`) ve onaylayın.
3. Sol menüden **Bot** sekmesine gelin.
4. **Reset Token** butonuna tıklayarak botunuzun tokenini kopyalayın (Bu tokeni kimseyle paylaşmayın).

### 2. Yetkili Uygulama (User Install) Yetkilendirmesi
1. Sol menüden **Installation** sekmesine gelin.
2. **Installation Contexts** (Kurulum Kapsamları) bölümünde:
   - ✅ **Guild Install** (İsteğe bağlı, sunuculara ekleme)
   - ✅ **User Install** (**MUTLAKA İŞARETLEYİN** - Hesaba yetkili uygulama olarak eklenmesini sağlar).
3. **Default Install Settings** bölümünde:
   - **Scopes:** `applications.commands` ve `bot` seçin.
   - **Permissions:** `Send Messages`, `Embed Links`, `Read Message History` izinlerini seçin.
4. Sayfanın altındaki yeşil **Save Changes** butonuna tıklayın.

### 3. Botu Hesabınıza Ekleme
1. Yine **Installation** sekmesinde **Install Link** kısmını **Discord Provided Link** olarak seçin veya:
   - Sol menüden **OAuth2** -> **URL Generator** sekmesine gidin.
   - **Scopes** kısmından `applications.commands` ve `bot` işaretleyin.
   - **Integration Type** kısmından **User Install** (Kullanıcı Kurulumu) seçin.
2. Oluşan bağlantıyı kopyalayıp tarayıcınızda açın.
3. Discord size **"Uygulamayı Hesabına Ekle"** seçeneğini gösterecektir. Onaylayarak hesabınıza yetkili uygulama olarak ekleyin!

---

## 💻 Kurulum ve Çalıştırma

### 1. Token Tanımlama
Klasördeki `.env.example` dosyasının adını `.env` yapın (veya bir kopyasını oluşturup `.env` olarak adlandırın).  
İçerisine bot tokeninizi yapıştırın:
```env
DISCORD_TOKEN=BURAYA_DISCORD_BOT_TOKENINIZI_YAZIN
```

### 2. Botu Başlatma
Windows üzerinde klasördeki **`start.bat`** dosyasına çift tıklayarak botu başlatabilirsiniz.

Veya terminalden:
```powershell
py -m pip install -r requirements.txt
py bot.py
```

Bot çalışınca konsolda:
```text
[INFO] Bot giriş yaptı: Hatırlatıcı Bot#1234
[INFO] Slash komutları Discord'a senkronize ediliyor (Global)...
[INFO] 4 adet slash komutu başarıyla senkronize edildi.
```
mesajını göreceksiniz.

---

## 📱 Kullanım Komutları

Artık Discord'da herhangi bir sohbette (DM, sunucu, grup) komutları kullanabilirsiniz:

### 1. `/hatırlatıcı`
```text
/hatırlatıcı neyihatirlatcak: "Diş randevusu" nekadarsureicindehatirlatcak: "5 Ekim 2026 17:00"
/hatırlatıcı neyihatirlatcak: "Fırındaki yemeği kontrol et" nekadarsureicindehatirlatcak: "25 dakika"
/hatırlatıcı neyihatirlatcak: "Toplantı var" nekadarsureicindehatirlatcak: "yarın 14:00"
/hatırlatıcı neyihatirlatcak: "Mola ver" nekadarsureicindehatirlatcak: "45dk"
```
> **Önemli Not:** Hatırlatma zamanı geldiğinde bot size **Özel Mesaj (DM)** gönderir. Botun size DM atabilmesi için Discord **Gizlilik Ayarları**'nızda Direkt Mesajların açık olduğundan emin olun veya bot ile bir kez DM sohbeti açın.

### 2. `/hatırlatıcılar`
Bekleyen tüm aktif hatırlatıcılarınızı, kalan sürelerini ve ID numaralarını listeler.

### 3. `/hatırlatıcı-sil`
```text
/hatırlatıcı-sil hatirlatici_id: 1
```
İptal etmek istediğiniz hatırlatıcıyı siler.

### 4. `/yardım`
Kullanım rehberini ve desteklenen tüm zaman formatlarını Discord arayüzünde gösterir.
