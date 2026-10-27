"""
═══════════════════════════════════════════════════════════════════════
  🎯 القناص الأسطوري V12.1 — HMA Edition (استراتيجية HMA_DMI_MOMENTUM فقط)
═══════════════════════════════════════════════════════════════════════
  النسخة النهائية بقرار المالك بعد تشخيص 30 يوماً على 846 زوجاً حقيقياً
  (تقرير تشخيص HMA + تقرير الاستراتيجيتين) — ثلاثة تعديلات معتمدة:

  ▸ 1) حذف استراتيجية SBR-1 نهائياً وكل ما يخصها: المحرك (SBR1Engine)،
       إعداداتها (SBRSettings)، قائمتها المستبعدة، مسار analyze_sbr،
       آليات منع تكرارها، وضع SBR_LIVE، ووقف التعادل الخاص بها —
       لا يبقى في الكود سوى HMA_DMI_MOMENTUM ومنطقها كما هو حرفياً.
  ▸ 2) إصلاح الاختناق (اعتماد المالك): MAX_OPEN_TRADES أصبح 3 صفقات
       متزامنة بدل 1 — القيد الواحد كان يخنق الاستراتيجية إلى الصفر
       تقريباً في الرجع (ربحها الكامل لا يتحقق إلا بتزامن أعلى).
       قابل للتغيير بمتغير البيئة MAX_OPEN_TRADES (بين 1 و10).
  ▸ 3) حظر نافذة المساء (اعتماد المالك): الدخول الجديد معطل
       16:00–23:59 UTC — النافذة الأكثر خسارة في التشخيص. المخارج
       تعمل طوال اليوم. للتعطيل: HMA_BLOCK_EVENING=false (وللتخصيص:
       HMA_EVENING_START_UTC / HMA_EVENING_END_UTC).

  ▸ 📊 لوحة مراقبة مدمجة جديدة (بديلة كاملة عن لوحة web_panel القديمة):
       - تعمل داخل هذا الملف نفسه — بلا ملفات خارجية وبلا مكتبات إضافية.
       - المنفذ: DASHBOARD_PORT (افتراضي 8999، ويتبع PORT تلقائياً على منصات النشر) —
         مهم على Railway: اجعل DASHBOARD_PORT=8080 ليطابق منفذ النطاق العام.
       - الحماية: DASHBOARD_TOKEN — لو ضُبط، بيانات اللوحة تتطلب المفتاح (موصى به
         عند عرض اللوحة على نطاق عام). التعطيل: DASHBOARD_ENABLED=false.
       - تعرض كل ما يفعله البوت صغيراً وكبيراً مع سبب كل قرار: دورات المسح،
         كل إشارة وسبب قبولها وتفاصيلها، كل رفض وسببه، كل دخول بتفاصيل
         تنفيذه، كل خروج بسببه ونتيجته الفعلية، أخطاء المنصة، نبض الحالة،
         المراكز الحية بربحها العائم، الرصيد، وإحصاءات اليوم.
       - ملف أحداث دائم: bot_events.jsonl (سطر JSON لكل حدث) للتدقيق لاحقاً.
       - 🕹️ أوامر المالك من اللوحة (V12.1 — عادت كما في لوحة V11.3 القديمة):
           ⏸️ إيقاف التداول (طوارئ) / ▶️ استئناف — يمنع الصفقات الجديدة فقط
             وإدارة الصفقات المفتوحة والمخارج تستمر دائماً.
           🛑 إغلاق صفقة واحدة أو كل الصفقات فوراً بسعر السوق (من جدول المراكز).
           🔍 مسح فوري الآن — يوقظ حلقة المسح فوراً بدل انتظار الدورة.
           🔁 إعادة محاولة تثبيت ستوب المنصة لصفقة لم تؤكد بعد.
           🧹 إعادة ضبط شامل: مسح السجل والإحصائيات والأحداث — بلا لمس الصفقات.
         كل الأوامر عبر POST /api/command وتتطلب نفس مفتاح DASHBOARD_TOKEN.

  ▸ كل حمايات V11 كما هي بلا مساسة: ستوب المنصة + المراقبة المحلية،
    مدير المخاطر (3 متتالية → توقف 4س | يومي 3 → بقية اليوم | سحب 5% →
    بقية اليوم)، فلتر الأخبار، إعادة التحقق اللحظي قبل التنفيذ، تبنّي
    المراكز اليتيمة، تبريد الرموز، منع تكرار الإشارات (يصمد لإعادة
    التشغيل)، الرصيد المرجعي، وضع Testnet، وإشعارات تيليجرام.

  ▸ توافق قاعدة البيانات: صفوف الاستراتيجية القديمة (SBR) في القاعدة
    تُدار عادي عبر مسارات المخارج المشتركة — لا ترحيل مطلوب ولا فقدان بيانات.

  ▸ التشغيل: python bot.py  ثم افتح اللوحة: http://<عنوان الخادم>:8999/
═══════════════════════════════════════════════════════════════════════
"""

from datetime import datetime

import asyncio, aiohttp, json, math, os, sys, time, logging, requests
import collections
import numpy as np
import pandas as pd
import hmac
import hashlib
import signal
from decimal import Decimal
from urllib.parse import urlencode
from logging.handlers import RotatingFileHandler
import websockets
import aiosqlite

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logger = logging.getLogger('SniperV10')
logger.setLevel(logging.INFO)


# ─── ⏰ توقيت ليبيا (UTC+2 ثابت) + نظام 12 ساعة صباحاً/مساءً في كل السجل ───
def _libya_logtime(*args):
    """محوّل وقت السجل — يقبل أي عدد من الوسائط."""
    try:
        from datetime import datetime, timezone, timedelta
        ts = args[-1] if args else None
        try:
            ts = float(ts) if ts is not None else None
        except (TypeError, ValueError):
            ts = None
        if ts is None:
            ts = time.time()
        return datetime.fromtimestamp(ts, timezone(timedelta(hours=2))).timetuple()
    except Exception:
        return time.localtime()


class _LibyaTimeFormatter(logging.Formatter):
    """فورماتر السجل: توقيت ليبيا + 12 ساعة + صباحاً/مساءً."""
    converter = staticmethod(_libya_logtime)

    def formatTime(self, record, datefmt=None):
        try:
            from datetime import datetime, timezone, timedelta
            dt = datetime.fromtimestamp(record.created, timezone(timedelta(hours=2)))
            return dt.strftime('%d-%m-%Y %I:%M:%S') + (' صباحاً' if dt.hour < 12 else ' مساءً')
        except Exception:
            return time.strftime('%d-%m-%Y %I:%M:%S %p')


def libya_time_str(ts=None, seconds=False):
    """سلسلة زمنية للعرض بتوقيت ليبيا (12 ساعة + صباحاً/مساءً)."""
    try:
        from datetime import datetime, timezone, timedelta
        ts = time.time() if ts is None else float(ts)
        dt = datetime.fromtimestamp(ts, timezone(timedelta(hours=2)))
    except Exception:
        return time.strftime('%m-%d %H:%M')
    fmt = '%m-%d %I:%M:%S' if seconds else '%m-%d %I:%M'
    return dt.strftime(fmt) + (' صباحاً' if dt.hour < 12 else ' مساءً')


fmt = _LibyaTimeFormatter('%(asctime)s - %(levelname)s - %(message)s')
fh = RotatingFileHandler('bot_v8.log', maxBytes=2*1024*1024, backupCount=2, encoding='utf-8')
fh.setFormatter(fmt); logger.addHandler(fh)
ch = logging.StreamHandler(); ch.setFormatter(fmt); logger.addHandler(ch)


# ─── فحص الـ IP الصادر عند الإقلاع ───
def check_outbound_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        ip_address = response.json().get('ip')
        logger.info(f"Current Outbound IP on Railway: {ip_address}")
        return ip_address
    except Exception as e:
        logger.warning(f"Failed to fetch IP: {e}")
        return None


check_outbound_ip()


# ═══════════════════════ قاعدة البيانات ═════════════════════
class DatabaseManager:
    """
    نفس ملف القاعدة (sniper_v9.db) كي تُحفظ بيانات المالك التاريخية.
    جداول: active_trades (مبسّطة — بلا TP2/جزئي)، daily_stats، bot_params،
    signal_log، scan_rejections (سجل أسباب رفض العملات للوحة).
    """

    def __init__(self, db_name=None):
        volume_dir = os.environ.get('RAILWAY_VOLUME_MOUNT_PATH', '/data')
        os.makedirs(volume_dir, exist_ok=True)
        self.db_name = os.path.join(volume_dir, 'sniper_v9.db')

    async def init_db(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS active_trades (
                symbol TEXT PRIMARY KEY, side TEXT, entry_price REAL, quantity REAL,
                sl REAL, tp REAL, highest_price REAL, lowest_price REAL,
                entry_time REAL, realized_pnl REAL DEFAULT 0,
                stop_order_id INTEGER, tp_order_id INTEGER,
                stop_state TEXT, stop_error TEXT)""")
            await db.execute("""CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY, realized_pnl REAL, wins INTEGER, losses INTEGER)""")
            await db.execute("""CREATE TABLE IF NOT EXISTS bot_params (
                key TEXT PRIMARY KEY, value TEXT)""")
            await db.execute("""CREATE TABLE IF NOT EXISTS signal_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, direction TEXT,
                entry_ts REAL, score REAL, components TEXT,
                result INTEGER DEFAULT -1, pnl REAL, pnl_source TEXT)""")
            try:   # قواعد بيانات أقدم: إضافة عمود مصدر النتيجة (مؤكد/تقديري)
                await db.execute("ALTER TABLE signal_log ADD COLUMN pnl_source TEXT")
            except Exception:
                pass
            await db.execute("""CREATE TABLE IF NOT EXISTS scan_rejections (
                id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, symbol TEXT,
                reason TEXT, details TEXT)""")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_rej_ts ON scan_rejections(ts)")
            # ─── ترحيلات آمنة لتتبع مصدر الإشارة/الصفقة (استراتيجيتان مستقلتان) ───
            # ALTER فقط — لا حذف ولا إعادة إنشاء: بيانات المالك القديمة محفوظة
            # والصفوف القديمة تُنسب للاستراتيجية النشطة الوحيدة.
            for _mig in (
                "ALTER TABLE active_trades ADD COLUMN strategy TEXT DEFAULT 'HMA_DMI_MOMENTUM'",
                "ALTER TABLE signal_log ADD COLUMN strategy TEXT DEFAULT 'HMA_DMI_MOMENTUM'",
                "ALTER TABLE scan_rejections ADD COLUMN strategy TEXT DEFAULT 'HMA_DMI_MOMENTUM'",
            ):
                try:
                    await db.execute(_mig)
                except Exception:
                    pass   # العمود موجود مسبقاً — الترحيل مكتمل سابقاً
            try:
                await db.execute("CREATE INDEX IF NOT EXISTS idx_signal_strategy ON signal_log(strategy)")
            except Exception:
                pass
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

    async def log_signal(self, symbol, direction, entry_ts, score, components, strategy=None):
        """تسجيل إشارة موسوم باسم الاستراتيجية التي أصدرتها."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute(
                    "INSERT INTO signal_log (symbol, direction, entry_ts, score, components, strategy) "
                    "VALUES (?,?,?,?,?,?)",
                    (symbol, direction, entry_ts, score, json.dumps(components, ensure_ascii=False),
                     str(strategy or HMA_STRATEGY_NAME)[:32]))
                await db.commit()
        except Exception as e:
            logger.warning(f"تعذر تسجيل الإشارة: {e}")

    async def set_signal_result(self, symbol, entry_ts, win, pnl, source=None, strategy=None):
        """win: 1 ربح | 0 خسارة | 2 محايدة/غير محسوبة — source: binance/estimated.
        strategy: تصفية النتيجة على صفوف الاستراتيجية نفسها كي لا تختلط
        نتائج الاستراتيجيتين على نفس الرمز."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                if strategy:
                    await db.execute(
                        "UPDATE signal_log SET result=?, pnl=?, pnl_source=? "
                        "WHERE symbol=? AND entry_ts=? AND result=-1 AND (strategy=? OR strategy IS NULL)",
                        (int(win) if win is not None else 2, pnl, source, symbol, entry_ts,
                         str(strategy)[:32]))
                else:
                    await db.execute(
                        "UPDATE signal_log SET result=?, pnl=?, pnl_source=? WHERE symbol=? AND entry_ts=? AND result=-1",
                        (int(win) if win is not None else 2, pnl, source, symbol, entry_ts))
                await db.commit()
        except Exception as e:
            logger.warning(f"تعذر تحديث نتيجة الإشارة: {e}")

    async def log_rejection(self, symbol, reason, details='', strategy=None):
        """سجل أسباب الرفض موسوماً بالاستراتيجية (استراتيجية/مخاطر/أخبار/تنفيذ)."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute(
                    "INSERT INTO scan_rejections (ts, symbol, reason, details, strategy) VALUES (?,?,?,?,?)",
                    (time.time(), str(symbol)[:24], str(reason)[:140], str(details)[:200],
                     str(strategy or HMA_STRATEGY_NAME)[:32]))
                await db.commit()
        except Exception as e:
            logger.warning(f"تعذر تسجيل الرفض: {e}")

    async def prune_rejections(self, max_age_s=3 * 86400):
        try:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute("DELETE FROM scan_rejections WHERE ts < ?", (time.time() - max_age_s,))
                await db.commit()
        except Exception:
            pass

    async def save_trade(self, t):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""INSERT OR REPLACE INTO active_trades
                (symbol, side, entry_price, quantity, sl, tp, highest_price, lowest_price,
                 entry_time, realized_pnl, stop_order_id, tp_order_id, stop_state, stop_error, strategy)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (t['symbol'], t['side'], t['entry_price'], t['quantity'],
                 t['sl'], t.get('tp'), t.get('highest_price', 0), t.get('lowest_price', 999999),
                 t['entry_time'], float(t.get('realized_pnl', 0.0)),
                 t.get('stop_order_id'), t.get('tp_order_id'),
                 t.get('stop_state', 'none'), t.get('stop_error'),
                 str(t.get('strategy') or HMA_STRATEGY_NAME)[:32]))
            await db.commit()

    async def load_active_trades(self):
        """تحميل متسامح: يعمل مع الجدول الجديد المبسّط ومع جدول V9 القديم
        (أعمدة إضافية مثل tp2/partial_closed تُتجاهل — الكمية المتبقية هي
        المرجع دائماً)."""
        trades = {}
        try:
            async with aiosqlite.connect(self.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""SELECT symbol, side, entry_price, quantity, sl, tp,
                    highest_price, lowest_price, entry_time, realized_pnl,
                    stop_order_id, tp_order_id, stop_state, stop_error, strategy
                    FROM active_trades""") as cur:
                    async for row in cur:
                        trades[row['symbol']] = {
                            'symbol': row['symbol'], 'side': row['side'],
                            'strategy': row['strategy'] or HMA_STRATEGY_NAME,
                            'entry_price': row['entry_price'], 'quantity': row['quantity'],
                            'sl': row['sl'], 'tp': row['tp'],
                            'highest_price': row['highest_price'] or 0,
                            'lowest_price': row['lowest_price'] or 999999,
                            'entry_time': row['entry_time'],
                            'realized_pnl': row['realized_pnl'] if row['realized_pnl'] is not None else 0.0,
                            'stop_order_id': row['stop_order_id'],
                            'tp_order_id': row['tp_order_id'],
                            'stop_state': row['stop_state'] or 'none',
                            'stop_error': row['stop_error'],
                            'stop_synced_price': None,
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
                    (row[1] + pnl, row[2] + w, row[3] + l, today))
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


# 🧭 قائمة الأزواج المستبعدة من HMA (اعتماد المالك):
# خاسرة مزمنة على النافذتين المستقلتين معاً (IS وOOS) — قاعدة النافذتين
# (لا استبعاد بلإحصاء نافذة واحدة = لا fitting).
# صفقات HMA المفتوحة سابقاً على هذه الأزواج تُدار بمخارجها حتى الإغلاق —
# الفلتر يمنع الإشارات الجديدة فقط.
HMA_SYMBOL_BLACKLIST = ('ETHUSDT', 'BNBUSDT', 'AVAXUSDT')

# 🌙 حظر نافذة المساء (اعتماد المالك — نتيجة تقرير تشخيص HMA على 30 يوماً):
# الدخول الجديد معطل بين 16:00 و23:59 UTC — النافذة الأكثر خسارة موثقاً
# في التشخيص. إدارة المخارج (صفقات HMA المفتوحة) تعمل طوال اليوم كالمعتاد.
# للتعطيل: HMA_BLOCK_EVENING=false | للتخصيص: HMA_EVENING_START_UTC/END
HMA_BLOCK_EVENING_UTC = os.environ.get('HMA_BLOCK_EVENING', 'true').lower() != 'false'
HMA_EVENING_START_UTC = int(os.environ.get('HMA_EVENING_START_UTC', '16'))
HMA_EVENING_END_UTC = int(os.environ.get('HMA_EVENING_END_UTC', '23'))

# 🔭 ثوابت المسح (كانت ضمن إعدادات القناص المحذوف — نفس القيم حرفياً)
HMA_SCAN_MIN_VOL_USDT = float(os.environ.get('HMA_SCAN_MIN_VOL_USDT', '30000000'))
HMA_UNIVERSE_POOL = int(os.environ.get('HMA_UNIVERSE_POOL', '150'))
HMA_MAX_SPREAD_PCT = float(os.environ.get('HMA_MAX_SPREAD_PCT', '0.15'))


class RiskManager:
    """
    حماية رأس المال — لا يمكن تجاوزها بإعادة تشغيل البوت لأن حالتُها
    تُحفظ في القاعدة وتُستعاد عند الإقلاع:
    - 3 خسائر متتالية → توقف 4 ساعات
    - 3 خسائر في اليوم → توقف بقية اليوم
    - سحب يومي 5% من الرصيد المرجعي → توقف بقية اليوم
    """
    MAX_CONSEC_LOSSES = 3
    PAUSE_HOURS = 4
    MAX_DAILY_LOSSES = 3
    MAX_DAILY_DRAWDOWN_PCT = 5.0

    def __init__(self, db=None):
        self.db = db
        self.consecutive_losses = 0
        self.daily_losses = 0
        self.daily_pnl = 0.0
        self.initial_balance = 0.0
        self.pause_until = 0.0
        self._day = time.strftime('%Y-%m-%d')

    def _rollover_day(self):
        today = time.strftime('%Y-%m-%d')
        if today != self._day:
            self._day = today
            self.daily_losses = 0
            self.daily_pnl = 0.0

    async def load(self):
        if not self.db:
            return
        raw = await self.db.get_param('risk_state')
        if not raw:
            return
        try:
            d = json.loads(raw)
            if d.get('day') == self._day:      # حالة أمس لا تُستعاد (إعادة ضبط يومية سليمة)
                self.consecutive_losses = max(0, int(d.get('consecutive_losses', 0)))
                self.daily_losses = max(0, int(d.get('daily_losses', 0)))
                self.daily_pnl = float(d.get('daily_pnl', 0.0))
                self.pause_until = float(d.get('pause_until', 0.0))
                self.initial_balance = float(d.get('initial_balance', 0.0))
                if self.pause_until > time.time():
                    mins = int((self.pause_until - time.time()) / 60)
                    logger.warning(f"🛡️ مدير المخاطر: استئناف إيقاف قائم — يتبقى {mins} دقيقة")
        except Exception as e:
            logger.warning(f"تعذر استعادة حالة مدير المخاطر: {e}")

    async def save(self):
        if not self.db:
            return
        try:
            await self.db.set_param('risk_state', json.dumps({
                'day': self._day,
                'consecutive_losses': self.consecutive_losses,
                'daily_losses': self.daily_losses,
                'daily_pnl': self.daily_pnl,
                'pause_until': self.pause_until,
                'initial_balance': self.initial_balance,
            }))
        except Exception as e:
            logger.warning(f"تعذر حفظ حالة مدير المخاطر: {e}")

    async def register_result(self, pnl):
        """تسجيل نتيجة صفقة مغلقة + حفظ الحالة فوراً."""
        self._rollover_day()
        pnl = float(pnl or 0.0)
        self.daily_pnl += pnl
        if pnl < 0:
            self.consecutive_losses += 1
            self.daily_losses += 1
            if self.consecutive_losses >= self.MAX_CONSEC_LOSSES:
                self.pause_until = time.time() + self.PAUSE_HOURS * 3600
                logger.warning(f"🛡️ {self.MAX_CONSEC_LOSSES} خسائر متتالية — توقف {self.PAUSE_HOURS} ساعات")
        elif pnl > 0:
            self.consecutive_losses = 0
        await self.save()

    def can_trade(self):
        """يعيد (مسموح؟، السبب) — يُعرض في اللوحة مباشرة."""
        self._rollover_day()
        now = time.time()
        if now < self.pause_until:
            mins = int((self.pause_until - now) / 60)
            return False, f"⏸️ توقف بعد {self.MAX_CONSEC_LOSSES} خسائر متتالية — يستأنف بعد {mins} دقيقة"
        if self.daily_losses >= self.MAX_DAILY_LOSSES:
            return False, f"🛑 تحقق الحد اليومي ({self.MAX_DAILY_LOSSES} خسائر) — توقف بقية اليوم"
        if (self.initial_balance > 0 and self.daily_pnl < 0
                and abs(self.daily_pnl) >= self.initial_balance * self.MAX_DAILY_DRAWDOWN_PCT / 100):
            return False, f"🛑 سحب يومي {self.MAX_DAILY_DRAWDOWN_PCT}% — توقف بقية اليوم"
        return True, "✅ مسموح"


# ═══════════════════════ فلتر الأخبار (كما هو — مُدار من اللوحة) ═══════════════════════
class NewsFilter:
    """
    فلتر حقيقي بمصدر حي: تقويم ForexFactory الأسبوعي (JSON مجاني بدون مفتاح)
    - يُجلب كل 4 ساعات ويشمل CPI/FOMC/NFP وكل أحداث الماكرو المؤثرة
    - كتم الإشارات تلقائياً قبل/بعد الأحداث المطابقة (تأثير + عملة)
    - كل الإعدادات في قاعدة البيانات → تُعدّل من اللوحة لحظياً
    - نوافذ يدوية إضافية بتوقيت UTC "HH:MM-HH:MM,..." (اختياري)
    - فشل الجلب لا يوقف التداول (Fail-open) وحالة الجلب تُعرض في اللوحة
    - تعطيله من اللوحة يعني عدم كتم أي إشارة أبداً (كما هو متوقع)
    """
    CALENDAR_URL = 'https://nfs.faireconomy.media/ff_calendar_thisweek.json'
    CALENDAR_TTL = 4 * 3600
    IMPACT_RANK = {'Holiday': 0, 'Low': 1, 'Medium': 2, 'High': 3}

    def __init__(self, db=None):
        self.db = db
        self.enabled = True
        self.impact_min = 'High'
        self.currencies = 'USD'
        self.before_min = 30
        self.after_min = 30
        self.blackout_windows = []
        self.events = []
        self.calendar_updated = 0.0
        self.last_fetch_ok = False
        self.last_error = None
        self.rejected_total = 0

    async def load(self):
        raw = None
        if self.db:
            raw = await self.db.get_param('news_filter')
        if raw:
            try:
                d = json.loads(raw)
                self.enabled = bool(d.get('enabled', True))
                self.impact_min = d.get('impact_min', 'High')
                self.currencies = d.get('currencies', 'USD')
                self.before_min = max(0, min(240, int(d.get('before_min', 30))))
                self.after_min = max(0, min(240, int(d.get('after_min', 30))))
                self.blackout_windows = self._parse(d.get('windows', ''))
                self.rejected_total = int(d.get('rejected_total', 0))
                logger.info(f"📰 فلتر الأخبار محمّل: "
                            f"{'مفعّل' if self.enabled else 'معطل'} | تأثير≥{self.impact_min} | "
                            f"±{self.before_min}/{self.after_min}د | عملات: {self.currencies}")
            except Exception as e:
                logger.warning(f"تعذر تحميل إعدادات فلتر الأخبار (افتراضيات): {e}")
        else:
            env = os.environ.get('NEWS_FILTER_ENABLED', '').lower()
            if env == 'true':
                self.enabled = True
            await self.save()

    async def save(self):
        if not self.db:
            return
        try:
            await self.db.set_param('news_filter', json.dumps({
                'enabled': self.enabled, 'impact_min': self.impact_min,
                'currencies': self.currencies, 'before_min': self.before_min,
                'after_min': self.after_min, 'windows': self.windows_spec(),
                'rejected_total': self.rejected_total}))
        except Exception as e:
            logger.warning(f"تعذر حفظ إعدادات فلتر الأخبار: {e}")

    @staticmethod
    def _parse(spec):
        out = []
        for part in (spec or '').split(','):
            part = part.strip()
            if '-' not in part:
                continue
            try:
                a, b = part.split('-')
                ah, am = map(int, a.split(':'))
                bh, bm = map(int, b.split(':'))
                out.append((ah * 60 + am, bh * 60 + bm))
            except Exception:
                continue
        return out

    def windows_spec(self):
        return ','.join(f"{s // 60:02d}:{s % 60:02d}-{e // 60:02d}:{e % 60:02d}"
                        for s, e in self.blackout_windows)

    def set_windows(self, spec):
        self.blackout_windows = self._parse(spec)

    @property
    def currencies_list(self):
        return [c.strip().upper() for c in (self.currencies or '').split(',') if c.strip()]

    async def refresh_calendar(self):
        try:
            def _fetch():
                r = requests.get(self.CALENDAR_URL, timeout=20,
                                 headers={'User-Agent': 'Mozilla/5.0'})
                r.raise_for_status()
                return r.json()
            data = await asyncio.to_thread(_fetch)
            events = []
            for e in (data if isinstance(data, list) else []):
                try:
                    title = str(e.get('title', '')).strip()[:90]
                    cur = str(e.get('country', '')).strip().upper()
                    impact = str(e.get('impact', '')).strip()
                    dstr = str(e.get('date', '')).strip()
                    if not title or not dstr or not cur:
                        continue
                    ts = datetime.fromisoformat(dstr).timestamp()
                    events.append({'title': title, 'cur': cur, 'impact': impact, 'ts': ts})
                except Exception:
                    continue
            self.events = sorted(events, key=lambda x: x['ts'])
            self.calendar_updated = time.time()
            self.last_fetch_ok = True
            self.last_error = None
            logger.info(f"📰 تقويم الأخبار محدّث: {len(self.events)} حدثاً هذا الأسبوع")
            return True, f"{len(self.events)} حدثاً"
        except Exception as e:
            self.last_fetch_ok = False
            self.last_error = str(e)[:140]
            logger.warning(f"تعذر جلب تقويم الأخبار (لا يوقف التداول): {e}")
            return False, self.last_error

    def _match_events(self):
        rank_min = self.IMPACT_RANK.get(self.impact_min, 3)
        curs = set(self.currencies_list) or {'USD'}
        return [e for e in self.events
                if e['cur'] in curs and self.IMPACT_RANK.get(e['impact'], 0) >= rank_min]

    def next_event(self):
        now_ts = time.time()
        upcoming = [e for e in self._match_events()
                    if e['ts'] >= now_ts - self.after_min * 60]
        return upcoming[0] if upcoming else None

    def is_blocked_now(self):
        """يعيد (محظور؟، السبب) — السبب يُعرض في اللوحة والإشعارات."""
        if not self.enabled:
            return False, 'الفلتر معطل من اللوحة'
        t = time.gmtime()
        now_min = t.tm_hour * 60 + t.tm_min
        for start, end in self.blackout_windows:
            if start <= now_min <= end:
                return True, f'نافذة أخبار يدوية {self.windows_spec()} (UTC)'
        if not self.events:
            if self.last_error:
                return False, 'تعذر جلب التقويم — التداول مستمر'
            return False, 'بانتظار جلب التقويم...'
        now_ts = time.time()
        for ev in self._match_events():
            if ev['ts'] - self.before_min * 60 <= now_ts <= ev['ts'] + self.after_min * 60:
                mins = int(abs(now_ts - ev['ts']) / 60)
                when = f'بعد {mins} دقيقة' if now_ts < ev['ts'] else f'قبل {mins} دقيقة'
                return True, (f"📰 {ev['title']} ({ev['cur']} — {ev['impact']}) {when}")
        return False, 'لا أحداث مؤثرة الآن'

    def status(self):
        nxt = self.next_event()
        blocked, reason = self.is_blocked_now()
        return {
            'enabled': self.enabled,
            'impact_min': self.impact_min,
            'currencies': self.currencies,
            'before_min': self.before_min,
            'after_min': self.after_min,
            'windows': self.windows_spec(),
            'blocked_now': blocked,
            'reason': reason,
            'next_event': ({'title': nxt['title'], 'cur': nxt['cur'], 'impact': nxt['impact'],
                            'in_min': max(0, int((nxt['ts'] - time.time()) / 60)),
                            'time': libya_time_str(nxt['ts']) + ' بتوقيت ليبيا'}
                           if nxt else None),
            'calendar_updated': int(self.calendar_updated),
            'calendar_age_min': (int((time.time() - self.calendar_updated) / 60)
                                 if self.calendar_updated else None),
            'events_count': len(self.events),
            'last_fetch_ok': self.last_fetch_ok,
            'last_error': self.last_error,
            'rejected_total': self.rejected_total,
        }


# ═══════════════════════════════════════════════════════════════════
HMA_STRATEGY_NAME = 'HMA_DMI_MOMENTUM'


class HMASettings:
    """
    كل عتبات استراتيجية HMA_DMI_MOMENTUM في مكان واحد:
    - عند أول تشغيل تُبذر من متغيرات Railway (HMA_MIN_POWER ... إلخ) ثم تُحفظ
      في القاعدة (مفتاح bot_params: hma_settings) — وبعدها القاعدة هي المرجع
      (تعديل اللوحة لحظي ويصمد لإعادة التشغيل).
    - القيم الافتراضية هي القيم المطلوبة من المالك: HMA 8/21 | DI 7 + تنعيم
      ADX 6 | زخم 2/5/9 | ER 10 | بنية 5 | Supertrend ATR14 ×1.35 | قوة ≥24
      | ثقة ≥5 | ADX قوي 20 | ER قوي 0.25 | تأكيد زخم ≥2 | مدة حالة 3 شموع
      | تبريد 3 شموع | انقلاب 0.60×ATR | استثناء هيكلي: قوة 12 / ثقة 4 /
      ADX 18.
    - V11.3 (اعتماد المالك): حقلا بوابة اتجاه 4 ساعات T3 —
      trend4h_enabled (1=مفعّلة افتراضياً) وtrend4h_ema_len (EMA50 على 4س).
      حقول جديدة كلياً: القاعدة القديمة بلا مفتاحين يبذر افتراضيهما تلقائياً
      عند التحميل (لا حاجة لترحيل قيم).
    - timeframe سلسلة تُدار خارج FIELDS (قيم مسموحة: 5m/15m/1h — الافتراضي 15m).
    """
    TIMEFRAMES = ('5m', '15m', '1h')
    TF_MS = {'5m': 300000, '15m': 900000, '1h': 3600000}

    FIELDS = {
        # الاسم: (النوع، الافتراضي، الأدنى، الأعلى، متغير Railway)
        'hma_fast':          (int,   8,    4,    50,   'HMA_FAST'),
        'hma_slow':          (int,   21,   10,   200,  'HMA_SLOW'),
        'di_period':         (int,   7,    3,    30,   'HMA_DI_PERIOD'),
        'adx_smooth':        (int,   6,    3,    30,   'HMA_ADX_SMOOTH'),
        'mom_fast':          (int,   2,    1,    20,   'HMA_MOM_FAST'),
        'mom_mid':           (int,   5,    2,    40,   'HMA_MOM_MID'),
        'mom_slow':          (int,   9,    3,    60,   'HMA_MOM_SLOW'),
        'er_period':         (int,   10,   5,    50,   'HMA_ER_PERIOD'),
        'struct_period':     (int,   5,    3,    20,   'HMA_STRUCT_PERIOD'),
        'st_atr_period':     (int,   14,   5,    50,   'HMA_ST_ATR_PERIOD'),
        'st_mult':           (float, 1.35, 0.5,  5.0,  'HMA_ST_MULT'),
        'ema_period':        (int,   200,  50,   400,  'HMA_EMA_PERIOD'),
        'ema_filter':        (int,   0,    0,    1,    'HMA_EMA_FILTER'),
        'min_power':         (float, 24.0, 0.0,  100.0,'HMA_MIN_POWER'),
        'min_confidence':    (int,   5,    0,    9,    'HMA_MIN_CONFIDENCE'),
        'strong_adx':        (float, 20.0, 5.0,  50.0, 'HMA_STRONG_ADX'),
        'strong_er':         (float, 0.25, 0.05, 0.9,  'HMA_STRONG_ER'),
        'min_mom_conf':      (int,   2,    1,    3,    'HMA_MIN_MOM_CONF'),
        'min_state_candles': (int,   3,    1,    20,   'HMA_MIN_STATE_CANDLES'),
        'cooldown_candles':  (int,   3,    0,    30,   'HMA_COOLDOWN_CANDLES'),
        'reversal_atr':      (float, 0.60, 0.1,  5.0,  'HMA_REVERSAL_ATR'),
        'so_power':          (float, 12.0, 0.0,  100.0,'HMA_SO_POWER'),
        'so_confidence':     (int,   4,    0,    9,    'HMA_SO_CONFIDENCE'),
        'so_adx':            (float, 18.0, 5.0,  50.0, 'HMA_SO_ADX'),
        'adx_gate':          (float, 20.0, 0.0,  50.0, 'HMA_ADX_GATE'),
        'sl_atr_mult':       (float, 2.0,  0.3,  6.0,  'HMA_SL_ATR'),
        'risk_min_pct':      (float, 0.15, 0.05, 2.0,  'HMA_RISK_MIN_PCT'),
        'risk_max_pct':      (float, 3.5,  0.5,  10.0, 'HMA_RISK_MAX_PCT'),
        'min_rr':            (float, 1.2,  0.5,  5.0,  'HMA_MIN_RR'),
        'tp1_return_pct':    (float, 30.0, 1.0,  100.0,'HMA_TP1_RETURN_PCT'),
        'tp1_max_atr':       (float, 4.0,  1.0,  20.0, 'HMA_TP1_MAX_ATR'),
        'universe_size':     (int,   40,   10,   200,  'HMA_UNIVERSE_SIZE'),
        'batch_size':        (int,   12,   4,    60,   'HMA_BATCH_SIZE'),
        'parallel':          (int,   4,    1,    10,   None),
        'max_signals_per_scan': (int, 1,  1,    3,    None),
        # 🧭 V11.3 — بوابة اتجاه 4 ساعات (اعتماد المالك T3): الإشارة تُقبل فقط
        # إذا حاذى اتجاه آخر شمعة 4س مغلقة كلياً (EMA على 4س + ميلها) الإشارة.
        'trend4h_enabled':   (int,   1,    0,    1,    None),
        'trend4h_ema_len':   (int,   50,   20,   200,  None),
    }
    LABELS = {
        'hma_fast': 'HMA السريعة',
        'hma_slow': 'HMA البطيئة',
        'di_period': 'فترة DI',
        'adx_smooth': 'تنعيم ADX',
        'mom_fast': 'زخم سريع',
        'mom_mid': 'زخم متوسط',
        'mom_slow': 'زخم بطيء',
        'er_period': 'فترة كفاءة الحركة ER',
        'struct_period': 'فترة بنية السوق (تأكيد القمم/القيعان)',
        'st_atr_period': 'فترة ATR لـ Supertrend',
        'st_mult': 'معامل ATR لـ Supertrend',
        'ema_period': 'فترة EMA (فلتر الاتجاه)',
        'ema_filter': 'فلتر EMA200 (1=مفعّل 0=معطل)',
        'min_power': 'أدنى قوة دخول (0-100)',
        'min_confidence': 'أدنى ثقة دخول (0-9)',
        'strong_adx': 'عتبة ADX القوي',
        'strong_er': 'عتبة ER القوي',
        'min_mom_conf': 'أدنى تأكيدات الزخم (1-3)',
        'min_state_candles': 'أدنى مدة الحالة (شموع مغلقة)',
        'cooldown_candles': 'تبريد الإشارات/التبدّل (شموع)',
        'reversal_atr': 'عتبة الانقلاب (×ATR)',
        'so_power': 'قوة الاستثناء الهيكلي',
        'so_confidence': 'ثقة الاستثناء الهيكلي',
        'so_adx': 'ADX للاستثناء الهيكلي',
        'adx_gate': 'بوابة اتجاهية ADX-14 عند الدخول (0=معطلة)',
        'sl_atr_mult': 'الستوب (×ATR)',
        'risk_min_pct': 'أدنى مسافة ستوب (%)',
        'risk_max_pct': 'أقصى مسافة ستوب (%)',
        'min_rr': 'أدنى عائد/مخاطرة (R:R)',
        'tp1_return_pct': 'هدف TP1 (% من الهامش)',
        'tp1_max_atr': 'أقصى مسافة TP1 واقعية (×ATR)',
        'universe_size': 'حجم كون HMA (أعلى سيولة)',
        'batch_size': 'عدد العملات المفحوصة كل دورة',
        'parallel': 'تحليلات متوازية',
        'max_signals_per_scan': 'أقصى إشارات منفذة في الدورة',
        'trend4h_enabled': 'بوابة اتجاه 4 ساعات T3 (1=مفعّلة 0=معطلة)',
        'trend4h_ema_len': 'فترة EMA لبوابة 4 ساعات (على شموع 4س مغلقة)',
    }

    VERSION = 3   # 🧭 V11.3: حقلا بوابة 4س جددان — افتراضاهما يُبزران تلقائياً
    V1_DEFAULTS = {'sl_atr_mult': 1.5, 'tp1_return_pct': 20.0}   # الافتراضي القديم (V11.0)
    V1_TO_V2 = {'sl_atr_mult': 2.0, 'tp1_return_pct': 30.0}      # الترقية: U4 المُتحقق عليه

    def _upgrade_v1_to_v2(self, stored):
        """ترقية موثقة لإعدادات HMA محفوظة من V11.0: يُحدَّث فقط ما بقي على
        الافتراضي القديم (لم يخصصه المالك)، والقيم المخصصة تبقى كما هي.
        يشمل الإطار: '15m' (الافتراضي القديم) → '1h'، وما هو مخصص يبقى.
        بوابة ADX حقل جديد يُبذر افتراضه 20.0 تلقائياً (ليس في القاعدة القديمة).
        V11.3: حقلا بوابة 4س جديدان كلياً — يُبزران من FIELDS تلقائياً عند
        غيابهما عن القاعدة (بلا ترحيل قيم)، وسلسلة الترقية v1→v2 هنا آمنة
        و idempotent (تُستدعى لأي إصدار محفوظ أقدم من VERSION الحالي)."""
        changed = []
        for k, new_v in self.V1_TO_V2.items():
            old_v = self.V1_DEFAULTS.get(k)
            try:
                cur = float(getattr(self, k))
            except Exception:
                continue
            if old_v is not None and abs(cur - float(old_v)) <= 1e-12:
                setattr(self, k, new_v)
                changed.append(f'{k}: {old_v:g}←{new_v:g}')
        # 🧭 ترقية الإطار: فقط إن بقي على الافتراضي القديم 15د
        stored_tf = (stored or {}).get('timeframe', '15m')
        if str(stored_tf) == '15m' and self.timeframe == '15m':
            self.timeframe = '1h'
            changed.append('timeframe: 15m←1h')
        if changed:
            logger.info("🧭 ترقية إعدادات HMA إلى v2 (الافتراضيات المعاد ضبطها فقط): "
                        + ", ".join(changed))

    def __init__(self, db=None):
        self.db = db
        self.timeframe = '1h'    # 🧭 V11.1: الإشارات على شموع ساعة مغلقة (أفضلية مُثبتة — راجع تقرير إعادة البناء)
        self.env_conflicts = []
        for k, spec in self.FIELDS.items():
            setattr(self, k, spec[1])

    def set_timeframe(self, tf):
        if tf in self.TIMEFRAMES and tf != self.timeframe:
            self.timeframe = tf
            return True
        return False

    def as_params(self):
        """قاموس معاملات المحرك النقي (struct_w = نافذة تأكيد القمة/القاع)."""
        p = {k: getattr(self, k) for k in self.FIELDS}
        p['struct_w'] = max(1, int(self.struct_period) // 2)
        return p

    async def load(self):
        self.env_conflicts = []
        raw = None
        if self.db:
            raw = await self.db.get_param('hma_settings')
        if raw:
            try:
                d = json.loads(raw)
                self.apply(d)
                # 🔄 ترقية الإعدادات القديمة (v1→v2): الافتراضيات المعاد ضبطها فقط
                if int(d.get('version', 1) or 1) < self.VERSION:
                    self._upgrade_v1_to_v2(d)
                    await self.save()
                self._collect_env_conflicts()
                logger.info(f"🧭 إعدادات HMA_DMI_MOMENTUM محمّلة من القاعدة: {self.describe()}")
                if self.env_conflicts:
                    logger.warning("⚠️ تعارض إعدادات HMA: متغيرات Railway تختلف عن القيم الفعالة "
                                   "(القاعدة هي المرجع بعد أول تشغيل) — الاستيراد من اللوحة")
            except Exception as e:
                logger.warning(f"تعذر تحميل إعدادات HMA (افتراضيات): {e}")
        else:
            seeded = {}
            for k, spec in self.FIELDS.items():
                env = spec[4]
                if env and os.environ.get(env) not in (None, ''):
                    try:
                        val = float(os.environ[env])
                        seeded[k] = val if spec[0] is float else int(val)
                    except (TypeError, ValueError):
                        logger.warning(f"قيمة HMA غير صالحة لـ {env}: {os.environ[env]}")
            self.apply(seeded)
            env_tf = os.environ.get('HMA_TIMEFRAME', '')
            if env_tf in self.TIMEFRAMES:
                self.timeframe = env_tf
            await self.save()
            if seeded:
                logger.info(f"🧭 إعدادات HMA مبذورة من متغيرات Railway: {sorted(seeded.keys())}")
            logger.info(f"🧭 إعدادات HMA النشطة: {self.describe()}")

    def apply(self, d):
        for k, v in (d or {}).items():
            if k == 'timeframe':
                self.set_timeframe(str(v))
                continue
            if k not in self.FIELDS:
                continue
            t, _, lo, hi, _ = self.FIELDS[k]
            try:
                x = float(v)
                x = t(x) if t is float else int(x)
            except (TypeError, ValueError):
                continue
            setattr(self, k, x)
        self._clamp()

    def _clamp(self):
        for k, (_, _, lo, hi, _) in self.FIELDS.items():
            try:
                v = float(getattr(self, k))
                setattr(self, k, max(lo, min(hi, v)))
            except Exception:
                setattr(self, k, self.FIELDS[k][1])
        for k, spec in self.FIELDS.items():
            if spec[0] is int:
                setattr(self, k, int(getattr(self, k)))

    def update(self, d):
        """من اللوحة: تحديث مجموعة إعدادات — يعيد قائمة التغييرات."""
        changed = []
        if 'timeframe' in (d or {}):
            old_tf = self.timeframe
            if self.set_timeframe(str(d['timeframe'])):
                changed.append(f"الإطار الزمني: {old_tf} ← {self.timeframe}")
        for k in self.FIELDS:
            if k not in (d or {}):
                continue
            try:
                old = getattr(self, k)
                new_raw = float(d[k])
                new = new_raw if self.FIELDS[k][0] is float else int(new_raw)
                if abs(float(new) - float(old)) > 1e-9:
                    changed.append(f"{self.LABELS.get(k, k)}: {old:g} ← {new:g}")
                    setattr(self, k, new)
            except (TypeError, ValueError):
                continue
        self._clamp()
        return changed

    async def save(self):
        if not self.db:
            return
        try:
            await self.db.set_param('hma_settings', json.dumps(self.status()))
        except Exception as e:
            logger.warning(f"تعذر حفظ إعدادات HMA: {e}")

    def _collect_env_conflicts(self):
        """كشف متغيرات Railway التي تختلف عن القيمة الفعالة — عرض فقط."""
        self.env_conflicts = []
        for k, spec in self.FIELDS.items():
            env = spec[4]
            if not env or os.environ.get(env) in (None, ''):
                continue
            try:
                ev = float(os.environ[env])
                cur = float(getattr(self, k))
            except (TypeError, ValueError):
                continue
            if abs(ev - cur) > 1e-9:
                self.env_conflicts.append({'field': k, 'env': env,
                                           'env_value': ev, 'active_value': cur,
                                           'label': self.LABELS.get(k, k)})

    def status(self):
        out = {k: getattr(self, k) for k in self.FIELDS}
        out['timeframe'] = self.timeframe
        out['version'] = self.VERSION
        return out

    def describe(self):
        gate = (f"بوابة 4س EMA{int(self.trend4h_ema_len)}+ميل ✓"
                if self.trend4h_enabled else "بوابة 4س معطلة")
        return (f"HMA {self.hma_fast}/{self.hma_slow} | DI {self.di_period}/ADX {self.adx_smooth} | "
                f"زخم {self.mom_fast}/{self.mom_mid}/{self.mom_slow} | ER {self.er_period} | "
                f"ST {self.st_atr_period}×{self.st_mult:g} | قوة≥{self.min_power:g} ثقة≥{self.min_confidence} | "
                f"بوابة ADX≥{self.adx_gate:g} | {gate} | {self.timeframe} | TP1={self.tp1_return_pct:g}% | "
                f"R:R≥{self.min_rr:g} | EMA200 {'مفعّل' if self.ema_filter else 'معطل'}")


# ═══════════════════ بوابة اتجاه 4 ساعات (V11.3 — اعتماد T3) ═══════════════════
def _trend_4h(df, mode='ema_slope', ema_len=50):
    """🧭 سلسلة اتجاه الإطار الأكبر (4 ساعات) مشتقة من شموع 1س مغلقة.
    نسخة مطابقة للفرعين المعتمدين (ema/ema_slope) من backtest._trend_4h
    — لضمان تطابق البوت الحي مع الباكتيست معاملياً (يُختبر تطابق المصفوفتين
    حرفياً في test_strategies.py). بلا إعادة رسم:
    لكل شمعة ساعة i يُستخدم آخر شمعة 4س **مغلقة كلياً** لحظة إغلاق i فقط
    (الشمعة 4س الجارية لا تُلمس أبداً — نفس مبدأ الشموع المغلقة في المحرك).
    يعيد مصفوفة اتجاه لكل شمعة 1س: ‎+1 صاعد | ‎−1 هابط | 0 محايد/غير جاهز.
    الأنماط:
      ema      — السعر (إغلاق المجموعة 4س) فوق/تحت EMA(ema_len) على 4س
      ema_slope— كالسابق + ميل EMA صاعد/هابط عبر آخر 3 شموع 4س مغلقة (T3)
    (أنماط dmi/dmi_adx/both موجودة في backtest.py للبحث فقط — لم يُعتمد منها شيء).
    ملاحظة الحجم: 700 شمعة 1س = 175 مجموعة 4س — وزن بذرة EMA50 المتبقي
    ≈ 0.09% (هامش مهمل مقابل تاريخ الباكتيست الأطول)."""
    n = len(df)
    t_close = pd.to_numeric(df['time']).to_numpy() + 3600_000   # لحظة إغلاق شمعة الساعة
    c_ = df['close'].to_numpy(dtype=float)
    G = 4 * 3600_000
    gid = (t_close // G).astype(int)          # عدد مجموعات 4س المكتملة عند إغلاق i
    n_groups = int(gid[-1])                   # آخر مجموعة مكتملة في كامل البيانات
    if n_groups < max(ema_len + 5, 30):
        return np.zeros(n, dtype=int)         # بيانات غير كافية — بوابة محايدة
    g_close = np.full(n_groups, np.nan)
    # إغلاق كل مجموعة 4س = إغلاق آخر شمعة 1س أُغلقت داخلها (بلا مستقبل)
    starts = np.searchsorted(t_close, np.arange(n_groups) * G, side='left')
    ends = np.searchsorted(t_close, (np.arange(n_groups) + 1) * G, side='left')
    for g in range(n_groups):
        if ends[g] > starts[g]:
            g_close[g] = c_[ends[g] - 1]
    valid = ~np.isnan(g_close)
    trend_g = np.zeros(n_groups, dtype=int)
    ema = pd.Series(g_close).ewm(span=ema_len, adjust=False).mean().to_numpy()
    for g in range(n_groups):
        if not valid[g]:
            continue
        e = ema[g]
        if not np.isfinite(e):
            continue
        up = g_close[g] > e
        down = g_close[g] < e
        if mode == 'ema_slope' and g >= 2:
            up = up and e > ema[g - 2]
            down = down and e < ema[g - 2]
        if up and not down:
            trend_g[g] = 1
        elif down and not up:
            trend_g[g] = -1
    # خريطة المجموعة → شموع الساعة: trend[i] = اتجاه آخر مجموعة مكتملة عند إغلاق i
    trend = trend_g[np.clip(gid - 1, 0, n_groups - 1)]
    return trend


# ═════════════════════════════════════════════════════════════════════════
# 🧭 محرك HMA_DMI_MOMENTUM — الاستراتيجية الوحيدة في هذا البوت
# ═════════════════════════════════════════════════════════════════════════
# مبادئ صارمة (مُختبرة في test_strategies.py):
#  1) شموع مغلقة فقط — المتصل يمرر DataFrame حُذفت منه الشمعة الجارية.
#  2) لا بيانات مستقبلية: كل المؤشرات متتالية خلفية (causal) — قيمة الشمعة i
#     تعتمد على الشموع ≤ i فقط (مُختبر بمقارنة الحساب على بادئات متزايدة).
#  3) القمم/القيعان الهيكلية لا تُستخدم قبل تأكيدها (تحتاج w شموع مغلقة
#     بعد القمة/القاع — تأخير التأكيد موثق: w = struct_period // 2 = 2).
#  4) آلة حالات NEUTRAL/BULL/BEAR قابلة لإعادة البناء الحتمي من الشموع
#     المغلقة نفسها — إعادة تشغيل البوت لا تغيّر الحالة (بلا حالة مخزنة
#     تتقادم) — إعادة تشغيل (replay) ثابتة على آخر REPLAY_BARS شمعة.
#  5) الدوال نقية (بلا شبكة/حالة خارجية) لتكون قابلة للاختبار المباشر.
#
# تعريفات موثقة للقياص الحسابية:
#  - Entry Power (0-100) لكل اتجاه = مجموع مكونات مرجّحة:
#      HMA (20): انحياز السريعة/البطيئة 14 + ميل السريعة 6
#      DMI/ADX (20): هيمنة DI 12 + ADX ≥ strong_adx 5 + ADX صاعد 3
#      الزخم (15): كل ROC من (2/5/9) بالاتجاه 5 (بحد 15)
#      ER (10): ER ≥ strong_er → 10، وإلا ER ≥ نصف العتبة → 5
#      Supertrend (15): انحياز الاتجاه
#      البنية (20): البنية السليمة (الإغلاق فوق آخر قاع مؤكد للشراء /
#                   تحت آخر قمة مؤكدة للبيع)
#  - Entry Confidence (0-9) = عدد التأكيدات المستقلة المحققة:
#      1 انحياز HMA | 2 ميل HMA | 3 هيمنة DI | 4 ADX قوي | 5 زخم ≥
#      min_mom_conf | 6 ER قوي | 7 Supertrend | 8 بنية سليمة |
#      9 EMA (يُحتسب فقط عند تفعيل الفلتر — بلا فلتر الحد الأعلى 8)
#  - الزناد (على شمعة مغلقة): استعادة HMA السريعة (تقاطع) أو استئناف بعد
#      ارتداد من HMA البطيئة (لمس خلال آخر 3 شموع + شمعة إغلاق مؤكدة).
#  - الاستثناء الهيكلي (محدود): يخفّض العتبتين فقط عند كسر إغلاقٍ لقمة/قاع
#      مؤكد بعمق ≥ reversal_atr×ATR مع ADX ≥ so_adx وهيمنة DI وتأكيد زخم
#      ≥1 — ولا يتجاوز: آلة الحالات (NEUTRAL لا يُتداول)، التبريد، فلتر
#      EMA، ولا أي بوابة مخاطر/تعارض.
# ═════════════════════════════════════════════════════════════════════════
class HmaDmiMomentumEngine:
    NAME = HMA_STRATEGY_NAME
    REPLAY_BARS = 160          # نافذة إعادة بناء الحالة (ثابتة → حتمية)
    STATE_NAMES = {0: 'NEUTRAL', 1: 'BULL', -1: 'BEAR'}

    # ─── المؤشرات الأساسية (كلها متتالية خلفية — بلا تسرب مستقبلي) ───
    @staticmethod
    def _wma(a, period):
        """المتوسط المتحرك المرجح — NaN قبل اكتمال أول نافذة."""
        a = np.asarray(a, dtype=float)
        n = len(a)
        out = np.full(n, np.nan)
        if period <= 0 or n < period:
            return out
        w = np.arange(1, period + 1, dtype=float)
        w = w / w.sum()
        out[period - 1:] = np.convolve(a, w[::-1], mode='valid')
        return out

    @classmethod
    def _hma(cls, a, period):
        """Hull MA = WMA(2×WMA(n/2) − WMA(n), √n)."""
        a = np.asarray(a, dtype=float)
        half = max(1, int(period) // 2)
        sq = max(1, int(math.sqrt(max(1, int(period)))))
        raw = 2.0 * cls._wma(a, half) - cls._wma(a, period)
        return cls._wma(raw, sq)

    @staticmethod
    def _ema(a, period):
        a = np.asarray(a, dtype=float)
        n = len(a)
        out = np.full(n, np.nan)
        if n < period or period <= 0:
            return out
        k = 2.0 / (period + 1.0)
        out[period - 1] = float(np.mean(a[:period]))
        for i in range(period, n):
            out[i] = out[i - 1] + k * (a[i] - out[i - 1])
        return out

    @staticmethod
    def _true_range(h, l, c):
        prev_c = np.roll(c, 1)
        prev_c[0] = c[0]
        return np.maximum(h - l, np.maximum(np.abs(h - prev_c), np.abs(l - prev_c)))

    @staticmethod
    def _rma(x, period, start_idx=0):
        """تنعيم وايلدر (RMA): أول قيمة = متوسط بسيط لأول نافذة صالحة،
        ثم out[i] = (out[i-1]×(p-1) + x[i]) / p — متتالية خلفية بحتة."""
        x = np.asarray(x, dtype=float)
        n = len(x)
        out = np.full(n, np.nan)
        s = start_idx + period
        if period <= 0 or n < s:
            return out
        out[s - 1] = float(np.mean(x[start_idx:s]))
        for i in range(s, n):
            out[i] = (out[i - 1] * (period - 1) + x[i]) / period
        return out

    @classmethod
    def _wilder_atr(cls, h, l, c, period):
        return cls._rma(cls._true_range(h, l, c), period, start_idx=0)

    @classmethod
    def _dmi_adx(cls, h, l, c, di_period, adx_smooth):
        """+DI/−DI بتنعيم وايلدر لفترة di_period، و ADX بتنعيم adx_smooth.
        الآمن ضد القسمة على صفر — القيم غير الجاهزة NaN."""
        n = len(c)
        up = np.diff(h, prepend=h[0])
        dn = -np.diff(l, prepend=l[0])
        plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
        minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
        tr = cls._true_range(h, l, c)
        atr_s = cls._rma(tr, di_period, 0)
        pdm_s = cls._rma(plus_dm, di_period, 0)
        mdm_s = cls._rma(minus_dm, di_period, 0)
        with np.errstate(divide='ignore', invalid='ignore'):
            plus_di = 100.0 * pdm_s / np.where(atr_s > 0, atr_s, np.nan)
            minus_di = 100.0 * mdm_s / np.where(atr_s > 0, atr_s, np.nan)
            dx = 100.0 * np.abs(plus_di - minus_di) / np.maximum(plus_di + minus_di, 1e-12)
        dx = np.where(np.isfinite(dx), dx, np.nan)
        first_valid = di_period - 1 if n >= di_period else 0
        adx = cls._rma(np.nan_to_num(dx, nan=0.0), adx_smooth,
                       start_idx=first_valid if n > first_valid else 0)
        if n > first_valid:
            adx[:first_valid + adx_smooth - 1] = np.nan
        return plus_di, minus_di, adx

    @classmethod
    def _supertrend(cls, h, l, c, atr_period, mult):
        """Supertrend القياسي (ATR وايلدر) — اتجاه +1 صاعد / −1 هابط / 0 غير جاهز.
        تعتمد قيمة الشمعة i على الشموع ≤ i فقط."""
        n = len(c)
        dir_out = np.zeros(n, dtype=np.int8)
        line = np.full(n, np.nan)
        atr = cls._wilder_atr(h, l, c, atr_period)
        if n <= atr_period:
            return dir_out, line
        mid = (h + l) / 2.0
        ub = mid + mult * atr
        lb = mid - mult * atr
        fub = np.nan
        flb = np.nan
        d = 1
        for i in range(atr_period, n):
            if not np.isfinite(atr[i]):
                continue
            if not np.isfinite(fub):
                fub, flb, d = ub[i], lb[i], 1
            else:
                fub = ub[i] if (ub[i] < fub or c[i - 1] > fub) else fub
                flb = lb[i] if (lb[i] > flb or c[i - 1] < flb) else flb
                if d == 1 and c[i] < flb:
                    d = -1
                elif d == -1 and c[i] > fub:
                    d = 1
            dir_out[i] = d
            line[i] = flb if d == 1 else fub
        return dir_out, line

    @staticmethod
    def _er(c, period):
        """كفاءة الحركة Efficiency Ratio = |c[i]−c[i−p]| / Σ|Δc| في النافذة.
        النطاق [0,1] — المسار المستقيم = 1.0 والمتعرج يقترب من 0.
        المسار الصفري (سعر ثابت) يعيد 0.0 بلا قسمة على صفر."""
        c = np.asarray(c, dtype=float)
        n = len(c)
        out = np.full(n, np.nan)
        if n <= period:
            return out
        change = np.abs(c[period:] - c[:-period])
        vol = np.abs(np.diff(c))
        cs = np.cumsum(np.concatenate(([0.0], vol)))
        path = cs[period:] - cs[:-period]
        out[period:] = np.where(path > 0, change / np.where(path > 0, path, 1.0), 0.0)
        return out

    @staticmethod
    def _roc(c, period):
        """معدل التغير المئوي (زخم) — NaN قبل اكتمال الفترة."""
        c = np.asarray(c, dtype=float)
        n = len(c)
        out = np.full(n, np.nan)
        if n <= period or period <= 0:
            return out
        base = c[:-period]
        out[period:] = np.where(base != 0, (c[period:] - base) / np.where(base != 0, base, 1.0) * 100.0, 0.0)
        return out

    @staticmethod
    def confirmed_pivots(h, l, w):
        """قمم/قيعان هيكلية مؤكدة فقط: القمة عند i هي أعلى نافذة ±w
        وتصبح صالحة للاستخدام ابتداءً من الشمعة i+w (تأخير التأكيد موثق).
        يعيد (قائمة قمم [(i, price)...]، قائمة قيعان [(i, price)...])."""
        h = np.asarray(h, dtype=float)
        l = np.asarray(l, dtype=float)
        n = len(h)
        w = max(1, int(w))
        ph, pl = [], []
        for i in range(w, n - w):
            if h[i] >= h[i - w:i + w + 1].max():
                ph.append((i, float(h[i])))
            if l[i] <= l[i - w:i + w + 1].min():
                pl.append((i, float(l[i])))
        return ph, pl

    @classmethod
    def compute_arrays(cls, df, params):
        """حساب كل المؤشرات مرة واحدة على شموع مغلقة — يعيد قاموس مصفوفات."""
        c = df['close'].to_numpy(dtype=float)
        h = df['high'].to_numpy(dtype=float)
        l = df['low'].to_numpy(dtype=float)
        ema_filter_on = int(params.get('ema_filter', 0)) == 1
        arr = {
            'n': len(c), 'close': c, 'high': h, 'low': l,
            'open': df['open'].to_numpy(dtype=float),
            'time': pd.to_numeric(df['time']).to_numpy(),
            'close_time': pd.to_numeric(df['close_time']).to_numpy(),
            'hma_fast': cls._hma(c, int(params['hma_fast'])),
            'hma_slow': cls._hma(c, int(params['hma_slow'])),
            'atr': cls._wilder_atr(h, l, c, int(params['st_atr_period'])),
            'er': cls._er(c, int(params['er_period'])),
            'roc_fast': cls._roc(c, int(params['mom_fast'])),
            'roc_mid': cls._roc(c, int(params['mom_mid'])),
            'roc_slow': cls._roc(c, int(params['mom_slow'])),
            'ema': (cls._ema(c, int(params['ema_period'])) if ema_filter_on
                    else np.full(len(c), np.nan)),
        }
        arr['plus_di'], arr['minus_di'], arr['adx'] = cls._dmi_adx(
            h, l, c, int(params['di_period']), int(params['adx_smooth']))
        arr['st_dir'], arr['st_line'] = cls._supertrend(
            h, l, c, int(params['st_atr_period']), float(params['st_mult']))
        arr['pivot_highs'], arr['pivot_lows'] = cls.confirmed_pivots(
            h, l, int(params.get('struct_w', 2)))
        return arr

    @staticmethod
    def min_bars(params):
        """أدنى عدد شموع مغلقة لتحليل صالح (إحماء المؤشرات الأطول)."""
        base = max(int(params['hma_slow']) * 3, int(params['er_period']) * 3,
                   int(params['di_period']) * 5 + int(params['adx_smooth']) * 3,
                   int(params['st_atr_period']) * 4, int(params['mom_slow']) * 3)
        if int(params.get('ema_filter', 0)) == 1:
            base = max(base, int(params['ema_period']) + 20)
        return base + 30

    # ─── آلة الحالات NEUTRAL/BULL/BEAR ───
    @staticmethod
    def _bar_direction(arr, i):
        """اتجاه الشمعة المرشح بأغلبية 3 من 4 أصوات مستقلة (كلها قيم مغلقة):
        1) انحياز HMA السريعة/البطيئة  2) هيمنة DI  3) اتجاه Supertrend
        4) إشارة مجموع الزخم (ROC 2+5+9). نقص الأصوات أو التعادل → 0."""
        if i < 1:
            return 0
        votes = 0
        total = 0
        h8, h21 = arr['hma_fast'][i], arr['hma_slow'][i]
        if np.isfinite(h8) and np.isfinite(h21) and h8 != h21:
            votes += 1 if h8 > h21 else -1
            total += 1
        pdi, mdi = arr['plus_di'][i], arr['minus_di'][i]
        if np.isfinite(pdi) and np.isfinite(mdi) and pdi != mdi:
            votes += 1 if pdi > mdi else -1
            total += 1
        sd = arr['st_dir'][i]
        if sd:
            votes += int(sd)
            total += 1
        m, valid = 0.0, True
        for k in ('roc_fast', 'roc_mid', 'roc_slow'):
            v = arr[k][i]
            if not np.isfinite(v):
                valid = False
                break
            m += v
        if valid and m != 0:
            votes += 1 if m > 0 else -1
            total += 1
        if total < 3:
            return 0
        if votes >= 3:
            return 1
        if votes <= -3:
            return -1
        return 0

    @classmethod
    def state_series(cls, arr, params, replay=None):
        """إعادة بناء حتمية لآلة الحالات على الشموع المغلقة:
        - التبدّل يتطلب مرشحاً ثابتاً min_state_candles شمعة مغلقة متتالية.
        - تبريد cooldown_candles شموع بعد كل تبدّل قبل تبدّل جديد.
        - الانقلاب المباشر BULL↔BEAR يتطلب حركة عكسية ≥ reversal_atr×ATR
          من أقصى إغلاق (للانقلاب الهابط) / أدنى إغلاق (للصاعد) خلال الحالة.
        يعيد (مصفوفة الحالات، meta لكل شمعة: بداية الحالة وعمرها وآخر تبدّل)."""
        n = arr['n']
        start = max(0, n - (replay or cls.REPLAY_BARS))
        min_dur = max(1, int(params['min_state_candles']))
        cool = max(0, int(params['cooldown_candles']))
        rev = float(params['reversal_atr'])
        atr = arr['atr']
        states = np.zeros(n, dtype=np.int8)
        meta = {}
        state, cand, cand_count = 0, 0, 0
        last_flip = start - 10 ** 9
        state_start = start
        extreme = None
        for i in range(start, n):
            d = cls._bar_direction(arr, i)
            if d != 0 and d == cand:
                cand_count += 1
            elif d != 0:
                cand, cand_count = d, 1
            else:
                cand, cand_count = 0, 0
            can_flip = (cand != 0 and cand != state
                        and cand_count >= min_dur
                        and (i - last_flip) >= cool)
            if can_flip:
                ok = True
                if state != 0 and cand == -state:
                    ext = extreme
                    if ext is not None and np.isfinite(atr[i]) and atr[i] > 0:
                        if state == 1:
                            ok = arr['close'][i] <= ext - rev * atr[i]
                        else:
                            ok = arr['close'][i] >= ext + rev * atr[i]
                if ok:
                    state, last_flip, state_start = cand, i, i
                    extreme = arr['close'][i]
                    cand_count = 0
            c = arr['close'][i]
            if extreme is None:
                extreme = c
            elif state == 1:
                extreme = max(extreme, c)
            elif state == -1:
                extreme = min(extreme, c)
            states[i] = state
            meta[i] = {'state': state, 'state_start': state_start,
                       'last_flip': last_flip, 'age': i - state_start}
        return states, meta

    # ─── القياس: Entry Power / Entry Confidence / تأكيدات الزخم ───
    @staticmethod
    def _last_confirmed_pivot(pivots, i, w):
        """آخر قمة/قاع مؤكد بحيث i >= مؤشر القمة + w (بلا استخدام مبكر)."""
        best = None
        for p in pivots:
            if p[0] + w <= i:
                best = p
            else:
                break
        return best

    @classmethod
    def _score_bar(cls, arr, i, dirn, params):
        """قياس شمعة مغلقة واحدة لاتجاه معين. يعيد
        (power 0-100, confidence 0-9, mom_conf 0-3, structure_ok)."""
        bull = dirn > 0
        aligned = lambda x: (x > 0) if bull else (x < 0)
        power = 0.0
        conf = 0
        c = arr['close'][i]
        w = int(params.get('struct_w', 2))

        # 1) HMA (20 نقطة)
        h8, h21 = arr['hma_fast'][i], arr['hma_slow'][i]
        h8p = arr['hma_fast'][i - 1] if i > 0 else np.nan
        if np.isfinite(h8) and np.isfinite(h21) and aligned(h8 - h21):
            power += 14.0
            conf += 1
        if np.isfinite(h8) and np.isfinite(h8p) and aligned(h8 - h8p):
            power += 6.0
            conf += 1

        # 2) DMI/ADX (20 نقطة)
        pdi, mdi, adx = arr['plus_di'][i], arr['minus_di'][i], arr['adx'][i]
        adx_p = arr['adx'][i - 1] if i > 0 else np.nan
        if np.isfinite(pdi) and np.isfinite(mdi) and aligned(pdi - mdi):
            power += 12.0
            conf += 1
        if np.isfinite(adx) and adx >= float(params['strong_adx']):
            power += 5.0
            conf += 1
        if np.isfinite(adx) and np.isfinite(adx_p) and aligned(adx - adx_p):
            power += 3.0

        # 3) الزخم (15 نقطة — 5 لكل ROC مؤكد)
        mom_conf = 0
        for k in ('roc_fast', 'roc_mid', 'roc_slow'):
            v = arr[k][i]
            if np.isfinite(v) and aligned(v):
                mom_conf += 1
        power += 5.0 * mom_conf
        if mom_conf >= int(params['min_mom_conf']):
            conf += 1

        # 4) كفاءة الحركة ER (10 نقاط)
        er = arr['er'][i]
        if np.isfinite(er):
            if er >= float(params['strong_er']):
                power += 10.0
                conf += 1
            elif er >= float(params['strong_er']) / 2.0:
                power += 5.0

        # 5) Supertrend (15 نقطة)
        sd = arr['st_dir'][i]
        if sd and aligned(sd):
            power += 15.0
            conf += 1

        # 6) البنية السليمة (20 نقطة) — بقمم/قيعان مؤكدة فقط
        structure_ok = False
        if bull:
            pl = cls._last_confirmed_pivot(arr['pivot_lows'], i, w)
            structure_ok = bool(pl) and c > pl[1]
        else:
            ph = cls._last_confirmed_pivot(arr['pivot_highs'], i, w)
            structure_ok = bool(ph) and c < ph[1]
        if structure_ok:
            power += 20.0
            conf += 1

        return min(100.0, power), conf, mom_conf, structure_ok

    @classmethod
    def _trigger(cls, arr, i, dirn):
        """زناد الدخول على شمعة مغلقة (يمنع ملاحقة الحركة الممتدة):
        BUY: استعادة HMA السريعة (إغلاق يقطعها صعوداً) أو استئناف بعد ارتداد
             من HMA البطيئة (لمس خلال آخر 3 شموع + شمعة صاعدة مغلقة فوق السريعة).
        SELL: المرآة المعاكسة تماماً."""
        c, o = arr['close'], arr['open']
        f, s = arr['hma_fast'], arr['hma_slow']
        if not (np.isfinite(f[i]) and np.isfinite(f[i - 1]) and np.isfinite(s[i])):
            return False, 'مؤشرات HMA غير جاهزة'
        lo_w = max(0, i - 2)
        if dirn > 0:
            if c[i] > f[i] and c[i - 1] <= f[i - 1]:
                return True, 'استعادة HMA السريعة (تقاطع صاعد)'
            touched = bool((arr['low'][lo_w:i + 1] <= arr['hma_slow'][lo_w:i + 1]).any())
            if touched and c[i] > f[i] and c[i] > o[i]:
                return True, 'استئناف صاعد بعد ارتداد من HMA البطيئة'
            return False, 'لا زناد شراء (لا استعادة ولا ارتداد مؤكد)'
        else:
            if c[i] < f[i] and c[i - 1] >= f[i - 1]:
                return True, 'كسر HMA السريعة (تقاطع هابط)'
            touched = bool((arr['high'][lo_w:i + 1] >= arr['hma_slow'][lo_w:i + 1]).any())
            if touched and c[i] < f[i] and c[i] < o[i]:
                return True, 'استئناف هابط بعد ارتداد من HMA البطيئة'
            return False, 'لا زناد بيع (لا كسر ولا ارتداد مؤكد)'

    @classmethod
    def _structural_override(cls, arr, i, dirn, params, power, confidence, mom_conf):
        """الاستثناء الهيكلي المحدود — شروطه الدقيقة (كلها إلزامية):
        1) تأكيد زخم ≥1 بالاتجاه.
        2) ADX ≥ so_adx وهيمنة DI بالاتجاه.
        3) إغلاق يكسر آخر قمة مؤكدة (للشراء) / قاع مؤكد (ل للبيع) بعمق
           ≥ reversal_atr × ATR.
        4) power ≥ so_power و confidence ≥ so_confidence.
        ما لا يتجاوزه أبداً: حالة NEUTRAL (لا تداول)، التبريد، فلتر EMA،
        وبوابات المخاطر والتعارض في مسار التنفيذ المشترك."""
        w = int(params.get('struct_w', 2))
        atr = arr['atr'][i]
        c = arr['close'][i]
        if not (np.isfinite(atr) and atr > 0):
            return False, 'ATR غير صالح للاستثناء الهيكلي'
        if mom_conf < 1:
            return False, 'لا تأكيد زخم واحد على الأقل للاستثناء الهيكلي'
        pdi, mdi, adx = arr['plus_di'][i], arr['minus_di'][i], arr['adx'][i]
        if not (np.isfinite(adx) and adx >= float(params['so_adx'])):
            return False, f'ADX أقل من حد الاستثناء ({(adx if np.isfinite(adx) else 0):.1f} < {float(params["so_adx"]):g})'
        if dirn > 0 and not (pdi > mdi):
            return False, 'DI غير مؤيّد للاستثناء الصاعد'
        if dirn < 0 and not (mdi > pdi):
            return False, 'DI غير مؤيّد للاستثناء الهابط'
        if dirn > 0:
            ph = cls._last_confirmed_pivot(arr['pivot_highs'], i, w)
            if not ph:
                return False, 'لا قمة مؤكدة لقياس الكسر الهيكلي'
            if c <= ph[1] + float(params['reversal_atr']) * atr:
                return False, 'الإغلاق لم يكسر القمة المؤكدة بعمق 0.6×ATR'
        else:
            pl = cls._last_confirmed_pivot(arr['pivot_lows'], i, w)
            if not pl:
                return False, 'لا قاع مؤكد لقياس الكسر الهيكلي'
            if c >= pl[1] - float(params['reversal_atr']) * atr:
                return False, 'الإغلاق لم يكسر القاع المؤكد بعمق 0.6×ATR'
        if power < float(params['so_power']) or confidence < int(params['so_confidence']):
            return False, (f'القوة/الثقة أقل من حد الاستثناء '
                           f'(قوة {power:g}/{float(params["so_power"]):g}، ثقة {confidence}/{int(params["so_confidence"])})')
        return True, 'كسر هيكلي مؤكد بعمق 0.6×ATR مع قوة اتجاه'

    @classmethod
    def evaluate_at(cls, arr, states, meta, i, params, include_details=True):
        """تقييم بوابات الدخول على شمعة مغلقة محددة i — يعتمد فقط على مصفوفات
        محسوبة مسبقاً (كلها متتالية خلفية: قيمة الفهرس i لا تتأثر بأي بيانات
        بعده — مُختبر في test_strategies.py) لذا يستخدمه محرك الاختبار التاريخي
        بأمان وبلا تسرب مستقبلي. يعيد قاموس القرار نفسه الذي يعيده evaluate."""
        result = {'signal': None, 'reject_reason': None,
                  'state': 'NEUTRAL', 'state_age': 0,
                  'power': {'BUY': 0.0, 'SELL': 0.0},
                  'confidence': {'BUY': 0, 'SELL': 0},
                  'mom_conf': {'BUY': 0, 'SELL': 0},
                  'snapshot': {}}
        try:
            n = arr['n']
            if i is None or i < 0 or i >= n or i not in meta:
                result['reject_reason'] = 'فهرس شمعة خارج نطاق التقييم'
                return result
            state = int(states[i])
            result['state'] = cls.STATE_NAMES[state]
            result['state_age'] = int(i - meta[i]['state_start'])

            if include_details:
                for dirn, key in ((1, 'BUY'), (-1, 'SELL')):
                    p, cf, mc, _ = cls._score_bar(arr, i, dirn, params)
                    result['power'][key] = round(float(p), 1)
                    result['confidence'][key] = int(cf)
                    result['mom_conf'][key] = int(mc)
                result['snapshot'] = {
                    'close': float(arr['close'][i]),
                    'hma_fast': float(arr['hma_fast'][i]) if np.isfinite(arr['hma_fast'][i]) else None,
                    'hma_slow': float(arr['hma_slow'][i]) if np.isfinite(arr['hma_slow'][i]) else None,
                    'plus_di': float(arr['plus_di'][i]) if np.isfinite(arr['plus_di'][i]) else None,
                    'minus_di': float(arr['minus_di'][i]) if np.isfinite(arr['minus_di'][i]) else None,
                    'adx': float(arr['adx'][i]) if np.isfinite(arr['adx'][i]) else None,
                    'er': float(arr['er'][i]) if np.isfinite(arr['er'][i]) else None,
                    'st_dir': int(arr['st_dir'][i]),
                    'atr': float(arr['atr'][i]) if np.isfinite(arr['atr'][i]) else None,
            }

            cool = max(0, int(params['cooldown_candles']))
            if state == 0:
                result['reject_reason'] = 'السوق محايد (NEUTRAL) — لا دخول'
                return result
            if (i - meta[i]['last_flip']) < cool:
                result['reject_reason'] = (f'تبريد آلة الحالات '
                                           f'({i - meta[i]["last_flip"]}/{cool} شموع بعد التبدّل)')
                return result

            dirn = state
            side = 'BUY' if dirn > 0 else 'SELL'
            power = result['power'][side]
            conf = result['confidence'][side]
            mc = result['mom_conf'][side]

            # ① فلتر EMA200 (صلب عند التفعيل — لا يتجاوزه الاستثناء الهيكلي)
            if int(params.get('ema_filter', 0)) == 1:
                ema_v = arr['ema'][i]
                if not np.isfinite(ema_v):
                    result['reject_reason'] = 'EMA200 غير جاهزة بعد'
                    return result
                if dirn > 0 and not arr['close'][i] > ema_v:
                    result['reject_reason'] = 'فلتر EMA200 يمنع الشراء (السعر أسفل المتوسط)'
                    return result
                if dirn < 0 and not arr['close'][i] < ema_v:
                    result['reject_reason'] = 'فلتر EMA200 يمنع البيع (السعر أعلى المتوسط)'
                    return result

            # ② الزخم الأدنى (صلب)
            if mc < int(params['min_mom_conf']):
                result['reject_reason'] = (f'تأكيد الزخم غير كافٍ '
                                           f'({mc}/{int(params["min_mom_conf"])})')
                return result

            # ③ الزناد + العتبات → وإلا الاستثناء الهيكلي (محدود)
            trig_ok, trig_txt = cls._trigger(arr, i, dirn)
            threshold_ok = (power >= float(params['min_power'])
                            and conf >= int(params['min_confidence']))
            override = False
            if trig_ok and threshold_ok:
                reason_txt = trig_txt
            else:
                ov_ok, ov_txt = cls._structural_override(arr, i, dirn, params,
                                                         power, conf, mc)
                if not ov_ok:
                    result['reject_reason'] = (f'قوة/ثقة أقل من العتبة '
                                               f'(قوة {power:g}/{float(params["min_power"]):g}، '
                                               f'ثقة {conf}/{int(params["min_confidence"])})'
                                               if trig_ok else trig_txt)
                    return result
                override = True
                reason_txt = 'استثناء هيكلي: ' + ov_txt

            result['signal'] = {
                'side': side,
                'candle_ms': int(arr['time'][i]),
                'candle_close_ms': int(arr['close_time'][i]),
                'close': float(arr['close'][i]),
                'atr': float(arr['atr'][i]),
                'power': float(power),
                'confidence': int(conf),
                'mom_conf': int(mc),
                'override': override,
                'reason_txt': reason_txt,
                'state': cls.STATE_NAMES[state],
            }
            return result
        except Exception as e:
            result['reject_reason'] = f'خطأ تقييم HMA: {e}'
            return result

    @classmethod
    def evaluate(cls, df, params):
        """التقييم الكامل على شموع مغلقة (الشمعة الجارية محذوفة مسبقاً).
        يعيد قاموساً: ok/state/state_age/power/confidence/mom_conf/signal/
        reject_reason/snapshot/arrays/states/meta/i — الإشارة تُقيَّم على
        آخر شمعة مغلقة فقط ولا تُعدَّل لاحقاً بأي بيانات جديدة (مُختبر)."""
        result = {'ok': False, 'signal': None, 'reject_reason': None,
                  'state': 'NEUTRAL', 'state_age': 0,
                  'power': {'BUY': 0.0, 'SELL': 0.0},
                  'confidence': {'BUY': 0, 'SELL': 0},
                  'mom_conf': {'BUY': 0, 'SELL': 0},
                  'snapshot': {}, 'arrays': None, 'states': None,
                  'meta': None, 'i': None}
        try:
            n = len(df)
            need = cls.min_bars(params)
            if n < need:
                result['reject_reason'] = f'بيانات غير كافية ({n} شمعة < {need})'
                return result
            arr = cls.compute_arrays(df, params)
            states, meta = cls.state_series(arr, params)
            i = n - 1
            decision = cls.evaluate_at(arr, states, meta, i, params)
            result.update(decision)
            result.update({'arrays': arr, 'states': states, 'meta': meta, 'i': i})
            result['ok'] = result['signal'] is not None
            return result
        except Exception as e:
            result['reject_reason'] = f'خطأ تقييم HMA: {e}'
            return result

    @staticmethod
    def exit_reason(arr, states, i, side):
        """سبب خروج استراتيجي إن وجد — على شمعة مغلقة، بشروط ثابتة (لا
        أحداث عابرة) كي تصمد أمام إعادة تشغيل البوت:
        - آلة الحالات صارت ضد اتجاه الصفقة (BULL لصفقة بيع مثلاً).
        - Supertrend مغلق ضد اتجاه الصفقة.
        ملاحظة موثقة: عكس شرط الدخول وحده ليس كافياً — الخروج يخضع لنفس
        آلة الحالات والشروط الثابتة أعلاه، وبوابات الستوب/TP1/الستوب الزمني
        المشتركة تبقى فعالة دائماً."""
        if states is None or i is None or i >= len(states):
            return None
        st = int(states[i])
        if side == 'BUY' and st == -1:
            return 'آلة الحالات انقلبت إلى BEAR'
        if side == 'SELL' and st == 1:
            return 'آلة الحالات انقلبت إلى BULL'
        sd = arr['st_dir'][i] if arr is not None else 0
        if side == 'BUY' and sd == -1:
            return 'Supertrend مغلق ضد اتجاه الشراء'
        if side == 'SELL' and sd == 1:
            return 'Supertrend مغلق ضد اتجاه البيع'
        return None

    @classmethod
    def adx_entry_ok(cls, arr, i, gate):
        """🧭 بوابة الاتجاهية عند الدخول (V11.1 — مُتحقق عليها في مختبر إعادة
        البناء على نافذتين): ADX-14 وايلدر على إطار الاستراتيجية (شموع مغلقة
        فقط)، يُحسب بنفس دالة DMI المحركية (_dmi_adx بنفس الفترتين 14/14).
        يعيد (مسموح؟, قيمة ADX أو None).
        - gate ≤ 0 → البوابة معطلة (يسمح دائماً).
        - ADX غير متاح/غير نهائي → يُرفض (محافظ — لا دخول بلا قياس).
        مطابقة حرفية لمنطق المختبر الموثق (adx14[i] ≥ gate عند شمعة الإشارة)."""
        if gate is None or float(gate) <= 0:
            return True, None
        try:
            _, _, adx14 = cls._dmi_adx(arr['high'], arr['low'], arr['close'], 14, 14)
            if i is None or i >= len(adx14):
                return False, None
            a = float(adx14[i])
            if not math.isfinite(a):
                return False, None
            return (a >= float(gate)), a
        except Exception:
            return False, None


# ══════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════
# 📊 لوحة المراقبة المدمجة V12 — كل ما يفعله البوت صغيراً وكبيراً مع السبب
# تعمل داخل هذا الملف نفسه (بلا ملفات خارجية): HTTP خفيف + صفحة عربية RTL.
# المنفذ: DASHBOARD_PORT (افتراضي 8999) — للتعطيل: DASHBOARD_ENABLED=false
# كل حدث يُعرض في اللوحة ويُكتب أيضاً في ملف JSONL دائم (bot_events.jsonl).
# ═════════════════════════════════════════════════════════════════════
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DASHBOARD_ENABLED = os.environ.get('DASHBOARD_ENABLED', 'true').lower() != 'false'
# المنفذ: DASHBOARD_PORT أولاً ثم PORT (منصات النشر مثل Railway) ثم 8999 —
# مهم: يجب أن يطابق منفذ النطاق العام في Railway (Settings → Public Networking).
DASHBOARD_PORT = int(os.environ.get('DASHBOARD_PORT')
                     or os.environ.get('PORT') or '8999')
DASHBOARD_EVENTS_FILE = os.environ.get('DASHBOARD_EVENTS_FILE', 'bot_events.jsonl')
# 🔑 حماية اختيارية: لو ضُبط DASHBOARD_TOKEN، بيانات اللوحة (/api/state) تتطلب المفتاح.
# ضعه عند عرض اللوحة على نطاق عام (مثل Railway) حتى لا يرى الغرباء رصيدك وصفقاتك.
DASHBOARD_TOKEN = (os.environ.get('DASHBOARD_TOKEN', '') or '').strip()


class ActionLog:
    """📊 السجل المركزي لكل حركات البوت مع السبب — ذاكرة حية للوحة +
    ملف JSONL دائم للتدقيق. آمن للخيوط: يكتب من حلقة asyncio ويعرض من HTTP."""

    def __init__(self, maxlen=1500):
        self._lock = threading.Lock()
        self._events = collections.deque(maxlen=maxlen)
        self._seq = 0
        self._bot = None
        self.state = {'status': 'إقلاع...', 'started_at': time.time()}
        self._fp = None
        try:
            if os.path.exists(DASHBOARD_EVENTS_FILE) \
                    and os.path.getsize(DASHBOARD_EVENTS_FILE) > 30 * 1024 * 1024:
                os.replace(DASHBOARD_EVENTS_FILE, DASHBOARD_EVENTS_FILE + '.old')
            self._fp = open(DASHBOARD_EVENTS_FILE, 'a', encoding='utf-8')
        except Exception:
            self._fp = None

    def bind(self, bot):
        self._bot = bot

    def log(self, kind, symbol=None, msg='', reason=None, detail=None, **extra):
        with self._lock:
            self._seq += 1
            ev = {'i': self._seq, 't': time.time(), 'kind': kind,
                  'symbol': symbol, 'msg': msg, 'reason': reason}
            if detail:
                ev['detail'] = str(detail)[:900]
            for k, v in extra.items():
                if v is not None:
                    ev[k] = v
            self._events.append(ev)
        try:
            if self._fp:
                self._fp.write(json.dumps(ev, ensure_ascii=False, default=str) + '\n')
                self._fp.flush()
        except Exception:
            pass

    def update_state(self, **kv):
        with self._lock:
            self.state.update(kv)

    def snapshot(self, limit=300, kind=None):
        with self._lock:
            evs = list(self._events)
            st = dict(self.state)
        if kind and kind != 'الكل':
            evs = [e for e in evs if e.get('kind') == kind]
        try:
            evs = evs[-max(1, int(limit)):]
        except Exception:
            evs = evs[-300:]
        st.setdefault('started_at', time.time())
        try:
            st['uptime_h'] = round((time.time() - st['started_at']) / 3600.0, 1)
        except Exception:
            pass
        return {'state': st, 'events': evs, 'now': time.time()}

    def clear(self):
        """🧹 مسح شامل: أحداث الذاكرة + إفراغ ملف JSONL الدائم — بداية جديدة."""
        with self._lock:
            self._events.clear()
            self._seq = 0
        try:
            if self._fp:
                self._fp.close()
                self._fp = open(DASHBOARD_EVENTS_FILE, 'w', encoding='utf-8')
        except Exception:
            pass


ACTION = ActionLog()


# ═══ 🕹️ جسر الأوامر: من خيط خادم HTTP إلى حلقة البوت asyncio بأمان ═══
class _DashBridge:
    """خادم اللوحة يعمل في خيط منفصل، والبوت يعمل في حلقة asyncio —
    هذا الجسر يرسل أمر اللوحة إلى الحلقة بأمان (run_coroutine_threadsafe)."""

    def __init__(self):
        self.bot = None
        self.loop = None

    def bind(self, bot, loop):
        self.bot = bot
        self.loop = loop

    def dispatch(self, action, symbol=None):
        if self.bot is None or self.loop is None:
            return {'ok': False, 'error': 'البوت لم يُقلع بعد — انتظر الإقلاع ثم أعد الأمر'}
        try:
            fut = asyncio.run_coroutine_threadsafe(
                self.bot.panel_command(action, symbol), self.loop)
            return fut.result(timeout=180)
        except Exception as e:
            return {'ok': False, 'error': f'فشل تنفيذ الأمر: {e}'}


DASH_BRIDGE = _DashBridge()
_ALLOWED_COMMANDS = ('pause', 'resume', 'close_one', 'close_all',
                     'reset_all', 'scan_now', 'stop_retry')


class _DashboardHandler(BaseHTTPRequestHandler):
    """خادم HTTP خفيف — يعرض الصفحة + واجهة JSON (الحالة + الأحداث المصفّاة)."""

    def log_message(self, *a, **k):
        return

    def _send(self, code, body, ctype='application/json; charset=utf-8'):
        data = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        # إذن CORS محصور: يسمح فقط لملف اللوحة المستقل (file:// يرسل Origin: null)
        # وللصفحات المحلية — المواقع البعيدة تُحجب (المتصفح يرفض قراءة الرد).
        try:
            origin = self.headers.get('Origin', '') or ''
        except Exception:
            origin = ''
        if (origin == 'null'
                or origin.startswith('http://localhost')
                or origin.startswith('http://127.0.0.1')):
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Vary', 'Origin')
        self.end_headers()
        try:
            self.wfile.write(data)
        except Exception:
            pass

    def do_GET(self):
        try:
            path = self.path.split('?')[0]
            qs = urllib.parse.parse_qs(self.path.split('?')[1]) if '?' in self.path else {}
            if path in ('/', '/index.html'):
                self._send(200, _DASHBOARD_HTML, 'text/html; charset=utf-8')
            elif path == '/api/state':
                # 🔑 بوابة المفتاح: بدون مفتاح صحيح لا تُعاد أي بيانات (رصيد/صفقات/أحداث)
                if DASHBOARD_TOKEN:
                    given = ((qs.get('key') or [''])[0]
                             or self.headers.get('X-Dash-Key', '') or '')
                    if given != DASHBOARD_TOKEN:
                        self._send(401, json.dumps(
                            {'error': 'unauthorized — اللوحة محمية بمفتاح'}))
                        return
                try:
                    limit = int((qs.get('limit') or ['400'])[0])
                except Exception:
                    limit = 400
                kind = (qs.get('kind') or ['الكل'])[0]
                self._send(200, json.dumps(ACTION.snapshot(limit=limit, kind=kind),
                                           ensure_ascii=False, default=str))
            elif path == '/health':
                self._send(200, json.dumps({'ok': True}))
            else:
                self._send(404, json.dumps({'error': 'not found'}))
        except Exception as e:
            try:
                self._send(500, json.dumps({'error': str(e)}))
            except Exception:
                pass

    def _check_key(self, qs):
        """🔑 نفس بوابة /api/state: لو ضُبط DASHBOARD_TOKEN فالأوامر تتطلب المفتاح."""
        if not DASHBOARD_TOKEN:
            return True
        given = ((qs.get('key') or [''])[0]
                 or self.headers.get('X-Dash-Key', '') or '')
        return given == DASHBOARD_TOKEN

    def do_OPTIONS(self):
        # طلب CORS المسبق من صفحة اللوحة المستقلة (file:// يرسل Origin: null)
        try:
            origin = self.headers.get('Origin', '') or ''
        except Exception:
            origin = ''
        allowed = (origin == 'null' or origin.startswith('http://localhost')
                   or origin.startswith('http://127.0.0.1'))
        if allowed:
            self.send_response(204)
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Dash-Key')
            self.send_header('Access-Control-Max-Age', '600')
            self.send_header('Content-Length', '0')
            self.end_headers()
        else:
            self.send_response(403)
            self.send_header('Content-Length', '0')
            self.end_headers()

    def do_POST(self):
        """🕹️ نقطة الأوامر الوحيدة: POST /api/command?key=...
        المتن JSON: {"action": "pause|resume|close_one|close_all|reset_all|scan_now|stop_retry", "symbol": "..."}"""
        try:
            path = self.path.split('?')[0]
            qs = urllib.parse.parse_qs(self.path.split('?')[1]) if '?' in self.path else {}
            if path != '/api/command':
                self._send(404, json.dumps({'error': 'not found'}))
                return
            if not self._check_key(qs):
                self._send(401, json.dumps(
                    {'ok': False, 'error': 'unauthorized — الأوامر محمية بمفتاح اللوحة'}))
                return
            try:
                length = int(self.headers.get('Content-Length') or 0)
                raw = self.rfile.read(length) if length > 0 else b'{}'
                body = json.loads(raw.decode('utf-8') or '{}')
            except Exception:
                body = {}
            if not isinstance(body, dict):
                body = {}
            action = str(body.get('action') or '').strip()
            symbol = str(body.get('symbol') or '').strip().upper() or None
            if action not in _ALLOWED_COMMANDS:
                self._send(400, json.dumps(
                    {'ok': False, 'error': f'أمر غير معروف: {action or "فارغ"}',
                     'allowed': list(_ALLOWED_COMMANDS)}))
                return
            if action in ('close_one', 'stop_retry') and not symbol:
                self._send(400, json.dumps(
                    {'ok': False, 'error': 'هذا الأمر يتطلب رمز الصفقة (symbol)'}))
                return
            ACTION.log('نظام', msg=f'🕹️ أمر من اللوحة: {action}'
                       + (f' — {symbol}' if symbol else ''))
            result = DASH_BRIDGE.dispatch(action, symbol)
            self._send(200, json.dumps(result, ensure_ascii=False, default=str))
        except Exception as e:
            try:
                self._send(500, json.dumps({'ok': False, 'error': str(e)}))
            except Exception:
                pass


_DASHBOARD_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🎯 لوحة مراقبة القناص — HMA</title>
<style>
  :root{
    --bg:#0b1220; --panel:#111a2e; --panel2:#0e1626; --line:#1e2a44;
    --txt:#e7edf7; --dim:#8b9bb8; --green:#2ecc71; --red:#ff5c69;
    --gold:#f5b942; --blue:#4da3ff; --purple:#b48bff; --cyan:#39d0d8;
  }
  *{box-sizing:border-box; margin:0; padding:0}
  body{background:var(--bg); color:var(--txt); font-family:"Segoe UI",Tahoma,"Noto Sans Arabic",Arial,sans-serif; font-size:14px; padding:16px; padding-bottom:40px}
  .wrap{max-width:1280px; margin:0 auto}
  /* ═══ الترويسة ═══ */
  .hdr{display:flex; flex-wrap:wrap; gap:10px; align-items:center; justify-content:space-between; margin-bottom:14px}
  .hdr h1{font-size:19px; font-weight:700}
  .hdr h1 small{color:var(--dim); font-weight:400; font-size:12px; margin-inline-start:8px}
  .chips{display:flex; flex-wrap:wrap; gap:8px}
  .chip{background:var(--panel); border:1px solid var(--line); border-radius:20px; padding:5px 12px; font-size:12px; color:var(--dim)}
  .chip b{color:var(--txt); font-weight:600}
  .dot{display:inline-block; width:8px; height:8px; border-radius:50%; margin-inline-end:6px; background:var(--green); box-shadow:0 0 6px var(--green)}
  .dot.off{background:var(--red); box-shadow:0 0 6px var(--red)}
  .dot.warn{background:var(--gold); box-shadow:0 0 6px var(--gold)}
  /* ═══ شريط النافذة والمخاطر ═══ */
  .strip{display:flex; flex-wrap:wrap; gap:10px; margin-bottom:14px}
  .strip .box{flex:1; min-width:240px; border-radius:12px; padding:10px 14px; font-size:13px; border:1px solid var(--line); background:var(--panel)}
  .box.night{border-color:#5b4a1e; background:linear-gradient(90deg,#231c08,#1a1508); color:var(--gold)}
  .box.open{border-color:#1d4d33; background:linear-gradient(90deg,#0a2114,#081a0f); color:#7ee2a8}
  .box.risk-bad{border-color:#5b1e1e; background:linear-gradient(90deg,#210a0a,#1a0808); color:#ff9b9b}
  .box b{font-weight:700}
  /* ═══ التحكم والطوارئ ═══ */
  .ctl{background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:12px 14px; margin-bottom:14px}
  .ctl-t{font-size:14px; font-weight:700; margin-bottom:10px; display:flex; flex-wrap:wrap; gap:8px; align-items:center}
  .ctl-t .ctl-note{font-size:11.5px; color:var(--dim); font-weight:400}
  .ctl-b{display:flex; flex-wrap:wrap; gap:8px}
  .cbtn{border:1px solid var(--line); background:var(--panel2); color:var(--txt); border-radius:10px; padding:9px 16px; font-size:13px; font-weight:700; cursor:pointer; font-family:inherit; transition:.2s}
  .cbtn:hover{filter:brightness(1.25)}
  .cbtn.stop{background:rgba(245,185,66,.12); color:var(--gold); border-color:#5b4a1e}
  .cbtn.stop.paused{background:rgba(46,204,113,.12); color:var(--green); border-color:#1d4d33}
  .cbtn.danger{background:rgba(255,92,105,.12); color:var(--red); border-color:#5b1e1e}
  .cbtn.wipe{background:rgba(180,139,255,.10); color:var(--purple); border-color:#4a3a6b}
  .rowbtn{border:1px solid #5b1e1e; background:rgba(255,92,105,.10); color:var(--red); border-radius:8px; padding:3px 10px; font-size:11.5px; font-weight:700; cursor:pointer; font-family:inherit; white-space:nowrap}
  .rowbtn.retry{border-color:#5b4a1e; background:rgba(245,185,66,.10); color:var(--gold)}
  .rowbtn:hover{filter:brightness(1.3)}
  /* ═══ البطاقات ═══ */
  .cards{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; margin-bottom:16px}
  .card{background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:12px 14px}
  .card .lbl{color:var(--dim); font-size:11.5px; margin-bottom:6px}
  .card .val{font-size:19px; font-weight:700; letter-spacing:.3px}
  .val.g{color:var(--green)} .val.r{color:var(--red)} .val.b{color:var(--blue)} .val.gold{color:var(--gold)}
  /* ═══ المراكز المفتوحة ═══ */
  .sec-t{font-size:15px; font-weight:700; margin:18px 0 10px; display:flex; align-items:center; gap:8px}
  .sec-t .cnt{background:var(--panel); border:1px solid var(--line); border-radius:12px; font-size:11.5px; padding:2px 10px; color:var(--dim)}
  table{width:100%; border-collapse:collapse; background:var(--panel); border:1px solid var(--line); border-radius:14px; overflow:hidden; font-size:13px}
  th{background:var(--panel2); color:var(--dim); font-weight:600; padding:9px 10px; text-align:right; font-size:12px; border-bottom:1px solid var(--line); white-space:nowrap}
  td{padding:9px 10px; border-bottom:1px solid #16203a; white-space:nowrap}
  tr:last-child td{border-bottom:none}
  .sym{font-weight:700; color:var(--cyan)}
  .side-buy{color:var(--green); font-weight:700} .side-sell{color:var(--red); font-weight:700}
  .num{font-family:Consolas,Menlo,monospace; direction:ltr; display:inline-block}
  .pill{border-radius:10px; padding:2px 8px; font-size:11px; border:1px solid var(--line)}
  .pill.ok{color:var(--green); border-color:#1d4d33} .pill.pl{color:var(--gold); border-color:#5b4a1e}
  .pill.loc{color:var(--red); border-color:#5b1e1e} .pill.none{color:var(--dim)}
  .empty{padding:22px; text-align:center; color:var(--dim); background:var(--panel); border:1px dashed var(--line); border-radius:14px}
  /* ═══ سجل الأحداث ═══ */
  .toolbar{display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:10px}
  .fbtn{background:var(--panel); color:var(--dim); border:1px solid var(--line); border-radius:20px; padding:5px 14px; cursor:pointer; font-size:12.5px; font-family:inherit}
  .fbtn:hover{color:var(--txt)} .fbtn.on{background:#1c2a4a; color:#fff; border-color:#33507f}
  .search{flex:1; min-width:180px; background:var(--panel); border:1px solid var(--line); border-radius:20px; padding:6px 14px; color:var(--txt); font-family:inherit; font-size:12.5px; outline:none}
  .search:focus{border-color:#33507f}
  #feed{display:flex; flex-direction:column; gap:7px}
  .ev{background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:9px 12px; border-inline-start:3px solid var(--dim)}
  .ev .top{display:flex; flex-wrap:wrap; gap:8px; align-items:center}
  .ev .t{color:var(--dim); font-size:11.5px; font-family:Consolas,Menlo,monospace; direction:ltr}
  .ev .k{font-size:10.5px; border-radius:8px; padding:2px 8px; font-weight:700}
  .ev .s{font-weight:700; color:var(--cyan); font-size:12.5px}
  .ev .m{flex:1; min-width:200px; font-size:13px}
  .ev .rsn{margin-top:6px; font-size:12.5px; color:var(--dim); background:var(--panel2); border-radius:8px; padding:6px 10px; border:1px solid var(--line)}
  .ev .rsn b{color:#c3d0e8; font-weight:600}
  .ev.dtl{cursor:pointer} .ev .more{display:none; margin-top:6px; font-size:12px; color:#a8b8d8; background:var(--panel2); border:1px solid var(--line); border-radius:8px; padding:8px 10px; white-space:pre-wrap}
  .ev.open .more{display:block}
  .k-دخول{color:#0a2114; background:var(--green)} .ev[data-k="دخول"]{border-inline-start-color:var(--green)}
  .k-خروج{color:#fff; background:var(--red)} .ev[data-k="خروج"]{border-inline-start-color:var(--red)}
  .k-إشارة{color:#06121f; background:var(--blue)} .ev[data-k="إشارة"]{border-inline-start-color:var(--blue)}
  .k-رفض{color:#211606; background:var(--gold)} .ev[data-k="رفض"]{border-inline-start-color:var(--gold)}
  .k-خطأ{color:#fff; background:#c0392b} .ev[data-k="خطأ"]{border-inline-start-color:#c0392b}
  .k-نظام{color:#0d1524; background:var(--dim)} .ev[data-k="نظام"]{border-inline-start-color:#3a4a6b}
  .k-دورة{color:#0d1524; background:#7f95bd} .ev[data-k="دورة"]{border-inline-start-color:#7f95bd}
  .k-نبض{color:#0d1524; background:var(--cyan)} .ev[data-k="نبض"]{border-inline-start-color:var(--cyan)}
  .k-مخاطر{color:#fff; background:#8e44ad} .ev[data-k="مخاطر"]{border-inline-start-color:#8e44ad}
  .k-أخبار{color:#0d1524; background:#e67e22} .ev[data-k="أخبار"]{border-inline-start-color:#e67e22}
  .foot{margin-top:14px; color:var(--dim); font-size:11.5px; text-align:center; line-height:1.9}
  .live{color:var(--green)}
</style>
</head>
<body>
<div class="wrap">

  <div class="hdr">
    <h1>🎯 لوحة مراقبة القناص <small>V12.1 — استراتيجية HMA_DMI_MOMENTUM</small></h1>
    <div class="chips">
      <span class="chip"><span class="dot" id="dotStatus"></span><b id="stStatus">—</b></span>
      <span class="chip">الوضع: <b id="stMode">—</b></span>
      <span class="chip">الإطار: <b id="stTf">—</b></span>
      <span class="chip">Testnet: <b id="stTestnet">—</b></span>
      <span class="chip">التشغيل منذ: <b id="stUptime">—</b></span>
      <span class="chip">آخر تحديث: <b id="stNow" class="live">—</b></span>
    </div>
  </div>

  <div class="strip">
    <div class="box" id="boxEvening">🌙 نافذة المساء: <b>—</b></div>
    <div class="box" id="boxRisk">🛡️ مدير المخاطر: <b>—</b></div>
    <div class="box" id="boxHma">🧭 الاستراتيجية: <b>—</b></div>
    <div class="box" id="boxScan">🔭 المسح: <b>—</b></div>
  </div>

  <div class="ctl">
    <div class="ctl-t">⚡ التحكم والطوارئ <span class="ctl-note">الأمر يصل للبوت فوراً — الإيقاف يمنع الصفقات الجديدة فقط، وإدارة الصفقات المفتوحة والمخارج تستمر دائماً</span></div>
    <div class="ctl-b">
      <button class="cbtn stop" id="btnPause">⏸️ إيقاف التداول (طوارئ)</button>
      <button class="cbtn danger" id="btnCloseAll">🛑 إغلاق كل الصفقات</button>
      <button class="cbtn" id="btnScan">🔍 مسح فوري الآن</button>
      <button class="cbtn wipe" id="btnReset">🧹 إعادة ضبط شامل للوحة</button>
    </div>
  </div>

  <div class="cards">
    <div class="card"><div class="lbl">💵 الرصيد المتاح</div><div class="val num" id="cBal">—</div></div>
    <div class="card"><div class="lbl">📈 PnL اليوم</div><div class="val num" id="cPnl">—</div></div>
    <div class="card"><div class="lbl">📅 صفقات اليوم</div><div class="val" id="cToday">—</div></div>
    <div class="card"><div class="lbl">🏆 فوز / خسارة (إجمالي)</div><div class="val" id="cWL">—</div></div>
    <div class="card"><div class="lbl">🔓 مفتوحة / الحد المتزامن</div><div class="val" id="cOpen">—</div></div>
    <div class="card"><div class="lbl">🔭 الكون السائل</div><div class="val" id="cUni">—</div></div>
    <div class="card"><div class="lbl">🔁 عدد الدورات</div><div class="val num" id="cCycles">—</div></div>
    <div class="card"><div class="lbl">✍️ صفقات منفذة (إجمالي)</div><div class="val" id="cExec">—</div></div>
  </div>

  <div class="sec-t">🔓 المراكز المفتوحة الآن <span class="cnt" id="posCnt">0</span></div>
  <div id="posWrap"><div class="empty">لا توجد صفقات مفتوحة حالياً</div></div>

  <div class="sec-t">📋 سجل كل الحركات — كل صغيرة وكبيرة مع السبب</div>
  <div class="toolbar">
    <button class="fbtn on" data-k="الكل">الكل</button>
    <button class="fbtn" data-k="دخول">دخول</button>
    <button class="fbtn" data-k="خروج">خروج</button>
    <button class="fbtn" data-k="إشارة">إشارات</button>
    <button class="fbtn" data-k="رفض">أسباب الرفض</button>
    <button class="fbtn" data-k="مخاطر">مخاطر</button>
    <button class="fbtn" data-k="خطأ">أخطاء</button>
    <button class="fbtn" data-k="نظام">نظام</button>
    <input class="search" id="q" type="text" placeholder="🔎 ابحث في السجل (رمز، سبب، كلمة)...">
  </div>
  <div id="feed"></div>

  <div class="foot">
    اللوحة المدمجة V12.1 — تُحدَّث تلقائياً كل 3 ثوانٍ | كل حدث يُكتب أيضاً في ملف <span class="num">bot_events.jsonl</span> بجانب البوت للتدقيق الدائم<br>
    🕹️ أوامر التحكم (إيقاف/إغلاق/مسح شامل) تُنفَّذ عبر <span class="num">/api/command</span> ومحمية بنفس مفتاح <span class="num">DASHBOARD_TOKEN</span> — ضع مفتاحاً قوياً إذا كانت اللوحة على نطاق عام<br>
    التوقيت المعروض بتوقيت ليبيا (UTC+2) | البوت يعمل حتى لو أُغلقت هذه الصفحة
  </div>
</div>

<script>
var curKind='الكل', q='';
var lastState=null;
function fmtN(x,d){ if(x===undefined||x===null||isNaN(x)) return '—'; return Number(x).toLocaleString('en-US',{minimumFractionDigits:d||0,maximumFractionDigits:(d===undefined?2:d)}); }
function sgn(x){ return (x>0?'+':'') + fmtN(x,2); }
function cls(x){ return x>0?'g':(x<0?'r':''); }
function libyaT(ts){
  try{ return new Intl.DateTimeFormat('ar-LY',{timeZone:'Africa/Tripoli',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false}).format(new Date(ts*1000)); }
  catch(e){ return new Date(ts*1000).toISOString().substr(11,8); }
}
function esc(s){ return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function render(s){
  var st=s.state||{};
  lastState=st;
  document.getElementById('stStatus').textContent = st.status||'—';
  var dot=document.getElementById('dotStatus');
  dot.className='dot' + (st.status==='يعمل'?'':(st.status?' warn':' off'));
  document.getElementById('stMode').textContent = st.mode||'—';
  document.getElementById('stTf').textContent = st.hma_timeframe||'—';
  document.getElementById('stTestnet').textContent = st.testnet? 'نعم 🧪':'لا';
  document.getElementById('stUptime').textContent = (st.uptime_h!=null? st.uptime_h+' ساعة':'—');
  document.getElementById('stNow').textContent = libyaT(s.now);
  var bp=document.getElementById('btnPause');
  if(st.trade_enabled===false){ bp.textContent='▶️ استئناف التداول'; bp.classList.add('paused'); }
  else{ bp.textContent='⏸️ إيقاف التداول (طوارئ)'; bp.classList.remove('paused'); }

  var ev=document.getElementById('boxEvening');
  if(st.evening_block){
    if(st.evening_blocked_now){ ev.className='box night'; ev.innerHTML='🌙 حظر نافذة المساء <b>سارٍ الآن</b> — الدخول الجديد معطل ('+esc(st.evening_window||'')+'). المخارج تعمل طبيعياً.'; }
    else{ ev.className='box open'; ev.innerHTML='✅ خارج نافذة الحظر — الدخول متاح. النافذة المحظورة: <b>'+esc(st.evening_window||'')+'</b>.'; }
  } else { ev.className='box open'; ev.innerHTML='ℹ️ حظر نافذة المساء <b>معطل</b> (HMA_BLOCK_EVENING=false).'; }

  var rk=document.getElementById('boxRisk');
  if(st.risk_ok===false){ rk.className='box risk-bad'; rk.innerHTML='🛡️ مدير المخاطر: <b>يمنع الدخول الآن</b> — '+esc(st.risk_reason||''); }
  else { rk.className='box open'; rk.innerHTML='🛡️ مدير المخاطر: <b>سليم</b> — '+esc(st.risk_reason||'التداول مسموح'); }

  var hm=document.getElementById('boxHma');
  var hmaTxt = st.hma_enabled? (st.hma_live? '⚔️ تداول فعلي':'👁️ إشارات فقط') : '⏸️ معطلة';
  hm.className='box'; hm.innerHTML='🧭 HMA_DMI_MOMENTUM: <b>'+esc(hmaTxt)+'</b> | الصفقات المتزامنة القصوى: <b>'+fmtN(st.max_open_trades,0)+'</b>';

  var sc=document.getElementById('boxScan');
  var ls=st.last_hma_scan||{};
  sc.className='box';
  sc.innerHTML='🔭 آخر دفعة HMA: فحص <b>'+fmtN(ls.scanned,0)+'</b> زوج | إشارات <b>'+fmtN(ls.signals,0)+'</b> | مخارج <b>'+fmtN(ls.exits,0)+'</b> | الكون: <b>'+fmtN(st.universe_count,0)+'</b>';

  document.getElementById('cBal').textContent = '$'+fmtN(st.balance,2);
  var dp=st.daily_pnl||0;
  var pe=document.getElementById('cPnl'); pe.textContent=sgn(dp)+' $'; pe.className='val num '+cls(dp);
  document.getElementById('cToday').textContent = fmtN(st.trades_today,0);
  var wl=document.getElementById('cWL');
  wl.innerHTML='<span class="g">'+fmtN(st.wins,0)+'</span> / <span class="r">'+fmtN(st.losses,0)+'</span>';
  document.getElementById('cOpen').innerHTML = fmtN(st.open_count,0)+' <span style="color:var(--dim);font-size:13px">/ '+fmtN(st.max_open_trades,0)+'</span>';
  document.getElementById('cUni').textContent = fmtN(st.universe_count,0);
  document.getElementById('cCycles').textContent = fmtN(st.cycles,0);
  document.getElementById('cExec').textContent = fmtN(st.trades_executed,0);

  /* المراكز */
  var ps=st.positions||[];
  document.getElementById('posCnt').textContent=ps.length;
  var pw=document.getElementById('posWrap');
  if(!ps.length){ pw.innerHTML='<div class="empty">لا توجد صفقات مفتوحة حالياً</div>'; }
  else{
    var h='<table><thead><tr><th>الرمز</th><th>الاتجاه</th><th>الدخول</th><th>السعر الآن</th><th>الهامش</th><th>PnL عائم</th><th>%</th><th>SL</th><th>TP1</th><th>العمر (ساعة)</th><th>ستوب المنصة</th><th>الثقة</th><th>إجراء</th></tr></thead><tbody>';
    for(var i=0;i<ps.length;i++){ var p=ps[i];
      h+='<tr><td class="sym">'+esc(p.symbol)+'</td>'
        +'<td class="'+(p.side==='BUY'?'side-buy':'side-sell')+'">'+(p.side==='BUY'?'▲ شراء':'▼ بيع')+'</td>'
        +'<td class="num">'+esc(p.entry)+'</td><td class="num">'+esc(p.current)+'</td>'
        +'<td class="num">$'+fmtN(p.margin,2)+'</td>'
        +'<td class="num '+cls(p.pnl)+'">'+sgn(p.pnl)+'</td>'
        +'<td class="num '+cls(p.pnl_pct)+'">'+sgn(p.pnl_pct)+'%</td>'
        +'<td class="num">'+esc(p.sl)+'</td><td class="num">'+esc(p.tp)+'</td>'
        +'<td class="num">'+fmtN(p.age_h,1)+'</td>'
        +'<td><span class="pill '+(p.stop_state==='verified'?'ok':(p.stop_state==='placed'?'pl':(p.stop_state==='local'?'loc':'none')))+'">'+(p.stop_state==='verified'?'مؤكد ✓':(p.stop_state==='placed'?'مثبت':(p.stop_state==='local'?'مراقبة محلية':'—')))+'</span></td>'
        +'<td class="num">'+(p.score!=null? esc(p.score)+'/9':'—')+'</td>'
        +'<td><button class="rowbtn" data-act="close_one" data-sym="'+esc(p.symbol)+'">🛑 إغلاق</button>'
        +(p.stop_state!=='verified'? ' <button class="rowbtn retry" data-act="stop_retry" data-sym="'+esc(p.symbol)+'" title="إعادة محاولة تثبيت ستوب المنصة">🔁</button>':'')+'</td></tr>';
    }
    pw.innerHTML=h+'</tbody></table>';
  }
}

function renderFeed(s){
  var evs=s.events||[];
  var f=document.getElementById('feed');
  var html='';
  for(var i=evs.length-1;i>=0;i--){
    var e=evs[i];
    var sym=e.symbol? '<span class="s">'+esc(e.symbol)+'</span>':'';
    var rsn=e.reason? '<div class="rsn"><b>السبب:</b> '+esc(e.reason)+'</div>':'';
    var d=e.detail? '<div class="more">'+esc(e.detail)+'</div>':'';
    html+='<div class="ev'+(e.detail?' dtl':'')+'" data-k="'+esc(e.kind)+'">'
        +'<div class="top"><span class="t">'+libyaT(e.t)+'</span>'
        +'<span class="k k-'+esc(e.kind)+'">'+esc(e.kind)+'</span>'+sym
        +'<span class="m">'+esc(e.msg)+'</span></div>'+rsn+d+'</div>';
  }
  f.innerHTML=html||'<div class="empty">لا أحداث بعد — أول دورة مسح قادمة</div>';
  applyFilter();
}

function applyFilter(){
  var items=document.querySelectorAll('#feed .ev');
  for(var i=0;i<items.length;i++){
    var okK=(curKind==='الكل'||items[i].getAttribute('data-k')===curKind);
    var okQ=!q||items[i].textContent.indexOf(q)>=0;
    items[i].style.display=(okK&&okQ)?'':'none';
  }
}
document.querySelectorAll('.fbtn').forEach(function(b){
  b.addEventListener('click',function(){
    document.querySelectorAll('.fbtn').forEach(function(x){x.classList.remove('on')});
    b.classList.add('on'); curKind=b.getAttribute('data-k'); applyFilter();
  });
});
document.getElementById('q').addEventListener('input',function(){ q=this.value.trim(); applyFilter(); });
document.getElementById('feed').addEventListener('click',function(ev){
  var el=ev.target.closest('.ev.dtl'); if(el) el.classList.toggle('open');
});

/* ═══ 🕹️ أوامر التحكم — نفس دلالات لوحة V11.3 القديمة ═══ */
async function cmd(action, sym){
  try{
    var body={action:action}; if(sym) body.symbol=sym;
    var r=await fetch('/api/command?key='+encodeURIComponent(KEY),
      {method:'POST', headers:{'Content-Type':'text/plain;charset=UTF-8'}, body:JSON.stringify(body)});
    if(r.status===401){
      skipAsk=false;
      document.getElementById('stNow').textContent='🔒 اضغط هنا لإدخال المفتاح';
      alert('🔒 الأوامر محمية بمفتاح (DASHBOARD_TOKEN).\\nاضغط على "آخر تحديث" أعلى الصفحة لإدخال المفتاح ثم أعد الأمر.');
      return;
    }
    var j=await r.json();
    alert((j.ok?'✅ ':'❌ ')+(j.info||j.error||'تم الأمر'));
    tick();
  }catch(e){ alert('❌ فشل الاتصال بالبوت: '+e.message); }
}
document.getElementById('btnPause').addEventListener('click',function(){
  var running=!(lastState&&lastState.trade_enabled===false);
  if(running){
    if(confirm('⏸️ إيقاف التداول (طوارئ)؟\\n\\nلن تُفتح أي صفقة جديدة.\\nإدارة الصفقات المفتوحة والمخارج تستمر طبيعياً.\\n(بعد إعادة تشغيل البوت يعود الوضع حسب متغير TRADE_ENABLED)')) cmd('pause');
  }else{
    if(confirm('▶️ استئناف التداول؟\\n\\nستُفتح صفقات جديدة حسب إشارات الاستراتيجية مجدداً.')) cmd('resume');
  }
});
document.getElementById('btnCloseAll').addEventListener('click',function(){
  if(confirm('⚠️ إغلاق كل الصفقات المفتوحة فوراً بسعر السوق؟')) cmd('close_all');
});
document.getElementById('btnScan').addEventListener('click',function(){ cmd('scan_now'); });
document.getElementById('btnReset').addEventListener('click',function(){
  var NL=String.fromCharCode(10);
  var msg='⚠️ إعادة ضبط شامل للوحة!'+NL+NL
    +'سيتم مسح:'+NL
    +'📋 سجل كل الأحداث (الشاشة + ملف bot_events.jsonl)'+NL
    +'📂 سجل الصفقات والإشارات'+NL
    +'🚫 سجل أسباب الرفض'+NL
    +'📊 الإحصائيات اليومية والإجماليات'+NL
    +'🚨 عدّادات الأخطاء'+NL+NL
    +'✅ لن تُغلق أي صفقة مفتوحة'+NL
    +'❌ لا يمكن التراجع! متابعة؟';
  if(!confirm(msg)) return;
  if(!confirm('❓ تأكيد أخير: هل أنت متأكد 100% من المسح الكامل؟')) return;
  cmd('reset_all');
});
document.getElementById('posWrap').addEventListener('click',function(ev){
  var b=ev.target.closest? ev.target.closest('.rowbtn') : null; if(!b) return;
  var act=b.getAttribute('data-act'), sym=b.getAttribute('data-sym');
  if(act==='close_one'){ if(confirm('🛑 إغلاق صفقة '+sym+' فوراً بسعر السوق؟')) cmd('close_one', sym); }
  else if(act==='stop_retry'){ if(confirm('🔁 إعادة محاولة تثبيت ستوب المنصة لصفقة '+sym+'؟')) cmd('stop_retry', sym); }
});

var KEY=''; try{ KEY=localStorage.getItem('dashKey')||''; }catch(e){}
var skipAsk=false;
document.getElementById('stNow').style.cursor='pointer';
document.getElementById('stNow').title='اضغط لإدخال/تغيير مفتاح اللوحة';
async function tick(){
  try{
    var r=await fetch('/api/state?limit=400&key='+encodeURIComponent(KEY),{cache:'no-store'});
    if(r.status===401){
      if(!skipAsk){
        skipAsk=true;
        var k=prompt('🔒 اللوحة محمية بمفتاح (DASHBOARD_TOKEN). أدخل المفتاح:');
        if(k!=null&&k.trim()){ KEY=k.trim(); try{ localStorage.setItem('dashKey',KEY); }catch(e){} }
      }
      document.getElementById('stNow').textContent='🔒 اضغط هنا لإدخال المفتاح';
      return;
    }
    skipAsk=false;
    var s=await r.json();
    render(s); renderFeed(s);
  }catch(e){
    document.getElementById('stNow').textContent='⚠️ انقطاع الاتصال بالبوت';
  }
}
tick(); setInterval(tick,3000);
document.getElementById('stNow').addEventListener('click',function(){ skipAsk=false; });
</script>
</body>
</html>
"""


#        🎯 القناص الأسطوري V12.0 — البوت الرئيسي (استراتيجية HMA فقط)
# ══════════════════════════════════════════════════════════════════════
class LegendarySniperHMA:
    def __init__(self):
        self.binance_api_key = os.environ.get('BINANCE_API_KEY', '')
        self.binance_api_secret = os.environ.get('BINANCE_API_SECRET', '')

        self.TRADE_ENABLED = os.environ.get('TRADE_ENABLED', 'false').lower() == 'true'
        self.LEVERAGE = int(os.environ.get('LEVERAGE', '10'))
        self.TRADE_SIZE_USDT = float(os.environ.get('TRADE_SIZE_USDT', '25'))
        self.MIN_WIN_USDT = float(os.environ.get('MIN_WIN_USDT', '0'))   # أرضية اختيارية لهدف الربح (0 = معطلة)
        # 🔓 إصلاح الاختناق (اعتماد المالك — تقرير التشخيص): كان الحد 1 ويخنق
        # الاستراتيجية إلى الصفر تقريباً. الافتراضي الآن 3 صفقات متزامنة
        # (هامش 25$ لكل صفقة) — قابل للتغيير بمتغير MAX_OPEN_TRADES (1-10).
        self.MAX_OPEN_TRADES = int(os.environ.get('MAX_OPEN_TRADES', '3'))
        self.TESTNET = os.environ.get('TESTNET', 'false').lower() == 'true'

        problems = []
        if self.TRADE_SIZE_USDT <= 0:
            problems.append("TRADE_SIZE_USDT يجب أن يكون أكبر من صفر")
        if self.MIN_WIN_USDT < 0:
            problems.append("MIN_WIN_USDT يجب أن يكون صفراً أو أكثر")
        if not (1 <= self.MAX_OPEN_TRADES <= 10):
            problems.append("MAX_OPEN_TRADES يجب أن يكون بين 1 و 10")
        if not (1 <= self.LEVERAGE <= 50):
            problems.append("LEVERAGE يجب أن يكون بين 1 و 50")
        if problems:
            raise SystemExit("❌ إعدادات خاطئة:\n- " + "\n- ".join(problems))
        if self.TESTNET:
            logger.info("🧪 وضع Testnet التجريبي مفعّل — كل التنفيذ تجريبي")

        if self.TRADE_ENABLED and (not self.binance_api_key or not self.binance_api_secret):
            self.TRADE_ENABLED = False
            logger.error("❌ التداول مفعّل لكن مفاتيح API ناقصة! التحويل للمراقبة فقط")

        self.PRICE_MAX_AGE = 30          # أقصى عمر مقبول لسعر الدخول — لا صفقة بأسعار قديمة
        self.REENTRY_COOLDOWN = 900      # تبريد 15 دقيقة لكل زوج بعد إغلاق صفقة
        self.VERIFY_EVERY_N_LOOPS = 5
        self.WS_STALE_ALERT = 120
        self.BALANCE_CACHE_SECONDS = 60

        self.data_url = "https://fapi.binance.com"
        self.trade_url = ("https://testnet.binancefuture.com" if self.TESTNET
                          else "https://fapi.binance.com")
        self.time_offset_ms = 0

        self.db = DatabaseManager()
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
        self._balance_cache = (0.0, 0.0)
        self._rest_price_ts = {}
        self._last_reject_log = {}       # خنق سجل الرفض: (رمز، سبب) → آخر وقت

        self.hma = HMASettings(self.db)        # كل عتبات HMA_DMI_MOMENTUM
        self.risk = RiskManager(self.db)
        self.news_filter = NewsFilter(self.db)

        # 🕹️ أوامر اللوحة: حدث "مسح فوري" يوقظ الحلقة فوراً (يُستدعى من نفس
        # الحلقة عبر DASH_BRIDGE لذا asyncio.Event آمن هنا)
        self._scan_now_evt = asyncio.Event()

        self.stats = {'total_scans': 0, 'trades_executed': 0, 'wins': 0, 'losses': 0,
                      'total_signals': 0, 'signals_found': 0,
                      'rejected_by_risk': 0, 'rejected_by_news': 0,
                      'rejected_open_trade': 0, 'rejected_quality': 0,
                      'rejected_execution': 0}

        self.api_rejected = None         # 🚨 علم رفض مفاتيح API (-2015) للوحة

        self.HMA_LIVE = os.environ.get('HMA_LIVE', 'false').lower() == 'true'  # 🧭 يُدار من اللوحة أيضاً
        self.MAX_TRADE_HOURS = float(os.environ.get('TRADE_MAX_HOURS', '24'))   # ⏰ ستوب زمني — V11.1: 24س (المُتحقق عليه للاستراتيجيتين — راجع تقرير إعادة البناء)
        self._universe_cache = []
        self._universe_ts = 0.0
        self._scan_cursor = 0
        self._ticker_cache = {}          # الرمز → {'qv','change'} من آخر مسح
        self._closing = set()            # مراكز قيد الإغلاق الآن — منع أوامر إغلاق مكررة
        self._recent_entry = {}          # الرمز → وقت آخر دخول (حماية تبنّي اليتيمة من التداخل)

        # 🧭 حالة استراتيجية HMA_DMI_MOMENTUM
        self.hma_enabled = os.environ.get('HMA_ENABLED', 'true').lower() != 'false'
        self._hma_done = {}              # (رمز، اتجاه، شمعة الإشارة) → منع التكرار — يصمد لإعادة التشغيل
        self._hma_last_signal_ms = {}    # الرمز → شمعة آخر إشارة HMA معالجة (أساس تبريد الإشارات)
        self._hma_cursor = 0             # مؤشر الدوران على كون HMA
        self.hma_states = {}             # الرمز → آخر حالة آلة الحالات المكتشفة (للعرض)
        self.last_hma_scan_info = None

    # ═══ نظام مكافحة الصمت ═══
    def _notify_error(self, source, exc=None, context=""):
        count = self.error_counts.get(source, 0) + 1
        self.error_counts[source] = count
        txt = f"⚠️ {source}" + (f" — {context}" if context else "")
        if exc is not None:
            txt += f" | `{str(exc)[:100]}`"
        logger.warning(f"{txt} (تكرار #{count})")
        ACTION.log('خطأ', msg=txt, reason=f"تكرار #{count}")
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
        """كل إشعار يذهب للوحة."""
        try:
            first_line = msg.split('\n')[0].replace('*', '').strip()
            kind = 'info'
            if msg.startswith('✅') or 'صفقة' in first_line and 'منفذة' in first_line:
                kind = 'trade'
            elif msg.startswith('🎯') or 'إشارات' in first_line:
                kind = 'signal'
            elif msg.startswith('🏁') or 'إغلاق' in first_line:
                kind = 'close'
            elif msg.startswith('🚨') or 'خطأ' in first_line or msg.startswith('⚠️'):
                kind = 'error'
            elif msg.startswith('🛑') or msg.startswith('⚙️') or msg.startswith('📰') or msg.startswith('🔭'):
                kind = 'system'
            kind_map = {'trade': 'دخول', 'signal': 'إشارة', 'close': 'خروج',
                        'error': 'خطأ', 'system': 'نظام', 'info': 'نظام'}
            ACTION.log(kind_map.get(kind, 'نظام'), msg=first_line, detail=msg)
        except Exception:
            pass

    # ═══ توقيت الخادم + طبقة Binance API ═══
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

    async def _fapi_request(self, method, endpoint, params=None, signed=False, retries=3,
                            quiet=(), soft=(), detailed=False):
        """مع detailed=True يعيد عند الفشل {'_error','_status','_code','_msg'}
        بكود رفض Binance الحقيقي — أساس تشخيص فشل الأوامر في اللوحة."""
        last_err = None
        for attempt in range(max(1, retries)):
            try:
                url = f"{self.trade_url}{endpoint}"
                headers = {'X-MBX-APIKEY': self.binance_api_key} if signed else {}
                req_params = self._sign(dict(params) if params else {}) if signed else params

                async with self.session.request(method, url, params=req_params,
                                                headers=headers, timeout=15) as r:
                    if r.status == 200:
                        if signed and getattr(self, 'api_rejected', None):
                            self.api_rejected = None
                        return await r.json()
                    body = await r.text()
                    code, msg = None, body[:200]
                    try:
                        j = json.loads(body)
                        if isinstance(j, dict):
                            code = j.get('code')
                            msg = str(j.get('msg', body))[:200]
                    except Exception:
                        pass
                    last_err = {'_error': True, '_status': r.status, '_code': code, '_msg': msg}

                    if r.status in (429, 418):
                        await asyncio.sleep(10 * (attempt + 1))
                        continue
                    if r.status == 401:
                        if detailed:
                            return last_err
                        code_401 = last_err.get('_code') if isinstance(last_err, dict) else None
                        if code_401 == -2015:
                            if self.api_rejected is None:
                                self.api_rejected = time.time()
                                logger.error("═" * 62)
                                logger.error("🚨 Binance يرفض مفاتيح API (رمز -2015) — لهذا يظهر الرصيد $0.00")
                                logger.error("المفاتيح يجب أن تكون من testnet.binancefuture.com (فوتشرز) وليس من موقع بينانس الحقيقي")
                                logger.error("الحل: testnet.binancefuture.com ← API Key ← Create HMAC_SHA256 ← Railway Variables ← إعادة نشر")
                                logger.error("═" * 62)
                            self._notify_error("🚨 مفاتيح API مرفوضة (-2015)",
                                context="المفاتيح يجب أن تكون من testnet.binancefuture.com (فوتشرز)")
                        else:
                            self._notify_error("خطأ 401 من Binance",
                                context=f"مفاتيح خاطئة أو مقيدة بـIP | الرد الخام: {body[:200]}")
                        return None
                    if '-1021' in body:
                        logger.warning("⚠️ خطأ توقيم -1021 — مزامنة الوقت وإعادة المحاولة")
                        await self.sync_server_time()
                        await asyncio.sleep(1)
                        continue
                    if r.status >= 500:
                        logger.warning(f"Futures API {r.status} — إعادة محاولة...")
                        await asyncio.sleep(2 ** attempt)
                        continue
                    for c in soft:
                        if str(c) in body:
                            return {'_soft_code': c}
                    if any(str(c) in body for c in quiet):
                        return None
                    if detailed:
                        return last_err
                    logger.warning(f"Futures API Error {r.status}: {body[:120]}")
                    return None
            except asyncio.TimeoutError:
                last_err = {'_error': True, '_status': 0, '_code': None, '_msg': 'timeout'}
                if attempt == max(1, retries) - 1:
                    if detailed:
                        return last_err
                    self._notify_error("انتهت مهلة طلب Binance", context=endpoint)
                    return None
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                last_err = {'_error': True, '_status': 0, '_code': None, '_msg': str(e)[:200]}
                if attempt == max(1, retries) - 1:
                    if detailed:
                        return last_err
                    self._notify_error("فشل طلب Binance", exc=e, context=endpoint)
                    return None
                await asyncio.sleep(2 ** attempt)
        return last_err if detailed else None

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

    # ═══ أدوات التنسيق الدقيق (كمية/سعر حسب قواعد Binance) ═══
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

    async def _refresh_price_rest(self, symbol):
        """عند تجمّد تدفق WebSocket: جلب bid/ask مباشرة من REST."""
        try:
            res = await self._fapi_request('GET', '/fapi/v1/ticker/bookTicker',
                                           {'symbol': symbol})
            if isinstance(res, dict):
                bid = float(res.get('bidPrice') or 0)
                ask = float(res.get('askPrice') or 0)
                if bid > 0 and ask > 0:
                    self.live_prices[symbol] = {'bid': bid, 'ask': ask, 'ts': time.time()}
                    return self.live_prices[symbol]
            res2 = await self._fapi_request('GET', '/fapi/v1/ticker/price',
                                            {'symbol': symbol})
            if isinstance(res2, dict):
                last = float(res2.get('price') or 0)
                if last > 0:
                    self.live_prices[symbol] = {'bid': last, 'ask': last, 'ts': time.time()}
                    return self.live_prices[symbol]
        except Exception:
            pass
        return None

    def set_cooldown(self, symbol):
        self.reentry_cooldown[symbol] = time.time() + self.REENTRY_COOLDOWN

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
        res = await self._fapi_request('GET', '/fapi/v2/balance', signed=True)
        avail = 0.0
        if isinstance(res, list):
            for b in res:
                if b.get('asset') == 'USDT':
                    avail = float(b.get('availableBalance', 0))
                    break
        self._balance_cache = (avail, now)
        return avail

    # ═══ WebSocket ═══
    async def ws_manager(self):
        ws_url = ("wss://stream.binancefuture.com/ws/!bookTicker" if self.TESTNET
                  else "wss://fstream.binance.com/ws/!bookTicker")
        while True:
            try:
                async with websockets.connect(ws_url, ping_interval=20) as ws:
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
        data = await self._fapi_request('GET', '/fapi/v1/klines',
            {'symbol': symbol, 'interval': interval, 'limit': limit})
        if data and len(data) > 20:
            df = pd.DataFrame(data, columns=[
                'time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_vol',
                'taker_buy_quote_vol', 'ignore'])
            for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            return df
        return None

    @staticmethod
    def _compute_atr(df, period=14):
        hl = df['high'] - df['low']
        hc = (df['high'] - df['close'].shift()).abs()
        lc = (df['low'] - df['close'].shift()).abs()
        tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
        return float(tr.rolling(period).mean().iloc[-1])

    # ═══ 🎯 هدف TP1: عائد مرتبط بالهامش ═══
    def _tp1_target_profit(self, margin):
        """الربح المستهدف بالدولار: tp1_return_pct% من الهامش المعطى
        (وأرضية اختيارية MIN_WIN_USDT إن وُجدت)."""
        pct = self.hma.tp1_return_pct
        target = float(margin) * pct / 100.0
        if self.MIN_WIN_USDT > 0:
            target = max(target, self.MIN_WIN_USDT)
        return target

    def _tp1_distance(self, price):
        """
        ⚠️ تقدير ما قبل التنفيذ فقط (يُستخدم في بوابات R:R قبل فتح الصفقة).
        المسافة السعرية التي تحقق ربحاً ≈ tp1_return_pct% من الهامش المخطط.
        بعد التنفيذ يُعاد الحساب من بيانات التنفيذ الفعلية عبر
        _tp1_distance_from_actual (كمية/سعر/رافعة ما بعد التقريب من المنصة).
        الربح = qty × المسافة = (margin×leverage/price) × dist
        ⟹ dist = price × الربح المستهدف / (margin × leverage)
        """
        try:
            margin = self.TRADE_SIZE_USDT
            lev = self.LEVERAGE
            notional = margin * lev
            if notional <= 0 or price <= 0:
                return 0.0
            target = self._tp1_target_profit(margin)
            return price * target / notional
        except Exception:
            return 0.0

    def _tp1_distance_from_actual(self, entry_price, qty, leverage):
        """🎯 هدف TP1 من بيانات التنفيذ الفعلية (بعد تقريب Binance):
        الهامش الفعلي = qty × السعر الفعلي / الرافعة الفعلية
        الربح المستهدف = الهامش الفعلي × tp1_return_pct/100
        المسافة = الربح المستهدف / الكمية الفعلية المنفذة
        كي يتحقق دائماً: (qty × المسافة) / الهامش الفعلي = pct% بالضبط."""
        try:
            entry_price = float(entry_price)
            qty = float(qty)
            leverage = float(leverage)
            if entry_price <= 0 or qty <= 0 or leverage <= 0:
                return 0.0
            margin = qty * entry_price / leverage
            return self._tp1_target_profit(margin) / qty
        except Exception:
            return 0.0

    def _round_tp_price(self, symbol, tp, side):
        """تقريب سعر الهدف على Tick ببعيداً عن الدخول كي لا ينقص الهدف بالتقريب:
        BUY → لأعلى | SELL → لأدنى (وفق قواعد دقة Binance)."""
        try:
            tp = float(tp)
        except (TypeError, ValueError):
            return tp
        tick = self.tick_sizes_cache.get(symbol)
        if not tick or tick <= 0:
            return tp
        dec = self._decimals_of(tick)
        ratio = round(tp / tick, 9)
        steps = math.ceil(ratio) if side == 'BUY' else math.floor(ratio)
        return round(steps * tick, dec)

    # 🧭 استراتيجية HMA_DMI_MOMENTUM — مسار مستقل بمنطقه الخاص، مع تنفيذ
    #    مشترك عبر نفس بوابات المخاطر/الرصيد/الحد الأقصى (execute_trade).
    # ═══════════════════════════════════════════════════════════════════
    def _strategy_display(self, strategy):
        return HMA_STRATEGY_NAME

    def _symbol_owner(self, symbol):
        """استراتيجية مالك الصفقة المفتوحة على الرمز (أو None) — أساس
        سياسة التعارض: مركز واحد لكل رمز، والصفقة يملكها من فتحها."""
        t = self.active_trades.get(symbol)
        return (t.get('strategy') or HMA_STRATEGY_NAME) if t else None

    async def analyze_hma(self, symbol):
        """تحليل زوج باستراتيجية HMA_DMI_MOMENTUM على شموع مغلقة فقط.
        يعيد (إشارة|None، سبب رفض|None، معلومات_حالة|None) — السبب يُسجَّل
        في القاعدة موسوماً بالاستراتيجية ويُعرض في اللوحة."""
        h = self.hma
        tf = h.timeframe
        # ⛔ فلتر V11.3: أزواج خاسرة مزمنة على النافذتين المستقلتين معاً —
        # مستبعدة من HMA بالكامل (اعتماد المالك). صفقات HMA المفتوحة سابقاً
        # تُدار بمخارجها حتى الإغلاق (هذا المسار للإشارات الجديدة فقط).
        if symbol in HMA_SYMBOL_BLACKLIST:
            return None, 'زوج مستبعد من HMA (فلتر V11.3 — خاسر مزمن على النافذتين)', None
        # 🌙 حظر نافذة المساء (اعتماد المالك — تقرير تشخيص HMA): الدخول الجديد
        # معطل 16:00–23:59 UTC (النافذة الأكثر خسارة موثقاً). المخارج تعمل.
        if HMA_BLOCK_EVENING_UTC and self._hma_evening_blocked_now():
            return None, ('🌙 حظر نافذة المساء — الدخول الجديد معطل '
                          f'({HMA_EVENING_START_UTC}:00–{HMA_EVENING_END_UTC}:59 UTC)'), None
        try:
            # 🧭 700 شمعة عند تفعيل بوابة 4س على إطار 1س: تغذي المحرك والبوابة
            # معاً — المحرك سببي ومقيّد بإعادة التشغيل فلا يتأثر بتاريخ أطول،
            # وهو أقرب لتاريخ الباكتيست الكامل (وزن بذرة EMA50(4س) ≈ 0.09%).
            df = await self.get_klines(symbol, tf, 700 if h.trend4h_enabled else 400)
        except Exception:
            return None, 'فشل جلب الشموع', None
        if df is None or len(df) < 60:
            return None, 'بيانات شموع غير كافية', None
        df = df.iloc[:-1]        # ⛔ الشمعة الجارية خارج التحليل نهائياً (مغلقة فقط)
        if len(df) < 60:
            return None, 'بيانات مغلقة غير كافية', None

        ev = HmaDmiMomentumEngine.evaluate(df, h.as_params())
        if not ev.get('ok'):
            return None, ev.get('reject_reason') or 'تحليل غير مكتمل', None

        state_info = {'state': ev['state'], 'age': ev['state_age'],
                      'ts': time.time(), 'candle_ms': int(df['time'].iloc[-1])}

        sig = ev['signal']
        if not sig:
            return None, ev['reject_reason'], state_info
        side = sig['side']

        # 🧭 بوابة الاتجاهية V11.1: ADX-14 (إطار الاستراتيجية) ≥ adx_gate —
        # استبعاد السوق العرضي عند الدخول (مُتحقق عليها في مختبر إعادة البناء:
        # قلّصت خسائر HMA وحدها بنحو الثلث وحافظت على أفضلية النظام الساعي)
        ok_adx, adx_val = HmaDmiMomentumEngine.adx_entry_ok(
            ev['arrays'], ev['i'], h.adx_gate)
        if not ok_adx:
            if adx_val is not None:
                return None, (f'فلتر الاتجاهية ADX: السوق عرضي '
                              f'(ADX {adx_val:.1f} < {h.adx_gate:g})'), state_info
            return None, 'فلتر الاتجاهية ADX: قياس غير متاح', state_info

        # 🧭 بوابة اتجاه 4 ساعات (V11.3 — اعتماد المالك T3): اتجاه آخر شمعة
        # 4س مغلقة كلياً (EMA{len} على 4س + ميلها عبر آخر 3 شموع 4س) يجب أن
        # يحاذي الإشارة — نفس خوارزمية backtest._trend_4h حرفياً (بلا إعادة
        # رسم: الشمعة 4س الجارية لا تُلمس). 0 (محايد/غير جاهز) = رفض محافظ.
        if h.trend4h_enabled:
            want = 1 if side == 'BUY' else -1
            try:
                if tf == '1h':
                    gdf = df                       # نفس السلسلة المغلقة أعلاه (700 شمعة)
                else:
                    gdf = await self.get_klines(symbol, '1h', 700)
                    gdf = gdf.iloc[:-1] if gdf is not None else None  # ⛔ مغلقة فقط
                if gdf is None or len(gdf) < 240:
                    return None, 'بوابة اتجاه 4 ساعات: بيانات 1س غير كافية', state_info
                tv = int(_trend_4h(gdf, mode='ema_slope',
                                   ema_len=int(h.trend4h_ema_len))[-1])
            except Exception:
                return None, 'بوابة اتجاه 4 ساعات: فشل الحساب', state_info
            if tv != want:
                t_txt = {1: 'صاعد', -1: 'هابط'}.get(tv, 'محايد/غير جاهز')
                return None, (f'بوابة اتجاه 4 ساعات: الاتجاه {t_txt} لا يحاذي '
                              f'{"الشراء" if side == "BUY" else "البيع"} '
                              f'(EMA{int(h.trend4h_ema_len)} على 4س + الميل)'), state_info

        # ⑤ منع تكرار الإشارة لنفس شمعة الإشارة (يصمد لإعادة التشغيل)
        key = int(sig['candle_ms'])
        if self._hma_done.get((symbol, side, key)):
            return None, 'إشارة مكررة لنفس شمعة الإشارة', state_info

        # تبريد الإشارات: لا إشارة جديدة قبل cooldown_candles من آخر إشارة معالجة
        last_ms = self._hma_last_signal_ms.get(symbol, 0)
        tf_ms = HMASettings.TF_MS.get(tf, 900000)
        if last_ms and (key - last_ms) < h.cooldown_candles * tf_ms:
            return None, f'تبريد الإشارات ({h.cooldown_candles} شموع من آخر إشارة)', state_info

        # 💰 وقف الخسارة بعمق sl_atr_mult × ATR (إطار الاستراتيجية) + بوابات المخاطرة
        close = float(sig['close'])
        atr = float(sig['atr'])
        if not (atr and math.isfinite(atr) and atr > 0):
            return None, 'ATR غير صالح', state_info
        sl = close - h.sl_atr_mult * atr if side == 'BUY' else close + h.sl_atr_mult * atr
        if sl <= 0 or math.isnan(sl):
            return None, 'وقف خسارة غير صالح', state_info
        risk_dist = abs(close - sl)
        risk_pct = risk_dist / close * 100 if close > 0 else 0.0
        if risk_pct < h.risk_min_pct or risk_pct > h.risk_max_pct:
            return None, f'المسافة إلى وقف الخسارة غير مناسبة ({risk_pct:.2f}%)', state_info

        # 🎯 هدف TP1 (نسبة HMA) + جدوى العائد مقابل المخاطرة
        tp1_dist = self._tp1_distance(close)
        if tp1_dist <= 0:
            return None, 'فشل حساب هدف TP1', state_info
        if tp1_dist > h.tp1_max_atr * atr:
            return None, (f'هدف TP1 بعيد عن ظروف السوق '
                          f'({tp1_dist/atr:.1f}×ATR > {h.tp1_max_atr:g}×ATR)')
        rr = tp1_dist / risk_dist if risk_dist > 0 else 0.0
        if rr < h.min_rr:
            return None, f'العائد المحتمل غير مجدٍ (R:R = {rr:.2f} < {h.min_rr:g})', state_info

        tp1 = close + tp1_dist if side == 'BUY' else close - tp1_dist
        state_txt = f"{sig['state']} عمرها {ev['state_age']} شمعة"
        if sig['override']:
            head = (f"🧭 HMA_DMI_MOMENTUM: {side} عبر استثناء هيكلي — {state_txt}")
        else:
            head = f"🧭 HMA_DMI_MOMENTUM: {side} — {state_txt}"
        lines = [
            head,
            f"✅ الزناد: {sig['reason_txt']} (إطار {tf} — شموع مغلقة فقط)",
            f"📐 القوة {sig['power']:g}/100 | الثقة {sig['confidence']}/9 | زخم {sig['mom_conf']}/3"
            + (f" | ADX {adx_val:.1f} ✓" if adx_val is not None else "")
            + (" | فلتر EMA200 ✓" if h.ema_filter else "")
            + (" | بوابة 4س ✓" if h.trend4h_enabled else ""),
            f"🛡️ ستوب ATR ({h.sl_atr_mult:g}×) ({risk_pct:.2f}%) | R:R {rr:.2f}",
            f"💰 TP1 = {h.tp1_return_pct:g}% من الهامش ({self.fmt_price(tp1)}) — إغلاق 100% عند اللمس",
        ]
        analysis = {
            'symbol': symbol, 'direction': side, 'strategy': HMA_STRATEGY_NAME,
            'price': close, 'sl': sl, 'tp1': tp1,
            'score': int(sig['confidence']), 'hma_key': key,
            'validation': {'atr_1h': atr,     # ATR بإطار الاستراتيجية — يستخدمه فحص TP1 لحظة التنفيذ
                           'risk_min_pct': h.risk_min_pct,
                           'risk_max_pct': h.risk_max_pct},
            'components': {
                'engine': HMA_STRATEGY_NAME, 'trigger': sig['reason_txt'],
                'state': sig['state'], 'state_age': ev['state_age'],
                'timeframe': tf, 'power': round(sig['power'], 1),
                'confidence': int(sig['confidence']), 'override': bool(sig['override']),
                'mom_conf': int(sig['mom_conf']),
                'adx': (round(adx_val, 1) if adx_val is not None else None),
                'rr': round(rr, 2), 'risk_pct': round(risk_pct, 2),
                'score': int(sig['confidence']), 'candle_ms': key,
            },
            'lines': lines,
        }
        return analysis, None, state_info

    async def _hma_signal_only(self, a):
        """🧭 وضع الإشارات فقط لاستراتيجية HMA — تسجيل موسوم باسمها."""
        try:
            await self.db.log_signal(a['symbol'], a['direction'], time.time(),
                                     a['score'], a['components'],
                                     strategy=HMA_STRATEGY_NAME)
        except Exception:
            pass

    async def _mark_hma_done(self, a):
        """استهلاك إشارة HMA: (الرمز، الاتجاه، شمعة الإشارة) — يُحفظ في
        القاعدة فوراً كي لا تعود الإشارة نفسها بعد إعادة تشغيل البوت."""
        key = (a['symbol'], a['direction'], int(a['hma_key']))
        self._hma_done[key] = time.time()
        self._hma_last_signal_ms[a['symbol']] = max(
            self._hma_last_signal_ms.get(a['symbol'], 0), int(a['hma_key']))
        try:
            data = {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in self._hma_done.items()}
            await self.db.set_param('hma_done', json.dumps(data))
        except Exception as e:
            logger.warning(f"تعذر حفظ مفتاح تكرار HMA: {e}")

    async def _load_hma_done(self):
        self._hma_done = {}
        self._hma_last_signal_ms = {}
        raw = await self.db.get_param('hma_done')
        if raw:
            try:
                for k, v in json.loads(raw).items():
                    sym, side, cm = k.split('|')
                    self._hma_done[(sym, side, int(cm))] = float(v)
                    self._hma_last_signal_ms[sym] = max(
                        self._hma_last_signal_ms.get(sym, 0), int(cm))
            except Exception as e:
                logger.warning(f"تعذر استعادة سجل إشارات HMA: {e}")
        self._prune_hma_done()

    def _prune_hma_done(self):
        cutoff = time.time() - 48 * 3600
        self._hma_done = {k: v for k, v in self._hma_done.items() if v > cutoff}

    # ═══ 🌙 نافذة حظر الدخول المسائية (اعتماد المالك — تقرير تشخيص HMA) ═══
    def _hma_evening_blocked_now(self):
        """هل نحن الآن داخل نافذة حظر الدخول المسائية (UTC)؟
        حظر الدخول الجديد فقط — إدارة مخارج الصفقات المفتوحة تعمل دائماً."""
        try:
            hour = time.gmtime().tm_hour
            if HMA_EVENING_START_UTC <= HMA_EVENING_END_UTC:
                return HMA_EVENING_START_UTC <= hour <= HMA_EVENING_END_UTC
            return hour >= HMA_EVENING_START_UTC or hour <= HMA_EVENING_END_UTC
        except Exception:
            return False

    # ═══ 📊 اللوحة المدمجة — التشغيل ومزامنة الحالة (عرض فقط، بلا تأثير في التداول) ═══
    def _start_dashboard(self):
        if not DASHBOARD_ENABLED:
            logger.info("📊 اللوحة المدمجة معطلة (DASHBOARD_ENABLED=false)")
            return
        try:
            ACTION.bind(self)
            srv = ThreadingHTTPServer(('0.0.0.0', DASHBOARD_PORT), _DashboardHandler)
            th = threading.Thread(target=srv.serve_forever, kwargs={'poll_interval': 0.5},
                                  daemon=True, name='dashboard')
            th.start()
            logger.info(f"📊 لوحة المراقبة المدمجة تعمل: http://0.0.0.0:{DASHBOARD_PORT}/")
            ACTION.log('نظام', msg=f'لوحة المراقبة المدمجة تعمل على المنفذ {DASHBOARD_PORT}')
        except Exception as e:
            logger.error(f"فشل تشغيل اللوحة المدمجة: {e}")

    def _action_positions_snapshot(self):
        """لقطة المراكز المفتوحة للعرض: السعر الحي + الربح العائم + عمر الصفقة."""
        out = []
        for sym, t in list(self.active_trades.items()):
            try:
                p = self.get_price(sym) or {}
                bid = float(p.get('bid') or 0)
                ask = float(p.get('ask') or 0)
                cur = (bid if t['side'] == 'BUY' else ask) or float(t['entry_price'])
                if cur <= 0:
                    cur = float(t['entry_price'])
                diff = (cur - float(t['entry_price'])) if t['side'] == 'BUY' \
                    else (float(t['entry_price']) - cur)
                margin = (float(t['quantity']) * float(t['entry_price'])
                          / max(1.0, float(self.LEVERAGE)))
                float_pnl = diff * float(t['quantity'])
                out.append({
                    'symbol': sym, 'side': t['side'],
                    'strategy': self._strategy_display(t.get('strategy')),
                    'entry': float(t['entry_price']), 'current': float(cur),
                    'qty': float(t['quantity']), 'margin': round(margin, 2),
                    'pnl': round(float_pnl, 4),
                    'pnl_pct': (round(float_pnl / margin * 100, 2) if margin > 0 else 0.0),
                    'sl': float(t.get('sl') or 0), 'tp': float(t.get('tp') or 0),
                    'age_h': round((time.time() - float(t.get('entry_time', time.time()))) / 3600.0, 1),
                    'stop_state': t.get('stop_state', 'none'),
                    'score': t.get('score'),
                })
            except Exception:
                continue
        return out

    async def _action_sync(self, loop_count):
        """مزامنة حالة اللوحة المدمجة كل دورة (عرض فقط — بلا أي تأثير على
        منطق التداول): المراكز الحية، الرصيد، إحصاءات اليوم، نافذة المساء."""
        try:
            try:
                balance = await self.get_available_usdt()
            except Exception:
                balance = self._balance_cache[0] if self._balance_cache else 0.0
            can_trade, risk_reason = self.risk.can_trade()
            evening_now = HMA_BLOCK_EVENING_UTC and self._hma_evening_blocked_now()
            ACTION.update_state(
                cycles=loop_count,
                status='يعمل',
                mode=('تداول فعلي (TESTNET 🧪)' if self.TESTNET else 'تداول فعلي')
                     if self.TRADE_ENABLED else 'مراقبة فقط',
                testnet=bool(self.TESTNET),
                trade_enabled=bool(self.TRADE_ENABLED),
                hma_live=bool(self.HMA_LIVE),
                hma_enabled=bool(self.hma_enabled),
                max_open_trades=int(self.MAX_OPEN_TRADES),
                open_count=len(self.active_trades),
                positions=self._action_positions_snapshot(),
                balance=round(float(balance or 0.0), 2),
                wins=int(self.stats.get('wins', 0)),
                losses=int(self.stats.get('losses', 0)),
                trades_executed=int(self.stats.get('trades_executed', 0)),
                daily_pnl=round(float(getattr(self.risk, 'daily_pnl', 0.0) or 0.0), 4),
                risk_ok=bool(can_trade),
                risk_reason=risk_reason,
                universe_count=len(self._universe_cache or []),
                last_scan=dict(self.last_scan_info or {}),
                last_hma_scan=dict(self.last_hma_scan_info or {}),
                evening_block=bool(HMA_BLOCK_EVENING_UTC),
                evening_blocked_now=bool(evening_now),
                evening_window=f"{HMA_EVENING_START_UTC}:00–{HMA_EVENING_END_UTC}:59 UTC",
                hma_timeframe=self.hma.timeframe,
                hma_batch=int(self.hma.batch_size),
                trades_today=self._trades_today(),
            )
            if loop_count % 5 == 0:
                ACTION.log('دورة',
                           msg=(f"الدورة #{loop_count} — كون {len(self._universe_cache or [])} زوج | "
                                f"مفتوحة {len(self.active_trades)}/{self.MAX_OPEN_TRADES} | "
                                + ('🌙 حظر المساء سارٍ الآن' if evening_now
                                   else '✅ الدخول متاح الآن')))
        except Exception as e:
            logger.debug(f"مزامنة اللوحة: {e}")

    async def _hma_exit_check(self, symbol, trade):
        """فحص الخروج الاستراتيجي لصفقة HMA مملوكة — شموع مغلقة فقط.
        يعيد (سبب الخروج|None، معلومات_الحالة|None)."""
        tf = self.hma.timeframe
        try:
            df = await self.get_klines(symbol, tf, 400)
        except Exception:
            return None, None
        if df is None or len(df) < 60:
            return None, None
        df = df.iloc[:-1]        # ⛔ شموع مغلقة فقط
        ev = HmaDmiMomentumEngine.evaluate(df, self.hma.as_params())
        if not ev.get('ok'):
            return None, None
        state_info = {'state': ev['state'], 'age': ev['state_age'],
                      'ts': time.time(), 'candle_ms': int(df['time'].iloc[-1])}
        reason = HmaDmiMomentumEngine.exit_reason(ev['arrays'], ev['states'],
                                                  ev['i'], trade['side'])
        return reason, state_info

    async def scan_hma(self):
        """دورة استراتيجية HMA_DMI_MOMENTUM: مراقبة مخارج صفقاتها المملوكة
        أولاً ثم مسح دفعة دوّارة من الكون السائل — التنفيذ عبر المسار المشترك
        (execute_trade) مع نفس بوابات المخاطر والرصيد والحد الأقصى، ومركز
        واحد لكل رمز: إشارة تصطدم بصفقة قائمة (لأي استراتيجية) تُستهلك
        فوراً بسجل واضح — بلا طابور مؤجل."""
        if not self.hma_enabled:
            self.last_hma_scan_info = {'ts': time.time(), 'enabled': False,
                                       'scanned': 0, 'signals': 0, 'exits': 0}
            return
        h = self.hma
        universe = [r['symbol'] for r in (self._universe_cache or [])][:int(h.universe_size)]
        owned = [s for s in self.active_trades
                 if self._symbol_owner(s) == HMA_STRATEGY_NAME]
        batch_syms = owned[:]          # صفقات HMA المفتوحة تُراقب دائماً (مخارج)
        seen = set(batch_syms)
        n = len(universe)
        if n:
            rot = min(max(1, int(h.batch_size)), n)
            start = self._hma_cursor % n
            for k in range(rot):
                s = universe[(start + k) % n]
                if s not in seen:
                    seen.add(s)
                    batch_syms.append(s)
            self._hma_cursor = (start + rot) % n

        sem = asyncio.Semaphore(max(1, int(h.parallel)))
        results, rejects = [], []
        exits = 0

        async def one(sym):
            nonlocal exits
            async with sem:
                trade = self.active_trades.get(sym)
                if trade and self._symbol_owner(sym) != HMA_STRATEGY_NAME:
                    return     # ⛔ الصفقة مملوكة لاستراتيجية أخرى — لا تداخل (سياسة التعارض)
                if trade:
                    # صفقة HMA مفتوحة → فحص الخروج الاستراتيجي على شمعة مغلقة
                    try:
                        exit_reason, state_info = await self._hma_exit_check(sym, trade)
                    except Exception as e:
                        self._notify_error(f"فحص خروج HMA {sym}", exc=e)
                        return
                    if state_info:
                        self.hma_states[sym] = state_info
                    if exit_reason:
                        prices = self.get_price(sym) or await self._refresh_price_rest(sym)
                        px = (prices['bid'] if trade['side'] == 'BUY' else prices['ask']) \
                            if prices else trade['entry_price']
                        closed, fill, pnl_over = await self._close_position(trade, px)
                        if closed:
                            exits += 1
                            await self._finalize_trade(
                                trade, fill, f"🧭 خروج استراتيجي HMA — {exit_reason}", pnl_over)
                    return    # لا إشارة دخول جديدة لرمز لديه صفقة قائمة
                try:
                    a, reason, state_info = await self.analyze_hma(sym)
                except Exception as e:
                    self._notify_error(f"فحص HMA {sym}", exc=e)
                    return
                if state_info:
                    self.hma_states[sym] = state_info
                if a:
                    results.append(a)
                elif reason:
                    rejects.append((sym, reason))

        await asyncio.gather(*[one(s) for s in batch_syms])

        self.last_hma_scan_info = {'ts': time.time(), 'enabled': True,
                                   'scanned': len(batch_syms),
                                   'signals': len(results), 'exits': exits,
                                   'cursor': self._hma_cursor}
        ACTION.update_state(last_hma_scan=self.last_hma_scan_info)
        await self._log_rejections(rejects, strategy=HMA_STRATEGY_NAME)

        # 🔔 تنبيه الإشارات الجديدة (خنق 30 دقيقة لكل رمز+اتجاه)
        now = time.time()
        for a in results:
            key = (a['symbol'], a['direction'], 'hma')
            if now - self.last_discovery_alert.get(key, 0) < 1800:
                continue
            self.last_discovery_alert[key] = now
            ACTION.log('إشارة', symbol=a['symbol'],
                       msg=f"إشارة {a['direction']} جديدة @ {self.fmt_price(a['price'])}",
                       reason=(a.get('components') or {}).get('trigger'),
                       detail="\n".join(a.get('lines') or []))
            await self.tg(f"🧭 *إشارة HMA_DMI_MOMENTUM جديدة:* `{a['symbol']}` *{a['direction']}* "
                          f"({a['components']['state']} | قوة {a['components']['power']:g} | "
                          f"ثقة {a['score']}/9 | إطار {a['components']['timeframe']})")

        # ⚙️ التنفيذ المشترك — الأعلى ثقة أولاً بحد أقصى للدورة، بلا طابور مؤجل
        results.sort(key=lambda a: a['score'], reverse=True)
        executed = 0
        for a in results:
            if len(self.active_trades) >= self.MAX_OPEN_TRADES:
                self.stats['rejected_open_trade'] += 1
                await self._mark_hma_done(a)   # ⛔ استهلاك الإشارة — لا تنفيذ مؤجل
                await self._log_rejections([(
                    a['symbol'],
                    'صفقة مفتوحة — الإعداد استُهلك ولن يُنفَّذ لاحقاً (يُعاد التحليل بعد الإغلاق)')],
                    strategy=HMA_STRATEGY_NAME)
                continue
            if executed >= int(h.max_signals_per_scan):
                break
            if not self.HMA_LIVE:
                await self._hma_signal_only(a)
                await self._mark_hma_done(a)   # 🛠️ إصلاح: كان بلا await — مفاتيح منع التكرار لا تُحفظ
                continue
            ok, why = await self.execute_trade(a)
            if ok:
                executed += 1
                await self._mark_hma_done(a)   # 🛠️ إصلاح: كان بلا await
                await asyncio.sleep(0.5)
            else:
                self.stats['rejected_execution'] += 1
                await self._log_rejections([(a['symbol'], f'رُفضت لحظة التنفيذ: {why}')],
                                           strategy=HMA_STRATEGY_NAME)


    # ═══ سجل أسباب الرفض (خنق: رمز+سبب مرة كل 30 دقيقة) — موسوم بالاستراتيجية ═══
    async def _log_rejections(self, rejects, strategy=None):
        now = time.time()
        fresh = []
        for item in rejects:
            symbol, reason = item[0], item[1]
            details = item[2] if len(item) > 2 else ''
            key = (symbol, reason)
            if now - self._last_reject_log.get(key, 0) < 1800:
                continue
            self._last_reject_log[key] = now
            fresh.append((symbol, reason, details))
        if not fresh:
            return
        self.stats['rejected_quality'] += len(fresh)
        for symbol, reason, details in fresh:
            ACTION.log('رفض', symbol=symbol, msg=reason, reason=details or None)
            await self.db.log_rejection(symbol, reason, details, strategy=strategy)

    # ═══ المسح: كون سائل ← دوران ← فحص متوازٍ ← تنفيذ منضبط ═══
    def _build_universe(self, tickers):
        """
        الكون = كل أزواج USDT الدائمة ذات سيولة 24س فعلية مقوّمة بـUSDT
        (quoteVolume) ≥ الحد الأدنى — العملات الخاملة لا تدخل أصلاً.
        التقلب والحركة تُقيَّم داخل تحليل HMA لكل زوج على حدة.
        """
        valid = {p['symbol'] for p in self.all_futures_pairs}
        rows = []
        self._ticker_cache = {}
        for t in tickers:
            sym = t.get('symbol', '')
            if sym not in valid:
                continue
            try:
                qv = float(t.get('quoteVolume') or 0)
                chg = float(t.get('priceChangePercent') or 0)
            except (TypeError, ValueError):
                continue
            self._ticker_cache[sym] = {'qv': qv, 'change': chg}
            if qv >= HMA_SCAN_MIN_VOL_USDT:
                rows.append({'symbol': sym, 'qv': qv, 'change': chg})
        rows.sort(key=lambda x: x['qv'], reverse=True)
        return rows[:HMA_UNIVERSE_POOL]

    def _pick_batch(self, universe):
        """دوران دائري عبر الكون كله — كل دورة شريحة مختلفة (بلا قوائم مفضلة)."""
        if not universe:
            return []
        n = len(universe)
        rot_n = min(max(4, int(self.hma.batch_size)), n)
        start = self._scan_cursor % n
        rotation = [universe[(start + i) % n] for i in range(rot_n)]
        self._scan_cursor = (start + rot_n) % n
        picked, seen = [], set()
        for row in rotation:
            s = row['symbol']
            if s in seen:
                continue
            seen.add(s)
            if s in self.active_trades or self.is_in_cooldown(s):
                continue
            picked.append(row)
        return picked

    def scan_status(self):
        return {
            'describe': self.hma.describe(),
            'universe_count': len(self._universe_cache),
            'universe_age_min': (int((time.time() - self._universe_ts) / 60)
                                 if self._universe_ts else None),
            'cursor': self._scan_cursor,
            'last': dict(self.last_scan_info) if self.last_scan_info else {},
        }

    async def _refresh_universe(self):
        """تحديث الكون السائل (أعلى سيولة 24س مقوّمة بـUSDT) — يستهلكه مسح
        HMA الدوّار كل دورة (بلا أي منطق دخول هنا — الدخول في scan_hma فقط)."""
        tickers = await self._fapi_request('GET', '/fapi/v1/ticker/24hr')
        if not tickers:
            self._notify_error("فشل جلب بيانات السوق", context="مشكلة اتصال مؤقتة")
            return
        self._reset_error("فشل جلب بيانات السوق")

        universe = self._build_universe(tickers)
        self._universe_cache = universe
        self._universe_ts = time.time()
        self.last_scan_info = {
            'ts': time.time(),
            'universe_count': len(universe),
            'cursor': self._scan_cursor,
        }

    # ═══ التنفيذ — مع إعادة تحقق كاملة لحظة الدخول (مسار HMA الوحيد) ═══
    async def execute_trade(self, analysis):
        """ينفذ إشارة HMA_DMI_MOMENTUM بعد كل بوابات الحماية وإعادة التحقق
        اللحظي. يعيد (نجاح؟، السبب)."""
        strat = analysis.get('strategy') or HMA_STRATEGY_NAME
        is_hma = strat == HMA_STRATEGY_NAME
        if not self.TRADE_ENABLED:
            return False, 'التداول معطل'
        if len(self.active_trades) >= self.MAX_OPEN_TRADES:
            return False, 'صفقة مفتوحة — الحد الأقصى للصفقات المتزامنة'

        # ✅ بوابة مدير المخاطر (3 متتالية → 4س | يومي 3 → اليوم | سحب 5%) — مشتركة
        can, reason = self.risk.can_trade()
        if not can:
            self.stats['rejected_by_risk'] += 1
            logger.warning(f"🛡️ إشارة {analysis['symbol']} ({strat}) مرفوضة بمدير المخاطر: {reason}")
            await self._log_rejections([(analysis['symbol'], f'🛡️ مدير المخاطر: {reason}')],
                                       strategy=strat)
            return False, reason

        # ✅ فلتر الأخبار (يُدار من اللوحة — تعطيله يمرر كل الإشارات) — مشترك
        news_blocked, news_reason = self.news_filter.is_blocked_now()
        if news_blocked:
            self.stats['rejected_by_news'] += 1
            self.news_filter.rejected_total += 1
            logger.info(f"📰 إشارة {analysis['symbol']} ({strat}) مرفوضة — {news_reason}")
            await self._log_rejections([(analysis['symbol'], f'📰 فلتر الأخبار: {news_reason}')],
                                       strategy=strat)
            return False, news_reason

        symbol = analysis['symbol']
        side = analysis['direction']
        # عتبات HMA الفعالة (الاستراتيجية الوحيدة)
        r_min = self.hma.risk_min_pct
        r_max = self.hma.risk_max_pct
        min_rr_eff = self.hma.min_rr
        tp1_max_atr_eff = self.hma.tp1_max_atr
        tp1_pct_eff = self.hma.tp1_return_pct
        if symbol in self.active_trades:
            return False, 'يوجد صفقة جارية على نفس الزوج'
        if self.is_in_cooldown(symbol):
            return False, 'الزوج في فترة تبريد بعد صفقة سابقة'

        # ⛔ إعادة تحقق لحظية: سعر حي + الاختراق ما زال سارياً
        prices = self.get_price(symbol) or await self._refresh_price_rest(symbol)
        if not prices:
            return False, 'لا سعر حي لحظة التنفيذ (تدفق الأسعار متوقف؟)'
        bid = float(prices.get('bid') or 0)
        ask = float(prices.get('ask') or 0)
        if bid <= 0 or ask <= 0:
            return False, 'سعر غير صالح لحظة التنفيذ'
        entry_price = ask if side == 'BUY' else bid

        v = analysis.get('validation', {})

        sl = analysis['sl']
        if side == 'BUY' and sl >= entry_price:
            return False, 'وقف الخسارة لم يعد منطقياً لحظة التنفيذ'
        if side == 'SELL' and sl <= entry_price:
            return False, 'وقف الخسارة لم يعد منطقياً لحظة التنفيذ'

        risk_dist = abs(entry_price - sl)
        risk_pct = risk_dist / entry_price * 100
        if risk_pct < r_min or risk_pct > r_max:
            return False, f'مسافة الستوب غير مناسبة لحظة التنفيذ ({risk_pct:.2f}%)'

        tp1_dist = self._tp1_distance(entry_price)
        if tp1_dist <= 0:
            return False, 'فشل حساب هدف TP1'
        atr_1h = v.get('atr_1h')
        if atr_1h and tp1_dist > tp1_max_atr_eff * atr_1h:
            return False, 'هدف TP1 بدا بعيداً عن ظروف السوق لحظة التنفيذ'
        rr = tp1_dist / risk_dist if risk_dist > 0 else 0.0
        if rr < min_rr_eff:
            return False, f'R:R تحلل لحظة التنفيذ ({rr:.2f} < {min_rr_eff:g})'

        # 💵 الرصيد
        available = await self.get_available_usdt()
        if available < self.TRADE_SIZE_USDT * 1.2:
            return False, f'رصيد غير كافٍ ({available:.2f}$ < المطلوب {self.TRADE_SIZE_USDT * 1.2:.2f}$)'

        # 📐 الكمية بدقة المنصة (Step/Min/Max/Notional)
        notional = self.TRADE_SIZE_USDT * self.LEVERAGE
        quantity = self.format_quantity(symbol, notional / entry_price)
        if quantity <= 0:
            return False, 'كمية محسوبة = صفر'
        if quantity < self.min_qty_cache.get(symbol, 0.0):
            return False, 'كمية أقل من الحد الأدنى للزوج'
        if quantity > self.max_qty_cache.get(symbol, 1e12):
            return False, 'كمية أعلى من الحد الأقصى للزوج'
        if quantity * entry_price < self.min_notional_cache.get(symbol, 5.0) * 1.02:
            return False, 'قيمة الأمر أقل من الحد الأدنى (Notional) للزوج'

        # رافعة + هامش معزول لهذا الزوج
        await self._fapi_request('POST', '/fapi/v1/leverage',
            {'symbol': symbol, 'leverage': self.LEVERAGE}, signed=True)
        await self._fapi_request('POST', '/fapi/v1/marginType',
            {'symbol': symbol, 'marginType': 'ISOLATED'}, signed=True, quiet=(-4046,))

        # 🚀 دخول ماركت — محاولة واحدة فقط (لا إعادة إرسال تلقائية منعاً
        # للدخول المزدوج عند انتهاء مهلة طلب نفّذ فعلياً)
        result = await self._fapi_request('POST', '/fapi/v1/order', {
            'symbol': symbol, 'side': side, 'type': 'MARKET',
            'quantity': self.qty_to_str(symbol, quantity)
        }, signed=True, retries=1)

        entry_status = result.get('status') if isinstance(result, dict) else None
        if entry_status not in ('FILLED', 'NEW'):
            # الرد ضاع أو فشل — نتحقق من المركز الفعلي قبل إعلان الفشل:
            # إن نُفّذ الدخول وضاع ردُه نتبنّى المركز (لا مركز ضائع ولا دخول مزدوج)
            min_step = (self.step_sizes_cache.get(symbol)
                        or self.min_qty_cache.get(symbol) or 1e-12)
            amt_check = await self.get_position_amt(symbol)
            if amt_check is not None and abs(amt_check) >= min_step:
                entry_status = 'FILLED'
                result = None
                self._notify_error(f"رد أمر الدخول ضاع لـ {symbol}",
                                   context="تأكد الدخول عبر فحص المركز الفعلي — الصفقة ستُدار طبيعياً")
            else:
                await self.tg(f"❌ *فشل تنفيذ {side} (`{symbol}`)*\n"
                              "⚠️ لن يُعاد الإرسال تلقائياً — منعاً للدخول المزدوج")
                return False, 'فشل أمر الدخول لدى Binance'

        # 📐 بيانات التنفيذ الفعلية: الكمية والسعر والرافعة بعد تقريب Binance
        fill_avg = 0.0
        fill_qty = 0.0
        if isinstance(result, dict):
            try:
                fill_avg = float(result.get('avgPrice') or 0)
            except (TypeError, ValueError):
                fill_avg = 0.0
            try:
                fill_qty = float(result.get('executedQty') or 0)
            except (TypeError, ValueError):
                fill_qty = 0.0
        pos = await self._get_position_info(symbol)
        real_entry = (pos['entry'] if pos and pos['entry'] > 0
                      else (fill_avg if fill_avg > 0 else entry_price))
        actual_qty = (abs(pos['amt']) if pos and abs(pos.get('amt', 0) or 0) > 0
                      else (fill_qty if fill_qty > 0 else quantity))
        if symbol in self.step_sizes_cache:   # إعادة الالتزام بخطوة الزوج إن كانت معروفة
            actual_qty = self.format_quantity(symbol, actual_qty) or quantity
        actual_lev = (pos['leverage'] if pos and pos['leverage'] > 0 else float(self.LEVERAGE))
        actual_margin = (pos['initial_margin'] if pos and pos['initial_margin'] > 0
                         else actual_qty * real_entry / actual_lev)

        # 🎯 TP1 من الهامش الفعلي المستخدم (كمية منفذة × سعر فعلي × رافعة فعلية)
        tp1_dist = self._tp1_distance_from_actual(real_entry, actual_qty, actual_lev)
        if tp1_dist <= 0:
            tp1_dist = self._tp1_distance(real_entry)
        tp1_raw = real_entry + tp1_dist if side == 'BUY' else real_entry - tp1_dist
        tp1 = self._round_tp_price(symbol, tp1_raw, side)

        trade_data = {
            'symbol': symbol, 'side': side, 'entry_price': real_entry,
            'quantity': actual_qty, 'sl': sl, 'tp': tp1,
            'score': analysis.get('score'),
            'strategy': strat,
            'trailing_active': False, 'highest_price': real_entry,
            'lowest_price': real_entry, 'entry_time': time.time(),
            'realized_pnl': 0.0,
            # 🛡️ V11.2 وقف التعادل: ATR لحظة الدخول (لإطلاق التعادل 1.0×ATR)
            'atr_entry': float((analysis.get('validation') or {}).get('atr_1h') or 0.0),
            'be_done': False,
            'stop_order_id': None, 'tp_order_id': None,
            'stop_state': 'none', 'stop_error': None,
            'stop_synced_price': None,
        }
        self.active_trades[symbol] = trade_data
        self._recent_entry[symbol] = time.time()
        await self.db.save_trade(trade_data)
        self.stats['trades_executed'] += 1
        self.entry_history.append((time.time(), time.strftime("%Y-%m-%d")))
        await self.db.log_signal(symbol, side, trade_data['entry_time'],
                                 analysis['score'], analysis['components'], strategy=strat)

        ref_price = bid if side == 'BUY' else ask
        await self._sync_stop_order(trade_data, ref_price)
        await self.db.save_trade(trade_data)

        # إشعار الشفافية: الهدف الإجمالي مقابل الصافي التقديري بعد الرسوم
        target_gross = self._tp1_target_profit(actual_margin)
        fees_est = actual_qty * real_entry * 0.001   # تقدير تيكر 0.05% × طرفين
        risk_pct_real = abs(real_entry - sl) / real_entry * 100 if real_entry > 0 else risk_pct
        st_state = trade_data.get('stop_state')
        if st_state == 'verified':
            stop_txt = '✅ مثبّت ومؤكد على المنصة'
        elif st_state == 'placed':
            stop_txt = '🟡 مثبّت — بانتظار التأكيد'
        elif st_state == 'local':
            stop_txt = '🛡️ مراقبة محلية فعّالة (فشل تثبيت أمر المنصة)'
        else:
            stop_txt = '⏳ جارٍ التثبيت...'
        strat_line = ''
        if True:   # HMA — الاستراتيجية الوحيدة
            comp = analysis.get('components', {})
            strat_line = (f"🧭 الزناد: {comp.get('trigger', '—')} | {comp.get('state', '—')} | "
                          f"قوة {comp.get('power', '—')} | ثقة {comp.get('confidence', '—')}/9"
                          + (' (استثناء هيكلي)' if comp.get('override') else '') + "\n")
        msg = (f"✅ *صفقة {self._strategy_display(strat)} منفذة!* (جودة {analysis['score']})\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
               f"🪙 `{symbol}` | {side} | رافعة {actual_lev:g}x | هامش فعلي {actual_margin:.2f}$\n"
               f"📐 تنفيذ فعلي: كمية {actual_qty} @ {self.fmt_price(real_entry)}\n"
               + strat_line
               + f"🛑 SL: {self.fmt_price(sl)} ({risk_pct_real:.2f}%)\n"
               f"🎯 TP1: {self.fmt_price(tp1)} — إغلاق 100% للمركز عند اللمس\n"
               f"💰 هدف الربح: ~{target_gross:.2f} USDT إجمالاً ({tp1_pct_eff:g}% من الهامش الفعلي)\n"
               f"🧾 صافٍ تقديري بعد الرسوم: ~{max(0.0, target_gross - fees_est):.2f} USDT\n"
               f"🛡️ ستوب المنصة: {stop_txt}\n"
               f"⏰ ستوب زمني: {self.MAX_TRADE_HOURS:g} ساعة")
        ACTION.log('دخول', symbol=symbol,
                   msg=f"تنفيذ {side} @ {self.fmt_price(real_entry)} | كمية {actual_qty} | هامش {actual_margin:.2f}$",
                   reason=f"SL {self.fmt_price(sl)} | TP1 {self.fmt_price(tp1)} | ستوب المنصة: {stop_txt}")
        await self.tg(msg)
        return True, 'تم التنفيذ'

    # ═══ أوامر المنصة الشرطية ═══
    async def _place_conditional_order(self, params, detailed=False):
        """تثبيت STOP_MARKET / TAKE_PROFIT_MARKET عبر /fapi/v1/order.
        مع detailed=True يعيد (حالة، حمولة) وحمولة الفشل تحمل كود رفض
        Binance الحقيقي."""
        res = await self._fapi_request('POST', '/fapi/v1/order', params, signed=True, detailed=True)
        if isinstance(res, dict):
            if res.get('_error'):
                return ('ERROR', res) if detailed else None
            oid = res.get('orderId')
            if oid:
                return ('OK', int(oid)) if detailed else int(oid)
            return ('OK', 'UNKNOWN') if detailed else 'UNKNOWN'
        return (('ERROR', {'_error': True, '_code': None, '_msg': 'رد غير متوقع'})
                if detailed else None)

    async def _cancel_conditional_order(self, symbol, order_id):
        await self._fapi_request('DELETE', '/fapi/v1/order',
            {'symbol': symbol, 'orderId': order_id}, signed=True, quiet=('-2011', '-2013'))

    # ═══ 🛡️ وقف الخسارة: STOP_MARKET حقيقي + مراقبة محلية احتياطية ═══
    async def _place_stop_order(self, trade, desired=None):
        """
        سلّم محاولات لتثبيت ستوب حي على المنصة:
        1) STOP_MARKET reduceOnly بالكمية المتبقية
        2) STOP_MARKET closePosition
        3) فشل الاثنين → مراقبة محلية فعّالة (البوت يغلق ماركت عند الستوب)
        الحالة تُعرض في اللوحة كما هي فعلاً — بلا ادعاءات.
        """
        symbol = trade['symbol']
        is_buy = trade['side'] == 'BUY'
        desired = trade['sl'] if desired is None else desired
        if not desired or desired <= 0:
            return False
        close_side = 'SELL' if is_buy else 'BUY'
        stop_str = self.price_to_str(symbol, desired)
        base = {'symbol': symbol, 'side': close_side, 'type': 'STOP_MARKET',
                'stopPrice': stop_str, 'workingType': 'CONTRACT_PRICE'}
        attempts = [
            ('reduceOnly', dict(base, quantity=self.qty_to_str(symbol, trade['quantity']),
                                reduceOnly='true')),
            ('closePosition', dict(base, closePosition='true')),
        ]
        errs = []
        for label, params in attempts:
            status, res = await self._place_conditional_order(params, detailed=True)
            if status == 'OK':
                trade['stop_order_id'] = None if res == 'UNKNOWN' else int(res)
                trade['stop_synced_price'] = desired
                trade['stop_state'] = 'placed'
                trade['stop_method'] = f'PLATFORM_{label}'
                trade['stop_error'] = None
                trade['stop_placed_at'] = time.time()   # نافذة سماح 90 ث للتأكيد
                await self._verify_stop_on_platform(trade)
                self._reset_error(f"ستوب المنصة {symbol}")
                return True
            errs.append(f"{label}: {res.get('_code')} {(res.get('_msg') or '')[:90]}".strip())

        trade['stop_order_id'] = None
        trade['stop_synced_price'] = desired
        trade['stop_state'] = 'local'
        trade['stop_method'] = 'LOCAL_MONITORING'
        trade['stop_error'] = ' | '.join(errs)[:200]
        trade['stop_retry_at'] = time.time() + 900
        self._notify_error(f"ستوب المنصة غير متاح لـ {symbol}",
                           context='المراقبة المحلية فعّالة وتغلق عند الستوب — إعادة محاولة لاحقاً')
        return True

    async def _verify_stop_on_platform(self, trade, strict=False):
        """التحقق الحقيقي: يفتح openOrders ويبحث عن أمر الستوب فعلياً —
        حالة (مؤكد ✓) لا تُمنح إلا برؤية الأمر حياً على المنصة.
        strict=True: عندما يتعذر العثور على الأمر تُخفض الحالة إلى مراقبة
        محلية فوراً مع إعادة تثبيت عاجلة — المركز لا يُعرض محمياً على المنصة
        إذا لم نستطع إثبات وجود أمر الوقف فعلاً."""
        if trade.get('stop_method') == 'LOCAL_MONITORING':
            return trade.get('stop_state') == 'verified'
        symbol = trade['symbol']
        orders = await self._fapi_request('GET', '/fapi/v1/openOrders',
            {'symbol': symbol}, signed=True)
        if not isinstance(orders, list):
            # تعذر التحقق (انقطاع/خطأ شبكة) — الحالة تبقى كما هي ولا تُرقّى
            # إلى مؤكد أبداً، وإعادة الفحص القادمة تتولى الأمر
            return trade.get('stop_state') == 'verified'
        want = trade.get('stop_synced_price')
        want_str = self.price_to_str(symbol, want) if want else None
        for o in orders:
            if o.get('type') not in ('STOP_MARKET', 'STOP') or o.get('status') != 'NEW':
                continue
            if trade.get('stop_order_id') and o.get('orderId') == trade['stop_order_id']:
                trade['stop_state'] = 'verified'
                trade['stop_verified_at'] = time.time()
                return True
            try:
                sp = float(o.get('stopPrice', 0) or 0)
            except (TypeError, ValueError):
                continue
            if want_str and sp > 0 and self.price_to_str(symbol, sp) == want_str:
                trade['stop_state'] = 'verified'
                trade['stop_verified_at'] = time.time()
                if not trade.get('stop_order_id'):
                    trade['stop_order_id'] = o.get('orderId')
                return True
        # لم يُعثر على أمر الستوب على المنصة — المركز ليس محمياً بأمر حي الآن
        if strict or trade.get('stop_state') == 'verified':
            trade['stop_state'] = 'local'
            trade['stop_method'] = 'LOCAL_MONITORING'
            trade['stop_error'] = 'أمر الستوب غير موجود على المنصة — إعادة تثبيت مجدولة'
            trade['stop_retry_at'] = time.time() + 30
            return False
        return False   # نافذة سماح لحالة "مثبّت" الجديدة قبل التشديد

    async def verify_platform_stops(self):
        """فحص دوري أن ستوبات المراكز المفتوحة ما زالت حية — ومراكز الستوب
        المحلي تُعاد محاولة تثبيتها على المنصة كل 15 دقيقة."""
        if not self.binance_api_key or not self.active_trades:
            return
        now = time.time()
        for symbol, trade in list(self.active_trades.items()):
            try:
                if trade.get('stop_method') == 'LOCAL_MONITORING':
                    # إعادة محاولة تثبيت ستوب حقيقي على المنصة كل 15 دقيقة
                    if now > trade.get('stop_retry_at', 0):
                        await self._sync_stop_order(trade, None, force=True)
                    continue
                # التحقق المشدد: ستوب اختفى من المنصة → مراقبة محلية + إعادة تثبيت عاجلة
                await self._verify_stop_on_platform(trade, strict=True)
            except Exception as e:
                logger.warning(f"تعذر التحقق من ستوب {symbol}: {e}")

    async def _sync_stop_order(self, trade, current_price, force=False):
        """مزامنة ستوب المنصة مع SL المطلوب — لا تضع أمراً خلف السعر الحالي
        (المراقبة المحلية تغطي تلك الحالة فوراً)."""
        symbol = trade['symbol']
        is_buy = trade['side'] == 'BUY'
        desired = trade['sl']
        if desired is None or desired <= 0:
            return False
        if current_price and ((is_buy and desired >= current_price)
                              or (not is_buy and desired <= current_price)):
            return False
        # ⏳ حالة "مثبّت" عمرها أكثر من 90 ثانية دون تأكيد → تحقق مشدد الآن:
        # إن كان الأمر مفقوداً فعلاً تُخفض الحالة لمراقبة محلية وتُعاد محاولة التثبيت
        if (not force and trade.get('stop_state') == 'placed'
                and time.time() > float(trade.get('stop_placed_at', 0) or 0) + 90):
            await self._verify_stop_on_platform(trade, strict=True)
        desired_str = self.price_to_str(symbol, desired)
        if (not force and trade.get('stop_state') in ('verified', 'placed')
                and trade.get('stop_synced_price') is not None
                and self.price_to_str(symbol, trade['stop_synced_price']) == desired_str):
            return False
        if (not force and trade.get('stop_state') == 'local'
                and trade.get('stop_synced_price') is not None
                and self.price_to_str(symbol, trade['stop_synced_price']) == desired_str
                and time.time() < trade.get('stop_retry_at', 0)):
            return False

        old_id = trade.get('stop_order_id')
        placed = await self._place_stop_order(trade, desired)
        if placed:
            if old_id and old_id != trade.get('stop_order_id'):
                await self._cancel_conditional_order(symbol, old_id)
            logger.info(f"🛡️ ستوب {symbol} عند {desired_str} — "
                        f"الحالة: {trade.get('stop_state')} ({trade.get('stop_method', '')})")
            return True
        return False

    # ═══ استعلامات المنصة ═══
    async def get_position_amt(self, symbol):
        try:
            res = await self._fapi_request('GET', '/fapi/v2/positionRisk',
                {'symbol': symbol}, signed=True)
            if isinstance(res, list) and res:
                return float(res[0].get('positionAmt', 0))
        except Exception as e:
            logger.warning(f"فشل استعلام المركز لـ {symbol}: {e}")
        return None

    async def _get_position_info(self, symbol):
        """بيانات المركز الفعلية الكاملة (كمية/سعر/رافعة/هامش) — أساس حساب
        TP1 من التنفيذ الفعلي. يعيد None عند تعذر الجلب."""
        try:
            res = await self._fapi_request('GET', '/fapi/v2/positionRisk',
                {'symbol': symbol}, signed=True)
            if isinstance(res, list) and res:
                p = res[0]
                try:
                    amt = float(p.get('positionAmt', 0) or 0)
                except (TypeError, ValueError):
                    amt = 0.0
                try:
                    entry = float(p.get('entryPrice', 0) or 0)
                except (TypeError, ValueError):
                    entry = 0.0
                try:
                    lev = float(p.get('leverage', 0) or 0)
                except (TypeError, ValueError):
                    lev = 0.0
                try:
                    im = float(p.get('initialMargin', 0) or 0)
                except (TypeError, ValueError):
                    im = 0.0
                return {'amt': amt, 'entry': entry, 'leverage': lev, 'initial_margin': im}
        except Exception as e:
            logger.warning(f"فشل استعلام بيانات المركز لـ {symbol}: {e}")
        return None

    async def _income_sum(self, symbol, income_type, start_ms):
        """مجموع سجلات دخل نوع محدد منذ لحظة الدخول — None عند فشل الجلب."""
        res = await self._fapi_request('GET', '/fapi/v1/income',
            {'symbol': symbol, 'incomeType': income_type,
             'startTime': start_ms, 'limit': 1000}, signed=True)
        if not isinstance(res, list):
            return None
        total = 0.0
        for e in res:
            try:
                total += float(e.get('income', 0) or 0)
            except (TypeError, ValueError):
                continue
        return total, len(res)

    async def get_trade_realized_pnl(self, symbol, trade, expect_new_fill=False):
        """النتيجة الفعلية للصفقة من Binance:
        NET = Σ REALIZED_PNL + Σ COMMISSION + Σ FUNDING_FEE منذ لحظة الدخول
        (يشمل التنفيذ الجزئي وتعدد عمليات الإغلاق).
        يعيد {'gross','fees','funding','net','fills','complete':True} أو None
        عند تعذر جلب البيانات (لن تُختلق نتيجة مؤكدة في هذه الحالة)."""
        try:
            entry_time = float(trade.get('entry_time', 0) or 0)
        except (TypeError, ValueError):
            entry_time = 0.0
        if entry_time <= 0:
            return None
        start_ms = int((entry_time - 5) * 1000)
        attempts = 2 if expect_new_fill else 1
        for attempt in range(attempts):
            gross = await self._income_sum(symbol, 'REALIZED_PNL', start_ms)
            fees = await self._income_sum(symbol, 'COMMISSION', start_ms)
            funding = await self._income_sum(symbol, 'FUNDING_FEE', start_ms)
            if gross is None or fees is None or funding is None:
                return None   # بيانات غير مكتملة — الحالة تُسجل بوضوح كتقدير
            if gross[1] == 0 and expect_new_fill and attempt < attempts - 1:
                await asyncio.sleep(2.0)   # مهلة ظهور سجل التنفيذ الطازج
                continue
            return {'gross': gross[0], 'fees': fees[0], 'funding': funding[0],
                    'net': gross[0] + fees[0] + funding[0],
                    'fills': gross[1], 'complete': True}
        return None

    async def verify_positions(self):
        """مطابقة الحالة المحلية مع المراكز الفعلية لدى Binance:
        - صفقة محلية بلا مركز فعلي تُنهى بأرباحها الحقيقية (وليس تقديراً
          إلا عند تعذر جلب بيانات الدخل).
        - مركز فعلي بلا صفقة محلية (يتيم) يُتبنّى بحماية كاملة — مزامنة
          مستمرة لا عند الإقلاع فقط."""
        if not self.TRADE_ENABLED or not self.binance_api_key:
            return
        if self.active_trades:
            for symbol, trade in list(self.active_trades.items()):
                try:
                    amt = await self.get_position_amt(symbol)
                    if amt is None:
                        continue   # تعذر التحقق — لا إغلاق وهمي
                    step = self.step_sizes_cache.get(symbol) or 1.0
                    if abs(amt) < step:
                        pnl_info = await self.get_trade_realized_pnl(symbol, trade)
                        prices = self.get_price(symbol)
                        px = (prices['bid'] if trade['side'] == 'BUY' else prices['ask']) if prices else trade['entry_price']
                        await self._finalize_trade(trade, px, "🛑 أُغلق على المنصة (خارج مراقبة البوت)", pnl_info)
                except Exception as e:
                    self._notify_error(f"فشل التحقق من مركز {symbol}", exc=e)
        # 🔁 مزامنة المراكز اليتيمة: مركز حي على المنصة بلا صفقة محلية → تبنّي بحماية كاملة
        try:
            positions = await self._fapi_request('GET', '/fapi/v2/positionRisk', signed=True)
            if isinstance(positions, list):
                for p in positions:
                    try:
                        amt = float(p.get('positionAmt', 0) or 0)
                    except (TypeError, ValueError):
                        continue
                    if abs(amt) <= 0:
                        continue
                    symbol = p.get('symbol')
                    if not symbol or symbol in self.active_trades:
                        continue
                    if time.time() - self._recent_entry.get(symbol, 0) < 180:
                        continue   # دخول جديد قيد الاستقرار — لا تداخل
                    await self._adopt_orphan_position(symbol, p)
        except Exception as e:
            self._notify_error("فحص المراكز اليتيمة", exc=e)

    # ═══ إغلاق آمن بالكمية الفعلية (مع تحقق المنصة قبل تأكيد الإغلاق) ═══
    async def _close_position(self, trade, current_price):
        symbol = trade['symbol']
        # ⛔ قفل إغلاق لكل رمز: لا أمر إغلاق مكرر لو تداخل مراقب/لوحة/مسار آخر
        if symbol in self._closing:
            return False, None, None
        self._closing.add(symbol)
        try:
            return await self._close_position_locked(trade, current_price)
        finally:
            self._closing.discard(symbol)

    async def _close_position_locked(self, trade, current_price):
        symbol = trade['symbol']
        is_buy = trade['side'] == 'BUY'
        close_side = 'SELL' if is_buy else 'BUY'

        amt = await self.get_position_amt(symbol)
        if amt is None:
            self._notify_error(f"تعذر قراءة مركز {symbol}", context="إعادة المحاولة لاحقاً")
            return False, None, None
        step = self.step_sizes_cache.get(symbol) or 1.0
        if abs(amt) < step:
            pnl_info = await self.get_trade_realized_pnl(symbol, trade)
            return True, current_price, pnl_info

        qty = self.format_quantity(symbol, min(trade['quantity'], abs(amt)))
        if qty <= 0:
            return True, current_price, await self.get_trade_realized_pnl(symbol, trade)

        res = await self._fapi_request('POST', '/fapi/v1/order', {
            'symbol': symbol, 'side': close_side, 'type': 'MARKET',
            'quantity': self.qty_to_str(symbol, qty), 'reduceOnly': 'true'
        }, signed=True)

        if res and res.get('status') in ['FILLED', 'NEW']:
            fill = float(res.get('avgPrice') or 0)
            fill_price = fill if fill > 0 else current_price
            self._reset_error(f"إغلاق {symbol}")
            # ✅ لا يُسجّل الإغلاق ناجحاً قبل التحقق من المركز الفعلي
            amt2 = await self.get_position_amt(symbol)
            if amt2 is not None and abs(amt2) >= step:
                self._notify_error(f"بقايا مركز {symbol} بعد الإغلاق",
                                   context=f"المتبقي {abs(amt2)} — إعادة محاولة الدورة القادمة")
                return False, None, None
            # 💵 النتيجة الفعلية من Binance (يشمل رسوم أمر الإغلاق نفسه)
            pnl_info = await self.get_trade_realized_pnl(symbol, trade, expect_new_fill=True)
            return True, fill_price, pnl_info

        amt2 = await self.get_position_amt(symbol)
        if amt2 is not None and abs(amt2) < step:
            return True, current_price, await self.get_trade_realized_pnl(symbol, trade)

        self._notify_error(f"فشل إغلاق {symbol}",
                           context="ستُعاد المحاولة — ستوب المنصة/المحلي يحمي المركز")
        return False, None, None

    # ═══ إنهاء الصفقة (محاسبة كاملة بنتيجة فعلية موثقة) ═══
    async def _finalize_trade(self, trade, fill_price, reason, pnl_override=None):
        symbol = trade['symbol']
        # ⛔ حماية من الاحتساب المزدوج لنفس الصفقة (مراقب + لوحة + مصالحة)
        if trade.get('_finalizing'):
            return
        trade['_finalizing'] = True
        is_buy = trade['side'] == 'BUY'

        # إلغاء أي أوامر حماية متبقية بعد تأكيد الإغلاق
        for oid_key in ('stop_order_id', 'tp_order_id'):
            oid = trade.get(oid_key)
            if oid:
                await self._cancel_conditional_order(symbol, oid)

        # 💵 مصدر النتيجة:
        #  1) بيانات Binance الفعلية (صافي = محقق + رسوم + تمويل) → مؤكدة
        #  2) تعذر الجلب → تقدير نظري موسوم بوضوح، ولا يُقدّم أبداً كنتيجة مؤكدة
        pnl_info = pnl_override if isinstance(pnl_override, dict) else None
        if pnl_info and pnl_info.get('complete'):
            final_pnl = float(pnl_info.get('net', 0.0) or 0.0)
            pnl_source = 'binance'
        else:
            try:
                qty = float(trade.get('quantity', 0) or 0)
                entry = float(trade.get('entry_price', 0) or 0)
                fill = float(fill_price or 0)
            except (TypeError, ValueError):
                qty = entry = fill = 0.0
            if qty > 0 and entry > 0 and fill > 0:
                final_pnl = (fill - entry) * qty if is_buy else (entry - fill) * qty
            else:
                final_pnl = 0.0
            pnl_source = 'estimated'

        total_pnl = float(trade.get('realized_pnl', 0.0) or 0.0) + final_pnl
        margin_used = self.TRADE_SIZE_USDT
        margin_pnl_pct = (total_pnl / margin_used * 100) if margin_used > 0 else 0

        # 🛡️ تسجيل النتيجة في مدير المخاطر (يوقف التداول تلقائياً عند الحدود + حفظ الحالة)
        await self.risk.register_result(total_pnl)

        # النتيجة: 1 ربح | 0 خسارة | 2 محايدة (صفر/غير قابلة للتحقق لا تُحتسب خسارة)
        result_code = 1 if total_pnl > 0 else (0 if total_pnl < 0 else 2)
        if result_code == 1:
            self.stats['wins'] += 1
        elif result_code == 0:
            self.stats['losses'] += 1

        try:
            await self.db.set_signal_result(symbol, trade['entry_time'], result_code,
                                            total_pnl, pnl_source,
                                            strategy=trade.get('strategy') or HMA_STRATEGY_NAME)
        except Exception:
            pass

        await self.db.update_daily_pnl(
            total_pnl, True if result_code == 1 else (False if result_code == 0 else None))
        await self.db.remove_trade(symbol)
        self.active_trades.pop(symbol, None)
        self.set_cooldown(symbol)

        if pnl_source == 'binance':
            src_txt = (f"🧾 المصدر: نتيجة Binance الفعلية (صافي بعد الرسوم والتمويل)\n"
                       f"   إجمالي: `{pnl_info['gross']:.4f}` | رسوم: `{pnl_info['fees']:.4f}` | "
                       f"تمويل: `{pnl_info['funding']:.4f}` | عمليات تنفيذ: {pnl_info.get('fills', 0)}")
            src_short = 'مؤكدة ✓'
        else:
            src_txt = ("⚠️ المصدر: تقدير نظري (فرق السعر × الكمية) — بيانات التنفيذ الفعلية "
                       "غير متاحة ولن تُعرض كنتيجة مؤكدة")
            src_short = 'تقديرية ⚠️'
        icon = "✅" if result_code == 1 else ("❌" if result_code == 0 else "➖")
        strat_line = f"🧭 الاستراتيجية: {self._strategy_display(trade.get('strategy') or HMA_STRATEGY_NAME)}\n"
        msg = (f"🏁 {icon} *إغلاق `{symbol}`*\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
               f"{reason}\n"
               f"{strat_line}"
               f"💵 النتيجة ({src_short}): `{total_pnl:.4f} USDT` ({margin_pnl_pct:.1f}% من الهامش)\n"
               f"{src_txt}\n"
               f"🏆 الإجمالي: {self.stats['wins']}W / {self.stats['losses']}L")
        ACTION.log('خروج', symbol=symbol, msg=(reason or '').strip()[:140],
                   reason=f"النتيجة {total_pnl:.4f} USDT ({src_short})",
                   pnl=round(total_pnl, 6))
        await self.tg(msg)

    # ═══ مراقبة الصفقات: SL ← ستوب زمني ← TP1 بإغلاق كامل ═══
    async def monitor_trades(self):
        if not self.active_trades:
            return
        stale_symbols = []
        for symbol, trade in list(self.active_trades.items()):
            prices = self.get_price(symbol)
            if not prices:
                now = time.time()
                if now - self._rest_price_ts.get(symbol, 0) >= 10:
                    self._rest_price_ts[symbol] = now
                    prices = await self._refresh_price_rest(symbol)
            if not prices:
                stale_symbols.append(symbol)
                continue

            is_buy = trade['side'] == 'BUY'
            current_price = prices['bid'] if is_buy else prices['ask']
            changed = False

            if is_buy and current_price > trade.get('highest_price', 0):
                trade['highest_price'] = current_price
                changed = True
            elif not is_buy and current_price < trade.get('lowest_price', 999999):
                trade['lowest_price'] = current_price
                changed = True

            # 1) 🛡️ وقف الخسارة — حماية محلية فورية تعمل دائماً سواء كان
            #      ستوب المنصة مثبتاً أم في وضع المراقبة المحلية
            if (is_buy and current_price <= trade['sl']) or (not is_buy and current_price >= trade['sl']):
                closed, fill_price, pnl_override = await self._close_position(trade, current_price)
                if closed:
                    await self._finalize_trade(trade, fill_price, "🛑 ضرب SL (حماية مؤكدة)", pnl_override)
                continue

            # 2) ⏰ الستوب الزمني — لا صفقة عالقة
            max_h = self.MAX_TRADE_HOURS
            if max_h and max_h > 0 and time.time() - trade.get('entry_time', 0) >= max_h * 3600:
                closed, fill_price, pnl_override = await self._close_position(trade, current_price)
                if closed:
                    await self._finalize_trade(trade, fill_price,
                        f"⏰ ستوب زمني ({max_h:g} ساعة بلا انطلاق)", pnl_override)
                continue

            # 3) 🎯 TP1 — إغلاق 100% من الكمية المتبقية فوراً (لا TP2 ولا تقسيم)
            tp = trade.get('tp')
            if tp and ((is_buy and current_price >= tp) or (not is_buy and current_price <= tp)):
                closed, fill_price, pnl_override = await self._close_position(trade, current_price)
                if closed:
                    await self._finalize_trade(trade, fill_price,
                        "🎯 TP1 — إغلاق كامل للمركز (هدف عائد الهامش)", pnl_override)
                else:
                    self._notify_error(f"تعذر إغلاق TP1 لـ {symbol}",
                                       context="إعادة المحاولة في الدورة القادمة — الوقف يحمي المركز")
                continue

            # 4) مزامنة ستوب المنصة مع الحالة الحالية (رخيصة إن لم يتغير شيء)
            try:
                await self._sync_stop_order(trade, current_price)
            except Exception as e:
                logger.warning(f"تعذر مزامنة ستوب {symbol}: {e}")

            if changed:
                await self.db.save_trade(trade)

        if stale_symbols:
            # ⚠️ بدون أسعار لا تعمل المراقبة المحلية — نُنبه بوضوح إن كان ستوب
            # المركز غير مؤكد على المنصة (المركز غير محمي بأمر حي الآن)
            unprot = [s for s in stale_symbols
                      if (self.active_trades.get(s, {}).get('stop_state') != 'verified')]
            ctx = ', '.join(stale_symbols)
            if unprot:
                ctx += f" | ⚠️ ستوب غير مؤكد على المنصة: {', '.join(unprot)}"
            self._notify_error("أسعار مجمّدة لمراكز مفتوحة", context=ctx)

    # ═══ تبنّي مركز يتيم من بياناته الفعلية (يُستخدم في المصالحة والفحص الدوري) ═══
    async def _adopt_orphan_position(self, symbol, pos_row):
        """تبنّي مركز موجود على المنصة بلا صفقة محلية: وقف خسارة + TP1 محسوب
        من بيانات المركز الفعلية (الكمية/السعر/الرافعة من المنصة نفسها)."""
        try:
            amt = float(pos_row.get('positionAmt', 0) or 0)
        except (TypeError, ValueError):
            amt = 0.0
        if abs(amt) <= 0:
            return False
        side = 'BUY' if amt > 0 else 'SELL'
        try:
            entry = float(pos_row.get('entryPrice', 0) or 0)
        except (TypeError, ValueError):
            entry = 0.0
        if not entry or entry <= 0:
            prices = self.get_price(symbol) or await self._refresh_price_rest(symbol)
            entry = (prices['bid'] if side == 'BUY' else prices['ask']) if prices else 0.0
        if not entry or entry <= 0:
            await self.tg(f"⚠️ *تعذّر تبنّي مركز يتيم* (`{symbol}`)\n"
                          "سعر الدخول غير متاح بعد — سيُعاد في فحص قادم")
            return False
        try:
            lev = float(pos_row.get('leverage', 0) or 0)
        except (TypeError, ValueError):
            lev = 0.0
        lev = lev if lev > 0 else float(self.LEVERAGE)
        qty = abs(amt)
        df = await self.get_klines(symbol, '15m', 50)
        atr = self._compute_atr(df) if df is not None else None
        if not atr or atr <= 0 or math.isnan(atr):
            atr = entry * 0.01
        tp1_dist = self._tp1_distance_from_actual(entry, qty, lev)
        if tp1_dist <= 0:
            tp1_dist = 1.5 * atr
        if side == 'BUY':
            sl = entry - 2 * atr
            tp1 = self._round_tp_price(symbol, entry + tp1_dist, side)
        else:
            sl = entry + 2 * atr
            tp1 = self._round_tp_price(symbol, entry - tp1_dist, side)
        trade = {
            'symbol': symbol, 'side': side, 'entry_price': entry,
            'quantity': qty, 'sl': sl, 'tp': tp1,
            'score': None,
            'strategy': 'UNKNOWN',   # مصدر المركز غير معروف — يُعرض كما هو بلا ادعاء
            'trailing_active': False, 'highest_price': entry, 'lowest_price': entry,
            'entry_time': time.time(), 'realized_pnl': 0.0,
            'stop_order_id': None, 'tp_order_id': None,
            'stop_state': 'none', 'stop_error': None,
            'stop_synced_price': None,
        }
        self.active_trades[symbol] = trade
        await self.db.save_trade(trade)
        await self._sync_stop_order(trade, entry)
        await self.db.save_trade(trade)
        await self.tg(f"🔄 *تم تبنّي مركز يتيم* (`{symbol}`)\n"
                      f"وقف عند {self.fmt_price(sl)} + TP1 عند {self.fmt_price(tp1)}")
        return True

    # ═══ المصالحة الذاتية عند الإقلاع ═══
    async def reconcile(self):
        if not self.binance_api_key or not self.TRADE_ENABLED:
            return
        try:
            positions = await self._fapi_request('GET', '/fapi/v2/positionRisk', signed=True)
            if not isinstance(positions, list):
                # ⛔ تعذر جلب المراكز الفعلية — لا تُنهى أي صفقة محلية دون تحقق
                # (منع إغلاق وهمي عند انقطاع الشبكة وقت الإقلاع)
                self._notify_error("تعذر جلب المراكز الفعلية للمصالحة",
                                   context="لن تُنهى أي صفقة دون تحقق — تُعاد المحاولة")
                return
            open_pos = {}
            for p in positions:
                try:
                    amt = float(p.get('positionAmt', 0) or 0)
                except (TypeError, ValueError):
                    continue
                if abs(amt) > 0:
                    open_pos[p['symbol']] = p   # الصف الكامل (يشمل الرافعة والهامش)

            # صفقات محلية انتهت أثناء التوقف — بنتيجتها الفعلية من Binance
            for symbol, trade in list(self.active_trades.items()):
                pos = open_pos.get(symbol)
                step = self.step_sizes_cache.get(symbol) or 1.0
                if not pos or abs(float(pos.get('positionAmt', 0) or 0)) < step:
                    pnl_info = await self.get_trade_realized_pnl(symbol, trade)
                    await self._finalize_trade(trade, trade['entry_price'],
                                               "🔄 أُغلق أثناء توقف البوت", pnl_info)

            # مراكز يتيمة → تُتبنّى بحماية كاملة (ستوب + TP1 بهدف الهامش الفعلي)
            for symbol, pos in open_pos.items():
                if symbol in self.active_trades:
                    continue
                await self._adopt_orphan_position(symbol, pos)

            # أوامر الحماية على المنصة: تبنّي الستوبات الحية + إلغاء الأوامر اليتيمة
            orders = await self._fapi_request('GET', '/fapi/v1/openOrders', signed=True)
            if not isinstance(orders, list):
                orders = []
            adopted = cancelled = 0
            for o in orders:
                otype = o.get('type')
                if otype not in ('STOP_MARKET', 'STOP', 'TAKE_PROFIT_MARKET'):
                    continue
                trade = self.active_trades.get(o.get('symbol'))
                if trade is not None:
                    if otype in ('STOP_MARKET', 'STOP'):
                        if not trade.get('stop_order_id'):
                            trade['stop_order_id'] = o.get('orderId')
                            try:
                                sp = float(o.get('stopPrice', 0) or 0)
                            except (TypeError, ValueError):
                                sp = 0.0
                            if sp > 0:
                                trade['stop_synced_price'] = sp
                            if trade.get('stop_state') not in ('verified', 'local'):
                                trade['stop_state'] = 'placed'
                            adopted += 1
                        continue
                    # لا نستخدم أوامر TP على المنصة — إلغاؤها يضمن خروجاً متسقاً
                    # عبر TP1 المحلي المعتمد على هدف الهامش
                    cancelled += 1
                    await self._fapi_request('DELETE', '/fapi/v1/order',
                        {'symbol': o['symbol'], 'orderId': o.get('orderId')}, signed=True,
                        quiet=('-2011', '-2013'))
                    continue
                cancelled += 1
                await self._fapi_request('DELETE', '/fapi/v1/order',
                    {'symbol': o['symbol'], 'orderId': o.get('orderId')}, signed=True,
                    quiet=('-2011', '-2013'))
            if adopted:
                await self.tg(f"🛡️ *مصالحة:* تم تبنّي {adopted} أمر ستوب حي على المنصة")
            if cancelled:
                await self.tg(f"🧹 *تنظيف ذاتي:* أُلغي {cancelled} أمر يتيم على المنصة")
            logger.info(f"🧾 المصالحة الذاتية: {len(open_pos)} مركز حي، {adopted} ستوب مُتبنى، {cancelled} أمر يتيم ملغى")
        except Exception as e:
            self._notify_error("فشل المصالحة الذاتية", exc=e, context="غير قاتل — تُعاد كل دورة")

    # ═══ إيقاف آمن ═══
    async def request_shutdown(self):
        if self._shutdown_requested:
            return
        self._shutdown_requested = True
        logger.info("🛑 طلب إيقاف آمن...")
        try:
            await self.tg("🛑 *إيقاف آمن:* ستوب المنصة/المحلي يحمي المراكز حتى العودة.")
        except Exception:
            pass

    # ═══ الصيانة الذاتية ═══
    def _cleanup_memory(self):
        now = time.time()
        self.reentry_cooldown = {k: v for k, v in self.reentry_cooldown.items() if v > now}
        self.last_discovery_alert = {k: v for k, v in self.last_discovery_alert.items()
                                     if v > now - 7200}
        self._last_reject_log = {k: v for k, v in self._last_reject_log.items()
                                 if v > now - 3600}
        if len(self.error_counts) > 500:
            self.error_counts.clear()
        self._prune_hma_done()

    def _trades_today(self):
        today = time.strftime("%Y-%m-%d")
        return sum(1 for _, d in self.entry_history if d == today)

    async def _send_daily_report(self, day):
        row = await self.db.get_day_stats(day)
        if not row:
            return
        pnl, w, l = row
        wr = (w / (w + l) * 100) if (w + l) > 0 else 0
        await self.tg(f"📊 *تقرير {day}*\n💰 PnL: `{pnl:.4f} USDT`\n"
                      f"🏆 {w}W / {l}L (فوز {wr:.0f}%)")

    async def _heartbeat_and_report(self, loop_count):
        now = time.time()
        today = time.strftime("%Y-%m-%d")
        if today != self._report_day:
            await self._send_daily_report(self._report_day)
            self._report_day = today
        if now - self._last_heartbeat >= 3600:
            self._last_heartbeat = now
            can, risk_reason = self.risk.can_trade()
            await self.tg(f"💓 *النبض:* حي ✓ | مسح #{loop_count} | "
                          f"صفقات اليوم: {self._trades_today()} | مفتوحة: {len(self.active_trades)}\n"
                          f"🛡️ المخاطر: {risk_reason}\n🧭 {self.hma.describe()}")

    # ═══ صيانة تقويم الأخبار ═══
    async def _news_boot(self):
        try:
            await self.news_filter.refresh_calendar()
            ev = self.news_filter.next_event()
            if self.news_filter.enabled and ev:
                await self.tg(f"📰 *فلتر الأخبار نشط* — الحدث القادم: {ev['title']} "
                              f"({ev['cur']}) بعد {max(0, int((ev['ts'] - time.time()) / 60))} دقيقة")
        except Exception:
            pass

    async def _maybe_refresh_news(self):
        if time.time() - self.news_filter.calendar_updated > self.news_filter.CALENDAR_TTL:
            try:
                await self.news_filter.refresh_calendar()
            except Exception:
                pass

    # ═══ اللوب الرئيسي ═══
    # ═══ 🕹️ أوامر المالك من اللوحة — نفس دلالات لوحة V11.3 القديمة (بلا لمس الاستراتيجية) ═══
    async def panel_command(self, action, symbol=None):
        """تنفيذ أمر اللوحة داخل حلقة البوت (يستدعى عبر DASH_BRIDGE).
        pause/resume: منع/إعادة فتح صفقات جديدة — المراقبة والمخارج تستمر دائماً.
        close_one/close_all: إغلاق فوري بسعر السوق عبر نفس مسار الإغلاق الرسمي
        (_close_position + _finalize_trade) فتُحسب النتيجة والمحاسبة كاملة.
        reset_all: مسح السجلات والإحصائيات والأحداث — لا يغلق أي صفقة مفتوحة.
        scan_now: إيقاظ الحلقة لمسح فوري. stop_retry: إعادة تثبيت ستوب المنصة."""
        try:
            # ── ⏸️ إيقاف التداول (طوارئ) ──
            if action == 'pause':
                self.TRADE_ENABLED = False
                ACTION.log('نظام', msg='⏸️ إيقاف التداول من اللوحة — لا صفقات جديدة. '
                                       'المراقبة وإدارة الصفقات المفتوحة والمخارج مستمرة.')
                await self.tg("⏸️ *إيقاف مؤقت من اللوحة*\n"
                              "لا فتح صفقات جديدة — المراقبة والمخارج مستمرة.")
                return {'ok': True, 'trade_enabled': False,
                        'info': 'أُوقف فتح الصفقات الجديدة — إدارة الصفقات المفتوحة مستمرة'}
            # ── ▶️ استئناف التداول ──
            if action == 'resume':
                if not self.binance_api_key or not self.binance_api_secret:
                    return {'ok': False, 'error': 'مفاتيح API ناقصة — لا يمكن استئناف التداول'}
                self.TRADE_ENABLED = True
                ACTION.log('نظام', msg='▶️ استئناف التداول من اللوحة — فتح الصفقات الجديدة عاد.')
                await self.tg("▶️ *استئناف من اللوحة*\nفتح الصفقات الجديدة عاد للعمل.")
                return {'ok': True, 'trade_enabled': True, 'info': 'استُأنف التداول'}
            # ── 🛑 إغلاق صفقة واحدة ──
            if action == 'close_one':
                t = self.active_trades.get(symbol or '')
                if not t:
                    return {'ok': False, 'error': f'لا توجد صفقة مفتوحة على {symbol}'}
                p = self.get_price(symbol) or {}
                px = (p.get('bid') if t['side'] == 'BUY' else p.get('ask')) \
                    or float(t['entry_price'])
                closed, fill, pnl_over = await self._close_position(t, px)
                if not closed:
                    return {'ok': False,
                            'error': f'فشل إغلاق {symbol} الآن — الحمايات قائمة وستُعاد المحاولة تلقائياً'}
                await self._finalize_trade(t, fill, '🛑 إغلاق يدوي من اللوحة (أمر المالك)', pnl_over)
                return {'ok': True, 'closed': [symbol], 'info': f'أُغلقت صفقة {symbol} ومُحسبت نتيجتها'}
            # ── 🛑 إغلاق كل الصفقات ──
            if action == 'close_all':
                closed_syms, failed = [], []
                for sym, t in list(self.active_trades.items()):
                    try:
                        p = self.get_price(sym) or {}
                        px = (p.get('bid') if t['side'] == 'BUY' else p.get('ask')) \
                            or float(t['entry_price'])
                        closed, fill, pnl_over = await self._close_position(t, px)
                        if closed:
                            await self._finalize_trade(
                                t, fill, '🛑 إغلاق جماعي من اللوحة (أمر المالك)', pnl_over)
                            closed_syms.append(sym)
                        else:
                            failed.append(sym)
                    except Exception as ex:
                        logger.error(f"إغلاق {sym} من اللوحة فشل: {ex}")
                        failed.append(sym)
                ACTION.log('نظام', msg=f'🛑 إغلاق جماعي من اللوحة: أُغلق {len(closed_syms)}'
                                + (f' | تعذر: {", ".join(failed)}' if failed else ''))
                await self.tg(f"🛑 *إغلاق جماعي من اللوحة*\n"
                              f"✅ أُغلق: {', '.join(closed_syms) or 'لا شيء'}"
                              + (f"\n⚠️ تعذر (تُعاد محاولته تلقائياً): {', '.join(failed)}"
                                 if failed else ''))
                return {'ok': True, 'closed': closed_syms, 'failed': failed,
                        'info': (f"أُغلق {len(closed_syms)} صفقة"
                                 + (f"، وتعذر {len(failed)} (يُعاد تلقائياً)" if failed else ''))}
            # ── 🧹 إعادة ضبط شامل (نفس نطاق لوحة V11.3 — بلا لمس الصفقات المفتوحة) ──
            if action == 'reset_all':
                cleared = []
                try:
                    async with aiosqlite.connect(self.db.db_name) as db:
                        await db.execute("DELETE FROM signal_log")
                        await db.execute("DELETE FROM daily_stats")
                        await db.execute("DELETE FROM scan_rejections")
                        await db.commit()
                    cleared += ['سجل الصفقات والإشارات', 'الإحصائيات اليومية',
                                'سجل أسباب الرفض']
                except Exception as ex:
                    logger.warning(f"مسح جداول القاعدة أثناء إعادة الضبط: {ex}")
                try:
                    for k in list(self.stats.keys()):
                        self.stats[k] = 0
                    cleared.append('عدّادات الإحصائيات')
                except Exception:
                    pass
                try:
                    self.error_counts.clear()
                    cleared.append('عدّادات الأخطاء')
                except Exception:
                    pass
                try:
                    ACTION.clear()
                    cleared.append('سجل أحداث اللوحة (الذاكرة + ملف JSONL)')
                except Exception:
                    pass
                ACTION.log('نظام', msg='⚙️ إعادة ضبط شامل من اللوحة — تم مسح: '
                           + '، '.join(cleared) + '. الصفقات المفتوحة لم تُمس.')
                await self.tg("⚙️ *إعادة ضبط شامل من اللوحة*\n"
                              f"تم مسح: {'، '.join(cleared) or 'لا شيء'}\n"
                              "✅ الصفقات المفتوحة لم تُمس")
                return {'ok': True, 'cleared': cleared,
                        'info': 'تم المسح الشامل — الشاشة نظيفة وبداية جديدة '
                                '(الصفقات المفتوحة سليمة)'}
            # ── 🔍 مسح فوري ──
            if action == 'scan_now':
                self._scan_now_evt.set()
                ACTION.log('نظام', msg='🔍 أُطلق مسح فوري من اللوحة — الحلقة ستستيقظ الآن')
                return {'ok': True, 'info': 'أُطلق مسح فوري — راقب سجل الأحداث خلال ثوانٍ'}
            # ── 🔁 إعادة محاولة تثبيت ستوب المنصة ──
            if action == 'stop_retry':
                t = self.active_trades.get(symbol or '')
                if not t:
                    return {'ok': False, 'error': f'لا توجد صفقة مفتوحة على {symbol}'}
                p = self.get_price(symbol) or {}
                px = (p.get('bid') if t['side'] == 'BUY' else p.get('ask')) \
                    or float(t['entry_price'])
                ok = await self._sync_stop_order(t, px, force=True)
                if ok:
                    try:
                        await self.db.save_trade(t)
                    except Exception:
                        pass
                return {'ok': bool(ok), 'state': t.get('stop_state'),
                        'stop_error': t.get('stop_error'),
                        'info': ('أُعيد تثبيت ستوب المنصة ✓' if ok else
                                 'تعذر التثبيت الآن — المراقبة المحلية تحمي الصفقة '
                                 'وستُعاد المحاولة تلقائياً')}
            return {'ok': False, 'error': f'أمر غير مدعوم: {action}'}
        except Exception as e:
            logger.error(f"تنفيذ أمر اللوحة {action} فشل: {e}")
            return {'ok': False, 'error': f'خطأ داخلي: {e}'}

    async def main_loop(self):
        self.session = aiohttp.ClientSession()
        try:
            await self.db.init_db()   # الجداول والأعمدة جاهزة قبل إقلاع اللوحة
            self._start_dashboard()
            DASH_BRIDGE.bind(self, asyncio.get_running_loop())   # 🕹️ جسر أوامر اللوحة

            loop = asyncio.get_running_loop()
            for sig_name in ('SIGINT', 'SIGTERM'):
                try:
                    loop.add_signal_handler(getattr(signal, sig_name),
                        lambda: asyncio.ensure_future(self.request_shutdown()))
                except (NotImplementedError, ValueError, AttributeError, RuntimeError):
                    pass

            await self.hma.load()
            await self.risk.load()
            await self.news_filter.load()
            await self._load_hma_done()
            try:
                _he = await self.db.get_param('hma_enabled')
                if _he is not None:
                    self.hma_enabled = (_he == '1')
                _hl = await self.db.get_param('hma_live')
                if _hl is not None:
                    self.HMA_LIVE = (_hl == '1')
            except Exception:
                pass
            asyncio.create_task(self._news_boot())

            market_tries = 0
            while not self.all_futures_pairs:
                market_tries += 1
                await self.load_market_data()
                if self.all_futures_pairs:
                    break
                if market_tries == 1 or market_tries % 5 == 0:
                    await self.tg(f"❌ *فشل تحميل بيانات السوق* (محاولة {market_tries})\n"
                                  "⏳ إعادة خلال 30 ثانية...")
                logger.error(f"فشل تحميل بيانات السوق (محاولة {market_tries})")
                await asyncio.sleep(30)

            self.active_trades = await self.db.load_active_trades()
            await self.sync_server_time()

            # 🛡️ الرصيد المرجعي لمدير المخاطر (أساس السحب اليومي 5%)
            try:
                if self.risk.initial_balance <= 0:
                    self.risk.initial_balance = await self.get_available_usdt()
                    await self.risk.save()
                if self.risk.initial_balance > 0:
                    logger.info(f"🛡️ مدير المخاطر: رصيد مرجعي {self.risk.initial_balance:.2f}$")
            except Exception:
                pass

            try:
                dual = await self._fapi_request('GET', '/fapi/v1/positionSide/dual', signed=True)
                if dual and dual.get('dualSidePosition'):
                    if self.TRADE_ENABLED:
                        self.TRADE_ENABLED = False
                        logger.error("❌ الحساب في وضع Hedge Mode — التحويل للمراقبة فقط")
                        await self.tg("⚠️ *تنبيه:* Hedge Mode مفعّل — البوت لوضع One-way فقط. تم التحويل للمراقبة.")
            except Exception as e:
                logger.warning(f"تعذر فحص Hedge Mode: {e}")

            self.ws_task = asyncio.create_task(self.ws_manager())
            await asyncio.sleep(10)

            if self.TRADE_ENABLED and self.binance_api_key:
                await self.reconcile()
                await self.verify_positions()

            mode_trade = ("⚔️ تداول تلقائي" + (" (TESTNET 🧪)" if self.TESTNET else "")
                          if self.TRADE_ENABLED else "👁️ مراقبة فقط")
            news_txt = (f"مفعّل — تأثير {self.news_filter.impact_min} ±{self.news_filter.before_min}د"
                        if self.news_filter.enabled else "معطل (يُدار من اللوحة)")
            ev_txt = (f"🌙 محظورة {HMA_EVENING_START_UTC}:00–{HMA_EVENING_END_UTC}:59 UTC"
                      if HMA_BLOCK_EVENING_UTC else "معطل (HMA_BLOCK_EVENING=false)")
            msg = ("🎯 *القناص الأسطوري V12.1 — استراتيجية HMA فقط!*\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
                   f"📡 الوضع: {mode_trade} | رافعة {self.LEVERAGE}x | هامش {self.TRADE_SIZE_USDT:g}$\n"
                   f"🧭 الاستراتيجية: HMA_DMI_MOMENTUM ({self.hma.timeframe}) — "
                   f"{'معطلة' if not self.hma_enabled else ('⚔️ تداول فعلي' if self.HMA_LIVE else '👁️ إشارات فقط')}\n"
                   f"🔓 الصفقات المتزامنة: {self.MAX_OPEN_TRADES} (إصلاح الاختناق — كان الحد 1)\n"
                   f"🌙 نافذة المساء: {ev_txt} — المخارج تعمل طوال اليوم\n"
                   f"🔭 المسح: كون {HMA_UNIVERSE_POOL} زوج سائل | دفعة {self.hma.batch_size}/دورة\n"
                   f"🧭 إعدادات HMA: {self.hma.describe()}\n"
                   f"💰 TP1: هدف عائد الهامش — إغلاق 100% عند اللمس (لا TP2)\n"
                   f"⏰ الستوب الزمني: {self.MAX_TRADE_HOURS:g} ساعة كحد أقصى لكل صفقة\n"
                   f"📰 فلتر الأخبار: {news_txt}\n"
                   f"📊 لوحة المراقبة المدمجة: {'المنفذ ' + str(DASHBOARD_PORT) if DASHBOARD_ENABLED else 'معطلة'}\n"
                   f"🕹️ أوامر اللوحة جاهزة: إيقاف طوارئ | إغلاق صفقة/الكل | مسح فوري | إعادة ضبط شامل\n"
                   f"🛡️ مدير المخاطر: 3 متتالية→توقف4س | يومي 3→اليوم | سحب 5%→اليوم\n"
                   "━━━━━━━━━━━━━━━━━━━━━━━━\n⏰ بدء المسح...")
            await self.tg(msg)

            loop_count = 0
            while not self._shutdown_requested:
                try:
                    newest_ts = max((p.get('ts', 0) for p in self.live_prices.values()), default=0)
                    if newest_ts and (time.time() - newest_ts) > self.WS_STALE_ALERT:
                        self._notify_error("توقف تدفق الأسعار (WebSocket)",
                            context=f"لا تحديثات منذ {int(time.time() - newest_ts)} ثانية — الوقف يحمي المراكز")

                    await self.monitor_trades()
                    await self._refresh_universe()
                    try:
                        await self.scan_hma()   # 🧭 دورة مستقلة لاستراتيجية HMA_DMI_MOMENTUM
                    except Exception as hma_err:
                        logger.error(f"خطأ في دورة HMA: {hma_err}")
                        self._notify_error("مسح HMA_DMI_MOMENTUM", exc=hma_err)

                    loop_count += 1
                    self.stats['total_scans'] = loop_count
                    await self._action_sync(loop_count)
                    if loop_count % self.VERIFY_EVERY_N_LOOPS == 0:
                        await self.verify_positions()
                        await self.verify_platform_stops()
                    if loop_count % 10 == 0:
                        await self.db.prune_rejections()
                    await self._maybe_refresh_news()

                    self._cleanup_memory()
                    await self._heartbeat_and_report(loop_count)
                    # ⏱️ نوم قابل للاستيقاظ: أمر "مسح فوري" من اللوحة يقطع النوم
                    try:
                        await asyncio.wait_for(self._scan_now_evt.wait(), timeout=60)
                        self._scan_now_evt.clear()
                        logger.info('🔍 مسح فوري بأمر من اللوحة')
                    except asyncio.TimeoutError:
                        pass
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
    bot = LegendarySniperHMA()
    bot.start()
