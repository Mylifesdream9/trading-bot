"""
═══════════════════════════════════════════════════════════════════════
  📐 الاستراتيجية الثالثة — "موجات 7/25/99" (MA + RSI) — وحدة مستقلة
═══════════════════════════════════════════════════════════════════════
  مبنية حرفياً على وصف المالك: MA 7/25/99 + RSI 7/25/99 (خطوط على الشارت)
  بتأكيد 15 دقيقة والساعة — بنفس واجهة strategy_trend.py لسهولة الدمج في V9.

  ── قواعد الدخول (كما كُتبت من المالك وطُبّقت في الاختبار) ──
    شراء — التأكيد الأول (15د، إلزامي):
      MA7 قطع MA25 أو MA99 صعوداً ضمن آخر 6 شمعات (الملاحظة 1: الأول يكفي،
      والثاني تأكيد أقوى غير إلزامي) + شمعة 15د أغلقت بزخم (جسم ≥ 50% من المدى)
      فوق MA7 وMA25.
    شراء — التأكيد الثاني (ساعة، تعزيز اختياري):
      MA7(ساعة) قطع MA99/MA25 صعوداً ضمن آخر 3 شمعات + إغلاق بزخم فوق MA7 وMA99.
    بيع — التأكيد الأول (ساعة، إلزامي):
      MA7(ساعة) قطع هبوطاً ضمن آخر 3 شمعات + إغلاق الشمعة الساعية بزخم تحت MA7 وMA25.
    بيع — التأكيد الثاني (15د، تعزيز اختياري): بالمقلوب.
    RSI على الشارت (اختياري حسب الملاحظة 2):
      خط RSI(n) = أدنى 99 شمعة + (أعلى 99 − أدنى 99) × RSI(n)/100
      الشراء: إغلاق الشمعة فوق خطي RSI7 وRSI25 — البيع: العكس.

  ── الخروج (الإعدادات المعدّلة المعتمدة بعد التشخيص والتحقق الخارجي) ──
    وقف = 3.0 × ATR(1h) — خارج الضجيج (كان 1.5×ATR يُلمس قبل أن يمشي الاتجاه)
    هدف = 1R = 3.0 × ATR(1h) — قريب (كان 2R لا يصل إليه 63% من الصفقات)
    فلتر التقلب: رفض الإشارة إذا ATR%(1h) > 6 — العملات فائقة التقلب كانت مصدر
       كل التصفيات تقريباً (−726$ من 54 صفقة في فترة التشخيص)
    بلا جني جزئي.

  ── نتيجة التشخيص (مايو-أكتوبر 2026، 1,561 صفقة أساس) ──
    السبب النهائي للخسارة: هدف 2R بعيد + وقف 1.5×ATR داخل الضجيج + عملات فائقة
    التقلب (التصفيات). ليس السوق العرضي (ADX<15 كان رابحاً) وليس تعارض الفريمات.

  ── نتيجة التركيبة المعدّلة (وقف3×ATR + هدف1R + ATR%≤6) ──
    تشخيص (مايو-أكتوبر 2026): فوز 52.9% | صافي +200.6$ | PF 1.07 (أساس: 36.6% / −46$)
    تحقق خارجي (فبراير-أبريل 2026 — خارج العينة تماماً):
      فوز 55.2% مقابل 36.3% للأساس (+19 نقطة) | صافي +324.5$ مقابل −112.6$ | PF 1.25
      متوسط 8 بذور ترتيب عشوائية: فوز 52.4% (أساس 35.2%) | صافي +78$ (أساس +38$، 6/8 موجبة)
      والأفضل من الأساس في 7/8 بذور على فترة التشخيص و5/8 على التحقق — التحسّن النسبي ثابت.
    تحفظ صادق: الربح الدولاري حساس لأي الصفقات تمسك بواري السعة الخمسة؛
      توقع الصفقة الواحدة رفيع (+0.21$/صفقة على التحقق). راقب حياً شهراً قبل التوسعة.
    الإعدادات الجديدة معتمدة في MARS_CONFIG أدناه.
═══════════════════════════════════════════════════════════════════════
"""
import json
import time

import numpy as np
import pandas as pd

MARS_CONFIG = {
    "name": "MARS",
    "label": "موجات 7/25/99",
    "enabled": True,
    # الدخول
    "ma_fast": 7, "ma_mid": 25, "ma_slow": 99,
    "rsi_fast": 7, "rsi_mid": 25, "rsi_slow": 99,
    "cross_window_15m": 6,       # "قطع ضمن آخر N شمعة 15د"
    "cross_window_1h": 3,        # "قطع ضمن آخر N شمعة ساعة"
    "momentum_body": 0.5,        # الزخم: الجسم ≥ 50% من مدى الشمعة
    "require_c2": False,         # التأكيد الثاني — تعزيز فقط (أضعف بالاختبار)
    "require_rsi": False,        # RSI على الشارت — اختياري (ضار بالاختبار)
    "rsi_line_win": 99,          # نافذة رسم خطوط RSI على الشارت
    # الخروج (الإعدادات المعدّلة المعتمدة — تحقق خارجي فبراير-أبريل 2026)
    "sl_atr1h": 3.0,             # الوقف = 3 × ATR(ساعة) — خارج الضجيج
    "tp_r": 1.0,                 # الهدف = 1R = 3 × ATR(ساعة) — قريب
    "max_atr_pct": 6.0,          # رفض الإشارة إذا ATR%(1h) > 6 (مضاد التصفيات)
    "entry_window_min": 10,      # الدخول خلال أول N دقيقة من إغلاق شمعة الإشارة (طزاجة)
    # السعة والتبريد (تُدار من البوت)
    "max_open_trades": 5,
    "reentry_cooldown": 3600,
    "scan_limit": 60,
}


# ═══════════════════════ مؤشرات ═══════════════════════
def sma(a, n):
    return pd.Series(a).rolling(n, min_periods=n).mean().to_numpy()


def rsi_wilder(close, n):
    """RSI بطريقة Wilder (RMA) — مطابق للمنصات."""
    d = np.diff(close, prepend=close[:1])
    up = np.where(d > 0, d, 0.0)
    dn = np.where(d < 0, -d, 0.0)
    au = pd.Series(up).ewm(alpha=1 / n, adjust=False, min_periods=n).mean().to_numpy()
    ad = pd.Series(dn).ewm(alpha=1 / n, adjust=False, min_periods=n).mean().to_numpy()
    rs = au / np.where(ad == 0, np.nan, ad)
    out = 100 - 100 / (1 + rs)
    return np.where(ad == 0, 100.0, np.where(au == 0, 0.0, out))


def atr_wilder(h, l, c, n=14):
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    return pd.Series(tr).ewm(alpha=1 / n, adjust=False, min_periods=n).mean().to_numpy()


def _recent(x, w):
    """تحقق الحدث خلال آخر w شمعة (شاملة الحالية)."""
    return pd.Series(x.astype(float)).rolling(w, min_periods=1).max().to_numpy() > 0.5


def _cross_up(a, b):
    x = np.zeros(len(a), dtype=bool)
    x[1:] = (a[1:] > b[1:]) & (a[:-1] <= b[:-1])
    return x


def _cross_dn(a, b):
    x = np.zeros(len(a), dtype=bool)
    x[1:] = (a[1:] < b[1:]) & (a[:-1] >= b[:-1])
    return x


def _arr(df, col):
    return df[col].to_numpy(dtype=float)


# ═══════════════════════ التحليل ═══════════════════════
def compute_signal(df15, df1h, cfg=None):
    """
    يُعيد dict للإشارة إذا تحققت القواعد على آخر شمعة مكتملة، وإلا None.
    df15/df1h: DataFrame بأعمدة open/high/low/close (شاملة آخر شمعة مغلقة فقط).
    """
    cfg = dict(MARS_CONFIG if cfg is None else cfg)
    if df15 is None or df1h is None or len(df15) < 130 or len(df1h) < 130:
        return None
    c15, o15, h15, l15 = _arr(df15, "close"), _arr(df15, "open"), _arr(df15, "high"), _arr(df15, "low")
    c1h, o1h, h1h, l1h = _arr(df1h, "close"), _arr(df1h, "open"), _arr(df1h, "high"), _arr(df1h, "low")

    def tf(o, h, l, c):
        ma7, ma25, ma99 = sma(c, cfg["ma_fast"]), sma(c, cfg["ma_mid"]), sma(c, cfg["ma_slow"])
        r7 = rsi_wilder(c, cfg["rsi_fast"])
        r25 = rsi_wilder(c, cfg["rsi_mid"])
        rng = h - l
        body = np.where(rng > 0, (c - o) / np.where(rng > 0, rng, 1.0), 0.0)
        lo = pd.Series(l).rolling(cfg["rsi_line_win"], min_periods=cfg["rsi_line_win"]).min()
        hi = pd.Series(h).rolling(cfg["rsi_line_win"], min_periods=cfg["rsi_line_win"]).max()
        line7 = (lo + (hi - lo) * r7 / 100.0).to_numpy()
        line25 = (lo + (hi - lo) * r25 / 100.0).to_numpy()
        return dict(ma7=ma7, ma25=ma25, ma99=ma99, r7=r7,
                    xu=_recent(_cross_up(ma7, ma25) | _cross_up(ma7, ma99), cfg["cross_window_15m"]),
                    xd=_recent(_cross_dn(ma7, ma25) | _cross_dn(ma7, ma99), cfg["cross_window_15m"]),
                    xu1=_recent(_cross_up(ma7, ma25) | _cross_up(ma7, ma99), cfg["cross_window_1h"]),
                    xd1=_recent(_cross_dn(ma7, ma25) | _cross_dn(ma7, ma99), cfg["cross_window_1h"]),
                    up=(ma7 > ma25) | (ma7 > ma99), dn=(ma7 < ma25) | (ma7 < ma99),
                    mom_b=(c > o) & (body >= cfg["momentum_body"]) & (c > ma7) & (c > ma25),
                    mom_s=(c < o) & (-body >= cfg["momentum_body"]) & (c < ma7) & (c < ma25),
                    mom_b99=(c > o) & (body >= cfg["momentum_body"]) & (c > ma7) & (c > ma99),
                    mom_s99=(c < o) & (-body >= cfg["momentum_body"]) & (c < ma7) & (c < ma99),
                    rsi_b=(c > line7) & (c > line25), rsi_s=(c < line7) & (c < line25))

    A, B = tf(o15, h15, l15, c15), tf(o1h, h1h, l1h, c1h)
    i, j = len(c15) - 1, len(c1h) - 1
    atr = atr_wilder(h1h, l1h, c1h, 14)[j]
    px = float(c15[i])
    if not np.isfinite(atr) or atr <= 0 or not np.isfinite(px):
        return None

    buy = A["xu"][i] & A["up"][i] & A["mom_b"][i]
    sell = B["xd1"][j] & B["dn"][j] & B["mom_s"][j]
    if cfg["require_c2"]:
        buy &= B["xu1"][j] & B["up"][j] & B["mom_b99"][j]
        sell &= A["xd"][i] & A["dn"][i] & A["mom_s99"][i]
    if cfg["require_rsi"]:
        buy &= A["rsi_b"][i]
        sell &= B["rsi_s"][j]
    if buy == sell:          # لا إشارة أو تعارض
        return None
    side = "BUY" if buy else "SELL"

    risk = float(cfg["sl_atr1h"]) * atr
    risk_pct = risk / px * 100.0
    if atr / px * 100.0 > float(cfg["max_atr_pct"]):
        return None          # عملة فائقة التقلب — مرفوضة (فلتر التحقق الخارجي)
    if side == "BUY":
        sl, tp = px - risk, px + float(cfg["tp_r"]) * risk
    else:
        sl, tp = px + risk, px - float(cfg["tp_r"]) * risk

    strong = bool((A["ma7"][i] > A["ma25"][i]) and (A["ma7"][i] > A["ma99"][i])) if buy \
        else bool((B["ma7"][j] < B["ma25"][j]) and (B["ma7"][j] < B["ma99"][j]))
    return {
        "side": side, "price_ref": px, "atr": float(atr), "risk_pct": round(risk_pct, 2),
        "sl": sl, "tp": tp, "strong": strong,
        "close_ts_15m": None,
    }


class MaRsiStrategy:
    """واجهة البوت (مطابقة لنمط TrendStrategy): analyze() تُعيد صيغة تنفيذ البوت."""

    def __init__(self, cfg=None, logger=None):
        self.cfg = dict(MARS_CONFIG)
        if cfg:
            self.cfg.update(cfg)
        self.log = logger or (lambda *a, **k: None)
        self.last_scan = {}
        self.stats = {"scanned": 0, "signals": 0, "errors": 0}

    def _closed(self, df):
        """الشموع المغلقة فقط (استبعاد شمعة قيد التكوين)."""
        if df is None or len(df) < 130:
            return None
        return df.iloc[:-1]

    async def analyze(self, bot, symbol, now=None):
        try:
            k15 = self._closed(await bot.get_klines(symbol, "15m", 200))
            k1h = self._closed(await bot.get_klines(symbol, "1h", 200))
            if k15 is None or k1h is None:
                return None
            sig = compute_signal(k15, k1h, self.cfg)
            if not sig:
                return None
            # نافذة الدخول: خلال أول N دقيقة من إغلاق شمعة الإشارة (15د للشراء،
            # ساعة للبيع) — كما في الاختبار كان الدخول عند فتح الشمعة التالية مباشرة.
            now_ms = int((now or time.time()) * 1000)
            if sig["side"] == "BUY":
                sig_close = int(k15["time"].iloc[-1]) + 15 * 60_000
            else:
                sig_close = int(k1h["time"].iloc[-1]) + 60 * 60_000
            elapsed_min = (now_ms - sig_close) / 60000.0
            if elapsed_min < -2 or elapsed_min > float(self.cfg["entry_window_min"]):
                return None   # إشارة قديمة — الزخم تلاشى، لا دخول
            prices = bot.get_price(symbol)
            if not prices:
                return None
            px = prices["ask"] if sig["side"] == "BUY" else prices["bid"]
            risk = float(self.cfg["sl_atr1h"]) * sig["atr"]
            if sig["side"] == "BUY":
                sl, tp = px - risk, px + float(self.cfg["tp_r"]) * risk
            else:
                sl, tp = px + risk, px - float(self.cfg["tp_r"]) * risk
            return {
                "symbol": symbol, "direction": sig["side"], "price": px,
                "sl": sl, "tp1": tp, "tp2": None,
                "score": 8, "strategy": "MARS", "atr_ref": sig["atr"],
                "components": {
                    "strategy": "MARS", "trigger": "تقاطع 7/25/99 + زخم",
                    "strong": sig["strong"], "risk_pct": sig["risk_pct"],
                },
                "signals_smc": [
                    f"📐 MA7 قطعت {'فوق' if sig['side'] == 'BUY' else 'تحت'} متوسطات 25/99 + إغلاق بزخم",
                    f"🛡️ وقف 3×ATR ساعة ({sig['risk_pct']:.1f}%) | هدف 1R | فلتر تقلب ≤6%",
                ],
            }
        except Exception as e:
            self.stats["errors"] += 1
            self.log(f"خطأ تحليل 7/25/99 لـ {symbol}: {e}")
            return None

    async def scan(self, bot, candidates, active_symbols, cooldowns):
        found, scanned = [], 0
        now = time.time()
        for sym in candidates:
            if len(found) >= 2:
                break
            if sym in active_symbols or cooldowns.get(sym, 0) > now:
                continue
            if scanned >= int(self.cfg["scan_limit"]):
                break
            scanned += 1
            a = await self.analyze(bot, sym, now)
            if a:
                found.append(a)
        self.stats["scanned"] = scanned
        self.stats["signals"] = len(found)
        self.last_scan = {"ts": now, "scanned": scanned, "signals": len(found)}
        return found


# ═══════════════════════ قاعدة بيانات مستقلة ═══════════════════════
# نفس نمط TrendDB حرفياً — جداول مستقلة (mars_trades / mars_daily) تنجو
# من إعادة التشغيل والنشر، ولا تختلط بأي استراتيجية أخرى.
MARS_SCHEMA = """
CREATE TABLE IF NOT EXISTS mars_trades (
    symbol TEXT PRIMARY KEY, side TEXT, entry REAL, sl REAL, tp1 REAL, atr REAL,
    entry_ts REAL, exit_ts REAL, pnl REAL, pnl_pct REAL, win INTEGER DEFAULT -1,
    reason TEXT, components TEXT, margin REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS mars_daily (
    date TEXT PRIMARY KEY, pnl REAL, wins INTEGER, losses INTEGER
);
CREATE INDEX IF NOT EXISTS idx_mars_entry ON mars_trades(entry_ts);
"""


class MaRsiDB:
    def __init__(self, db_name="sniper_v8.db"):
        self.db_name = db_name

    async def init(self):
        import aiosqlite
        async with aiosqlite.connect(self.db_name) as db:
            await db.executescript(MARS_SCHEMA)
            try:
                await db.execute("ALTER TABLE mars_trades ADD COLUMN margin REAL DEFAULT 0")
            except Exception:
                pass
            await db.commit()

    async def open(self, t):
        import aiosqlite
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                """INSERT OR REPLACE INTO mars_trades
                   (symbol, side, entry, sl, tp1, atr, entry_ts, margin, components)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (t["symbol"], t["side"], t["entry_price"], t["sl"], t.get("tp"),
                 t.get("atr_ref") or 0, t["entry_time"],
                 float(t.get("margin_usdt") or 0),
                 json.dumps(t.get("components", {}), ensure_ascii=False)))
            await db.commit()

    async def close(self, symbol, exit_ts, pnl, pnl_pct, win, reason):
        import aiosqlite
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                """UPDATE mars_trades SET exit_ts=?, pnl=?, pnl_pct=?, win=?, reason=?
                   WHERE symbol=? AND win=-1""",
                (exit_ts, pnl, pnl_pct, int(win), str(reason)[:200], symbol))
            day = time.strftime("%Y-%m-%d", time.localtime(exit_ts))
            async with db.execute("SELECT pnl, wins, losses FROM mars_daily WHERE date=?",
                                  (day,)) as cur:
                row = await cur.fetchone()
            w, l = (1, 0) if win else (0, 1)
            if row:
                await db.execute("UPDATE mars_daily SET pnl=?, wins=?, losses=? WHERE date=?",
                                 (row[0] + pnl, row[1] + w, row[2] + l, day))
            else:
                await db.execute("INSERT INTO mars_daily VALUES (?,?,?,?)", (day, pnl, w, l))
            await db.commit()

    async def update_sl(self, symbol, sl):
        import aiosqlite
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("UPDATE mars_trades SET sl=? WHERE symbol=? AND win=-1",
                             (sl, symbol))
            await db.commit()

    async def open_symbols(self):
        """استعادة صفقات الموجات المفتوحة بعد إعادة التشغيل."""
        import aiosqlite
        out = {}
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute(
                    """SELECT symbol, side, entry, sl, tp1, atr, entry_ts, margin
                       FROM mars_trades WHERE win=-1""") as cur:
                for r in await cur.fetchall():
                    out[r[0]] = {"symbol": r[0], "side": r[1], "entry": r[2], "sl": r[3],
                                 "tp1": r[4], "tp2": None, "atr": r[5], "entry_ts": r[6],
                                 "margin": r[7] or 0}
        return out

    async def summary(self, days=30):
        import aiosqlite
        since = time.time() - days * 86400
        out = {"closed": 0, "wins": 0, "losses": 0, "winrate": 0.0, "net": 0.0,
               "pf": 0.0, "avg_win": 0.0, "avg_loss": 0.0, "trades": [], "daily": []}
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                    """SELECT COUNT(*) n, SUM(win=1) w, SUM(win=0) l, SUM(pnl) net,
                              AVG(CASE WHEN win=1 THEN pnl END) aw,
                              AVG(CASE WHEN win=0 THEN pnl END) al,
                              SUM(CASE WHEN win=1 THEN pnl ELSE 0 END) g,
                              SUM(CASE WHEN win=0 THEN -pnl ELSE 0 END) ls
                       FROM mars_trades WHERE win>=0 AND exit_ts>=?""", (since,)) as cur:
                r = await cur.fetchone()
            if r and r["n"]:
                n = r["n"]
                out.update({
                    "closed": n, "wins": int(r["w"] or 0), "losses": int(r["l"] or 0),
                    "winrate": round((r["w"] or 0) / n * 100, 2),
                    "net": round(r["net"] or 0.0, 2),
                    "pf": round((r["g"] or 0) / r["ls"], 3) if (r["ls"] or 0) > 0 else 999.0,
                    "avg_win": round(r["aw"] or 0.0, 2), "avg_loss": round(r["al"] or 0.0, 2),
                })
            async with db.execute(
                    """SELECT symbol, side, entry, exit_ts, pnl, pnl_pct, win, reason
                       FROM mars_trades WHERE win>=0 ORDER BY exit_ts DESC LIMIT 60""") as cur:
                out["trades"] = [dict(x) for x in await cur.fetchall()]
            async with db.execute(
                    "SELECT date, pnl, wins, losses FROM mars_daily ORDER BY date DESC LIMIT 30") as cur:
                out["daily"] = [{"date": x[0], "pnl": round(x[1] or 0, 2), "wins": x[2],
                                 "losses": x[3]} for x in await cur.fetchall()]
        return out


class MaRsiExitManager:
    """خروج معدّل معتمد: وقف 3×ATR + هدف 1R — بلا جني جزئي ولا وقف متحرك."""

    def __init__(self, cfg=None, logger=None):
        self.cfg = dict(MARS_CONFIG)
        if cfg:
            self.cfg.update(cfg)
        self.log = logger or (lambda *a, **k: None)

    def decide(self, trade, price, atr_now=None):
        side = trade["side"]
        is_buy = side == "BUY"
        sl = float(trade["sl"])
        tp = float(trade.get("tp") or 0)
        if (is_buy and price <= sl) or ((not is_buy) and price >= sl):
            return {"action": "close", "reason": "🛑 ضرب الوقف"}
        if tp and ((is_buy and price >= tp) or ((not is_buy) and price <= tp)):
            return {"action": "close", "reason": "🎯 هدف 1R محقق"}
        return {"action": "hold"}
