"""
═══════════════════════════════════════════════════════════════════════
  🖥️ لوحة القناص V10 — Legendary Sniper Control Panel
═══════════════════════════════════════════════════════════════════════
  إعادة بناء شاملة — تبويبات كاملة متزامنة لحظة بلحظة:

  🔴 الرئيسية    : نبض البوت، الساعة الحية، الرصيد، حالة المطوّر، الأخطاء
  💰 ربح اليوم   : صافي الربح بعد الرسوم من المنصة مباشرة + تفصيل الرسوم
  📊 المفتوحة    : كل تفاصيل الصفقات المفتوحة (دخول/أهداف/وقف/عائم/عمر)
  🗂 السجل       : كل الصفقات المغلقة + ملخص الأيام + إحصاءات 30 يوماً
  🎛 التحكم      : إيقاف البوت، وضع الطوارئ، إغلاق شامل، مسح البيانات

  ✅ مزامنة كل 2.5 ثانية + ساعة حية بمزامنة خادم
  ✅ كل التاريخ من قاعدة البيانات (sniper_v8.db) — ينجو من إعادة النشر
  ✅ واجهة عربية RTL كاملة — تعمل داخل عملية البوت (نفس الواجهة القديمة)
"""
import os, time, json
import aiosqlite
from aiohttp import web

PANEL_START = time.time()
PANEL_VERSION = "V10.0"

# ═══════════════════════ الواجهة (HTML) ═══════════════════════
PAGE = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>القناص الأسطوري — لوحة التحكم V10</title>
<style>
:root{
  --bg:#0a0e16; --card:#111726; --card2:#0d1320; --line:#1e293b;
  --tx:#e2e8f0; --mut:#7c8aa5; --gold:#f5b942; --green:#10b981;
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
.b-off{color:var(--mut)}
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
<div class="hdr">
  <div class="logo">🥷 القناص الأسطوري <small id="ver">لوحة V10</small></div>
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
    <div class="card"><div class="kpi"><span class="v" id="dToday">—</span><span class="l">📅 صافي ربح اليوم بعد الرسوم</span></div></div>
    <div class="card"><div class="kpi"><span class="v" id="dOpen">—</span><span class="l">📊 صفقات مفتوحة الآن / السعة</span></div></div>
    <div class="card"><div class="kpi"><span class="v" id="dTotal">—</span><span class="l">🏆 صافي الربح الإجمالي (كل التاريخ)</span></div></div>
  </div>
  <div class="grid g3" style="margin-top:12px">
    <div class="card">
      <h3>💓 <b>نبض البوت</b> — مزامنة لحظية</h3>
      <div id="dHeart"></div>
    </div>
    <div class="card">
      <h3>🧠 <b>المطوّر التكيفي</b> — حالة التعلم</h3>
      <div id="dTuner"></div>
      <div id="dTunerHist" style="display:flex;gap:3px;margin-top:8px;flex-wrap:wrap"></div>
    </div>
    <div class="card">
      <h3>⚙️ <b>الإعدادات الحالية</b> (V8.2)</h3>
      <div id="dSettings"></div>
    </div>
  </div>
  <div class="grid g2" style="margin-top:12px">
    <div class="card">
      <h3>🔔 <b>آخر الأحداث</b> — مباشر</h3>
      <div class="feed" id="dFeed"><div class="empty">لا إشعارات بعد</div></div>
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
      <h3>💎 <b>الصافي بعد الرسوم</b> — من المنصة مباشرة</h3>
      <div class="big" id="tNet">—</div>
      <div class="note" id="tNetSub"></div>
    </div>
    <div class="card"><h3>💵 <b>الأرباح المحققة</b> (إغلاقات)</h3><div class="med" id="tReal">—</div><div class="note" id="tRealSub"></div></div>
    <div class="card"><h3>🧾 <b>العمولات</b> (رسوم التنفيذ)</h3><div class="med" id="tComm">—</div><div class="note">من سجل المنصة الرسمي</div></div>
    <div class="card"><h3>🏦 <b>تمويل التمويلات</b> (Funding)</h3><div class="med" id="tFund">—</div><div class="note">يُخصم/يُضاف كل 8 ساعات</div></div>
  </div>
  <div class="grid g3" style="margin-top:12px">
    <div class="card"><h3>📌 <b>ملخص اليوم</b></h3><div id="tSummary"></div></div>
    <div class="card" style="grid-column:span 2"><h3>🧾 <b>صفقات اليوم</b> — بالتفصيل (من قاعدة البيانات)</h3>
      <div class="tblbox" style="max-height:380px"><table id="tTrades"></table></div>
    </div>
  </div>
  <div class="note">💡 الصافي يُحسب من سجل دخل المنصة الرسمي: الأرباح المحققة + التمويل − العمولات. إن تعذر الاتصال بالمنصة يُعرض رابط القاعدة المحلية (بعد إغلاق الصفقات).</div>
</div>

<!-- ═════════ 📊 المفتوحة ═════════ -->
<div class="sec" id="s-open">
  <div class="card">
    <h3>📊 <b>الصفقات المفتوحة الآن</b> — تحديث كل 2.5 ثانية <span id="oCount"></span></h3>
    <div class="tblbox"><table id="oTbl"></table></div>
    <div class="note">🎯 التقدم = المسافة المقطوعة نحو TP1 | التريلينق يُفعّل تلقائياً بعد جني 70% عند TP1 مع نقل الوقف لنقطة التعادل.</div>
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
    <div class="card"><h3>📅 <b>ملخص كل الأيام</b> — من القاعدة الدائمة</h3>
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
  <div id="cEmergBox"></div>
  <div class="grid g2">
    <div class="card">
      <h3>⏯ <b>التداول</b></h3>
      <div id="cTrade"></div>
      <div class="btnrow" style="margin-top:12px">
        <button class="btn b-orange" id="cPauseBtn">⏸️ إيقاف مؤقت</button>
        <button class="btn b-green" id="cResumeBtn">▶️ استئناف</button>
        <button class="btn b-blue" onclick="refreshBal()">🔄 تحديث الرصيد من المنصة</button>
      </div>
    </div>
    <div class="card">
      <h3>🚨 <b>وضع الطوارئ</b> — إجراء جذر</h3>
      <div class="note">يُغلق كل الصفقات المفتوحة فوراً بسعر السوق + يوقف الدخول الجديد نهائياً حتى تُلغيه بنفسك يدوياً.</div>
      <div class="btnrow" style="margin-top:12px">
        <button class="btn b-red" onclick="doEmergency()">🚨 تفعيل وضع الطوارئ (إغلاق الكل + قفل)</button>
        <button class="btn b-gray" id="cEmergReset" onclick="doEmergencyReset()">🔓 إلغاء وضع الطوارئ</button>
      </div>
    </div>
    <div class="card">
      <h3>🛑 <b>إيقاف البوت</b> — إيقاف آمن كامل</h3>
      <div class="note">يوقف البوت بأمان (يُغلق الاتصالات ويحفظ الحالة). المراكز المفتوحة تبقى محمية بستوب المنصة. اللوحة ستنقطع لأنها تعمل داخل البوت.</div>
      <div class="btnrow" style="margin-top:12px">
        <button class="btn b-red" onclick="doStop()">🛑 إيقاف البوت الآن</button>
      </div>
    </div>
    <div class="card">
      <h3>🗑 <b>حذف شامل للبيانات</b> — لا رجعة فيه</h3>
      <div class="note">يمسح سجل الصفقات والإشعارات والإحصاءات اليومية من قاعدة البيانات <b>sniper_v8.db</b>.
      الصفقات المفتوحة لا تُمسح (أغلقها أولاً أو استخدم الطوارئ). النتائج تُصفر للأبد.</div>
      <div class="btnrow" style="margin-top:12px">
        <button class="btn b-orange" onclick="doWipe(false)">🗑 مسح السجل والتاريخ</button>
        <button class="btn b-red" onclick="doWipe(true)">💣 مسح شامل (يشمل حالة المطوّر التعليمية)</button>
      </div>
    </div>
  </div>
  <div class="card" style="margin-top:12px">
    <h3>💾 <b>حالة قاعدة البيانات</b> — التاريخ ينجو من إعادة النشر</h3>
    <div id="cDb"></div>
  </div>
</div>
</div>
<script>
'use strict';
let SRV_OFF = 0, LAST_SYNC = 0, NOTIF_ID = 0, HIST_TIMER = null, CUR_TAB = 's-dash';
let LAST_OV = null, LAST_TODAY = null;

const $ = id => document.getElementById(id);
const esc = s => String(s??'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const mo = (x, d=2) => (x>=0?'+':'') + Number(x).toFixed(d);
const mono = x => '<span class="mono">' + x + '</span>';
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
  if(CUR_TAB==='s-today' && LAST_TODAY) renderToday(LAST_TODAY);
});

/* ─── الحلقة السريعة: كل 2.5 ثانية ─── */
async function loadAll(){
  const [ov, tr, td] = await Promise.all([api('/api/overview'), api('/api/trades'), api('/api/today')]);
  LAST_OV = ov; LAST_TODAY = td;
  SRV_OFF = (ov.server_ts * 1000) - Date.now(); tickClock();
  LAST_SYNC = Date.now();
  $('syncBadge').innerHTML = '<span class="dot g"></span>متزامن لحظياً';
  $('syncBadge').className = 'badge b-ok';
  renderTop(ov); renderDash(ov, td); renderOpen(tr); renderToday(td); renderControl(ov);
  loadNotifs();
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
  $('ver').textContent = 'لوحة ' + (ov.panel_version||'V10') + ' • بوت V8.2';
  const mb = $('modeBadge');
  if(ov.emergency){ mb.textContent='🚨 وضع الطوارئ'; mb.className='badge b-emg'; }
  else if(ov.trade_enabled){ mb.textContent='🟢 التداول مفعّل'; mb.className='badge b-ok'; }
  else { mb.textContent='⏸️ التداول موقوف'; mb.className='badge b-warn'; }
  $('emgBadge').style.display = ov.emergency ? '' : 'none';
  const hb = $('hbBadge');
  if(ov.scan_age_s < 120){ hb.innerHTML = '<span class="dot g"></span>نبض حي — آخر مسح ' + ago(ov.last_scan_ts); hb.className='badge b-ok'; }
  else { hb.innerHTML = '<span class="dot r"></span>لا مسح منذ ' + ago(ov.last_scan_ts); hb.className='badge b-bad'; }
}

/* ─── الرئيسية ─── */
function renderDash(ov, td){
  $('dBal').textContent = (ov.balance||0).toFixed(2) + ' $';
  const net = td && td.income && td.income.ok ? td.income.net : (td ? td.db_today_pnl : 0);
  const e1 = $('dToday'); e1.textContent = mo(net) + ' $'; e1.className = 'v ' + cl(net);
  $('dOpen').textContent = ov.open_trades + ' / ' + ov.max_open;
  const e2 = $('dTotal'); e2.textContent = mo(ov.all_time_net||0) + ' $'; e2.className = 'v ' + cl(ov.all_time_net||0);

  $('dHeart').innerHTML =
    kv('آخر مسح للسوق', ago(ov.last_scan_ts) + mono(' (#'+ov.scans+')')) +
    kv('عمر آخر سعر حي', ov.price_age > 3600 ? '<b class="neg">قديم جداً</b>' : mono(ov.price_age+' ث')) +
    kv('معدل المسح', mono('كل ' + ov.loop_sec + ' ثانية')) +
    kv('مدة التشغيل', mono(dur(ov.uptime_s))) +
    kv('أزواج مرصودة', mono(ov.pairs)) +
    kv('صفقات اليوم (عدد)', mono(ov.trades_today)) +
    kv('الوضع', ov.testnet ? '🧪 Testnet تجريبي' : '🔴 حقيقي — أموال فعلية');

  const tu = ov.tuner||{};
  $('dTuner').innerHTML =
    kv('الحد الأدنى للنقاط', mono(tu.min_score+' / 8')) +
    kv('قرب أمر البلوك', mono('≤ ' + tu.proximity_pct + '%')) +
    kv('ستوكاستيك صارم', tu.strict_stoch ? 'نعم 🔒' : 'لا 🔓') +
    kv('فوز آخر 10 صفقات', mono(tu.winrate||'غير كافٍ بعد'));
  $('dTunerHist').innerHTML = (ov.tuner_results||[]).slice(-20).map(w =>
    '<span class="tag '+(w?'win':'loss')+'" style="width:24px;text-align:center">'+(w?'✓':'✗')+'</span>').join('')
    || '<span class="mut">لا نتائج بعد</span>';

  $('dSettings').innerHTML =
    kv('الرافعة', mono(ov.leverage+'x')) + kv('هامش الصفقة', mono('$'+ov.trade_size)) +
    kv('حجم المركز', mono('$'+(ov.trade_size*ov.leverage))) +
    kv('صفقات متزامنة', mono(ov.max_open)) + kv('النسخة', mono(ov.bot_version||'V8.2'));

  const ek = Object.keys(ov.errors||{});
  $('dErrors').innerHTML = !ek.length
    ? '<div class="empty">✅ لا أخطاء — كل شيء نظيف</div>'
    : ek.map(k => '<div class="kv err-item"><span>'+esc(k)+'</span><b>×'+ov.errors[k]+'</b></div>').join('');
}
const kv = (a,b) => '<div class="kv"><span>'+a+'</span><b>'+b+'</b></div>';

/* ─── الصفقات المفتوحة (تفاصيل كاملة) ─── */
function renderOpen(tr){
  const box = $('oTbl');
  $('oCount').textContent = tr.length ? '('+tr.length+')' : '';
  if(!tr.length){ box.innerHTML = '<tr><td><div class="empty">لا صفقات مفتوحة — القناص يراقب السوق 🔭</div></td></tr>'; return; }
  let h = '<tr><th>الزوج</th><th>الاتجاه</th><th>الدخول</th><th>السعر الحالي</th><th>الكمية</th><th>العائم</th><th>% الهامش</th>'+
          '<th>جُني جزئي</th><th>الوقف SL</th><th>المسافة للوقف</th><th>هدف 1</th><th>التقدم لهدف1</th><th>هدف 2</th>'+
          '<th>التقدم لهدف2</th><th>التريلينق</th><th>أعلى/أدنى</th><th>عمر الصفقة</th><th>النقاط</th><th>النوع</th></tr>';
  tr.forEach(t => {
    const pnlCls = cl(t.pnl||0);
    const prog = p => '<div class="bar"><i style="width:'+Math.max(0,Math.min(100,p))+'%;background:'+
      (p>=100?'var(--green)':(p>50?'var(--gold)':'var(--blue)'))+'"></i></div>' +
      '<span class="mut mono" style="font-size:10px">'+p.toFixed(0)+'%</span>';
    h += '<tr><td><b>'+esc(t.symbol)+'</b></td>'
      + '<td><span class="tag '+(t.side==='BUY'?'buy':'sell')+'">'+(t.side==='BUY'?'▲ شراء':'▼ بيع')+'</span></td>'
      + '<td>'+mono(t.entry)+'</td><td>'+mono(t.current??'—')+'</td>'
      + '<td>'+mono(t.qty)+'</td>'
      + '<td class="'+pnlCls+'"><b>'+mono(t.pnl===null?'—':mo(t.pnl)+' $')+'</b></td>'
      + '<td class="'+pnlCls+'">'+(t.pnl_pct===null?'—':mono(mo(t.pnl_pct,1)+'%'))+'</td>'
      + '<td class="'+cl(t.realized)+'">'+mono(t.realized?mo(t.realized)+' $':'—')+'</td>'
      + '<td class="neg">'+mono(t.sl)+'</td>'
      + '<td class="'+(t.sl_dist_pct>0?'neg':'pos')+'">'+mono(mo(t.sl_dist_pct,2)+'%')+'</td>'
      + '<td class="pos">'+mono(t.tp1)+'</td><td>'+prog(t.tp1_prog)+'</td>'
      + '<td class="blue">'+mono(t.tp2)+'</td><td>'+prog(t.tp2_prog)+'</td>'
      + '<td>'+(t.trailing?'<span class="tag win">🏃 مفعل</span>':'<span class="tag open">انتظار</span>')+'</td>'
      + '<td class="mut mono" style="font-size:11px">'+t.hi+' / '+t.lo+'</td>'
      + '<td>'+mono(dur(t.age_s))+'</td>'
      + '<td><span class="tag info">'+(t.score??'—')+'/8</span></td>'
      + '<td class="mut">'+esc(t.kind||'—')+'</td></tr>';
  });
  box.innerHTML = h;
}

/* ─── ربح اليوم ─── */
function renderToday(td){
  const inc = td.income||{ok:false};
  const set = (id, v, cls) => { const e=$(id); e.textContent = v; if(cls!==undefined) e.className = e.className.split(' ')[0]+' '+cls; };
  if(inc.ok){
    set('tNet', mo(inc.net)+' $', cl(inc.net));
    $('tNetSub').textContent = 'من '+inc.n_income+' حركة دخل على المنصة — محدّث الآن';
    set('tReal', mo(inc.realized)+' $', cl(inc.realized));
    set('tComm', mo(inc.commission)+' $', 'neg');
    set('tFund', mo(inc.funding)+' $', cl(inc.funding));
  } else {
    set('tNet', mo(td.db_today_pnl)+' $', cl(td.db_today_pnl));
    $('tNetSub').textContent = '⚠️ من القاعدة المحلية (تعذر السؤال للمنصة: '+esc(inc.error||'—')+')';
    set('tReal','—','mut'); set('tComm','—','mut'); set('tFund','—','mut');
  }
  $('tSummary').innerHTML =
    kv('صفقات دخلت اليوم', mono(td.trades_count)) +
    kv('رابحة / خاسرة', '<span class="pos">'+td.wins+'</span> / <span class="neg">'+td.losses+'</span>') +
    kv('مفتوحة الآن', mono(td.open_now)) +
    kv('PnL القاعدة (بعد الإغلاقات)', mono(mo(td.db_today_pnl)+' $')) +
    kv('حد الحماية اليومي', mono('3 صفقات قبل تجمّد ارتخاء المطوّر'));

  let h = '<tr><th>الوقت</th><th>الزوج</th><th>الاتجاه</th><th>النقاط</th><th>التفعيل</th><th>الحالة</th><th>النتيجة</th><th>% من الهامش</th><th>المدة</th></tr>';
  (td.trades||[]).forEach(t => {
    const open = t.result === -1 || t.result === null;
    h += '<tr><td class="mono">'+t.time+'</td><td><b>'+esc(t.symbol)+'</b></td>'
      + '<td><span class="tag '+(t.direction==='BUY'?'buy':'sell')+'">'+(t.direction==='BUY'?'شراء':'بيع')+'</span></td>'
      + '<td>'+(t.score??'—')+'</td><td class="mut">'+esc(t.trigger||'—')+'</td>'
      + '<td>'+(open?'<span class="tag open">⏳ جارية</span>':(t.result?'<span class="tag win">ربح</span>':'<span class="tag loss">خسارة</span>'))+'</td>'
      + '<td class="'+cl(t.pnl||0)+'"><b>'+(t.pnl===null?'—':mono(mo(t.pnl)+' $'))+'</b></td>'
      + '<td>'+(t.pnl_pct!=null?mono(mo(t.pnl_pct,1)+'%'):'—')+'</td>'
      + '<td class="mut">'+(t.duration_s!=null?mono(dur(t.duration_s)):'—')+'</td></tr>';
  });
  $('tTrades').innerHTML = h || '<tr><td><div class="empty">لا صفقات اليوم بعد — الانتظار جزء من الاستراتيجية</div></td></tr>';
}

/* ─── السجل والأيام ─── */
async function loadHistory(){
  const h = await api('/api/history');
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
  const rows = await api('/api/closed' + (day ? '?date='+day : ''));
  let h = '<tr><th>فتحت</th><th>أُغلقت</th><th>الزوج</th><th>الاتجاه</th><th>النقاط</th><th>التفعيل</th><th>سبب الإغلاق</th><th>المدة</th><th>النتيجة</th><th>% من الهامش</th></tr>';
  rows.forEach(t => {
    h += '<tr><td class="mono">'+t.open_time+'</td><td class="mono">'+(t.close_time||'—')+'</td>'
      + '<td><b>'+esc(t.symbol)+'</b></td>'
      + '<td><span class="tag '+(t.direction==='BUY'?'buy':'sell')+'">'+(t.direction==='BUY'?'شراء':'بيع')+'</span></td>'
      + '<td>'+(t.score??'—')+'</td><td class="mut">'+esc(t.trigger||'—')+'</td>'
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
    + '<polygon points="'+X(0)+','+(H-P)+' '+pts+' '+X(curve.length-1)+','+(H-P)+'" fill="rgba(245,185,66,.10)"/>'
    + '<polyline points="'+pts+'" fill="none" stroke="#f5b942" stroke-width="2"/>'
    + '<circle cx="'+X(curve.length-1)+'" cy="'+Y(vals[vals.length-1])+'" r="3.5" fill="#f5b942"/>';
  $('hChartNote').textContent = 'من '+curve[0].date+' إلى '+curve[curve.length-1].date+' — تراكمي '+mo(vals[vals.length-1])+' $';
}

/* ─── الإشعارات المباشرة ─── */
async function loadNotifs(){
  const n = await api('/api/notifications?after='+NOTIF_ID);
  if(n.items.length){
    const box = $('dFeed');
    if(box.querySelector('.empty')) box.innerHTML = '';
    n.items.reverse().forEach(it => {
      NOTIF_ID = Math.max(NOTIF_ID, it.id);
      const d = document.createElement('div'); d.className = 'it';
      d.innerHTML = '<div class="h">'+esc(it.title)+'</div>'+(it.body?'<div class="mut" style="font-size:11px">'+esc(it.body)+'</div>':'')+'<div class="t">🕐 '+it.time+'</div>';
      box.prepend(d);
    });
    while(box.children.length > 60) box.lastChild.remove();
  }
}
setInterval(() => loadNotifs().catch(()=>{}), 4000);

/* ─── أزرار التحكم ─── */
function renderControl(ov){
  $('cTrade').innerHTML =
    kv('حالة التداول', ov.trade_enabled ? '<span class="pos">🟢 مفعّل — يدخل صفقات</span>' : '<span class="neg">⏸️ موقوف — مراقبة فقط</span>') +
    kv('وضع الطوارئ', ov.emergency ? '<span class="neg">🚨 مفعّل — كل الدخول مقفول</span>' : 'غير مفعل') +
    kv('المفاتيح', ov.has_keys ? 'موجودة ✅' : 'غير مضبوطة ❌');
  $('cPauseBtn').onclick = doPause; $('cResumeBtn').onclick = doResume;
  $('cEmergReset').disabled = !ov.emergency;
  $('cEmergBox').innerHTML = ov.emergency
    ? '<div class="warnbox">🚨 <b>وضع الطوارئ مفعّل الآن!</b> — كل الدخول الجديد مقفول. الصفقات المفتوحة: '+ov.open_trades+'. لإلغائه استخدم زر "إلغاء وضع الطوارئ" ثم استأنف التداول يدوياً.</div>' : '';
  $('cDb').innerHTML =
    kv('ملف القاعدة', mono(esc(ov.db_name||'sniper_v8.db'))) +
    kv('صفقات مسجلة (signal_log)', mono(ov.db_rows.signals)) +
    kv('أيام مسجلة (daily_stats)', mono(ov.db_rows.days)) +
    kv('إشعارات محفوظة', mono(ov.db_rows.notifs)) +
    kv('صفقات مفتوحة محفوظة', mono(ov.db_rows.active)) +
    kv('الحماية', '💾 كل التاريخ أعلاه محفوظ دائمًا — يعود كاملاً بعد إعادة النشر أو إعادة التشغيل');
}
async function refreshBal(){
  try{ const r = await api('/api/balance', {method:'POST'});
    alert('الرصيد المتاح من المنصة: '+r.balance.toFixed(2)+' USDT'); loadAll(); }catch(e){ alert('فشل: '+e.message); }
}
async function act(path, body){
  try{ return await api(path, {method:'POST', headers:{'Content-Type':'application/json'},
       body: JSON.stringify(body||{})}); }catch(e){ alert('فشل: '+e.message); return null; }
}
async function doPause(){ if(await act('/api/pause')) loadAll(); }
async function doResume(){ if(await act('/api/resume')) loadAll(); }
async function doEmergency(){
  if(!confirm('🚨 سيتَّم إغلاق كل الصفقات المفتوحة فوراً بسعر السوق وقفل أي دخول جديد.\nهل أنت متأكد؟')) return;
  if(!confirm('تأكيد أخير: اضغط موافق للتنفيذ الفوري.')) return;
  const r = await act('/api/emergency');
  if(r){ alert('تم! أُغلق: ' + (r.closed.length ? r.closed.join(', ') : 'لا صفقات مفتوحة')); loadAll(); }
}
async function doEmergencyReset(){ if(await act('/api/emergency-reset')){ alert('أُلغي وضع الطوارئ — التداول ما زال موقوفاً، استأنفه يدوياً.'); loadAll(); } }
async function doStop(){
  if(!confirm('🛑 سيُوقف البوت بأمان كلياً (المراكز تبقى محمية بستوب المنصة).\nاللوحة ستنقطع لأنها تعمل داخل البوت.\nمتأكد؟')) return;
  if(!confirm('تأكيد أخير: اضغط موافق للإيقاف.')) return;
  const r = await act('/api/stop-bot');
  if(r){ document.body.innerHTML = '<div style="display:flex;height:100vh;align-items:center;justify-content:center;flex-direction:column;gap:10px"><div style="font-size:40px">🛑</div><div style="font-size:20px;font-weight:700">جارٍ إيقاف البوت بأمان...</div><div class="mut">ستنقطع اللوحة خلال ثوانٍ. شغّل البوت من جديد ليعود كل شيء (البيانات محفوظة).</div></div>'; }
}
async function doWipe(full){
  const w = prompt(full
    ? '💣 مسح شامل: سيُمسح كل التاريخ + حالة المطوّر التعليمية + الإشعارات.\nاكتب كلمة: حذف للتأكيد'
    : '🗑 سيُمسح سجل الصفقات والأيام والإشعارات (لا يمسح حالة المطوّر).\nاكتب كلمة: حذف للتأكيد');
  if(w !== 'حذف'){ if(w!==null) alert('لم تُكتب كلمة التأكيد — أُلغي المسح'); return; }
  const r = await act('/api/wipe', {full: !!full});
  if(r){ alert('تم المسح: ' + r.deleted); loadAll(); if(CUR_TAB==='s-hist') loadHistory(); }
}

tickClock();
loadAll().catch(syncFail);
</script>
</body>
</html>"""


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


def _day_start_ts():
    return time.mktime(time.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d'))


def _comp_trigger(components_json):
    try:
        comp = json.loads(components_json or '{}')
        return comp.get('trigger') or '—'
    except Exception:
        return '—'


# ═══════════════════════ الخادم ═══════════════════════
def create_app(bot):
    def j(data, status=200):
        return web.json_response(data, status=status,
                                 headers={'Cache-Control': 'no-store'})

    async def index(request):
        return web.Response(text=PAGE, content_type='text/html',
                            headers={'Cache-Control': 'no-store, must-revalidate'})

    # ─── نظرة عامة ───
    async def overview(request):
        tuner = bot.tuner
        wr = tuner.recent_winrate(10)
        newest = max((p.get('ts', 0) for p in bot.live_prices.values()), default=0)
        scan = bot.last_scan_info or {}
        db_rows = {'signals': 0, 'days': 0, 'notifs': 0, 'active': 0}
        all_net, all_closed, all_wins, gross_w, gross_l = 0.0, 0, 0, 0.0, 0.0
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                for key, tbl in (('signals', 'signal_log'), ('days', 'daily_stats'),
                                 ('notifs', 'notifications'), ('active', 'active_trades')):
                    try:
                        async with db.execute(f"SELECT COUNT(*) c FROM {tbl}") as cur:
                            db_rows[key] = (await cur.fetchone())[0]
                    except Exception:
                        pass
                async with db.execute(
                        """SELECT COUNT(*) c, COALESCE(SUM(pnl),0) p,
                                  SUM(result=1) w, SUM(result=0) l,
                                  COALESCE(SUM(CASE WHEN result=1 THEN pnl END),0) gw,
                                  COALESCE(SUM(CASE WHEN result=0 THEN pnl END),0) gl
                           FROM signal_log WHERE result >= 0""") as cur:
                    r = await cur.fetchone()
                    all_closed, all_net = r[0] or 0, r[1] or 0.0
                    all_wins, gross_w, gross_l = r[2] or 0, r[4] or 0.0, r[5] or 0.0
        except Exception:
            pass
        return j({
            'ok': True, 'server_ts': time.time(),
            'panel_version': PANEL_VERSION, 'bot_version': 'V8.2',
            'trade_enabled': bot.TRADE_ENABLED, 'emergency': bot.EMERGENCY_MODE,
            'testnet': bot.TESTNET, 'has_keys': bool(bot.binance_api_key),
            'leverage': bot.LEVERAGE, 'trade_size': bot.TRADE_SIZE_USDT,
            'max_open': bot.MAX_OPEN_TRADES, 'pairs': len(bot.all_futures_pairs),
            'balance': round(bot._balance_cache[0], 2) if bot._balance_cache[1] > 0 else 0.0,
            'open_trades': len(bot.active_trades),
            'trades_today': bot._trades_today(),
            'scans': bot.stats.get('total_scans', 0),
            'last_scan_ts': scan.get('ts', 0),
            'scan_age_s': int(time.time() - scan['ts']) if scan.get('ts') else 999999,
            'loop_sec': 60,
            'uptime_s': int(time.time() - PANEL_START),
            'price_age': int(time.time() - newest) if newest else 999999,
            'tuner': {'min_score': tuner.min_score,
                      'proximity_pct': round(tuner.proximity_pct * 100, 1),
                      'strict_stoch': tuner.strict_stoch,
                      'winrate': (str(int(wr * 100)) + '%') if wr is not None else None},
            'tuner_results': list(tuner.results)[-25:],
            'errors': dict(bot.error_counts),
            'all_time_net': round(all_net, 4),
            'db_name': bot.db.db_name, 'db_rows': db_rows,
        })

    # ─── الصفقات المفتوحة: كل التفاصيل ───
    async def trades(request):
        # نوع الدخول (sweep/retest) من سجل الإشارات
        trig_by_sym = {}
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                        """SELECT symbol, components FROM signal_log
                           WHERE result = -1 ORDER BY id DESC LIMIT 40""") as cur:
                    async for r in cur:
                        trig_by_sym.setdefault(r['symbol'], _comp_trigger(r['components']))
        except Exception:
            pass
        out = []
        margin = bot.TRADE_SIZE_USDT or 25.0
        for symbol, t in list(bot.active_trades.items()):
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
            out.append({
                'symbol': symbol, 'side': t['side'],
                'entry': round(entry, 8),
                'current': round(cur, 8) if cur else None,
                'qty': t['quantity'],
                'notional': round(t['quantity'] * entry, 2),
                'pnl': round(pnl, 4) if pnl is not None else None,
                'pnl_pct': round(pnl / margin * 100, 2) if pnl is not None else None,
                'realized': round(t.get('realized_pnl', 0.0), 4),
                'sl': round(t['sl'], 8),
                'sl_dist_pct': round(sl_dist, 2),
                'tp1': round(t['tp'], 8) if t.get('tp') else None,
                'tp1_prog': round(prog_to(t.get('tp')), 1),
                'tp2': round(t['tp2'], 8) if t.get('tp2') else None,
                'tp2_prog': round(prog_to(t.get('tp2')), 1),
                'trailing': bool(t.get('trailing_active')),
                'hi': t.get('highest_price'), 'lo': t.get('lowest_price'),
                'age_s': int(time.time() - t.get('entry_time', time.time())),
                'score': t.get('score'),
                'kind': trig_by_sym.get(symbol, '—'),
            })
        out.sort(key=lambda x: x['age_s'])
        return j(out)

    # ─── ربح اليوم بعد الرسوم ───
    async def today(request):
        day_ts = _day_start_ts()
        inc = await bot.get_income_summary(int(day_ts * 1000))
        db_pnl, wins, losses = 0.0, 0, 0
        rows = []
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                        "SELECT realized_pnl, wins, losses FROM daily_stats WHERE date=?",
                        (time.strftime('%Y-%m-%d'),)) as cur:
                    r = await cur.fetchone()
                if r:
                    db_pnl, wins, losses = r[0] or 0.0, r[1] or 0, r[2] or 0
                async with db.execute(
                        """SELECT symbol, direction, entry_ts, score, components,
                                  result, pnl, close_ts, close_reason, duration_s, pnl_pct
                           FROM signal_log WHERE entry_ts >= ?
                           ORDER BY entry_ts DESC LIMIT 100""", (day_ts,)) as cur:
                    items = await cur.fetchall()
                margin = bot.TRADE_SIZE_USDT or 25.0
                for r in items:
                    pp = r['pnl_pct']
                    if pp is None and r['pnl'] is not None:
                        pp = round(r['pnl'] / margin * 100, 2)
                    rows.append({
                        'time': time.strftime('%H:%M:%S', time.localtime(r['entry_ts'])),
                        'symbol': r['symbol'], 'direction': r['direction'],
                        'score': int(r['score'] or 0),
                        'trigger': _comp_trigger(r['components']),
                        'result': r['result'], 'pnl': r['pnl'], 'pnl_pct': pp,
                        'duration_s': r['duration_s'],
                    })
        except Exception:
            pass
        return j({'ok': True, 'income': inc, 'db_today_pnl': round(db_pnl, 4),
                  'trades_count': len(rows), 'wins': wins, 'losses': losses,
                  'open_now': len(bot.active_trades), 'trades': rows})

    # ─── السجل الكامل: أيام + إحصاءات + منحنى ───
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
                        "SELECT date, realized_pnl, wins, losses FROM daily_stats "
                        "ORDER BY date ASC") as cur:
                    items = await cur.fetchall()
                cum = 0.0
                for r in items:
                    p = r['realized_pnl'] or 0.0
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
                        """SELECT symbol, direction, entry_ts, pnl, pnl_pct FROM signal_log
                           WHERE result >= 0 ORDER BY pnl ASC""") as cur:
                    trs = await cur.fetchall()
                n = len(trs)
                if n:
                    wins = [t for t in trs if (t['pnl'] or 0) > 0]
                    losses = [t for t in trs if (t['pnl'] or 0) <= 0]
                    gw = sum(t['pnl'] for t in wins)
                    gl = sum(t['pnl'] for t in trs if (t['pnl'] or 0) <= 0)
                    agg.update({
                        'total_closed': n, 'total_wins': len(wins), 'total_losses': len(losses),
                        'overall_winrate': round(len(wins) / n * 100, 1),
                        'profit_factor': round(gw / abs(gl), 2) if gl else None,
                        'gross_win': round(gw, 4), 'gross_loss': round(gl, 4),
                        'avg_win': round(gw / len(wins), 4) if wins else None,
                        'avg_loss': round(gl / len(losses), 4) if losses else None,
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
        return j({'ok': True, 'days': days_desc, 'agg': agg, 'curve': days})

    # ─── الصفقات المغلقة بالتفصيل ───
    async def closed(request):
        day = request.query.get('date', '')
        limit = min(int(request.query.get('limit', 300)), 1000)
        out = []
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                db.row_factory = aiosqlite.Row
                sql = """SELECT symbol, direction, entry_ts, score, components, pnl,
                                close_ts, close_reason, duration_s, pnl_pct
                         FROM signal_log WHERE result >= 0"""
                args = []
                if day:
                    sql += " AND entry_ts >= ? AND entry_ts < ?"
                    args = [time.mktime(time.strptime(day, '%Y-%m-%d')),
                            time.mktime(time.strptime(day, '%Y-%m-%d')) + 86400]
                sql += " ORDER BY entry_ts DESC LIMIT ?"
                args.append(limit)
                async with db.execute(sql, args) as cur:
                    for r in await cur.fetchall():
                        out.append({
                            'open_time': time.strftime('%m-%d %H:%M', time.localtime(r['entry_ts'])),
                            'close_time': time.strftime('%m-%d %H:%M', time.localtime(r['close_ts'])) if r['close_ts'] else None,
                            'symbol': r['symbol'], 'direction': r['direction'],
                            'score': int(r['score'] or 0),
                            'trigger': _comp_trigger(r['components']),
                            'reason': r['close_reason'],
                            'duration_s': r['duration_s'],
                            'pnl': round(r['pnl'] or 0, 4),
                            'pnl_pct': r['pnl_pct'],
                        })
        except Exception:
            pass
        return j(out)

    # ─── إشعارات ───
    async def notifications(request):
        after = int(request.query.get('after', 0))
        if PANEL_DB:
            return j(await PANEL_DB.get_after(after))
        return j({'items': [], 'last_id': after})

    # ─── تحديث الرصيد من المنصة ───
    async def refresh_balance(request):
        try:
            balance = await bot.get_available_usdt()
        except Exception:
            balance = 0.0
        return j({'ok': True, 'balance': round(balance, 2)})

    # ─── تحكم: إيقاف/استئناف ───
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

    # ─── إغلاق شامل فوري ───
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
        closed = await _close_all_positions('👋 إغلاق يدوي من اللوحة')
        return j({'ok': True, 'closed': closed})

    # ─── وضع الطوارئ ───
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

    # ─── إيقاف البوت بأمان ───
    async def stop_bot(request):
        ok = bot.request_shutdown('panel')
        if ok:
            await notify('stop', '🛑 إيقاف البوت', 'طلب إيقاف آمن من اللوحة — سيتوقف خلال ≤60 ثانية')
        return j({'ok': ok, 'error': None if ok else 'البوت يتوقف بالفعل'})

    # ─── مسح البيانات ───
    async def wipe(request):
        try:
            body = await request.json()
        except Exception:
            body = {}
        full = bool(body.get('full'))
        if bot.active_trades:
            return j({'ok': False, 'error':
                      'توجد صفقات مفتوحة: ' + ', '.join(bot.active_trades) +
                      ' — أغلقها أولاً (زر الإغلاق الشامل أو الطوارئ)'}, status=400)
        deleted = []
        async with aiosqlite.connect(bot.db.db_name) as db:
            tables = ['signal_log', 'daily_stats', 'notifications']
            if full:
                tables.append('bot_params')
            for tbl in tables:
                try:
                    cur = await db.execute(f"DELETE FROM {tbl}")
                    deleted.append(f"{tbl}({cur.rowcount})")
                except Exception:
                    pass
            await db.commit()
        if full:
            try:
                bot.tuner.results.clear()
            except Exception:
                pass
        await notify('wipe', '🗑 مسح بيانات' + (' شامل' if full else ''), '، '.join(deleted))
        return j({'ok': True, 'deleted': '، '.join(deleted) or 'لا شيء'})

    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/api/overview', overview)
    app.router.add_get('/api/trades', trades)
    app.router.add_get('/api/today', today)
    app.router.add_get('/api/history', history)
    app.router.add_get('/api/closed', closed)
    app.router.add_get('/api/notifications', notifications)
    app.router.add_post('/api/balance', refresh_balance)
    app.router.add_post('/api/pause', pause)
    app.router.add_post('/api/resume', resume)
    app.router.add_post('/api/close-all', close_all)
    app.router.add_post('/api/emergency', emergency)
    app.router.add_post('/api/emergency-reset', emergency_reset)
    app.router.add_post('/api/stop-bot', stop_bot)
    app.router.add_post('/api/wipe', wipe)
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
        print(f'🖥️ لوحة القناص {PANEL_VERSION} تعمل على المنفذ {port} — 5 تبويبات متزامنة لحظياً')
        return True
    except Exception as e:
        print(f'⚠️ فشل اللوحة (البوت يكمل عمله): {e}')
        return False
