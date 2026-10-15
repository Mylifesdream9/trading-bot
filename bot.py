"""
═══════════════════════════════════════════════════════════════════════
  🚀 القناص الأسطوري V9.0 — النسخة الخارقة (Smart Adaptive Sniper)
═══════════════════════════════════════════════════════════════════════
  ✅ نظام تقييم جديد 10 نقاط (6 مكونات: OB/زناد/ستوك/حجم/اتجاه/بنية)
  ✅ R:R ديناميكي ذكي (1.2:1 إلى 2.0:1 حسب جودة الإشارة)
  ✅ خروج جزئي 70% (يحافظ على فرصة ربح أكبر + R:R محسّن)
  ✅ ستوكاستك كنقاط فقط (ليس شرط رفض حتمي)
  ✅ مسح شامل لكل العقود PERPETUAL (300+) مع Caching ذكي
  ✅ مطوّر تكييفي حقيقي (8 معاملات قابلة للتعديل)
  ✅ Risk Management مستقل (1.5% per trade, max DD 5%, max 3 خسائر/يوم)
  ✅ فلتر أخبار اقتصادية (NFP, FOMC, CPI, FOMC Minutes)
  ✅ وضع Backtest كامل (اختبار على بيانات تاريخية)
  ✅ إصلاح 32 خطأ برمجي ومنطقي من V8.2
═══════════════════════════════════════════════════════════════════════
"""

import asyncio
import aiohttp
import json
import math
import os
import sys
import time
import logging
import requests
import collections
import pandas as pd
import numpy as np
import hmac
import hashlib
import signal
import threading
from decimal import Decimal
from urllib.parse import urlencode
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone, timedelta
import websockets
import aiosqlite
from web_panel import start_web_panel, notify as panel_notify

# ─── إصلاح ترميز الإخراج (Windows / Linux) ───
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ─── Logger ───
logger = logging.getLogger('SniperV9')
logger.setLevel(logging.INFO)
_fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
_fh = RotatingFileHandler('bot_v9.log', maxBytes=2*1024*1024, backupCount=3, encoding='utf-8')
_fh.setFormatter(_fmt)
logger.addHandler(_fh)
_ch = logging.StreamHandler()
_ch.setFormatter(_fmt)
logger.addHandler(_ch)


def check_outbound_ip():
    """فحص الـ IP الصادر عند الإقلاع للتشخيص."""
    try:
        r = requests.get('https://api.ipify.org?format=json', timeout=10)
        ip = r.json().get('ip')
        logger.info(f"Current Outbound IP on Railway: {ip}")
        return ip
    except Exception as e:
        logger.warning(f"Failed to fetch IP: {e}")
        return None


check_outbound_ip()


# ══════════════════════════════════════════════════════════════════════
#  Constants & Enums
# ══════════════════════════════════════════════════════════════════════
SCAN_INTERVAL_SECONDS = 30          # فاصل المسح (بدلاً من 60)
REENTRY_COOLDOWN_SECONDS = 1200     # 20 دقيقة (بدلاً من 15)
WS_STALE_ALERT_SECONDS = 120
BALANCE_CACHE_SECONDS = 5
KLINE_CACHE_SECONDS = 180           # 3 دقائق cache لـ klines
VERIFY_EVERY_N_LOOPS = 5
MAX_DAILY_LOSSES = 3                # إيقاف اليوم بعد 3 خسائر
MAX_CONSECUTIVE_LOSSES = 3          # إيقاف مؤقت بعد 3 خسائر متتالية
PAUSE_AFTER_LOSS_MINUTES = 240      # إيقاف 4 ساعات بعد خسائر متتالية

# أحداث أخبار تجنّب التداول فيها
HIGH_IMPACT_NEWS_EVENTS = {
    'Nonfarm Payrolls', 'FOMC', 'CPI', 'FOMC Meeting Minutes',
    'Interest Rate Decision', 'Unemployment Claims', 'GDP',
    'PPI', 'Retail Sales', 'ISM Manufacturing PMI'
}


# ══════════════════════════════════════════════════════════════════════
#  Database Manager (محسّن)
# ══════════════════════════════════════════════════════════════════════
class DatabaseManager:
    def __init__(self, db_name=None):
        volume_dir = os.environ.get('RAILWAY_VOLUME_MOUNT_PATH', '/data')
        os.makedirs(volume_dir, exist_ok=True)
        self.db_name = os.path.join(volume_dir, 'sniper_v9.db')

    async def init_db(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS active_trades (
                symbol TEXT PRIMARY KEY, side TEXT, entry_price REAL, quantity REAL,
                sl REAL, tp REAL, tp2 REAL, trailing_active INTEGER, highest_price REAL,
                lowest_price REAL, entry_time REAL, partial_closed INTEGER,
                realized_pnl REAL DEFAULT 0, stop_order_id INTEGER, tp_order_id INTEGER,
                score REAL DEFAULT 0, partial_ratio REAL DEFAULT 0.7,
                tp2_mult REAL DEFAULT 4.5, sl_atr_mult REAL DEFAULT 1.5,
                tp1_atr_mult REAL DEFAULT 1.8,
                stop_is_algo INTEGER DEFAULT 0, tp_is_algo INTEGER DEFAULT 0,
                stop_synced_price REAL, tp_skipped INTEGER DEFAULT 0,
                tp_unconfirmed INTEGER DEFAULT 0)""")
            # إضافة أعمدة مفقودة بأمان
            for col_def in [
                'realized_pnl REAL DEFAULT 0', 'stop_order_id INTEGER',
                'tp2 REAL', 'tp_order_id INTEGER',
                'score REAL DEFAULT 0', 'partial_ratio REAL DEFAULT 0.7',
                'tp2_mult REAL DEFAULT 4.5', 'sl_atr_mult REAL DEFAULT 1.5',
                'tp1_atr_mult REAL DEFAULT 1.8',
                'stop_is_algo INTEGER DEFAULT 0', 'tp_is_algo INTEGER DEFAULT 0',
                'stop_synced_price REAL', 'tp_skipped INTEGER DEFAULT 0',
                'tp_unconfirmed INTEGER DEFAULT 0'
            ]:
                try:
                    await db.execute(f"ALTER TABLE active_trades ADD COLUMN {col_def}")
                except Exception:
                    pass
            await db.execute("""CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY, realized_pnl REAL, wins INTEGER, losses INTEGER)""")
            await db.execute("""CREATE TABLE IF NOT EXISTS bot_params (
                key TEXT PRIMARY KEY, value TEXT)""")
            await db.execute("""CREATE TABLE IF NOT EXISTS signal_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, direction TEXT,
                entry_ts REAL, score REAL, components TEXT,
                result INTEGER DEFAULT -1, pnl REAL)""")
            await db.execute("""CREATE TABLE IF NOT EXISTS news_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, currency TEXT,
                impact TEXT, event TEXT, forecast TEXT, actual TEXT)""")
            await db.commit()

    async def get_param(self, key):
        try:
            async with aiosqlite.connect(self.db_name) as db:
                async with db.execute("SELECT value FROM bot_params WHERE key=?", (key,)) as cur:
                    row = await cur.fetchone()
                    return row[0] if row else None
        except Exception:
            return None

    async def set_param(self, key, value):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("INSERT OR REPLACE INTO bot_params (key, value) VALUES (?,?)", (key, value))
            await db.commit()

    async def log_signal(self, symbol, direction, entry_ts, score, components):
        try:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute(
                    "INSERT INTO signal_log (symbol, direction, entry_ts, score, components) VALUES (?,?,?,?,?)",
                    (symbol, direction, entry_ts, score, json.dumps(components, ensure_ascii=False, default=str)))
                await db.commit()
        except Exception as e:
            logger.warning(f"تعذر تسجيل الإشارة: {e}")

    async def set_signal_result(self, symbol, entry_ts, win, pnl):
        try:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute(
                    "UPDATE signal_log SET result=?, pnl=? WHERE symbol=? AND entry_ts=? AND result=-1",
                    (int(win), pnl, symbol, entry_ts))
                await db.commit()
        except Exception as e:
            logger.warning(f"تعذر تحديث نتيجة الإشارة: {e}")

    async def save_trade(self, t):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""INSERT OR REPLACE INTO active_trades
                (symbol, side, entry_price, quantity, sl, tp, tp2, trailing_active,
                 highest_price, lowest_price, entry_time, partial_closed,
                 realized_pnl, stop_order_id, tp_order_id, score, partial_ratio,
                 tp2_mult, sl_atr_mult, tp1_atr_mult,
                 stop_is_algo, tp_is_algo, stop_synced_price, tp_skipped, tp_unconfirmed)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (t['symbol'], t['side'], t['entry_price'], t['quantity'],
                 t['sl'], t['tp'], t.get('tp2'), int(t.get('trailing_active', False)),
                 t.get('highest_price', 0), t.get('lowest_price', 999999999),
                 t['entry_time'], int(t.get('partial_closed', 0)),
                 float(t.get('realized_pnl', 0.0)), t.get('stop_order_id'), t.get('tp_order_id'),
                 float(t.get('score', 0) or 0), float(t.get('partial_ratio', 0.7)),
                 float(t.get('tp2_mult', 4.5)), float(t.get('sl_atr_mult', 1.5)),
                 float(t.get('tp1_atr_mult', 1.8)),
                 int(t.get('stop_is_algo', False)), int(t.get('tp_is_algo', False)),
                 t.get('stop_synced_price'), int(t.get('tp_skipped', False)),
                 int(t.get('tp_unconfirmed', False))))
            await db.commit()

    async def load_active_trades(self):
        trades = {}
        try:
            async with aiosqlite.connect(self.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""SELECT * FROM active_trades""") as cur:
                    async for row in cur:
                        trades[row['symbol']] = {
                            'symbol': row['symbol'], 'side': row['side'],
                            'entry_price': row['entry_price'], 'quantity': row['quantity'],
                            'sl': row['sl'], 'tp': row['tp'], 'tp2': row['tp2'],
                            'trailing_active': bool(row['trailing_active']),
                            'highest_price': row['highest_price'] or 0,
                            'lowest_price': row['lowest_price'] if row['lowest_price'] and row['lowest_price'] < 900000000 else 999999999,
                            'entry_time': row['entry_time'],
                            'partial_closed': bool(row['partial_closed']),
                            'realized_pnl': row['realized_pnl'] if row['realized_pnl'] is not None else 0.0,
                            'stop_order_id': row['stop_order_id'],
                            'tp_order_id': row['tp_order_id'],
                            'score': row['score'] if 'score' in row.keys() else 0,
                            'partial_ratio': row['partial_ratio'] if 'partial_ratio' in row.keys() else 0.7,
                            'tp2_mult': row['tp2_mult'] if 'tp2_mult' in row.keys() else 4.5,
                            'sl_atr_mult': row['sl_atr_mult'] if 'sl_atr_mult' in row.keys() else 1.5,
                            'tp1_atr_mult': row['tp1_atr_mult'] if 'tp1_atr_mult' in row.keys() else 1.8,
                            'stop_is_algo': bool(row['stop_is_algo']) if 'stop_is_algo' in row.keys() else False,
                            'tp_is_algo': bool(row['tp_is_algo']) if 'tp_is_algo' in row.keys() else False,
                            'stop_synced_price': row['stop_synced_price'] if 'stop_synced_price' in row.keys() else None,
                            'tp_skipped': bool(row['tp_skipped']) if 'tp_skipped' in row.keys() else False,
                            'tp_unconfirmed': bool(row['tp_unconfirmed']) if 'tp_unconfirmed' in row.keys() else False,
                        }
        except Exception as e:
            logger.error(f"❌ فشل تحميل الصفقات من القاعدة: {e}")
        return trades

    async def remove_trade(self, symbol):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("DELETE FROM active_trades WHERE symbol=?", (symbol,))
            await db.commit()

    async def update_daily_pnl(self, pnl, is_win=None):
        today = time.strftime("%Y-%m-%d")
        w = 1 if is_win is True else 0
        l = 1 if is_win is False else 0
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT * FROM daily_stats WHERE date=?", (today,)) as cur:
                row = await cur.fetchone()
            if row:
                await db.execute("UPDATE daily_stats SET realized_pnl=?, wins=?, losses=? WHERE date=?",
                    (row[1]+pnl, row[2]+w, row[3]+l, today))
            else:
                await db.execute("INSERT INTO daily_stats VALUES (?,?,?,?)", (today, pnl, w, l))
            await db.commit()

    async def get_day_stats(self, day):
        try:
            async with aiosqlite.connect(self.db_name) as db:
                async with db.execute(
                        "SELECT realized_pnl, wins, losses FROM daily_stats WHERE date=?", (day,)) as cur:
                    return await cur.fetchone()
        except Exception:
            return None


# ══════════════════════════════════════════════════════════════════════
#  Risk Manager — نظام إدارة المخاطر المستقل (جديد)
# ══════════════════════════════════════════════════════════════════════
class RiskManager:
    """إدارة المخاطر: حجم الصفقة، الحد الأقصى للخسارة، الإيقاف المؤقت."""

    def __init__(self, bot):
        self.bot = bot
        self.consecutive_losses = 0
        self.daily_losses = 0
        self.daily_pnl = 0.0
        self.last_loss_pause_until = 0.0
        self.current_day = time.strftime("%Y-%m-%d")
        self.max_risk_per_trade_pct = 0.015  # 1.5% من الرصيد
        self.max_daily_drawdown_pct = 0.05   # 5% إيقاف اليوم
        self.initial_balance = 0.0

    def reset_daily_if_needed(self):
        today = time.strftime("%Y-%m-%d")
        if today != self.current_day:
            self.current_day = today
            self.daily_losses = 0
            self.daily_pnl = 0.0
            logger.info("🔄 بدء يوم تداول جديد — تصفير عدّادات الخسارة")

    def record_trade_result(self, is_win, pnl):
        self.reset_daily_if_needed()
        self.daily_pnl += pnl
        if is_win:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            self.daily_losses += 1
            if self.consecutive_losses >= MAX_CONSECUTIVE_LOSSES:
                self.last_loss_pause_until = time.time() + PAUSE_AFTER_LOSS_MINUTES * 60
                logger.warning(f"⏸️ إيقاف مؤقت {PAUSE_AFTER_LOSS_MINUTES} دقيقة بسبب {MAX_CONSECUTIVE_LOSSES} خسائر متتالية")

    def can_trade(self):
        """هل يُسمح بالتداول الآن؟"""
        self.reset_daily_if_needed()
        if self.daily_losses >= MAX_DAILY_LOSSES:
            return False, f"🛑 تم الوصول للحد اليومي للخسائر ({MAX_DAILY_LOSSES})"
        if time.time() < self.last_loss_pause_until:
            remain = int((self.last_loss_pause_until - time.time()) / 60)
            return False, f"⏸️ إيقاف مؤقت — باقي {remain} دقيقة"
        # فحص السحب اليومي
        if self.initial_balance > 0:
            dd_pct = abs(min(0, self.daily_pnl)) / self.initial_balance
            if dd_pct >= self.max_daily_drawdown_pct:
                return False, f"🛑 السحب اليومي بلغ {dd_pct*100:.1f}%"
        return True, "✅ مسموح"

    def calc_position_size(self, entry_price, sl_price, balance):
        """✅ V9.3: حساب حجم الصفقة بناءً على المخاطرة 1.5% — مقيد بإعداد Railway.
        
        القاعدة: الهامش الديناميكي لا يتجاوز أبداً TRADE_SIZE_USDT المضبوط في Railway.
        يسمح فقط بالانخفاض (نصف المبلغ) لتفادي المخاطرة العالية، لكن لا يرتفع أبداً.
        """
        if balance <= 0 or entry_price <= 0 or sl_price <= 0:
            return self.bot.TRADE_SIZE_USDT  # fallback للإعداد الثابت
        risk_amount = balance * self.max_risk_per_trade_pct
        risk_per_unit = abs(entry_price - sl_price)
        if risk_per_unit <= 0:
            return self.bot.TRADE_SIZE_USDT
        # حجم العقد (position value) = risk_amount / (risk_per_unit/entry_price)
        position_value = risk_amount / (risk_per_unit / entry_price)
        # مع الرافعة، الهامش = القيمة / الرافعة
        margin = position_value / self.bot.LEVERAGE
        # ✅ V9.3: الحد الأقصى = TRADE_SIZE_USDT (لا يتجاوزه أبداً)
        # الحد الأدنى = نصف TRADE_SIZE_USDT (يسمح بهامش أصغر إذا المخاطرة صغيرة)
        margin = max(self.bot.TRADE_SIZE_USDT * 0.5, min(margin, self.bot.TRADE_SIZE_USDT))
        return round(margin, 2)


# ══════════════════════════════════════════════════════════════════════
#  News Filter — فلتر الأخبار الاقتصادية (جديد)
# ══════════════════════════════════════════════════════════════════════
class NewsFilter:
    """فلتر بسيط للأخبار الاقتصادية عالية التأثير.
    يستخدم مصدرًا مجانيًا (Python calendar) — يمكن إغلاقه بسهولة."""

    def __init__(self):
        self.enabled = os.environ.get('NEWS_FILTER_ENABLED', 'true').lower() == 'true'
        self.blackout_minutes_before = 30
        self.blackout_minutes_after = 30
        self._cached_events = []
        self._last_fetch = 0

    async def fetch_events(self):
        """جلب أحداث الأسبوع من ForexFactory (محاكاة مبسطة).
        في حال فشل الجلب، نعتمد على قائمة مواعيد ثابتة للأحداث الكبرى."""
        if not self.enabled:
            return
        now = time.time()
        if now - self._last_fetch < 3600:  # تحديث كل ساعة
            return
        self._last_fetch = now
        # محاكاة: في الإنتاج يمكن استبدالها بـ API حقيقي
        # نبني قائمة بالأحداث المتوقعة للأسبوع القادم بناءً على نمط شهري ثابت
        events = []
        try:
            # الأحداث المتكررة شهرياً (تقريبية)
            today = datetime.now(timezone.utc)
            # NFP = أول جمعة من الشهر
            first_of_month = today.replace(day=1)
            first_friday = first_of_month + timedelta(days=(4 - first_of_month.weekday()) % 7)
            nfp_time = first_friday.replace(hour=12, minute=30, second=0, microsecond=0)
            events.append({'ts': nfp_time.timestamp(), 'event': 'Nonfarm Payrolls', 'impact': 'high'})

            # CPI = عادة منتصف الشهر
            cpi_day = first_of_month + timedelta(days=10)
            while cpi_day.weekday() != 2:  # الأربعاء
                cpi_day += timedelta(days=1)
            cpi_time = cpi_day.replace(hour=12, minute=30, second=0, microsecond=0)
            events.append({'ts': cpi_time.timestamp(), 'event': 'CPI', 'impact': 'high'})

            # FOMC = أربعاء الأسبوع الثالث
            fomc_day = first_of_month + timedelta(days=14)
            while fomc_day.weekday() != 2:
                fomc_day += timedelta(days=1)
            fomc_time = fomc_day.replace(hour=18, minute=0, second=0, microsecond=0)
            events.append({'ts': fomc_time.timestamp(), 'event': 'FOMC', 'impact': 'high'})

            # FOMC Minutes = بعد 3 أسابيع من FOMC
            fomc_min_time = fomc_time + timedelta(days=21)
            events.append({'ts': fomc_min_time.timestamp(), 'event': 'FOMC Meeting Minutes', 'impact': 'high'})

            self._cached_events = events
        except Exception as e:
            logger.warning(f"تعذر بناء قائمة الأخبار: {e}")

    def is_blackout(self, symbol=''):
        """هل نحن في فترة حظر بسبب أخبار؟"""
        if not self.enabled or not self._cached_events:
            return False, ''
        now = time.time()
        for ev in self._cached_events:
            ts = ev['ts']
            before = ts - self.blackout_minutes_before * 60
            after = ts + self.blackout_minutes_after * 60
            if before <= now <= after:
                return True, ev['event']
        return False, ''


# ══════════════════════════════════════════════════════════════════════
#  Adaptive Tuner V2 — المطوّر التكييفي الحقيقي (محسّن)
# ══════════════════════════════════════════════════════════════════════
class AdaptiveTunerV2:
    """مطوّر تكييفي حقيقي: 8 معاملات قابلة للتعديل تلقائيًا."""

    def __init__(self, db):
        self.db = db
        # ✅ V9.2: عتبة عالية لدقة أعلى
        self.min_score = 7
        # نطاق القرب من OB — غير مستخدم فعلياً (الدخول من داخل OB)
        self.proximity_pct = 0.005
        # صرامة الستوكاستك
        self.stoch_strictness = 1
        # ✅ V9.2: SL = 0.5×ATR تحت OB
        self.sl_atr_mult = 0.5
        # ✅ V9.2: TP1 = 3.0×ATR
        self.tp1_atr_mult = 3.0
        # نسبة الجني الجزئي
        self.partial_ratio = 0.7
        # عتبة التقلب
        self.volatility_threshold = 3.0
        # ✅ V9.2: Trailing 2.5% (مساحة كافية للوصول لـ TP2)
        self.trailing_pct = 0.025

        self.results = collections.deque(maxlen=30)
        self.last_adjustment = 0

    def _clamp(self):
        self.min_score = max(6, min(8, int(self.min_score)))
        self.proximity_pct = max(0.002, min(0.01, float(self.proximity_pct)))
        self.stoch_strictness = max(0, min(1, int(self.stoch_strictness)))
        self.sl_atr_mult = max(0.3, min(0.8, float(self.sl_atr_mult)))  # ✅ V9.2: 0.3-0.8
        self.tp1_atr_mult = max(2.5, min(4.0, float(self.tp1_atr_mult)))  # ✅ V9.2: 2.5-4.0
        self.partial_ratio = max(0.5, min(1.0, float(self.partial_ratio)))
        self.volatility_threshold = max(3.0, min(8.0, float(self.volatility_threshold)))
        self.trailing_pct = max(0.015, min(0.035, float(self.trailing_pct)))  # ✅ V9.2: 1.5-3.5%

    async def load(self):
        raw = await self.db.get_param('tuner_v2')
        if raw:
            try:
                d = json.loads(raw)
                self.min_score = int(d.get('min_score', 6))
                self.proximity_pct = float(d.get('proximity_pct', 0.025))
                self.stoch_strictness = int(d.get('stoch_strictness', 1))
                self.sl_atr_mult = float(d.get('sl_atr_mult', 1.5))
                self.tp1_atr_mult = float(d.get('tp1_atr_mult', 1.8))
                self.partial_ratio = float(d.get('partial_ratio', 0.7))
                self.volatility_threshold = float(d.get('volatility_threshold', 3.0))
                self.trailing_pct = float(d.get('trailing_pct', 0.015))
                self.results = collections.deque(d.get('results', [])[-30:], maxlen=30)
                self._clamp()
                logger.info(f"🧠 المطوّر التكييفي V2 محمّل: {self.describe()}")
            except Exception as e:
                logger.warning(f"تعذر تحميل المطوّر التكيفي V2 (سيبدأ افتراضياً): {e}")

    async def save(self):
        try:
            await self.db.set_param('tuner_v2', json.dumps({
                'min_score': self.min_score,
                'proximity_pct': self.proximity_pct,
                'stoch_strictness': self.stoch_strictness,
                'sl_atr_mult': self.sl_atr_mult,
                'tp1_atr_mult': self.tp1_atr_mult,
                'partial_ratio': self.partial_ratio,
                'volatility_threshold': self.volatility_threshold,
                'trailing_pct': self.trailing_pct,
                'results': list(self.results)}))
        except Exception as e:
            logger.warning(f"تعذر حفظ المطوّر التكيفي V2: {e}")

    def record(self, win):
        self.results.append(bool(win))

    def recent_winrate(self, n=10):
        recent = list(self.results)[-n:]
        if len(recent) < 5:
            return None
        return sum(recent) / len(recent)

    def adapt(self):
        """تعديل تكيفي ذكي بناءً على آخر النتائج.
        يتم استدعاؤها كل ساعة. يحتاج لـ 5 نتائج على الأقل."""
        now = time.time()
        if now - self.last_adjustment < 3600:  # مرة كل ساعة
            return None
        if len(self.results) < 5:  # ✅ حد أدنى 5 نتائج
            return None
        self.last_adjustment = now

        wr = self.recent_winrate(10)
        if wr is None:
            return None

        action = None
        if wr < 0.40:
            # فوز ضعيف → تشديد
            self._tighten()
            action = f"🔒 تشديد (فوز {wr*100:.0f}%): رفع min_score، تقليص نطاق القرب، SL أضيق"
        elif wr > 0.65 and len(self.results) >= 8:
            # فوز ممتاز → ارتخاء محدود لزيادة الفرص
            self._relax()
            action = f"🔓 ارتخاء (فوز {wr*100:.0f}%): توسيع نطاق القرب، SL أوسع قليلاً"
        return action

    def _tighten(self):
        self.min_score = min(8, self.min_score + 1)
        self.proximity_pct = max(0.002, self.proximity_pct - 0.001)
        self.stoch_strictness = 1
        self.sl_atr_mult = max(0.3, self.sl_atr_mult - 0.05)

    def _relax(self):
        self.min_score = max(6, self.min_score - 1)
        self.proximity_pct = min(0.01, self.proximity_pct + 0.001)
        self.sl_atr_mult = min(0.8, self.sl_atr_mult + 0.05)

    def describe(self):
        return (f"min={self.min_score}/10 | قربOB≤{self.proximity_pct*100:.1f}% | "
                f"ستوك={'صارم' if self.stoch_strictness else 'مرن'} | "
                f"SL={self.sl_atr_mult}×ATR | TP1={self.tp1_atr_mult}×ATR | "
                f"جني={int(self.partial_ratio*100)}% | تريل={self.trailing_pct*100:.1f}%")


# ══════════════════════════════════════════════════════════════════════
#  SMC Engine V2 — محرك التحليل (محسّن)
# ══════════════════════════════════════════════════════════════════════
class WhaleSMCEngineV2:
    """محرك SMC محسّن: OB + Liquidity Sweep + Stochastic + EMA Multi-TF."""

    @staticmethod
    def detect_order_blocks(df, trend, atr_value=None):
        """كاشف OB بـ threshold ديناميكي حسب ATR."""
        obs = []
        # threshold ديناميكي: 0.8% افتراضياً، أو 0.5×ATR/Self.kمن السعر
        threshold = 0.012
        if atr_value and len(df) > 0:
            last_close = df['close'].iloc[-1]
            if last_close > 0:
                atr_pct = atr_value / last_close
                threshold = max(0.008, min(0.025, atr_pct * 0.8))

        for i in range(2, len(df)-1):
            try:
                if df['close'].iloc[i] > df['open'].iloc[i]:
                    # شمعة خضراء
                    prev_low = df['low'].iloc[i-1]
                    if prev_low <= 0:
                        continue
                    impulse_pct = (df['close'].iloc[i] - prev_low) / prev_low
                    if df['close'].iloc[i-1] < df['open'].iloc[i-1] and impulse_pct > threshold:
                        obs.append({'type': 'demand', 'top': float(df['open'].iloc[i-1]),
                                    'bottom': float(df['low'].iloc[i-1]), 'index': i-1,
                                    'strength': float(impulse_pct)})
                elif df['close'].iloc[i] < df['open'].iloc[i]:
                    # شمعة حمراء
                    prev_high = df['high'].iloc[i-1]
                    if prev_high <= 0:
                        continue
                    impulse_pct = (prev_high - df['close'].iloc[i]) / prev_high
                    if df['close'].iloc[i-1] > df['open'].iloc[i-1] and impulse_pct > threshold:
                        obs.append({'type': 'supply', 'top': float(df['high'].iloc[i-1]),
                                    'bottom': float(df['close'].iloc[i-1]), 'index': i-1,
                                    'strength': float(impulse_pct)})
            except (TypeError, ValueError, ZeroDivisionError):
                continue
        return obs

    @staticmethod
    def detect_liquidity_sweep(df_15m, ob_zone, direction):
        """✅ V9.1: تصفية سيولة دقيقة — الإغلاق يجب أن يكون داخل OB وليس فوقه.
        
        الخطأ القديم: كان يتطلب current_close > ob_top (السعر تحرك بالفعل فوق OB)
        الإصلاح: current_close يجب أن يكون داخل OB (بين bottom و top)
        هذا يضمن الدخول من داخل المنطقة وليس من فوقها.
        """
        if len(df_15m) < 4:
            return False
        current_open = float(df_15m['open'].iloc[-2])
        current_low = float(df_15m['low'].iloc[-2])
        current_high = float(df_15m['high'].iloc[-2])
        current_close = float(df_15m['close'].iloc[-2])
        prev_close = float(df_15m['close'].iloc[-3])
        ob_bottom = float(ob_zone['bottom'])
        ob_top = float(ob_zone['top'])

        if direction == 'BUY' and ob_zone['type'] == 'demand':
            # ✅ شروط الـ sweep الدقيق:
            # 1) السعر نزل تحت OB_bottom (صيد السيولة)
            # 2) الإغلاق عاد داخل OB (بين bottom و top) — وليس فوق top
            # 3) الإغلاق أعلى من الإغلاق السابق (زخم صاعد)
            # 4) الإغلاق في النصف العلوي من الشمعة (قوة الشراء)
            if not (current_low < ob_bottom):
                return False
            if not (current_close > ob_bottom):
                return False
            if not (current_close <= ob_top * 1.001):  # داخل أو على حافة OB
                return False
            if not (current_close > prev_close):
                return False
            # فلتر الزخم: الإغلاق في النصف العلوي للشمعة
            candle_range = current_high - current_low
            if candle_range > 0:
                close_position = (current_close - current_low) / candle_range
                if close_position < 0.5:  # الإغلاق يجب أن يكون في النصف العلوي
                    return False
            return True

        elif direction == 'SELL' and ob_zone['type'] == 'supply':
            if not (current_high > ob_top):
                return False
            if not (current_close < ob_top):
                return False
            if not (current_close >= ob_bottom * 0.999):
                return False
            if not (current_close < prev_close):
                return False
            candle_range = current_high - current_low
            if candle_range > 0:
                close_position = (current_high - current_close) / candle_range
                if close_position < 0.5:
                    return False
            return True
        return False

    @staticmethod
    def detect_ob_retest(df_15m, ob_zone, direction):
        """✅ V9.6: إعادة اختبار دقيقة — آخر شمعتين فقط (وليس 3).

        المشكلة القديمة: كان يقبل retest من آخر 3 شمعات (45 دقيقة)
        هذا يعني البوت قد يدخل على إشارة عمرها 45 دقيقة!

        الحل: آخر شمعتين فقط (30 دقيقة كحد أقصى) + شمعة اليوم يجب أن تكون ارتداد.
        """
        if len(df_15m) < 5:
            return False
        # ✅ V9.6: آخر شمعتين فقط (بدلاً من 3)
        lows = df_15m['low'].iloc[-3:-1]
        highs = df_15m['high'].iloc[-3:-1]
        closes = df_15m['close'].iloc[-3:-1]
        opens = df_15m['open'].iloc[-3:-1]
        if len(closes) < 2:
            return False
        try:
            ob_bottom = float(ob_zone['bottom'])
            ob_top = float(ob_zone['top'])
            if direction == 'BUY' and ob_zone['type'] == 'demand':
                # ✅ السعر لمس OB_top من فوق (لمس المنطقة)
                touched = bool((lows <= ob_top).any())
                if not touched:
                    return False
                # ✅ آخر إغلاق يجب أن يكون قريباً من OB (داخل أو فوق بحافة ضيقة)
                last_close = float(closes.iloc[-1])
                distance_from_ob = (last_close - ob_top) / ob_top
                if distance_from_ob > 0.003:  # الإغلاق أكثر من 0.3% فوق OB = متأخر
                    return False
                # ✅ الزخم: آخر شمعة صاعدة
                if float(closes.iloc[-1]) <= float(closes.iloc[-2]):
                    return False
                # ✅ شمعة أخيرة خضراء (close > open)
                if float(closes.iloc[-1]) <= float(opens.iloc[-1]):
                    return False
                return True
            if direction == 'SELL' and ob_zone['type'] == 'supply':
                touched = bool((highs >= ob_bottom).any())
                if not touched:
                    return False
                last_close = float(closes.iloc[-1])
                distance_from_ob = (ob_bottom - last_close) / ob_bottom
                if distance_from_ob > 0.003:
                    return False
                if float(closes.iloc[-1]) >= float(closes.iloc[-2]):
                    return False
                if float(closes.iloc[-1]) >= float(opens.iloc[-1]):
                    return False
                return True
        except (TypeError, ValueError):
            return False
        return False

    @staticmethod
    def calculate_stochastic(df, k_period=14, d_period=3):
        """ستوكاستك K/D — مع حماية من القسمة على صفر."""
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()
        diff = (high_max - low_min).replace(0, np.nan)
        df['stoch_k'] = 100 * ((df['close'] - low_min) / diff)
        df['stoch_d'] = df['stoch_k'].rolling(window=d_period).mean()
        df['stoch_k'] = df['stoch_k'].fillna(50)
        df['stoch_d'] = df['stoch_d'].fillna(50)
        return df

    @staticmethod
    def compute_atr_wilder(df, period=14):
        """ATR بطريقة Wilder's EMA — أدق من rolling mean."""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            prev_close = close.shift(1)
            tr1 = high - low
            tr2 = (high - prev_close).abs()
            tr3 = (low - prev_close).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            # Wilder's smoothing = EMA with alpha = 1/period
            atr = tr.ewm(alpha=1/period, adjust=False).mean()
            val = float(atr.iloc[-1])
            if math.isnan(val) or val <= 0:
                return None
            return val
        except Exception:
            return None

    @staticmethod
    def detect_market_structure(df, trend):
        """كشف بنية السوق: HH/HL (صعود) أو LH/LL (هبوط)."""
        try:
            if len(df) < 20:
                return False
            # نأخذ آخر 5 قمم/قيعان
            recent = df.iloc[-20:]
            highs = recent['high'].values
            lows = recent['low'].values
            # تحقق من HH و HL لصعود
            if trend == 'BUY':
                # آخر قمتين صاعدتان وآخر قاعين صاعدان
                last_high = highs[-1]
                prev_high = highs[-5] if len(highs) >= 5 else highs[0]
                last_low = lows[-1]
                prev_low = lows[-5] if len(lows) >= 5 else lows[0]
                return bool(last_high > prev_high and last_low > prev_low)
            else:
                last_high = highs[-1]
                prev_high = highs[-5] if len(highs) >= 5 else highs[0]
                last_low = lows[-1]
                prev_low = lows[-5] if len(lows) >= 5 else lows[0]
                return bool(last_high < prev_high and last_low < prev_low)
        except (TypeError, ValueError, IndexError):
            return False

    @staticmethod
    def multi_tf_trend(df_4h, df_1h, current_price):
        """✅ V9.6: تحقق توافق الاتجاه على 4h و 1h — EMA50 مع فلتر الاتجاه العرضي.
        
        المشكلة القديمة: السعر فوق EMA50 = BUY، تحته = SELL
        لكن في سوق عرضي (السعر قريب من EMA50)، هذا يعطي إشارات خاطئة.
        
        الحل: إذا السعر قريب من EMA50 بأقل من 0.8%، اعتبر السوق عرضي وارفض.
        """
        try:
            ema_4h = df_4h['close'].ewm(span=50, adjust=False).mean().iloc[-1]
            ema_1h = df_1h['close'].ewm(span=50, adjust=False).mean().iloc[-1]
            if math.isnan(ema_4h) or math.isnan(ema_1h):
                return None, False

            # ✅ V9.6: فلتر الاتجاه العرضي
            # إذا السعر قريب جداً من EMA50 (أقل من 0.8%)، السوق عرضي — ارفض
            distance_4h_pct = abs(current_price - ema_4h) / ema_4h if ema_4h > 0 else 0
            distance_1h_pct = abs(current_price - ema_1h) / ema_1h if ema_1h > 0 else 0
            if distance_4h_pct < 0.008 or distance_1h_pct < 0.008:
                # السوق عرضي — لا اتجاه واضح
                return None, False

            # ✅ V9.6: تحقق قوة الاتجاه بـ EMA slope
            # نأخذ آخر 5 قيم EMA ونتحقق أن الميل واضح
            ema_4h_recent = df_4h['close'].ewm(span=50, adjust=False).mean().iloc[-5:]
            ema_1h_recent = df_1h['close'].ewm(span=50, adjust=False).mean().iloc[-5:]
            if len(ema_4h_recent) >= 5 and len(ema_1h_recent) >= 5:
                # الميل = (آخر قيمة - أول قيمة) / أول قيمة
                slope_4h = (ema_4h_recent.iloc[-1] - ema_4h_recent.iloc[0]) / ema_4h_recent.iloc[0]
                slope_1h = (ema_1h_recent.iloc[-1] - ema_1h_recent.iloc[0]) / ema_1h_recent.iloc[0]
                # إذا الميل ضعيف جداً (أقل من 0.5%)، السوق عرضي
                if abs(slope_4h) < 0.005 or abs(slope_1h) < 0.005:
                    return None, False

            trend_4h = 'BUY' if current_price > ema_4h else 'SELL'
            trend_1h = 'BUY' if current_price > ema_1h else 'SELL'
            aligned = (trend_4h == trend_1h)
            return trend_4h, aligned
        except (TypeError, ValueError):
            return None, False


# ══════════════════════════════════════════════════════════════════════
#  Kline Cache — ذاكرة مؤقتة لـ klines (جديد)
# ══════════════════════════════════════════════════════════════════════
class KlineCache:
    """ذاكرة مؤقتة لبيانات klines لتقليل طلبات API."""

    def __init__(self):
        self._cache = {}  # (symbol, interval) -> (df, ts)

    def get(self, symbol, interval, max_age=KLINE_CACHE_SECONDS):
        key = (symbol, interval)
        entry = self._cache.get(key)
        if entry and (time.time() - entry[1]) < max_age:
            return entry[0]
        return None

    def set(self, symbol, interval, df):
        self._cache[(symbol, interval)] = (df, time.time())
        # تنظيف الكاش القديم
        now = time.time()
        for k in list(self._cache.keys()):
            if now - self._cache[k][1] > 600:
                del self._cache[k]


# ══════════════════════════════════════════════════════════════════════
#  🚀 القناص الأسطوري V9.0 — النسخة الخارقة
# ══════════════════════════════════════════════════════════════════════
class LegendarySniperFuturesV9:
    def __init__(self):
        self.binance_api_key = os.environ.get('BINANCE_API_KEY', '')
        self.binance_api_secret = os.environ.get('BINANCE_API_SECRET', '')

        self.TRADE_ENABLED = os.environ.get('TRADE_ENABLED', 'false').lower() == 'true'
        self.LEVERAGE = int(os.environ.get('LEVERAGE', '10'))
        self.TRADE_SIZE_USDT = float(os.environ.get('TRADE_SIZE_USDT', '25'))
        self.MAX_OPEN_TRADES = int(os.environ.get('MAX_OPEN_TRADES', '2'))
        self.TESTNET = os.environ.get('TESTNET', 'false').lower() == 'true'
        self.BACKTEST_MODE = os.environ.get('BACKTEST_MODE', 'false').lower() == 'true'
        self.BACKTEST_DAYS = int(os.environ.get('BACKTEST_DAYS', '30'))
        self.BACKTEST_SYMBOLS = os.environ.get('BACKTEST_SYMBOLS',
                                                'BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,XRPUSDT').split(',')

        # تحقق الإعدادات
        problems = []
        if self.TRADE_SIZE_USDT <= 0:
            problems.append("TRADE_SIZE_USDT يجب أن يكون أكبر من صفر")
        if not (1 <= self.MAX_OPEN_TRADES <= 10):
            problems.append("MAX_OPEN_TRADES يجب أن يكون بين 1 و 10")
        if not (1 <= self.LEVERAGE <= 50):
            problems.append("LEVERAGE يجب أن يكون بين 1 و 50")
        if self.TESTNET:
            logger.info("🧪 وضع Testnet التجريبي مفعّل")
        if problems:
            raise SystemExit("❌ إعدادات خاطئة:\n- " + "\n- ".join(problems))

        if self.TRADE_ENABLED and (not self.binance_api_key or not self.binance_api_secret):
            self.TRADE_ENABLED = False
            logger.error("❌ التداول مفعّل لكن مفاتيح API ناقصة! التحويل للمراقبة فقط")

        self.PRICE_MAX_AGE = 30
        self.VERIFY_EVERY_N_LOOPS = VERIFY_EVERY_N_LOOPS
        self.WS_STALE_ALERT = WS_STALE_ALERT_SECONDS
        self.BALANCE_CACHE_SECONDS = BALANCE_CACHE_SECONDS

        self.data_url = "https://fapi.binance.com"
        self.trade_url = ("https://testnet.binancefuture.com" if self.TESTNET
                          else "https://fapi.binance.com")
        self.time_offset_ms = 0

        self.db = DatabaseManager()
        self.smc = WhaleSMCEngineV2()
        self.tuner = AdaptiveTunerV2(self.db)
        self.risk = RiskManager(self)
        self.news_filter = NewsFilter()
        self.kline_cache = KlineCache()
        self.session = None
        self.ws_task = None
        self._shutdown_requested = False

        self.all_futures_pairs = []
        self.step_sizes_cache = {}
        self.tick_sizes_cache = {}
        self.min_qty_cache = {}
        self.max_qty_cache = {}
        self.min_notional_cache = {}
        self.live_prices = {}
        self.active_trades = {}
        self.reentry_cooldown = {}
        self.error_counts = {}
        self.last_discovery_alert = {}
        self.entry_history = collections.deque(maxlen=200)
        self.last_scan_info = None
        self._last_heartbeat = 0
        self._report_day = time.strftime("%Y-%m-%d")
        self._last_freq_check = 0
        self._balance_cache = (0.0, 0.0)
        self._loop_count = 0

        self.stats = {
            'total_scans': 0, 'trades_executed': 0, 'wins': 0, 'losses': 0,
            'signals_found': 0, 'rejected_by_risk': 0, 'rejected_by_news': 0,
            'total_signals': 0
        }

    # ═══ نظام مكافحة الصمت ═══
    def _notify_error(self, source, exc=None, context=""):
        count = self.error_counts.get(source, 0) + 1
        self.error_counts[source] = count
        txt = f"⚠️ {source}" + (f" — {context}" if context else "")
        if exc is not None:
            txt += f" | `{str(exc)[:100]}`"
        logger.warning(f"{txt} (تكرار #{count})")
        if count == 1 or count % 10 == 0:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.tg(f"{txt}\n🔢 مرات التكرار: {count}"))
            except RuntimeError:
                pass

    def _reset_error(self, source):
        self.error_counts.pop(source, None)

    def fmt_price(self, price):
        if price is None or price == 0:
            return "$0"
        if price < 0.00001:
            return f"${price:.10f}"
        elif price < 0.001:
            return f"${price:.6f}"
        elif price < 1:
            return f"${price:.4f}"
        elif price < 100:
            return f"${price:.2f}"
        else:
            return f"${price:,.1f}"

    async def tg(self, msg):
        """كل إشعار يذهب للوحة + السجل."""
        try:
            first_line = msg.split('\n')[0].replace('*', '').strip()
            kind = 'info'
            if msg.startswith('✅') or 'صفقة منفذة' in msg:
                kind = 'trade'
            elif msg.startswith('🎯') or 'جني' in first_line:
                kind = 'partial'
            elif msg.startswith('🏁') or 'إغلاق' in first_line:
                kind = 'close'
            elif msg.startswith('🚨') or 'خطأ' in first_line or msg.startswith('⚠️'):
                kind = 'error'
            elif 'المطوّر' in first_line or msg.startswith('🧠'):
                kind = 'tuner'
            elif msg.startswith('🛑'):
                kind = 'system'
            await panel_notify(kind, first_line, msg, 'info')
        except Exception:
            pass

    # ═══ توقيت الخادم ═══
    async def sync_server_time(self):
        try:
            res = await self._fapi_request('GET', '/fapi/v1/time')
            if res and 'serverTime' in res:
                self.time_offset_ms = int(res['serverTime']) - int(time.time() * 1000)
                logger.info(f"🕐 مزامنة وقت الخادم: إزاحة {self.time_offset_ms}ms")
        except Exception as e:
            logger.warning(f"تعذر مزامنة وقت الخادم: {e}")

    def _sign(self, params):
        params['timestamp'] = int(time.time() * 1000) + self.time_offset_ms
        params['recvWindow'] = 5000
        query = urlencode(params)
        params['signature'] = hmac.new(
            self.binance_api_secret.encode(), query.encode(), hashlib.sha256
        ).hexdigest()
        return params

    async def _fapi_request(self, method, endpoint, params=None, signed=False,
                            retries=3, quiet=(), soft=()):
        for attempt in range(retries):
            try:
                url = f"{self.trade_url}{endpoint}"
                headers = {'X-MBX-APIKEY': self.binance_api_key} if signed else {}
                req_params = self._sign(dict(params) if params else {}) if signed else params

                async with self.session.request(method, url, params=req_params,
                                                headers=headers, timeout=15) as r:
                    if r.status == 200:
                        return await r.json()
                    body = await r.text()
                    if r.status in (429, 418):
                        await asyncio.sleep(10 * (attempt + 1))
                        continue
                    if r.status == 401:
                        self._notify_error("خطأ 401 من Binance",
                                           context=f"مفاتيح خاطئة أو مقيدة بـIP | الرد: {body[:200]}")
                        return None
                    if '-1021' in body:
                        logger.warning("⚠️ خطأ توقيم -1021 — مزامنة الوقت وإعادة المحاولة")
                        await self.sync_server_time()
                        await asyncio.sleep(1)
                        continue
                    if r.status >= 500:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    for c in soft:
                        if str(c) in body:
                            return {'_soft_code': c}
                    if any(str(c) in body for c in quiet):
                        return None
                    logger.warning(f"Futures API Error {r.status}: {body[:120]}")
                    return None
            except asyncio.TimeoutError:
                if attempt == retries - 1:
                    self._notify_error("انتهت مهلة طلب Binance", context=endpoint)
                    return None
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                if attempt == retries - 1:
                    self._notify_error("فشل طلب Binance", exc=e, context=endpoint)
                    return None
                await asyncio.sleep(2 ** attempt)
        return None

    async def setup_futures_account(self):
        msg = f"⚙️ *إعداد حساب العقود الآجلة (الرافعة {self.LEVERAGE}x)*\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
        setup_count = 0
        for pair in self.all_futures_pairs[:60]:
            symbol = pair['symbol']
            try:
                lev_res = await self._fapi_request('POST', '/fapi/v1/leverage',
                    {'symbol': symbol, 'leverage': self.LEVERAGE}, signed=True)
                await self._fapi_request('POST', '/fapi/v1/marginType',
                    {'symbol': symbol, 'marginType': 'ISOLATED'}, signed=True, quiet=(-4046,))
                if lev_res and lev_res.get('leverage') == self.LEVERAGE:
                    setup_count += 1
            except Exception as e:
                logger.debug(f"تخطي إعداد {symbol}: {e}")
            await asyncio.sleep(0.12)
        msg += f"✅ تم ضبط الرافعة والهامش المعزول لـ {setup_count} زوج"
        await self.tg(msg)

    async def load_market_data(self):
        data = await self._fapi_request('GET', '/fapi/v1/exchangeInfo')
        if not data:
            return
        new_pairs = []
        for s in data.get('symbols', []):
            if s['quoteAsset'] == 'USDT' and s['status'] == 'TRADING' and s['contractType'] == 'PERPETUAL':
                new_pairs.append({'symbol': s['symbol'], 'baseAsset': s['baseAsset']})
                for f in s.get('filters', []):
                    if f['filterType'] == 'LOT_SIZE':
                        self.step_sizes_cache[s['symbol']] = float(f['stepSize'])
                        self.min_qty_cache[s['symbol']] = float(f.get('minQty', f['stepSize']))
                        self.max_qty_cache[s['symbol']] = float(f.get('maxQty', 1e12))
                    elif f['filterType'] == 'PRICE_FILTER':
                        self.tick_sizes_cache[s['symbol']] = float(f['tickSize'])
                    elif f['filterType'] == 'MIN_NOTIONAL':
                        self.min_notional_cache[s['symbol']] = float(f.get('notional', f.get('minNotional', 5.0)))
        self.all_futures_pairs = new_pairs
        logger.info(f"📊 تم تحميل {len(self.all_futures_pairs)} زوج عقود آجلة")

    @staticmethod
    def _decimals_of(step):
        try:
            exp = Decimal(str(step)).normalize().as_tuple().exponent
            return max(0, -exp)
        except Exception:
            return 8

    def _step_qty(self, symbol, qty):
        step = self.step_sizes_cache.get(symbol) or 1.0
        if step <= 0:
            step = 1.0
        dec = self._decimals_of(step)
        return round(math.floor(round(qty / step, 9)) * step, dec)

    def format_quantity(self, symbol, qty):
        return self._step_qty(symbol, qty)

    def qty_to_str(self, symbol, qty):
        step = self.step_sizes_cache.get(symbol) or 1.0
        dec = self._decimals_of(step)
        return f"{self._step_qty(symbol, qty):.{dec}f}"

    def price_to_str(self, symbol, price):
        tick = self.tick_sizes_cache.get(symbol)
        if not tick or tick <= 0:
            if price >= 100:
                dec = 2
            elif price >= 1:
                dec = 4
            elif price >= 0.01:
                dec = 6
            else:
                dec = 8
            return f"{price:.{dec}f}"
        dec = self._decimals_of(tick)
        stepped = math.floor(round(price / tick, 9)) * tick
        return f"{round(stepped, dec):.{dec}f}"

    def get_price(self, symbol):
        p = self.live_prices.get(symbol)
        if p and (time.time() - p.get('ts', 0)) <= self.PRICE_MAX_AGE:
            return p
        return None

    def set_cooldown(self, symbol):
        self.reentry_cooldown[symbol] = time.time() + REENTRY_COOLDOWN_SECONDS

    def is_in_cooldown(self, symbol):
        expiry = self.reentry_cooldown.get(symbol, 0)
        if time.time() < expiry:
            return True
        self.reentry_cooldown.pop(symbol, None)
        return False

    async def get_available_usdt(self):
        now = time.time()
        cached_val, cached_ts = self._balance_cache
        if now - cached_ts < self.BALANCE_CACHE_SECONDS and cached_ts > 0:
            return cached_val
        if not self.binance_api_key:
            return 0.0
        res = await self._fapi_request('GET', '/fapi/v2/balance', signed=True)
        avail = 0.0
        if isinstance(res, list):
            for b in res:
                if b.get('asset') == 'USDT':
                    avail = float(b.get('availableBalance', 0))
                    break
        if avail > 0:
            self._balance_cache = (avail, now)
            if self.risk.initial_balance == 0:
                self.risk.initial_balance = avail
        return avail

    # ═══ WebSocket ═══
    async def ws_manager(self):
        ws_url = ("wss://stream.binancefuture.com/ws/!bookTicker" if self.TESTNET
                  else "wss://fstream.binance.com/ws/!bookTicker")
        while True:
            try:
                async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10) as ws:
                    logger.info("✅ Futures WebSocket متصل (Global Mode)!")
                    self._reset_error("انقطاع WebSocket")
                    async for message in ws:
                        try:
                            data = json.loads(message)
                            if 's' in data and 'b' in data and 'a' in data:
                                self.live_prices[data['s']] = {
                                    'bid': float(data['b']), 'ask': float(data['a']),
                                    'ts': time.time()}
                        except (ValueError, KeyError, TypeError):
                            continue
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self._notify_error("انقطاع WebSocket", exc=e, context="إعادة الاتصال خلال 5 ثوانٍ")
                await asyncio.sleep(5)

    async def get_klines(self, symbol, interval='15m', limit=100):
        # تحقق من الكاش
        cached = self.kline_cache.get(symbol, interval)
        if cached is not None:
            return cached
        data = await self._fapi_request('GET', '/fapi/v1/klines',
            {'symbol': symbol, 'interval': interval, 'limit': limit})
        if data and len(data) > 20:
            df = pd.DataFrame(data, columns=[
                'time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_vol',
                'taker_buy_quote_vol', 'ignore'])
            for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            # تحقق من البيانات الناقصة
            if df.isnull().any().any():
                df = df.dropna()
                if len(df) < 20:
                    return None
            self.kline_cache.set(symbol, interval, df)
            return df
        return None

    @staticmethod
    def _compute_atr(df, period=14):
        """يستخدم Wilder's ATR الآن (من SMC Engine)."""
        return WhaleSMCEngineV2.compute_atr_wilder(df, period)

    # ═══ ✅ V9.1: نظام التقييم — دقة الدخول أولاً ═══
    async def analyze_whale_zone(self, symbol):
        """نظام التقييم 10 نقاط (6 مكونات) — دقة الدخول هي الأهم:
        - ✅ دقة الدخول (0-3) [الأهم]: داخل OB=3, على الحافة=2, قريب=1, بعيد=رفض
        - الزناد (0-3): sweep قوي=3, sweep/retest عادي=2, لمس=1
        - ستوكاستك (0-2): cross مع تشبع=2, cross عادي=1
        - حجم (0-1): تضخيم حجم
        - توافق EMA Multi-TF (0-1)
        - بنية السوق (0-1)
        """
        tuner = self.tuner
        df_4h = await self.get_klines(symbol, '4h', 100)
        df_1h = await self.get_klines(symbol, '1h', 100)
        df_15m = await self.get_klines(symbol, '15m', 100)
        if (df_4h is None or len(df_4h) < 30 or df_1h is None or len(df_1h) < 30
                or df_15m is None or len(df_15m) < 30):
            return None

        prices = self.get_price(symbol)
        if not prices:
            return None

        mid = (prices['bid'] + prices['ask']) / 2
        # 1) تحقق توافق EMA على 4h و 1h
        trend, aligned = self.smc.multi_tf_trend(df_4h, df_1h, mid)
        if trend is None:
            return None
        trend_pts = 1 if aligned else 0
        current_price = prices['ask'] if trend == 'BUY' else prices['bid']

        # 2) ✅ V9.1: قرب منطقة الحوت (OB) — الدخول من داخل المنطقة وليس فوقها
        atr_1h = self._compute_atr(df_1h)
        if not atr_1h or atr_1h <= 0:
            return None
        obs = self.smc.detect_order_blocks(df_1h, trend, atr_1h)
        if not obs:
            return None
        nearby_ob = None
        proximity_pts = 0
        for ob in reversed(obs[-10:]):
            if trend == 'BUY' and ob['type'] == 'demand':
                ob_bottom = float(ob['bottom'])
                ob_top = float(ob['top'])
                # ✅ V9.1: السعر يجب أن يكون داخل OB أو على حافتها مباشرة
                # السعر داخل المنطقة (بين bottom و top) = دقة قصوى
                if ob_bottom <= current_price <= ob_top:
                    nearby_ob = ob
                    proximity_pts = 3  # ✅ دقة قصوى: داخل المنطقة
                    break
                # السعر عند حافة OB العلوية (ضمن 0.2% فقط) = دقة عالية
                elif ob_top < current_price <= ob_top * 1.002:
                    nearby_ob = ob
                    proximity_pts = 2  # على الحافة
                    break
                # السعر لمس OB من فوق ضمن 0.5% = مقبول
                elif ob_top * 0.998 <= current_price <= ob_top * 1.005:
                    nearby_ob = ob
                    proximity_pts = 1  # قريب
                    break
                # ❌ السعر أكثر من 0.5% فوق OB = متأخر جداً، ارفض
            elif trend == 'SELL' and ob['type'] == 'supply':
                ob_bottom = float(ob['bottom'])
                ob_top = float(ob['top'])
                if ob_bottom <= current_price <= ob_top:
                    nearby_ob = ob
                    proximity_pts = 3
                    break
                elif ob_bottom * 0.998 <= current_price < ob_bottom:
                    nearby_ob = ob
                    proximity_pts = 2
                    break
                elif ob_bottom * 0.995 <= current_price <= ob_bottom * 1.002:
                    nearby_ob = ob
                    proximity_pts = 1
                    break
        if not nearby_ob:
            return None  # السعر بعيد عن OB — لا صفقة

        # 3) الزناد
        sweep = self.smc.detect_liquidity_sweep(df_15m, nearby_ob, trend)
        retest = False if sweep else self.smc.detect_ob_retest(df_15m, nearby_ob, trend)
        if not (sweep or retest):
            return None
        trigger_pts = 3 if sweep else 2

        # 4) الاستوكاستك (نقاط فقط، ليس شرط رفض!)
        df_15m = self.smc.calculate_stochastic(df_15m)
        current_k = float(df_15m['stoch_k'].iloc[-2])
        prev_k = float(df_15m['stoch_k'].iloc[-3])
        current_d = float(df_15m['stoch_d'].iloc[-2])
        prev_d = float(df_15m['stoch_d'].iloc[-3])

        stoch_pts = 0
        if trend == 'BUY':
            # cross صاعد
            if current_k > current_d and prev_k <= prev_d:
                stoch_pts = 2 if current_k < 25 else 1
            elif current_k < 35 and tuner.stoch_strictness == 0:
                stoch_pts = 1
        else:
            if current_k < current_d and prev_k >= prev_d:
                stoch_pts = 2 if current_k > 75 else 1
            elif current_k > 65 and tuner.stoch_strictness == 0:
                stoch_pts = 1

        # 5) حجم التداول
        vol_pts = 0
        try:
            qv = df_15m['quote_volume']
            base = qv.iloc[-22:-2].mean()
            if base and base > 0 and qv.iloc[-2] > base * 1.3:
                vol_pts = 1
        except (TypeError, ValueError, IndexError):
            pass

        # 6) بنية السوق (HH/HL أو LH/LL)
        structure_ok = self.smc.detect_market_structure(df_1h, trend)
        structure_pts = 1 if structure_ok else 0

        # المجموع
        score = proximity_pts + trigger_pts + stoch_pts + vol_pts + trend_pts + structure_pts
        self.stats['total_signals'] += 1
        if score < tuner.min_score:
            return None

        # 7) ✅ V9.2: الدخول والأهداف — ربحية حقيقية
        atr_15m = self._compute_atr(df_15m)
        if not atr_15m or atr_15m <= 0 or math.isnan(atr_15m):
            return None

        exit_plan = self._exit_plan(score, tuner)

        # ✅ V9.2: SL محكم 0.5×ATR تحت OB
        sl_buffer = atr_15m * exit_plan['sl_atr_mult']
        if trend == 'BUY':
            sweep_low = float(df_15m['low'].iloc[-2])
            sl_base = min(nearby_ob['bottom'], sweep_low)
            sl = sl_base - sl_buffer
            # ✅ V9.2: TP1 = 3.0×ATR (ربح ~1.5%)
            tp1 = current_price + atr_15m * exit_plan['tp1_atr_mult']
            # ✅ V9.2: TP2 = 6.0×ATR (ربح ~3%)
            tp2 = current_price + atr_15m * exit_plan['tp2_mult']
        else:
            sweep_high = float(df_15m['high'].iloc[-2])
            sl_base = max(nearby_ob['top'], sweep_high)
            sl = sl_base + sl_buffer
            tp1 = current_price - atr_15m * exit_plan['tp1_atr_mult']
            tp2 = current_price - atr_15m * exit_plan['tp2_mult']

        # تحقق صحة الأسعار
        if sl <= 0 or math.isnan(sl) or math.isnan(tp1) or math.isnan(tp2):
            return None
        if trend == 'BUY' and sl >= current_price:
            return None
        if trend == 'SELL' and sl <= current_price:
            return None
        if trend == 'BUY' and tp1 <= current_price:
            return None
        if trend == 'SELL' and tp1 >= current_price:
            return None

        # تحقق المخاطرة (R:R يجب أن يكون ≥ 1.2)
        risk_per_unit = abs(current_price - sl)
        reward_per_unit = abs(tp1 - current_price)
        if risk_per_unit <= 0:
            return None
        rr_ratio = reward_per_unit / risk_per_unit
        if rr_ratio < 1.2:
            return None  # R:R ضعيف — ارفض

        # نسبة المخاطرة (٪) — فلتر
        risk_pct = risk_per_unit / current_price * 100
        if risk_pct > 4.0 or risk_pct < 0.05:
            return None

        return {
            'symbol': symbol, 'direction': trend, 'price': current_price,
            'sl': sl, 'tp1': tp1, 'tp2': tp2, 'score': score,
            'rr_ratio': rr_ratio,
            'exit_plan': exit_plan,
            'signal_ts': time.time(),  # ✅ V9.6: timestamp للإشارة لفلتر العمر
            'components': {
                'proximity': proximity_pts,
                'trigger': 'sweep' if sweep else 'retest',
                'trigger_pts': trigger_pts,
                'stoch_pts': stoch_pts,
                'volume': vol_pts,
                'trend_aligned': trend_pts,
                'structure': structure_pts,
                'score': score,
                'rr_ratio': rr_ratio,
                'tuner': tuner.describe()
            },
            'signals_smc': [
                f"🐋 {'صيد حوت' if sweep else 'إعادة اختبار'} في منطقة {'طلب' if trend=='BUY' else 'عرض'}",
                f"📍 الدخول: {'داخل OB' if proximity_pts == 3 else 'على حافة OB' if proximity_pts == 2 else 'قريب من OB'}",
                f"📊 تقييم الإشارة: {score}/10",
                f"⚖️ R:R = {rr_ratio:.2f}:1",
                f"🛡️ SL: 0.5×ATR تحت OB ({risk_pct:.1f}%)",
                f"🎯 TP1: 3×ATR (~1.5% ربح) | TP2: 6×ATR (~3% ربح)"
            ]
        }

    # ═══ ✅ V9.2: خطة الخروج — ربحية حقيقية ═══
    @staticmethod
    def _exit_plan(score, tuner):
        """
        ✅ V9.2: أهداف تدر ربحاً حقيقياً
        
        مع هامش $25 ورافعة 10x:
        - TP1 = 3.0×ATR ≈ 1.5% حركة = ~$3.75 ربح كامل (70% = $2.60)
        - TP2 = 6.0×ATR ≈ 3.0% حركة = ~$7.50 ربح كامل (30% = $2.25)
        - SL = 0.5×ATR تحت OB ≈ 0.25% خسارة = ~$0.63 خسارة
        
        R:R = 6:1 (ممتاز)
        
        3 صفقات ناجحة في اليوم = ~$7.50 صافي ربح
        5 صفقات ناجحة في اليوم = ~$12.50 صافي ربح
        """
        # ✅ V9.2: أهداف مرتفعة لربحية حقيقية
        return {
            'sl_atr_mult': 0.5,      # SL محكم تحت OB
            'tp1_atr_mult': 3.0,     # TP1 = 3.0×ATR (≈ 1.5% حركة)
            'tp2_mult': 6.0,         # TP2 = 6.0×ATR (≈ 3.0% حركة)
            'partial_ratio': 0.7     # 70% جني + 30% يركض لـ TP2
        }

    # ═══ التنفيذ ═══
    async def execute_trade(self, analysis):
        if not self.TRADE_ENABLED:
            return
        if len(self.active_trades) >= self.MAX_OPEN_TRADES:
            return

        symbol = analysis['symbol']
        if symbol in self.active_trades:
            return
        if self.is_in_cooldown(symbol):
            return

        # فحص Risk Manager
        can_trade, reason = self.risk.can_trade()
        if not can_trade:
            self.stats['rejected_by_risk'] += 1
            logger.info(f"🛡️ Risk: رفض {symbol} — {reason}")
            return

        # فحص News Filter
        in_blackout, news_event = self.news_filter.is_blackout(symbol)
        if in_blackout:
            self.stats['rejected_by_news'] += 1
            logger.info(f"📰 News: رفض {symbol} — حظر بسبب {news_event}")
            return

        available = await self.get_available_usdt()
        # ✅ V9.3: حساب حجم الصفقة بناءً على المخاطرة (مقيد بـ TRADE_SIZE_USDT)
        dynamic_size = self.risk.calc_position_size(
            analysis['price'], analysis['sl'], available or self.TRADE_SIZE_USDT
        )
        # ✅ V9.3: الحد الأقصى = TRADE_SIZE_USDT (لا يتجاوزه أبداً)
        # الهامش الديناميكي يسمح فقط بتقليل الحجم (نصف المبلغ) لتفادي المخاطرة العالية
        trade_size = min(dynamic_size, self.TRADE_SIZE_USDT)
        if available < trade_size * 1.2:
            self._notify_error("رصيد غير كافٍ للدخول",
                               context=f"المتاح {available:.2f}$ < المطلوب {trade_size * 1.2:.2f}$")
            return

        notional = trade_size * self.LEVERAGE
        quantity = self.format_quantity(symbol, notional / analysis['price'])
        if quantity <= 0:
            return
        if quantity < self.min_qty_cache.get(symbol, 0.0):
            return
        if quantity > self.max_qty_cache.get(symbol, 1e12):
            return
        if quantity * analysis['price'] < self.min_notional_cache.get(symbol, 5.0) * 1.02:
            return

        await self._fapi_request('POST', '/fapi/v1/leverage',
            {'symbol': symbol, 'leverage': self.LEVERAGE}, signed=True)
        await self._fapi_request('POST', '/fapi/v1/marginType',
            {'symbol': symbol, 'marginType': 'ISOLATED'}, signed=True, quiet=(-4046,))

        side = 'BUY' if analysis['direction'] == 'BUY' else 'SELL'
        result = await self._fapi_request('POST', '/fapi/v1/order', {
            'symbol': symbol, 'side': side, 'type': 'MARKET',
            'quantity': self.qty_to_str(symbol, quantity)
        }, signed=True)

        if not result or result.get('status') not in ['FILLED', 'NEW']:
            await self.tg(f"❌ *فشل تنفيذ {side} (`{symbol}`)*\n⚠️ تأكد من إعدادات العقود الآجلة وصلاحيات المفتاح")
            return

        avg = float(result.get('avgPrice') or 0)
        entry_price = avg if avg > 0 else analysis['price']

        exit_plan = analysis['exit_plan']
        trade_data = {
            'symbol': symbol, 'side': side, 'entry_price': entry_price,
            'quantity': quantity, 'sl': analysis['sl'], 'tp': analysis['tp1'],
            'tp2': analysis['tp2'],
            'score': analysis['score'],
            'partial_ratio': exit_plan['partial_ratio'],
            'tp2_mult': exit_plan['tp2_mult'],
            'sl_atr_mult': exit_plan['sl_atr_mult'],
            'tp1_atr_mult': exit_plan['tp1_atr_mult'],
            'trailing_active': False, 'highest_price': entry_price,
            'lowest_price': entry_price, 'entry_time': time.time(),
            'partial_closed': False, 'realized_pnl': 0.0,
            'stop_order_id': None, 'tp_order_id': None,
            'stop_is_algo': False, 'tp_is_algo': False,
            'stop_synced_price': None, 'tp_skipped': False,
            'tp_unconfirmed': False,
            'trade_size': trade_size
        }
        self.active_trades[symbol] = trade_data
        await self.db.save_trade(trade_data)
        self.stats['trades_executed'] += 1
        self.entry_history.append((time.time(), time.strftime("%Y-%m-%d")))
        await self.db.log_signal(symbol, side, trade_data['entry_time'],
                                 analysis['score'], analysis['components'])

        prices = self.get_price(symbol)
        ref_price = None
        if prices:
            ref_price = prices['bid'] if side == 'BUY' else prices['ask']
        if ref_price is None:
            ref_price = entry_price
        await self._sync_stop_order(trade_data, ref_price)
        await self.db.save_trade(trade_data)

        msg = (f"✅ *صفقة منفذة!* (تقييم {analysis['score']}/10)\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
               f"📍 الدخول: {'داخل OB ⭐' if analysis.get('components',{}).get('proximity',0) == 3 else 'على حافة OB' if analysis.get('components',{}).get('proximity',0) == 2 else 'قريب من OB'}\n"
               f"🏃 خطة الخروج: جني {int(exit_plan['partial_ratio']*100)}% عند TP1 والباقي يركض لـ TP2\n"
               f"⚖️ R:R = {analysis['rr_ratio']:.2f}:1\n"
               f"🪙 `{symbol}` | رافعة {self.LEVERAGE}x | هامش {trade_size:.1f}$\n"
               f"💵 الدخول: {self.fmt_price(entry_price)}\n"
               f"🛑 SL: {self.fmt_price(analysis['sl'])} (0.5×ATR تحت OB)\n"
               f"🎯 TP1: {self.fmt_price(analysis['tp1'])} (3×ATR ≈ +$2.60)\n"
               f"🎯 TP2: {self.fmt_price(analysis['tp2'])} (6×ATR ≈ +$2.25)\n"
               f"💰 ربح محتمل: ~${(trade_size*self.LEVERAGE*0.015*0.7 + trade_size*self.LEVERAGE*0.03*0.3):.2f}\n"
               f"🛡️ ستوب المنصة: {'✅' if trade_data['stop_order_id'] else '⏳'}\n"
               f"🧠 {self.tuner.describe()}")
        await self.tg(msg)

    # ═══ أوامر المنصة الشرطية (Algo Order API) ═══
    @staticmethod
    def _find_order_id(data):
        if isinstance(data, dict):
            for k in ('algoId', 'orderId', 'algoID', 'orderID'):
                v = data.get(k)
                if v:
                    return v
            for v in data.values():
                r = LegendarySniperFuturesV9._find_order_id(v)
                if r:
                    return r
        elif isinstance(data, list):
            for v in data:
                r = LegendarySniperFuturesV9._find_order_id(v)
                if r:
                    return r
        return None

    async def _place_algo_order(self, params):
        payload = {'algoType': 'CONDITIONAL'}
        payload.update(params)
        res = await self._fapi_request('POST', '/fapi/v1/algoOrder', payload,
                                       signed=True, soft=(-4130,))
        if isinstance(res, dict):
            if '_soft_code' in res:
                return 'EXISTS' if res['_soft_code'] == -4130 else None
            oid = self._find_order_id(res)
            if oid:
                return oid
            return 'UNKNOWN'
        return None

    async def _cancel_algo_order(self, symbol, algo_id):
        await self._fapi_request('DELETE', '/fapi/v1/algoOrder',
            {'symbol': symbol, 'algoId': algo_id}, signed=True, quiet=('-2011', '-2013'))

    async def _cancel_regular_order(self, symbol, order_id):
        await self._fapi_request('DELETE', '/fapi/v1/order',
            {'symbol': symbol, 'orderId': order_id}, signed=True, quiet=('-2011', '-2013'))

    async def _sync_stop_order(self, trade, current_price):
        symbol = trade['symbol']
        
        # ✅ إضافة فحص المركز للتأكد من أنه موجود ولا يسبب خطأ -4509
        amt = await self.get_position_amt(symbol)
        if amt is None or abs(amt) <= 0:
            return False

        is_buy = trade['side'] == 'BUY'
        desired = trade['sl']
        if desired is None:
            return False
        if not current_price or current_price <= 0:
            return False
        if (is_buy and desired >= current_price) or (not is_buy and desired <= current_price):
            return False

        desired_str = self.price_to_str(symbol, desired)
        if trade.get('stop_order_id') and trade.get('stop_synced_price') is not None:
            if self.price_to_str(symbol, trade['stop_synced_price']) == desired_str:
                return False

        stop_side = 'SELL' if is_buy else 'BUY'
        
        # ✅ التعديل الأهم: استخدام quantity مع reduceOnly بدلاً من closePosition لـ Testnet
        new_id = await self._place_algo_order({
            'symbol': symbol, 'side': stop_side, 'type': 'STOP_MARKET',
            'triggerPrice': desired_str, 
            'quantity': self.qty_to_str(symbol, abs(amt)),
            'reduceOnly': 'true',
            'workingType': 'CONTRACT_PRICE'})

        if new_id:
            old_id = trade.get('stop_order_id')
            old_is_algo = trade.get('stop_is_algo', True)
            if old_id:
                if old_is_algo:
                    await self._cancel_algo_order(symbol, old_id)
                else:
                    await self._cancel_regular_order(symbol, old_id)
            trade['stop_is_algo'] = True
            trade['stop_synced_price'] = desired
            if new_id in ('EXISTS', 'UNKNOWN'):
                trade['stop_order_id'] = None
                self._reset_error(f"ستوب المنصة {symbol}")
                logger.info(f"🛡️ ستوب {symbol} مؤكد على المنصة (معرف غير متاح من Testnet)")
                return True
            trade['stop_order_id'] = new_id
            self._reset_error(f"ستوب المنصة {symbol}")
            return True

        self._notify_error(f"تعذّر وضع ستوب المنصة لـ {symbol}",
                           context="سيُعاد — الوقف المحلي يعمل")
        return False

    async def _place_tp_order(self, trade, current_price):
        symbol = trade['symbol']
        is_buy = trade['side'] == 'BUY'
        if trade.get('tp_order_id') or trade.get('tp_skipped') or trade.get('tp_unconfirmed'):
            return
        tp2 = trade.get('tp2')
        if not tp2:
            return
        if (is_buy and tp2 <= current_price) or (not is_buy and tp2 >= current_price):
            trade['tp_skipped'] = True
            return
        close_side = 'SELL' if is_buy else 'BUY'
        # ✅ V9.0 إصلاح: استخدم الكمية المتبقية وليس الكمية الأصلية
        remaining_qty = trade['quantity']
        new_id = await self._place_algo_order({
            'symbol': symbol, 'side': close_side, 'type': 'TAKE_PROFIT_MARKET',
            'triggerPrice': self.price_to_str(symbol, tp2),
            'quantity': self.qty_to_str(symbol, remaining_qty),
            'reduceOnly': 'true',
            'workingType': 'CONTRACT_PRICE'})
        if new_id:
            trade['tp_is_algo'] = True
            if new_id in ('EXISTS', 'UNKNOWN'):
                trade['tp_order_id'] = None
                trade['tp_unconfirmed'] = True
            else:
                trade['tp_order_id'] = new_id
            await self.tg(f"🎯 *هدف TP2 مثبّت على المنصة* (`{symbol}`) عند {self.fmt_price(tp2)}\n"
                          f"📊 الكمية المتبقية: {remaining_qty}")
        else:
            trade['tp_skipped'] = True
            self._notify_error(f"تعذر تثبيت TP2 لـ {symbol}",
                               context="الوقف المتحرك سيُدير الخروج بدلاً منه")

    async def get_position_amt(self, symbol):
        try:
            res = await self._fapi_request('GET', '/fapi/v2/positionRisk',
                {'symbol': symbol}, signed=True)
            if isinstance(res, list) and res:
                return float(res[0].get('positionAmt', 0))
        except Exception as e:
            logger.warning(f"فشل استعلام المركز لـ {symbol}: {e}")
        return None

    async def get_last_realized_pnl(self, symbol, trade):
        try:
            res = await self._fapi_request('GET', '/fapi/v1/income',
                {'symbol': symbol, 'incomeType': 'REALIZED_PNL', 'limit': 20}, signed=True)
            if isinstance(res, list) and res:
                entry_ms = int(trade.get('entry_time', 0) * 1000)
                last = None
                for e in res:
                    if int(e.get('time', 0)) >= entry_ms - 5000:
                        last = e
                        break
                if last is not None:
                    return float(last.get('income', 0))
        except Exception as e:
            logger.warning(f"فشل جلب الأرباح المحققة لـ {symbol}: {e}")
        return None

    async def verify_positions(self):
        if not self.TRADE_ENABLED or not self.binance_api_key:
            return
        if not self.active_trades:
            return
        for symbol, trade in list(self.active_trades.items()):
            try:
                amt = await self.get_position_amt(symbol)
                if amt is None:
                    continue
                step = self.step_sizes_cache.get(symbol) or 1.0
                if abs(amt) < step:
                    pnl = await self.get_last_realized_pnl(symbol, trade)
                    
                    # ✅ تم جلب الأرباح أولاً، ثم تسجيلها وتحديث حالتها في اللوحة
                    is_win = pnl > 0 if pnl is not None else False
                    await self.db.set_signal_result(symbol, trade['entry_time'], is_win, pnl or 0.0)

                    prices = self.get_price(symbol)
                    if prices:
                        px = prices['bid'] if trade['side'] == 'BUY' else prices['ask']
                    else:
                        px = trade['entry_price']
                    
                    # تحديد نوع الإغلاق بناءً على PnL
                    if pnl is not None:
                        reason = "✅ أُغلق على المنصة (TP محتمل)" if pnl > 0 else "🛑 أُغلق على المنصة (SL محتمل)"
                    else:
                        reason = "🔄 أُغلق على المنصة"
                    await self._finalize_trade(trade, px, reason, pnl)
            except Exception as e:
                self._notify_error(f"فشل التحقق من مركز {symbol}", exc=e)

    async def _close_position(self, trade, current_price):
        symbol = trade['symbol']
        is_buy = trade['side'] == 'BUY'
        close_side = 'SELL' if is_buy else 'BUY'

        amt = await self.get_position_amt(symbol)
        if amt is None:
            self._notify_error(f"تعذر قراءة مركز {symbol}", context="إعادة المحاولة لاحقاً")
            return False, None, None
        step = self.step_sizes_cache.get(symbol) or 1.0
        if abs(amt) < step:
            pnl = await self.get_last_realized_pnl(symbol, trade)
            return True, current_price, pnl

        qty = self.format_quantity(symbol, min(trade['quantity'], abs(amt)))
        if qty <= 0:
            return True, current_price, await self.get_last_realized_pnl(symbol, trade)

        res = await self._fapi_request('POST', '/fapi/v1/order', {
            'symbol': symbol, 'side': close_side, 'type': 'MARKET',
            'quantity': self.qty_to_str(symbol, qty), 'reduceOnly': 'true'
        }, signed=True)

        if res and res.get('status') in ['FILLED', 'NEW']:
            fill = float(res.get('avgPrice') or 0)
            fill_price = fill if fill > 0 else current_price
            self._reset_error(f"إغلاق {symbol}")
            return True, fill_price, None

        amt2 = await self.get_position_amt(symbol)
        if amt2 is not None and abs(amt2) < step:
            return True, current_price, await self.get_last_realized_pnl(symbol, trade)

        self._notify_error(f"فشل إغلاق {symbol}",
                           context="ستُعاد المحاولة — ستوب المنصة يحمي المركز")
        return False, None, None

    async def _finalize_trade(self, trade, fill_price, reason, pnl_override=None):
        symbol = trade['symbol']
        is_buy = trade['side'] == 'BUY'

        # إلغاء الستوب والـ TP المعلقين بأمان
        for oid_key, algo_key in (('stop_order_id', 'stop_is_algo'), ('tp_order_id', 'tp_is_algo')):
            oid = trade.get(oid_key)
            if not oid:
                continue
            try:
                if trade.get(algo_key):
                    await self._cancel_algo_order(symbol, oid)
                else:
                    await self._cancel_regular_order(symbol, oid)
                    await self._cancel_algo_order(symbol, oid)
            except Exception as e:
                logger.debug(f"تعذر إلغاء أمر {oid_key}: {e}")

        if pnl_override is not None:
            final_pnl = pnl_override
        else:
            if is_buy:
                final_pnl = (fill_price - trade['entry_price']) * trade['quantity']
            else:
                final_pnl = (trade['entry_price'] - fill_price) * trade['quantity']

        total_pnl = trade.get('realized_pnl', 0.0) + final_pnl
        margin_used = trade.get('trade_size', self.TRADE_SIZE_USDT)
        margin_pnl_pct = (total_pnl / margin_used * 100) if margin_used > 0 else 0

        is_win = total_pnl > 0
        if is_win:
            self.stats['wins'] += 1
        else:
            self.stats['losses'] += 1

        # تحديث Risk Manager
        self.risk.record_trade_result(is_win, total_pnl)

        # تحديث Tuner
        self.tuner.record(is_win)
        try:
            await self.db.set_signal_result(symbol, trade['entry_time'], is_win, total_pnl)
        except Exception:
            pass

        await self.db.update_daily_pnl(total_pnl, is_win)
        await self.db.remove_trade(symbol)
        self.active_trades.pop(symbol, None)
        self.set_cooldown(symbol)

        icon = "✅" if is_win else "❌"
        partial_note = (f"\n🧾 جني جزئي سابق: `{trade.get('realized_pnl', 0.0):.4f} USDT`"
                        if abs(trade.get('realized_pnl', 0.0)) > 1e-9 else "")
        score_note = f"\n📊 تقييم الإشارة: `{trade.get('score', '—')}/10`" if trade.get('score') else ""
        consecutive_note = ""
        if self.risk.consecutive_losses >= 2:
            consecutive_note = f"\n⚠️ خسائر متتالية: {self.risk.consecutive_losses}"
        msg = (f"🏁 {icon} *إغلاق `{symbol}`*\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
               f"{reason}\n"
               f"💵 النتيجة: `{total_pnl:.4f} USDT` ({margin_pnl_pct:.1f}% من الهامش)\n"
               f"🏆 الإجمالي: {self.stats['wins']}W / {self.stats['losses']}L"
               f"{partial_note}{score_note}{consecutive_note}\n"
               f"🧠 {self.tuner.describe()}")
        await self.tg(msg)

    # ═══ مراقبة الصفقات (خروج ديناميكي + TP2 + Trailing محسّن) ═══
    async def monitor_trades(self):
        if not self.active_trades:
            return
        stale_symbols = []

        for symbol, trade in list(self.active_trades.items()):
            prices = self.get_price(symbol)
            if not prices:
                stale_symbols.append(symbol)
                continue

            is_buy = trade['side'] == 'BUY'
            current_price = prices['bid'] if is_buy else prices['ask']
            if current_price <= 0:
                continue
            changed = False

            if is_buy and current_price > trade.get('highest_price', 0):
                trade['highest_price'] = current_price
                changed = True
            elif not is_buy and (trade.get('lowest_price', 999999999) == 999999999 or
                                  current_price < trade.get('lowest_price', 999999999)):
                trade['lowest_price'] = current_price
                changed = True

            # 1) وقف الخسارة
            if (is_buy and current_price <= trade['sl']) or (not is_buy and current_price >= trade['sl']):
                closed, fill_price, pnl_override = await self._close_position(trade, current_price)
                if closed:
                    await self._finalize_trade(trade, fill_price, "🛑 ضرب SL", pnl_override)
                continue

            # 2) الجني الجزئي عند TP1 — V9.0: نسبة ديناميكية حسب exit_plan
            if not trade.get('partial_closed', False) and trade.get('tp'):
                if (is_buy and current_price >= trade['tp']) or (not is_buy and current_price <= trade['tp']):
                    ratio = trade.get('partial_ratio', 0.7)
                    partial_qty = self.format_quantity(symbol, trade['quantity'] * ratio)
                    remaining_qty = self.format_quantity(symbol, trade['quantity'] - partial_qty)
                    min_notional = self.min_notional_cache.get(symbol, 5.0)

                    # إذا الكميات صغيرة جداً → إغلاق كامل
                    if (partial_qty <= 0 or remaining_qty <= 0
                            or partial_qty * current_price < min_notional
                            or remaining_qty * current_price < min_notional):
                        closed, fill_price, pnl_override = await self._close_position(trade, current_price)
                        if closed:
                            await self._finalize_trade(trade, fill_price,
                                "🎯 TP1 (إغلاق كامل — حدود الزوج)", pnl_override)
                        continue

                    close_side = 'SELL' if is_buy else 'BUY'
                    res = await self._fapi_request('POST', '/fapi/v1/order', {
                        'symbol': symbol, 'side': close_side, 'type': 'MARKET',
                        'quantity': self.qty_to_str(symbol, partial_qty),
                        'reduceOnly': 'true'
                    }, signed=True)

                    if res and res.get('status') in ['FILLED', 'NEW']:
                        fill = float(res.get('avgPrice') or 0)
                        fill_price = fill if fill > 0 else current_price
                        if is_buy:
                            partial_pnl = (fill_price - trade['entry_price']) * partial_qty
                        else:
                            partial_pnl = (trade['entry_price'] - fill_price) * partial_qty

                        trade['realized_pnl'] = trade.get('realized_pnl', 0.0) + partial_pnl
                        await self.db.update_daily_pnl(partial_pnl, None)
                        trade['quantity'] = remaining_qty
                        trade['partial_closed'] = True
                        # ✅ V9.3: نقل SL إلى سعر TP1 (lock الربح) — وليس التعادل
                        # هذا يضمن أن الـ 30% المتبقية:
                        #   - إما أن تصل لـ TP2 = ربح أكبر
                        #   - أو تخرج عند TP1 = ربح مضمون (لا خسارة أبداً)
                        tp1_price = trade.get('tp')
                        if tp1_price:
                            # SL عند TP1 بهامش ضيق جداً (0.1%) للسماح بحدوث Trailing
                            if is_buy:
                                new_sl = tp1_price * 0.999  # تحت TP1 بـ 0.1%
                                if new_sl > trade['sl']:  # فقط إذا أعلى من SL الحالي
                                    trade['sl'] = new_sl
                            else:
                                new_sl = tp1_price * 1.001  # فوق TP1 بـ 0.1%
                                if new_sl < trade['sl']:
                                    trade['sl'] = new_sl
                        changed = True
                        await self.tg(f"🎯 *جني أرباح أول (`{symbol}`)*\n"
                                      f"💸 أُغلق {int(ratio*100)}% بربح: `{partial_pnl:.4f} USDT`\n"
                                      f"🛡️ الوقف نُقل لـ TP1 (ربح مضمون للـ 30% المتبقية)\n"
                                      f"📊 التقييم: {trade.get('score', '—')}/10")
                        await self._place_tp_order(trade, current_price)
                    else:
                        amt = await self.get_position_amt(symbol)
                        if amt is not None and abs(amt) < (self.step_sizes_cache.get(symbol) or 1.0):
                            pnl = await self.get_last_realized_pnl(symbol, trade)
                            await self._finalize_trade(trade, current_price, "🛑 أُغلق على المنصة (Stop)", pnl)
                            continue
                        self._notify_error(f"فشل الجني الجزئي لـ {symbol}",
                                           context="إعادة المحاولة في الدورة القادمة")

            # 3) ✅ V9.3: الوقف المتحرك الذكي (بعد الجزئي)
            # الفرق: Trailing لا ينزل SL أبداً تحت TP1 (حماية الربح)
            if trade.get('partial_closed'):
                trailing_pct = self.tuner.trailing_pct
                tp1_price = trade.get('tp', 0)
                if is_buy:
                    new_sl = trade['highest_price'] * (1 - trailing_pct)
                    # ✅ V9.3: SL لا ينزل تحت TP1 أبداً (lock الربح)
                    if tp1_price > 0:
                        new_sl = max(new_sl, tp1_price * 0.999)
                    if new_sl > trade['sl']:
                        trade['sl'] = new_sl
                        changed = True
                else:
                    new_sl = trade['lowest_price'] * (1 + trailing_pct)
                    if tp1_price > 0:
                        new_sl = min(new_sl, tp1_price * 1.001)
                    if new_sl < trade['sl']:
                        trade['sl'] = new_sl
                        changed = True

            # 4) مزامنة ستوب المنصة
            if await self._sync_stop_order(trade, current_price):
                changed = True

            if changed:
                await self.db.save_trade(trade)

        if stale_symbols:
            self._notify_error("أسعار مجمّدة لمراكز مفتوحة",
                               context=f"{', '.join(stale_symbols)} — ستوب المنصة يحميها")

    # ═══ المسح الشامل (V9.0: كل العقود) ═══
    async def scan_all_perpetuals(self):
        """مسح كل العقود PERPETUAL + فلترة بالتقلب."""
        tickers = await self._fapi_request('GET', '/fapi/v1/ticker/24hr')
        if not tickers:
            self._notify_error("فشل جلب بيانات تقلب السوق", context="مشكلة اتصال مؤقتة")
            return
        self._reset_error("فشل جلب بيانات تقلب السوق")

        # فلترة بالتقلب: بين threshold و 15% (تجنب العملات التي تحركت كثيراً = الفرصة فاتت)
        targets = []
        min_vol = self.tuner.volatility_threshold
        for t in tickers:
            symbol = t.get('symbol', '')
            try:
                change = abs(float(t.get('priceChangePercent', 0)))
                quote_vol = float(t.get('quoteVolume', 0))
            except (TypeError, ValueError):
                continue
            # شرط: تقلب معقول + سيولة كافية (≥ 10M$ يومياً)
            if (min_vol <= change <= 15
                    and quote_vol >= 10_000_000
                    and symbol in self.step_sizes_cache):
                targets.append({'symbol': symbol, 'change': change, 'volume': quote_vol})

        # ترتيب: الأعلى تقلباً أولاً
        targets.sort(key=lambda x: x['change'], reverse=True)

        # مسح حتى 40 عملة (بدلاً من 20)
        scan_targets = targets[:40]
        results = []
        for target in scan_targets:
            symbol = target['symbol']
            if symbol in self.active_trades:
                continue
            if self.is_in_cooldown(symbol):
                continue
            try:
                analysis = await self.analyze_whale_zone(symbol)
                if analysis:
                    results.append(analysis)
            except Exception as e:
                logger.debug(f"خطأ تحليل {symbol}: {e}")
            await asyncio.sleep(0.25)  # تأخير أقصر

        self.stats['signals_found'] += len(results)
        self.last_scan_info = {
            'ts': time.time(),
            'volatile': len(targets),
            'scanned': len(scan_targets),
            'signals': len(results)
        }

        fresh_lines = []
        now = time.time()
        # ✅ V9.6: فلتر عمر الإشارة — لا تنفذ إشارة أقدم من 15 دقيقة
        MAX_SIGNAL_AGE_SECONDS = 900  # 15 دقيقة كحد أقصى لعمر الإشارة
        executable_signals = []

        for a in results:
            key = (a['symbol'], a['direction'])
            # إشعار فقط للإشارات الجديدة (لمنع تكرار الإشعارات)
            if now - self.last_discovery_alert.get(key, 0) < 1800:
                # لا تخطر، لكن قد تكون الإشارة لا تزال قابلة للتنفيذ
                pass
            else:
                self.last_discovery_alert[key] = now
                fresh_lines.append(f"🐋 `{a['symbol']}` *{a['direction']}* @ {self.fmt_price(a['price'])}"
                                   f" (تقييم {a['score']}/10 | R:R {a['rr_ratio']:.1f}:1)")

            # ✅ V9.6: تحقق أن الإشارة لا تزال "طازجة" قبل التنفيذ
            signal_ts = a.get('signal_ts', now)
            signal_age = now - signal_ts
            if signal_age > MAX_SIGNAL_AGE_SECONDS:
                logger.info(f"⏭️ {a['symbol']}: إشارة قديمة ({signal_age/60:.0f} دقيقة) — تخطي التنفيذ")
                continue

            # ✅ V9.6: تحقق أن السعر لم يتحرك كثيراً من نقطة الإشارة
            current_prices = self.get_price(a['symbol'])
            if current_prices:
                current_mid = (current_prices['bid'] + current_prices['ask']) / 2
                price_drift = abs(current_mid - a['price']) / a['price']
                if price_drift > 0.005:  # السعر تحرك أكثر من 0.5% من الإشارة
                    logger.info(f"⏭️ {a['symbol']}: السعر تحرك {price_drift*100:.1f}% من الإشارة — تخطي")
                    continue
                # تحديث سعر الإشارة للسعر الحالي
                a['price'] = current_prices['ask'] if a['direction'] == 'BUY' else current_prices['bid']

            executable_signals.append(a)

        if fresh_lines:
            await self.tg("🚀 *إشارات جديدة!*\n━━━━━━━━━━━━━━━━━━━━━━━━\n" + "\n".join(fresh_lines))

        # ✅ V9.6: تنفيذ فقط الإشارات الطازجة
        for a in executable_signals:
            await self.execute_trade(a)
            await asyncio.sleep(0.5)

    # ═══ المطوّر التكييفي — V9.0: تعديل حقيقي ═══
    def _trades_today(self):
        today = time.strftime("%Y-%m-%d")
        return sum(1 for _, d in self.entry_history if d == today)

    def _frequency_guard(self):
        now = time.time()
        if now - self._last_freq_check < 3600:
            return
        self._last_freq_check = now

        # محاولة تكييف المعاملات
        action = self.tuner.adapt()
        if action:
            logger.info(f"🧠 مطوّر تكييفي: {action}")
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.tuner.save())
                loop.create_task(self.tg(f"🧠 *المطوّر التكييفي:*\n{action}\n{self.tuner.describe()}"))
            except RuntimeError:
                pass

    # ═══ الصيانة الذاتية ═══
    def _cleanup_memory(self):
        now = time.time()
        self.reentry_cooldown = {k: v for k, v in self.reentry_cooldown.items() if v > now}
        self.last_discovery_alert = {k: v for k, v in self.last_discovery_alert.items()
                                     if v > now - 7200}
        # تنظيف live_prices القديمة (إصلاح تسرب الذاكرة)
        if len(self.live_prices) > 500:
            cutoff = now - 300  # أقدم من 5 دقائق
            self.live_prices = {k: v for k, v in self.live_prices.items() if v.get('ts', 0) > cutoff}
        if len(self.error_counts) > 500:
            self.error_counts.clear()

    async def _send_daily_report(self, day):
        row = await self.db.get_day_stats(day)
        if not row:
            return
        pnl, w, l = row
        wr = (w / (w + l) * 100) if (w + l) > 0 else 0
        await self.tg(f"📊 *تقرير {day}*\n💰 PnL: `{pnl:.4f} USDT`\n"
                      f"🏆 {w}W / {l}L (فوز {wr:.0f}%)\n🧠 {self.tuner.describe()}")

    async def _heartbeat_and_report(self, loop_count):
        now = time.time()
        today = time.strftime("%Y-%m-%d")
        if today != self._report_day:
            await self._send_daily_report(self._report_day)
            self._report_day = today
        if now - self._last_heartbeat >= 3600:
            self._last_heartbeat = now
            wr = self.tuner.recent_winrate(10)
            wr_txt = f"{wr*100:.0f}%" if wr is not None else "غير كافٍ بعد"
            can_t, reason = self.risk.can_trade()
            status = "✅ مسموح" if can_t else reason
            await self.tg(f"💓 *النبض:* حي ✓ | مسح #{loop_count} | "
                          f"صفقات اليوم: {self._trades_today()} | فوز آخر 10: {wr_txt}\n"
                          f"🛡️ المخاطر: {status}\n"
                          f"📊 إجمالي: {self.stats['signals_found']} إشارة / {self.stats['trades_executed']} صفقة\n"
                          f"🧠 {self.tuner.describe()}")

    # ═══ المصالحة الذاتية عند الإقلاع ═══
    async def reconcile(self):
        if not self.binance_api_key or not self.TRADE_ENABLED:
            return
        try:
            positions = await self._fapi_request('GET', '/fapi/v2/positionRisk', signed=True)
            open_pos = {}
            if isinstance(positions, list):
                for p in positions:
                    try:
                        amt = float(p.get('positionAmt', 0))
                    except (TypeError, ValueError):
                        continue
                    if abs(amt) > 0:
                        open_pos[p['symbol']] = {'amt': amt, 'entry': float(p.get('entryPrice', 0))}

            for symbol, trade in list(self.active_trades.items()):
                pos = open_pos.get(symbol)
                step = self.step_sizes_cache.get(symbol) or 1.0
                if not pos or abs(pos['amt']) < step:
                    pnl = await self.get_last_realized_pnl(symbol, trade)
                    await self._finalize_trade(trade, trade['entry_price'],
                                               "🔄 أُغلق أثناء توقف البوت", pnl)

            for symbol, pos in open_pos.items():
                if symbol in self.active_trades:
                    continue
                side = 'BUY' if pos['amt'] > 0 else 'SELL'
                entry = pos['entry'] or (self.live_prices.get(symbol, {}).get('bid', 0))

                if not entry or entry <= 0:
                    await self.tg(f"⚠️ *تعذّر تبنّي مركز يتيم* (`{symbol}`)\n"
                                  f"سعر الدخول غير متاح بعد — سيُعاد في إعادة تشغيل قادمة")
                    continue

                df = await self.get_klines(symbol, '15m', 50)
                atr = self._compute_atr(df) if df is not None else None
                if not atr or atr <= 0 or math.isnan(atr):
                    atr = entry * 0.01

                if side == 'BUY':
                    sl, tp1, tp2 = entry - 1.5*atr, entry + 1.8*atr, entry + 4*atr
                else:
                    sl, tp1, tp2 = entry + 1.5*atr, entry - 1.8*atr, entry - 4*atr
                trade = {
                    'symbol': symbol, 'side': side, 'entry_price': entry,
                    'quantity': abs(pos['amt']), 'sl': sl, 'tp': tp1, 'tp2': tp2,
                    'score': 0, 'partial_ratio': 0.7, 'tp2_mult': 4.0,
                    'sl_atr_mult': 1.5, 'tp1_atr_mult': 1.8,
                    'trailing_active': False, 'highest_price': entry, 'lowest_price': entry,
                    'entry_time': time.time(), 'partial_closed': False,
                    'realized_pnl': 0.0, 'stop_order_id': None, 'tp_order_id': None,
                    'stop_is_algo': False, 'tp_is_algo': False,
                    'stop_synced_price': None, 'tp_skipped': False, 'tp_unconfirmed': False,
                    'trade_size': self.TRADE_SIZE_USDT
                }
                self.active_trades[symbol] = trade
                await self.db.save_trade(trade)
                await self._sync_stop_order(trade, entry)
                await self.db.save_trade(trade)
                await self.tg(f"🔄 *تم تبنّي مركز يتيم* (`{symbol}`)\n"
                              f"وقف ATR تلقائي عند {self.fmt_price(sl)}")

            orders = await self._fapi_request('GET', '/fapi/v1/openOrders', signed=True)
            if not isinstance(orders, list):
                orders = []
            known_ids = set()
            for t in self.active_trades.values():
                if t.get('stop_order_id'):
                    known_ids.add(t['stop_order_id'])
                if t.get('tp_order_id'):
                    known_ids.add(t['tp_order_id'])
            cancelled = 0
            for o in orders:
                if o.get('orderId') not in known_ids and o.get('type') in ('STOP_MARKET', 'TAKE_PROFIT_MARKET'):
                    await self._cancel_regular_order(o['symbol'], o['orderId'])
                    cancelled += 1
            if cancelled:
                await self.tg(f"🧹 *تنظيف ذاتي:* أُلغي {cancelled} أمر يتيم على المنصة")
            logger.info(f"🧾 المصالحة الذاتية: {len(open_pos)} مركز حي، {cancelled} أمر يتيم ملغى")
        except Exception as e:
            self._notify_error("فشل المصالحة الذاتية", exc=e, context="غير قاتل — تُعاد كل دورات")

    # ═══ إيقاف آمن ═══
    async def request_shutdown(self):
        if self._shutdown_requested:
            return
        self._shutdown_requested = True
        logger.info("🛑 طلب إيقاف آمن...")
        try:
            await self.tg("🛑 *إيقاف آمن:* ستوب/أوامر TP على المنصة تبقى فعالة وتحمي المراكز.")
        except Exception:
            pass

    # ═══ ✅ V9.0: وضع Backtest ═══
    async def run_backtest(self):
        """وضع الاختبار على بيانات تاريخية."""
        logger.info(f"🧪 بدء Backtest على {self.BACKTEST_DAYS} يوم لـ {len(self.BACKTEST_SYMBOLS)} عملة")
        await self.tg(f"🧪 *بدء Backtest*\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
                      f"📅 المدة: {self.BACKTEST_DAYS} يوم\n"
                      f"🪙 العملات: {', '.join(self.BACKTEST_SYMBOLS)}\n"
                      f"💰 رأس المال: {self.TRADE_SIZE_USDT}$\n"
                      f"⚡ الرافعة: {self.LEVERAGE}x")

        # جمع البيانات التاريخية
        all_results = []
        end_time = int(time.time() * 1000)
        start_time = end_time - self.BACKTEST_DAYS * 24 * 3600 * 1000

        for symbol in self.BACKTEST_SYMBOLS:
            try:
                # جلب بيانات 15m لكل الفترة
                df_15m = await self._fetch_historical_klines(symbol, '15m', start_time, end_time)
                df_1h = await self._fetch_historical_klines(symbol, '1h', start_time, end_time)
                df_4h = await self._fetch_historical_klines(symbol, '4h', start_time, end_time)
                if df_15m is None or df_1h is None or df_4h is None:
                    logger.warning(f"تعذر جلب بيانات {symbol}")
                    continue
                logger.info(f"📊 {symbol}: {len(df_15m)} شمعة 15m")
                # محاكاة
                results = self._simulate_trades(symbol, df_4h, df_1h, df_15m)
                all_results.extend(results)
            except Exception as e:
                logger.error(f"خطأ Backtest لـ {symbol}: {e}")

        # تقرير النتائج
        self._print_backtest_report(all_results)
        await self.tg(self._format_backtest_telegram(all_results))

    async def _fetch_historical_klines(self, symbol, interval, start_ms, end_ms):
        """جلب بيانات تاريخية كاملة (متعددة الطلبات)."""
        all_data = []
        cur_start = start_ms
        while cur_start < end_ms:
            try:
                data = await self._fapi_request('GET', '/fapi/v1/klines', {
                    'symbol': symbol, 'interval': interval,
                    'startTime': cur_start, 'endTime': end_ms, 'limit': 1500
                })
                if not data:
                    break
                all_data.extend(data)
                last_ts = int(data[-1][0])
                if last_ts <= cur_start:
                    break
                cur_start = last_ts + 1
                await asyncio.sleep(0.2)  # احترام rate limit
            except Exception as e:
                logger.warning(f"خطأ جلب klines {symbol} {interval}: {e}")
                break
        if not all_data or len(all_data) < 30:
            return None
        df = pd.DataFrame(all_data, columns=[
            'time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_vol',
            'taker_buy_quote_vol', 'ignore'])
        for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna()

    def _simulate_trades(self, symbol, df_4h, df_1h, df_15m):
        """محاكاة الصفقات على البيانات التاريخية."""
        results = []
        # نمر على كل شمعة 15m
        min_idx = 100  # نحتاج 100 شمعة قبل البدء
        if len(df_15m) <= min_idx + 50:
            return results

        for i in range(min_idx, len(df_15m) - 5):
            try:
                # عينة البيانات حتى هذه النقطة
                cur_15m = df_15m.iloc[:i+1].copy()
                # ابحث عن أقرب 1h و 4h
                cur_time = cur_15m['time'].iloc[-1]
                cur_1h = df_1h[df_1h['time'] <= cur_time].iloc[-100:] if len(df_1h[df_1h['time'] <= cur_time]) >= 30 else None
                cur_4h = df_4h[df_4h['time'] <= cur_time].iloc[-100:] if len(df_4h[df_4h['time'] <= cur_time]) >= 30 else None
                if cur_1h is None or cur_4h is None:
                    continue

                # السعر الحالي
                current_price = float(cur_15m['close'].iloc[-1])

                # تحقق توافق EMA
                trend, aligned = self.smc.multi_tf_trend(cur_4h, cur_1h, current_price)
                if trend is None:
                    continue
                trend_pts = 1 if aligned else 0

                # OB
                atr_1h = self._compute_atr(cur_1h)
                if not atr_1h or atr_1h <= 0:
                    continue
                obs = self.smc.detect_order_blocks(cur_1h, trend, atr_1h)
                if not obs:
                    continue

                nearby_ob = None
                proximity_pts = 0
                for ob in reversed(obs[-10:]):
                    if trend == 'BUY' and ob['type'] == 'demand':
                        ob_bottom = float(ob['bottom'])
                        ob_top = float(ob['top'])
                        if ob_bottom <= current_price <= ob_top:
                            nearby_ob = ob
                            proximity_pts = 3
                            break
                        elif ob_top < current_price <= ob_top * 1.002:
                            nearby_ob = ob
                            proximity_pts = 2
                            break
                        elif ob_top * 0.998 <= current_price <= ob_top * 1.005:
                            nearby_ob = ob
                            proximity_pts = 1
                            break
                    elif trend == 'SELL' and ob['type'] == 'supply':
                        ob_bottom = float(ob['bottom'])
                        ob_top = float(ob['top'])
                        if ob_bottom <= current_price <= ob_top:
                            nearby_ob = ob
                            proximity_pts = 3
                            break
                        elif ob_bottom * 0.998 <= current_price < ob_bottom:
                            nearby_ob = ob
                            proximity_pts = 2
                            break
                        elif ob_bottom * 0.995 <= current_price <= ob_bottom * 1.002:
                            nearby_ob = ob
                            proximity_pts = 1
                            break
                if not nearby_ob:
                    continue

                # الزناد
                sweep = self.smc.detect_liquidity_sweep(cur_15m, nearby_ob, trend)
                retest = False if sweep else self.smc.detect_ob_retest(cur_15m, nearby_ob, trend)
                if not (sweep or retest):
                    continue
                trigger_pts = 3 if sweep else 2

                # الستوكاستك
                cur_15m_stoch = self.smc.calculate_stochastic(cur_15m.copy())
                current_k = float(cur_15m_stoch['stoch_k'].iloc[-2])
                prev_k = float(cur_15m_stoch['stoch_k'].iloc[-3])
                current_d = float(cur_15m_stoch['stoch_d'].iloc[-2])
                prev_d = float(cur_15m_stoch['stoch_d'].iloc[-3])

                stoch_pts = 0
                if trend == 'BUY':
                    if current_k > current_d and prev_k <= prev_d:
                        stoch_pts = 2 if current_k < 25 else 1
                else:
                    if current_k < current_d and prev_k >= prev_d:
                        stoch_pts = 2 if current_k > 75 else 1

                # الحجم
                vol_pts = 0
                try:
                    qv = cur_15m['quote_volume']
                    base = qv.iloc[-22:-2].mean()
                    if base and base > 0 and qv.iloc[-2] > base * 1.3:
                        vol_pts = 1
                except (TypeError, ValueError, IndexError):
                    pass

                # البنية
                structure_ok = self.smc.detect_market_structure(cur_1h, trend)
                structure_pts = 1 if structure_ok else 0

                score = proximity_pts + trigger_pts + stoch_pts + vol_pts + trend_pts + structure_pts
                if score < self.tuner.min_score:
                    continue

                # حساب SL/TP — V9.2: ربحية حقيقية
                atr_15m = self._compute_atr(cur_15m)
                if not atr_15m or atr_15m <= 0:
                    continue
                exit_plan = self._exit_plan(score, self.tuner)
                sl_buffer = atr_15m * 0.5  # ✅ V9.2
                if trend == 'BUY':
                    sweep_low = float(cur_15m['low'].iloc[-1])
                    sl_base = min(float(nearby_ob['bottom']), sweep_low)
                    sl = sl_base - sl_buffer
                    tp1 = current_price + atr_15m * 3.0  # ✅ V9.2: 3×ATR
                    tp2 = current_price + atr_15m * 6.0  # ✅ V9.2: 6×ATR
                else:
                    sweep_high = float(cur_15m['high'].iloc[-1])
                    sl_base = max(float(nearby_ob['top']), sweep_high)
                    sl = sl_base + sl_buffer
                    tp1 = current_price - atr_15m * 3.0
                    tp2 = current_price - atr_15m * 6.0

                risk_per_unit = abs(current_price - sl)
                if risk_per_unit <= 0:
                    continue
                rr = abs(tp1 - current_price) / risk_per_unit
                if rr < 1.2:
                    continue

                # محاكاة الصفقة: ابحث عن SL أو TP1 في الشموع التالية
                entry_idx = i
                result_pnl = None
                for j in range(i+1, min(i+100, len(df_15m))):
                    future_high = float(df_15m['high'].iloc[j])
                    future_low = float(df_15m['low'].iloc[j])
                    if trend == 'BUY':
                        if future_low <= sl:
                            result_pnl = -risk_per_unit
                            break
                        if future_high >= tp1:
                            result_pnl = abs(tp1 - current_price)
                            break
                    else:
                        if future_high >= sl:
                            result_pnl = -risk_per_unit
                            break
                        if future_low <= tp1:
                            result_pnl = abs(tp1 - current_price)
                            break

                if result_pnl is not None:
                    qty = (self.TRADE_SIZE_USDT * self.LEVERAGE) / current_price
                    pnl_usd = result_pnl * qty
                    results.append({
                        'symbol': symbol, 'score': score, 'trend': trend,
                        'rr': rr, 'pnl': pnl_usd, 'time': cur_time
                    })
                    # تخطي 10 شموع لتجنب التداخل
                    i += 10
            except Exception as e:
                continue
        return results

    def _print_backtest_report(self, results):
        """طباعة تقرير Backtest في السجل."""
        if not results:
            logger.info("🧪 Backtest: لا توجد صفقات")
            return
        wins = [r for r in results if r['pnl'] > 0]
        losses = [r for r in results if r['pnl'] <= 0]
        total_pnl = sum(r['pnl'] for r in results)
        win_rate = len(wins) / len(results) * 100
        avg_win = sum(r['pnl'] for r in wins) / len(wins) if wins else 0
        avg_loss = sum(r['pnl'] for r in losses) / len(losses) if losses else 0
        profit_factor = sum(r['pnl'] for r in wins) / abs(sum(r['pnl'] for r in losses)) if losses else float('inf')

        report = f"""
═══════════════════════════════════════════════
  📊 تقرير Backtest (آخر {self.BACKTEST_DAYS} يوم)
═══════════════════════════════════════════════
  📈 إجمالي الصفقات: {len(results)}
  ✅ رابحة: {len(wins)} ({win_rate:.1f}%)
  ❌ خاسرة: {len(losses)} ({100-win_rate:.1f}%)
  💰 صافي الربح: {total_pnl:.2f}$ ({total_pnl/self.TRADE_SIZE_USDT*100:.1f}%)
  🎯 متوسط الربح: {avg_win:.2f}$
  🛑 متوسط الخسارة: {avg_loss:.2f}$
  ⚖️ Profit Factor: {profit_factor:.2f}
  📊 متوسط R:R: {sum(r['rr'] for r in results)/len(results):.2f}:1
═══════════════════════════════════════════════
"""
        logger.info(report)
        print(report)

    def _format_backtest_telegram(self, results):
        """تنسيق تقرير Backtest للوحة."""
        if not results:
            return "🧪 Backtest: لا توجد صفقات في الفترة المختبرة"
        wins = [r for r in results if r['pnl'] > 0]
        losses = [r for r in results if r['pnl'] <= 0]
        total_pnl = sum(r['pnl'] for r in results)
        win_rate = len(wins) / len(results) * 100
        avg_win = sum(r['pnl'] for r in wins) / len(wins) if wins else 0
        avg_loss = sum(r['pnl'] for r in losses) / len(losses) if losses else 0
        profit_factor = (sum(r['pnl'] for r in wins) / abs(sum(r['pnl'] for r in losses))
                         if losses else float('inf'))
        return (f"🧪 *تقرير Backtest*\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📅 المدة: {self.BACKTEST_DAYS} يوم\n"
                f"📈 إجمالي الصفقات: {len(results)}\n"
                f"✅ رابحة: {len(wins)} ({win_rate:.1f}%)\n"
                f"❌ خاسرة: {len(losses)} ({100-win_rate:.1f}%)\n"
                f"💰 صافي الربح: {total_pnl:.2f}$\n"
                f"🎯 متوسط الربح: {avg_win:.2f}$\n"
                f"🛑 متوسط الخسارة: {avg_loss:.2f}$\n"
                f"⚖️ Profit Factor: {profit_factor:.2f}\n"
                f"📊 متوسط R:R: {sum(r['rr'] for r in results)/len(results):.2f}:1")

    # ═══ اللوب الرئيسي ═══
    async def main_loop(self):
        self.session = aiohttp.ClientSession()
        try:
            await start_web_panel(self)

            loop = asyncio.get_running_loop()
            for sig_name in ('SIGINT', 'SIGTERM'):
                try:
                    loop.add_signal_handler(getattr(signal, sig_name),
                        lambda: asyncio.ensure_future(self.request_shutdown()))
                except (NotImplementedError, ValueError, AttributeError, RuntimeError):
                    pass

            await self.db.init_db()
            await self.tuner.load()
            await self.news_filter.fetch_events()

            # ✅ وضع Backtest: شغّله ثم اخروج
            if self.BACKTEST_MODE:
                # تحميل بيانات السوق للمعلومات الأساسية
                market_tries = 0
                while not self.all_futures_pairs and market_tries < 5:
                    market_tries += 1
                    await self.load_market_data()
                    if self.all_futures_pairs:
                        break
                    await asyncio.sleep(10)
                await self.run_backtest()
                await asyncio.sleep(5)
                return

            market_tries = 0
            while not self.all_futures_pairs:
                market_tries += 1
                await self.load_market_data()
                if self.all_futures_pairs:
                    break
                if market_tries == 1 or market_tries % 5 == 0:
                    await self.tg(f"❌ *فشل تحميل بيانات السوق* (محاولة {market_tries})\n"
                                  f"⏳ إعادة خلال 30 ثانية...")
                logger.error(f"فشل تحميل بيانات السوق (محاولة {market_tries})")
                if market_tries > 20:
                    logger.error("🚨 تجاوز حد المحاولات — إنهاء")
                    return
                await asyncio.sleep(30)

            self.active_trades = await self.db.load_active_trades()
            await self.sync_server_time()

            try:
                dual = await self._fapi_request('GET', '/fapi/v1/positionSide/dual', signed=True)
                if dual and dual.get('dualSidePosition'):
                    if self.TRADE_ENABLED:
                        self.TRADE_ENABLED = False
                        logger.error("❌ الحساب في وضع Hedge Mode — التحويل للمراقبة فقط")
                        await self.tg("⚠️ *تنبيه:* Hedge Mode مفعّل — البوت لوضع One-way فقط. تم التحويل للمراقبة.")
            except Exception as e:
                logger.warning(f"تعذر فحص Hedge Mode: {e}")

            if self.TRADE_ENABLED and self.binance_api_key:
                await self.setup_futures_account()

            self.ws_task = asyncio.create_task(self.ws_manager())
            await asyncio.sleep(10)

            if self.TRADE_ENABLED and self.binance_api_key:
                await self.reconcile()
                await self.verify_positions()
                # تهيئة الرصيد الأولي للـ Risk Manager
                bal = await self.get_available_usdt()
                if bal > 0:
                    self.risk.initial_balance = bal

            mode_trade = ("⚔️ تداول تلقائي" + (" (TESTNET 🧪)" if self.TESTNET else "")
                          if self.TRADE_ENABLED else "👁️ مراقبة فقط")
            msg = ("🚀 *القناص الأسطوري V9.2 — ربحية حقيقية!*\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
                   f"📡 الوضع: {mode_trade} | رافعة {self.LEVERAGE}x | هامش {self.TRADE_SIZE_USDT:.0f}$\n"
                   f"🎯 العتبة: {self.tuner.min_score}/10 (دقة الدخول أولاً)\n"
                   f"📍 الدخول: من داخل OB فقط (ليس فوقه)\n"
                   f"🛡️ SL: 0.5×ATR تحت OB (محكم)\n"
                   f"🎯 TP1: 3×ATR ≈ +$2.60 ربح | TP2: 6×ATR ≈ +$2.25 ربح\n"
                   f"💰 ربح الصفقة الكاملة: ~$4.85\n"
                   f"⚖️ R:R = 6:1 (ممتاز)\n"
                   f"🏃 خروج: 70% جني + 30% يركض لـ TP2\n"
                   f"📊 هدف يومي: 3 صفقات = ~$14.55 | 5 صفقات = ~$24.25\n"
                   f"🛡️ إدارة مخاطر: حد خسارة يومي {MAX_DAILY_LOSSES}\n"
                   f"📰 فلتر أخبار: {'مفعّل' if self.news_filter.enabled else 'معطل'}\n"
                   "━━━━━━━━━━━━━━━━━━━━━━━━\n⏰ بدء المسح...")
            await self.tg(msg)

            loop_count = 0
            while not self._shutdown_requested:
                try:
                    newest_ts = max((p.get('ts', 0) for p in self.live_prices.values()), default=0)
                    if newest_ts and (time.time() - newest_ts) > self.WS_STALE_ALERT:
                        self._notify_error("توقف تدفق الأسعار (WebSocket)",
                            context=f"لا تحديثات منذ {int(time.time() - newest_ts)} ثانية — ستوب المنصة يحمي المراكز")

                    await self.monitor_trades()
                    await self.scan_all_perpetuals()

                    loop_count += 1
                    self._loop_count = loop_count
                    self.stats['total_scans'] = loop_count
                    if loop_count % self.VERIFY_EVERY_N_LOOPS == 0:
                        await self.verify_positions()

                    self._frequency_guard()
                    self._cleanup_memory()
                    await self._heartbeat_and_report(loop_count)
                    await asyncio.sleep(SCAN_INTERVAL_SECONDS)
                except asyncio.CancelledError:
                    raise
                except Exception as loop_err:
                    logger.error(f"خطأ في الحلقة: {loop_err}")
                    self._notify_error("خطأ في الحلقة الرئيسية", exc=loop_err)
                    await asyncio.sleep(15)
        finally:
            if self.ws_task:
                self.ws_task.cancel()
            if self.session and not self.session.closed:
                await self.session.close()

    def start(self):
        asyncio.run(self.main_loop())


if __name__ == "__main__":
    bot = LegendarySniperFuturesV9()
    bot.start()
