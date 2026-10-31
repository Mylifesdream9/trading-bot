"""
═══════════════════════════════════════════════════════════════════════
  🚀 الاستراتيجية الثانية — "راكب الترند" (Trend Rider) — مستقلة تماماً
═══════════════════════════════════════════════════════════════════════
  مبنية من الصفر: تحليل خاص، دخول خاص، وإدارة خروج خاصة.
  لا تشترك مع استراتيجية "القناص" في أي شيء سوى محرك التنفيذ في البوت
  (فتح المركز/الوقف على المنصة) — التحليل والقرار والخروج كلها هنا.

  ── منطق الدخول ──
    الاتجاه العام (4h): EMA20 > EMA50  و  السعر فوق EMA50.
    الاختراق (1h): إغلاق الشمعة الساعية فوق أعلى 48 شمعة سابقة (يومان).
    التأكيد: شمعة الاختراق صاعدة (إغلاق > افتتاح) — وللعرض بالعكس.
    فلتر مخاطرة: 0.15% ≤ ATR(1h) ≤ 6% | الوقف ≤ 3.5% من السعر
                | استبعاد العملات المتحركة > 35% في 24 ساعة.

  ── إدارة الخروج (خاصة بها بالكامل) ──
    الوقف الابتدائي : 2.5 × ATR(1h)
    TP1             : 0.9 × مسافة الوقف → يُغلق 70% من المركز
    بعد TP1         : نقل الوقف للتعادل +0.2% ثم وقف متحرك
                      = أعلى إغلاق منذ الدخول − 1.5 × ATR(1h)
    لا هدف ثانٍ ثابت : الـ30% المتبقية تركب الترند حتى يضربه الوقف المتحرك
    خروج زمني       : 5 أيام إن لم يتحقق شيء

  ── نتيجة الاختبار (600 عملة × 30 يوماً، Bitget USDT-M) ──
    داخل العيّنة (300 عملة): فوز 56.0% | عامل ربح 1.104
    خارج العيّنة (300 عملة): فوز 56.3% | عامل ربح 1.107
    الكل (600 عملة)        : فوز 56.2% | عامل ربح 1.106 | صافي +1,183$
    سعة 3 صفقات متزامنة    : عامل ربح 1.096 | صافي +29.9$
    الارتباط اليومي مع الاستراتيجية الأولى: 0.42 (توزيع حقيقي للمخاطر)
    تحذير: النصف الثاني من الشهر كان ضعيفاً (PF 0.95) — الاستراتيجيتان
    تكملان بعضهما: القناص أقوى في هذا النصف والترند أقوى في النصف الأول.
═══════════════════════════════════════════════════════════════════════
"""
import json
import math
import time

import numpy as np
import pandas as pd

TREND_CONFIG = {
    "name": "TREND",
    "label": "راكب الترند",
    "enabled": True,
    # الدخول
    "donch": 48,               # اختراق أعلى/أدنى 48 شمعة ساعة سابقة
    "sl_atr1h": 2.5,           # الوقف = 2.5 × ATR(1h)
    "tp1_r": 0.90,             # TP1 = 0.9 × مسافة الوقف
    "partial": 0.70,           # يُغلق 70% عند TP1
    "trail_atr": 1.5,          # الوقف المتحرك = 1.5 × ATR(1h) من أعلى إغلاق
    "be_offset": 0.002,        # التعادل +0.2% بعد الجني
    "max_hold_minutes": 5 * 24 * 60,
    # فلاتر
    "max_risk_pct": 3.5,
    "min_atr_pct": 0.15,
    "max_atr_pct": 6.0,
    "max_day_change": 0.35,
    "entry_window_min": 25,    # الدخول خلال أول 25 دقيقة بعد إغلاق الساعة
    # السعة المستقلة
    "max_open_trades": 5,
    "reentry_cooldown": 3600,
    "scan_limit": 60,
}


# ═══════════════════════ مؤشرات ═══════════════════════
def ema(a, n):
    a = np.asarray(a, dtype=float)
    out = np.empty_like(a)
    out[0] = a[0]
    k = 2.0 / (n + 1.0)
    for i in range(1, len(a)):
        out[i] = out[i - 1] + k * (a[i] - out[i - 1])
    return out


def rma(a, n):
    a = np.asarray(a, dtype=float)
    out = np.full_like(a, np.nan)
    if len(a) < n:
        return out
    out[n - 1] = np.nanmean(a[:n])
    for i in range(n, len(a)):
        out[i] = out[i - 1] + (a[i] - out[i - 1]) / n
    return out


def atr(h, l, c, n=14):
    c = np.asarray(c, dtype=float)
    h = np.asarray(h, dtype=float)
    l = np.asarray(l, dtype=float)
    pc = np.roll(c, 1)
    pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    return rma(tr, n)


def _closed(df):
    """الشموع المغلقة فقط (يُستبعد آخر شمعة قيد التكوين)."""
    if df is None or len(df) < 60:
        return None
    return df.iloc[:-1].copy()


def _arr(df, col):
    return df[col].to_numpy(dtype=float)


# ═══════════════════════ التحليل ═══════════════════════
def compute_signal(df15, df1h, df4h, cfg=None):
    """
    يُعيد dict للتحليل إذا تحققت شروط الدخول على آخر شمعة ساعية مكتملة، وإلا None.
    """
    cfg = dict(TREND_CONFIG if cfg is None else cfg)
    h1, h4, m15 = _closed(df1h), _closed(df4h), _closed(df15)
    if h1 is None or h4 is None or m15 is None:
        return None
    if len(h1) < 220 or len(h4) < 55:
        return None

    c1, o1, hh1, ll1 = _arr(h1, "close"), _arr(h1, "open"), _arr(h1, "high"), _arr(h1, "low")
    a1 = atr(hh1, ll1, c1, 14)
    e20, e50 = ema(c1, 20), ema(c1, 50)
    n = int(cfg["donch"])
    if len(c1) < n + 5:
        return None
    prior_high = float(pd.Series(hh1).rolling(n).max().iloc[-2])   # بدون شمعة الإشارة
    prior_low = float(pd.Series(ll1).rolling(n).min().iloc[-2])
    i = len(c1) - 1
    cx, ox = c1[i], o1[i]
    a = a1[i]
    if not np.isfinite(a) or a <= 0:
        return None

    c4 = _arr(h4, "close")
    e20_4, e50_4 = ema(c4, 20)[-1], ema(c4, 50)[-1]
    up4 = e20_4 > e50_4 and cx > e50_4
    dn4 = e20_4 < e50_4 and cx < e50_4

    px = float(m15["close"].iloc[-1])
    atr_pct = a / px * 100.0
    if atr_pct > float(cfg["max_atr_pct"]) or atr_pct < float(cfg["min_atr_pct"]):
        return None
    mc = _arr(m15, "close")
    if len(mc) >= 97 and abs(mc[-1] / max(mc[-97], 1e-12) - 1.0) > float(cfg["max_day_change"]):
        return None

    side = None
    if up4 and cx > prior_high and cx > ox:
        side = "BUY"
    elif dn4 and cx < prior_low and cx < ox:
        side = "SELL"
    if side is None:
        return None

    risk = float(cfg["sl_atr1h"]) * a
    risk_pct = risk / px * 100.0
    if risk_pct > float(cfg["max_risk_pct"]) or risk_pct < 0.05:
        return None

    return {
        "side": side, "price_ref": px, "atr": float(a), "atr_pct": round(atr_pct, 2),
        "risk": float(risk), "risk_pct": round(risk_pct, 2),
        "prior_high": round(prior_high, 10), "prior_low": round(prior_low, 10),
        "trend_4h": "صاعد" if up4 else "هابط",
        "hour_close_ts": int(h1["close_time"].iloc[-1]) if "close_time" in h1 else None,
        "hour_open_ts": int(h1["time"].iloc[-1]),
        "hour_ref_price": float(cx),
    }


class TrendStrategy:
    """واجهة البوت: analyze() تُعيد تحليلاً بصيغة تنفيذ البوت نفسها."""

    def __init__(self, cfg=None, logger=None):
        self.cfg = dict(TREND_CONFIG)
        if cfg:
            self.cfg.update(cfg)
        self.log = logger or (lambda *a, **k: None)
        self.last_scan = {}
        self.stats = {"scanned": 0, "signals": 0, "errors": 0}

    async def analyze(self, bot, symbol, now=None):
        try:
            k15 = await bot.get_klines(symbol, "15m", 200)
            k1h = await bot.get_klines(symbol, "1h", 260)
            k4h = await bot.get_klines(symbol, "4h", 120)
            if k15 is None or k1h is None or k4h is None:
                return None
            sig = compute_signal(k15, k1h, k4h, self.cfg)
            if not sig:
                return None
            # نافذة الدخول: خلال أول X دقيقة بعد إغلاق الشمعة الساعية
            now_ms = int((now or time.time()) * 1000)
            hour_open = sig["hour_open_ts"]
            elapsed_min = (now_ms - (hour_open + 3600_000)) / 60000.0
            if elapsed_min < -2 or elapsed_min > float(self.cfg["entry_window_min"]):
                return None
            prices = bot.get_price(symbol)
            if not prices:
                return None
            px = prices["ask"] if sig["side"] == "BUY" else prices["bid"]
            risk = float(self.cfg["sl_atr1h"]) * sig["atr"]
            if sig["side"] == "BUY":
                sl, tp1 = px - risk, px + float(self.cfg["tp1_r"]) * risk
            else:
                sl, tp1 = px + risk, px - float(self.cfg["tp1_r"]) * risk
            return {
                "symbol": symbol, "direction": sig["side"], "price": px,
                "sl": sl, "tp1": tp1, "tp2": None,
                "score": 8, "strategy": "TREND",
                "atr_ref": sig["atr"],
                "components": {
                    "strategy": "TREND", "trigger": "اختراق 48 ساعة",
                    "trend_4h": sig["trend_4h"], "atr_pct": sig["atr_pct"],
                    "risk_pct": sig["risk_pct"], "level": sig["prior_high"] if sig["side"] == "BUY" else sig["prior_low"],
                },
                "signals_smc": [
                    f"🚀 اختراق {'صاعد' if sig['side']=='BUY' else 'هابط'} بعد 48 ساعة تجميع",
                    f"📈 اتجاه 4 ساعات {sig['trend_4h']} | ATR(1h) {sig['atr_pct']}%",
                    f"🛡️ وقف {sig['risk_pct']}% | TP1 عند {self.cfg['tp1_r']}R ثم وقف متحرك",
                ],
            }
        except Exception as e:
            self.stats["errors"] += 1
            self.log(f"خطأ تحليل الترند لـ {symbol}: {e}")
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


# ═══════════════════════ إدارة الخروج الخاصة ═══════════════════════
class TrendExitManager:
    """
    تُدار الصفقة بالكامل هنا: وقف ATR، جني 70% عند TP1، تعادل، وقف متحرك 1.5×ATR،
    وخروج زمني 5 أيام. البوت لا يطبّق قواعد الاستراتيجية الأولى على صفقات الترند.
    """

    def __init__(self, cfg=None, logger=None):
        self.cfg = dict(TREND_CONFIG)
        if cfg:
            self.cfg.update(cfg)
        self.log = logger or (lambda *a, **k: None)

    def decide(self, trade, price, atr_now=None):
        """
        يُعيد:
          {"action": "hold"}
          {"action": "close",  "reason": str}
          {"action": "partial", "reason": str}     # جني 70% + نقل للتعادل
          {"action": "move_sl", "sl": float}       # تحديث الوقف فقط
        """
        side = trade["side"]
        cfg = self.cfg
        atr = float(trade.get("atr_ref") or (atr_now or 0) or 0)
        if atr <= 0:
            return {"action": "hold"}
        is_buy = side == "BUY"
        entry = float(trade["entry_price"])
        sl = float(trade["sl"])
        tp1 = float(trade["tp"]) if trade.get("tp") else None
        partial_done = bool(trade.get("partial_closed"))

        # 1) وقف الخسارة
        if (is_buy and price <= sl) or ((not is_buy) and price >= sl):
            return {"action": "close", "reason": "🛑 ضرب الوقف" if not partial_done else "🪂 الوقف المتحرك"}

        # 2) خروج زمني
        held_min = (time.time() - float(trade["entry_time"])) / 60.0
        if held_min >= float(cfg["max_hold_minutes"]):
            return {"action": "close", "reason": "⏳ خروج زمني (5 أيام)"}

        # 3) الجني الجزئي عند TP1
        if (not partial_done) and tp1:
            if (is_buy and price >= tp1) or ((not is_buy) and price <= tp1):
                return {"action": "partial", "reason": "🎯 جني 70% عند TP1"}

        # 4) الوقف المتحرك بعد الجني (1.0 × ATR من أعلى/أدنى إغلاق)
        if partial_done:
            ext = float(trade.get("highest_price" if is_buy else "lowest_price") or price)
            if is_buy:
                ext = max(ext, price)
                new_sl = ext - float(cfg["trail_atr"]) * atr
                if new_sl > sl + 1e-12:
                    return {"action": "move_sl", "sl": new_sl}
            else:
                ext = min(ext, price)
                new_sl = ext + float(cfg["trail_atr"]) * atr
                if new_sl < sl - 1e-12:
                    return {"action": "move_sl", "sl": new_sl}
        return {"action": "hold"}


# ═══════════════════════ قاعدة بيانات مستقلة ═══════════════════════
SCHEMA = """
CREATE TABLE IF NOT EXISTS trend_trades (
    symbol TEXT PRIMARY KEY, side TEXT, entry REAL, sl REAL, tp1 REAL, atr REAL,
    entry_ts REAL, exit_ts REAL, pnl REAL, pnl_pct REAL, win INTEGER DEFAULT -1,
    reason TEXT, components TEXT, margin REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS trend_daily (
    date TEXT PRIMARY KEY, pnl REAL, wins INTEGER, losses INTEGER
);
CREATE INDEX IF NOT EXISTS idx_trend_entry ON trend_trades(entry_ts);
"""


class TrendDB:
    def __init__(self, db_name="sniper_v8.db"):
        self.db_name = db_name

    async def init(self):
        import aiosqlite
        async with aiosqlite.connect(self.db_name) as db:
            await db.executescript(SCHEMA)
            # ترقية قواعد بيانات قديمة: عمود هامش صفقة الترند
            try:
                await db.execute("ALTER TABLE trend_trades ADD COLUMN margin REAL DEFAULT 0")
            except Exception:
                pass
            await db.commit()

    async def open(self, t):
        import aiosqlite
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                """INSERT OR REPLACE INTO trend_trades
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
                """UPDATE trend_trades SET exit_ts=?, pnl=?, pnl_pct=?, win=?, reason=?
                   WHERE symbol=? AND win=-1""",
                (exit_ts, pnl, pnl_pct, int(win), str(reason)[:200], symbol))
            day = time.strftime("%Y-%m-%d", time.localtime(exit_ts))
            async with db.execute("SELECT pnl, wins, losses FROM trend_daily WHERE date=?", (day,)) as cur:
                row = await cur.fetchone()
            w, l = (1, 0) if win else (0, 1)
            if row:
                await db.execute("UPDATE trend_daily SET pnl=?, wins=?, losses=? WHERE date=?",
                                 (row[0] + pnl, row[1] + w, row[2] + l, day))
            else:
                await db.execute("INSERT INTO trend_daily VALUES (?,?,?,?)", (day, pnl, w, l))
            await db.commit()

    async def update_sl(self, symbol, sl):
        import aiosqlite
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("UPDATE trend_trades SET sl=? WHERE symbol=? AND win=-1", (sl, symbol))
            await db.commit()

    async def open_symbols(self):
        """استعادة صفقات الترند المفتوحة بعد إعادة التشغيل."""
        import aiosqlite
        out = {}
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute(
                    """SELECT symbol, side, entry, sl, tp1, atr, entry_ts, margin
                       FROM trend_trades WHERE win=-1""") as cur:
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
                       FROM trend_trades WHERE win>=0 AND exit_ts>=?""", (since,)) as cur:
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
                       FROM trend_trades WHERE win>=0 ORDER BY exit_ts DESC LIMIT 60""") as cur:
                out["trades"] = [dict(x) for x in await cur.fetchall()]
            async with db.execute("SELECT date, pnl, wins, losses FROM trend_daily ORDER BY date DESC LIMIT 30") as cur:
                out["daily"] = [{"date": x[0], "pnl": round(x[1] or 0, 2), "wins": x[2], "losses": x[3]}
                                for x in await cur.fetchall()]
        return out
