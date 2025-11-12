#!/usr/bin/env python

import os
import hmac
import hashlib
import base64
from datetime import datetime
from zoneinfo import ZoneInfo


class Serial:
    def __init__(
        self,
        secret_key: str | None = None,
        timezone: str = "Europe/Istanbul",
        group_count: int = 5,
        group_size: int = 5,
        hash_algo=hashlib.sha256
    ):
        self.secret_key = (secret_key or os.getenv("SECRET_KEY") or "change-me").encode("utf-8")
        self.timezone = ZoneInfo(timezone)
        self.group_count = group_count
        self.group_size = group_size
        self.hash_algo = hash_algo

    def _get_date_str(self, date: datetime | None = None) -> str:
        """YYYY-MM-DD döndürür, belirtilen saat dilimine göre."""
        now = date.astimezone(self.timezone) if date else datetime.now(self.timezone)
        return now.strftime("%Y-%m-%d")

    def _hmac_for_date(self, date_str: str) -> bytes:
        """Gizli anahtar + tarih ile HMAC üretir."""
        return hmac.new(self.secret_key, msg=date_str.encode(), digestmod=self.hash_algo).digest()

    def _encode_base32(self, data: bytes) -> str:
        """Base32 kodla, '=' paddingleri kaldır, büyük harf yap."""
        return base64.b32encode(data).decode("ascii").rstrip("=").upper()

    def _format_serial(self, code: str) -> str:
        """XXXXX-XXXXX-... formatına böler."""
        needed_len = self.group_count * self.group_size
        if len(code) < needed_len:
            code *= ((needed_len // len(code)) + 1)
        trimmed = code[:needed_len]
        groups = [trimmed[i:i+self.group_size] for i in range(0, needed_len, self.group_size)]
        return "-".join(groups)

    def generate(self, date: datetime | None = None) -> str:
        """Belirtilen gün için deterministik seri üret."""
        date_str = self._get_date_str(date)
        mac = self._hmac_for_date(date_str)
        b32 = self._encode_base32(mac)
        return self._format_serial(b32)

    def verify(self, serial: str, date: datetime | None = None) -> bool:
        """Verilen serial belirtilen (veya bugünkü) güne ait mi?"""
        expected = self.generate(date)
        s1 = serial.replace("-", "").upper()
        s2 = expected.replace("-", "").upper()
        return hmac.compare_digest(s1, s2)
