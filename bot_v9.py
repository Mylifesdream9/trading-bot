"""
═══════════════════════════════════════════════════════════════════════
  🥷🔥 القناص V9 — روبوت باستراتيجيتين مستقلتين تماماً
═══════════════════════════════════════════════════════════════════════
  الاستراتيجية 1 (القناص)     : تعمل كما هي، بلا أي تغيير في ملفها.
  الاستراتيجية 2 (راكب الترند): تحليل خاص + دخول خاص + إدارة خروج خاصة.

  التشغيل:  python3 bot_v9.py        (بدل python3 bot.py)

  · لكل استراتيجية سعة صفقات مستقلة (MAX_OPEN_TRADES_TREND)
    وهامش صفقة مستقل (TRADE_SIZE_USDT_TREND — 0 = نفس هامش القناص).
  · كل صفقة تُوسم باسم استراتيجيتها، وتُدار بقواعدها فقط:
      - صفقات القناص  → monitor_trades الأصلي (TP1/TP2 + تريلينغ 1%).
      - صفقات الترند  → TrendExitManager (جني 70% عند 0.9R + وقف متحرك 1.5×ATR + خروج زمني).
  · المطوّر التكيفي (AdaptiveTuner) يبقى خاصاً بالقناص ولا يتغذى من صفقات الترند.
  · إحصاءات وسجل مستقلان في قاعدة البيانات (جدولا trend_trades / trend_daily).
  · لوحة للاستراتيجية الثانية بتبويبات على:  http://HOST:PORT/trend
      (نظرة عامة · مفتوحة · السجل · الأيام · الحركات) — تبويب الحركات يسجل
      كل حدث: إشارة، دخول، جني جزئي، نقل وقف، إغلاق.
═══════════════════════════════════════════════════════════════════════
"""
import asyncio
import json
import logging
import os
import time
from collections import deque

import aiosqlite

import bot as botmod                      # البوت الحالي كما هو (المحرّك)
import web_panel_trend                    # لوحة الاستراتيجية الثانية (طبقة عرض مستقلة)
from strategy_trend import (TREND_CONFIG, TrendDB, TrendExitManager,
                            TrendStrategy)

logger = logging.getLogger('SniperV9')

# سعة الصفقات الخاصة باستراتيجية الترند (مستقلة عن القناص)
MAX_OPEN_TRADES_TREND = int(os.environ.get('MAX_OPEN_TRADES_TREND', '5'))
# سعة استراتيجية القناص (0 = اترك إعداد bot.py كما هو)
MAX_OPEN_TRADES_SNIPER = int(os.environ.get('MAX_OPEN_TRADES_SNIPER', '0'))
# سقف إجمالي صارم لكل الصفقات المفتوحة من الاستراتيجيتين (0 = بلا سقف)
MAX_TOTAL_TRADES = int(os.environ.get('MAX_TOTAL_TRADES', '0'))
TREND_ENABLED = os.environ.get('STRATEGY_TREND_ENABLED', 'true').lower() == 'true'
# هامش صفقة الترند الخاص (0 = يستخدم TRADE_SIZE_USDT المشترك نفسه)
TREND_TRADE_SIZE_USDT = float(os.environ.get('TRADE_SIZE_USDT_TREND', '0'))


class _NullTuner:
    """بديل صامت حتى لا تتلوث ذاكرة المطوّر التكيفي الخاص بالقناص."""

    def record(self, *a, **k):
        return

    def describe(self):
        return "—"

    def recent_winrate(self, *a, **k):
        return None


class LegendarySniperV9(botmod.LegendarySniperFuturesV8):
    def __init__(self):
        super().__init__()
        # ✅ إضافة: مسار قاعدة البيانات من متغير البيئة (مثال على Railway: DB_FILE=/data/sniper_v8.db)
        db_file = os.environ.get('DB_FILE')
        if db_file:
            self.db.db_name = db_file
        self.trend = TrendStrategy({"enabled": TREND_ENABLED}, logger.warning)
        self.trend_exit = TrendExitManager(logger=logger.warning)
        self.trend_db = TrendDB(self.db.db_name)
        self.trend_cooldown = {}
        self.stats_trend = {"wins": 0, "losses": 0, "trades": 0}
        self._trend_cursor = 0
        self.trend_events = deque(maxlen=300)   # سجل حيّ لكل حركة
        # أرقام تعرضها اللوحة (اللوحة لا تعرف ثوابت هذا الملف)
        self.trend_capacity = MAX_OPEN_TRADES_TREND
        self.total_cap = MAX_TOTAL_TRADES
        # هامش صفقة الترند الفعلي (يُعرض في اللوحة ويُستخدم عند الدخول)
        self.trend_trade_size = TREND_TRADE_SIZE_USDT if TREND_TRADE_SIZE_USDT > 0 else self.TRADE_SIZE_USDT
        self._apply_sniper_cap()

    def _log_trend(self, kind, msg):
        """تسجيل حركة في سجل الاستراتيجية الثانية (يظهر في تبويب الحركات)."""
        try:
            self.trend_events.append({"ts": time.time(), "kind": kind, "msg": msg})
        except Exception:
            pass

    def _apply_sniper_cap(self):
        """تطبيق سقف القناص القادم من البيئة (إن وُجد)."""
        if MAX_OPEN_TRADES_SNIPER > 0 and getattr(self, 'MAX_OPEN_TRADES', 0) != MAX_OPEN_TRADES_SNIPER:
            self.MAX_OPEN_TRADES = MAX_OPEN_TRADES_SNIPER

    def _total_cap_hit(self, extra=0):
        """هل وصلنا السقف الإجمالي للصفقات المفتوحة؟"""
        if MAX_TOTAL_TRADES <= 0:
            return False
        return len(self.active_trades) + extra > MAX_TOTAL_TRADES

    # ═══════════════ الإقلاع: استعادة صفقات الترند المفتوحة ═══════════════
    async def main_loop(self):
        try:
            await self.trend_db.init()
        except Exception as e:
            logger.error(f"تعذر تهيئة قاعدة بيانات الترند: {e}")

        # ✅ إضافة: تحميل إعدادات الترند المحفوظة من اللوحة (تنجو من إعادة التشغيل والنشر)
        try:
            await self.db.init_db()   # ضمان وجود جدول الإعدادات حتى على قاعدة جديدة
        except Exception:
            pass
        try:
            raw = await self.db.get_param('trend_config')
            if raw:
                saved = json.loads(raw)
                self.trend.cfg.update({k: v for k, v in saved.items() if k in self.trend.cfg})
                self.trend_exit.cfg.update(self.trend.cfg)
                self.trend_capacity = int(self.trend.cfg.get('max_open_trades', self.trend_capacity))
                logger.info(f"⚙️ إعدادات الترند محمّلة من القاعدة — سعة {self.trend_capacity} صفقة، "
                            f"الحالة: {'مفعّلة' if self.trend.cfg.get('enabled') else 'متوقفة'}")
        except Exception as e:
            logger.warning(f"تعذر تحميل إعدادات الترند المحفوظة: {e}")

        orig_load = self.db.load_active_trades

        async def _load_with_trend():
            trades = await orig_load()
            try:
                open_trend = await self.trend_db.open_symbols()
            except Exception:
                open_trend = {}
            for sym, row in open_trend.items():
                if sym in trades:
                    trades[sym]['strategy'] = 'TREND'
                    trades[sym]['atr_ref'] = row.get('atr') or 0.0
                    trades[sym]['tp2'] = None
                    trades[sym]['components'] = {'strategy': 'TREND'}
                    m = float(row.get('margin') or 0)
                    trades[sym]['margin_usdt'] = m if m > 0 else self.trend_trade_size
                    logger.info(f"♻️ استُعيدت صفقة ترند مفتوحة: {sym}")
            return trades

        self.db.load_active_trades = _load_with_trend

        # لوحة القناص + صفحة الاستراتيجية الثانية (من web_panel_trend.py)
        botmod.start_web_panel = web_panel_trend.start_web_panel_trend
        await super().main_loop()

    async def scan_volatile_coins(self):
        self._apply_sniper_cap()
        await super().scan_volatile_coins()
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
        trend_size = TREND_TRADE_SIZE_USDT if TREND_TRADE_SIZE_USDT > 0 else saved_size
        # نسمح بفتح صفقة واحدة إضافية عبر المسار الأصلي (سعة الترند مستقلة)
        self.MAX_OPEN_TRADES = max(saved_cap, len(self.active_trades) + 1)
        # هامش مستقل لصفقة الترند (TRADE_SIZE_USDT_TREND) — مؤقت أثناء التنفيذ فقط
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
        """يحذف أثر صفقة الترند من جدول إشارات القناص ومن عدّاد صفقات اليوم."""
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
            logger.warning(f"تعذر فصل سجل إشارات الترند: {e}")

    # ═══════════════ المراقبة: كل استراتيجية بقواعدها ═══════════════
    async def monitor_trades(self):
        trend_syms = [s for s, t in list(self.active_trades.items()) if t.get('strategy') == 'TREND']
        if trend_syms:
            held = {}
            for s in trend_syms:
                held[s] = self.active_trades.pop(s)
            try:
                await super().monitor_trades()
            finally:
                self.active_trades.update(held)
        else:
            await super().monitor_trades()
        if trend_syms:
            await self._trend_monitor(trend_syms)

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



# ═══════════════ نقطة التشغيل (كانت ناقصة في الملف المسلَّم) ═══════════════
if __name__ == "__main__":
    bot = LegendarySniperV9()
    bot.start()
