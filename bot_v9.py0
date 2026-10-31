"""
═══════════════════════════════════════════════════════════════════════
  📐 موجات 7/25/99 V9 — بوت باستراتيجية واحدة فقط
═══════════════════════════════════════════════════════════════════════
  ✅ استراتيجية القناص (Sweep/Retest/ستوكاستك) محذوفة نهائياً:
     · لا مسح قناص (scan_volatile_coins لا يستدعي محرك القناص إطلاقاً)
     · لا تحليل حوت (analyze_whale_zone مُعطَّل ويعيد None دائماً)
     · المطوّر التكيفي الخاص بالقناص معطّل (بديل صامت _DeadTuner)
     · لا لوحة للقناص — لوحة واحدة فقط لاستراتيجية الموجات على "/"
  ✅ الاستراتيجية الوحيدة: «موجات 7/25/99» (strategy_mars.py)
     — التركيبة المعدلة التي أثبتت فوز 55.20% في فترة التحقق المستقلة:
       شراء: تقاطع MA7 صعوداً ضمن آخر 6 شمعات 15د + إغلاق بزخم فوق MA7/MA25
       بيع : تقاطع MA7 هبوطاً ضمن آخر 3 شمعات ساعة + إغلاق بزخم تحت MA7/MA25
       وقف 1.5×ATR(ساعة) | هدف 2R | فلتر مخاطرة 8% | بلا جني جزئي
  · محرك التنفيذ (الأوامر/الستوب/المصالحة/الويب سوكيت/القاعدة) من bot.py كما هو —
    لكن كل مسار إشارة أو محاسبة للقناص مُعطَّل أو موجَّه للموجات.
  · كل صفقة تُوسم MARS وتُدار بـ MaRsiExitManager وتُحاسب في mars_trades/mars_daily.
  · لوحة واحدة: http://HOST:PORT/  (الرئيسية · ربح اليوم · المفتوحة · السجل · التحكم)
  · التشغيل: python3 bot_v9.py
═══════════════════════════════════════════════════════════════════════
"""
import asyncio
import json
import logging
import math
import os
import time
from collections import deque

import aiosqlite

import bot as botmod                      # محرك التنفيذ كما هو (الأوامر والستوب والمصالحة)
import web_panel_mars                     # لوحة «موجات 7/25/99» — اللوحة الوحيدة
from strategy_mars import (MaRsiExitManager, MaRsiStrategy, MarsDB)

logger = logging.getLogger('MarsV9')

# سعة صفقات الموجات المتزامنة (مستقلة)
MAX_OPEN_TRADES_MARS = int(os.environ.get('MAX_OPEN_TRADES_MARS', '5'))
# سقف إجمالي صارم لكل الصفقات المفتوحة (0 = بلا سقف)
MAX_TOTAL_TRADES = int(os.environ.get('MAX_TOTAL_TRADES', '0'))
MARS_ENABLED = os.environ.get('STRATEGY_MARS_ENABLED', 'true').lower() == 'true'
# هامش صفقة الموجات (0 = يستخدم TRADE_SIZE_USDT المشترك نفسه)
MARS_TRADE_SIZE_USDT = float(os.environ.get('TRADE_SIZE_USDT_MARS', '0'))


class _DeadTuner:
    """بديل صامت كامل: القناص ومطوّره التكيفي معطّلان — لا تعلّم ولا رسائل."""

    results = []

    async def load(self):
        return None

    async def save(self):
        return None

    def record(self, *a, **k):
        return None

    def describe(self):
        return "معطّل (استراتيجية موجات 7/25/99 بلا مطوّر تكيفي)"

    def recent_winrate(self, *a, **k):
        return None

    def relax_step(self):
        return False

    def tighten_step(self):
        return False


class MarsBotV9(botmod.LegendarySniperFuturesV8):
    """محرك bot.py + استراتيجية موجات 7/25/99 فقط — القناص محذوف."""

    def __init__(self):
        super().__init__()
        # ✅ مسار قاعدة البيانات من متغير البيئة (مثال Railway: DB_FILE=/data/sniper_v8.db)
        db_file = os.environ.get('DB_FILE')
        if db_file:
            self.db.db_name = db_file
        # ✅ تعطيل المطوّر التكيفي الخاص بالقناص نهائياً (قبل tuner.load في الإقلاع)
        self.tuner = _DeadTuner()
        # ✅ الاستراتيجية الوحيدة: موجات 7/25/99
        self.mars = MaRsiStrategy({"enabled": MARS_ENABLED}, logger.warning)
        self.mars_exit = MaRsiExitManager(logger=logger.warning)
        self.mars_db = MarsDB(self.db.db_name)
        self.mars_cooldown = {}
        self._mars_cursor = 0
        self.stats_mars = {"wins": 0, "losses": 0, "trades": 0}
        self.mars_events = deque(maxlen=300)   # سجل حيّ لكل حركة (تبويب الحركات)
        # أرقام تعرضها اللوحة
        self.mars_capacity = MAX_OPEN_TRADES_MARS
        self.total_cap = MAX_TOTAL_TRADES
        self.mars_trade_size = MARS_TRADE_SIZE_USDT if MARS_TRADE_SIZE_USDT > 0 else self.TRADE_SIZE_USDT

    # ═══════════════ أدوات مساعدة ═══════════════
    def _log_mars(self, kind, msg):
        """تسجيل حركة في سجل الموجات (يظهر في اللوحة)."""
        try:
            self.mars_events.append({"ts": time.time(), "kind": kind, "msg": msg})
        except Exception:
            pass

    def _mars_open(self):
        return {s: t for s, t in self.active_trades.items() if t.get('strategy') == 'MARS'}

    def _total_cap_hit(self, extra=0):
        if MAX_TOTAL_TRADES <= 0:
            return False
        return len(self.active_trades) + extra > MAX_TOTAL_TRADES

    async def tg(self, msg):
        """تصفية رسالة إقلاع القناص القديمة + تمرير كل ما عداها."""
        try:
            if 'القناص الأسطوري' in msg:
                return
        except Exception:
            pass
        await super().tg(msg)

    # ═══════════════ القناص: مُعطَّل بأمان كامل ═══════════════
    async def analyze_whale_zone(self, symbol):
        """⚠️ القناص محذوف — لا تحليل حوت ولا Sweep/Retest. يعيد None دائماً."""
        return None

    def _frequency_guard(self):
        """⚠️ حارس التردد/الفوز خاص بالقناص — معطّل."""
        return None

    # ═══════════════ الإقلاع ═══════════════
    async def _mars_open_rows(self):
        """صفوف الموجات المفتوحة (win=-1) بأمان — مع إعادة محاولة وتهيئة القاعدة."""
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
        logger.error(f"❌ تعذّرت قراءة صفقات الموجات المفتوحة ({last_err}) — سيتولّى مسار التبنّي في المصالحة")
        return {}

    async def main_loop(self):
        try:
            await self.mars_db.init()
        except Exception as e:
            logger.error(f"تعذر تهيئة قاعدة بيانات الموجات: {e}")

        # تحميل إعدادات الموجات المحفوظة من اللوحة (تنجو من إعادة التشغيل والنشر)
        try:
            await self.db.init_db()
        except Exception:
            pass
        try:
            raw = await self.db.get_param('mars_config')
            if raw:
                saved = json.loads(raw)
                self.mars.cfg.update({k: v for k, v in saved.items() if k in self.mars.cfg})
                self.mars_exit.cfg.update(self.mars.cfg)
                self.mars_capacity = int(self.mars.cfg.get('max_open_trades', self.mars_capacity))
                logger.info(f"⚙️ إعدادات الموجات محمّلة من القاعدة — سعة {self.mars_capacity} صفقة، "
                            f"الحالة: {'مفعّلة' if self.mars.cfg.get('enabled') else 'متوقفة'}")
        except Exception as e:
            logger.warning(f"تعذر تحميل إعدادات الموجات المحفوظة: {e}")

        orig_load = self.db.load_active_trades

        async def _load_with_mars():
            trades = await orig_load()
            open_mars = await self._mars_open_rows()
            restored = 0
            for sym, row in open_mars.items():
                if sym in trades:
                    trades[sym]['strategy'] = 'MARS'
                    trades[sym]['atr_ref'] = row.get('atr') or 0.0
                    trades[sym]['tp2'] = None
                    trades[sym]['components'] = {'strategy': 'MARS'}
                    m = float(row.get('margin') or 0)
                    trades[sym]['margin_usdt'] = m if m > 0 else self.mars_trade_size
                    restored += 1
                    logger.info(f"♻️ استُعيدت صفقة موجات مفتوحة: {sym}")
            if open_mars and not restored:
                logger.warning(f"⚠️ {len(open_mars)} سجل موجات مفتوح بلا صفقة حية مطابقة — "
                               f"سيتبنّاها مسار التبنّي الواعي في المصالحة")
            return trades

        self.db.load_active_trades = _load_with_mars

        # ✅ لوحة الموجات فقط — لا توجد أي لوحة للقناص
        botmod.start_web_panel = web_panel_mars.start_web_panel_mars
        await super().main_loop()

    # ═══════════════ المسح: موجات 7/25/99 فقط ═══════════════
    async def scan_volatile_coins(self):
        """لا super() هنا — القناص محذوف. مسح الموجات فقط على دوران كامل الأزواج."""
        if not self.mars.cfg.get('enabled') or self.EMERGENCY_MODE or not self.TRADE_ENABLED:
            return
        try:
            candidates = self._mars_candidates()
            if not candidates:
                return
            if len(self._mars_open()) >= self.mars_capacity or self._total_cap_hit():
                return
            sigs = await self.mars.scan(self, candidates, set(self.active_trades), self.mars_cooldown)
            # تتبّع دورة المسح — يظهر في نبض اللوحة
            self.last_scan_info = {'ts': time.time(), 'volatile': len(candidates),
                                   'scanned': len(candidates), 'signals': len(sigs)}
            if sigs:
                self._log_mars("SCAN", f"{len(sigs)} إشارة موجات من {len(candidates)} زوجاً مفحوصاً")
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

    # ═══════════════ التنفيذ ═══════════════
    async def _mars_execute(self, analysis):
        sym = analysis['symbol']
        if sym in self.active_trades:
            return
        if len(self._mars_open()) >= self.mars_capacity:
            return
        if self._total_cap_hit(extra=1):
            return
        saved_cap = self.MAX_OPEN_TRADES
        saved_size = self.TRADE_SIZE_USDT
        mars_size = MARS_TRADE_SIZE_USDT if MARS_TRADE_SIZE_USDT > 0 else saved_size
        # نسمح بفتح صفقة واحدة إضافية عبر المسار الأصلي (سعة الموجات مستقلة)
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
        # فصل السجل: لا تُوسم صفقة الموجات في إشارات القناص القديمة
        await self._detach_from_legacy_log(trade)
        self.mars_cooldown[sym] = time.time() + int(self.mars.cfg['reentry_cooldown'])
        self.stats_mars['trades'] += 1
        _risk = abs(analysis['price'] - analysis['sl'])
        self._log_mars("ENTRY", f"{sym} {analysis['direction']} @ {self.fmt_price(analysis['price'])} | "
                                f"وقف {self.fmt_price(analysis['sl'])} ({_risk / analysis['price'] * 100:.2f}%) | "
                                f"هدف {self.fmt_price(analysis['tp1'])} (2R) | مخاطرة {_risk * (trade.get('quantity') or 0):.3f}$")
        await self.tg(f"🚀 *صفقة موجات جديدة* (`{sym}`)\n"
                      f"الاتجاه: {analysis['direction']} | هامش {mars_size:.0f}$ | وقف 1.5×ATR(ساعة)\n"
                      f"🎯 الهدف: {self.fmt_price(analysis['tp1'])} (2R — بلا جني جزئي)")

    async def _detach_from_legacy_log(self, trade):
        """يحذف أثر صفقة الموجات من جدول إشارات القناص القديم ومن عدّاد اليوم."""
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
            logger.warning(f"تعذر فصل سجل الإشارات القديم: {e}")

    # ═══════════════ مصالحة واعية للموجات ═══════════════
    async def reconcile(self):
        """المصالحة الأصلية + وعي كامل بالموجات:
        1) قبل المصالحة: كل مركز يتيم يُتبنّى كصفقة موجات — له سجل مفتوح
           أُعيدت هويته كاملة، وبلا سجل أُنشئ له وقف 1.5×ATR(ساعة) وهدف 2R —
           ولا يتحول أبداً لصفقة قناص بقواعدها القديمة.
        2) بعد المصالحة: سجلات موجات ميتة (مركزها أُغلق خارج البوت) تُغلق نهائياً."""
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
            logger.warning(f"⚠️ تعذّرت قراءة المراكز لتبنّي الموجات: {e}")
        try:
            await self._adopt_mars_orphans(open_pos)
        except Exception as e:
            logger.warning(f"⚠️ خطأ تبنّي صفقات الموجات: {e}")
        await super().reconcile()
        try:
            await self._close_stale_mars_rows(open_pos)
        except Exception as e:
            logger.warning(f"⚠️ خطأ تنظيف سجلات الموجات الميتة: {e}")

    async def _atr_1h_fallback(self, symbol, entry):
        """ATR(1h) احتياطي لتبنّي مركز بلا سجل."""
        try:
            df = await self.get_klines(symbol, '1h', 120)
            if df is not None and len(df) > 20:
                a = float(self._compute_atr(df))
                if a > 0 and not math.isnan(a):
                    return a
        except Exception:
            pass
        return entry * 0.01   # احتياط: 1% من سعر صالح

    async def _adopt_mars_orphans(self, open_pos):
        """تبنّي كل مركز يتيم كصفقة موجات بهويتها أو بقواعد الموجات نفسها."""
        rows = await self.mars_db.open_symbols()
        adopted = []
        for sym, pos in open_pos.items():
            if sym in self.active_trades:
                continue
            step = self.step_sizes_cache.get(sym) or 1.0
            if abs(pos['amt']) < step:
                continue
            row = rows.get(sym)
            side = 'BUY' if pos['amt'] > 0 else 'SELL'
            entry = float((row or {}).get('entry') or 0) or float(pos.get('entry') or 0)
            if entry <= 0:
                await self.tg(f"⚠️ *تعذّر تبنّي مركز يتيم* (`{sym}`)\n"
                              f"سعر الدخول غير متاح بعد — سيُعاد في إعادة تشغيل قادمة")
                continue
            atr = float((row or {}).get('atr') or 0)
            if atr <= 0:
                atr = await self._atr_1h_fallback(sym, entry)
            sl = float((row or {}).get('sl') or 0)
            if sl <= 0:
                sl = entry - 1.5 * atr if side == 'BUY' else entry + 1.5 * atr
            tp = float((row or {}).get('tp1') or 0)
            if tp <= 0:
                tp = entry + 3.0 * atr if side == 'BUY' else entry - 3.0 * atr
            trade = {
                'symbol': sym, 'side': side, 'entry_price': entry,
                'quantity': abs(pos['amt']), 'sl': sl, 'tp': tp, 'tp2': None,
                'trailing_active': False, 'highest_price': entry, 'lowest_price': entry,
                'entry_time': float((row or {}).get('entry_ts') or time.time()),
                'partial_closed': False, 'realized_pnl': 0.0,
                'stop_order_id': None, 'tp_order_id': None,
                'stop_is_algo': False, 'tp_is_algo': False,
                'stop_synced_price': None, 'tp_skipped': False,
                'strategy': 'MARS', 'atr_ref': atr,
                'margin_usdt': float((row or {}).get('margin') or 0) or self.mars_trade_size,
                'components': {'strategy': 'MARS', 'trigger': 'تبنّي بعد إعادة تشغيل'},
            }
            self.active_trades[sym] = trade
            await self.db.save_trade(trade)
            try:
                await self._sync_stop_order(trade, entry)
            except Exception:
                pass
            try:
                await self.mars_db.open(trade)   # يضمن وجود سجل موحد (INSERT OR REPLACE)
            except Exception as e:
                logger.warning(f"تعذر حفظ سجل تبنّي الموجات لـ {sym}: {e}")
            adopted.append(sym)
            logger.info(f"🔄 تبنّي موجات: {sym} {side} @ {self.fmt_price(entry)} "
                        f"(وقف 1.5×ATR وهدف 2R)")
        if adopted:
            await self.tg("🔄 *تبنّي موجات*\n"
                          + "، ".join(f"`{s}`" for s in adopted)
                          + "\nاستُعيدت بوقف 1.5×ATR وهدف 2R — تظهر في لوحة الموجات")

    async def _close_stale_mars_rows(self, open_pos):
        """سجل موجات مفتوح بلا مركز على المنصة وبلا صفقة حية → انتهى فعلاً."""
        rows = await self.mars_db.open_symbols()
        for sym, row in rows.items():
            if sym in self.active_trades:
                continue
            pos = open_pos.get(sym)
            step = self.step_sizes_cache.get(sym) or 1.0
            if pos and abs(pos['amt']) >= step:
                continue   # المركز حي — مسؤوليته التبنّي
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
        """كل مسار إغلاق يمر من هنا: صفقة الموجات تُحاسب محاسبة الموجات دائماً."""
        if trade.get('strategy') == 'MARS':
            return await self._finalize_mars(trade, fill_price, reason, pnl_override)
        return await super()._finalize_trade(trade, fill_price, reason, pnl_override)

    # ═══════════════ المراقبة: قواعد الموجات فقط ═══════════════
    async def monitor_trades(self):
        mars_syms = [s for s, t in list(self.active_trades.items()) if t.get('strategy') == 'MARS']
        if mars_syms:
            held = {}
            for s in mars_syms:
                held[s] = self.active_trades.pop(s)
            try:
                await super().monitor_trades()
            finally:
                self.active_trades.update(held)
        else:
            await super().monitor_trades()
        if mars_syms:
            await self._mars_monitor(mars_syms)

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
                    continue   # ✅ أُغلقت وحُذفت من القاعدة — لا تُحفظ من جديد (لا صفقة شبح)
            elif act == 'move_sl':          # احتياط (قواعد الموجات لا تُحرّك الوقف)
                new_sl = decision['sl']
                if (is_buy and new_sl > trade['sl']) or ((not is_buy) and new_sl < trade['sl']):
                    self._log_mars("SL", f"{sym} تحديث الوقف: {self.fmt_price(new_sl)}")
                    trade['sl'] = new_sl
                    await self.db.save_trade(trade)
                    await self.mars_db.update_sl(sym, new_sl)
                    await self._sync_stop_order(trade, price)
            await self.db.save_trade(trade)

    # ═══════════════ محاسبة إغلاق الموجات ═══════════════
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
        # تعطيل كتابة جداول القناص القديمة (signal_log/daily_stats) أثناء إغلاق الموجات
        set_sig, upd_daily = self.db.set_signal_result, self.db.update_daily_pnl

        async def _noop(*a, **k):
            return None

        self.db.set_signal_result = _noop
        self.db.update_daily_pnl = _noop
        saved_size = self.TRADE_SIZE_USDT
        if margin_used > 0:
            self.TRADE_SIZE_USDT = margin_used   # نسبة الربح تُحسب من هامش الصفقة نفسه
        try:
            await super()._finalize_trade(trade, fill_price, reason, pnl_override)
        finally:
            self.TRADE_SIZE_USDT = saved_size
            self.db.set_signal_result = set_sig
            self.db.update_daily_pnl = upd_daily
        # فصل إحصاءات الموجات عن عدّادات المحرك القديمة
        self.stats['wins'], self.stats['losses'] = w0, l0
        if win:
            self.stats_mars['wins'] += 1
        else:
            self.stats_mars['losses'] += 1
        # تبريد الزوج ساعة من لحظة الإغلاق (مطابق للاختبار)
        self.mars_cooldown[trade['symbol']] = time.time() + int(self.mars.cfg['reentry_cooldown'])
        try:
            await self.mars_db.close(trade['symbol'], time.time(), total, round(pct, 2), win, reason)
        except Exception as e:
            logger.warning(f"تعذر إغلاق سجل الموجات: {e}")
        logger.info(f"🏁 موجات: {trade['symbol']} {total:+.3f} USDT ({pct:+.1f}%) — {reason}")
        self._log_mars("CLOSE", f"{trade['symbol']} {trade['side']} أُغلقت {total:+.4f}$ ({pct:+.1f}%) — {reason}")

    # ═══════════════ تقارير بلا قناص ═══════════════
    async def _send_daily_report(self, day):
        """تقرير يومي من قاعدة الموجات (بدل جدول daily_stats الخاص بالقناص)."""
        try:
            async with aiosqlite.connect(self.db.db_name) as db:
                async with db.execute(
                        "SELECT pnl, wins, losses FROM mars_daily WHERE date=?", (day,)) as cur:
                    row = await cur.fetchone()
            if not row:
                return
            pnl, w, l = row[0] or 0.0, row[1] or 0, row[2] or 0
            wr = (w / (w + l) * 100) if (w + l) > 0 else 0
            await self.tg(f"📊 *تقرير الموجات {day}*\n💰 PnL: `{pnl:.4f} USDT`\n"
                          f"🏆 {w}W / {l}L (فوز {wr:.0f}%)")
        except Exception as e:
            logger.warning(f"تعذر تقرير الموجات اليومي: {e}")

    async def _heartbeat_and_report(self, loop_count):
        """نبض ساعي بلا مطوّر قناص."""
        now = time.time()
        today = time.strftime("%Y-%m-%d")
        if today != self._report_day:
            await self._send_daily_report(self._report_day)
            self._report_day = today
        if now - self._last_heartbeat >= 3600:
            self._last_heartbeat = now
            open_m = len(self._mars_open())
            await self.tg(f"💓 *النبض:* حي ✓ | مسح #{loop_count} | "
                          f"صفقات الموجات المفتوحة: {open_m}/{self.mars_capacity} | "
                          f"فوز: {self.stats_mars['wins']}W / {self.stats_mars['losses']}L")


# ═══════════════════════ نقطة التشغيل ═══════════════════════
if __name__ == "__main__":
    bot = MarsBotV9()
    bot.start()
