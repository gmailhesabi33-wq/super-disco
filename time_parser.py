"""
Zaman ayrıştırıcı modülü (time_parser.py)
Türkçe tarih ve saat ifadelerini (örn. '5 Ekim 2026 17:00', '10 dakika sonra', 'yarın 15:30', '2 saat')
anlar ve timezone-aware (Europe/Istanbul) datetime nesnesine dönüştürür.
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
import dateparser
import pytz

TURKEY_TZ = pytz.timezone("Europe/Istanbul")

# Kısayol regex kalıpları (örn: "10dk", "15 dakika", "2 saat", "30 sn", "1 gün")
SHORTCUT_REGEX = re.compile(
    r"^(\d+)\s*(sn|saniye|sec|second|seconds|dk|dakika|min|minute|minutes|sa|saat|hr|hour|hours|g|gun|gün|day|days|h|hf|hafta|week|weeks)(?:\s*sonra)?$",
    re.IGNORECASE
)

UNIT_MULTIPLIERS = {
    # Saniye
    "sn": "seconds", "saniye": "seconds", "sec": "seconds", "second": "seconds", "seconds": "seconds",
    # Dakika
    "dk": "minutes", "dakika": "minutes", "min": "minutes", "minute": "minutes", "minutes": "minutes",
    # Saat
    "sa": "hours", "saat": "hours", "hr": "hours", "hour": "hours", "hours": "hours",
    # Gün
    "g": "days", "gun": "days", "gün": "days", "day": "days", "days": "days",
    # Hafta
    "h": "weeks", "hf": "weeks", "hafta": "weeks", "week": "weeks", "weeks": "weeks"
}


def parse_reminder_time(time_str: str) -> Tuple[Optional[datetime], Optional[str]]:
    """
    Kullanıcının girdiği zaman metnini ayrıştırır.
    Dönüş: (datetime_objesi, hata_mesajı)
    """
    if not time_str or not time_str.strip():
        return None, "Zaman parametresi boş bırakılamaz."

    time_str = time_str.strip()
    now = datetime.now(TURKEY_TZ)

    # 1. Kısayol kontrolü (10dk, 2 saat, 30 saniye vb.)
    match = SHORTCUT_REGEX.match(time_str)
    if match:
        val = int(match.group(1))
        unit_raw = match.group(2).lower()
        param_name = UNIT_MULTIPLIERS.get(unit_raw)
        if param_name:
            delta_kwargs = {param_name: val}
            target_time = now + timedelta(**delta_kwargs)
            return target_time, None

    # 2. dateparser ile Türkçe doğal dil ayrıştırma
    # Ayarları: Türkiye saat dilimi, gün/ay/yıl sırası, geleceğe öncelik ver
    parsed = dateparser.parse(
        time_str,
        languages=["tr", "en"],
        settings={
            "DATE_ORDER": "DMY",
            "TIMEZONE": "Europe/Istanbul",
            "TO_TIMEZONE": "Europe/Istanbul",
            "RETURN_AS_TIMEZONE_AWARE": True,
            "PREFER_DATES_FROM": "future",
            "RELATIVE_BASE": now
        }
    )

    if not parsed:
        return None, (
            f"'{time_str}' zamanı anlaşılamadı.\n"
            "Örnek formatlar:\n"
            "• `5 Ekim 2026 17:00`\n"
            "• `10 dakika` veya `10dk`\n"
            "• `2 saat sonra`\n"
            "• `yarın 15:30`\n"
            "• `25.10.2026 09:00`"
        )

    # 3. Geçmiş zaman kontrolü
    if parsed <= now:
        return None, "Belirttiğiniz tarih/saat geçmişte kalmış! Lütfen ileri bir zaman belirtin."

    return parsed, None
