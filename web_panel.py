"""
═══════════════════════════════════════════════════════════════════════
  🖥️ لوحتا التحكم — في ملف واحد
═══════════════════════════════════════════════════════════════════════
  ملف واحد فيه لوحتان مستقلتان بالكامل، يربط بينهما شريط تبويبات أعلى الصفحة:

    🚀 راكب الترند      →  /trend   (بياناته من trend_trades / trend_daily)
    📐 موجات 7/25/99    →  /mars    (بياناتها من mars_trades / mars_daily)

  كل لوحة خمسة تبويبات متزامنة كل 2.5 ثانية:
    الرئيسية · ربح اليوم · المفتوحة · السجل والأيام · التحكم
  وفي التحكم: أزرار الاستراتيجية نفسها + الأدوات العامة المشتركة
  (إيقاف مؤقت، طوارئ، إغلاق شامل، إيقاف البوت، مسح شامل).

  طبقة عرض فقط لا تعرف التداول — تستقبل نسخة البوت مثل السابق.
  المسارات:
    GET  /  /trend  /mars
    GET  /api/trend/{panel,trades,today,history,closed}
    POST /api/trend/{enable,disable,close-all,wipe}
    GET  /api/mars/{panel,trades,today,history,closed}
    POST /api/mars/{enable,disable,close-all,wipe}
    GET  /api/notifications
    POST /api/{balance,pause,resume,close-all,emergency,emergency-reset,stop-bot,wipe}
═══════════════════════════════════════════════════════════════════════
"""
import os
import time
import json

import aiosqlite
from aiohttp import web

PANEL_START = time.time()
PANEL_VERSION = "V11-Dual"

STRATEGY_META = {
    'trend': {
        'key': 'trend', 'attr': 'trend', 'exit_attr': 'trend_exit',
        'db_attr': 'trend_db', 'events_attr': 'trend_events', 'stats_attr': 'stats_trend',
        'cap_attr': 'trend_capacity', 'persist': 'trend_config',
        'name': 'راكب الترند', 'logo': '🚀 راكب الترند', 'accent': '#f5b942',
        'tables': ('trend_trades', 'trend_daily'), 'skey': 'TREND',
        'other_key': 'mars',
        'note_open': '🎯 التقدم = المسافة المقطوعة نحو TP1 | قواعد الترند: جني 70% عند TP1 (0.9R) ثم نقل الوقف للتعادل ثم وقف متحرك 1.5×ATR — ولا يوجد هدف ثانٍ (الرابح يُترك يركب الترند).',
        'note_ctrl': 'الإيقاف/التفعيل يُحفظ في قاعدة البيانات — ينجو من إعادة التشغيل والنشر. الصفقات المفتوحة تُدار بقواعدها حتى إغلاقها حتى لو أوقفت الاستراتيجية.',
    },
    'mars': {
        'key': 'mars', 'attr': 'mars', 'exit_attr': 'mars_exit',
        'db_attr': 'mars_db', 'events_attr': 'mars_events', 'stats_attr': 'stats_mars',
        'cap_attr': 'mars_capacity', 'persist': 'mars_config',
        'name': 'موجات 7/25/99', 'logo': '📐 موجات 7/25/99', 'accent': '#8b5cf6',
        'tables': ('mars_trades', 'mars_daily'), 'skey': 'MARS',
        'other_key': 'trend',
        'note_open': '🎯 التقدم = المسافة المقطوعة نحو هدف 2R | قواعد الموجات: وقف 1.5×ATR(1h) وهدف ثابت 2R — بلا جني جزئي ولا وقف متحرك (نفس إعداد الاختبار المعتمد فوز 55.20%). الهدف مثبّت أيضاً على المنصة.',
        'note_ctrl': 'الإيقاف/التفعيل يُحفظ في قاعدة البيانات — ينجو من إعادة التشغيل والنشر. الصفقات المفتوحة تُدار بقواعدها حتى إغلاقها حتى لو أوقفت الاستراتيجية.',
    },
}


def _num(obj, attr, default=0):
    try:
        return int(getattr(obj, attr, default) or 0)
    except Exception:
        return default


def _day_start_ts():
    return time.mktime(time.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d'))


# ═══════════════════════ قاعدة إشعارات اللوحة ═══════════════════════
NOTIFY_SCHEMA = """CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, kind TEXT,
    title TEXT, body TEXT, level TEXT DEFAULT 'info')"""


class PanelDB:
    def __init__(self, db_name):
        self.db_name = db_name

    async def init(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(NOTIFY_SCHEMA)
            await db.commit()

    async def add(self, kind, title, body='', level='info'):
        try:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute(
                    "INSERT INTO notifications (ts, kind, title, body, level) VALUES (?,?,?,?,?)",
                    (time.time(), kind, str(title)[:200], str(body)[:600], level))
                await db.commit()
        except Exception:
            pass

    async def get_after(self, after_id, limit=50):
        try:
            async with aiosqlite.connect(self.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                        "SELECT id, ts, kind, title, body FROM notifications "
                        "WHERE id > ? ORDER BY id DESC LIMIT ?", (after_id, limit)) as cur:
                    rows = await cur.fetchall()
                return {'items': [{
                            'id': r['id'], 'kind': r['kind'], 'title': r['title'],
                            'body': r['body'],
                            'time': time.strftime('%m-%d %H:%M:%S', time.localtime(r['ts'])),
                        } for r in reversed(rows)],
                        'last_id': max((r['id'] for r in rows), default=after_id)}
        except Exception:
            return {'items': [], 'last_id': after_id}


PANEL_DB = None


async def notify(kind, title, body='', level='info'):
    if PANEL_DB:
        await PANEL_DB.add(kind, title, body, level)


def tab_bar(active, accent):
    """شريط ربط اللوحتين أعلى كل صفحة."""
    def _a(href, key, label):
        on = key == active
        border = accent if on else '#1e293b'
        bg = 'rgba(139,92,246,.14)' if (on and key == 'mars') else \
             ('rgba(245,185,66,.14)' if on else 'transparent')
        color = accent if on else '#7c8aa5'
        return ('<a href="' + href + '" style="display:flex;align-items:center;gap:7px;'
                'padding:7px 16px;border-radius:10px;text-decoration:none;font-size:13px;'
                'font-weight:700;border:1px solid ' + border + ';background:' + bg +
                ';color:' + color + '">' + label + '</a>')

    return ('<div style="position:sticky;top:0;z-index:99999;display:flex;gap:8px;'
            'align-items:center;background:#080c13;border-bottom:1px solid #1e293b;'
            "padding:9px 14px;font-family:'Segoe UI',Tahoma,Arial,sans-serif;direction:rtl\">"
            + _a('/trend', 'trend', '🚀 راكب الترند')
            + _a('/mars', 'mars', '📐 موجات 7/25/99')
            + '<span style="margin-right:auto;color:#5b6880;font-size:11px">'
              'بوت ثنائي الاستراتيجية — V11</span></div>')


# ═══════════════════════ قالب الصفحة (لوحتان من قالب واحد) ═══════════════════════
_TPL_HTML = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__NAME__ — لوحة التحكم V11</title>
<style>
:root{
  --bg:#0a0e16; --card:#111726; --card2:#0d1320; --line:#1e293b;
  --tx:#e2e8f0; --mut:#7c8aa5; --gold:__ACCENT__; --green:#10b981;
  --red:#ef4444; --blue:#3b82f6; --orange:#f59e0b; --purple:#8b5cf6;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--tx);font-family:'Segoe UI',Tahoma,Arial,sans-serif;
     min-height:100vh;font-size:14px}
.hdr{position:sticky;top:0;z-index:50;background:linear-gradient(90deg,#0d1320,#111726);
     border-bottom:1px solid var(--line);padding:10px 16px;display:flex;align-items:center;
     gap:12px;flex-wrap:wrap}
.logo{font-size:18px;font-weight:800;color:var(--gold)}
.logo small{color:var(--mut);font-weight:400;font-size:11px}
.clock{font-family:monospace;font-size:20px;font-weight:700;color:var(--tx);
       background:var(--card2);border:1px solid var(--line);border-radius:10px;
       padding:4px 14px;min-width:150px;text-align:center}
.clock small{display:block;font-size:10px;color:var(--mut);font-weight:400}
.badge{padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;
       border:1px solid var(--line);background:var(--card2)}
.b-ok{color:var(--green);border-color:var(--green)}
.b-warn{color:var(--orange);border-color:var(--orange)}
.b-bad{color:var(--red);border-color:var(--red)}
.b-emg{color:#fff;background:var(--red);border-color:var(--red);animation:pulse 1s infinite}
@keyframes pulse{50%{opacity:.55}}
.tabs{display:flex;gap:6px;padding:10px 16px 0;flex-wrap:wrap;
      position:sticky;top:57px;z-index:40;background:var(--bg)}
.tab{padding:9px 18px;border-radius:12px 12px 0 0;cursor:pointer;border:1px solid var(--line);
     border-bottom:none;background:var(--card2);color:var(--mut);font-weight:700;font-size:13px}
.tab.on{background:var(--card);color:var(--gold);border-color:var(--gold)}
.wrap{padding:14px 16px 40px;max-width:1350px;margin:0 auto}
.sec{display:none}.sec.on{display:block}
.grid{display:grid;gap:12px}
.g4{grid-template-columns:repeat(auto-fit,minmax(210px,1fr))}
.g3{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.g2{grid-template-columns:repeat(auto-fit,minmax(420px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px}
.card h3{font-size:13px;color:var(--mut);margin-bottom:10px;font-weight:600}
.card h3 b{color:var(--gold)}
.kpi{display:flex;flex-direction:column;gap:2px}
.kpi .v{font-size:24px;font-weight:800;font-family:monospace}
.kpi .l{font-size:11px;color:var(--mut)}
.pos{color:var(--green)}.neg{color:var(--red)}.gold{color:var(--gold)}.blue{color:var(--blue)}
.kv{display:flex;justify-content:space-between;padding:6px 2px;border-bottom:1px dashed var(--line);font-size:13px}
.kv:last-child{border-bottom:none}
.kv span{color:var(--mut)}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{background:var(--card2);color:var(--mut);font-weight:600;padding:8px 6px;
   border-bottom:1px solid var(--line);position:sticky;top:0;text-align:right;white-space:nowrap}
td{padding:7px 6px;border-bottom:1px solid #16202f;white-space:nowrap}
tr:hover td{background:#141c2e}
.tblbox{overflow:auto;max-height:520px;border:1px solid var(--line);border-radius:10px}
.tag{display:inline-block;padding:2px 9px;border-radius:12px;font-size:11px;font-weight:700}
.tag.buy{background:rgba(16,185,129,.15);color:var(--green)}
.tag.sell{background:rgba(239,68,68,.15);color:var(--red)}
.tag.open{background:rgba(59,130,246,.15);color:var(--blue)}
.tag.info{background:rgba(139,92,246,.15);color:var(--purple)}
.tag.win{background:rgba(16,185,129,.15);color:var(--green)}
.tag.loss{background:rgba(239,68,68,.15);color:var(--red)}
.bar{height:7px;background:var(--card2);border-radius:6px;overflow:hidden;min-width:80px}
.bar i{display:block;height:100%;border-radius:6px}
.btn{padding:10px 16px;border-radius:10px;border:none;cursor:pointer;font-weight:700;
     font-size:13px;color:#fff;transition:.15s}
.btn:hover{filter:brightness(1.15)}
.btn:disabled{opacity:.4;cursor:not-allowed}
.b-blue{background:var(--blue)}.b-green{background:var(--green)}
.b-orange{background:var(--orange)}.b-red{background:var(--red)}
.b-gray{background:#334155}.b-purple{background:var(--purple)}
.btnrow{display:flex;gap:10px;flex-wrap:wrap}
.empty{color:var(--mut);text-align:center;padding:26px;font-size:13px}
.note{font-size:11px;color:var(--mut);line-height:1.7;margin-top:8px}
.warnbox{background:rgba(239,68,68,.08);border:1px solid var(--red);border-radius:12px;
         padding:14px;margin-bottom:12px;color:#fca5a5;font-size:13px;line-height:1.8}
.big{font-size:38px;font-weight:800;font-family:monospace}
.med{font-size:17px;font-weight:700;font-family:monospace}
.feed{max-height:340px;overflow:auto}
.feed .it{padding:8px 4px;border-bottom:1px dashed var(--line);font-size:12px}
.feed .it .t{color:var(--mut);font-size:10.5px}
.feed .it .h{font-weight:700}
.err-item{color:var(--orange)}
.spark{width:100%;height:130px}
select,input{background:var(--card2);color:var(--tx);border:1px solid var(--line);
             border-radius:8px;padding:7px 10px;font-size:13px;font-family:inherit}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-left:5px}
.dot.g{background:var(--green);animation:pulse 1.5s infinite}
.dot.r{background:var(--red)}
.mono{font-family:monospace}
.mut{color:var(--mut)}
.kpi .v,.big,.med,.mono,.clock,td.mono{direction:ltr;unicode-bidi:isolate}
@media(max-width:700px){.clock{font-size:15px;min-width:120px}.big{font-size:28px}}
</style>
</head>
<body>
__TABS__
<div class="hdr">
  <div class="logo">__LOGO__ <small id="ver">لوحة V11 • بوت ثنائي</small></div>
  <div class="clock" id="clock">--:--:--<small id="cdate">...</small></div>
  <span class="badge" id="syncBadge"><span class="dot r"></span>جاري الاتصال...</span>
  <span class="badge" id="modeBadge">—</span>
  <span class="badge" id="emgBadge" style="display:none">🚨 طوارئ</span>
  <span style="flex:1"></span>
  <span class="badge" id="hbBadge">نبض: —</span>
</div>

<div class="tabs">
  <div class="tab on" data-s="s-dash">🔴 الرئيسية</div>
  <div class="tab" data-s="s-today">💰 ربح اليوم</div>
  <div class="tab" data-s="s-open">📊 الصفقات المفتوحة</div>
  <div class="tab" data-s="s-hist">🗂 السجل والأيام</div>
  <div class="tab" data-s="s-ctrl">🎛 التحكم</div>
</div>

<div class="wrap">
<!-- ═════════ 🔴 الرئيسية ═════════ -->
<div class="sec on" id="s-dash">
  <div class="grid g4">
    <div class="card"><div class="kpi"><span class="v" id="dBal">—</span><span class="l">💰 الرصيد المتاح (USDT)</span></div></div>
    <div class="card"><div class="kpi"><span class="v" id="dToday">—</span><span class="l">📅 صافي الاستراتيجية اليوم</span></div></div>
    <div class="card"><div class="kpi"><span class="v" id="dOpen">—</span><span class="l">📊 مفتوحة الآن / السعة</span></div></div>
    <div class="card"><div class="kpi"><span class="v" id="dTotal">—</span><span class="l">🏆 صافي الاستراتيجية الإجمالي</span></div></div>
  </div>
  <div class="grid g3" style="margin-top:12px">
    <div class="card">
      <h3>💓 <b>نبض البوت</b> — مزامنة لحظية</h3>
      <div id="dHeart"></div>
    </div>
    <div class="card">
      <h3>🧠 <b>قواعد __NAME__</b> — ثابتة ومستقلة</h3>
      <div id="dRules"></div>
    </div>
    <div class="card">
      <h3>⚙️ <b>الإعدادات الحالية</b> (V11)</h3>
      <div id="dSettings"></div>
    </div>
  </div>
  <div class="grid g2" style="margin-top:12px">
    <div class="card">
      <h3>⚡ <b>آخر حركات __NAME__</b> — مباشر</h3>
      <div class="feed" id="dFeed"><div class="empty">لا حركات بعد</div></div>
    </div>
    <div class="card">
      <h3>⚠️ <b>سجل الأخطاء</b> (آخر دورة تشغيل)</h3>
      <div id="dErrors" style="max-height:340px;overflow:auto"></div>
    </div>
  </div>
</div>

<!-- ═════════ 💰 ربح اليوم ═════════ -->
<div class="sec" id="s-today">
  <div class="grid g4">
    <div class="card" style="border-color:var(--gold)">
      <h3>💎 <b>صافي اليوم</b> — من قاعدة الاستراتيجية</h3>
      <div class="big" id="tNet">—</div>
      <div class="note" id="tNetSub"></div>
    </div>
    <div class="card"><h3>📈 <b>العائم الحالي</b> (صفقات مفتوحة)</h3><div class="med" id="tFloat">—</div><div class="note" id="tFloatSub"></div></div>
    <div class="card"><h3>🧾 <b>العمولات التقديرية</b> لليوم</h3><div class="med" id="tFees">—</div><div class="note" id="tFeesSub"></div></div>
    <div class="card"><h3>🏆 <b>الإجمالي الكلي</b> (كل التاريخ)</h3><div class="med" id="tAll">—</div><div class="note">صافي كل صفقات هذه الاستراتيجية المغلقة منذ البداية</div></div>
  </div>
  <div class="grid g3" style="margin-top:12px">
    <div class="card"><h3>📌 <b>ملخص اليوم</b></h3><div id="tSummary"></div></div>
    <div class="card" style="grid-column:span 2"><h3>🧾 <b>صفقات اليوم</b> — بالتفصيل (من قاعدة الاستراتيجية)</h3>
      <div class="tblbox" style="max-height:380px"><table id="tTrades"></table></div>
    </div>
  </div>
  <div class="note">💡 الصافي هنا من قاعدة الاستراتيجية المستقلة. رسوم المنصة والتمويل مشتركة بين الاستراتيجيتين على نفس الحساب.</div>
</div>

<!-- ═════════ 📊 المفتوحة ═════════ -->
<div class="sec" id="s-open">
  <div class="card">
    <h3>📊 <b>صفقات __NAME__ المفتوحة الآن</b> — تحديث كل 2.5 ثانية <span id="oCount"></span></h3>
    <div class="tblbox"><table id="oTbl"></table></div>
    <div class="note">__NOTE_OPEN__</div>
  </div>
</div>

<!-- ═════════ 🗂 السجل ═════════ -->
<div class="sec" id="s-hist">
  <div class="grid g4">
    <div class="card"><div class="kpi"><span class="v" id="hTotal">—</span><span class="l">إجمالي الصفقات المغلقة</span></div></div>
    <div class="card"><div class="kpi"><span class="v" id="hWR">—</span><span class="l">نسبة الفوز الإجمالية</span></div></div>
    <div class="card"><div class="kpi"><span class="v" id="hPF">—</span><span class="l">عامل الربح (Profit Factor)</span></div></div>
    <div class="card"><div class="kpi"><span class="v" id="hNet">—</span><span class="l">الصافي التراكمي (كل التاريخ)</span></div></div>
  </div>
  <div class="grid g3" style="margin-top:12px">
    <div class="card"><h3>📈 <b>منحنى الربح التراكمي</b> — يوم بيوم</h3><svg class="spark" id="hChart" preserveAspectRatio="none"></svg><div class="note" id="hChartNote"></div></div>
    <div class="card"><h3>📊 <b>متوسطات وإحصاءات</b></h3><div id="hStats"></div></div>
    <div class="card"><h3>📅 <b>ملخص كل الأيام</b> — من قاعدة الاستراتيجية</h3>
      <div class="tblbox" style="max-height:300px"><table id="hDays"></table></div>
    </div>
  </div>
  <div class="card" style="margin-top:12px">
    <h3>🗄 <b>كل الصفقات المغلقة</b> — بالتفصيل الممل
      <select id="hDayFilter" style="margin-right:10px"><option value="">كل الأيام</option></select>
      <span class="mut" id="hCount"></span></h3>
    <div class="tblbox"><table id="hTbl"></table></div>
  </div>
</div>

<!-- ═════════ 🎛 التحكم ═════════ -->
<div class="sec" id="s-ctrl">
  <div id="cInfoBox"></div>
  <div class="grid g2">
    <div class="card">
      <h3>⏯ <b>استراتيجية __NAME__</b></h3>
      <div id="cTrade"></div>
      <div class="btnrow" style="margin-top:12px">
        <button class="btn b-green" id="cOnBtn">▶️ تفعيل الاستراتيجية</button>
        <button class="btn b-orange" id="cOffBtn">⏸️ إيقاف الاستراتيجية</button>
        <button class="btn b-blue" onclick="doKeyCloseAll()">👋 إغلاق صفقاتها المفتوحة</button>
        <button class="btn b-red" onclick="doKeyWipe()">🗑 مسح بياناتها</button>
      </div>
      <div class="note">__NOTE_CTRL__ «مسح بياناتها» يمسح سجل هذه الاستراتيجية وربح أيامها فقط — لا يلمس الاستراتيجية الأخرى.</div>
    </div>
    <div class="card">
      <h3>🛡 <b>سعة الصفقات المتزامنة</b> — مستقلة تماماً</h3>
      <div id="cCaps"></div>
    </div>
    <div class="card">
      <h3>🔗 <b>الأدوات العامة</b> — مشتركة بين الاستراتيجيتين</h3>
      <div id="cGlobal"></div>
      <div class="btnrow" style="margin-top:12px">
        <button class="btn b-orange" id="cPauseBtn">⏸️ إيقاف مؤقت (الكل)</button>
        <button class="btn b-green" id="cResumeBtn">▶️ استئناف</button>
        <button class="btn b-blue" onclick="doBalance()">🔄 تحديث الرصيد</button>
      </div>
      <div class="btnrow" style="margin-top:10px">
        <button class="btn b-red" onclick="doEmergency()">🚨 وضع الطوارئ (إغلاق الكل + قفل)</button>
        <button class="btn b-gray" onclick="doEmergencyReset()">🔓 إلغاء الطوارئ</button>
      </div>
      <div class="btnrow" style="margin-top:10px">
        <button class="btn b-red" onclick="doStop()">🛑 إيقاف البوت بأمان</button>
        <button class="btn b-orange" onclick="doWipeAll()">💣 مسح شامل لكل البيانات</button>
      </div>
      <div class="note">وضع الطوارئ يُغلق كل الصفقات (الاستراتيجيتين + المتبنّى) ويقفل الدخول حتى تلغيه يدوياً. «إيقاف البوت» إيقاف آمن — ستوب/أوامر الهدف على المنصة تبقى تحمي المراكز. «المسح الشامل» يمسح كل الجداول والسجلات نهائياً.</div>
    </div>
    <div class="card">
      <h3>📊 <b>ملخص الأداء</b></h3>
      <div id="cSummary"></div>
    </div>
  </div>
  <div class="card" style="margin-top:12px">
    <h3>💾 <b>حالة قاعدة بيانات الاستراتيجية</b> — التاريخ ينجو من إعادة النشر</h3>
    <div id="cDb"></div>
  </div>
</div>
</div>
"""
_TPL_JS = r"""
<script>
'use strict';
let SRV_OFF = 0, LAST_SYNC = 0, CUR_TAB = 's-dash';
let LAST_OV = null, LAST_TODAY = null;

const $ = id => document.getElementById(id);
const esc = s => String(s??'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const mo = (x, d=2) => (x>=0?'+':'') + Number(x).toFixed(d);
const mono = x => '<span class="mono">' + x + '</span>';
const kv = (a,b) => '<div class="kv"><span>'+a+'</span><b>'+b+'</b></div>';
async function api(p, opts){ const r = await fetch(p, opts);
  const j = await r.json().catch(()=>({ok:false,error:'رد غير صالح'}));
  if(!r.ok) throw new Error(j.error || ('HTTP '+r.status)); return j; }
const ago = ts => { const s = Math.max(0, Math.floor((Date.now()+SRV_OFF)/1000 - ts));
  if(s<60) return 'قبل '+s+' ث'; if(s<3600) return 'قبل '+Math.floor(s/60)+' د';
  if(s<86400) return 'قبل '+Math.floor(s/3600)+' س'; return 'قبل '+Math.floor(s/86400)+' يوم'; };
const dur = s => { s=Math.round(s||0); if(s<60) return s+' ث';
  if(s<3600) return Math.floor(s/60)+' د '+(s%60)+' ث';
  const h=Math.floor(s/3600); return h+' س '+Math.floor((s%3600)/60)+' د'; };
const cl = v => v>0?'pos':(v<0?'neg':'mut');

/* ─── الساعة الحية (مزامنة مع خادم البوت) ─── */
function tickClock(){
  const d = new Date(Date.now() + SRV_OFF);
  const p = n => String(n).padStart(2,'0');
  $('clock').innerHTML = p(d.getHours())+':'+p(d.getMinutes())+':'+p(d.getSeconds())+
    '<small>' + d.toLocaleDateString('ar', {weekday:'long', year:'numeric', month:'long', day:'numeric'}) + '</small>';
}
setInterval(tickClock, 1000);

/* ─── التبويبات ─── */
document.querySelectorAll('.tab').forEach(t => t.onclick = () => {
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('on'));
  document.querySelectorAll('.sec').forEach(x=>x.classList.remove('on'));
  t.classList.add('on'); CUR_TAB = t.dataset.s; $(''+CUR_TAB).classList.add('on');
  if(CUR_TAB==='s-hist') loadHistory();
  if(CUR_TAB==='s-today' && LAST_TODAY) renderToday(LAST_TODAY, LAST_OV);
});

/* ─── الحلقة السريعة: كل 2.5 ثانية ─── */
async function loadAll(){
  const [ov, tr, td] = await Promise.all([api('/api/__KEY__/panel'), api('/api/__KEY__/trades'), api('/api/__KEY__/today')]);
  LAST_OV = ov; LAST_TODAY = td;
  SRV_OFF = (ov.server_ts * 1000) - Date.now(); tickClock();
  LAST_SYNC = Date.now();
  $('syncBadge').innerHTML = '<span class="dot g"></span>متزامن لحظياً';
  $('syncBadge').className = 'badge b-ok';
  renderTop(ov); renderDash(ov, td); renderOpen(tr); renderToday(td, ov); renderControl(ov);
}
setInterval(() => loadAll().catch(syncFail), 2500);
function syncFail(e){
  $('syncBadge').innerHTML = '<span class="dot r"></span>انقطع الاتصال — إعادة محاولة';
  $('syncBadge').className = 'badge b-bad';
  $('hbBadge').textContent = 'البوت غير متصل';
}
setInterval(() => { if(LAST_SYNC && Date.now()-LAST_SYNC > 8000){
  $('syncBadge').innerHTML = '<span class="dot r"></span>تأخر البيانات ('+ago(LAST_SYNC/1000)+')';
  $('syncBadge').className = 'badge b-warn'; } }, 3000);

/* ─── الشريط العلوي ─── */
function renderTop(ov){
  $('ver').textContent = 'لوحة ' + (ov.panel_version||'V11') + ' • بوت ثنائي';
  const mb = $('modeBadge');
  if(ov.emergency){ mb.textContent='🚨 وضع الطوارئ'; mb.className='badge b-emg'; }
  else if(!ov.key_enabled){ mb.textContent='🔴 الاستراتيجية متوقفة'; mb.className='badge b-bad'; }
  else if(ov.trade_enabled){ mb.textContent='🟢 التداول مفعّل'; mb.className='badge b-ok'; }
  else { mb.textContent='⏸️ التداول موقوف'; mb.className='badge b-warn'; }
  $('emgBadge').style.display = ov.emergency ? '' : 'none';
  const hb = $('hbBadge');
  if(ov.own_scan_age_s < 3600){
    hb.innerHTML = '<span class="dot g"></span>مسح ' + ago(ov.own_scan_ts) + ' (' + (ov.own_last.scanned||0) + ' زوجاً)';
    hb.className='badge b-ok';
  } else {
    hb.innerHTML = '<span class="dot r"></span>لا مسح بعد';
    hb.className='badge b-bad';
  }
}

/* ─── الرئيسية ─── */
function renderDash(ov, td){
  $('dBal').textContent = (ov.balance||0).toFixed(2) + ' $';
  const net = td ? td.db_today_pnl : 0;
  const e1 = $('dToday'); e1.textContent = mo(net) + ' $'; e1.className = 'v ' + cl(net);
  $('dOpen').textContent = ov.open_trades + ' / ' + ov.max_open;
  const e2 = $('dTotal'); e2.textContent = mo(ov.all_time_net||0) + ' $'; e2.className = 'v ' + cl(ov.all_time_net||0);

  $('dHeart').innerHTML =
    kv('آخر مسح شامل للسوق', ago(ov.last_scan_ts) + mono(' (#'+ov.scans+')')) +
    kv('آخر مسح للاستراتيجية', ov.own_scan_age_s < 9999
        ? ago(ov.own_scan_ts) + mono(' ('+(ov.own_last.scanned||0)+' زوجاً)')
        : '<span class="mut">لم يبدأ بعد</span>') +
    kv('عمر آخر سعر حي', ov.price_age > 3600 ? '<b class="neg">قديم جداً</b>' : mono(ov.price_age+' ث')) +
    kv('معدل المسح', mono('كل ' + ov.loop_sec + ' ثانية')) +
    kv('مدة التشغيل', mono(dur(ov.uptime_s))) +
    kv('أزواج مرصودة', mono(ov.pairs)) +
    kv('صفقات اليوم (عدد)', mono(ov.trades_today)) +
    kv('الوضع', ov.testnet ? '🧪 Testnet تجريبي' : '🔴 حقيقي — أموال فعلية');

  $('dRules').innerHTML = (ov.rule_defs||[]).map(r => kv(r[0], r[1])).join('');
  $('dSettings').innerHTML = (ov.settings_defs||[]).map(r => kv(r[0], r[1])).join('');

  const ek = Object.keys(ov.errors||{});
  $('dErrors').innerHTML = !ek.length
    ? '<div class="empty">✅ لا أخطاء — كل شيء نظيف</div>'
    : ek.map(k => '<div class="kv err-item"><span>'+esc(k)+'</span><b>×'+ov.errors[k]+'</b></div>').join('');
}

/* ─── آخر الحركات ─── */
function renderFeed(evs){
  const box = $('dFeed');
  if(!evs || !evs.length){ box.innerHTML = '<div class="empty">لا حركات بعد — بانتظار أول إشارة 🚀</div>'; return; }
  box.innerHTML = evs.map(e =>
    '<div class="it"><div class="h">'+esc(e.msg)+'</div>'+
    '<div class="t">🕐 '+new Date(e.ts*1000).toLocaleTimeString('ar-EG',{hour:'2-digit',minute:'2-digit',second:'2-digit'})+' • '+esc(e.kind)+'</div></div>').join('');
}

/* ─── الصفقات المفتوحة ─── */
function renderOpen(tr){
  const box = $('oTbl');
  $('oCount').textContent = tr.length ? '('+tr.length+')' : '';
  if(!tr.length){ box.innerHTML = '<tr><td><div class="empty">لا صفقات مفتوحة — الاستراتيجية تراقب السوق 🔭</div></td></tr>'; renderFeed(LAST_OV&&LAST_OV.events); return; }
  let h = '<tr><th>الزوج</th><th>الاتجاه</th><th>الهامش</th><th>الدخول</th><th>السعر الحالي</th><th>الكمية</th><th>العائم</th><th>% الهامش'+
          '</th><th>جُني جزئي</th><th>الوقف SL</th><th>المسافة للوقف</th><th>الهدف</th><th>التقدم للهدف</th><th>هدف 2</th>'+
          '<th>التريلينق</th><th>أعلى/أدنى</th><th>عمر الصفقة</th><th>النوع</th></tr>';
  tr.forEach(t => {
    const pnlCls = cl(t.pnl||0);
    const prog = p => '<div class="bar"><i style="width:'+Math.max(0,Math.min(100,p))+'%;background:'+
      (p>=100?'var(--green)':(p>50?'var(--gold)':'var(--blue)'))+'"></i></div>' +
      '<span class="mut mono" style="font-size:10px">'+p.toFixed(0)+'%</span>';
    h += '<tr><td><b>'+esc(t.symbol)+'</b></td>'
      + '<td><span class="tag '+(t.side==='BUY'?'buy':'sell')+'">'+(t.side==='BUY'?'▲ شراء':'▼ بيع')+'</span></td>'
      + '<td>'+mono(t.entry)+'</td><td>'+mono(t.current??'—')+'</td>'
      + '<td style="color:var(--gold);font-weight:700">'+(t.margin!=null?mono(t.margin)+' $':'—')+'</td>'
      + '<td>'+mono(t.qty)+'</td>'
      + '<td class="'+pnlCls+'"><b>'+mono(t.pnl===null?'—':mo(t.pnl)+' $')+'</b></td>'
      + '<td class="'+pnlCls+'">'+(t.pnl_pct===null?'—':mono(mo(t.pnl_pct,1)+'%'))+'</td>'
      + '<td class="'+cl(t.realized)+'">'+mono(t.realized?mo(t.realized)+' $':'—')+'</td>'
      + '<td class="neg">'+mono(t.sl)+'</td>'
      + '<td class="'+(t.sl_dist_pct>0?'neg':'pos')+'">'+mono(mo(t.sl_dist_pct,2)+'%')+'</td>'
      + '<td class="pos">'+mono(t.tp1??'—')+'</td><td>'+prog(t.tp1_prog||0)+'</td>'
      + '<td class="mut">'+(t.tp2!=null?mono(t.tp2):'—')+'</td>'
      + '<td>'+(t.trailing===null?'<span class="mut">—</span>':(t.trailing?'<span class="tag win">🏃 مفعل</span>':'<span class="tag open">انتظار</span>'))+'</td>'
      + '<td class="mut mono" style="font-size:11px">'+t.hi+' / '+t.lo+'</td>'
      + '<td>'+mono(dur(t.age_s))+'</td>'
      + '<td class="mut">'+esc(t.kind||'—')+'</td></tr>';
  });
  box.innerHTML = h;
  renderFeed(LAST_OV&&LAST_OV.events);
}

/* ─── ربح اليوم ─── */
function renderToday(td, ov){
  const set = (id, v, cls) => { const e=$(id); e.textContent = v; if(cls!==undefined) e.className = e.className.split(' ')[0]+' '+cls; };
  set('tNet', mo(td.db_today_pnl)+' $', cl(td.db_today_pnl));
  $('tNetSub').textContent = 'من قاعدة الاستراتيجية المحلية — pnl الصفقات المغلقة اليوم';
  set('tFloat', mo(td.floating||0)+' $', cl(td.floating||0));
  $('tFloatSub').textContent = 'العائم الحالي للصفقات المفتوحة (يشمل المحقق الجزئي)';
  set('tFees', mo(td.fees_est||0)+' $', 'neg');
  $('tFeesSub').textContent = 'تقديري: ' + ((td.wins||0)+(td.losses||0)) + ' إغلاقاً اليوم — رسوم المنصة مشتركة بين الاستراتيجيتين';
  const allNet = (ov&&ov.all_time_net)||0;
  set('tAll', mo(allNet)+' $', cl(allNet));
  $('tSummary').innerHTML =
    kv('صفقات دخلت اليوم', mono(td.trades_count)) +
    kv('رابحة / خاسرة اليوم', '<span class="pos">'+td.wins+'</span> / <span class="neg">'+td.losses+'</span>') +
    kv('مفتوحة الآن', mono(td.open_now)) +
    kv('PnL القاعدة (بعد الإغلاقات)', mono(mo(td.db_today_pnl)+' $')) +
    kv('السعة', mono(td.open_now + ' / ' + ((ov&&ov.max_open)||0)));

  let h = '<tr><th>الوقت</th><th>الزوج</th><th>الاتجاه</th><th>التفعيل</th><th>الحالة</th><th>النتيجة</th><th>% من الهامش</th><th>المدة</th></tr>';
  (td.trades||[]).forEach(t => {
    const open = t.result === -1 || t.result === null;
    h += '<tr><td class="mono">'+t.time+'</td><td><b>'+esc(t.symbol)+'</b></td>'
      + '<td><span class="tag '+(t.direction==='BUY'?'buy':'sell')+'">'+(t.direction==='BUY'?'شراء':'بيع')+'</span></td>'
      + '<td class="mut">'+esc(t.trigger||'—')+'</td>'
      + '<td>'+(open?'<span class="tag open">⏳ جارية</span>':(t.result?'<span class="tag win">ربح</span>':'<span class="tag loss">خسارة</span>'))+'</td>'
      + '<td class="'+cl(t.pnl||0)+'"><b>'+(t.pnl===null?'—':mono(mo(t.pnl)+' $'))+'</b></td>'
      + '<td>'+(t.pnl_pct!=null?mono(mo(t.pnl_pct,1)+'%'):'—')+'</td>'
      + '<td class="mut">'+(t.duration_s!=null?mono(dur(t.duration_s)):'—')+'</td></tr>';
  });
  $('tTrades').innerHTML = h || '<tr><td><div class="empty">لا صفقات اليوم بعد — الانتظار جزء من الاستراتيجية</div></td></tr>';
}

/* ─── السجل والأيام ─── */
async function loadHistory(){
  const h = await api('/api/__KEY__/history');
  $('hTotal').textContent = h.agg.total_closed;
  $('hWR').textContent = h.agg.overall_winrate!=null ? h.agg.overall_winrate+'%' : '—';
  $('hPF').textContent = h.agg.profit_factor!=null ? h.agg.profit_factor : '—';
  const e = $('hNet'); e.textContent = mo(h.agg.total_pnl)+' $'; e.className = 'v '+cl(h.agg.total_pnl);
  $('hStats').innerHTML =
    kv('أرباح الصفقات الرابحة', '<span class="pos">'+mono(mo(h.agg.gross_win)+' $')+'</span>') +
    kv('خسائر الصفقات الخاسرة', '<span class="neg">'+mono(mo(h.agg.gross_loss)+' $')+'</span>') +
    kv('متوسط الصفقة الرابحة', '<span class="pos">'+mono(mo(h.agg.avg_win)+' $')+'</span>') +
    kv('متوسط الصفقة الخاسرة', '<span class="neg">'+mono(mo(h.agg.avg_loss)+' $')+'</span>') +
    kv('أفضل صفقة', '<span class="pos">'+mono(mo(h.agg.best_trade.pnl)+' $')+'</span> <span class="mut">('+esc(h.agg.best_trade.symbol)+' — '+h.agg.best_trade.date+')</span>') +
    kv('أسوأ صفقة', '<span class="neg">'+mono(mo(h.agg.worst_trade.pnl)+' $')+'</span> <span class="mut">('+esc(h.agg.worst_trade.symbol)+' — '+h.agg.worst_trade.date+')</span>') +
    kv('أفضل يوم', '<span class="pos">'+mono(mo(h.agg.best_day.pnl)+' $')+'</span> <span class="mut">('+h.agg.best_day.date+')</span>') +
    kv('أسوأ يوم', '<span class="neg">'+mono(mo(h.agg.worst_day.pnl)+' $')+'</span> <span class="mut">('+h.agg.worst_day.date+')</span>') +
    kv('أيام نشطة', mono(h.agg.active_days+' يوم')) +
    kv('إجمالي العمولات المدفوعة (تقديري)', mono(mo(h.agg.est_fees)+' $'));
  drawChart(h.curve);

  let dh = '<tr><th>اليوم</th><th>الصفقات</th><th>ربح</th><th>خسارة</th><th>نسبة الفوز</th><th>PnL اليوم</th><th>تراكمي</th></tr>';
  h.days.forEach(d => {
    dh += '<tr><td><b>'+d.date+'</b></td><td>'+d.total+'</td>'
      + '<td class="pos">'+d.wins+'</td><td class="neg">'+d.losses+'</td>'
      + '<td>'+(d.winrate!=null?mono(d.winrate+'%'):'—')+'</td>'
      + '<td class="'+cl(d.pnl)+'"><b>'+mono(mo(d.pnl)+' $')+'</b></td>'
      + '<td class="'+cl(d.cum)+'">'+mono(mo(d.cum)+' $')+'</td></tr>';
  });
  $('hDays').innerHTML = dh || '<tr><td><div class="empty">لا أيام مسجلة بعد</div></td></tr>';

  const sel = $('hDayFilter');
  if(sel.options.length <= 1){
    h.days.forEach(d => { const o = document.createElement('option'); o.value = d.date; o.textContent = d.date; sel.appendChild(o); });
    sel.onchange = loadClosed;
  }
  loadClosed();
}
async function loadClosed(){
  const day = $('hDayFilter').value;
  const rows = await api('/api/__KEY__/closed' + (day ? '?date='+day : ''));
  let h = '<tr><th>فتحت</th><th>أُغلقت</th><th>الزوج</th><th>الاتجاه</th><th>التفعيل</th><th>سبب الإغلاق</th><th>المدة</th><th>النتيجة</th><th>% من الهامش</th></tr>';
  rows.forEach(t => {
    h += '<tr><td class="mono">'+t.open_time+'</td><td class="mono">'+(t.close_time||'—')+'</td>'
      + '<td><b>'+esc(t.symbol)+'</b></td>'
      + '<td><span class="tag '+(t.direction==='BUY'?'buy':'sell')+'">'+(t.direction==='BUY'?'شراء':'بيع')+'</span></td>'
      + '<td class="mut">'+esc(t.trigger||'—')+'</td>'
      + '<td class="mut" style="max-width:210px;white-space:normal">'+esc(t.reason||'—')+'</td>'
      + '<td>'+(t.duration_s!=null?mono(dur(t.duration_s)):'—')+'</td>'
      + '<td class="'+cl(t.pnl)+'"><b>'+mono(mo(t.pnl)+' $')+'</b></td>'
      + '<td class="'+cl(t.pnl)+'">'+(t.pnl_pct!=null?mono(mo(t.pnl_pct,1)+'%'):'—')+'</td></tr>';
  });
  $('hTbl').innerHTML = h || '<tr><td><div class="empty">لا صفقات مغلقة'+(day?' في '+esc(day):'')+' بعد</div></td></tr>';
  $('hCount').textContent = '('+rows.length+' صفقة)';
}
function drawChart(curve){
  const svg = $('hChart');
  if(!curve || curve.length < 2){ svg.innerHTML = '<text x="50%" y="50%" fill="#7c8aa5" text-anchor="middle">لا بيانات كافية للرسم بعد</text>'; $('hChartNote').textContent=''; return; }
  const W=600, H=130, P=8;
  const vals = curve.map(p=>p.cum), mn = Math.min(...vals,0), mx = Math.max(...vals,0.01);
  const X = i => P + i*(W-2*P)/(curve.length-1);
  const Y = v => H-P - (v-mn)/(mx-mn)*(H-2*P);
  const pts = curve.map((p,i)=>X(i).toFixed(1)+','+Y(p.cum).toFixed(1)).join(' ');
  const zero = Y(0).toFixed(1);
  svg.setAttribute('viewBox','0 0 '+W+' '+H);
  svg.innerHTML = '<line x1="0" y1="'+zero+'" x2="'+W+'" y2="'+zero+'" stroke="#1e293b" stroke-dasharray="4 3"/>'
    + '<polygon points="'+X(0)+','+(H-P)+' '+pts+' '+X(curve.length-1)+','+(H-P)+'" fill="rgba(139,92,246,.08)"/>'
    + '<polyline points="'+pts+'" fill="none" style="stroke:var(--gold)" stroke-width="2"/>'
    + '<circle cx="'+X(curve.length-1)+'" cy="'+Y(vals[vals.length-1])+'" r="3.5" style="fill:var(--gold)"/>';
  $('hChartNote').textContent = 'من '+curve[0].date+' إلى '+curve[curve.length-1].date+' — تراكمي '+mo(vals[vals.length-1])+' $';
}

/* ─── التحكم ─── */
function renderControl(ov){
  $('cTrade').innerHTML =
    kv('حالة الاستراتيجية', ov.key_enabled ? '<span class="pos">🟢 مفعّلة — تراقب السوق وتدخل</span>' : '<span class="neg">🔴 متوقفة — مراقبة فقط</span>') +
    kv('التداول العام', ov.trade_enabled ? '<span class="pos">🟢 مفعّل (مشترك)</span>' : '<span class="neg">⏸️ موقوف (مشترك)</span>') +
    kv('وضع الطوارئ', ov.emergency ? '<span class="neg">🚨 مفعّل — كل الدخول مقفول</span>' : 'غير مفعل') +
    kv('المفاتيح', ov.has_keys ? 'موجودة ✅' : 'غير مضبوطة ❌');
  $('cOnBtn').disabled = !!ov.key_enabled;
  $('cOffBtn').disabled = !ov.key_enabled;
  $('cCaps').innerHTML =
    kv('سعة هذه الاستراتيجية', mono(ov.max_open + ' صفقة')) +
    kv('سعة ' + esc(ov.other_name||'الاستراتيجية الأخرى'), mono(ov.other_cap + ' صفقة')) +
    kv('السقف الإجمالي (الاستراتيجيتان)', ov.total_cap>0 ? mono(ov.total_cap + ' صفقة') : 'بلا سقف') +
    kv('الهامش / الرافعة', mono('$'+ov.trade_size + ' / ' + ov.leverage + 'x'));
  $('cGlobal').innerHTML =
    kv('الرصيد المتاح', mono((ov.balance||0).toFixed(2)+' $')) +
    kv('إجمالي المفتوح (الكل)', mono(ov.total_open + ' صفقة')) +
    kv('أزواج مرصودة', mono(ov.pairs));
  $('cSummary').innerHTML =
    kv('أداء 30 يوماً', ov.perf30.winrate!=null ? mono(ov.perf30.winrate+'% فوز على '+ov.perf30.closed+' صفقة') : '<span class="mut">لا صفقات مغلقة بعد</span>') +
    kv('الصافي الكلي', mono(mo(ov.all_time_net||0)+' $')) +
    kv('صفقات مسجلة', mono(ov.db_rows.trades||0)) +
    kv('أيام مسجلة', mono(ov.db_rows.days||0));
  $('cInfoBox').innerHTML = ov.emergency
    ? '<div class="warnbox">🚨 وضع الطوارئ مفعّل — كل الدخول مقفول للاستراتيجيتين. الصفقات المفتوحة أُغلقت أو تُدار حتى إغلاقها.</div>'
    : (!ov.key_enabled ? '<div class="warnbox">🔴 هذه الاستراتيجية متوقفة — لن تُفتح صفقات جديدة. الصفقات المفتوحة تُدار بقواعدها حتى إغلاقها. اضغط «تفعيل الاستراتيجية» للعودة.</div>' : '');
  $('cDb').innerHTML =
    kv('ملف القاعدة', mono(esc(ov.db_name||'sniper_v8.db'))) +
    kv('صفقات مسجلة ('+esc(ov.table_trades)+')', mono(ov.db_rows.trades)) +
    kv('منها مفتوحة محفوظة', mono(ov.db_rows.open)) +
    kv('أيام مسجلة ('+esc(ov.table_daily)+')', mono(ov.db_rows.days)) +
    kv('الحماية', '💾 كل التاريخ محفوظ دائماً — يعود كاملاً بعد إعادة النشر أو إعادة التشغيل');
}
async function act(path, body){
  try{ return await api(path, {method:'POST', headers:{'Content-Type':'application/json'},
       body: JSON.stringify(body||{})}); }catch(e){ alert('فشل: '+e.message); return null; }
}
async function doKeyOn(){ if(await act('/api/__KEY__/enable')) loadAll(); }
async function doKeyOff(){ if(await act('/api/__KEY__/disable')) loadAll(); }
async function doKeyCloseAll(){
  if(!confirm('👋 سيتَّم إغلاق كل صفقات هذه الاستراتيجية المفتوحة بسعر السوق (الاستراتيجية الأخرى لا تُلمس).\nهل أنت متأكد؟')) return;
  const r = await act('/api/__KEY__/close-all');
  if(r){ alert('تم! أُغلق: ' + (r.closed.length ? r.closed.join(', ') : 'لا صفقات مفتوحة')); loadAll(); }
}
async function doKeyWipe(){
  const w = prompt('🗑 سيُمسح سجل هذه الاستراتيجية وربح الأيام والأحداث نهائياً (لا يلمس الاستراتيجية الأخرى).\nاكتب كلمة: حذف للتأكيد','');
  if(w !== 'حذف'){ if(w!==null) alert('لم تُكتب كلمة التأكيد — أُلغي المسح'); return; }
  const r = await act('/api/__KEY__/wipe');
  if(r){ alert('تم المسح: ' + (r.deleted||'')); loadAll(); }
}
async function doBalance(){ const r = await act('/api/balance'); if(r){ alert('الرصيد المتاح: ' + r.balance + ' $'); loadAll(); } }
async function doPause(){ if(await act('/api/pause')) loadAll(); }
async function doResume(){ const r = await act('/api/resume'); if(r&&r.ok) loadAll(); else if(r) alert(r.error||'فشل'); }
async function doEmergency(){
  if(!confirm('🚨 سيتم إغلاق كل الصفقات المفتوحة (الاستراتيجيتين) فوراً بسعر السوق + قفل أي دخول جديد حتى تلغيه يدوياً.\nهل أنت متأكد؟')) return;
  const r = await act('/api/emergency');
  if(r){ alert('وضع الطوارئ مفعّل. أُغلق: ' + (r.closed.length ? r.closed.join(', ') : 'لا صفقات مفتوحة')); loadAll(); }
}
async function doEmergencyReset(){ const r = await act('/api/emergency-reset'); if(r){ alert('أُلغي وضع الطوارئ — التداول ما زال موقوفاً، اضغط استئناف'); loadAll(); } }
async function doStop(){
  if(!confirm('🛑 إيقاف آمن للبوت بالكامل. ستوب/أوامر الهدف على المنصة تبقى تحمي المراكز.\nهل أنت متأكد؟')) return;
  const r = await act('/api/stop-bot');
  if(r&&r.ok) alert('تم طلب الإيقاف — سيتوقف البوت خلال ≤60 ثانية وتنقطع اللوحة');
  else if(r) alert(r.error||'فشل');
}
async function doWipeAll(){
  const w = prompt('💣 مسح شامل نهائي: كل سجلات الاستراتيجيتين + سجل الإشارات + أرباح الأيام + الإعدادات المحفوظة.\nاكتب كلمة: حذف للتأكيد','');
  if(w !== 'حذف'){ if(w!==null) alert('لم تُكتب كلمة التأكيد — أُلغي المسح'); return; }
  const r = await act('/api/wipe');
  if(r){ alert('تم المسح: ' + (r.deleted||'')); loadAll(); }
}
$('cOnBtn').onclick = doKeyOn; $('cOffBtn').onclick = doKeyOff;
$('cPauseBtn').onclick = doPause; $('cResumeBtn').onclick = doResume;

tickClock();
loadAll().catch(syncFail);
</script>
</body>
</html>"""

PAGE_TEMPLATE = _TPL_HTML + _TPL_JS


def render_page(key):
    """يُركّب صفحة اللوحة من القالب الواحد باختلاف الاستراتيجية."""
    m = STRATEGY_META[key]
    return (PAGE_TEMPLATE
            .replace('__KEY__', key)
            .replace('__NAME__', m['name'])
            .replace('__LOGO__', m['logo'])
            .replace('__ACCENT__', m['accent'])
            .replace('__NOTE_OPEN__', m['note_open'])
            .replace('__NOTE_CTRL__', m['note_ctrl'])
            .replace('__TABS__', tab_bar(key, m['accent'])))

# ═══════════════════════ معالجات كل استراتيجية (مصنع واحد للوحتين) ═══════════════════════
def _strategy_handlers(bot, m):
    key = m['key']
    strat = getattr(bot, m['attr'])
    events = getattr(bot, m['events_attr'])
    tables = m['tables']          # (trades_table, daily_table)
    persist_key = m['persist']
    other = STRATEGY_META[m['other_key']]

    def _own_open():
        return {s: t for s, t in getattr(bot, 'active_trades', {}).items()
                if t.get('strategy') == m['skey']}

    async def _persist_cfg():
        try:
            await bot.db.set_param(persist_key, json.dumps(dict(strat.cfg)))
        except Exception:
            pass

    def _rule_defs(cfg, perf30):
        p30 = (f"{perf30['winrate']}% فوز على {perf30['closed']} صفقة"
               if perf30.get('winrate') is not None else 'لا صفقات مغلقة بعد')
        if key == 'trend':
            return [
                ['الاختراق', f"أعلى/أدنى {cfg.get('donch')} شمعة ساعة"],
                ['فلتر الاتجاه', 'اتجاه 4 ساعات EMA20/50'],
                ['وقف الخسارة', f"{cfg.get('sl_atr1h')} × ATR(1h)"],
                ['الجني الجزئي', f"{int((cfg.get('partial') or 0)*100)}% عند {cfg.get('tp1_r')}R"],
                ['الوقف المتحرك', f"{cfg.get('trail_atr')} × ATR بعد الجني"],
                ['الخروج الزمني', f"{round((cfg.get('max_hold_minutes') or 0)/1440)} أيام"],
                ['فلتر ATR(1h)', f"{cfg.get('min_atr_pct')}% – {cfg.get('max_atr_pct')}%"],
                ['أقصى مخاطرة للصفقة', f"{cfg.get('max_risk_pct')}%"],
                ['أداء 30 يوماً', p30],
            ]
        return [
            ['الدخول شراء', 'MA7 قطعت 25/99 صعوداً (آخر 6 شمعات 15د) + إغلاق بزخم فوق MA7/MA25'],
            ['الدخول بيع', 'MA7 قطعت 25/99 هبوطاً (آخر 3 شمعات ساعة) + إغلاق بزخم تحت MA7/MA25'],
            ['وقف الخسارة', f"{cfg.get('sl_atr1h')} × ATR(1h)"],
            ['الهدف', f"ثابت {cfg.get('tp_r')}R = {round((cfg.get('tp_r') or 0)*(cfg.get('sl_atr1h') or 0),1)} × ATR(1h)"],
            ['الجني الجزئي', 'لا يوجد — الهدف ثابت 2R'],
            ['فلتر المخاطرة', f"رفض أي وقف أكبر من {cfg.get('max_risk_pct')}% من السعر (قرب التصفية عند 10x)"],
            ['الخروج الزمني', f"{round((cfg.get('max_hold_minutes') or 0)/1440)} أيام"],
            ['أداء الاختبار المعتمد', 'فوز 55.20% — فترة التحقق المستقلة (التركيبة المعدلة)'],
            ['أداء 30 يوماً', p30],
        ]

    async def _db_stats():
        """صفوف القاعدة + صافي الكل + أداء 30 يوماً."""
        out = {'trades': 0, 'open': 0, 'days': 0, 'all_net': 0.0,
               'perf30': {'winrate': None, 'closed': 0, 'net': 0.0}, 'today_count': 0}
        day_ts = _day_start_ts()
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                async with db.execute(f"SELECT COUNT(*) c FROM {tables[0]}") as cur:
                    out['trades'] = (await cur.fetchone())[0]
                async with db.execute(f"SELECT COUNT(*) c FROM {tables[0]} WHERE win=-1") as cur:
                    out['open'] = (await cur.fetchone())[0]
                async with db.execute(f"SELECT COUNT(*) c FROM {tables[1]}") as cur:
                    out['days'] = (await cur.fetchone())[0]
                async with db.execute(
                        f"SELECT COALESCE(SUM(pnl),0) p FROM {tables[0]} WHERE win>=0") as cur:
                    out['all_net'] = (await cur.fetchone())[0] or 0.0
                async with db.execute(
                        f"SELECT COUNT(*) c FROM {tables[0]} WHERE entry_ts>=?", (day_ts,)) as cur:
                    out['today_count'] = (await cur.fetchone())[0]
                async with db.execute(
                        f"""SELECT COUNT(*) n, SUM(win=1) w, COALESCE(SUM(pnl),0) p
                            FROM {tables[0]} WHERE win>=0 AND exit_ts>=?""",
                        (time.time() - 30 * 86400,)) as cur:
                    r = await cur.fetchone()
                    closed30 = r[0] or 0
                    out['perf30'] = {'winrate': round((r[1] or 0) / closed30 * 100, 1) if closed30 else None,
                                     'closed': closed30, 'net': round(r[2] or 0.0, 4)}
        except Exception:
            pass
        return out

    # ─── صفحة اللوحة ───
    async def page(request):
        return web.Response(text=render_page(key), content_type='text/html',
                            headers={'Cache-Control': 'no-store, must-revalidate'})

    # ─── نظرة عامة ───
    async def panel(request):
        cfg = strat.cfg
        st = await _db_stats()
        own_scan = getattr(strat, 'last_scan', {}) or {}
        scan = getattr(bot, 'last_scan_info', None) or {}
        newest = max((p.get('ts', 0) for p in getattr(bot, 'live_prices', {}).values()), default=0)
        scan_ts = scan.get('ts', 0) if isinstance(scan, dict) else 0
        own_ts = own_scan.get('ts', 0)
        cap = _num(bot, m['cap_attr'], 5)
        return web.json_response({
            'ok': True, 'server_ts': time.time(),
            'panel_version': PANEL_VERSION, 'bot_version': 'V11',
            'strategy': m['skey'], 'strategy_name': m['name'],
            'key_enabled': bool(cfg.get('enabled')),
            'trade_enabled': bot.TRADE_ENABLED, 'emergency': bot.EMERGENCY_MODE,
            'testnet': bot.TESTNET, 'has_keys': bool(bot.binance_api_key),
            'leverage': bot.LEVERAGE,
            'trade_size': round(bot.strategy_margin(m['skey']), 2),
            'max_open': cap,
            'other_name': other['logo'], 'other_cap': bot.strategy_capacity(other['skey']),
            'total_cap': getattr(bot, 'max_total_trades', 0),
            'total_open': len(getattr(bot, 'active_trades', {}) or {}),
            'pairs': len(getattr(bot, 'all_futures_pairs', []) or []),
            'balance': round(bot._balance_cache[0], 2) if bot._balance_cache[1] > 0 else 0.0,
            'open_trades': len(_own_open()),
            'trades_today': st['today_count'],
            'scans': bot.stats.get('total_scans', 0),
            'last_scan_ts': scan_ts,
            'scan_age_s': int(time.time() - scan_ts) if scan_ts else 999999,
            'own_scan_ts': own_ts,
            'own_scan_age_s': int(time.time() - own_ts) if own_ts else 999999,
            'own_last': {'scanned': own_scan.get('scanned', 0),
                         'signals': own_scan.get('signals', 0)},
            'loop_sec': 60,
            'uptime_s': int(time.time() - PANEL_START),
            'price_age': int(time.time() - newest) if newest else 999999,
            'rule_defs': _rule_defs(cfg, st['perf30']),
            'settings_defs': [
                ['الرافعة', f"{bot.LEVERAGE}x"],
                ['هامش الصفقة', f"${round(bot.strategy_margin(m['skey']), 2)}"],
                ['حجم المركز', f"${round(bot.strategy_margin(m['skey']) * bot.LEVERAGE, 2)}"],
                ['صفقات متزامنة (هذه)', str(cap)],
                ['صفقات متزامنة (الأخرى)', str(bot.strategy_capacity(other['skey']))],
                ['السقف الإجمالي', str(getattr(bot, 'max_total_trades', 0))],
                ['النسخة', 'V11'],
            ],
            'perf30': st['perf30'],
            'errors': dict(getattr(bot, 'error_counts', {})),
            'all_time_net': round(st['all_net'], 4),
            'db_name': bot.db.db_name, 'db_rows': {'trades': st['trades'], 'open': st['open'], 'days': st['days']},
            'table_trades': tables[0], 'table_daily': tables[1],
            'events': list(reversed(list(events)))[:80],
        }, headers={'Cache-Control': 'no-store'})

    # ─── الصفقات المفتوحة ───
    async def trades(request):
        out = []
        default_margin = bot.strategy_margin(m['skey'])
        for symbol, t in list(_own_open().items()):
            prices = bot.get_price(symbol)
            cur = pnl = None
            if prices:
                cur = prices['bid'] if t['side'] == 'BUY' else prices['ask']
                diff = (cur - t['entry_price']) if t['side'] == 'BUY' else (t['entry_price'] - cur)
                pnl = diff * t['quantity'] + t.get('realized_pnl', 0.0)
            entry = t['entry_price']
            is_buy = t['side'] == 'BUY'

            def prog_to(target):
                if not cur or not target or abs(target - entry) < 1e-12:
                    return 0.0
                return max(0.0, min(100.0, ((cur - entry) if is_buy else (entry - cur))
                                          / abs(target - entry) * 100))

            sl_dist = 0.0
            if cur and t.get('sl') and abs(cur) > 1e-12:
                sl_dist = (t['sl'] - cur) / cur * 100 if is_buy else (cur - t['sl']) / cur * 100
            margin = float(t.get('margin_usdt') or default_margin)
            comp = t.get('components') or {}
            if m['skey'] == 'MARS':
                trailing = None        # لا تريلينق في استراتيجية الموجات
            else:
                trailing = bool(t.get('partial_closed'))
            out.append({
                'symbol': symbol, 'side': t['side'],
                'margin': round(margin, 2),
                'entry': round(entry, 8),
                'current': round(cur, 8) if cur else None,
                'qty': t['quantity'],
                'notional': round(t['quantity'] * entry, 2),
                'pnl': round(pnl, 4) if pnl is not None else None,
                'pnl_pct': round(pnl / margin * 100, 2) if pnl is not None and margin else None,
                'realized': round(t.get('realized_pnl', 0.0), 4),
                'sl': round(t['sl'], 8),
                'sl_dist_pct': round(sl_dist, 2),
                'tp1': round(t['tp'], 8) if t.get('tp') else None,
                'tp1_prog': round(prog_to(t.get('tp')), 1),
                'tp2': round(t['tp2'], 8) if t.get('tp2') else None,
                'trailing': trailing,
                'hi': t.get('highest_price'), 'lo': t.get('lowest_price'),
                'age_s': int(time.time() - t.get('entry_time', time.time())),
                'kind': comp.get('trigger') or (m['name']),
            })
        out.sort(key=lambda x: x['age_s'])
        return web.json_response(out, headers={'Cache-Control': 'no-store'})

    # ─── ربح اليوم ───
    async def today(request):
        day_ts = _day_start_ts()
        db_pnl, wins, losses = 0.0, 0, 0
        rows = []
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                        f"SELECT pnl, wins, losses FROM {tables[1]} WHERE date=?",
                        (time.strftime('%Y-%m-%d'),)) as cur:
                    r = await cur.fetchone()
                if r:
                    db_pnl, wins, losses = r[0] or 0.0, r[1] or 0, r[2] or 0
                async with db.execute(
                        f"""SELECT symbol, side, entry_ts, exit_ts, pnl, pnl_pct, win, components
                            FROM {tables[0]} WHERE entry_ts >= ?
                            ORDER BY entry_ts DESC LIMIT 100""", (day_ts,)) as cur:
                    items = await cur.fetchall()
                for r in items:
                    try:
                        trigger = (json.loads(r['components'] or '{}').get('trigger')) or '—'
                    except Exception:
                        trigger = '—'
                    rows.append({
                        'time': time.strftime('%H:%M:%S', time.localtime(r['entry_ts'])),
                        'symbol': r['symbol'], 'direction': r['side'],
                        'trigger': trigger,
                        'result': -1 if r['win'] == -1 else (1 if r['win'] else 0),
                        'pnl': r['pnl'], 'pnl_pct': r['pnl_pct'],
                        'duration_s': (r['exit_ts'] - r['entry_ts']) if r['exit_ts'] else None,
                    })
        except Exception:
            pass
        floating = 0.0
        for sym, t in _own_open().items():
            prices = bot.get_price(sym)
            if prices:
                cur = prices['bid'] if t['side'] == 'BUY' else prices['ask']
                diff = (cur - t['entry_price']) if t['side'] == 'BUY' else (t['entry_price'] - cur)
                floating += diff * (t.get('quantity') or 0.0) + t.get('realized_pnl', 0.0)
        n_closed_today = wins + losses
        return web.json_response({
            'ok': True,
            'db_today_pnl': round(db_pnl, 4),
            'realized_today': round(db_pnl, 4),
            'floating': round(floating, 4),
            'fees_est': round(n_closed_today * 0.34, 2),
            'trades_count': len(rows), 'wins': wins, 'losses': losses,
            'open_now': len(_own_open()), 'trades': rows,
        }, headers={'Cache-Control': 'no-store'})

    # ─── السجل الكامل ───
    async def history(request):
        days, agg = [], {'total_closed': 0, 'total_wins': 0, 'total_losses': 0,
                         'overall_winrate': None, 'profit_factor': None, 'total_pnl': 0.0,
                         'gross_win': 0.0, 'gross_loss': 0.0, 'avg_win': None,
                         'avg_loss': None, 'best_trade': {'pnl': 0, 'symbol': '—', 'date': '—'},
                         'worst_trade': {'pnl': 0, 'symbol': '—', 'date': '—'},
                         'best_day': {'pnl': 0, 'date': '—'},
                         'worst_day': {'pnl': 0, 'date': '—'},
                         'active_days': 0, 'est_fees': 0.0}
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                        f"SELECT date, pnl, wins, losses FROM {tables[1]} ORDER BY date ASC") as cur:
                    items = await cur.fetchall()
                cum = 0.0
                for r in items:
                    p = r['pnl'] or 0.0
                    w, l = r['wins'] or 0, r['losses'] or 0
                    tot = w + l
                    cum += p
                    d = {'date': r['date'], 'pnl': round(p, 4), 'wins': w, 'losses': l,
                         'total': tot,
                         'winrate': round(w / tot * 100, 1) if tot else None,
                         'cum': round(cum, 4)}
                    days.append(d)
                    if tot:
                        if agg['best_day']['date'] == '—' or p > agg['best_day']['pnl']:
                            agg['best_day'] = {'pnl': round(p, 4), 'date': r['date']}
                        if agg['worst_day']['date'] == '—' or p < agg['worst_day']['pnl']:
                            agg['worst_day'] = {'pnl': round(p, 4), 'date': r['date']}
                agg['active_days'] = sum(1 for d in days if d['total'] > 0)
                agg['total_pnl'] = round(cum, 4)
                async with db.execute(
                        f"""SELECT symbol, side, entry_ts, pnl, pnl_pct FROM {tables[0]}
                            WHERE win>=0 ORDER BY pnl ASC""") as cur:
                    trs = await cur.fetchall()
                n = len(trs)
                if n:
                    wins_l = [t for t in trs if (t['pnl'] or 0) > 0]
                    losses_l = [t for t in trs if (t['pnl'] or 0) <= 0]
                    gw = sum(t['pnl'] for t in wins_l)
                    gl = sum(t['pnl'] for t in trs if (t['pnl'] or 0) <= 0)
                    agg.update({
                        'total_closed': n, 'total_wins': len(wins_l),
                        'total_losses': len(losses_l),
                        'overall_winrate': round(len(wins_l) / n * 100, 1),
                        'profit_factor': round(gw / abs(gl), 2) if gl else None,
                        'gross_win': round(gw, 4), 'gross_loss': round(gl, 4),
                        'avg_win': round(gw / len(wins_l), 4) if wins_l else None,
                        'avg_loss': round(gl / len(losses_l), 4) if losses_l else None,
                        'est_fees': round(n * 0.34, 2),
                    })

                    def _d(ts):
                        return time.strftime('%m-%d', time.localtime(ts)) if ts else '—'

                    agg['best_trade'] = {'pnl': round(trs[-1]['pnl'], 4),
                                         'symbol': trs[-1]['symbol'],
                                         'date': _d(trs[-1]['entry_ts'])}
                    agg['worst_trade'] = {'pnl': round(trs[0]['pnl'], 4),
                                          'symbol': trs[0]['symbol'],
                                          'date': _d(trs[0]['entry_ts'])}
        except Exception:
            pass
        days_desc = list(reversed(days))
        return web.json_response({'ok': True, 'days': days_desc, 'agg': agg,
                                  'curve': days},
                                 headers={'Cache-Control': 'no-store'})

    # ─── الصفقات المغلقة بالتفصيل ───
    async def closed(request):
        day = request.query.get('date', '')
        limit = min(int(request.query.get('limit', 300)), 1000)
        out = []
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                db.row_factory = aiosqlite.Row
                sql = f"""SELECT symbol, side, entry_ts, exit_ts, pnl, pnl_pct, reason, components
                          FROM {tables[0]} WHERE win>=0"""
                args = []
                if day:
                    sql += " AND entry_ts >= ? AND entry_ts < ?"
                    args = [time.mktime(time.strptime(day, '%Y-%m-%d')),
                            time.mktime(time.strptime(day, '%Y-%m-%d')) + 86400]
                sql += " ORDER BY entry_ts DESC LIMIT ?"
                args.append(limit)
                async with db.execute(sql, args) as cur:
                    for r in await cur.fetchall():
                        try:
                            trigger = (json.loads(r['components'] or '{}').get('trigger')) or '—'
                        except Exception:
                            trigger = '—'
                        out.append({
                            'open_time': time.strftime('%m-%d %H:%M',
                                                       time.localtime(r['entry_ts'])),
                            'close_time': time.strftime('%m-%d %H:%M',
                                                        time.localtime(r['exit_ts']))
                                          if r['exit_ts'] else None,
                            'symbol': r['symbol'], 'direction': r['side'],
                            'trigger': trigger,
                            'reason': r['reason'],
                            'duration_s': (r['exit_ts'] - r['entry_ts'])
                                          if (r['exit_ts'] and r['entry_ts']) else None,
                            'pnl': round(r['pnl'] or 0, 4),
                            'pnl_pct': r['pnl_pct'],
                        })
        except Exception:
            pass
        return web.json_response(out, headers={'Cache-Control': 'no-store'})

    # ─── التحكم: خاص بهذه الاستراتيجية فقط ───
    async def enable(request):
        strat.cfg['enabled'] = True
        try:
            getattr(bot, m['exit_attr']).cfg.update(strat.cfg)
        except Exception:
            pass
        try:
            setattr(bot, m['cap_attr'], int(strat.cfg.get('max_open_trades', 5)))
        except Exception:
            pass
        await _persist_cfg()
        await notify(m['skey'], f"▶️ تفعيل {m['name']}", f"أُعيدت تفعيل {m['name']} من لوحتها")
        return web.json_response({'ok': True, 'enabled': True},
                                 headers={'Cache-Control': 'no-store'})

    async def disable(request):
        strat.cfg['enabled'] = False
        try:
            getattr(bot, m['exit_attr']).cfg.update(strat.cfg)
        except Exception:
            pass
        await _persist_cfg()
        await notify(m['skey'], f"⏸️ إيقاف {m['name']}",
                     f"أُوقفت {m['name']} من لوحتها — الصفقات المفتوحة تُدار حتى إغلاقها")
        return web.json_response({'ok': True, 'enabled': False},
                                 headers={'Cache-Control': 'no-store'})

    async def close_all(request):
        closed_syms = []
        for sym, t in list(_own_open().items()):
            prices = bot.get_price(sym)
            px = (prices['bid'] if t['side'] == 'BUY' else prices['ask']) \
                if prices else t['entry_price']
            try:
                ok, fill, pnl_over = await bot._close_position(t, px)
                if ok:
                    await bot._finalize_trade(t, fill, f"👋 إغلاق يدوي من لوحة {m['name']}",
                                              pnl_over)
                    closed_syms.append(sym)
            except Exception:
                pass
        await notify(m['skey'], f"👋 إغلاق صفقات {m['name']}",
                     'أُغلق: ' + (', '.join(closed_syms) if closed_syms
                                  else 'لا صفقات مفتوحة'))
        return web.json_response({'ok': True, 'closed': closed_syms},
                                 headers={'Cache-Control': 'no-store'})

    async def wipe(request):
        open_own = _own_open()
        if open_own:
            return web.json_response(
                {'ok': False, 'error': 'توجد صفقات مفتوحة: ' + ', '.join(open_own)
                 + ' — أغلقها أولاً (زر الإغلاق)'}, status=400)
        deleted = []
        async with aiosqlite.connect(bot.db.db_name) as db:
            for tbl in tables:
                try:
                    cur = await db.execute(f'DELETE FROM {tbl}')
                    deleted.append(f'{tbl}({cur.rowcount})')
                except Exception:
                    pass
            await db.commit()
        try:
            events.clear()
        except Exception:
            pass
        try:
            st = getattr(bot, m['stats_attr'])
            if 'trades' in st:
                st.update({'wins': 0, 'losses': 0, 'trades': 0})
            else:
                st.update({'wins': 0, 'losses': 0})
        except Exception:
            pass
        await notify(m['skey'], f"🗑 مسح بيانات {m['name']}", '، '.join(deleted) or 'لا شيء')
        return web.json_response({'ok': True, 'deleted': '، '.join(deleted) or 'لا شيء'},
                                 headers={'Cache-Control': 'no-store'})

    return {'page': page, 'panel': panel, 'trades': trades, 'today': today,
            'history': history, 'closed': closed, 'enable': enable,
            'disable': disable, 'close_all': close_all, 'wipe': wipe}


# ═══════════════════════ الأدوات العامة المشتركة ═══════════════════════
def _shared_handlers(bot):
    def j(data, status=200):
        return web.json_response(data, status=status,
                                 headers={'Cache-Control': 'no-store'})

    async def index(request):
        raise web.HTTPFound('/trend')

    async def notifications(request):
        after = int(request.query.get('after', 0))
        if PANEL_DB:
            return j(await PANEL_DB.get_after(after))
        return j({'items': [], 'last_id': after})

    async def refresh_balance(request):
        try:
            balance = await bot.get_available_usdt()
        except Exception:
            balance = 0.0
        return j({'ok': True, 'balance': round(balance, 2)})

    async def pause(request):
        bot.TRADE_ENABLED = False
        await notify('pause', '⏸️ إيقاف مؤقت', 'أُوقف التداول من اللوحة — المراقبة فقط')
        return j({'ok': True})

    async def resume(request):
        if bot.EMERGENCY_MODE:
            return j({'ok': False, 'error': 'وضع الطوارئ مفعّل — ألغِ الطوارئ أولاً ثم استأنف'}, status=400)
        if not bot.binance_api_key:
            return j({'ok': False, 'error': 'مفاتيح API ناقصة'}, status=400)
        bot.TRADE_ENABLED = True
        await notify('resume', '▶️ استئناف', 'أُعيد تفعيل التداول من اللوحة')
        return j({'ok': True})

    async def _close_all_positions(reason):
        closed = []
        for symbol, t in list(bot.active_trades.items()):
            prices = bot.get_price(symbol)
            px = (prices['bid'] if t['side'] == 'BUY' else prices['ask']) if prices else t['entry_price']
            ok, fill, pnl_over = await bot._close_position(t, px)
            if ok:
                await bot._finalize_trade(t, fill, reason, pnl_over)
                closed.append(symbol)
        return closed

    async def close_all(request):
        closed = await _close_all_positions('👋 إغلاق شامل من اللوحة')
        return j({'ok': True, 'closed': closed})

    async def emergency(request):
        closed = await _close_all_positions('🚨 وضع طوارئ من اللوحة')
        bot.TRADE_ENABLED = False
        bot.EMERGENCY_MODE = True
        msg = 'أُغلق: ' + (', '.join(closed) if closed else 'لا صفقات مفتوحة') + ' — الدخول الجديد مقفول'
        await notify('emergency', '🚨 وضع الطوارئ مفعّل', msg, level='critical')
        try:
            await bot.tg('🚨 *وضع طوارئ من اللوحة*\n' + msg)
        except Exception:
            pass
        return j({'ok': True, 'closed': closed})

    async def emergency_reset(request):
        bot.EMERGENCY_MODE = False
        await notify('emergency', '🔓 أُلغي وضع الطوارئ', 'التداول ما زال موقوفاً — استأنف يدوياً')
        return j({'ok': True})

    async def stop_bot(request):
        ok = await bot.request_shutdown('panel')
        if ok:
            await notify('stop', '🛑 إيقاف البوت', 'طلب إيقاف آمن من اللوحة — سيتوقف خلال ≤60 ثانية')
        return j({'ok': ok, 'error': None if ok else 'البوت يتوقف بالفعل'})

    async def wipe(request):
        if bot.active_trades:
            return j({'ok': False, 'error':
                      'توجد صفقات مفتوحة: ' + ', '.join(bot.active_trades) +
                      ' — أغلقها أولاً (زر الإغلاق الشامل أو الطوارئ)'}, status=400)
        deleted = []
        async with aiosqlite.connect(bot.db.db_name) as db:
            for tbl in ('signal_log', 'daily_stats', 'notifications', 'bot_params',
                        'trend_trades', 'trend_daily', 'mars_trades', 'mars_daily'):
                try:
                    cur = await db.execute(f"DELETE FROM {tbl}")
                    deleted.append(f"{tbl}({cur.rowcount})")
                except Exception:
                    pass
            await db.commit()
        try:
            bot.trend_events.clear(); bot.mars_events.clear()
        except Exception:
            pass
        await notify('wipe', '💣 مسح شامل', '، '.join(deleted))
        return j({'ok': True, 'deleted': '، '.join(deleted) or 'لا شيء'})

    return {'index': index, 'notifications': notifications, 'refresh_balance': refresh_balance,
            'pause': pause, 'resume': resume, 'close_all': close_all,
            'emergency': emergency, 'emergency_reset': emergency_reset,
            'stop_bot': stop_bot, 'wipe': wipe}


# ═══════════════════════ الخادم ═══════════════════════
def create_app(bot):
    app = web.Application()
    shared = _shared_handlers(bot)
    app.router.add_get('/', shared['index'])
    app.router.add_get('/api/notifications', shared['notifications'])
    app.router.add_post('/api/balance', shared['refresh_balance'])
    app.router.add_post('/api/pause', shared['pause'])
    app.router.add_post('/api/resume', shared['resume'])
    app.router.add_post('/api/close-all', shared['close_all'])
    app.router.add_post('/api/emergency', shared['emergency'])
    app.router.add_post('/api/emergency-reset', shared['emergency_reset'])
    app.router.add_post('/api/stop-bot', shared['stop_bot'])
    app.router.add_post('/api/wipe', shared['wipe'])

    for key in ('trend', 'mars'):
        h = _strategy_handlers(bot, STRATEGY_META[key])
        app.router.add_get(f'/{key}', h['page'])
        app.router.add_get(f'/api/{key}/panel', h['panel'])
        app.router.add_get(f'/api/{key}/trades', h['trades'])
        app.router.add_get(f'/api/{key}/today', h['today'])
        app.router.add_get(f'/api/{key}/history', h['history'])
        app.router.add_get(f'/api/{key}/closed', h['closed'])
        app.router.add_post(f'/api/{key}/enable', h['enable'])
        app.router.add_post(f'/api/{key}/disable', h['disable'])
        app.router.add_post(f'/api/{key}/close-all', h['close_all'])
        app.router.add_post(f'/api/{key}/wipe', h['wipe'])
    return app


async def start_web_panel(bot):
    global PANEL_DB
    try:
        PANEL_DB = PanelDB(bot.db.db_name)
        await PANEL_DB.init()
        app = create_app(bot)
        runner = web.AppRunner(app)
        await runner.setup()
        port = int(os.environ.get('PORT', '8080'))
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        print(f'🖥️ اللوحتان تعملان على المنفذ {port} — 🚀 /trend و 📐 /mars')
        return True
    except Exception as e:
        print(f'⚠️ فشل اللوحة (البوت يكمل عمله): {e}')
        return False
