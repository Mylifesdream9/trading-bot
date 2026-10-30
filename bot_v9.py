"""
═══════════════════════════════════════════════════════════════════════
  🥷🔥 القناص V9 — روبوت باستراتيجيتين مستقلتين تماماً
═══════════════════════════════════════════════════════════════════════
  الاستراتيجية 1 (القناص)     : تعمل كما هي، بلا أي تغيير في ملفها.
  الاستراتيجية 2 (راكب الترند): تحليل خاص + دخول خاص + إدارة خروج خاصة.

  التشغيل:  python3 bot_v9.py        (بدل python3 bot.py)

  · لكل استراتيجية سعة صفقات مستقلة (MAX_OPEN_TRADES_TREND).
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

from aiohttp import web

import bot as botmod                      # البوت الحالي كما هو
import web_panel
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
        self.trend = TrendStrategy({"enabled": TREND_ENABLED}, logger.warning)
        self.trend_exit = TrendExitManager(logger=logger.warning)
        self.trend_db = TrendDB(self.db.db_name)
        self.trend_cooldown = {}
        self.stats_trend = {"wins": 0, "losses": 0, "trades": 0}
        self._trend_cursor = 0
        self.trend_events = deque(maxlen=300)   # سجل حيّ لكل حركة
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
                    logger.info(f"♻️ استُعيدت صفقة ترند مفتوحة: {sym}")
            return trades

        self.db.load_active_trades = _load_with_trend

        # اللوحة مع صفحة الاستراتيجية الثانية
        botmod.start_web_panel = self._start_panel_with_trend
        await super().main_loop()

    # ═══════════════ اللوحة ═══════════════
    async def _start_panel_with_trend(self, bot=None):
        bot = bot or self
        try:
            if hasattr(web_panel, 'PanelDB'):
                web_panel.PANEL_DB = web_panel.PanelDB(bot.db.db_name)
                await web_panel.PANEL_DB.init()
            app = web_panel.create_app(bot)
            app.middlewares.append(self._tabs_middleware)
            app.router.add_get('/trend', self._trend_page)
            app.router.add_get('/api/trend/overview', self._trend_overview)
            runner = web.AppRunner(app)
            await runner.setup()
            port = int(os.environ.get('PORT', '8080'))
            await web.TCPSite(runner, '0.0.0.0', port).start()
            print(f"🖥️ اللوحة تعمل على المنفذ {port} — صفحة الاستراتيجية الثانية: /trend")
            return True
        except Exception as e:
            print(f"⚠️ تعذر تشغيل اللوحة الموسّعة ({e}) — تشغيل اللوحة الأصلية")
            try:
                return await web_panel.start_web_panel(bot)
            except Exception as e2:
                print(f"⚠️ فشل اللوحة: {e2}")
                return False

    async def _tabs_middleware(self, request, handler):
        """شريط تبويبات الاستراتيجيتين + إخفاء صفقات الترند من واجهات القناص."""
        resp = await handler(request)
        try:
            if request.path in ('/', '/trend') and getattr(resp, 'content_type', '') == 'text/html':
                body = resp.text or ''
                if '<body' in body and 'id="v9tabs"' not in body:
                    bar = _tab_bar('trend' if request.path == '/trend' else 'sniper')
                    k = body.index('>', body.index('<body')) + 1
                    resp.text = body[:k] + bar + body[k:]
            elif request.path in ('/api/trades', '/api/overview') \
                    and getattr(resp, 'content_type', '') == 'application/json':
                trend_syms = {s for s, t in self.active_trades.items()
                              if t.get('strategy') == 'TREND'}
                if trend_syms:
                    data = json.loads(resp.text)
                    if request.path == '/api/trades' and isinstance(data, list):
                        data = [x for x in data if x.get('symbol') not in trend_syms]
                    elif isinstance(data, dict) and isinstance(data.get('open_trades'), int):
                        data['open_trades'] = max(0, data['open_trades'] - len(trend_syms))
                    else:
                        return resp
                    return web.json_response(data, headers={'Cache-Control': 'no-store'})
        except Exception as e:
            logger.warning(f"خطأ في ميدلوير التبويبات: {e}")
        return resp

    async def _trend_overview(self, request):
        data = {"ok": True, "stats": self.stats_trend, "config": {
            k: self.trend.cfg.get(k) for k in
            ("donch", "sl_atr1h", "tp1_r", "partial", "trail_atr",
             "max_hold_minutes", "min_atr_pct", "max_atr_pct", "max_risk_pct")},
            "open": [], "enabled": bool(self.trend.cfg.get('enabled')),
            "capacity": MAX_OPEN_TRADES_TREND,
            "total_cap": MAX_TOTAL_TRADES, "sniper_cap": getattr(self, 'MAX_OPEN_TRADES', 0),
            "events": list(reversed(self.trend_events))[:120]}
        try:
            data["summary"] = await self.trend_db.summary()
        except Exception as e:
            data["summary"] = {"error": str(e)}
        risk_cfg = float(self.trend.cfg['sl_atr1h'])
        for sym, t in self.active_trades.items():
            if t.get('strategy') != 'TREND':
                continue
            prices = self.get_price(sym) or {}
            is_buy = t['side'] == 'BUY'
            px = prices.get('bid' if is_buy else 'ask') or t['entry_price']
            move = (px - t['entry_price']) if is_buy else (t['entry_price'] - px)
            qty = t.get('quantity') or 0.0
            risk = (t.get('atr_ref') or 0.0) * risk_cfg
            data["open"].append({
                "symbol": sym, "side": t['side'], "entry": t['entry_price'],
                "price": px, "sl": t['sl'], "tp1": t.get('tp'),
                "qty": round(qty, 6), "risk": round(risk, 8),
                "r": round(move / risk, 2) if risk else 0.0,
                "pnl_usdt": round(move * qty, 4),
                "realized": round(t.get('realized_pnl', 0.0), 4),
                "pnl_pct": round(move / t['entry_price'] * self.LEVERAGE * 100, 2),
                "partial": bool(t.get('partial_closed')),
                "age_min": int((time.time() - t['entry_time']) / 60),
            })
        return web.json_response(data)

    async def _trend_page(self, request):
        return web.Response(text=TREND_PAGE, content_type='text/html')

    # ═══════════════ المسح ═══════════════
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
            if open_trend >= MAX_OPEN_TRADES_TREND or self._total_cap_hit():
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
        if open_trend >= MAX_OPEN_TRADES_TREND:
            return
        if self._total_cap_hit(extra=1):
            return
        saved_cap = self.MAX_OPEN_TRADES
        # نسمح بفتح صفقة واحدة إضافية عبر المسار الأصلي (سعة الترند مستقلة)
        self.MAX_OPEN_TRADES = max(saved_cap, len(self.active_trades) + 1)
        try:
            await super().execute_trade(analysis)
        finally:
            self.MAX_OPEN_TRADES = saved_cap
        trade = self.active_trades.get(sym)
        if not trade or trade.get('strategy'):
            return
        trade['strategy'] = 'TREND'
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
                      f"الاتجاه: {analysis['direction']} | وقف ATR(1h)\n"
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
        pct = total / self.TRADE_SIZE_USDT * 100 if self.TRADE_SIZE_USDT else 0
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
        try:
            await super()._finalize_trade(trade, fill_price, reason, pnl_override)
        finally:
            self.tuner = saved
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


# ═══════════════════════ صفحة اللوحة الخاصة بالاستراتيجية الثانية ═══════════════════════
def _tab_bar(active):
    """شريط تبويبات يربط لوحة القناص بلوحة الاستراتيجية الثانية."""
    def _a(href, key, label):
        on = key == active
        border = '#f5b942' if on else '#1e293b'
        bg = 'rgba(245,185,66,.14)' if on else 'transparent'
        color = '#f5b942' if on else '#7c8aa5'
        return ('<a href="' + href + '" style="display:flex;align-items:center;gap:7px;'
                'padding:7px 16px;border-radius:10px;text-decoration:none;font-size:13px;'
                'font-weight:700;border:1px solid ' + border + ';background:' + bg +
                ';color:' + color + '">' + label + '</a>')

    return ('<div id="v9tabs" style="position:sticky;top:0;z-index:99999;display:flex;gap:8px;'
            'align-items:center;background:#080c13;border-bottom:1px solid #1e293b;'
            "padding:9px 14px;font-family:'Segoe UI',Tahoma,Arial,sans-serif;direction:rtl\">"
            + _a('/', 'sniper', '🥷 القناص')
            + _a('/trend', 'trend', '🚀 راكب الترند')
            + '<span style="margin-right:auto;color:#5b6880;font-size:11px">'
              'استراتيجيتان مستقلتان — V9</span></div>')


# ═══════════════════════ صفحة لوحة الاستراتيجية الثانية (تبويبات) ═══════════════════════
TREND_PAGE = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>🚀 راكب الترند — الاستراتيجية الثانية</title>
<style>
:root{--bg:#0a0e16;--card:#111726;--line:#1e293b;--tx:#e2e8f0;--mut:#7c8aa5;--gold:#f5b942;
--green:#10b981;--red:#ef4444;--blue:#3b82f6;--violet:#8b5cf6}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--tx);font-family:'Segoe UI',Tahoma,Arial,sans-serif;font-size:14px}
.hdr{padding:13px 18px;border-bottom:1px solid var(--line);display:flex;gap:14px;align-items:center;flex-wrap:wrap;background:#080c13}
.logo{font-size:18px;font-weight:800;color:var(--gold)}
.hdr a{color:var(--mut);text-decoration:none;font-size:12px;border:1px solid var(--line);padding:5px 11px;border-radius:9px}
.hdr a:hover{color:var(--tx);border-color:var(--gold)}
.wrap{padding:16px;max-width:1280px;margin:0 auto}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
.tab{background:var(--card);border:1px solid var(--line);color:var(--mut);padding:8px 15px;border-radius:11px;
cursor:pointer;font-size:13px;font-weight:600;font-family:inherit}
.tab:hover{color:var(--tx)}
.tab.on{background:rgba(245,185,66,.12);border-color:var(--gold);color:var(--gold)}
.pane{display:none}.pane.on{display:block}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(170px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px;margin-bottom:12px}
.card h3{font-size:12px;color:var(--mut);margin-bottom:8px;font-weight:600}
.big{font-size:24px;font-weight:800;font-family:monospace}
.pos{color:var(--green)}.neg{color:var(--red)}.gold{color:var(--gold)}
table{width:100%;border-collapse:collapse;font-size:12.5px;margin-top:6px}
th{background:#0d1320;color:var(--mut);padding:8px 6px;text-align:right;font-weight:600;position:sticky;top:0}
td{padding:7px 6px;border-bottom:1px solid #16202f}
tr:hover td{background:#0d1522}
.tag{padding:2px 9px;border-radius:12px;font-size:11px;font-weight:700}
.buy{background:rgba(16,185,129,.15);color:var(--green)}
.sell{background:rgba(239,68,68,.15);color:var(--red)}
.k{display:inline-block;min-width:62px;text-align:center;padding:2px 8px;border-radius:9px;font-size:10.5px;font-weight:800}
.k-ENTRY{background:rgba(59,130,246,.16);color:#60a5fa}
.k-CLOSE{background:rgba(139,92,246,.16);color:#a78bfa}
.k-PARTIAL{background:rgba(245,185,66,.16);color:var(--gold)}
.k-TRAIL{background:rgba(16,185,129,.14);color:var(--green)}
.k-SCAN{background:#16202f;color:var(--mut)}
.k-ERROR{background:rgba(239,68,68,.16);color:var(--red)}
.ev{display:flex;gap:10px;padding:8px 4px;border-bottom:1px solid #16202f;align-items:flex-start;font-size:12.5px}
.ev time{color:var(--mut);font-family:monospace;font-size:11px;white-space:nowrap;padding-top:2px}
.note{font-size:11.5px;color:var(--mut);margin-top:10px;line-height:1.9}
.scroll{max-height:62vh;overflow:auto}
.empty{color:var(--mut);text-align:center;padding:22px;font-size:12.5px}
</style></head><body>
<div class="hdr"><div class="logo">🚀 راكب الترند</div>
<span style="color:var(--mut);font-size:12px" id="mode">…</span>
<span style="margin-right:auto;color:var(--mut);font-size:12px" id="upd"></span></div>
<div class="wrap">
<div class="tabs">
<div class="tab on" data-t="overview" onclick="show('overview')">📊 نظرة عامة</div>
<div class="tab" data-t="open" onclick="show('open')">📌 مفتوحة (<span id="nOpen">0</span>)</div>
<div class="tab" data-t="history" onclick="show('history')">📜 السجل</div>
<div class="tab" data-t="days" onclick="show('days')">📅 الأيام</div>
<div class="tab" data-t="events" onclick="show('events')">⚡ الحركات</div>
</div>

<div class="pane on" id="p-overview">
<div class="grid">
<div class="card"><h3>نسبة الفوز (30 يوماً)</h3><div class="big gold" id="wr">—</div></div>
<div class="card"><h3>عامل الربح (PF)</h3><div class="big" id="pf">—</div></div>
<div class="card"><h3>صافي الربح</h3><div class="big" id="net">—</div></div>
<div class="card"><h3>مغلقة / مفتوحة</h3><div class="big" id="cnt">—</div></div>
<div class="card"><h3>متوسط الربح / الخسارة</h3><div class="big" id="avgs" style="font-size:19px">—</div></div>
<div class="card"><h3>خسائر / أرباح (عدد)</h3><div class="big" id="wl" style="font-size:19px">—</div></div>
</div>
<div class="card" style="margin-top:12px"><h3>قواعد هذه الاستراتيجية (مستقلة تماماً عن القناص)</h3>
<div class="note" id="rules">…</div></div>
</div>

<div class="pane" id="p-open">
<div class="card"><h3>الصفقات المفتوحة الآن</h3><div class="scroll">
<table id="tOpen"><thead><tr><th>العملة</th><th>الاتجاه</th><th>الدخول</th><th>السعر</th><th>الوقف</th>
<th>TP1</th><th>R</th><th>عائم $</th><th>عائم %</th><th>الجزئي</th><th>العمر</th></tr></thead>
<tbody></tbody></table></div></div>
</div>

<div class="pane" id="p-history">
<div class="card"><h3>آخر 60 صفقة مغلقة</h3><div class="scroll">
<table id="tHist"><thead><tr><th>العملة</th><th>الاتجاه</th><th>الدخول</th><th>الربح $</th><th>الربح %</th>
<th>النتيجة</th><th>السبب</th><th>وقت الإغلاق</th></tr></thead><tbody></tbody></table></div></div>
</div>

<div class="pane" id="p-days">
<div class="card"><h3>النتيجة اليومية (آخر 30 يوماً)</h3><div class="scroll">
<table id="tDays"><thead><tr><th>التاريخ</th><th>الصافي $</th><th>رابحة</th><th>خاسرة</th>
<th>الإجمالي</th><th>نسبة الفوز</th></tr></thead><tbody></tbody></table></div></div>
</div>

<div class="pane" id="p-events">
<div class="card"><h3>كل حركة يقوم بها البوت — الاستراتيجية الثانية (آخر 120)</h3>
<div class="scroll" id="evList"><div class="empty">لا حركات بعد…</div></div>
<div class="note">ENTRY = دخول · PARTIAL = جني 70% · TRAIL = نقل الوقف المتحرك · CLOSE = إغلاق · SCAN = مسح إشارات.</div>
</div>
</div>
</div>
<script>
const $=i=>document.getElementById(i);
const f=(x,d=2)=>(Number(x)>=0?'+':'')+Number(x).toFixed(d);
const money=x=>(Number(x)>=0?'+':'')+Number(x).toFixed(2)+'$';
const cls=x=>Number(x)>=0?'pos':'neg';
function show(t){document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('on',b.dataset.t===t));
 document.querySelectorAll('.pane').forEach(p=>p.classList.toggle('on',p.id==='p-'+t));}
function ago(m){return m<60?m+'د':(m<1440?Math.round(m/60)+'س':Math.round(m/1440)+'ي');}
async function tick(){
 try{
  const r=await fetch('/api/trend/overview',{cache:'no-store'}); const d=await r.json();
  const s=d.summary||{}; const c=d.config||{};
  $('mode').textContent=d.enabled?'🟢 مفعّلة':'🔴 متوقفة';
  $('wr').textContent=(s.winrate??0)+'%';
  $('pf').textContent=(s.pf??0);
  $('net').textContent=money(s.net??0); $('net').className='big '+cls(s.net??0);
  $('cnt').textContent=(s.closed??0)+' / '+(d.open||[]).length;
  $('avgs').textContent=money(s.avg_win??0)+' / '+Number(s.avg_loss??0).toFixed(2)+'$';
  $('wl').textContent=(s.losses??0)+' / '+(s.wins??0);
  $('nOpen').textContent=(d.open||[]).length;
  $('rules').innerHTML=`اختراق أعلى/أدنى <b>${c.donch}</b> شمعة ساعة بعد اتجاه 4 ساعات ·
   وقف <b>${c.sl_atr1h}×ATR(1h)</b> · جني <b>${(c.partial*100).toFixed(0)}%</b> عند <b>${c.tp1_r}R</b> ·
   وقف متحرك <b>${c.trail_atr}×ATR</b> · خروج زمني <b>${Math.round((c.max_hold_minutes||0)/1440)}</b> أيام ·
   فلتر ATR <b>${c.min_atr_pct}–${c.max_atr_pct}%</b> · أقصى مخاطرة <b>${c.max_risk_pct}%</b><br>
   السعة: <b>${d.capacity}</b> صفقة للترند + <b>${d.sniper_cap}</b> للقناص${d.total_cap?` · سقف إجمالي <b>${d.total_cap}</b>`:''}`;

  let h='';
  for(const t of (d.open||[])){
   h+=`<tr><td><b>${t.symbol}</b></td><td><span class="tag ${t.side==='BUY'?'buy':'sell'}">${t.side}</span></td>
   <td>${t.entry}</td><td>${t.price}</td><td>${t.sl}</td><td>${t.tp1??'—'}</td>
   <td class="${cls(t.r)}">${Number(t.r).toFixed(2)}R</td>
   <td class="${cls(t.pnl_usdt)}">${money(t.pnl_usdt)}</td>
   <td class="${cls(t.pnl_pct)}">${f(t.pnl_pct)}%</td>
   <td>${t.partial?'✅ 70%':'—'}</td><td>${ago(t.age_min)}</td></tr>`;
  }
  $('tOpen').tBodies[0].innerHTML=h||'<tr><td colspan="11" class="empty">لا صفقات مفتوحة</td></tr>';

  let c2='';
  for(const t of (s.trades||[])){
   const ts=t.exit_ts?new Date(t.exit_ts*1000).toLocaleString('ar-EG',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}):'—';
   c2+=`<tr><td><b>${t.symbol}</b></td><td><span class="tag ${t.side==='BUY'?'buy':'sell'}">${t.side}</span></td>
   <td>${t.entry}</td><td class="${cls(t.pnl)}">${money(t.pnl)}</td>
   <td class="${cls(t.pnl_pct)}">${f(t.pnl_pct||0)}%</td>
   <td>${t.win?'✅ رابحة':'❌ خاسرة'}</td><td>${t.reason||''}</td><td style="color:#7c8aa5">${ts}</td></tr>`;
  }
  $('tHist').tBodies[0].innerHTML=c2||'<tr><td colspan="8" class="empty">لا صفقات مغلقة بعد</td></tr>';

  let c3='';
  for(const x of (s.daily||[])){
   const tot=(x.wins||0)+(x.losses||0);
   c3+=`<tr><td>${x.date}</td><td class="${cls(x.pnl)}">${money(x.pnl)}</td>
   <td class="pos">${x.wins||0}</td><td class="neg">${x.losses||0}</td><td>${tot}</td>
   <td>${tot?Math.round((x.wins||0)/tot*100)+'%':'—'}</td></tr>`;
  }
  $('tDays').tBodies[0].innerHTML=c3||'<tr><td colspan="6" class="empty">لا أيام مسجلة بعد</td></tr>';

  let ev='';
  for(const e of (d.events||[])){
   const ts=new Date(e.ts*1000).toLocaleTimeString('ar-EG',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
   ev+=`<div class="ev"><time>${ts}</time><span class="k k-${e.kind}">${e.kind}</span><span>${e.msg}</span></div>`;
  }
  $('evList').innerHTML=ev||'<div class="empty">لا حركات بعد…</div>';
  $('upd').textContent='آخر تحديث: '+new Date().toLocaleTimeString('ar-EG');
 }catch(e){$('upd').textContent='⚠️ خطأ في التحديث';}
}
tick(); setInterval(tick,3000);
</script></body></html>
"""
