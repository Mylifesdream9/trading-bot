"""
═══════════════════════════════════════════════════════════════════════
  📐 موجات 7/25/99 V9 — روبوت باستراتيجيتين مستقلتين تماماً
═══════════════════════════════════════════════════════════════════════
  ⚠️ تغيير جوهري عن النسخة السابقة: استراتيجية القناص حُذفت من المسح
     والدخول نهائياً — لم يعد هناك أي تحليل أو إشارة أو دخول منها.
     صفقات القناص القديمة التي كانت مفتوحة لحظة التبديل (إن وُجدت) تُدار
     بقواعدها القديمة فقط حتى تُغلق، ولن يُفتح منها صفقة جديدة أبداً.

  الاستراتيجية 1 (موجات 7/25/99 — MARS): حلت محل القناص.
    · الدخول (التأكيد الأول كما اختُبر — بدون تأكيد ثانٍ وبدون RSI):
        شراء: MA7 قطعت MA25 أو MA99 صعوداً ضمن آخر 6 شمعات 15د + إغلاق 15د
              بزخم (جسم ≥ 50% من المدى) فوق MA7 وMA25 — خلال 10 دقائق من
              إغلاق شمعة الإشارة.
        بيع : MA7(ساعة) قطعت هبوطاً ضمن آخر 3 شمعات + إغلاق ساعي بزخم تحت
              MA7 وMA25 — خلال 10 دقائق من إغلاق شمعة الإشارة.
    · الخروج (التركيبة المعدلة المعتمدة بعد التشخيص والتحقق الخارجي):
        وقف = 3.0 × ATR(1h) | هدف = 1R = 3.0 × ATR(1h)
        فلتر التقلب: رفض الإشارة إذا ATR%(1h) > 6
        بلا جني جزئي ولا وقف متحرك — خروج كامل عند الهدف أو الوقف.
    · نتيجة التركيبة المعدلة على فترة تحقق منفصلة تماماً عن فترة التطوير
      (فبراير–أبريل 2026، 500 زوج، 375 صفقة):
        فوز 55.2% مقابل 36.3% للأساس | صافي +324.5$ مقابل −112.6$ | PF 1.25
    · هامش الصفقة 14$ ورافعة 10x وسعة 5 صفقات متزامنة (نفس إعدادات الاختبار)
      — كلها قابلة للضبط من متغيرات البيئة أو من لوحة MARS.

  الاستراتيجية 2 (راكب الترند): كما هي تماماً — بلا أي تغيير في ملفها.

  التشغيل:  python3 bot_v9.py        (نفس أمر التشغيل السابق)

  · لكل استراتيجية سعة صفقات مستقلة (MAX_OPEN_TRADES_MARS / MAX_OPEN_TRADES_TREND)
    وهامش صفقة مستقل (TRADE_SIZE_USDT_MARS / TRADE_SIZE_USDT_TREND — 0 = مشترك).
  · كل صفقة تُوسم باسم استراتيجيتها، وتُدار بقواعدها فقط:
      - صفقات MARS    → MaRsiExitManager (وقف 3×ATR + هدف 1R).
      - صفقات الترند  → TrendExitManager (جني 70% عند 0.9R + وقف متحرك).
      - صفقات القناص القديمة → monitor_trades الأصلي (حتى تُغلق فقط).
  · المطوّر التكيفي (AdaptiveTuner) صار معطلاً فعلياً: لا صفقات قناص جديدة،
    وصفقات MARS والترند لا تتغذى منه إطلاقاً.
  · إحصاءات وسجلات مستقلة في قاعدة البيانات:
      mars_trades / mars_daily  +  trend_trades / trend_daily.
  · اللوحات الثلاث في تطبيق واحد: / (القناص القديم) · /trend · /mars
      تبويب الحركات في لوحة MARS يسجل كل حدث: مسح، دخول، إغلاق.
═══════════════════════════════════════════════════════════════════════
"""
import asyncio
import json
import logging
import os
import time
from collections import deque

import aiosqlite

import bot as botmod                      # المحرك (تنفيذ/أوامر/مصالحة) — كما هو
import web_panel_mars                     # اللوحات الثلاث في تطبيق واحد
from strategy_mars import (MaRsiDB, MaRsiExitManager,
                           MaRsiStrategy)
from strategy_trend import (TrendDB, TrendExitManager,
                            TrendStrategy)

logger = logging.getLogger('MarsBotV9')
logger.setLevel(logging.INFO)
try:
    # إخراج سجلات هذا الملف في bot_v8.log نفسه (كانت تضيع سابقاً)
    for _h in logging.getLogger('SniperV8').handlers:
        logger.addHandler(_h)
except Exception:
    pass

# ═════════ سعة/هامش استراتيجية موجات 7/25/99 (مستقلة) ═════════
MAX_OPEN_TRADES_MARS = int(os.environ.get('MAX_OPEN_TRADES_MARS', '5'))
# هامش صفقة MARS: الافتراضي 14$ — نفس إعدادات التركيبة المعدلة المُتحقَّق منها
MARS_TRADE_SIZE_USDT = float(os.environ.get('TRADE_SIZE_USDT_MARS', '14'))
MARS_ENABLED = os.environ.get('STRATEGY_MARS_ENABLED', 'true').lower() == 'true'

# سعة الصفقات الخاصة باستراتيجية الترند (مستقلة — كما هي)
MAX_OPEN_TRADES_TREND = int(os.environ.get('MAX_OPEN_TRADES_TREND', '5'))
# سعة مسار القناص القديم (لا جديد منه — تهم فقط صفقاته القديمة المفتوحة)
MAX_OPEN_TRADES_SNIPER = int(os.environ.get('MAX_OPEN_TRADES_SNIPER', '0'))
# سقف إجمالي صارم لكل الصفقات المفتوحة من الاستراتيجيتين (0 = بلا سقف)
MAX_TOTAL_TRADES = int(os.environ.get('MAX_TOTAL_TRADES', '0'))
TREND_ENABLED = os.environ.get('STRATEGY_TREND_ENABLED', 'true').lower() == 'true'
# هامش صفقة الترند الخاص (0 = يستخدم TRADE_SIZE_USDT المشترك نفسه)
TREND_TRADE_SIZE_USDT = float(os.environ.get('TRADE_SIZE_USDT_TREND', '0'))


class _NullTuner:
    """بديل صامت حتى لا تتلوث ذاكرة المطوّر التكيفي بصفقات MARS أو الترند."""

    def record(self, *a, **k):
        return

    def describe(self):
        return "—"

    def recent_winrate(self, *a, **k):
        return None


class MarsBotV9(botmod.LegendarySniperFuturesV8):
    def __init__(self):
        super().__init__()
        # ✅ مسار قاعدة البيانات من متغير البيئة (مثال على Railway: DB_FILE=/data/sniper_v8.db)
        db_file = os.environ.get('DB_FILE')
        if db_file:
            self.db.db_name = db_file

        # ── الاستراتيجية 1: موجات 7/25/99 (حلّت محل القناص) ──
        self.mars = MaRsiStrategy({"enabled": MARS_ENABLED}, logger.warning)
        self.mars_exit = MaRsiExitManager(logger=logger.warning)
        self.mars_db = MaRsiDB(self.db.db_name)
        self.mars_cooldown = {}
        self.stats_mars = {"wins": 0, "losses": 0, "trades": 0}
        self._mars_cursor = 0
        self.mars_events = deque(maxlen=300)   # سجل حيّ لكل حركة
        self.mars_capacity = MAX_OPEN_TRADES_MARS
        self.mars_trade_size = (MARS_TRADE_SIZE_USDT if MARS_TRADE_SIZE_USDT > 0
                                else self.TRADE_SIZE_USDT)

        # ── الاستراتيجية 2: راكب الترند (كما هي تماماً) ──
        self.trend = TrendStrategy({"enabled": TREND_ENABLED}, logger.warning)
        self.trend_exit = TrendExitManager(logger=logger.warning)
        self.trend_db = TrendDB(self.db.db_name)
        self.trend_cooldown = {}
        self.stats_trend = {"wins": 0, "losses": 0, "trades": 0}
        self._trend_cursor = 0
        self.trend_events = deque(maxlen=300)
        self.trend_capacity = MAX_OPEN_TRADES_TREND
        self.trend_trade_size = (TREND_TRADE_SIZE_USDT if TREND_TRADE_SIZE_USDT > 0
                                 else self.TRADE_SIZE_USDT)

        # أرقام تعرضها اللوحة (اللوحة لا تعرف ثوابت هذا الملف)
        self.total_cap = MAX_TOTAL_TRADES
        self._apply_sniper_cap()

    # ═══════════════ سجل الحركات (يظهر في تبويب الحركات) ═══════════════
    def _log_mars(self, kind, msg):
        try:
            self.mars_events.append({"ts": time.time(), "kind": kind, "msg": msg})
        except Exception:
            pass

    def _log_trend(self, kind, msg):
        try:
            self.trend_events.append({"ts": time.time(), "kind": kind, "msg": msg})
        except Exception:
            pass

    def _apply_sniper_cap(self):
        """تطبيق سقف مسار القناص القديم القادم من البيئة (إن وُجد)."""
        if MAX_OPEN_TRADES_SNIPER > 0 and getattr(self, 'MAX_OPEN_TRADES', 0) != MAX_OPEN_TRADES_SNIPER:
            self.MAX_OPEN_TRADES = MAX_OPEN_TRADES_SNIPER

    def _total_cap_hit(self, extra=0):
        """هل وصلنا السقف الإجمالي للصفقات المفتوحة؟"""
        if MAX_TOTAL_TRADES <= 0:
            return False
        return len(self.active_trades) + extra > MAX_TOTAL_TRADES

    # ═══════════════ الإقلاع: استعادة الصفقات المفتوحة ═══════════════
    async def _trend_open_rows(self):
        """صفوف الترند المفتوحة (win=-1) بأمان — مع إعادة محاولة وترقية القاعدة."""
        last_err = None
        for attempt in (1, 2):
            try:
                return await self.trend_db.open_symbols()
            except Exception as e:
                last_err = e
                if attempt == 1:
                    logger.warning(f"⚠️ فشلت قراءة صفقات الترند المفتوحة ({e}) — تهيئة القاعدة وإعادة المحاولة")
                    try:
                        await self.trend_db.init()
                    except Exception:
                        pass
        logger.error(f"❌ تعذّرت قراءة صفقات الترند المفتوحة ({last_err}) — سيُعوّضها مسار التبنّي الواعي في المصالحة")
        return {}

    async def _mars_open_rows(self):
        """صفوف الموجات المفتوحة (win=-1) بأمان — نفس نمط الترند."""
        last_err = None
        for attempt in (1, 2):
            try:
                return await self.mars_db.open_symbols()
            except Exception as e:
                last_err = e
                if attempt == 1:
                    logger.warning(f"⚠️ فشلت قراءة صفقات الموجات المفتوحة ({e}) — تهيئة القاعدة وإعادة المحاولة")
                    try:
                        await self.mars_db.init()
                    except Exception:
                        pass
        logger.error(f"❌ تعذّرت قراءة صفقات الموجات المفتوحة ({last_err}) — سيُعوّضها مسار التبنّي الواعي في المصالحة")
        return {}

    async def main_loop(self):
        try:
            await self.trend_db.init()
        except Exception as e:
            logger.error(f"تعذر تهيئة قاعدة بيانات الترند: {e}")
        try:
            await self.mars_db.init()
        except Exception as e:
            logger.error(f"تعذر تهيئة قاعدة بيانات الموجات: {e}")

        # ✅ تحميل الإعدادات المحفوظة من اللوحتين (تنجو من إعادة التشغيل والنشر)
        try:
            await self.db.init_db()   # ضمان وجود جدول الإعدادات حتى على قاعدة جديدة
        except Exception:
            pass
        for key, strat, mgr, cap_attr in (
                ('mars_config', self.mars, self.mars_exit, 'mars_capacity'),
                ('trend_config', self.trend, self.trend_exit, 'trend_capacity')):
            try:
                raw = await self.db.get_param(key)
                if raw:
                    saved = json.loads(raw)
                    strat.cfg.update({k: v for k, v in saved.items() if k in strat.cfg})
                    mgr.cfg.update(strat.cfg)
                    cap = int(strat.cfg.get('max_open_trades', getattr(self, cap_attr)))
                    setattr(self, cap_attr, cap)
                    logger.info(f"⚙️ إعدادات {key} محمّلة من القاعدة — سعة {cap} صفقة، "
                                f"الحالة: {'مفعّلة' if strat.cfg.get('enabled') else 'متوقفة'}")
            except Exception as e:
                logger.warning(f"تعذر تحميل إعدادات {key} المحفوظة: {e}")

        orig_load = self.db.load_active_trades

        async def _load_with_strategies():
            trades = await orig_load()
            for sym, row in (await self._trend_open_rows()).items():
                if sym in trades and not trades[sym].get('strategy'):
                    trades[sym]['strategy'] = 'TREND'
                    trades[sym]['atr_ref'] = row.get('atr') or 0.0
                    trades[sym]['tp2'] = None
                    trades[sym]['components'] = {'strategy': 'TREND'}
                    m = float(row.get('margin') or 0)
                    trades[sym]['margin_usdt'] = m if m > 0 else self.trend_trade_size
                    logger.info(f"♻️ استُعيدت صفقة ترند مفتوحة: {sym}")
            for sym, row in (await self._mars_open_rows()).items():
                if sym in trades and not trades[sym].get('strategy'):
                    trades[sym]['strategy'] = 'MARS'
                    trades[sym]['atr_ref'] = row.get('atr') or 0.0
                    trades[sym]['tp2'] = None
                    trades[sym]['components'] = {'strategy': 'MARS'}
                    m = float(row.get('margin') or 0)
                    trades[sym]['margin_usdt'] = m if m > 0 else self.mars_trade_size
                    logger.info(f"♻️ استُعيدت صفقة موجات مفتوحة: {sym}")
            return trades

        self.db.load_active_trades = _load_with_strategies

        # اللوحات الثلاث: / (القناص القديم) · /trend · /mars
        botmod.start_web_panel = web_panel_mars.start_web_panel_full
        await super().main_loop()

    # ═══════════════ المسح: MARS + الترند — القناص محذوف ═══════════════
    async def scan_volatile_coins(self):
        self._apply_sniper_cap()
        # ⚠️ القناص حُذف: لا استدعاء لـ super().scan_volatile_coins() —
        #    لا تحليل SMC ولا إشارات ولا دخول منه بعد اليوم.
        await self._mars_scan_cycle()
        if not self.trend.cfg.get('enabled') or self.EMERGENCY_MODE or not self.TRADE_ENABLED:
            return
        try:
            candidates = self._trend_candidates()
            if not candidates:
                return
            open_trend = sum(1 for t in self.active_trades.values() if t.get('strategy') == 'TREND')
            if open_trend >= self.trend_capacity or self._total_cap_hit():
                return
            sigs = await self.trend.scan(self, candidates, set(self.active_trades), self.trend_cooldown)
            if sigs:
                self._log_trend("SCAN", f"{len(sigs)} إشارة اختراق من {len(candidates)} زوجاً مفحوصاً")
            for a in sigs:
                await self._trend_execute(a)
                await asyncio.sleep(1)
        except Exception as e:
            self._notify_error("خطأ مسح استراتيجية الترند", exc=e)

    async def _mars_scan_cycle(self):
        if not self.mars.cfg.get('enabled') or self.EMERGENCY_MODE or not self.TRADE_ENABLED:
            return
        try:
            candidates = self._mars_candidates()
            if not candidates:
                return
            open_mars = sum(1 for t in self.active_trades.values() if t.get('strategy') == 'MARS')
            if open_mars >= self.mars_capacity or self._total_cap_hit():
                return
            sigs = await self.mars.scan(self, candidates, set(self.active_trades), self.mars_cooldown)
            if sigs:
                self._log_mars("SCAN", f"{len(sigs)} إشارة تقاطع من {len(candidates)} زوجاً مفحوصاً")
            for a in sigs:
                await self._mars_execute(a)
                await asyncio.sleep(1)
        except Exception as e:
            self._notify_error("خطأ مسح استراتيجية الموجات", exc=e)

    def _mars_candidates(self):
        """دوران على كل أزواج العقود حتى تُغطّى كلها داخل نافذة الدخول."""
        pairs = [p['symbol'] for p in self.all_futures_pairs]
        if not pairs:
            return []
        n = len(pairs)
        start = self._mars_cursor % n
        self._mars_cursor = (start + int(self.mars.cfg['scan_limit'])) % n
        out = []
        for k in range(min(int(self.mars.cfg['scan_limit']), n)):
            sym = pairs[(start + k) % n]
            if sym not in self.active_trades:
                out.append(sym)
        return out

    def _trend_candidates(self):
        """دوران على كل أزواج العقود حتى تُغطّى كلها داخل نافذة الدخول."""
        pairs = [p['symbol'] for p in self.all_futures_pairs]
        if not pairs:
            return []
        n = len(pairs)
        start = self._trend_cursor % n
        self._trend_cursor = (start + int(self.trend.cfg['scan_limit'])) % n
        out = []
        for k in range(min(int(self.trend.cfg['scan_limit']), n)):
            sym = pairs[(start + k) % n]
            if sym not in self.active_trades:
                out.append(sym)
        return out

    # ═══════════════ التنفيذ المستقل ═══════════════
    async def _mars_execute(self, analysis):
        sym = analysis['symbol']
        if sym in self.active_trades:
            return
        open_mars = sum(1 for t in self.active_trades.values() if t.get('strategy') == 'MARS')
        if open_mars >= self.mars_capacity:
            return
        if self._total_cap_hit(extra=1):
            return
        saved_cap = self.MAX_OPEN_TRADES
        saved_size = self.TRADE_SIZE_USDT
        mars_size = self.mars_trade_size
        # نسمح بفتح صفقة واحدة إضافية عبر المسار الأصلي (سعة MARS مستقلة)
        self.MAX_OPEN_TRADES = max(saved_cap, len(self.active_trades) + 1)
        self.TRADE_SIZE_USDT = mars_size
        try:
            await super().execute_trade(analysis)
        finally:
            self.MAX_OPEN_TRADES = saved_cap
            self.TRADE_SIZE_USDT = saved_size
        trade = self.active_trades.get(sym)
        if not trade or trade.get('strategy'):
            return
        trade['strategy'] = 'MARS'
        trade['margin_usdt'] = mars_size
        trade['atr_ref'] = analysis.get('atr_ref') or 0.0
        trade['tp2'] = None
        trade['components'] = analysis.get('components', {})
        await self.db.save_trade(trade)
        try:
            await self.mars_db.open(trade)
        except Exception as e:
            logger.warning(f"تعذر تسجيل صفقة الموجات: {e}")
        # فصل كامل: لا تُسجَّل صفقة الموجات في سجل إشارات القناص ولا في عدّاد يومه
        await self._detach_from_sniper_log(trade)
        self.mars_cooldown[sym] = time.time() + int(self.mars.cfg['reentry_cooldown'])
        self.stats_mars['trades'] += 1
        _risk = abs(analysis['price'] - analysis['sl'])
        self._log_mars("ENTRY", f"{sym} {analysis['direction']} @ {self.fmt_price(analysis['price'])} | "
                                f"وقف 3×ATR ({_risk / analysis['price'] * 100:.2f}%) | "
                                f"هدف 1R {self.fmt_price(analysis['tp1'])} | "
                                f"مخاطرة {_risk * (trade.get('quantity') or 0):.3f}$")
        await self.tg(f"🚀 *صفقة موجات 7/25/99 جديدة* (`{sym}`)\n"
                      f"الاتجاه: {analysis['direction']} | هامش {mars_size:.0f}$ | وقف 3×ATR(ساعة)\n"
                      f"🎯 هدف 1R: {self.fmt_price(analysis['tp1'])} | فلتر التقلب ≤6% مفعّل")

    async def _trend_execute(self, analysis):
        sym = analysis['symbol']
        if sym in self.active_trades:
            return
        open_trend = sum(1 for t in self.active_trades.values() if t.get('strategy') == 'TREND')
        if open_trend >= self.trend_capacity:
            return
        if self._total_cap_hit(extra=1):
            return
        saved_cap = self.MAX_OPEN_TRADES
        saved_size = self.TRADE_SIZE_USDT
        trend_size = self.trend_trade_size
        # نسمح بفتح صفقة واحدة إضافية عبر المسار الأصلي (سعة الترند مستقلة)
        self.MAX_OPEN_TRADES = max(saved_cap, len(self.active_trades) + 1)
        self.TRADE_SIZE_USDT = trend_size
        try:
            await super().execute_trade(analysis)
        finally:
            self.MAX_OPEN_TRADES = saved_cap
            self.TRADE_SIZE_USDT = saved_size
        trade = self.active_trades.get(sym)
        if not trade or trade.get('strategy'):
            return
        trade['strategy'] = 'TREND'
        trade['margin_usdt'] = trend_size
        trade['atr_ref'] = analysis.get('atr_ref') or 0.0
        trade['tp2'] = None
        trade['components'] = analysis.get('components', {})
        await self.db.save_trade(trade)
        try:
            await self.trend_db.open(trade)
        except Exception as e:
            logger.warning(f"تعذر تسجيل صفقة الترند: {e}")
        # فصل كامل: لا تُسجَّل صفقة الترند في سجل إشارات القناص ولا في عدّاد يومه
        await self._detach_from_sniper_log(trade)
        self.trend_cooldown[sym] = time.time() + int(self.trend.cfg['reentry_cooldown'])
        self.stats_trend['trades'] += 1
        _risk = abs(analysis['price'] - analysis['sl'])
        self._log_trend("ENTRY", f"{sym} {analysis['direction']} @ {self.fmt_price(analysis['price'])} | "
                                 f"وقف {self.fmt_price(analysis['sl'])} ({_risk / analysis['price'] * 100:.2f}%) | "
                                 f"TP1 {self.fmt_price(analysis['tp1'])} | مخاطرة {_risk * (trade.get('quantity') or 0):.3f}$")
        await self.tg(f"🚀 *صفقة ترند جديدة* (`{sym}`)\n"
                      f"الاتجاه: {analysis['direction']} | هامش {trend_size:.0f}$ | وقف ATR(1h)\n"
                      f"🎯 TP1: {self.fmt_price(analysis['tp1'])} ثم وقف متحرك 1×ATR")

    async def _detach_from_sniper_log(self, trade):
        """يحذف أثر الصفقة من جدول إشارات القناص ومن عدّاد صفقات اليوم."""
        try:
            entry = trade.get('entry_time') or 0
            if self.entry_history and self.entry_history[-1][0] >= entry - 1:
                self.entry_history.pop()
        except Exception:
            pass
        try:
            async with aiosqlite.connect(self.db.db_name) as db:
                await db.execute(
                    "DELETE FROM signal_log WHERE symbol=? AND entry_ts>=?",
                    (trade['symbol'], float(entry) - 1))
                await db.commit()
        except Exception as e:
            logger.warning(f"تعذر فصل سجل إشارات الصفقة: {e}")

    # ═══════════════ مصالحة واعية للترند والموجات ═══════════════
    async def reconcile(self):
        """المصالحة الأصلية + وعي كامل بالاستراتيجيتين:
        1) قبل المصالحة: أي مركز يتيم له سجل ترند أو موجات مفتوح يُتبنّى بصفقة
           استراتيجيته (بوقفه وهدفه وهامشه من قاعدتها) — ولا يتحول أبداً لصفقة قناص.
        2) بعد المصالحة: سجلات ميتة (مركزها أُغلق خارج البوت أثناء التوقف) تُغلق
           نهائياً حتى لا تعود شبحاً في كل إقلاع."""
        if not self.binance_api_key or not self.TRADE_ENABLED:
            await super().reconcile()
            return
        open_pos = {}
        try:
            positions = await self._fapi_request('GET', '/fapi/v2/positionRisk', signed=True)
            if isinstance(positions, list):
                for p in positions:
                    try:
                        amt = float(p.get('positionAmt', 0))
                    except (TypeError, ValueError):
                        continue
                    if abs(amt) > 0:
                        open_pos[p['symbol']] = {'amt': amt,
                                                 'entry': float(p.get('entryPrice', 0))}
        except Exception as e:
            logger.warning(f"⚠️ تعذّرت قراءة المراكز لتبنّي الصفقات: {e}")
        try:
            await self._adopt_trend_orphans(open_pos)
        except Exception as e:
            logger.warning(f"⚠️ خطأ تبنّي صفقات الترند: {e}")
        try:
            await self._adopt_mars_orphans(open_pos)
        except Exception as e:
            logger.warning(f"⚠️ خطأ تبنّي صفقات الموجات: {e}")
        await super().reconcile()
        try:
            await self._close_stale_trend_rows(open_pos)
        except Exception as e:
            logger.warning(f"⚠️ خطأ تنظيف سجلات الترند الميتة: {e}")
        try:
            await self._close_stale_mars_rows(open_pos)
        except Exception as e:
            logger.warning(f"⚠️ خطأ تنظيف سجلات الموجات الميتة: {e}")

    async def _adopt_trend_orphans(self, open_pos):
        """تبنّي المراكز اليتيمة التي لها سجل ترند مفتوح — بصفقاتها الكاملة."""
        rows = await self.trend_db.open_symbols()
        adopted = []
        for sym, row in rows.items():
            if sym in self.active_trades or sym not in open_pos:
                continue
            pos = open_pos[sym]
            step = self.step_sizes_cache.get(sym) or 1.0
            if abs(pos['amt']) < step:
                continue
            entry = float(row.get('entry') or 0) or float(pos.get('entry') or 0)
            if entry <= 0:
                continue
            side = 'BUY' if pos['amt'] > 0 else 'SELL'
            atr = float(row.get('atr') or 0)
            sl = float(row.get('sl') or 0)
            if sl <= 0:
                sl = entry - 2.5 * atr if side == 'BUY' else entry + 2.5 * atr
            tp1 = float(row.get('tp1') or 0)
            if tp1 <= 0 and atr > 0:
                tp1 = entry + 0.9 * 2.5 * atr if side == 'BUY' else entry - 0.9 * 2.5 * atr
            trade = {
                'symbol': sym, 'side': side, 'entry_price': entry,
                'quantity': abs(pos['amt']), 'sl': sl, 'tp': tp1 or None, 'tp2': None,
                'trailing_active': False, 'highest_price': entry, 'lowest_price': entry,
                'entry_time': float(row.get('entry_ts') or time.time()),
                'partial_closed': False, 'realized_pnl': 0.0,
                'stop_order_id': None, 'tp_order_id': None,
                'stop_is_algo': False, 'tp_is_algo': False,
                'stop_synced_price': None, 'tp_skipped': False,
                'strategy': 'TREND', 'atr_ref': atr,
                'margin_usdt': float(row.get('margin') or 0) or self.trend_trade_size,
                'components': {'strategy': 'TREND', 'trigger': 'تبنّي بعد إعادة تشغيل'},
            }
            self.active_trades[sym] = trade
            await self.db.save_trade(trade)
            try:
                await self._sync_stop_order(trade, entry)
            except Exception:
                pass
            adopted.append(sym)
            logger.info(f"🔄 تبنّي ترند: {sym} {side} @ {self.fmt_price(entry)} "
                        f"(وقف/هدف/هامش من قاعدة الترند)")
        if adopted:
            await self.tg("🔄 *تبنّي ترند*\n"
                          + "، ".join(f"`{s}`" for s in adopted)
                          + "\nاستُعيدت بوقفها وهدفها وهامشها من قاعدة الترند — ستظهر في لوحة الترند")

    async def _adopt_mars_orphans(self, open_pos):
        """تبنّي المراكز اليتيمة التي لها سجل موجات مفتوح — بصفقاتها الكاملة."""
        rows = await self.mars_db.open_symbols()
        adopted = []
        for sym, row in rows.items():
            if sym in self.active_trades or sym not in open_pos:
                continue
            pos = open_pos[sym]
            step = self.step_sizes_cache.get(sym) or 1.0
            if abs(pos['amt']) < step:
                continue
            entry = float(row.get('entry') or 0) or float(pos.get('entry') or 0)
            if entry <= 0:
                continue
            side = 'BUY' if pos['amt'] > 0 else 'SELL'
            atr = float(row.get('atr') or 0)
            sl_atr = float(self.mars.cfg.get('sl_atr1h', 3.0)) or 3.0
            tp_r = float(self.mars.cfg.get('tp_r', 1.0)) or 1.0
            sl = float(row.get('sl') or 0)
            if sl <= 0:
                sl = entry - sl_atr * atr if side == 'BUY' else entry + sl_atr * atr
            tp1 = float(row.get('tp1') or 0)
            if tp1 <= 0 and atr > 0:
                tp1 = entry + tp_r * sl_atr * atr if side == 'BUY' else entry - tp_r * sl_atr * atr
            trade = {
                'symbol': sym, 'side': side, 'entry_price': entry,
                'quantity': abs(pos['amt']), 'sl': sl, 'tp': tp1 or None, 'tp2': None,
                'trailing_active': False, 'highest_price': entry, 'lowest_price': entry,
                'entry_time': float(row.get('entry_ts') or time.time()),
                'partial_closed': False, 'realized_pnl': 0.0,
                'stop_order_id': None, 'tp_order_id': None,
                'stop_is_algo': False, 'tp_is_algo': False,
                'stop_synced_price': None, 'tp_skipped': False,
                'strategy': 'MARS', 'atr_ref': atr,
                'margin_usdt': float(row.get('margin') or 0) or self.mars_trade_size,
                'components': {'strategy': 'MARS', 'trigger': 'تبنّي بعد إعادة تشغيل'},
            }
            self.active_trades[sym] = trade
            await self.db.save_trade(trade)
            try:
                await self._sync_stop_order(trade, entry)
            except Exception:
                pass
            adopted.append(sym)
            logger.info(f"🔄 تبنّي موجات: {sym} {side} @ {self.fmt_price(entry)} "
                        f"(وقف/هدف/هامش من قاعدة الموجات)")
        if adopted:
            await self.tg("🔄 *تبنّي موجات 7/25/99*\n"
                          + "، ".join(f"`{s}`" for s in adopted)
                          + "\nاستُعيدت بوقفها وهدفها وهامشها من قاعدة الموجات — ستظهر في لوحة MARS")

    async def _close_stale_trend_rows(self, open_pos):
        """سجل ترند مفتوح بلا مركز على المنصة وبلا صفقة حية → انتهى فعلاً."""
        rows = await self.trend_db.open_symbols()
        for sym, row in rows.items():
            if sym in self.active_trades:
                continue
            pos = open_pos.get(sym)
            step = self.step_sizes_cache.get(sym) or 1.0
            if pos and abs(pos['amt']) >= step:
                continue   # المركز حي — مسؤوليته المصالحة/التبني
            fake = {'symbol': sym, 'entry_time': float(row.get('entry_ts') or 0)}
            try:
                pnl = await self.get_last_realized_pnl(sym, fake)
            except Exception:
                pnl = None
            if pnl is None:
                pnl = 0.0
            await self.trend_db.close(sym, time.time(), round(pnl, 4), 0.0,
                                      pnl > 0, '🔄 أُغلق مركزه خارج البوت أثناء التوقف')
            logger.info(f"🧹 سجل ترند ميت نُظّف: {sym} ({pnl:+.4f}$)")

    async def _close_stale_mars_rows(self, open_pos):
        """سجل موجات مفتوح بلا مركز على المنصة وبلا صفقة حية → انتهى فعلاً."""
        rows = await self.mars_db.open_symbols()
        for sym, row in rows.items():
            if sym in self.active_trades:
                continue
            pos = open_pos.get(sym)
            step = self.step_sizes_cache.get(sym) or 1.0
            if pos and abs(pos['amt']) >= step:
                continue   # المركز حي — مسؤوليته المصالحة/التبني
            fake = {'symbol': sym, 'entry_time': float(row.get('entry_ts') or 0)}
            try:
                pnl = await self.get_last_realized_pnl(sym, fake)
            except Exception:
                pnl = None
            if pnl is None:
                pnl = 0.0
            await self.mars_db.close(sym, time.time(), round(pnl, 4), 0.0,
                                     pnl > 0, '🔄 أُغلق مركزه خارج البوت أثناء التوقف')
            logger.info(f"🧹 سجل موجات ميت نُظّف: {sym} ({pnl:+.4f}$)")

    # ═══════════════ موجّه الإغلاق المركزي ═══════════════
    async def _finalize_trade(self, trade, fill_price, reason, pnl_override=None):
        """أي مسار إغلاق (تحقق المراكز، إغلاق شامل، مصالحة، إلخ) يمر من هنا:
        كل صفقة تُغلق بمحاسبة استراتيجيتها — ولا تعود إحصاءاتها لغيرها."""
        if trade.get('strategy') == 'MARS':
            return await self._finalize_mars(trade, fill_price, reason, pnl_override)
        if trade.get('strategy') == 'TREND':
            return await self._finalize_trend(trade, fill_price, reason, pnl_override)
        return await super()._finalize_trade(trade, fill_price, reason, pnl_override)

    # ═══════════════ المراقبة: كل استراتيجية بقواعدها ═══════════════
    async def monitor_trades(self):
        mars_syms = [s for s, t in list(self.active_trades.items()) if t.get('strategy') == 'MARS']
        trend_syms = [s for s, t in list(self.active_trades.items()) if t.get('strategy') == 'TREND']
        held = {}
        for s in mars_syms + trend_syms:
            held[s] = self.active_trades.pop(s)
        try:
            # صفقات القناص القديمة المتبقية فقط تُمرَّر لمسار القناص الأصلي
            await super().monitor_trades()
        finally:
            self.active_trades.update(held)
        if mars_syms:
            await self._mars_monitor(mars_syms)
        if trend_syms:
            await self._trend_monitor(trend_syms)

    async def _mars_monitor(self, symbols):
        for sym in symbols:
            trade = self.active_trades.get(sym)
            if not trade:
                continue
            prices = self.get_price(sym)
            if not prices:
                continue
            is_buy = trade['side'] == 'BUY'
            price = prices['bid'] if is_buy else prices['ask']
            if is_buy and price > trade.get('highest_price', 0):
                trade['highest_price'] = price
            elif (not is_buy) and price < trade.get('lowest_price', 999999):
                trade['lowest_price'] = price

            decision = self.mars_exit.decide(trade, price)
            act = decision.get('action')
            if act == 'close':
                ok, fill, pnl_over = await self._close_position(trade, price)
                if ok:
                    await self._finalize_mars(trade, fill, decision['reason'], pnl_over)
                    continue
            # مزامنة وقف المنصة (لا تكلفة إذا كان مُزامَناً — حماية إضافية فقط)
            try:
                await self._sync_stop_order(trade, price)
            except Exception:
                pass
            await self.db.save_trade(trade)

    async def _trend_monitor(self, symbols):
        for sym in symbols:
            trade = self.active_trades.get(sym)
            if not trade:
                continue
            prices = self.get_price(sym)
            if not prices:
                continue
            is_buy = trade['side'] == 'BUY'
            price = prices['bid'] if is_buy else prices['ask']
            if is_buy and price > trade.get('highest_price', 0):
                trade['highest_price'] = price
            elif (not is_buy) and price < trade.get('lowest_price', 999999):
                trade['lowest_price'] = price

            decision = self.trend_exit.decide(trade, price)
            act = decision.get('action')
            if act == 'close':
                ok, fill, pnl_over = await self._close_position(trade, price)
                if ok:
                    await self._finalize_trend(trade, fill, decision['reason'], pnl_over)
            elif act == 'partial':
                await self._trend_partial(trade, price)
            elif act == 'move_sl':
                new_sl = decision['sl']
                if (is_buy and new_sl > trade['sl']) or ((not is_buy) and new_sl < trade['sl']):
                    self._log_trend("TRAIL", f"{sym} وقف متحرك: {self.fmt_price(trade['sl'])} → "
                                             f"{self.fmt_price(new_sl)}")
                    trade['sl'] = new_sl
                    await self.db.save_trade(trade)
                    await self.trend_db.update_sl(sym, new_sl)
                    await self._sync_stop_order(trade, price)
            await self.db.save_trade(trade)

    async def _trend_partial(self, trade, price):
        """جني 70% عند TP1 ثم نقل الوقف للتعادل — قواعد خاصة بالترند."""
        sym = trade['symbol']
        is_buy = trade['side'] == 'BUY'
        frac = float(self.trend.cfg['partial'])
        qty = self.format_quantity(sym, trade['quantity'] * frac)
        rem = self.format_quantity(sym, trade['quantity'] - qty)
        min_notional = self.min_notional_cache.get(sym, 5.0)
        if qty <= 0 or rem <= 0 or qty * price < min_notional or rem * price < min_notional:
            ok, fill, pnl_over = await self._close_position(trade, price)
            if ok:
                await self._finalize_trend(trade, fill, "🎯 TP1 (إغلاق كامل — حدود الزوج)", pnl_over)
            return
        res = await self._fapi_request('POST', '/fapi/v1/order', {
            'symbol': sym, 'side': 'SELL' if is_buy else 'BUY', 'type': 'MARKET',
            'quantity': self.qty_to_str(sym, qty), 'reduceOnly': 'true'}, signed=True)
        if not res or res.get('status') not in ('FILLED', 'NEW'):
            self._notify_error(f"فشل الجني الجزئي (ترند) لـ {sym}")
            return
        fill = float(res.get('avgPrice') or 0) or price
        part_pnl = ((fill - trade['entry_price']) if is_buy else (trade['entry_price'] - fill)) * qty
        trade['realized_pnl'] = trade.get('realized_pnl', 0.0) + part_pnl
        await self.db.update_daily_pnl(part_pnl, None)
        trade['quantity'] = rem
        trade['partial_closed'] = True
        be = float(self.trend.cfg.get('be_offset', 0.002))
        trade['sl'] = trade['entry_price'] * (1 + be) if is_buy else trade['entry_price'] * (1 - be)
        await self.db.save_trade(trade)
        await self.trend_db.update_sl(sym, trade['sl'])
        await self._sync_stop_order(trade, price)
        _pc = float(self.trend.cfg['partial']) * 100
        self._log_trend("PARTIAL", f"{sym} جني {_pc:.0f}% عند TP1 — ربح محقق {part_pnl:+.4f}$ | "
                                   f"الوقف إلى التعادل {self.fmt_price(trade['sl'])}")
        await self.tg(f"🎯 *جني ترند* (`{sym}`)\n💸 أُغلق {_pc:.0f}% بربح `{part_pnl:.4f} USDT`\n"
                      f"🛡️ الوقف للتعادل ثم وقف متحرك {self.trend.cfg['trail_atr']}×ATR(1h)")

    async def _finalize_mars(self, trade, fill_price, reason, pnl_override=None):
        is_buy = trade['side'] == 'BUY'
        if pnl_override is not None:
            final = float(pnl_override)
        else:
            final = ((fill_price - trade['entry_price']) if is_buy
                     else (trade['entry_price'] - fill_price)) * trade['quantity']
        total = trade.get('realized_pnl', 0.0) + final
        margin_used = float(trade.get('margin_usdt') or self.TRADE_SIZE_USDT or 0)
        pct = total / margin_used * 100 if margin_used else 0
        win = total > 0

        w0, l0 = self.stats['wins'], self.stats['losses']
        saved = self.tuner
        self.tuner = _NullTuner()
        # تعطيل كتابة القناص في daily_stats/signal_log أثناء إغلاق صفقة الموجات
        set_sig, upd_daily = self.db.set_signal_result, self.db.update_daily_pnl

        async def _noop(*a, **k):
            return None

        self.db.set_signal_result = _noop
        self.db.update_daily_pnl = _noop
        saved_size = self.TRADE_SIZE_USDT
        if margin_used > 0:
            self.TRADE_SIZE_USDT = margin_used   # نسبة الربح تُحسب من هامش الموجات نفسه
        try:
            await super()._finalize_trade(trade, fill_price, reason, pnl_override)
        finally:
            self.tuner = saved
            self.TRADE_SIZE_USDT = saved_size
            self.db.set_signal_result = set_sig
            self.db.update_daily_pnl = upd_daily
        # فصل إحصاءات الموجات عن إحصاءات القناص
        self.stats['wins'], self.stats['losses'] = w0, l0
        if win:
            self.stats_mars['wins'] += 1
        else:
            self.stats_mars['losses'] += 1
        try:
            await self.mars_db.close(trade['symbol'], time.time(), total, round(pct, 2), win, reason)
        except Exception as e:
            logger.warning(f"تعذر إغلاق سجل الموجات: {e}")
        logger.info(f"🏁 موجات: {trade['symbol']} {total:+.3f} USDT ({pct:+.1f}%) — {reason}")
        self._log_mars("CLOSE", f"{trade['symbol']} {trade['side']} أُغلقت {total:+.4f}$ ({pct:+.1f}%) — {reason}")

    async def _finalize_trend(self, trade, fill_price, reason, pnl_override=None):
        is_buy = trade['side'] == 'BUY'
        if pnl_override is not None:
            final = float(pnl_override)
        else:
            final = ((fill_price - trade['entry_price']) if is_buy
                     else (trade['entry_price'] - fill_price)) * trade['quantity']
        total = trade.get('realized_pnl', 0.0) + final
        margin_used = float(trade.get('margin_usdt') or self.TRADE_SIZE_USDT or 0)
        pct = total / margin_used * 100 if margin_used else 0
        win = total > 0

        w0, l0 = self.stats['wins'], self.stats['losses']
        saved = self.tuner
        self.tuner = _NullTuner()
        # تعطيل كتابة القناص في daily_stats/signal_log أثناء إغلاق صفقة الترند
        set_sig, upd_daily = self.db.set_signal_result, self.db.update_daily_pnl

        async def _noop(*a, **k):
            return None

        self.db.set_signal_result = _noop
        self.db.update_daily_pnl = _noop
        saved_size = self.TRADE_SIZE_USDT
        if margin_used > 0:
            self.TRADE_SIZE_USDT = margin_used   # نسبة الربح تُحسب من هامش الترند نفسه
        try:
            await super()._finalize_trade(trade, fill_price, reason, pnl_override)
        finally:
            self.tuner = saved
            self.TRADE_SIZE_USDT = saved_size
            self.db.set_signal_result = set_sig
            self.db.update_daily_pnl = upd_daily
        # فصل إحصاءات الترند عن إحصاءات القناص
        self.stats['wins'], self.stats['losses'] = w0, l0
        if win:
            self.stats_trend['wins'] += 1
        else:
            self.stats_trend['losses'] += 1
        try:
            await self.trend_db.close(trade['symbol'], time.time(), total, round(pct, 2), win, reason)
        except Exception as e:
            logger.warning(f"تعذر إغلاق سجل الترند: {e}")
        logger.info(f"🏁 ترند: {trade['symbol']} {total:+.3f} USDT ({pct:+.1f}%) — {reason}")
        self._log_trend("CLOSE", f"{trade['symbol']} {trade['side']} أُغلقت {total:+.4f}$ ({pct:+.1f}%) — {reason}")


# ═══════════════ نقطة التشغيل ═══════════════
if __name__ == "__main__":
    bot = MarsBotV9()
    bot.start()
