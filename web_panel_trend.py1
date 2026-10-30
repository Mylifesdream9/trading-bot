""""
═══════════════════════════════════════════════════════════════════════
  🚀 لوحة الاستراتيجية الثانية — «راكب الترند»
═══════════════════════════════════════════════════════════════════════
  طبقة العرض فقط. لا تعرف شيئاً عن التداول ولا تستورد bot_v9.py،
  بل تتلقى نسخة البوت كما يفعل web_panel.create_app(bot) — نفس أسلوب مشروعك:

      bot.py ──(import)──> web_panel.py     ← اللوحة الأصلية (لم تُعدّل)
      bot_v9.py ──(import)──> web_panel_trend.py  ← هذه اللوحة

  ما تضيفه فوق لوحة القناص الأصلية:
    · شريط تبويبات (🥷 القناص | 🚀 راكب الترند) يُحقن في صفحتي / و /trend.
    · صفحة /trend بخمسة تبويبات: نظرة عامة · مفتوحة · السجل · الأيام · الحركات.
    · مسار JSON: /api/trend/overview
    · إخفاء صفقات الترند من واجهات القناص (/api/trades و /api/overview)
      حتى لا تختلط إحصاءات الاستراتيجيتين في الشاشة.
═══════════════════════════════════════════════════════════════════════
"""
import json
import os
import time

from aiohttp import web

import web_panel

PANEL_VERSION = "V9-Trend"
TABS_ID = "v9tabs"


def _num(bot, attr, default=0):
    """قراءة رقم من نسخة البوت بأمان."""
    try:
        return int(getattr(bot, attr, default) or 0)
    except Exception:
        return default


def make_handlers(bot):
    """يبني معالجات اللوحة مرتبطة بنسخة البوت (نفس نمط web_panel.create_app)."""

    async def trend_page(request):
        return web.Response(text=TREND_PAGE, content_type='text/html')

    async def trend_overview(request):
        cfg = getattr(getattr(bot, 'trend', None), 'cfg', {}) or {}
        data = {
            "ok": True,
            "stats": getattr(bot, 'stats_trend', {"wins": 0, "losses": 0, "trades": 0}),
            "config": {k: cfg.get(k) for k in
                       ("donch", "sl_atr1h", "tp1_r", "partial", "trail_atr",
                        "max_hold_minutes", "min_atr_pct", "max_atr_pct", "max_risk_pct")},
            "open": [],
            "enabled": bool(cfg.get('enabled')),
            "capacity": _num(bot, 'trend_capacity', 0),
            "total_cap": _num(bot, 'total_cap', 0),
            "sniper_cap": _num(bot, 'MAX_OPEN_TRADES', 0),
            "events": list(reversed(getattr(bot, 'trend_events', [])))[:120],
        }
        try:
            data["summary"] = await bot.trend_db.summary()
        except Exception as e:
            data["summary"] = {"error": str(e)}

        risk_cfg = float(cfg.get('sl_atr1h') or 0) or 1.0
        leverage = float(getattr(bot, 'LEVERAGE', 1) or 1)
        for sym, t in getattr(bot, 'active_trades', {}).items():
            if t.get('strategy') != 'TREND':
                continue
            prices = bot.get_price(sym) or {}
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
                "pnl_pct": round(move / t['entry_price'] * leverage * 100, 2),
                "partial": bool(t.get('partial_closed')),
                "age_min": int((time.time() - t['entry_time']) / 60),
            })
        return web.json_response(data)

    @web.middleware
    async def tabs_middleware(request, handler):
        """شريط التبويبات + إخفاء صفقات الترند من واجهات القناص."""
        resp = await handler(request)
        try:
            if request.path in ('/', '/trend') and getattr(resp, 'content_type', '') == 'text/html':
                body = resp.text or ''
                if '<body' in body and ('id="%s"' % TABS_ID) not in body:
                    active = 'trend' if request.path == '/trend' else 'sniper'
                    k = body.index('>', body.index('<body')) + 1
                    resp.text = body[:k] + _tab_bar(active) + body[k:]
            elif request.path in ('/api/trades', '/api/overview') \
                    and getattr(resp, 'content_type', '') == 'application/json':
                trend_syms = {s for s, t in getattr(bot, 'active_trades', {}).items()
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
            print(f"⚠️ خطأ في ميدلوير التبويبات: {e}")
        return resp

    return trend_page, trend_overview, tabs_middleware


async def start_web_panel_trend(bot):
    """يستبدل start_web_panel في bot.py: نفس الخطوات + مسارات الاستراتيجية الثانية."""
    try:
        # نفس ما تفعله web_panel.start_web_panel الأصلية بالضبط
        if hasattr(web_panel, 'PanelDB'):
            web_panel.PANEL_DB = web_panel.PanelDB(bot.db.db_name)
            await web_panel.PANEL_DB.init()

        app = web_panel.create_app(bot)
        trend_page, trend_overview, tabs_middleware = make_handlers(bot)
        app.middlewares.append(tabs_middleware)
        app.router.add_get('/trend', trend_page)
        app.router.add_get('/api/trend/overview', trend_overview)

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
