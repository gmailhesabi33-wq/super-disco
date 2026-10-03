"""
Discord Hatırlatıcı Botu (bot.py)
Yetkili Uygulama (User-Installable App) olarak çalışır.
Kullanıcılar botu doğrudan Discord hesaplarına ekleyebilir ve her yerde (DM, grup, sunucular)
/hatırlatıcı komutunu kullanarak belirtilen tarihte DM hatırlatması alabilirler.
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

from time_parser import parse_reminder_time, TURKEY_TZ
from database import (
    init_db,
    add_reminder,
    get_due_reminders,
    mark_reminder_completed,
    get_user_reminders,
    delete_reminder
)

# Ortam değişkenlerini yükle (.env dosyasından)
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("HatirlaticiBot")

# Bot istemcisi
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    logger.info(f"Bot giriş yaptı: {bot.user} (ID: {bot.user.id})")
    logger.info("Hatırlatıcı kontrol görevi başlatılıyor...")
    if not check_reminders_task.is_running():
        check_reminders_task.start()


@bot.event
async def setup_hook():
    """Bot başlatılırken veritabanını hazırlar ve komutları senkronize eder."""
    logger.info("Veritabanı ilklendiriliyor...")
    await init_db()

    logger.info("Slash komutları Discord'a senkronize ediliyor (Global)...")
    try:
        synced = await bot.tree.sync()
        logger.info(f"{len(synced)} adet slash komutu başarıyla senkronize edildi.")
    except Exception as e:
        logger.error(f"Komut senkronizasyon hatası: {e}")


# ==========================================
# 1. /hatırlatıcı KOMUTU (Yetkili Uygulama Destekli)
# ==========================================
@bot.tree.command(
    name="hatırlatıcı",
    description="Belirttiğiniz tarihte veya sürede size DM üzerinden hatırlatma mesajı gönderir."
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(
    neyihatirlatcak="Hatırlatılmasını istediğiniz not, mesaj veya konu",
    nekadarsureicindehatirlatcak="Ne zaman hatırlatılsın? (Örn: '5 Ekim 2026 17:00', '10 dakika', 'yarın 15:30')"
)
async def hatirlatici(
    interaction: discord.Interaction,
    neyihatirlatcak: str,
    nekadarsureicindehatirlatcak: str
):
    # Zamanı analiz et
    target_dt, error_msg = parse_reminder_time(nekadarsureicindehatirlatcak)
    if error_msg or not target_dt:
        embed_err = discord.Embed(
            title="❌ Geçersiz Zaman Formatı",
            description=error_msg or "Zaman anlaşılamadı.",
            color=0xED4245
        )
        await interaction.response.send_message(embed=embed_err, ephemeral=True)
        return

    target_ts = target_dt.timestamp()
    unix_ts = int(target_ts)

    # Veritabanına kaydet
    reminder_id = await add_reminder(
        user_id=interaction.user.id,
        channel_id=interaction.channel_id,
        remind_text=neyihatirlatcak,
        target_timestamp=target_ts
    )

    # Başarılı yanıt
    embed = discord.Embed(
        title="⏰ Hatırlatıcı Başarıyla Kuruldu!",
        description="Belirttiğiniz tarih ve saatte size **DM (Özel Mesaj)** üzerinden bildirim gönderilecektir.",
        color=0x5865F2,
        timestamp=target_dt
    )
    embed.add_field(
        name="📝 Hatırlatılacak Not",
        value=f"```\n{neyihatirlatcak}\n```",
        inline=False
    )
    embed.add_field(
        name="📅 Hatırlatma Zamanı",
        value=f"<t:{unix_ts}:F>\n(<t:{unix_ts}:R>)",
        inline=True
    )
    embed.add_field(
        name="🆔 Hatırlatıcı No",
        value=f"`#{reminder_id}`",
        inline=True
    )
    embed.set_footer(
        text="💡 Botun DM gönderebilmesi için Gizlilik Ayarlarınızdan DM'lerin açık olduğundan emin olun."
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)
    logger.info(f"Kullanıcı {interaction.user} (ID: {interaction.user.id}) hatırlatıcı kurdu: #{reminder_id} - {target_dt}")


# ==========================================
# 2. /hatırlatıcılar KOMUTU (Aktif Listesi)
# ==========================================
@bot.tree.command(
    name="hatırlatıcılar",
    description="Bekleyen aktif hatırlatıcılarınızı listeler."
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def hatirlaticilar(interaction: discord.Interaction):
    reminders = await get_user_reminders(interaction.user.id)

    if not reminders:
        embed = discord.Embed(
            title="📋 Hatırlatıcı Listeniz",
            description="Şu anda bekleyen herhangi bir aktif hatırlatıcınız bulunmuyor.\n`/hatırlatıcı` komutu ile yeni bir tane ekleyebilirsiniz!",
            color=0x5865F2
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title=f"📋 Aktif Hatırlatıcılarınız ({len(reminders)} adet)",
        description="Aşağıda zamanı bekleyen tüm hatırlatıcılarınız listelenmiştir:",
        color=0x5865F2
    )

    for rem in reminders[:15]:  # En fazla 15 kayıt göster
        ts = int(rem["target_timestamp"])
        not_metni = rem["remind_text"]
        if len(not_metni) > 50:
            not_metni = not_metni[:47] + "..."
        embed.add_field(
            name=f"🆔 #{rem['id']} • <t:{ts}:R>",
            value=f"📅 <t:{ts}:F>\n💬 {not_metni}",
            inline=False
        )

    embed.set_footer(text="Bir hatırlatıcıyı silmek için: /hatırlatıcı-sil <id>")
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==========================================
# 3. /hatırlatıcı-sil KOMUTU
# ==========================================
@bot.tree.command(
    name="hatırlatıcı-sil",
    description="ID numarasını belirttiğiniz bir hatırlatıcınızı iptal eder/siler."
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(
    hatirlatici_id="Silmek istediğiniz hatırlatıcının numarası (örn: 1)"
)
async def hatirlatici_sil(interaction: discord.Interaction, hatirlatici_id: int):
    success = await delete_reminder(reminder_id=hatirlatici_id, user_id=interaction.user.id)
    if success:
        embed = discord.Embed(
            title="🗑️ Hatırlatıcı Silindi",
            description=f"`#{hatirlatici_id}` numaralı hatırlatıcı başarıyla silindi.",
            color=0x57F287
        )
    else:
        embed = discord.Embed(
            title="❌ Bulunamadı",
            description=f"`#{hatirlatici_id}` numaralı bir hatırlatıcınız bulunamadı veya daha önce silinmiş.",
            color=0xED4245
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==========================================
# 4. /yardım KOMUTU
# ==========================================
@bot.tree.command(
    name="yardım",
    description="Hatırlatıcı botunun nasıl kullanılacağını ve zaman formatlarını gösterir."
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def yardim(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📖 Hatırlatıcı Botu Kullanım Kılavuzu",
        description="Bu bot bir **Yetkili Uygulama**'dır. Hesabınıza eklediğinizde her sunucuda ve özel mesajlarda çalışır!",
        color=0x5865F2
    )
    embed.add_field(
        name="📌 Komut Formatı",
        value="`/hatırlatıcı neyihatirlatcak: [Not] nekadarsureicindehatirlatcak: [Zaman]`",
        inline=False
    )
    embed.add_field(
        name="⏰ Örnek Zaman Girişleri",
        value=(
            "• **Tam Tarih ve Saat:** `5 Ekim 2026 17:00`\n"
            "• **Gün/Ay Formatı:** `15.11.2026 14:30`\n"
            "• **Göreceli Süreler:** `10 dakika`, `2 saat`, `3 gün`\n"
            "• **Kısaltmalar:** `15dk`, `30sn`, `1sa`, `2gün`\n"
            "• **Doğal Dil:** `yarın 15:30`, `1 saat sonra`"
        ),
        inline=False
    )
    embed.add_field(
        name="⚙️ Diğer Komutlar",
        value=(
            "• `/hatırlatıcılar` - Aktif hatırlatıcılarınızı listeler.\n"
            "• `/hatırlatıcı-sil <id>` - Bir hatırlatıcıyı iptal eder.\n"
            "• `/yardım` - Bu kılavuzu gösterir."
        ),
        inline=False
    )
    embed.set_footer(text="Geliştirici: Google Antigravity • Python discord.py")
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==========================================
# ARKA PLAN GÖREVİ (Zamanı Gelenleri DM ile Gönder)
# ==========================================
@tasks.loop(seconds=5)
async def check_reminders_task():
    """Her 5 saniyede bir veritabanını tarar ve vakti gelen hatırlatıcıları DM ile gönderir."""
    try:
        due_items = await get_due_reminders()
        for item in due_items:
            reminder_id = item["id"]
            user_id = item["user_id"]
            remind_text = item["remind_text"]
            created_ts = item["created_timestamp"]

            # Tekrar gönderilmemesi için önce tamamlandı olarak işaretle
            await mark_reminder_completed(reminder_id)

            # Kullanıcıyı bul
            user = bot.get_user(user_id)
            if not user:
                try:
                    user = await bot.fetch_user(user_id)
                except Exception as fetch_err:
                    logger.error(f"Kullanıcı fetch edilemedi (ID: {user_id}): {fetch_err}")
                    continue

            # DM Mesajını hazırla
            embed = discord.Embed(
                title="🔔 Hatırlatıcı Zamanı Geldi!",
                description=f"Merhaba! Daha önce kurmuş olduğunuz hatırlatıcının zamanı geldi:\n\n💬 **Notunuz:**\n```\n{remind_text}\n```",
                color=0x57F287,
                timestamp=datetime.now(TURKEY_TZ)
            )
            embed.add_field(
                name="⏰ Kurulma Zamanı",
                value=f"<t:{int(created_ts)}:R>",
                inline=True
            )
            embed.set_footer(text=f"Hatırlatıcı ID: #{reminder_id}")

            # DM gönder
            try:
                await user.send(embed=embed)
                logger.info(f"Hatırlatıcı #{reminder_id} kullanıcıya başarıyla DM gönderildi: {user} (ID: {user_id})")
            except discord.Forbidden:
                logger.warning(f"Kullanıcıya DM gönderilemedi! DM'leri kapalı veya botu engellemiş: {user} (ID: {user_id})")
            except Exception as send_err:
                logger.error(f"DM gönderme hatası (#{reminder_id}): {send_err}")

    except Exception as e:
        logger.error(f"check_reminders_task döngü hatası: {e}")


@check_reminders_task.before_loop
async def before_check_reminders():
    await bot.wait_until_ready()


def main():
    if not TOKEN:
        logger.error(
            "DISCORD_TOKEN bulunamadı!\n"
            "Lütfen .env dosyası oluşturup içine DISCORD_TOKEN=botunuzun_tokeni yazın."
        )
        sys.exit(1)

    logger.info("Bot başlatılıyor...")
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
