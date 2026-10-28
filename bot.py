"""
═══════════════════════════════════════════════════════════════════════
  🔥 القناص الأسطوري V9.1 — Legendary Sniper (Stop Guardian + News AI) 🔥
═══════════════════════════════════════════════════════════════════════
  ✅ V9.1 (هذه النسخة) — حل جذري لمشكلتين:
     🛑 ستوب المنصة لن يفشل بصمت بعد الآن:
        - سلّم محاولات ذكي: STOP_MARKET+closePosition → STOP_MARKET+reduceOnly
          → عند -2021 "سيُفعَّل فوراً": إبعاد السعر تلقائياً وإعادة المحاولة
        - التقاط كود رفض Binance الحقيقي (-2021/-2022/-4061...) وعرضه في اللوحة
        - تحقق فعلي من المنصة (openOrders): الحالة "مؤكد ✓" لا تُعرض إلا بعد
          رؤية الأمر حياً على المنصة — نهاية "STOP_MARKET مثبّت" الوهمية
        - المصالحة تتبنّى أوامر الحماية الحية بدل إلغائها (لا مزيد من قتل الستوبات)
     📰 فلتر الأخبار صار حقيقياً ومفعّلاً:
        - تقويم ForexFactory الأسبوعي الحي (CPI/FOMC/NFP...) كل 4 ساعات
        - كتم تلقائي قبل/بعد الأحداث عالية التأثير — والفشل لا يوقف البوت
        - كل الإعدادات من اللوحة مباشرة (تفعيل/تأثير/دقائق/عملات/نوافذ) —
          محفوظة في قاعدة البيانات، بدون Environment Variables ولا إعادة نشر
  ✅ V9.0 كاملة: ستوك 3 أوضاع + VuManChu Swing + تقييم /10 + مدير مخاطر
═══════════════════════════════════════════════════════════════════════
"""

from datetime import datetime

import asyncio, aiohttp, json, math, os, sys, time, logging, requests
import collections
import pandas as pd
import numpy as np
import hmac
import hashlib
import signal
from decimal import Decimal
from urllib.parse import urlencode
from logging.handlers import RotatingFileHandler
import websockets
import aiosqlite
from web_panel import start_web_panel, notify as panel_notify

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logger = logging.getLogger('SniperV9')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh = RotatingFileHandler('bot_v8.log', maxBytes=2*1024*1024, backupCount=2, encoding='utf-8')
fh.setFormatter(fmt); logger.addHandler(fh)
ch = logging.StreamHandler(); ch.setFormatter(fmt); logger.addHandler(ch)

# ─── دالة فحص الـ IP الصادر عند الإقلاع ───
def check_outbound_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        ip_address = response.json().get('ip')
        logger.info(f"Current Outbound IP on Railway: {ip_address}")
        return ip_address
    except Exception as e:
        logger.warning(f"Failed to fetch IP: {e}")
        return None

# استدعاء الفحص مباشرة عند بدء التشغيل
check_outbound_ip()

# ═══════════════════════ قاعدة البيانات ═════════════════════
class DatabaseManager:
    def __init__(self, db_name='sniper_v8.db'):
        self.db_name = db_name

    async def init_db(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS active_trades (
                symbol TEXT PRIMARY KEY, side TEXT, entry_price REAL, quantity REAL,
                sl REAL, tp REAL, tp2 REAL, trailing_active INTEGER, highest_price REAL,
                lowest_price REAL, entry_time REAL, partial_closed INTEGER,
                realized_pnl REAL DEFAULT 0, stop_order_id INTEGER, tp_order_id INTEGER)""")
            for col_def in ('realized_pnl REAL DEFAULT 0', 'stop_order_id INTEGER',
                            'tp2 REAL', 'tp_order_id INTEGER',
                            'stop_state TEXT', 'stop_error TEXT'):
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
                    (symbol, direction, entry_ts, score, json.dumps(components, ensure_ascii=False)))
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
                 realized_pnl, stop_order_id, tp_order_id, stop_state, stop_error)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (t['symbol'], t['side'], t['entry_price'], t['quantity'],
                 t['sl'], t['tp'], t.get('tp2'), int(t.get('trailing_active', False)),
                 t.get('highest_price', 0), t.get('lowest_price', 999999),
                 t['entry_time'], int(t.get('partial_closed', 0)),
                 float(t.get('realized_pnl', 0.0)), t.get('stop_order_id'), t.get('tp_order_id'),
                 t.get('stop_state'), t.get('stop_error')))
            await db.commit()

    async def load_active_trades(self):
        trades = {}
        try:
            async with aiosqlite.connect(self.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""SELECT symbol, side, entry_price, quantity, sl, tp, tp2,
                    trailing_active, highest_price, lowest_price, entry_time, partial_closed,
                    realized_pnl, stop_order_id, tp_order_id, stop_state, stop_error
                    FROM active_trades""") as cur:
                    async for row in cur:
                        trades[row['symbol']] = {
                            'symbol': row['symbol'], 'side': row['side'],
                            'entry_price': row['entry_price'], 'quantity': row['quantity'],
                            'sl': row['sl'], 'tp': row['tp'], 'tp2': row['tp2'],
                            'trailing_active': bool(row['trailing_active']),
                            'highest_price': row['highest_price'],
                            'lowest_price': row['lowest_price'],
                            'entry_time': row['entry_time'],
                            'partial_closed': bool(row['partial_closed']),
                            'realized_pnl': row['realized_pnl'] if row['realized_pnl'] is not None else 0.0,
                            'stop_order_id': row['stop_order_id'],
                            'tp_order_id': row['tp_order_id'],
                            'stop_state': row['stop_state'] or 'none',
                            'stop_error': row['stop_error'],
                            'stop_synced_price': None, 'tp_skipped': False
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


# ═══════════════════════ المطوّر التكيفي (Self-Tuning) ═════════════════════
class AdaptiveTuner:
    """
    ✅ V9.0: min_score مثبت عند 6/10 بقرار المالك — لا يُخفَّض أبداً
    - stoch_strictness: 0=معطل | 1=مرن (افتراضي — لا يرفض الإشارات) | 2=صارم
      (الوضع الصارم القديم كان سبب قلة/تأخر الإشارات — أصبح اختيارياً)
    - vmc_enabled: تفعيل مؤشر VuManChu Swing (+2 نقاط تقييم)
    - كل معاملات التحليل محفوظة ومعروضة في اللوحة: SL/TP1×ATR، الجني الجزئي،
      الوقف المتحرك، أقصى مخاطرة للصفقة
    """
    STOCH_MODES = {0: 'معطل', 1: 'مرن', 2: 'صارم'}

    def __init__(self, db):
        self.db = db
        self.min_score = 6          # ✅ ثابت — لا صفقات بتقييم أقل من 6/10
        self.proximity_pct = 0.02
        self.stoch_strictness = 1   # ✅ V9.0: مرن افتراضياً (كان strict_stoch=True قاتلاً للإشارات)
        self.vmc_enabled = True     # ✅ V9.0: مؤشر VuManChu Swing
        self.sl_atr_mult = 2.0      # مضاعف ATR للوقف
        self.tp1_atr_mult = 1.5     # مضاعف ATR للهدف الأول
        self.partial_ratio = 0.7    # الجني الجزئي الأساسي (الديناميكي حسب التقييم 8-10/6-7)
        self.volatility_threshold = 3.0   # أقصى مخاطرة % للصفقة
        self.trailing_pct = 0.01    # الوقف المتحرك 1% بعد الجني الجزئي
        self.results = collections.deque(maxlen=20)

    def _clamp(self):
        self.min_score = 6          # ✅ أمان ثابت
        self.proximity_pct = max(0.015, min(0.045, float(self.proximity_pct)))
        self.stoch_strictness = max(0, min(2, int(self.stoch_strictness)))
        self.sl_atr_mult = max(1.0, min(4.0, float(self.sl_atr_mult)))
        self.tp1_atr_mult = max(0.8, min(4.0, float(self.tp1_atr_mult)))
        self.partial_ratio = max(0.3, min(0.95, float(self.partial_ratio)))
        self.volatility_threshold = max(0.5, min(10.0, float(self.volatility_threshold)))
        self.trailing_pct = max(0.003, min(0.03, float(self.trailing_pct)))

    async def load(self):
        raw = await self.db.get_param('tuner')
        if raw:
            try:
                d = json.loads(raw)
                self.min_score = max(6, int(d.get('min_score', 6)))
                self.proximity_pct = float(d.get('proximity_pct', 0.02))
                # ✅ توافق خلفي مع V8.2 (strict_stoch منطقية ← stoch_strictness رقمية)
                if 'stoch_strictness' in d:
                    self.stoch_strictness = int(d.get('stoch_strictness', 1))
                else:
                    self.stoch_strictness = 2 if d.get('strict_stoch', True) else 1
                self.vmc_enabled = bool(d.get('vmc_enabled', True))
                self.sl_atr_mult = float(d.get('sl_atr_mult', 2.0))
                self.tp1_atr_mult = float(d.get('tp1_atr_mult', 1.5))
                self.partial_ratio = float(d.get('partial_ratio', 0.7))
                self.volatility_threshold = float(d.get('volatility_threshold', 3.0))
                self.trailing_pct = float(d.get('trailing_pct', 0.01))
                self.results = collections.deque(d.get('results', [])[-20:], maxlen=20)
                self._clamp()
                logger.info(f"🧠 المطوّر التكيفي محمّل: {self.describe()}")
            except Exception as e:
                logger.warning(f"تعذر تحميل المطوّر التكيفي (سيبدأ افتراضياً): {e}")

    async def save(self):
        try:
            await self.db.set_param('tuner', json.dumps({
                'min_score': self.min_score, 'proximity_pct': self.proximity_pct,
                'stoch_strictness': self.stoch_strictness,
                'vmc_enabled': self.vmc_enabled,
                'sl_atr_mult': self.sl_atr_mult, 'tp1_atr_mult': self.tp1_atr_mult,
                'partial_ratio': self.partial_ratio,
                'volatility_threshold': self.volatility_threshold,
                'trailing_pct': self.trailing_pct,
                'results': list(self.results)}))
        except Exception as e:
            logger.warning(f"تعذر حفظ المطوّر التكيفي: {e}")

    def record(self, win):
        self.results.append(bool(win))

    def recent_winrate(self, n=10):
        recent = list(self.results)[-n:]
        if len(recent) < 5:
            return None
        return sum(recent) / len(recent)

    def relax_step(self):
        # ✅ يحافظ على ≥6 دائماً — الارتخاء في نطاق القرب فقط
        before = round(self.proximity_pct, 4)
        if self.proximity_pct < 0.045:
            self.proximity_pct = round(min(0.045, self.proximity_pct + 0.005), 4)
        return before != round(self.proximity_pct, 4)

    def tighten_step(self):
        # ✅ V9.0: التشديد في القرب فقط — لا يعيد الصرامة القاتلة للإشارات تلقائياً
        before = (self.stoch_strictness, round(self.proximity_pct, 4))
        if self.proximity_pct > 0.02:
            self.proximity_pct = round(max(0.02, self.proximity_pct - 0.005), 4)
        self.stoch_strictness = max(self.stoch_strictness, 1)   # مرن على الأقل — لا صارم تلقائياً
        return before != (self.stoch_strictness, round(self.proximity_pct, 4))

    def describe(self):
        return (f"min_score={self.min_score}/10 | قرب OB≤{self.proximity_pct*100:.1f}% | "
                f"ستوك: {self.STOCH_MODES.get(self.stoch_strictness, 'مرن')} | "
                f"VMC: {'مفعّل' if self.vmc_enabled else 'معطل'}")


# ═══════════════════════ مدير المخاطر (V9.0 — متزامن مع اللوحة) ═════════════════════
class RiskManager:
    """
    حماية رأس المال — كل قيمه معروضة في تبويب 🛡️ إدارة المخاطر باللوحة:
    - 3 خسائر متتالية → توقف 4 ساعات
    - 3 خسائر في اليوم → توقف بقية اليوم
    - سحب يومي 5% من الرصيد الابتدائي → توقف بقية اليوم
    """
    MAX_CONSEC_LOSSES = 3
    PAUSE_HOURS = 4
    MAX_DAILY_LOSSES = 3
    MAX_DAILY_DRAWDOWN_PCT = 5.0

    def __init__(self):
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

    def register_result(self, pnl):
        """تسجيل نتيجة صفقة مغلقة (تُستدعى من _finalize_trade)"""
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

    def can_trade(self):
        """يعيد (مسموح؟، السبب) — يُعرض في اللوحة مباشرة"""
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


# ═══════════════════════ فلتر الأخبار V2 (V9.1 — حقيقي ومُدار من اللوحة) ═══════════════════════
class NewsFilter:
    """
    ✅ V9.1: نهاية "فلتر الأخبار معطل" — فلتر حقيقي:
    - مصدر حي: تقويم ForexFactory الأسبوعي (JSON مجاني بدون مفتاح)
      يُجلب كل 4 ساعات ويشمل CPI/FOMC/NFP وكل أحداث الماكرو المؤثرة
    - كتم الإشارات تلقائياً قبل/بعد الأحداث المطابقة (تأثير + عملة)
    - كل الإعدادات في قاعدة البيانات → تُعدّل من اللوحة لحظياً بدون إعادة نشر
    - نوافذ يدوية إضافية بتوقيت UTC "HH:MM-HH:MM,..." (اختياري)
    - فشل الجلب لا يوقف التداول (Fail-open) وحالة الجلب تُعرض في اللوحة
    """
    CALENDAR_URL = 'https://nfs.faireconomy.media/ff_calendar_thisweek.json'
    CALENDAR_TTL = 4 * 3600
    IMPACT_RANK = {'Holiday': 0, 'Low': 1, 'Medium': 2, 'High': 3}

    def __init__(self, db=None):
        self.db = db
        self.enabled = True          # ✅ مفعّل افتراضياً — قرار المالك (نهاية "معطل")
        self.impact_min = 'High'     # High فقط افتراضياً (CPI/FOMC/NFP...)
        self.currencies = 'USD'      # العملات المتابعة (فاصلة بينها)
        self.before_min = 30         # كتم قبل الحدث (دقيقة)
        self.after_min = 30          # كتم بعد الحدث (دقيقة)
        self.blackout_windows = []   # نوافذ يدوية UTC [(بداية_دقيقة, نهاية_دقيقة)]
        self.events = []             # [{'title','cur','impact','ts'}]
        self.calendar_updated = 0.0
        self.last_fetch_ok = False
        self.last_error = None
        self.rejected_total = 0

    # ─── الحفظ/التحميل: قاعدة البيانات هي مصدر الحقيقة ───
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
            # بذرة توافقية مع V9.0: من فعّله عبر ENV سابقاً يبقى مفعّلاً
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

    # ─── جلب التقويم الحي (لا يرفع استثناءً أبداً) ───
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

    # ─── المطابقة ───
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
        """✅ V9.1: يعيد (محظور؟، السبب) — السبب يُعرض في اللوحة والإشعارات"""
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
                            'time': time.strftime('%m-%d %H:%M', time.gmtime(nxt['ts'])) + ' UTC'}
                           if nxt else None),
            'calendar_updated': int(self.calendar_updated),
            'calendar_age_min': (int((time.time() - self.calendar_updated) / 60)
                                 if self.calendar_updated else None),
            'events_count': len(self.events),
            'last_fetch_ok': self.last_fetch_ok,
            'last_error': self.last_error,
            'rejected_total': self.rejected_total,
        }


# ═══════════════════════ محرك SMC - صياد الحيتان ═════════════════════
class WhaleSMCEngine:
    @staticmethod
    def detect_order_blocks(df, trend):
        obs = []
        threshold = 0.015

        for i in range(2, len(df)-1):
            if df['close'].iloc[i] > df['open'].iloc[i]:
                impulse_pct = (df['close'].iloc[i] - df['low'].iloc[i-1]) / df['low'].iloc[i-1]
                if df['close'].iloc[i-1] < df['open'].iloc[i-1] and impulse_pct > threshold:
                    obs.append({'type': 'demand', 'top': df['open'].iloc[i-1],
                                'bottom': df['low'].iloc[i-1], 'index': i-1})
            elif df['close'].iloc[i] < df['open'].iloc[i]:
                impulse_pct = (df['high'].iloc[i-1] - df['close'].iloc[i]) / df['high'].iloc[i-1]
                if df['close'].iloc[i-1] > df['open'].iloc[i-1] and impulse_pct > threshold:
                    obs.append({'type': 'supply', 'top': df['high'].iloc[i-1],
                                'bottom': df['close'].iloc[i-1], 'index': i-1})
        return obs

    @staticmethod
    def detect_liquidity_sweep(df_15m, ob_zone, direction):
        """تصفية سيولة (الزناد القوي) — الشمعة المغلقة الأخيرة فقط (منع Repainting)"""
        current_low = df_15m['low'].iloc[-2]
        current_high = df_15m['high'].iloc[-2]
        current_close = df_15m['close'].iloc[-2]
        prev_close = df_15m['close'].iloc[-3]

        if direction == 'BUY' and ob_zone['type'] == 'demand':
            if current_low < ob_zone['bottom'] and current_close > ob_zone['top'] and current_close > prev_close:
                return True
        elif direction == 'SELL' and ob_zone['type'] == 'supply':
            if current_high > ob_zone['top'] and current_close < ob_zone['bottom'] and current_close < prev_close:
                return True
        return False

    @staticmethod
    def detect_ob_retest(df_15m, ob_zone, direction):
        """الزناد البديل: إعادة اختبار المنطقة خلال آخر 3 شمعات"""
        lows = df_15m['low'].iloc[-4:-1]
        highs = df_15m['high'].iloc[-4:-1]
        closes = df_15m['close'].iloc[-4:-1]
        if len(closes) < 3:
            return False
        if direction == 'BUY' and ob_zone['type'] == 'demand':
            touched = bool((lows <= ob_zone['top']).any())
            return bool(touched and closes.iloc[-1] > ob_zone['top'] and closes.iloc[-1] > closes.iloc[-2])
        if direction == 'SELL' and ob_zone['type'] == 'supply':
            touched = bool((highs >= ob_zone['bottom']).any())
            return bool(touched and closes.iloc[-1] < ob_zone['bottom'] and closes.iloc[-1] < closes.iloc[-2])
        return False

    @staticmethod
    def calculate_stochastic(df, k_period=14, d_period=3):
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()
        diff = (high_max - low_min).replace(0, np.nan)
        df['stoch_k'] = 100 * ((df['close'] - low_min) / diff)
        df['stoch_d'] = df['stoch_k'].rolling(window=d_period).mean()
        df['stoch_k'] = df['stoch_k'].fillna(50)
        df['stoch_d'] = df['stoch_d'].fillna(50)
        return df

    # ═══ ✅ V9.0: مؤشر VuManChu Swing (WaveTrend) ═══
    @staticmethod
    def calculate_vumanchu(df, channel_len=10, avg_len=21, smooth=7, wt_smooth=3):
        """
        VuManChu Swing — مذبذب WaveTrend (نمط LazyBear):
        wt1 = خط سريع (TCI)، wt2 = خط الإشارة (SMA3).
        تقاطع wt1 فوق/تحت wt2 بعد مناطق التشبع (-53/+53) = إشارة زخم قوية.
        يضيف عمودي vmc_wt1 / vmc_wt2 إلى df.
        """
        ap = (df['high'] + df['low'] + df['close']) / 3.0
        esa = ap.ewm(span=channel_len, adjust=False).mean()
        dev = (ap - esa).abs().ewm(span=avg_len, adjust=False).mean()
        dev = dev.replace(0, np.nan)
        ci = (ap - esa) / (0.015 * dev)
        wt1 = ci.ewm(span=smooth, adjust=False).mean()
        wt2 = wt1.rolling(wt_smooth).mean()
        df['vmc_wt1'] = wt1.fillna(0.0)
        df['vmc_wt2'] = wt2.fillna(0.0)
        return df


# ══════════════════════════════════════════════════════════════════════
#        🔥 القناص الأسطوري V9.1 (Stop Guardian + News AI) 🔥
# ══════════════════════════════════════════════════════════════════════
class LegendarySniperFuturesV8:
    def __init__(self):
        self.binance_api_key = os.environ.get('BINANCE_API_KEY', '')
        self.binance_api_secret = os.environ.get('BINANCE_API_SECRET', '')

        self.TRADE_ENABLED = os.environ.get('TRADE_ENABLED', 'false').lower() == 'true'
        self.LEVERAGE = 10
        self.TRADE_SIZE_USDT = float(os.environ.get('TRADE_SIZE_USDT', '25'))
        self.MAX_OPEN_TRADES = int(os.environ.get('MAX_OPEN_TRADES', '1'))
        self.TESTNET = os.environ.get('TESTNET', 'false').lower() == 'true'

        problems = []
        if self.TRADE_SIZE_USDT <= 0:
            problems.append("TRADE_SIZE_USDT يجب أن يكون أكبر من صفر")
        if not (1 <= self.MAX_OPEN_TRADES <= 10):
            problems.append("MAX_OPEN_TRADES يجب أن يكون بين 1 و 10")
        if self.TESTNET:
            logger.info("🧪 وضع Testnet التجريبي مفعّل")
        if problems:
            raise SystemExit("❌ إعدادات خاطئة:\n- " + "\n- ".join(problems))

        if self.TRADE_ENABLED and (not self.binance_api_key or not self.binance_api_secret):
            self.TRADE_ENABLED = False
            logger.error("❌ التداول مفعّل لكن مفاتيح API ناقصة! التحويل للمراقبة فقط")

        self.PRICE_MAX_AGE = 30
        self.REENTRY_COOLDOWN = 900
        self.VERIFY_EVERY_N_LOOPS = 5
        self.WS_STALE_ALERT = 120
        self.BALANCE_CACHE_SECONDS = 60

        self.data_url = "https://fapi.binance.com"
        self.trade_url = ("https://testnet.binancefuture.com" if self.TESTNET
                          else "https://fapi.binance.com")
        self.time_offset_ms = 0

        self.db = DatabaseManager()
        self.smc = WhaleSMCEngine()
        self.tuner = AdaptiveTuner(self.db)
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
        self._last_tighten = 0
        self._balance_cache = (0.0, 0.0)

        # ✅ V9.0: مدير المخاطر + فلتر الأخبار (متزامنان مع اللوحة)
        self.risk = RiskManager()
        self.news_filter = NewsFilter(self.db)   # ✅ V9.1: مُدار من اللوحة عبر القاعدة

        # ✅ V9.0: إحصائيات موسعة يعرضها تبويب المخاطر في اللوحة
        self.stats = {'total_scans': 0, 'trades_executed': 0, 'wins': 0, 'losses': 0,
                      'signals_found': 0, 'total_signals': 0,
                      'rejected_by_risk': 0, 'rejected_by_news': 0}

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
        if price is None or price == 0: return "$0"
        if price < 0.00001: return f"${price:.10f}"
        elif price < 0.001: return f"${price:.6f}"
        elif price < 1: return f"${price:.4f}"
        elif price < 100: return f"${price:.2f}"
        else: return f"${price:,.1f}"

    async def tg(self, msg):
        """✅ كل إشعار يذهب للوحة"""
        try:
            first_line = msg.split('\n')[0].replace('*', '').strip()
            kind = 'info'
            if msg.startswith('✅') or 'صفقة منفذة' in msg: kind = 'trade'
            elif msg.startswith('🎯') or 'جني' in first_line: kind = 'partial'
            elif msg.startswith('🏁') or 'إغلاق' in first_line: kind = 'close'
            elif msg.startswith('🚨') or 'خطأ' in first_line or msg.startswith('⚠️'): kind = 'error'
            elif 'المطوّر' in first_line or msg.startswith('🧠'): kind = 'tuner'
            elif msg.startswith('🛑'): kind = 'system'
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

    async def _fapi_request(self, method, endpoint, params=None, signed=False, retries=3,
                            quiet=(), soft=(), detailed=False):
        """
        ✅ V9.1: مع detailed=True يعيد عند الفشل {'_error','_status','_code','_msg'}
        بكود رفض Binance الحقيقي — أساس تشخيص "تعذر وضع الستوب" في اللوحة.
        """
        last_err = None
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
                    # ✅ V9.1: فك كود الرفض الحقيقي من جسم الرد
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
                if attempt == retries - 1:
                    if detailed:
                        return last_err
                    self._notify_error("انتهت مهلة طلب Binance", context=endpoint)
                    return None
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                last_err = {'_error': True, '_status': 0, '_code': None, '_msg': str(e)[:200]}
                if attempt == retries - 1:
                    if detailed:
                        return last_err
                    self._notify_error("فشل طلب Binance", exc=e, context=endpoint)
                    return None
                await asyncio.sleep(2 ** attempt)
        return last_err if detailed else None

    async def setup_futures_account(self):
        msg = f"⚙️ *إعداد حساب العقود الآجلة (الرافعة {self.LEVERAGE}x)*\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
        setup_count = 0
        for pair in self.all_futures_pairs[:50]:
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
            await asyncio.sleep(0.15)
        msg += f"✅ تم ضبط الرافعة والهامش المعزول لـ {setup_count} زوج"
        await self.tg(msg)

    async def load_market_data(self):
        data = await self._fapi_request('GET', '/fapi/v1/exchangeInfo')
        if not data: return
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

    # ═══ أدوات التنسيق الدقيق ═══
    @staticmethod
    def _decimals_of(step):
        try:
            exp = Decimal(str(step)).normalize().as_tuple().exponent
            return max(0, -exp)
        except Exception:
            return 8

    def _step_qty(self, symbol, qty):
        step = self.step_sizes_cache.get(symbol) or 1.0
        if step <= 0: step = 1.0
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
            if price >= 100: dec = 2
            elif price >= 1: dec = 4
            elif price >= 0.01: dec = 6
            else: dec = 8
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
        self.reentry_cooldown[symbol] = time.time() + self.REENTRY_COOLDOWN

    def is_in_cooldown(self, symbol):
        expiry = self.reentry_cooldown.get(symbol, 0)
        if time.time() < expiry: return True
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
                'time','open','high','low','close','volume',
                'close_time','quote_volume','trades','taker_buy_vol',
                'taker_buy_quote_vol','ignore'])
            for col in ['open','high','low','close','volume','quote_volume']:
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

    # ═══ ✅ V8.2: الخروج الديناميكي — الجودة تكافأ بخطة أوسع ═══
    @staticmethod
    def _exit_plan(score):
        """
        إشارة أقوى → قبض أقل عند TP1 + هدف أبعد
        إشارة عادية → قبض سريع (Hit & Run كلاسيكي)
        """
        if score >= 8:
            return {'partial_ratio': 0.5, 'tp2_mult': 5.0}   # ذهبية (8-10): نصف يركض لنحو 5×ATR
        elif score >= 6:
            return {'partial_ratio': 0.7, 'tp2_mult': 4.5}   # جيدة (6-7): 70/30 بهدف 4.5×ATR
        else:
            return {'partial_ratio': 0.9, 'tp2_mult': 4.0}   # عادية: كلاسيكي

    # ═══ التحليل بنظام التقييم المرن ═══
    async def analyze_whale_zone(self, symbol):
        tuner = self.tuner
        df_4h = await self.get_klines(symbol, '4h', 100)
        df_1h = await self.get_klines(symbol, '1h', 100)
        df_15m = await self.get_klines(symbol, '15m', 100)
        if (df_4h is None or len(df_4h) < 30 or df_1h is None or len(df_1h) < 30
                or df_15m is None or len(df_15m) < 30):
            return None

        prices = self.get_price(symbol)
        if not prices: return None

        mid = (prices['bid'] + prices['ask']) / 2
        ema50_4h = df_4h['close'].ewm(span=50, adjust=False).mean().iloc[-1]
        trend = 'BUY' if mid > ema50_4h else 'SELL'
        current_price = prices['ask'] if trend == 'BUY' else prices['bid']

        # 1) قرب منطقة الحوت
        obs = self.smc.detect_order_blocks(df_1h, trend)
        if not obs: return None
        nearby_ob = None
        proximity_pts = 0
        for ob in reversed(obs):
            if trend == 'BUY' and ob['type'] == 'demand':
                distance_pct = (current_price - ob['top']) / current_price
                if -0.005 <= distance_pct <= tuner.proximity_pct:
                    nearby_ob = ob
                    proximity_pts = 2 if distance_pct <= 0.01 else 1
                    break
            elif trend == 'SELL' and ob['type'] == 'supply':
                distance_pct = (ob['bottom'] - current_price) / current_price
                if -0.005 <= distance_pct <= tuner.proximity_pct:
                    nearby_ob = ob
                    proximity_pts = 2 if distance_pct <= 0.01 else 1
                    break
        if not nearby_ob: return None

        # 2) الزناد
        sweep = self.smc.detect_liquidity_sweep(df_15m, nearby_ob, trend)
        retest = False if sweep else self.smc.detect_ob_retest(df_15m, nearby_ob, trend)
        if not (sweep or retest): return None
        trigger_pts = 3 if sweep else 2

        # 3) الاستوكاستك
        df_15m = self.smc.calculate_stochastic(df_15m)
        current_k = df_15m['stoch_k'].iloc[-2]
        prev_k = df_15m['stoch_k'].iloc[-3]
        current_d = df_15m['stoch_d'].iloc[-2]
        prev_d = df_15m['stoch_d'].iloc[-3]

        # ✅ V9.0: 3 أوضاع بدل البوابة الصارمة (حل قلة/تأخر الإشارات)
        stoch_pts = 0
        if tuner.stoch_strictness == 2:
            # صارم (سلوك V8.2 القديم): تقاطع حتمي في الشمعة المغلقة الأخيرة وإلا رفض
            if trend == 'BUY':
                if not (current_k > current_d and prev_k <= prev_d):
                    return None
                stoch_pts = 2 if current_k < 20 else 0
            else:
                if not (current_k < current_d and prev_k >= prev_d):
                    return None
                stoch_pts = 2 if current_k > 80 else 0
        elif tuner.stoch_strictness == 1:
            # ✅ مرن (افتراضي): التوجيه يكفي — لا رفض
            # تقاطع جديد بمنطقة تشبع = 2 | توافق اتجاهي = 1 | تعارض = 0 (بدون رفض)
            fresh_cross = (current_k > current_d and prev_k <= prev_d) if trend == 'BUY' \
                else (current_k < current_d and prev_k >= prev_d)
            aligned = (current_k > current_d) if trend == 'BUY' else (current_k < current_d)
            in_zone = (current_k < 35) if trend == 'BUY' else (current_k > 65)
            if fresh_cross:
                stoch_pts = 2 if in_zone else 1
            elif aligned:
                stoch_pts = 1
            # الوضع 0 (معطل): 0 نقاط ولا رفض — القرار لبقية المكونات

        # ✅ V9.0: مؤشر VuManChu Swing (WaveTrend) — حتى +2 نقطة
        vmc_pts = 0
        if tuner.vmc_enabled:
            df_15m = self.smc.calculate_vumanchu(df_15m)
            wt1_now = df_15m['vmc_wt1'].iloc[-2]
            wt1_prev = df_15m['vmc_wt1'].iloc[-3]
            wt2_now = df_15m['vmc_wt2'].iloc[-2]
            wt2_prev = df_15m['vmc_wt2'].iloc[-3]
            if trend == 'BUY':
                vmc_cross = wt1_now > wt2_now and wt1_prev <= wt2_prev
                vmc_aligned = wt1_now > wt2_now and wt1_now > wt1_prev
            else:
                vmc_cross = wt1_now < wt2_now and wt1_prev >= wt2_prev
                vmc_aligned = wt1_now < wt2_now and wt1_now < wt1_prev
            if vmc_cross:
                vmc_pts = 2      # تقاطع WaveTrend جديد = تأكيد زخم قوي
            elif vmc_aligned:
                vmc_pts = 1      # توافق اتجاهي

        # 4) حجم التداول
        vol_pts = 0
        try:
            qv = df_15m['quote_volume']
            base = qv.iloc[-22:-2].mean()
            if base and qv.iloc[-2] > base * 1.3:
                vol_pts = 1
        except Exception:
            pass

        score = proximity_pts + trigger_pts + stoch_pts + vol_pts + vmc_pts
        if score < tuner.min_score:
            return None

        # 5) الدخول والأهداف + ✅ V8.2: خطة خروج ديناميكية
        atr = self._compute_atr(df_15m)
        if not atr or atr <= 0 or math.isnan(atr):
            return None
        exit_plan = self._exit_plan(score)
        sl_buffer = atr * tuner.sl_atr_mult      # ✅ V9.0: قابل للضبط (يظهر في اللوحة)
        if trend == 'BUY':
            sl = nearby_ob['bottom'] - sl_buffer
            tp1 = current_price + atr * tuner.tp1_atr_mult   # ✅ V9.0: قابل للضبط
            tp2 = current_price + atr * exit_plan['tp2_mult']   # ✅ ديناميكي
        else:
            sl = nearby_ob['top'] + sl_buffer
            tp1 = current_price - atr * tuner.tp1_atr_mult   # ✅ V9.0: قابل للضبط
            tp2 = current_price - atr * exit_plan['tp2_mult']   # ✅ ديناميكي

        if sl <= 0 or math.isnan(sl): return None
        if trend == 'BUY' and sl >= current_price: return None
        if trend == 'SELL' and sl <= current_price: return None

        risk_pct = abs(current_price - sl) / current_price * 100
        if risk_pct > tuner.volatility_threshold or risk_pct < 0.05:   # ✅ V9.0: من المطوّر
            return None

        return {
            'symbol': symbol, 'direction': trend, 'price': current_price,
            'sl': sl, 'tp1': tp1, 'tp2': tp2, 'score': score,
            'exit_plan': exit_plan,
            'components': {
                'proximity': proximity_pts,
                'trigger': 'sweep' if sweep else 'retest',
                'trigger_pts': trigger_pts,
                'stoch': stoch_pts,
                'stoch_mode': tuner.stoch_strictness,
                'vmc': vmc_pts,
                'volume': vol_pts,
                'score': score,
                'tuner': tuner.describe()
            },
            'signals_smc': [
                f"🐋 {'صيد حوت' if sweep else 'إعادة اختبار'} في منطقة {'طلب' if trend=='BUY' else 'عرض'}",
                f"📊 تقييم الإشارة: {score}/10",
                f"🌀 VuManChu: {vmc_pts}/2 | ستوك ({tuner.STOCH_MODES.get(tuner.stoch_strictness, 'مرن')}): {stoch_pts}/2",
                f"🛡️ وقف ATR ({risk_pct:.1f}%)"]
        }

    # ═══ التنفيذ ═══
    async def execute_trade(self, analysis):
        if not self.TRADE_ENABLED: return
        if len(self.active_trades) >= self.MAX_OPEN_TRADES: return

        # ✅ V9.0: بوابة مدير المخاطر (3 متتالية → 4س | يومي 3 → اليوم | سحب 5%)
        can, reason = self.risk.can_trade()
        if not can:
            self.stats['rejected_by_risk'] += 1
            logger.warning(f"🛡️ إشارة {analysis['symbol']} مرفوضة بالمخاطر: {reason}")
            return

        # ✅ V9.1: فلتر الأخبار الحقيقي (تقويم حي + نوافذ — يُدار من اللوحة)
        news_blocked, news_reason = self.news_filter.is_blocked_now()
        if news_blocked:
            self.stats['rejected_by_news'] += 1
            self.news_filter.rejected_total += 1
            logger.info(f"📰 إشارة {analysis['symbol']} مرفوضة — {news_reason}")
            return

        symbol = analysis['symbol']
        if symbol in self.active_trades: return
        if self.is_in_cooldown(symbol): return

        available = await self.get_available_usdt()
        if available < self.TRADE_SIZE_USDT * 1.2:
            self._notify_error("رصيد غير كافٍ للدخول",
                               context=f"المتاح {available:.2f}$ < المطلوب {self.TRADE_SIZE_USDT * 1.2:.2f}$")
            return

        notional = self.TRADE_SIZE_USDT * self.LEVERAGE
        quantity = self.format_quantity(symbol, notional / analysis['price'])
        if quantity <= 0: return
        if quantity < self.min_qty_cache.get(symbol, 0.0): return
        if quantity > self.max_qty_cache.get(symbol, 1e12): return
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

        trade_data = {
            'symbol': symbol, 'side': side, 'entry_price': entry_price,
            'quantity': quantity, 'sl': analysis['sl'], 'tp': analysis['tp1'],
            'tp2': analysis['tp2'],
            'score': analysis.get('score'),
            'partial_ratio': analysis.get('exit_plan', {}).get('partial_ratio', 0.9),  # ✅ V8.2
            'trailing_active': False, 'highest_price': entry_price,
            'lowest_price': entry_price, 'entry_time': time.time(),
            'partial_closed': False, 'realized_pnl': 0.0,
            'stop_order_id': None, 'tp_order_id': None,
            'stop_state': 'none', 'stop_error': None,
            'stop_synced_price': None, 'tp_skipped': False
            }
        self.active_trades[symbol] = trade_data
        await self.db.save_trade(trade_data)
        self.stats['trades_executed'] += 1
        self.entry_history.append((time.time(), time.strftime("%Y-%m-%d")))
        await self.db.log_signal(symbol, side, trade_data['entry_time'],
                                 analysis['score'], analysis['components'])

        prices = self.get_price(symbol)
        ref_price = (prices['bid'] if side == 'BUY' else prices['ask']) if prices else entry_price
        await self._sync_stop_order(trade_data, ref_price)
        await self.db.save_trade(trade_data)

        # ✅ V8.2: رسالة الخطة للشفافية + ✅ V9.1: حالة الستوب الحقيقية
        ep = analysis.get('exit_plan', {'partial_ratio': 0.9})
        st_state = trade_data.get('stop_state')
        if st_state == 'verified':
            stop_txt = '✅ مثبّت ومؤكد على المنصة'
        elif st_state == 'placed':
            stop_txt = '🟡 مثبّت — بانتظار التأكيد'
        elif st_state == 'failed':
            stop_txt = '❌ فشل — إعادة محاولة تلقائية (' + str(trade_data.get('stop_error', ''))[:80] + ')'
        else:
            stop_txt = '⏳ جارٍ التثبيت...'
        msg = (f"✅ *صفقة منفذة!* (تقييم {analysis['score']}/10)\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
               f"🏃 خطة الخروج: جني {int(ep['partial_ratio']*100)}% عند TP1 والباقي يركض\n"
               f"🪙 `{symbol}` | رافعة {self.LEVERAGE}x | هامش {self.TRADE_SIZE_USDT:.0f}$\n"
               f"💵 الدخول: {self.fmt_price(entry_price)}\n"
               f"🛑 SL: {self.fmt_price(analysis['sl'])}\n"
               f"🎯 TP1: {self.fmt_price(analysis['tp1'])} | TP2: {self.fmt_price(analysis['tp2'])}\n"
               f"🛡️ ستوب المنصة: {stop_txt}\n"
               f"🧠 {self.tuner.describe()}")
        await self.tg(msg)

    # ═══ أوامر المنصة الشرطية — ✅ V9.1: سلّم محاولات + تشخيص كامل + تحقق ═══
    async def _place_conditional_order(self, params, detailed=False):
        """
        تثبيت STOP_MARKET / TAKE_PROFIT_MARKET عبر /fapi/v1/order الرسمي.
        ✅ V9.1: مع detailed=True يعيد (حالة، حمولة) — وحمولة الفشل تحمل
        كود رفض Binance الحقيقي (-2021/-2022/-4061...) — نهاية الفشل الصامت.
        """
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
        """إلغاء أمر شرطي عادي (stop/tp) — يتسق مع openOrders والمصالحة الذاتية"""
        await self._fapi_request('DELETE', '/fapi/v1/order',
            {'symbol': symbol, 'orderId': order_id}, signed=True, quiet=('-2011', '-2013'))

    def _stop_success(self, trade, oid, price, method):
        """توحيد حالة النجاح بعد وضع الستوب"""
        trade['stop_order_id'] = None if oid == 'UNKNOWN' else oid
        trade['stop_synced_price'] = price
        trade['stop_state'] = 'placed'
        trade['stop_error'] = None
        trade['stop_method'] = method

    # ═══ ✅ V9.1: محرك ستوب المنصة — سلّم محاولات ذكي مع تشخيص كامل ═══
    async def _place_stop_order(self, trade, desired=None):
        """
        يحاول تثبيت الستوب بثلاث استراتيجيات بالترتيب عبر المسار الحديث المتوافق مع Binance:
          1) STOP_MARKET + closePosition=true
          2) STOP_MARKET + reduceOnly + الكمية المتبقية
          3) عند -2021 "سيُفعَّل فوراً": إبعاد سعر الستوب بهامش أمان وإعادة المحاولة
        يحدّث: stop_order_id / stop_synced_price / stop_state / stop_error
        """
        symbol = trade['symbol']
        is_buy = trade['side'] == 'BUY'
        stop_side = 'SELL' if is_buy else 'BUY'
        desired = trade['sl'] if desired is None else desired
        if not desired or desired <= 0:
            return False

        prices = self.get_price(symbol)
        cur = (prices['bid'] if is_buy else prices['ask']) if prices else None
        if cur:
            if (is_buy and desired >= cur) or (not is_buy and desired <= cur):
                return False   # سيُرفض فوراً (would immediately trigger)

        desired_str = self.price_to_str(symbol, desired)
        
        # ✅ تحديث هيكل البيانات ليتوافق مع نظام الأوامر الحديث في بينانس
        base = {
            'symbol': symbol, 
            'side': stop_side, 
            'type': 'STOP_MARKET',
            'stopPrice': desired_str,
            'workingType': 'CONTRACT_PRICE'
        }
        
        attempts = [
            ('closePosition', dict(base, closePosition='true')),
            ('reduceOnly', dict(base, 
                                quantity=self.qty_to_str(symbol, trade.get('quantity', 0)),
                                reduceOnly='true')),
        ]

        errs = []
        for label, params in attempts:
            status, res = await self._place_conditional_order(params, detailed=True)
            if status == 'OK':
                self._stop_success(trade, res, desired, f'STOP_MARKET({label})')
                self._reset_error(f"ستوب المنصة {symbol}")
                return True
            code, msg = res.get('_code'), (res.get('_msg') or '')
            errs.append(f"{label}: {code} {msg[:90]}".strip())

            # ✅ معالجة -2021: الستوب لامس السعر الحالي → نُبعد بهامش أمان ونعيد
            if code == -2021 and cur:
                tick = self.tick_sizes_cache.get(symbol) or (cur * 0.0001)
                buffer = max(3 * tick, cur * 0.0015)
                nudged = cur - buffer if is_buy else cur + buffer
                n_str = self.price_to_str(symbol, nudged)
                
                nudged_params = dict(base)
                nudged_params['stopPrice'] = n_str
                nudged_params['closePosition'] = 'true'
                if 'quantity' in nudged_params:
                    nudged_params.pop('quantity', None)
                if 'reduceOnly' in nudged_params:
                    nudged_params.pop('reduceOnly', None)

                status2, res2 = await self._place_conditional_order(nudged_params, detailed=True)
                if status2 == 'OK':
                    self._stop_success(trade, res2, nudged, 'STOP_MARKET(nudged-2021)')
                    trade['sl'] = nudged   # ✅ توحيد الوقف المحلي مع المنصة
                    self._reset_error(f"ستوب المنصة {symbol}")
                    await self.tg(f"🛡️ ستوب `{symbol}` وُضع مُبعداً قليلاً ({n_str}) "
                                  f"تفادياً للرفض الفوري — الأصلي {desired_str}")
                    return True
                code2, msg2 = res2.get('_code'), (res2.get('_msg') or '')
                errs.append(f"nudged: {code2} {msg2[:90]}".strip())
                break   # -2021 حتى بعد الإبعاد → المشكلة ليست في السعر

            if code == -4061:
                self._notify_error(f"Hedge Mode يرفض ستوب {symbol}",
                                   context="البوت يتطلب One-way — غيّر وضع المركز في إعدادات Binance")

        trade['stop_state'] = 'failed'
        trade['stop_error'] = ' | '.join(errs)[:240]
        trade['stop_synced_price'] = None
        self._notify_error(f"تعذّر وضع ستوب المنصة لـ {symbol}",
                           context=trade['stop_error'][:200])
        return False

    # ═══ ✅ V9.1: تحقق حقيقي من المنصة أن الستوب حي فعلاً ═══
    async def _verify_stop_on_platform(self, trade):
        """
        يفتح openOrders للرمز ويبحث عن أمر الستوب فعلياً —
        حالة "مؤكد ✓" لا تُمنح إلا برؤية الأمر حياً على المنصة.
        """
        symbol = trade['symbol']
        orders = await self._fapi_request('GET', '/fapi/v1/openOrders',
            {'symbol': symbol}, signed=True)
        if not isinstance(orders, list):
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
        if trade.get('stop_state') == 'verified':
            trade['stop_state'] = 'placed'   # اختفى من المنصة (فُعّل/أُلغي) — سيتعاد
        return False

    async def verify_platform_stops(self):
        """✅ V9.1: فحص دوري أن ستوبات المراكز المفتوحة ما زالت حية على المنصة"""
        if not self.binance_api_key or not self.active_trades:
            return
        for symbol, trade in list(self.active_trades.items()):
            if trade.get('stop_state') == 'failed':
                continue   # _sync_stop_order في دورة المراقبة يعيد المحاولة
            try:
                await self._verify_stop_on_platform(trade)
            except Exception as e:
                logger.warning(f"تعذر التحقق من ستوب {symbol}: {e}")

    # ═══ مزامنة الستوب ═══
    async def _sync_stop_order(self, trade, current_price, force=False):
        symbol = trade['symbol']
        is_buy = trade['side'] == 'BUY'
        desired = trade['sl']
        if desired is None: return False

        if current_price and ((is_buy and desired >= current_price) or (not is_buy and desired <= current_price)):
            return False

        desired_str = self.price_to_str(symbol, desired)
        if (not force and trade.get('stop_state') == 'verified'
                and trade.get('stop_synced_price') is not None
                and self.price_to_str(symbol, trade['stop_synced_price']) == desired_str):
            return False

        old_id = trade.get('stop_order_id')
        placed = await self._place_stop_order(trade, desired)
        if placed:
            if old_id:
                await self._cancel_conditional_order(symbol, old_id)
            await self._verify_stop_on_platform(trade)
            logger.info(f"🛡️ ستوب المنصة {symbol} مثبت عند {desired_str} — "
                        f"الحالة: {trade.get('stop_state')} ({trade.get('stop_method', '')})")
            return True
        return False

    # ═══ جني TP2 على المنصة — ✅ V9.1 مع سلّم بديل وتشخيص ═══
    async def _place_tp_order(self, trade, current_price):
        symbol = trade['symbol']
        is_buy = trade['side'] == 'BUY'
        if trade.get('tp_order_id') or trade.get('tp_skipped') or trade.get('tp_unconfirmed'):
            return
        tp2 = trade.get('tp2')
        if not tp2: return
        if (is_buy and tp2 <= current_price) or (not is_buy and tp2 >= current_price):
            trade['tp_skipped'] = True
            return
        close_side = 'SELL' if is_buy else 'BUY'
        tp_str = self.price_to_str(symbol, tp2)
        base = {'symbol': symbol, 'side': close_side, 'type': 'TAKE_PROFIT_MARKET',
                'stopPrice': tp_str, 'workingType': 'CONTRACT_PRICE'}
        attempts = [
            ('reduceOnly', dict(base, quantity=self.qty_to_str(symbol, trade['quantity']),
                                reduceOnly='true')),
            ('closePosition', dict(base, closePosition='true')),
        ]
        errs = []
        for label, params in attempts:
            status, res = await self._place_conditional_order(params, detailed=True)
            if status == 'OK':
                if res == 'UNKNOWN':
                    trade['tp_order_id'] = None
                    trade['tp_unconfirmed'] = True
                else:
                    trade['tp_order_id'] = res
                self._reset_error(f"TP2 {symbol}")
                await self.tg(f"🎯 *هدف TP2 مثبّت على المنصة* (`{symbol}`) عند {self.fmt_price(tp2)}")
                return
            errs.append(f"{label}: {res.get('_code')} {(res.get('_msg') or '')[:90]}".strip())
        trade['tp_skipped'] = True
        trade['tp_error'] = ' | '.join(errs)[:200]
        self._notify_error(f"تعذر تثبيت TP2 لـ {symbol}",
                           context=(trade['tp_error'][:160] + ' — الوقف المتحرك يدير الخروج'))

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
        if not self.active_trades: return
        for symbol, trade in list(self.active_trades.items()):
            try:
                amt = await self.get_position_amt(symbol)
                if amt is None: continue
                step = self.step_sizes_cache.get(symbol) or 1.0
                if abs(amt) < step:
                    pnl = await self.get_last_realized_pnl(symbol, trade)
                    prices = self.get_price(symbol)
                    px = (prices['bid'] if trade['side'] == 'BUY' else prices['ask']) if prices else trade['entry_price']
                    await self._finalize_trade(trade, px, "🛑 أُغلق على المنصة (Stop-Loss)", pnl)
            except Exception as e:
                self._notify_error(f"فشل التحقق من مركز {symbol}", exc=e)

    # ═══ إغلاق آمن بالكمية الفعلية ═══
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

    # ═══ إنهاء الصفقة (محاسبة كاملة) ═══
    async def _finalize_trade(self, trade, fill_price, reason, pnl_override=None):
        symbol = trade['symbol']
        is_buy = trade['side'] == 'BUY'

        # ✅ V9.0: كل الأوامر عادية عبر /fapi/v1/order — إلغاء موحّد
        for oid_key in ('stop_order_id', 'tp_order_id'):
            oid = trade.get(oid_key)
            if oid:
                await self._cancel_conditional_order(symbol, oid)

        if pnl_override is not None:
            final_pnl = pnl_override
        else:
            if is_buy: final_pnl = (fill_price - trade['entry_price']) * trade['quantity']
            else: final_pnl = (trade['entry_price'] - fill_price) * trade['quantity']

        total_pnl = trade.get('realized_pnl', 0.0) + final_pnl
        margin_used = self.TRADE_SIZE_USDT
        margin_pnl_pct = (total_pnl / margin_used * 100) if margin_used > 0 else 0

        # ✅ V9.0: تسجيل النتيجة في مدير المخاطر (يوقف التداول تلقائياً عند الحدود)
        self.risk.register_result(total_pnl)

        is_win = total_pnl > 0
        if is_win: self.stats['wins'] += 1
        else: self.stats['losses'] += 1

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
        msg = (f"🏁 {icon} *إغلاق `{symbol}`*\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
               f"{reason}\n"
               f"💵 النتيجة: `{total_pnl:.4f} USDT` ({margin_pnl_pct:.1f}% من الهامش)\n"
               f"🏆 الإجمالي: {self.stats['wins']}W / {self.stats['losses']}L{partial_note}{score_note}\n"
               f"🧠 {self.tuner.describe()}")
        await self.tg(msg)

    # ═══ مراقبة الصفقات (خروج ديناميكي + TP2 على المنصة) ═══
    async def monitor_trades(self):
        if not self.active_trades: return
        stale_symbols = []

        for symbol, trade in list(self.active_trades.items()):
            prices = self.get_price(symbol)
            if not prices:
                stale_symbols.append(symbol)
                continue

            is_buy = trade['side'] == 'BUY'
            current_price = prices['bid'] if is_buy else prices['ask']
            changed = False

            if is_buy and current_price > trade.get('highest_price', 0):
                trade['highest_price'] = current_price; changed = True
            elif not is_buy and current_price < trade.get('lowest_price', 999999):
                trade['lowest_price'] = current_price; changed = True

            # 1) وقف الخسارة
            if (is_buy and current_price <= trade['sl']) or (not is_buy and current_price >= trade['sl']):
                closed, fill_price, pnl_override = await self._close_position(trade, current_price)
                if closed:
                    await self._finalize_trade(trade, fill_price, "🛑 ضرب SL", pnl_override)
                continue

            # 2) الجني الجزئي عند TP1 — ✅ V8.2: نسبة ديناميكية حسب تقييم الصفقة
            if not trade.get('partial_closed', False) and trade.get('tp'):
                if (is_buy and current_price >= trade['tp']) or (not is_buy and current_price <= trade['tp']):
                    ratio = trade.get('partial_ratio', 0.9)   # ✅ V8.2: 50%/70%/90%
                    partial_qty = self.format_quantity(symbol, trade['quantity'] * ratio)
                    remaining_qty = self.format_quantity(symbol, trade['quantity'] - partial_qty)
                    min_notional = self.min_notional_cache.get(symbol, 5.0)

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
                        if is_buy: partial_pnl = (fill_price - trade['entry_price']) * partial_qty
                        else: partial_pnl = (trade['entry_price'] - fill_price) * partial_qty

                        trade['realized_pnl'] = trade.get('realized_pnl', 0.0) + partial_pnl
                        await self.db.update_daily_pnl(partial_pnl, None)
                        trade['quantity'] = remaining_qty
                        trade['partial_closed'] = True
                        trade['sl'] = trade['entry_price'] * 1.003 if is_buy else trade['entry_price'] * 0.997
                        changed = True
                        await self.tg(f"🎯 *جني أرباح أول (`{symbol}`)*\n"
                                      f"💸 أُغلق {int(ratio*100)}% بربح: `{partial_pnl:.4f} USDT`\n"
                                      f"🛡️ الوقف على التعادل (+0.3%)")
                        await self._place_tp_order(trade, current_price)
                    else:
                        amt = await self.get_position_amt(symbol)
                        if amt is not None and abs(amt) < (self.step_sizes_cache.get(symbol) or 1.0):
                            pnl = await self.get_last_realized_pnl(symbol, trade)
                            await self._finalize_trade(trade, current_price, "🛑 أُغلق على المنصة (Stop)", pnl)
                            continue
                        self._notify_error(f"فشل الجني الجزئي لـ {symbol}",
                                           context="إعادة المحاولة في الدورة القادمة")

            # 3) الوقف المتحرك (بعد الجزئي)
            if trade.get('partial_closed'):
                # ✅ V9.0: نسبة الوقف المتحرك من المطوّر (افتراضي 1% — تظهر في اللوحة)
                trail = self.tuner.trailing_pct
                if is_buy:
                    new_sl = trade['highest_price'] * (1 - trail)
                    if new_sl > trade['sl']:
                        trade['sl'] = new_sl; changed = True
                else:
                    new_sl = trade['lowest_price'] * (1 + trail)
                    if new_sl < trade['sl']:
                        trade['sl'] = new_sl; changed = True

            # 4) مزامنة ستوب المنصة
            if await self._sync_stop_order(trade, current_price):
                changed = True

            if changed:
                await self.db.save_trade(trade)

        if stale_symbols:
            self._notify_error("أسعار مجمّدة لمراكز مفتوحة",
                               context=f"{', '.join(stale_symbols)} — ستوب المنصة يحميها")

    # ═══ المسح الديناميكي ═══
    async def scan_volatile_coins(self):
        tickers = await self._fapi_request('GET', '/fapi/v1/ticker/24hr')
        if not tickers:
            self._notify_error("فشل جلب بيانات تقلب السوق", context="مشكلة اتصال مؤقتة")
            return
        self._reset_error("فشل جلب بيانات تقلب السوق")

        targets = []
        for t in tickers:
            symbol = t.get('symbol', '')
            try:
                change = abs(float(t.get('priceChangePercent', 0)))
            except (TypeError, ValueError):
                continue
            if change > 5 and symbol in self.step_sizes_cache:
                targets.append({'symbol': symbol, 'change': change})
        targets.sort(key=lambda x: x['change'], reverse=True)

        scan_targets = targets[:20]
        results = []
        for target in scan_targets:
            symbol = target['symbol']
            if symbol in self.active_trades: continue
            if self.is_in_cooldown(symbol): continue
            analysis = await self.analyze_whale_zone(symbol)
            if analysis:
                results.append(analysis)
            await asyncio.sleep(0.5)

        self.last_scan_info = {
            'ts': time.time(),
            'volatile': len(targets),
            'scanned': len(scan_targets),
            'signals': len(results)
        }

        fresh_lines = []
        now = time.time()
        for a in results:
            key = (a['symbol'], a['direction'])
            if now - self.last_discovery_alert.get(key, 0) < 1800:
                continue
            self.last_discovery_alert[key] = now
            fresh_lines.append(f"🐋 `{a['symbol']}` *{a['direction']}* @ {self.fmt_price(a['price'])}"
                               f" (تقييم {a['score']}/10)")

        if fresh_lines:
            self.stats['signals_found'] += len(fresh_lines)
            await self.tg("🚀 *إشارات جديدة!*\n━━━━━━━━━━━━━━━━━━━━━━━━\n" + "\n".join(fresh_lines))

        # ✅ V9.0: عدادات إحصائيات اللوحة (إجمالي/مرفوض أخبار/مرفوض مخاطر)
        self.stats['total_signals'] += len(results)
        news_blocked, _news_reason = self.news_filter.is_blocked_now()   # ✅ V9.1
        blocked_news = bool(news_blocked)
        blocked_risk = not self.risk.can_trade()[0]
        for a in results:
            if blocked_news:
                self.stats['rejected_by_news'] += 1
            elif blocked_risk:
                self.stats['rejected_by_risk'] += 1
            else:
                await self.execute_trade(a)
            await asyncio.sleep(1)

    # ═══ المطوّر التكيفي ═══
    def _trades_today(self):
        today = time.strftime("%Y-%m-%d")
        return sum(1 for _, d in self.entry_history if d == today)

    def _frequency_guard(self):
        now = time.time()
        if now - self._last_freq_check < 3600:
            return
        self._last_freq_check = now

        last_ts = self.entry_history[-1][0] if self.entry_history else 0
        hours_since = (now - last_ts) / 3600 if last_ts else 999
        if hours_since >= 10 and self._trades_today() < 3:
            if self.tuner.relax_step():
                logger.info("🧠 ارتخاء تكيفي بسبب قلة النشاط")
                asyncio.get_running_loop().create_task(self.tuner.save())
                asyncio.get_running_loop().create_task(self.tg(
                    f"🧠 *المطوّر التكيفي:* رفع النشاط تلقائياً (توسيع نطاق القرب)\n{self.tuner.describe()}"))

        wr = self.tuner.recent_winrate(10)
        if wr is not None and wr < 0.38 and now - self._last_tighten > 6 * 3600:
            self._last_tighten = now
            if self.tuner.tighten_step():
                logger.info("🧠 تشديد تكيفي بسبب تدهور نسبة الفوز")
                asyncio.get_running_loop().create_task(self.tuner.save())
                asyncio.get_running_loop().create_task(self.tg(
                    f"🧠 *المطوّر التكيفي:* تشديد الجودة (فوز آخر 10 = {wr*100:.0f}%)\n{self.tuner.describe()}"))

    # ═══ الصيانة الذاتية ═══
    def _cleanup_memory(self):
        now = time.time()
        self.reentry_cooldown = {k: v for k, v in self.reentry_cooldown.items() if v > now}
        self.last_discovery_alert = {k: v for k, v in self.last_discovery_alert.items()
                                     if v > now - 7200}
        if len(self.error_counts) > 500:
            self.error_counts.clear()

    async def _send_daily_report(self, day):
        row = await self.db.get_day_stats(day)
        if not row: return
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
            await self.tg(f"💓 *النبض:* حي ✓ | مسح #{loop_count} | "
                          f"صفقات اليوم: {self._trades_today()} | فوز آخر 10: {wr_txt}\n"
                          f"🧠 {self.tuner.describe()}")

    # ═══ ✅ V9.1: صيانة تقويم الأخبار ═══
    async def _news_boot(self):
        """جلب أول للتقويم وإشعار بالحدث القادم"""
        try:
            await self.news_filter.refresh_calendar()
            ev = self.news_filter.next_event()
            if self.news_filter.enabled and ev:
                await self.tg(f"📰 *فلتر الأخبار نشط* — الحدث القادم: {ev['title']} "
                              f"({ev['cur']}) بعد {max(0, int((ev['ts'] - time.time()) / 60))} دقيقة")
        except Exception:
            pass

    async def _maybe_refresh_news(self):
        """تحديث تقويم الأخبار كل 4 ساعات"""
        if time.time() - self.news_filter.calendar_updated > self.news_filter.CALENDAR_TTL:
            try:
                await self.news_filter.refresh_calendar()
            except Exception:
                pass

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
                    sl, tp1, tp2 = entry - 2*atr, entry + 1.5*atr, entry + 4*atr
                else:
                    sl, tp1, tp2 = entry + 2*atr, entry - 1.5*atr, entry - 4*atr
                trade = {
                    'symbol': symbol, 'side': side, 'entry_price': entry,
                    'quantity': abs(pos['amt']), 'sl': sl, 'tp': tp1, 'tp2': tp2,
                    'trailing_active': False, 'highest_price': entry, 'lowest_price': entry,
                    'entry_time': time.time(), 'partial_closed': False,
                    'realized_pnl': 0.0, 'stop_order_id': None, 'tp_order_id': None,
                    'stop_state': 'none', 'stop_error': None,
                    'stop_synced_price': None, 'tp_skipped': False
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
            # ✅ V9.1: تبنّي أوامر الحماية الحية لصفقاتنا بدل إلغائها —
            # كان الإلغاء الأعمى يقتل الستوبات التي فُقدت معرفاتها (UNKNOWN)
            adopted = cancelled = 0
            for o in orders:
                otype = o.get('type')
                if otype not in ('STOP_MARKET', 'STOP', 'TAKE_PROFIT_MARKET'):
                    continue
                trade = self.active_trades.get(o.get('symbol'))
                if trade is not None:
                    try:
                        sp = float(o.get('stopPrice', 0) or 0)
                    except (TypeError, ValueError):
                        sp = 0.0
                    if otype in ('STOP_MARKET', 'STOP') and not trade.get('stop_order_id'):
                        trade['stop_order_id'] = o.get('orderId')
                        if sp > 0:
                            trade['stop_synced_price'] = sp
                        trade['stop_state'] = 'placed'
                        adopted += 1
                    elif otype == 'TAKE_PROFIT_MARKET' and not trade.get('tp_order_id'):
                        trade['tp_order_id'] = o.get('orderId')
                        adopted += 1
                    continue
                cancelled += 1
                await self._fapi_request('DELETE', '/fapi/v1/order',
                    {'symbol': o['symbol'], 'orderId': o.get('orderId')}, signed=True,
                    quiet=('-2011', '-2013'))
            if adopted:
                await self.tg(f"🛡️ *مصالحة:* تم تبنّي {adopted} أمر حماية حي على المنصة")
            if cancelled:
                await self.tg(f"🧹 *تنظيف ذاتي:* أُلغي {cancelled} أمر يتيم على المنصة")
            logger.info(f"🧾 المصالحة الذاتية: {len(open_pos)} مركز حي، {adopted} أمر مُتبنى، {cancelled} أمر يتيم ملغى")
        except Exception as e:
            self._notify_error("فشل المصالحة الذاتية", exc=e, context="غير قاتل — تُعاد كل دورات")

    # ═══ إيقاف آمن ═══
    async def request_shutdown(self):
        if self._shutdown_requested: return
        self._shutdown_requested = True
        logger.info("🛑 طلب إيقاف آمن...")
        try:
            await self.tg("🛑 *إيقاف آمن:* ستوب/أوامر TP على المنصة تبقى فعالة وتحمي المراكز.")
        except Exception:
            pass

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
            await self.news_filter.load()   # ✅ V9.1: فلتر الأخبار من القاعدة
            asyncio.create_task(self._news_boot())   # ✅ جلب أول للتقويم (غير معيق)

            market_tries = 0
            while not self.all_futures_pairs:
                market_tries += 1
                await self.load_market_data()
                if self.all_futures_pairs: break
                if market_tries == 1 or market_tries % 5 == 0:
                    await self.tg(f"❌ *فشل تحميل بيانات السوق* (محاولة {market_tries})\n"
                                  f"⏳ إعادة خلال 30 ثانية...")
                logger.error(f"فشل تحميل بيانات السوق (محاولة {market_tries})")
                await asyncio.sleep(30)

            self.active_trades = await self.db.load_active_trades()
            await self.sync_server_time()

            # ✅ V9.0: الرصيد الابتدائي لمدير المخاطر (أساس حساب السحب اليومي 5%)
            try:
                self.risk.initial_balance = await self.get_available_usdt()
                if self.risk.initial_balance > 0:
                    logger.info(f"🛡️ مدير المخاطر: رصيد ابتدائي {self.risk.initial_balance:.2f}$")
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

            if self.TRADE_ENABLED and self.binance_api_key:
                await self.setup_futures_account()

            self.ws_task = asyncio.create_task(self.ws_manager())
            await asyncio.sleep(10)

            if self.TRADE_ENABLED and self.binance_api_key:
                await self.reconcile()
                await self.verify_positions()

            mode_trade = "⚔️ تداول تلقائي" + (" (TESTNET 🧪)" if self.TESTNET else "") \
                         if self.TRADE_ENABLED else "👁️ مراقبة فقط"
            msg = ("🔥 *القناص الأسطوري V9.1 — حارس الستوب وأخبار السوق!*\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
                   f"📡 الوضع: {mode_trade} | رافعة {self.LEVERAGE}x | هامش {self.TRADE_SIZE_USDT:.0f}$\n"
                   f"🧠 العتبة: {self.tuner.min_score}/10 ثابتة\n"
                   f"🌀 VuManChu Swing: {'مفعّل (+2 تقييم)' if self.tuner.vmc_enabled else 'معطل'}\n"
                   f"📰 فلتر الأخبار: {('مفعّل — تأثير ' + self.news_filter.impact_min + ' ±' + str(self.news_filter.before_min) + 'د') if self.news_filter.enabled else 'معطل (يُدار من اللوحة)'}\n"
                   f"📉 ستوكاستك: {self.tuner.STOCH_MODES.get(self.tuner.stoch_strictness, 'مرن')} — لا يعطّل الإشارات\n"
                   f"🏃 خروج ديناميكي: 8-10→جني50% | 6-7→جني70% | أقل→جني90%\n"
                   f"🎯 TP2 ديناميكي: 8-10→5×ATR | 6-7→4.5×ATR | أقل→4×ATR\n"
                   f"🛡️ مدير المخاطر: 3 متتالية→توقف4س | يومي 3→اليوم | سحب 5%→اليوم\n"
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
                    await self.scan_volatile_coins()

                    loop_count += 1
                    self.stats['total_scans'] = loop_count
                    if loop_count % self.VERIFY_EVERY_N_LOOPS == 0:
                        await self.verify_positions()
                        await self.verify_platform_stops()   # ✅ V9.1: ستوبات حية؟
                    await self._maybe_refresh_news()   # ✅ V9.1: تقويم حي

                    self._frequency_guard()
                    self._cleanup_memory()
                    await self._heartbeat_and_report(loop_count)
                    await asyncio.sleep(60)
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
    bot = LegendarySniperFuturesV8()
    bot.start()






