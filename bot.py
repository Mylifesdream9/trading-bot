"""
═══════════════════════════════════════════════════════════════════════
  🔥 القناص الأسطوري V9.0 — Legendary Sniper (Ultimate Precision & Self-Healing) 🔥
═══════════════════════════════════════════════════════════════════════
  ✅ V9.0 (النسخة الخارقة المحصنة):
     - تصفية جذرية لإشارات 6/8: تُرفض تلقائياً إن لم تكن مصحوبة بحجم تداول أو تصفية سيولة حقيقية.
     - مناطق طلب/عرض ديناميكية (Dynamic OB) مبنية على الـ ATR لكل عملة.
     - حماية كاملة لحدود الحد الأدنى للأعمدة (Min Notional) في الجني الجزئي والإغلاق.
     - استوكاستك وزخم لحظي مؤكد على الشمعة المغلقة حصراً.
     - مطور تكيفي ذكي يمنع الارتخاء العشوائي ويركز على دقة الدخول.
═══════════════════════════════════════════════════════════════════════
"""

import asyncio, aiohttp, json, math, os, sys, time, logging, requests
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
import websockets
import aiosqlite
from web_panel import start_web_panel, notify as panel_notify

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logger = logging.getLogger('SniperV9')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh = RotatingFileHandler('bot_v9.log', maxBytes=2*1024*1024, backupCount=2, encoding='utf-8')
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
    def __init__(self, db_name='sniper_v9.db'):
        self.db_name = db_name

    async def init_db(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS active_trades (
                symbol TEXT PRIMARY KEY, side TEXT, entry_price REAL, quantity REAL,
                sl REAL, tp REAL, tp2 REAL, trailing_active INTEGER, highest_price REAL,
                lowest_price REAL, entry_time REAL, partial_closed INTEGER,
                realized_pnl REAL DEFAULT 0, stop_order_id INTEGER, tp_order_id INTEGER)""")
            for col_def in ('realized_pnl REAL DEFAULT 0', 'stop_order_id INTEGER',
                            'tp2 REAL', 'tp_order_id INTEGER'):
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
                 realized_pnl, stop_order_id, tp_order_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (t['symbol'], t['side'], t['entry_price'], t['quantity'],
                 t['sl'], t['tp'], t.get('tp2'), int(t.get('trailing_active', False)),
                 t.get('highest_price', 0), t.get('lowest_price', 999999),
                 t['entry_time'], int(t.get('partial_closed', 0)),
                 float(t.get('realized_pnl', 0.0)), t.get('stop_order_id'), t.get('tp_order_id')))
            await db.commit()

    async def load_active_trades(self):
        trades = {}
        try:
            async with aiosqlite.connect(self.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""SELECT symbol, side, entry_price, quantity, sl, tp, tp2,
                    trailing_active, highest_price, lowest_price, entry_time, partial_closed,
                    realized_pnl, stop_order_id, tp_order_id FROM active_trades""") as cur:
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


# ═══════════════════════ المطوّر التكيفي المحصن (Adaptive Tuner V9) ═════════════════════
class AdaptiveTuner:
    def __init__(self, db):
        self.db = db
        self.min_score = 6          # الحد الأدنى الثابت
        self.proximity_pct = 0.025  # نطاق قرب آمن ومحكم
        self.strict_stoch = True
        self.results = collections.deque(maxlen=20)

    def _clamp(self):
        self.min_score = 6
        self.proximity_pct = max(0.015, min(0.035, float(self.proximity_pct)))

    async def load(self):
        raw = await self.db.get_param('tuner')
        if raw:
            try:
                d = json.loads(raw)
                self.min_score = max(6, int(d.get('min_score', 6)))
                self.proximity_pct = float(d.get('proximity_pct', 0.025))
                self.strict_stoch = bool(d.get('strict_stoch', True))
                self.results = collections.deque(d.get('results', [])[-20:], maxlen=20)
                self._clamp()
                logger.info(f"🧠 المطوّر التكيفي V9 محمّل: {self.describe()}")
            except Exception as e:
                logger.warning(f"تعذر تحميل المطوّر التكيفي: {e}")

    async def save(self):
        try:
            await self.db.set_param('tuner', json.dumps({
                'min_score': self.min_score, 'proximity_pct': self.proximity_pct,
                'strict_stoch': self.strict_stoch, 'results': list(self.results)}))
        except Exception as e:
            logger.warning(f"تعذر حفظ المطوّر التكيفي: {e}")

    def record(self, win):
        self.results.append(bool(win))

    def recent_winrate(self, n=10):
        recent = list(self.results)[-n:]
        if len(recent) < 5:
            return None
        return sum(recent) / len(recent)

    def tighten_step(self):
        before = (self.strict_stoch, round(self.proximity_pct, 4))
        if self.proximity_pct > 0.015:
            self.proximity_pct = round(max(0.015, self.proximity_pct - 0.005), 4)
        self.strict_stoch = True
        return before != (self.strict_stoch, round(self.proximity_pct, 4))

    def describe(self):
        return (f"min_score={self.min_score} | قرب OB≤{self.proximity_pct*100:.1f}% | "
                f"ستوك صارم={'نعم' if self.strict_stoch else 'لا'}")


# ═══════════════════════ محرك SMC المحصن V9 ═════════════════════
class WhaleSMCEngine:
    @staticmethod
    def detect_order_blocks(df, trend, atr):
        """مناطق طلب وعرض ديناميكية مبنية على الـ ATR لضمان الدقة لكل عملة"""
        obs = []
        if atr <= 0: return obs
        threshold = max(0.008, min(0.025, (atr / df['close'].iloc[-1]) * 1.2))

        for i in range(2, len(df)-1):
            if df['close'].iloc[i] > df['open'].iloc[i]:
                impulse_pct = (df['close'].iloc[i] - df['low'].iloc[i-1]) / df['low'].iloc[i-1]
                if df['close'].iloc[i-1] < df['open'].iloc[i-1] and impulse_pct >= threshold:
                    obs.append({'type': 'demand', 'top': df['open'].iloc[i-1],
                                'bottom': df['low'].iloc[i-1], 'index': i-1})
            elif df['close'].iloc[i] < df['open'].iloc[i]:
                impulse_pct = (df['high'].iloc[i-1] - df['close'].iloc[i]) / df['high'].iloc[i-1]
                if df['close'].iloc[i-1] > df['open'].iloc[i-1] and impulse_pct >= threshold:
                    obs.append({'type': 'supply', 'top': df['high'].iloc[i-1],
                                'bottom': df['close'].iloc[i-1], 'index': i-1})
        return obs

    @staticmethod
    def detect_liquidity_sweep(df_15m, ob_zone, direction):
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


# ══════════════════════════════════════════════════════════════════════
#       🔥 القناص الأسطوري V9.0 — محرك التداول الأساسي 🔥
# ══════════════════════════════════════════════════════════════════════
class LegendarySniperFuturesV9:
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
        self._balance_cache = (0.0, 0.0)

        self.stats = {'total_scans': 0, 'trades_executed': 0, 'wins': 0, 'losses': 0}

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
                loop.create_task(self.tg(f"{txt}\n🔢 التكرار: {count}"))
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

    async def _fapi_request(self, method, endpoint, params=None, signed=False, retries=3, quiet=(), soft=()):
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
                        self._notify_error("خطأ 401 من Binance", context="مفاتيح خاطئة أو مقيدة بـIP")
                        return None
                    if '-1021' in body:
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
                    return None
            except asyncio.TimeoutError:
                if attempt == retries - 1:
                    return None
                await asyncio.sleep(2 ** attempt)
            except Exception:
                if attempt == retries - 1:
                    return None
                await asyncio.sleep(2 ** attempt)
        return None

    async def setup_futures_account(self):
        for pair in self.all_futures_pairs[:50]:
            symbol = pair['symbol']
            try:
                await self._fapi_request('POST', '/fapi/v1/leverage',
                    {'symbol': symbol, 'leverage': self.LEVERAGE}, signed=True)
                await self._fapi_request('POST', '/fapi/v1/marginType',
                    {'symbol': symbol, 'marginType': 'ISOLATED'}, signed=True, quiet=(-4046,))
            except Exception:
                pass
            await asyncio.sleep(0.15)

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
                        self.max_qty_cache[s['symbol']] = float(f['maxQty', 1e12])
                    elif f['filterType'] == 'PRICE_FILTER':
                        self.tick_sizes_cache[s['symbol']] = float(f['tickSize'])
                    elif f['filterType'] == 'MIN_NOTIONAL':
                        self.min_notional_cache[s['symbol']] = float(f.get('notional', f.get('minNotional', 5.0)))
        self.all_futures_pairs = new_pairs
        logger.info(f"📊 تم تحميل {len(self.all_futures_pairs)} زوج عقود آجلة (V9)")

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

    def qty_to_str(self, symbol, qty):
        step = self.step_sizes_cache.get(symbol) or 1.0
        dec = self._decimals_of(step)
        return f"{self._step_qty(symbol, qty):.{dec}f}"

    def price_to_str(self, symbol, price):
        tick = self.tick_sizes_cache.get(symbol)
        if not tick or tick <= 0:
            return f"{price:.4f}"
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

    async def ws_manager(self):
        ws_url = ("wss://stream.binancefuture.com/ws/!bookTicker" if self.TESTNET
                  else "wss://fstream.binance.com/ws/!bookTicker")
        while True:
            try:
                async with websockets.connect(ws_url, ping_interval=20) as ws:
                    logger.info("✅ Futures WebSocket متصل بنجاح!")
                    async for message in ws:
                        try:
                            data = json.loads(message)
                            if 's' in data and 'b' in data and 'a' in data:
                                self.live_prices[data['s']] = {
                                    'bid': float(data['b']), 'ask': float(data['a']),
                                    'ts': time.time()}
                        except Exception:
                            continue
            except asyncio.CancelledError:
                raise
            except Exception:
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

    @staticmethod
    def _exit_plan(score):
        if score >= 7:
            return {'partial_ratio': 0.5, 'tp2_mult': 5.0}
        elif score >= 6:
            return {'partial_ratio': 0.7, 'tp2_mult': 4.5}
        else:
            return {'partial_ratio': 0.9, 'tp2_mult': 4.0}

    # ═══ تحليل الـ SMC المفلتر والمصحح V9 ═══
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

        atr_1h = self._compute_atr(df_1h)

        # 1) مناطق الحوت الديناميكية
        obs = self.smc.detect_order_blocks(df_1h, trend, atr_1h)
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

        # 2) الزناد الموثوق
        sweep = self.smc.detect_liquidity_sweep(df_15m, nearby_ob, trend)
        retest = False if sweep else self.smc.detect_ob_retest(df_15m, nearby_ob, trend)
        if not (sweep or retest): return None
        trigger_pts = 3 if sweep else 2

        # 3) الاستوكاستك المؤكد
        df_15m = self.smc.calculate_stochastic(df_15m)
        current_k = df_15m['stoch_k'].iloc[-2]
        prev_k = df_15m['stoch_k'].iloc[-3]
        current_d = df_15m['stoch_d'].iloc[-2]

        if trend == 'BUY':
            if not (current_k > current_d and prev_k <= current_d):
                return None
            stoch_pts = 2 if current_k < 25 else (0 if tuner.strict_stoch else 1)
        else:
            if not (current_k < current_d and prev_k >= current_d):
                return None
            stoch_pts = 2 if current_k > 75 else (0 if tuner.strict_stoch else 1)

        # 4) حجم التداول
        vol_pts = 0
        try:
            qv = df_15m['quote_volume']
            base = qv.iloc[-22:-2].mean()
            if base and qv.iloc[-2] > base * 1.3:
                vol_pts = 1
        except Exception:
            pass

        score = proximity_pts + trigger_pts + stoch_pts + vol_pts

        # 🛡️ فلتر V9 الصارم لإشارات 6/8: منع الإشارات الضعيفة
        if score == 6 and not (sweep or vol_pts > 0):
            return None

        if score < tuner.min_score:
            return None

        # 5) الحسابات والأهداف
        atr_15m = self._compute_atr(df_15m)
        if not atr_15m or atr_15m <= 0 or math.isnan(atr_15m):
            return None

        exit_plan = self._exit_plan(score)
        sl_buffer = atr_15m * 1.8
        if trend == 'BUY':
            sl = nearby_ob['bottom'] - sl_buffer
            tp1 = current_price + atr_15m * 1.5
            tp2 = current_price + atr_15m * exit_plan['tp2_mult']
        else:
            sl = nearby_ob['top'] + sl_buffer
            tp1 = current_price - atr_15m * 1.5
            tp2 = current_price - atr_15m * exit_plan['tp2_mult']

        if sl <= 0 or math.isnan(sl): return None
        if trend == 'BUY' and sl >= current_price: return None
        if trend == 'SELL' and sl <= current_price: return None

        risk_pct = abs(current_price - sl) / current_price * 100
        if risk_pct > 2.5 or risk_pct < 0.05:
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
                'volume': vol_pts,
                'score': score
            }
        }

    # ═══ تنفيذ الصفقة ═══
    async def execute_trade(self, analysis):
        if not self.TRADE_ENABLED: return
        if len(self.active_trades) >= self.MAX_OPEN_TRADES: return

        symbol = analysis['symbol']
        if symbol in self.active_trades: return
        if self.is_in_cooldown(symbol): return

        available = await self.get_available_usdt()
        if available < self.TRADE_SIZE_USDT * 1.2:
            return

        notional = self.TRADE_SIZE_USDT * self.LEVERAGE
        quantity = self._step_qty(symbol, notional / analysis['price'])
        if quantity <= 0: return

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
            return

        avg = float(result.get('avgPrice') or 0)
        entry_price = avg if avg > 0 else analysis['price']

        trade_data = {
            'symbol': symbol, 'side': side, 'entry_price': entry_price,
            'quantity': quantity, 'sl': analysis['sl'], 'tp': analysis['tp1'],
            'tp2': analysis['tp2'],
            'score': analysis.get('score'),
            'partial_ratio': analysis.get('exit_plan', {}).get('partial_ratio', 0.9),
            'trailing_active': False, 'highest_price': entry_price,
            'lowest_price': entry_price, 'entry_time': time.time(),
            'partial_closed': False, 'realized_pnl': 0.0,
            'stop_order_id': None, 'tp_order_id': None,
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

        ep = analysis.get('exit_plan', {'partial_ratio': 0.9})
        msg = (f"✅ *صفقة V9 منفذة!* (تقييم {analysis['score']}/8)\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
               f"🏃 الخروج: جني {int(ep['partial_ratio']*100)}% عند TP1 والباقي يركض\n"
               f"🪙 `{symbol}` | رافعة {self.LEVERAGE}x | هامش {self.TRADE_SIZE_USDT:.0f}$\n"
               f"💵 الدخول: {self.fmt_price(entry_price)}\n"
               f"🛑 SL: {self.fmt_price(analysis['sl'])}\n"
               f"🎯 TP1: {self.fmt_price(analysis['tp1'])} | TP2: {self.fmt_price(analysis['tp2'])}")
        await self.tg(msg)

    @staticmethod
    def _find_order_id(data):
        if isinstance(data, dict):
            for k in ('algoId', 'orderId', 'algoID', 'orderID'):
                v = data.get(k)
                if v: return v
            for v in data.values():
                r = LegendarySniperFuturesV9._find_order_id(v)
                if r: return r
        elif isinstance(data, list):
            for v in data:
                r = LegendarySniperFuturesV9._find_order_id(v)
                if r: return r
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
            if oid: return oid
            return 'UNKNOWN'
        return None

    async def _cancel_algo_order(self, symbol, algo_id):
        await self._fapi_request('DELETE', '/fapi/v1/algoOrder',
            {'symbol': symbol, 'algoId': algo_id}, signed=True, quiet=('-2011', '-2013'))

    async def _sync_stop_order(self, trade, current_price):
        symbol = trade['symbol']
        is_buy = trade['side'] == 'BUY'
        desired = trade['sl']
        if desired is None: return False

        if current_price and ((is_buy and desired >= current_price) or (not is_buy and desired <= current_price)):
            return False

        desired_str = self.price_to_str(symbol, desired)
        stop_side = 'SELL' if is_buy else 'BUY'
        new_id = await self._place_algo_order({
            'symbol': symbol, 'side': stop_side, 'type': 'STOP_MARKET',
            'triggerPrice': desired_str, 'closePosition': 'true',
            'workingType': 'CONTRACT_PRICE'})

        if new_id:
            old_id = trade.get('stop_order_id')
            if old_id:
                await self._cancel_algo_order(symbol, old_id)
            trade['stop_order_id'] = None if new_id in ('EXISTS', 'UNKNOWN') else new_id
            return True
        return False

    async def get_position_amt(self, symbol):
        try:
            res = await self._fapi_request('GET', '/fapi/v2/positionRisk',
                {'symbol': symbol}, signed=True)
            if isinstance(res, list) and res:
                return float(res[0].get('positionAmt', 0))
        except Exception:
            pass
        return None

    async def get_last_realized_pnl(self, symbol, trade):
        try:
            res = await self._fapi_request('GET', '/fapi/v1/income',
                {'symbol': symbol, 'incomeType': 'REALIZED_PNL', 'limit': 20}, signed=True)
            if isinstance(res, list) and res:
                entry_ms = int(trade.get('entry_time', 0) * 1000)
                for e in res:
                    if int(e.get('time', 0)) >= entry_ms - 5000:
                        return float(e.get('income', 0))
        except Exception:
            pass
        return None

    async def verify_positions(self):
        if not self.TRADE_ENABLED or not self.active_trades: return
        for symbol, trade in list(self.active_trades.items()):
            amt = await self.get_position_amt(symbol)
            if amt is not None and abs(amt) < (self.step_sizes_cache.get(symbol) or 1.0):
                pnl = await self.get_last_realized_pnl(symbol, trade)
                prices = self.get_price(symbol)
                px = (prices['bid'] if trade['side'] == 'BUY' else prices['ask']) if prices else trade['entry_price']
                await self._finalize_trade(trade, px, "🛑 أُغلق على المنصة", pnl)

    async def _close_position(self, trade, current_price):
        symbol = trade['symbol']
        is_buy = trade['side'] == 'BUY'
        close_side = 'SELL' if is_buy else 'BUY'

        amt = await self.get_position_amt(symbol)
        if amt is None: return False, None, None
        step = self.step_sizes_cache.get(symbol) or 1.0
        if abs(amt) < step:
            pnl = await self.get_last_realized_pnl(symbol, trade)
            return True, current_price, pnl

        qty = self._step_qty(symbol, min(trade['quantity'], abs(amt)))
        res = await self._fapi_request('POST', '/fapi/v1/order', {
            'symbol': symbol, 'side': close_side, 'type': 'MARKET',
            'quantity': self.qty_to_str(symbol, qty), 'reduceOnly': 'true'
        }, signed=True)

        if res and res.get('status') in ['FILLED', 'NEW']:
            fill = float(res.get('avgPrice') or current_price)
            return True, fill, None
        return False, None, None

    async def _finalize_trade(self, trade, fill_price, reason, pnl_override=None):
        symbol = trade['symbol']
        is_buy = trade['side'] == 'BUY'

        if trade.get('stop_order_id'):
            await self._cancel_algo_order(symbol, trade['stop_order_id'])

        final_pnl = pnl_override if pnl_override is not None else (
            (fill_price - trade['entry_price']) * trade['quantity'] if is_buy
            else (trade['entry_price'] - fill_price) * trade['quantity']
        )

        total_pnl = trade.get('realized_pnl', 0.0) + final_pnl
        is_win = total_pnl > 0
        if is_win: self.stats['wins'] += 1
        else: self.stats['losses'] += 1

        self.tuner.record(is_win)
        await self.db.set_signal_result(symbol, trade['entry_time'], is_win, total_pnl)
        await self.db.update_daily_pnl(total_pnl, is_win)
        await self.db.remove_trade(symbol)
        self.active_trades.pop(symbol, None)
        self.set_cooldown(symbol)

        icon = "✅" if is_win else "❌"
        msg = (f"🏁 {icon} *إغلاق صفقة `{symbol}`*\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
               f"{reason}\n"
               f"💵 النتيجة: `{total_pnl:.4f} USDT`\n"
               f"🏆 الأداء: {self.stats['wins']}W / {self.stats['losses']}L")
        await self.tg(msg)

    async def monitor_trades(self):
        if not self.active_trades: return
        for symbol, trade in list(self.active_trades.items()):
            prices = self.get_price(symbol)
            if not prices: continue

            is_buy = trade['side'] == 'BUY'
            current_price = prices['bid'] if is_buy else prices['ask']

            if is_buy and current_price > trade.get('highest_price', 0):
                trade['highest_price'] = current_price
            elif not is_buy and current_price < trade.get('lowest_price', 999999):
                trade['lowest_price'] = current_price

            if (is_buy and current_price <= trade['sl']) or (not is_buy and current_price >= trade['sl']):
                closed, fill_price, pnl_override = await self._close_position(trade, current_price)
                if closed:
                    await self._finalize_trade(trade, fill_price, "🛑 ضرب وقف الخسارة SL", pnl_override)
                continue

            # الجني الجزئي الديناميكي
            if not trade.get('partial_closed', False) and trade.get('tp'):
                if (is_buy and current_price >= trade['tp']) or (not is_buy and current_price <= trade['tp']):
                    ratio = trade.get('partial_ratio', 0.9)
                    partial_qty = self._step_qty(symbol, trade['quantity'] * ratio)
                    remaining_qty = self._step_qty(symbol, trade['quantity'] - partial_qty)
                    min_notional = self.min_notional_cache.get(symbol, 5.0)

                    if partial_qty * current_price < min_notional or remaining_qty * current_price < min_notional:
                        closed, fill_price, pnl_override = await self._close_position(trade, current_price)
                        if closed:
                            await self._finalize_trade(trade, fill_price, "🎯 TP1 (إغلاق كامل لحدود القيمة)", pnl_override)
                        continue

                    close_side = 'SELL' if is_buy else 'BUY'
                    res = await self._fapi_request('POST', '/fapi/v1/order', {
                        'symbol': symbol, 'side': close_side, 'type': 'MARKET',
                        'quantity': self.qty_to_str(symbol, partial_qty), 'reduceOnly': 'true'
                    }, signed=True)

                    if res and res.get('status') in ['FILLED', 'NEW']:
                        fill = float(res.get('avgPrice') or current_price)
                        partial_pnl = (fill - trade['entry_price']) * partial_qty if is_buy else (trade['entry_price'] - fill) * partial_qty
                        trade['realized_pnl'] = trade.get('realized_pnl', 0.0) + partial_pnl
                        await self.db.update_daily_pnl(partial_pnl, None)
                        trade['quantity'] = remaining_qty
                        trade['partial_closed'] = True
                        trade['sl'] = trade['entry_price'] * 1.002 if is_buy else trade['entry_price'] * 0.998
                        await self.tg(f"🎯 *جني جزئي ناجح (`{symbol}`)*\nربح جزء محقق: `{partial_pnl:.4f} USDT`")

            await self._sync_stop_order(trade, current_price)
            await self.db.save_trade(trade)

    async def scan_volatile_coins(self):
        tickers = await self._fapi_request('GET', '/fapi/v1/ticker/24hr')
        if not tickers: return

        targets = []
        for t in tickers:
            symbol = t.get('symbol', '')
            try:
                change = abs(float(t.get('priceChangePercent', 0)))
            except Exception:
                continue
            if change > 4 and symbol in self.step_sizes_cache:
                targets.append({'symbol': symbol, 'change': change})
        targets.sort(key=lambda x: x['change'], reverse=True)

        for target in targets[:20]:
            symbol = target['symbol']
            if symbol in self.active_trades or self.is_in_cooldown(symbol): continue
            analysis = await self.analyze_whale_zone(symbol)
            if analysis:
                await self.execute_trade(analysis)
            await asyncio.sleep(0.3)

    async def main_loop(self):
        self.session = aiohttp.ClientSession()
        try:
            await start_web_panel(self)
            await self.db.init_db()
            await self.tuner.load()

            while not self.all_futures_pairs:
                await self.load_market_data()
                if not self.all_futures_pairs:
                    await asyncio.sleep(15)

            self.active_trades = await self.db.load_active_trades()
            await self.sync_server_time()

            if self.TRADE_ENABLED and self.binance_api_key:
                await self.setup_futures_account()

            self.ws_task = asyncio.create_task(self.ws_manager())
            await asyncio.sleep(5)

            mode_trade = "⚔️ تداول تلقائي V9" + (" (TESTNET)" if self.TESTNET else "") if self.TRADE_ENABLED else "👁️ مراقبة فقط"
            await self.tg(f"🔥 *القناص الأسطوري V9.0 يعمل بنجاح!*\n📡 الوضع: {mode_trade}\n🧠 {self.tuner.describe()}")

            while not self._shutdown_requested:
                try:
                    await self.monitor_trades()
                    await self.scan_volatile_coins()
                    await asyncio.sleep(60)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.error(f"خطأ في اللوب الرئيسي: {e}")
                    await asyncio.sleep(15)
        finally:
            if self.ws_task: self.ws_task.cancel()
            if self.session and not self.session.closed: await self.session.close()

    def start(self):
        asyncio.run(self.main_loop())

if __name__ == "__main__":
    bot = LegendarySniperFuturesV9()
    bot.start()
