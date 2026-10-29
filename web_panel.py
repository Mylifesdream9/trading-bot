"""
🖥️ Sniper Panel V10 — إعادة بناء كاملة
════════════════════════════════════════════════════
✅ مزامنة لحظة بلحظة مع البوت (تحديث كل 5 ثوانٍ + أعمار بالثواني)
✅ تبويب 📡 الإشارات الحية: كل إشارة مرفوضة مع سبب رفضها التفصيلي + عدادات
✅ تبويب 💰 ربح اليوم: المحقق + الرسوم + الصافي بعد الرسوم
✅ تبويب 📜 السجل الكامل: كل صفقة مغلقة بكل تفاصيلها + كل الأيام + فلتر تاريخ
✅ تبويب 🎛️ التحكم: إيقاف/استئناف، إغلاق الكل، طوارئ، إيقاف البوت، حذف كل البيانات
✅ تبويب 📂 المراكز الحية: كل تفاصيل كل مركز مفتوح (وقف/أهداف/تقدم/عمر/تتبع)
✅ حفظ دائم: كل شيء في قاعدة البيانات عبر DATA_DIR (Railway Volume = يبقى بعد إعادة النشر)
"""

import os
import json
import time
import aiosqlite
from aiohttp import web

PANEL_START = time.time()
DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))

NOTIFY_SCHEMA = """
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL, kind TEXT, title TEXT, body TEXT, level TEXT
)"""

PAGE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🎯 القناص V10</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0f1a;--bg2:#111827;--card:#1a2234;--bord:#2d3748;--txt:#f1f5f9;--sub:#94a3b8;
--green:#00d4aa;--blue:#3b82f6;--purple:#8b5cf6;--orange:#f97316;--red:#ef4444;--yellow:#eab308}
body{font-family:'Tajawal',sans-serif;background:var(--bg);color:var(--txt);min-height:100vh}
.bg{position:fixed;inset:0;background:
radial-gradient(ellipse at 20% 20%,rgba(0,212,170,.07) 0%,transparent 50%),
radial-gradient(ellipse at 80% 80%,rgba(139,92,246,.07) 0%,transparent 50%);pointer-events:none;z-index:0}
.hidden{display:none!important}
.hd{background:var(--bg2);border-bottom:1px solid var(--bord);padding:12px 16px;position:sticky;top:0;z-index:100}
.hd-in{max-width:1400px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.logo{display:flex;align-items:center;gap:12px}
.logo-ic{width:45px;height:45px;background:linear-gradient(135deg,#00d4aa,#00a080);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:22px}
.logo h1{font-size:21px;background:linear-gradient(135deg,var(--green),var(--blue));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.logo span{font-size:11px;color:var(--sub);display:block}
.badge{display:flex;align-items:center;gap:8px;padding:8px 16px;background:rgba(0,212,170,.15);
border:1px solid rgba(0,212,170,.3);border-radius:50px;font-size:13px;color:var(--green)}
.badge.off{background:rgba(239,68,68,.15);border-color:rgba(239,68,68,.3);color:var(--red)}
.dot{width:8px;height:8px;background:var(--green);border-radius:50%;animation:pl 2s infinite}
.badge.off .dot{background:var(--red)}
@keyframes pl{0%,100%{opacity:1}50%{opacity:.4}}
button{font-family:inherit}
.act{padding:10px 18px;border:none;border-radius:10px;font-weight:700;cursor:pointer;font-size:13px;transition:.3s}
.btn-g{background:linear-gradient(135deg,#00d4aa,#00a080);color:#fff}
.btn-r{background:rgba(239,68,68,.15);color:var(--red);border:1px solid rgba(239,68,68,.4)}
.btn-o{background:rgba(249,115,22,.15);color:var(--orange);border:1px solid rgba(249,115,22,.4)}
.btn-s{background:rgba(255,255,255,.08);color:var(--sub);border:1px solid var(--bord)}
main{position:relative;z-index:1;max-width:1400px;margin:0 auto;padding:16px}
.tabs{display:flex;gap:5px;margin-bottom:18px;border-bottom:1px solid var(--bord);overflow-x:auto;padding-bottom:2px}
.tab{padding:12px 16px;border:none;background:transparent;color:var(--sub);cursor:pointer;font-weight:600;
font-size:13px;border-radius:10px 10px 0 0;transition:.2s;white-space:nowrap;position:relative}
.tab.act{color:var(--green);background:rgba(0,212,170,.1)}
.tab.act::after{content:'';position:absolute;bottom:-2px;right:0;left:0;height:2px;background:var(--green)}
.tc{display:none}
.tc.act{display:block;animation:fi .3s}
@keyframes fi{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:14px;margin-bottom:20px}
.card{background:var(--card);border:1px solid var(--bord);border-radius:16px;padding:20px;position:relative;overflow:hidden;transition:.3s}
.card:hover{border-color:rgba(0,212,170,.3)}
.card::before{content:'';position:absolute;top:0;right:0;width:100px;height:100px;border-radius:50%;filter:blur(50px);opacity:.12}
.card.g::before{background:var(--green)}.card.b::before{background:var(--blue)}.card.p::before{background:var(--purple)}
.card.o::before{background:var(--orange)}.card.y::before{background:var(--yellow)}.card.r::before{background:var(--red)}
.card .l{font-size:13px;color:var(--sub)}
.card .v{font-size:28px;font-weight:800;margin:8px 0 4px}
.card .s{font-size:11px;color:var(--sub);padding-top:8px;border-top:1px solid var(--bord);margin-top:8px}
.card.g .v{color:var(--green)}.card.b .v{color:var(--blue)}.card.p .v{color:var(--purple)}
.card.o .v{color:var(--orange)}.card.y .v{color:var(--yellow)}.card.r .v{color:var(--red)}
.pos{color:var(--green)!important}.neg{color:var(--red)!important}
.sec{background:var(--card);border:1px solid var(--bord);border-radius:16px;padding:20px;margin-bottom:20px}
.sec h3{margin-bottom:14px;font-size:16px}
.sec h3 small{color:var(--sub);font-weight:400;font-size:11px;margin-right:8px}
table{width:100%;border-collapse:collapse}
th{text-align:right;padding:9px;color:var(--sub);font-size:11px;border-bottom:1px solid var(--bord)}
td{padding:10px 9px;font-size:13px;border-bottom:1px solid rgba(255,255,255,.04)}
tr:hover td{background:rgba(0,212,170,.03)}
.tag{padding:3px 9px;border-radius:6px;font-size:11px;font-weight:700;display:inline-block}
.tag.buy{background:rgba(0,212,170,.15);color:var(--green)}
.tag.sell{background:rgba(239,68,68,.15);color:var(--red)}
.tag.win{background:rgba(16,185,129,.15);color:#10b981}
.tag.loss{background:rgba(239,68,68,.15);color:var(--red)}
.tag.open{background:rgba(245,158,11,.15);color:#f59e0b}
.tag.info{background:rgba(59,130,246,.15);color:var(--blue)}
.tag.ok{background:rgba(16,185,129,.15);color:#10b981}
.tag.tp{background:rgba(139,92,246,.15);color:var(--purple)}
.chip{padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;display:inline-block;white-space:nowrap}
.c-red{background:rgba(239,68,68,.15);color:var(--red)}
.c-orange{background:rgba(249,115,22,.15);color:var(--orange)}
.c-blue{background:rgba(59,130,246,.15);color:var(--blue)}
.c-purple{background:rgba(139,92,246,.15);color:var(--purple)}
.c-yellow{background:rgba(234,179,8,.15);color:var(--yellow)}
.c-green{background:rgba(0,212,170,.15);color:var(--green)}
.c-gray{background:rgba(148,163,184,.12);color:var(--sub)}
.empty{text-align:center;color:var(--sub);padding:30px;font-size:14px}
.feed{display:flex;flex-direction:column;gap:9px;max-height:560px;overflow-y:auto;padding-left:4px}
.nt{display:flex;gap:12px;padding:13px;background:var(--bg2);border-radius:12px;border-right:4px solid transparent;animation:fi .3s}
.nt.trade{border-right-color:var(--green)}.nt.partial{border-right-color:var(--blue)}
.nt.close{border-right-color:var(--purple)}.nt.error{border-right-color:var(--red)}
.nt.tuner{border-right-color:var(--orange)}.nt.info{border-right-color:var(--sub)}
.nt-ic{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0}
.nt.trade .nt-ic{background:rgba(0,212,170,.15)}.nt.partial .nt-ic{background:rgba(59,130,246,.15)}
.nt.close .nt-ic{background:rgba(139,92,246,.15)}.nt.error .nt-ic{background:rgba(239,68,68,.15)}
.nt.tuner .nt-ic{background:rgba(249,115,22,.15)}.nt.info .nt-ic{background:rgba(148,163,184,.15)}
.nt-b{flex:1;min-width:0}
.nt-t{font-size:14px;font-weight:700;margin-bottom:3px}
.nt-x{font-size:12px;color:var(--sub);line-height:1.6;white-space:pre-wrap;word-break:break-word}
.nt-tm{font-size:10px;color:var(--sub);opacity:.7;direction:ltr;text-align:right;margin-top:4px}
.hg{display:flex;flex-direction:column;gap:10px}
.hi{display:flex;align-items:center;gap:12px;background:var(--bg2);padding:13px;border-radius:12px}
.hd2{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.hd2.ok{background:#10b981;box-shadow:0 0 10px rgba(16,185,129,.5)}
.hd2.bad{background:var(--red);box-shadow:0 0 10px rgba(239,68,68,.5)}
.hd2.warn{background:var(--yellow)}
.hn{font-size:13px;font-weight:600}
.hs{font-size:11px;color:var(--sub)}
.kv{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:13px;gap:12px}
.kv:last-child{border-bottom:none}
.kv b{color:var(--green);text-align:left}
.bar{display:flex;height:6px;border-radius:3px;overflow:hidden;margin-top:10px;background:var(--bg2)}
.rbar{height:22px;border-radius:6px;background:var(--bg2);margin-bottom:7px;position:relative;overflow:hidden}
.rbar>div{height:100%;border-radius:6px;opacity:.85}
.rbar span{position:absolute;inset:0;display:flex;justify-content:space-between;align-items:center;
padding:0 10px;font-size:11px;font-weight:700;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.6)}
.foot{text-align:center;padding:18px;color:var(--sub);font-size:12px;border-top:1px solid var(--bord);margin-top:18px}
.arow{display:flex;gap:10px;flex-wrap:wrap}
.sbar{background:var(--bg2);border:1px solid var(--bord);border-radius:12px;padding:10px 16px;
margin-bottom:16px;display:flex;align-items:center;gap:10px;font-size:12px;color:var(--sub);flex-wrap:wrap}
.sbar b{color:var(--green)}
.sbar .sep{opacity:.3}
details.hrow{background:var(--bg2);border:1px solid var(--bord);border-radius:12px;margin-bottom:8px;overflow:hidden}
details.hrow summary{list-style:none;cursor:pointer;display:grid;gap:8px;padding:12px 14px;font-size:12px;align-items:center}
details.hrow summary::-webkit-details-marker{display:none}
details.hrow[open]{border-color:rgba(0,212,170,.4)}
details.hrow .det{padding:4px 14px 14px;border-top:1px solid var(--bord)}
.dgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:4px 18px;padding-top:10px}
.dgrid .kv{font-size:12px}
.c1{grid-template-columns:110px 1fr 90px 130px 90px}
.c2{grid-template-columns:110px 1fr 90px 130px 90px 110px}
.pbar{height:5px;border-radius:3px;background:var(--bg2);overflow:hidden;margin-top:6px}
.pbar>div{height:100%}
input[type=date]{background:var(--bg2);border:1px solid var(--bord);color:var(--txt);
border-radius:10px;padding:9px 12px;font-family:inherit;font-size:13px}
@media(max-width:768px){.card .v{font-size:22px}.tab{padding:10px 10px;font-size:11px}
.c1,.c2{grid-template-columns:90px 1fr 80px 90px}.dgrid{grid-template-columns:1fr 1fr}}
</style>
</head>
<body>
<div class="bg"></div>

<header class="hd"><div class="hd-in">
  <div class="logo">
    <div class="logo-ic">🎯</div>
    <div><h1>القناص الأسطوري</h1><span id="modeTxt">V10 — مركز العمليات</span></div>
  </div>
  <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
    <div class="badge" id="liveB"><span class="dot"></span><span id="liveT">البوت حي ✓</span></div>
    <button class="act btn-g" onclick="loadAll()">🔄 تحديث</button>
  </div>
</div></header>

<main>
<div class="sbar">
  ⏱️ مزامنة: <b id="lastUpd">—</b><span class="sep">•</span>
  🕐 وقت الخادم: <b id="srvT">—</b><span class="sep">•</span>
  🔄 آخر دورة بوت: <b id="loopAgo">—</b><span class="sep">•</span>
  📡 آخر مسح: <b id="scanAgo">—</b><span class="sep">•</span>
  💓 الأسعار: <b id="pxAge">—</b><span class="sep">•</span>
  ⚡ تحديث تلقائي كل 5 ثوانٍ
</div>

<div class="tabs">
  <button class="tab act" onclick="sw('overview',this)">📊 نظرة عامة</button>
  <button class="tab" onclick="sw('positions',this)">📂 المراكز الحية</button>
  <button class="tab" onclick="sw('signals',this)">📡 الإشارات الحية</button>
  <button class="tab" onclick="sw('today',this)">💰 ربح اليوم</button>
  <button class="tab" onclick="sw('history',this)">📜 السجل الكامل</button>
  <button class="tab" onclick="sw('notifications',this)">🔔 سجل البوت <span id="nCount" class="tag ok" style="padding:1px 7px;font-size:10px">0</span></button>
  <button class="tab" onclick="sw('tuner',this)">🧠 المطوّر</button>
  <button class="tab" onclick="sw('control',this)">🎛️ التحكم</button>
  <button class="tab" onclick="sw('system',this)">⚙️ النظام</button>
</div>

<!-- نظرة عامة -->
<div class="tc act" id="t-overview">
  <div class="grid">
    <div class="card g"><div class="l">💵 الرصيد</div><div class="v" id="balance">$0</div><div class="s" id="modeSub">—</div></div>
    <div class="card b"><div class="l">💰 صافي اليوم (بعد الرسوم)</div><div class="v" id="netToday">$0</div><div class="s" id="netSub">—</div></div>
    <div class="card p"><div class="l">🏆 نسبة الفوز</div><div class="v" id="wrAll">—</div><div class="s" id="allWl">—</div></div>
    <div class="card o"><div class="l">📂 المراكز المفتوحة</div><div class="v" id="openC">0</div><div class="s" id="slotsS">—</div></div>
    <div class="card y"><div class="l">🧠 فوز آخر 10</div><div class="v" id="wr10">—</div><div class="s" id="tunerS">—</div></div>
  </div>
  <div class="grid" style="grid-template-columns:2fr 1fr">
    <div class="sec"><h3>📂 آخر المراكز الحية <small>— التفاصيل الكاملة في تبويب المراكز</small></h3><div id="openMini">—</div></div>
    <div class="sec"><h3>🛡️ الحمايات</h3><div class="hg" id="healthBox">—</div></div>
  </div>
  <div class="sec"><h3>⚡ آخر أحداث البوت <small>— كل إجراء صغير وكبير</small></h3><div class="feed" id="liveFeed" style="max-height:300px"></div></div>
</div>

<!-- المراكز الحية -->
<div class="tc" id="t-positions">
  <div class="sec"><h3>📂 المراكز المفتوحة الآن — كل التفاصيل لحظة بلحظة</h3><div id="posBox">—</div></div>
</div>

<!-- الإشارات الحية -->
<div class="tc" id="t-signals">
  <div class="sec"><h3>🔍 ملخص آخر دورة مسح</h3><div id="scanSum">—</div></div>
  <div class="sec"><h3>🚫 أسباب الرفض (آخر 24 ساعة)</h3><div id="rejBars">—</div></div>
  <div class="sec"><h3>🚫 البث الحي: كل إشارة مرفوضة وسببها <small>— مباشر من قلب البوت</small></h3>
    <div style="max-height:480px;overflow-y:auto" id="rejFeed">—</div></div>
  <div class="sec"><h3>✅ الإشارات المنفذة</h3><div id="sigBox">—</div></div>
</div>

<!-- ربح اليوم -->
<div class="tc" id="t-today">
  <div id="todayCards">—</div>
  <div class="sec"><h3>🏁 صفقات اليوم المغلقة</h3><div id="todayTrades">—</div></div>
</div>

<!-- السجل الكامل -->
<div class="tc" id="t-history">
  <div class="sec">
    <h3>📜 كل الصفقات المغلقة — تاريخ كامل بكل التفاصيل</h3>
    <div class="arow" style="margin-bottom:14px;align-items:center">
      <input type="date" id="histDate" onchange="histOffset=0;loadHistory()">
      <button class="act btn-s" onclick="document.getElementById('histDate').value='';histOffset=0;loadHistory()">كل التواريخ</button>
      <button class="act btn-s" onclick="histOffset+=100;loadHistory()">الأقدم ↓</button>
      <span style="color:var(--sub);font-size:12px" id="histCount">—</span>
    </div>
    <div id="histBox">—</div>
  </div>
  <div class="sec"><h3>🗓️ الأداء لكل يوم (كل التاريخ)</h3><div id="daysBox">—</div></div>
  <div class="sec"><h3>🏆 إجماليات الحساب عبر التاريخ</h3><div id="aggBox">—</div></div>
</div>

<!-- سجل البوت -->
<div class="tc" id="t-notifications">
  <div class="sec"><h3>🔔 كل ما يقوم به البوت — لحظة بلحظة</h3><div class="feed" id="notifFeed"></div></div>
</div>

<!-- المطوّر -->
<div class="tc" id="t-tuner">
  <div class="grid" style="grid-template-columns:1fr 1fr">
    <div class="sec"><h3>🧠 الحالة</h3><div id="tunerSt">—</div></div>
    <div class="sec"><h3>📈 آخر 20 نتيجة</h3><div id="tunerH">—</div><div class="bar" id="tunerBar"></div></div>
  </div>
</div>

<!-- التحكم -->
<div class="tc" id="t-control">
  <div class="grid" style="grid-template-columns:1fr 1fr">
    <div class="sec"><h3>🎛️ أوامر التشغيل</h3>
      <div class="arow" style="margin-bottom:12px">
        <button class="act btn-s" id="pauseBtn" onclick="doPause()">⏸️ إيقاف مؤقت</button>
        <button class="act btn-o" onclick="doEmergency()">🚨 الطوارئ: إيقاف + إغلاق الكل</button>
      </div>
      <div class="arow" style="margin-bottom:12px">
        <button class="act btn-r" onclick="doCloseAll()">🛑 إغلاق كل الصفقات فوراً</button>
        <button class="act btn-r" onclick="doShutdown()">⏹️ إيقاف البوت تماماً</button>
      </div>
      <div class="arow">
        <button class="act btn-s" onclick="doBalance()">🔄 تحديث الرصيد من المنصة</button>
        <button class="act btn-r" onclick="doWipe()">🗑️ حذف كل البيانات</button>
      </div>
      <p style="color:var(--sub);font-size:11px;margin-top:12px;line-height:1.8">
      ⚠️ «الطوارئ» = إيقاف التداول الجديد + إغلاق كل المراكز بسعر السوق.<br>
      ⏹️ «إيقاف البوت» يوقف العملية بالكامل بأمان — الستوبات على المنصة تبقى تحمي المراكز.<br>
      🗑️ «حذف كل البيانات» يمسح السجلات والإشعارات والإحصائيات — لا رجوع بعدها.<br>
      🛡️ المراكز محمية دائماً بستوب المنصة حتى لو انهار البوت.</p>
    </div>
    <div class="sec"><h3>💾 التخزين والبقاء بعد إعادة النشر</h3><div id="storeBox">—</div></div>
  </div>
</div>

<!-- النظام -->
<div class="tc" id="t-system">
  <div class="grid" style="grid-template-columns:1fr 1fr">
    <div class="sec"><h3>⚙️ الإعدادات والفلاتر</h3><div id="setBox">—</div></div>
    <div>
      <div class="sec"><h3>🚨 الأخطاء</h3><div id="errBox">—</div></div>
      <div class="sec"><h3>ℹ️ عن اللوحة</h3>
        <div class="kv"><span>الإصدار</span><b>لوحة V10 + بوت V8.4</b></div>
        <div class="kv"><span>مدة التشغيل</span><b id="upT">—</b></div>
        <div class="kv"><span>دورات المسح</span><b id="scanN">—</b></div>
      </div>
    </div>
  </div>
</div>

<div class="foot">🔥 القناص الأسطوري V10 — مركز العمليات | مزامنة لحظية • سجل كامل • تحكم شامل</div>
</main>

<script>
let lastNid = 0, timer = null, cur = 'overview', histOffset = 0;

async function api(path){
  const c = new AbortController();
  const t = setTimeout(()=>c.abort(), 8000);
  try{
    const res = await fetch(path, {signal:c.signal, cache:'no-store'});
    if(!res.ok) throw new Error('HTTP ' + res.status);
    return await res.json();
  }finally{ clearTimeout(t); }
}
async function post(path){
  const c = new AbortController();
  const t = setTimeout(()=>c.abort(), 30000);
  try{
    const r = await fetch(path, {method:'POST', signal:c.signal});
    return await r.json();
  }finally{ clearTimeout(t); }
}
function sw(name, el){
  cur = name;
  document.querySelectorAll('.tc').forEach(x=>x.classList.remove('act'));
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('act'));
  document.getElementById('t-'+name).classList.add('act');
  el.classList.add('act');
  if(name==='history') loadHistory();
  if(name==='control') loadStorage();
}
function mo(v){return (v>=0?'+':'') + '$' + Math.abs(v).toFixed(2)}
function sg(v,d){d=d||1;return (v>=0?'+':'') + (+v).toFixed(d)}
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function ago(ts){ if(!ts) return '—'; const s = Math.max(0, Math.floor(Date.now()/1000 - ts));
  if(s<60) return 'قبل ' + s + ' ث'; if(s<3600) return 'قبل ' + Math.floor(s/60) + ' د'; if(s<86400) return 'قبل ' + Math.floor(s/3600) + ' س'; return 'قبل ' + Math.floor(s/86400) + ' يوم'; }
function dur(sec){ if(sec==null) return '—'; sec = Math.floor(sec);
  if(sec<60) return sec + ' ث'; const h = Math.floor(sec/3600), m = Math.floor((sec%3600)/60);
  return h>0 ? h+'س '+m+'د' : m+'د'; }
const DIR = {BUY:['شراء','buy'],SELL:['بيع','sell']};
function dirTag(d){ const m = DIR[d]||[d,'gray']; return '<span class="tag '+m[1]+'">'+m[0]+'</span>'; }
const STAGES = {
  data:['فشل بيانات الشموع','red'], price:['لا سعر حي','red'],
  spread:['سبريد واسع','orange'], volume:['سيولة 24س منخفضة','orange'],
  no_ob:['لا يوجد Order Block','gray'], far_ob:['OB بعيد عن السعر','blue'],
  no_trigger:['لا Sweep ولا Retest','purple'], stoch:['ستوكاستك بلا تقاطع','blue'],
  score:['تقييم أقل من الحد','yellow'], atr:['ATR غير صالح','red'],
  sl:['وقف غير صالح','red'], risk:['مخاطرة خارج الحدود','orange'],
  slot:['الخانات ممتلئة','orange'], paused:['التداول موقوف','gray'],
  cooldown:['فترة تهدئة','gray'], dup:['صفقة مفتوحة مسبقاً','gray'],
  balance:['رصيد غير كافٍ','red'], qty:['كمية دون حدود الزوج','gray']};
function stageChip(s){ const m = STAGES[s] || [s,'gray']; return '<span class="chip c-'+m[1]+'">'+m[0]+'</span>'; }
const KM = {trade:['trade','🟢'],partial:['partial','🎯'],close:['close','🏁'],
error:['error','🚨'],tuner:['tuner','🧠'],info:['info','ℹ️'],system:['info','⚙️']};

/* ─── الرسوم ─── */
function detRow(kvPairs){ return '<div class="dgrid">' + kvPairs.map(p=>
  '<div class="kv"><span>'+p[0]+'</span><b>'+p[1]+'</b></div>').join('') + '</div>'; }

function tradeRow(r, withDate){
  const win = r.total_pnl >= 0;
  const head =
    '<div style="display:contents">' +
    '<div><b>'+esc(r.symbol)+'</b></div>' +
    '<div>'+dirTag(r.side)+' <span style="color:var(--sub);font-size:11px">'+esc(r.trigger||'—')+'</span></div>' +
    '<div class="'+(win?'pos':'neg')+'"><b>'+mo(r.total_pnl)+'</b></div>' +
    '<div style="color:var(--sub)">'+sg(r.pnl_pct)+'% من الهامش</div>' +
    '<div style="color:var(--sub)">'+esc(withDate?(r.date_str||''):dur(r.duration_sec))+'</div>' +
    (withDate?'':'<div style="color:var(--sub);font-size:11px">'+esc(r.reason||'')+'</div>') +
    '</div>';
  const det = detRow([
    ['⏰ الدخول', esc(r.entry_str||'—')], ['⏰ الخروج', esc(r.exit_str||'—')],
    ['⏱️ المدة', dur(r.duration_sec)], ['🎯 الزناد', esc(r.trigger||'—')],
    ['📊 التقييم', (r.score!=null? r.score+'/8':'—')],
    ['💵 سعر الدخول', esc(r.entry_price)], ['💵 سعر الخروج', esc(r.exit_price)],
    ['📦 الكمية الأولية', esc(r.qty_initial)], ['📦 الكمية المتبقية', esc(r.qty_final)],
    ['🧾 الجني الجزئي', '$'+(+(r.realized_partial||0)).toFixed(4)],
    ['🛑 آخر ستوب', esc(r.sl)], ['🎯 TP1', esc(r.tp1)], ['🎯 TP2', esc(r.tp2)],
    ['⬆️ أعلى سعر', esc(r.highest)], ['⬇️ أدنى سعر', esc(r.lowest)],
    ['🏁 سبب الإغلاق', esc(r.reason||'—')],
  ]);
  return '<details class="hrow"><summary class="c'+(withDate?'2':'1')+'">'+head+'</summary>'+det+'</details>';
}

/* ─── الأجزاء ─── */
function renderHeader(ov){
  document.getElementById('lastUpd').textContent =
    new Date().toLocaleTimeString('ar',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
  if(ov.server_now) document.getElementById('srvT').textContent =
    new Date(ov.server_now*1000).toLocaleTimeString('ar',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
  document.getElementById('loopAgo').textContent = ago(ov.last_loop_ts);
  const lsa = ov.last_scan && ov.last_scan.ts ? ago(ov.last_scan.ts) : '—';
  document.getElementById('scanAgo').textContent = lsa;
  document.getElementById('pxAge').textContent = ov.price_age < 120 ? 'حية ✓' : 'متوقفة ' + ov.price_age + 'ث';
  const lv = ov.price_age < 120 && ov.last_loop_age != null && ov.last_loop_age < 180;
  document.getElementById('liveB').className = 'badge' + (lv?'':' off');
  document.getElementById('liveT').textContent = lv ? 'البوت حي ✓' : 'انتبه: البوت صامت!';
  const mode = ov.trade_enabled ? (ov.testnet ? '⚔️ تجريبي 🧪' : '⚔️ تداول حقيقي') : '👁️ مراقبة';
  document.getElementById('modeTxt').textContent = mode + ' • V10';
  document.getElementById('upT').textContent = dur(ov.uptime*60);
  document.getElementById('scanN').textContent = ov.scans;
}

function renderOverview(ov){
  document.getElementById('balance').textContent = '$' + (+ov.balance).toFixed(2);
  document.getElementById('modeSub').textContent = ov.leverage+'x • هامش $'+ov.trade_size+' • '+ov.pairs+' زوج';
  const nt = ov.net_today, ntEl = document.getElementById('netToday');
  ntEl.textContent = mo(nt); ntEl.className = 'v ' + (nt>=0?'pos':'neg');
  document.getElementById('netSub').textContent =
    'محقق: ' + mo(ov.today.pnl) + ' • رسوم: $' + (+ov.fees_today).toFixed(2);
  const tot = ov.stats.wins + ov.stats.losses;
  document.getElementById('wrAll').textContent = tot ? Math.round(ov.stats.wins/tot*100)+'%' : '—';
  document.getElementById('allWl').textContent = ov.stats.wins+'W / '+ov.stats.losses+'L';
  document.getElementById('openC').textContent = ov.open_trades;
  document.getElementById('slotsS').textContent = 'خانات: '+ov.open_trades+'/'+ov.max_open+' • تشغيل: '+dur(ov.uptime*60);
  document.getElementById('wr10').textContent = ov.tuner.winrate || '—';
  document.getElementById('tunerS').textContent = 'عتبة: '+ov.tuner.min_score+'/8';
  const mode = ov.trade_enabled ? (ov.testnet?'تداول تجريبي':'تداول حقيقي') : 'مراقبة فقط';
  document.getElementById('healthBox').innerHTML = [
    ['تدفق الأسعار', ov.price_age<120?'متصل ✓':'متوقف '+ov.price_age+'ث', ov.price_age<120?'ok':'bad'],
    ['دورة البوت', ov.last_loop_age!=null?('قبل '+ov.last_loop_age+'ث'):'—', (ov.last_loop_age!=null&&ov.last_loop_age<180)?'ok':'bad'],
    ['ستوبات المنصة', ov.open_trades>0?'مفعّلة على كل مركز':'لا مراكز', 'ok'],
    ['الوضع', mode, ov.trade_enabled?'ok':'warn'],
    ['رصيد كافٍ', '$'+(+ov.balance).toFixed(2), ov.balance>=ov.trade_size?'ok':'warn'],
  ].map(h=>'<div class="hi"><div class="hd2 '+h[2]+'"></div><div><div class="hn">'+h[0]+'</div><div class="hs">'+h[1]+'</div></div></div>').join('');
}

function renderPositions(list){
  const box = document.getElementById('posBox');
  const mini = document.getElementById('openMini');
  if(!list || !list.length){
    box.innerHTML = '<div class="empty">لا مراكز مفتوحة — القناص يراقب السوق 🔭</div>';
    mini.innerHTML = '<div class="empty">لا مراكز مفتوحة</div>'; return;
  }
  let h = '';
  list.forEach(t=>{
    const win = (t.pnl||0) >= 0;
    const prog = Math.max(0, Math.min(100, Math.abs(t.dist_tp1_pct||0) / (Math.abs(t.dist_tp1_pct||0)+Math.abs(t.dist_sl_pct||0)+1e-9) * 100));
    const head = '<div style="display:contents">' +
      '<div><b>'+esc(t.symbol)+'</b><div style="font-size:10px;color:var(--sub)">'+ago(t.entry_ts)+'</div></div>' +
      '<div>'+dirTag(t.side)+' '+esc(t.entry)+' <span style="color:var(--sub)">→</span> <b>'+esc(t.current||'—')+'</b></div>' +
      '<div class="'+(win?'pos':'neg')+'"><b>'+mo(t.pnl)+'</b></div>' +
      '<div style="color:var(--sub)">'+sg(t.pnl_pct)+'% هامش</div>' +
      '<div>'+(t.partial?'<span class="tag info">🎯 جُني 70%</span>':'<span class="tag open">⏳ جديدة</span>')+' '+(t.trailing?'<span class="tag tp">🧲 تتبع</span>':'')+'</div>' +
      (t.stop_ok?'':'<div><span class="tag loss">⚠️ بلا ستوب منصة</span></div>') +
      '</div>';
    const det = detRow([
      ['💵 الدخول', t.entry], ['💵 السعر الحالي', t.current||'—'],
      ['📦 الكمية', t.qty], ['📦 الكمية الأولية', t.qty_initial],
      ['💼 الهامش', '$'+t.margin], ['💼 القيمة الاسمية', '$'+t.notional],
      ['🛑 الوقف الحالي', t.sl], ['📏 مسافة الوقف', sg(t.dist_sl_pct)+'%'],
      ['🎯 TP1', t.tp1], ['📏 مسافة TP1', sg(t.dist_tp1_pct)+'%'],
      ['🎯 TP2', t.tp2], ['🧾 الجني الجزئي المحقق', '$'+(+(t.realized||0)).toFixed(4)],
      ['⬆️ أعلى سعر وصل', t.highest], ['⬇️ أدنى سعر وصل', t.lowest],
      ['⏰ وقت الدخول', t.entry_str], ['⏱️ عمر المركز', t.age_str],
      ['🎯 الزناد', t.trigger||'—'], ['📊 التقييم', t.score!=null? t.score+'/8':'—'],
      ['🛡️ ستوب المنصة', t.stop_ok?'مثبّت ✓':'غير مؤكد ⚠️'],
    ]) + '<div style="margin-top:10px;font-size:11px;color:var(--sub)">التقدم نحو TP1 مقابل الوقف:</div>' +
      '<div class="pbar"><div style="width:'+prog+'%;background:linear-gradient(90deg,#00d4aa,#3b82f6)"></div></div>';
    h += '<details class="hrow"><summary class="c2">'+head+'</summary>'+det+'</details>';
  });
  box.innerHTML = h;
  mini.innerHTML = list.slice(0,4).map(t=>
    '<div class="hi"><div class="hd2 '+((t.pnl||0)>=0?'ok':'bad')+'"></div><div><div class="hn">'+esc(t.symbol)+' '+dirTag(t.side)+'</div><div class="hs">'+mo(t.pnl)+' • '+sg(t.pnl_pct)+'% هامش</div></div></div>').join('');
}

function renderRejections(rj){
  const ls = rj.last_scan;
  const sb = document.getElementById('scanSum');
  if(ls && ls.ts){
    sb.innerHTML = '<div class="grid" style="margin-bottom:0">' +
      '<div class="card b"><div class="l">⏰ آخر مسح</div><div class="v" style="font-size:18px">'+ago(ls.ts)+'</div></div>' +
      '<div class="card g"><div class="l">🔥 عملات متقلبة</div><div class="v">'+ls.volatile+'</div><div class="s">مفحوصة: '+ls.scanned+'</div></div>' +
      '<div class="card o"><div class="l">🚫 مرفوضة (سيولة)</div><div class="v">'+(ls.vol_filtered||0)+'</div><div class="s">غير متقلبة: '+(ls.not_volatile||0)+'</div></div>' +
      '<div class="card p"><div class="l">✅ إشارات ناجية</div><div class="v">'+ls.signals+'</div><div class="s">من أصل '+ls.scanned+' مفحوصة</div></div>' +
      '</div>';
  } else sb.innerHTML = '<div class="empty">لم يكتمل أي مسح بعد</div>';
  const keys = Object.keys(rj.counts||{}).sort((a,b)=>rj.counts[b]-rj.counts[a]);
  const maxC = keys.length ? rj.counts[keys[0]] : 0;
  document.getElementById('rejBars').innerHTML = keys.length ?
    keys.map(k=>{ const m = STAGES[k]||[k,'gray'];
      const w = Math.round(rj.counts[k]/maxC*100);
      return '<div class="rbar"><div style="width:'+w+'%;background:var(--'+(m[1]==='gray'?'sub':m[1])+')"></div>' +
        '<span><span>'+m[0]+'</span><span>'+rj.counts[k]+'</span></span></div>'; }).join('')
    : '<div class="empty">لا رفض في آخر 24 ساعة</div>';
  const items = rj.items||[];
  document.getElementById('rejFeed').innerHTML = items.length ?
    '<table><tr><th>الوقت</th><th>الزوج</th><th>الاتجاه</th><th>السبب</th><th>التفصيل</th></tr>' +
    items.map(e=>'<tr><td style="color:var(--sub);font-size:11px">'+esc(e.time)+'</td>' +
      '<td><b>'+esc(e.symbol)+'</b></td><td>'+(e.trend?dirTag(e.trend):'—')+'</td>' +
      '<td>'+stageChip(e.stage)+'</td><td style="font-size:11px;color:var(--sub)">'+esc(e.detail)+'</td></tr>').join('') +
    '</table>' : '<div class="empty">لا رفض مسجل بعد — انتظر أول دورة مسح</div>';
}

function renderToday(td){
  const wr = td.total>0 ? Math.round(td.wins/td.total*100)+'%' : '—';
  document.getElementById('todayCards').innerHTML = '<div class="grid">' +
    '<div class="card '+(td.net>=0?'g':'r')+'"><div class="l">💰 الصافي بعد الرسوم</div><div class="v '+(td.net>=0?'pos':'neg')+'">'+mo(td.net)+'</div><div class="s">'+esc(td.date)+'</div></div>' +
    '<div class="card b"><div class="l">💵 المحقق (قبل الرسوم)</div><div class="v '+(td.realized>=0?'pos':'neg')+'">'+mo(td.realized)+'</div></div>' +
    '<div class="card o"><div class="l">🧾 رسوم اليوم</div><div class="v">$'+(+td.fees).toFixed(2)+'</div><div class="s">'+(td.fees_zero?'(مراقبة/تجريبي — بلا رسوم فعلية)':'عمولات المنصة اليوم')+'</div></div>' +
    '<div class="card p"><div class="l">📂 صفقات اليوم</div><div class="v">'+td.total+'</div></div>' +
    '<div class="card y"><div class="l">🏆 نسبة الفوز</div><div class="v">'+wr+'</div><div class="s">✅ '+td.wins+' • ❌ '+td.losses+'</div></div>' +
    '</div>';
  document.getElementById('todayTrades').innerHTML = td.trades.length ?
    td.trades.map(r=>tradeRow(r,false)).join('') : '<div class="empty">لا صفقات مغلقة اليوم بعد</div>';
}

function renderSignals(list){
  const sb = document.getElementById('sigBox');
  if(!list || !list.length){ sb.innerHTML = '<div class="empty">لا إشارات منفذة بعد</div>'; return; }
  sb.innerHTML = '<table><tr><th>الوقت</th><th>الزوج</th><th>الاتجاه</th><th>التقييم</th><th>الزناد</th><th>النتيجة</th></tr>' +
    list.map(s=>{
      const r = s.result===1?'<span class="tag win">ربح '+mo(s.pnl)+'</span>':s.result===0?'<span class="tag loss">خسارة '+mo(s.pnl)+'</span>':'<span class="tag open">جارية</span>';
      return '<tr><td style="color:var(--sub);font-size:11px">'+esc(s.time)+'</td><td><b>'+esc(s.symbol)+'</b></td>' +
        '<td>'+dirTag(s.direction)+'</td><td><b>'+s.score+'/8</b></td>' +
        '<td>'+(s.trigger==='sweep'?'⚡ كنس سيولة':s.trigger==='retest'?'🔄 إعادة اختبار':esc(s.trigger||'—'))+'</td><td>'+r+'</td></tr>';
    }).join('') + '</table>';
}

async function loadHistory(){
  try{
    const d = document.getElementById('histDate').value;
    const q = '?offset='+histOffset+'&limit=100' + (d?'&date='+d:'');
    const h = await api('/api/history'+q);
    const days = await api('/api/history/days');
    document.getElementById('histCount').textContent = 'الإجمالي: ' + h.total + ' صفقة' + (d?' (بتاريخ '+d+')':'');
    document.getElementById('histBox').innerHTML = h.rows.length ?
      h.rows.map(r=>tradeRow(r,true)).join('') : '<div class="empty">لا صفقات في هذا النطاق — السجل يبدأ من تحديث V10</div>';
    document.getElementById('daysBox').innerHTML = days.days.length ?
      '<table><tr><th>اليوم</th><th>النتيجة</th><th>✅</th><th>❌</th><th>المجموع</th><th>الفوز</th></tr>' +
      days.days.map(x=>'<tr><td><b>'+x.date+'</b></td><td class="'+(x.pnl>=0?'pos':'neg')+'"><b>'+mo(x.pnl)+'</b></td>' +
        '<td style="color:var(--green)">'+x.wins+'</td><td style="color:var(--red)">'+x.losses+'</td><td>'+x.total+'</td><td>'+(x.winrate!=null?x.winrate+'%':'—')+'</td></tr>').join('') +
      '</table>' : '<div class="empty">لا أيام مسجلة بعد</div>';
    const a = days.agg;
    document.getElementById('aggBox').innerHTML =
      '<div class="kv"><span>أيام نشطة</span><b>'+a.active_days+'</b></div>' +
      '<div class="kv"><span>إجمالي الصفقات المغلقة</span><b>'+a.total_closed+'</b></div>' +
      '<div class="kv"><span>رابحة / خاسرة</span><b>'+a.total_wins+' / '+(a.total_closed-a.total_wins)+'</b></div>' +
      '<div class="kv"><span>نسبة الفوز التاريخية</span><b>'+(a.overall_winrate!=null?a.overall_winrate+'%':'—')+'</b></div>' +
      '<div class="kv"><span>إجمالي الربح/الخسارة</span><b class="'+(a.total_pnl>=0?'pos':'neg')+'">'+mo(a.total_pnl)+'</b></div>' +
      (a.best_day?'<div class="kv"><span>🥇 أفضل يوم</span><b>'+a.best_day.date+' ('+mo(a.best_day.pnl)+')</b></div>':'') +
      (a.worst_day?'<div class="kv"><span>💀 أسوأ يوم</span><b>'+a.worst_day.date+' ('+mo(a.worst_day.pnl)+')</b></div>':'');
  }catch(e){ console.error(e); }
}

function renderNotifs(nf){
  if(nf.items && nf.items.length){
    lastNid = nf.last_id || lastNid;
    document.getElementById('nCount').textContent = nf.total_unread || nf.items.length;
    const feed = document.getElementById('notifFeed');
    const lf = document.getElementById('liveFeed');
    let html = '';
    nf.items.forEach(n=>{
      const k = KM[n.kind] || KM.info;
      html += '<div class="nt '+k[0]+'"><div class="nt-ic">'+k[1]+'</div>' +
        '<div class="nt-b"><div class="nt-t">'+esc(n.title)+'</div>' +
        (n.body?'<div class="nt-x">'+esc(n.body)+'</div>':'') +
        '<div class="nt-tm">'+n.time+'</div></div></div>';
    });
    feed.innerHTML = html + feed.innerHTML;
    lf.innerHTML = html + lf.innerHTML;
    while(lf.children.length>12) lf.removeChild(lf.lastChild);
    while(feed.children.length>200) feed.removeChild(feed.lastChild);
  }
}

function renderTuner(ov){
  const tu = ov.tuner;
  document.getElementById('tunerSt').innerHTML =
    '<div class="kv"><span>الحد الأدنى للتقييم</span><b>'+tu.min_score+' / 8 (ثابت)</b></div>' +
    '<div class="kv"><span>نطاق القرب من OB</span><b>'+(tu.proximity_pct*100).toFixed(1)+'%</b></div>' +
    '<div class="kv"><span>ستوك صارم</span><b>'+(tu.strict_stoch?'نعم':'لا')+'</b></div>' +
    '<div class="kv"><span>فوز آخر 10</span><b>'+(tu.winrate||'غير كافٍ')+'</b></div>';
  api('/api/tuner-history').then(hist=>{
    const th = document.getElementById('tunerH');
    const bar = document.getElementById('tunerBar');
    if(hist && hist.length){
      th.innerHTML = hist.map(w=>'<span class="tag '+(w?'win':'loss')+'" style="width:26px;text-align:center">'+(w?'✓':'✗')+'</span>').join(' ');
      bar.innerHTML = hist.map(w=>'<div style="flex:1;background:'+(w?'#10b981':'#ef4444')+'"></div>').join('');
    } else { th.innerHTML='<div class="empty">لا نتائج بعد</div>'; bar.innerHTML=''; }
  }).catch(()=>{});
}

function renderErrors(er){
  const eb = document.getElementById('errBox');
  const ek = Object.keys(er.errors||{});
  if(!ek.length){ eb.innerHTML='<div class="empty" style="padding:16px">✅ لا أخطاء — كل شيء نظيف</div>'; }
  else{ eb.innerHTML = ek.map(k=>'<div class="kv"><span>'+esc(k)+'</span><b style="color:var(--orange)">×'+er.errors[k]+'</b></div>').join(''); }
}

function renderSettings(ov){
  document.getElementById('setBox').innerHTML =
    '<div class="kv"><span>الوضع</span><b>'+(ov.trade_enabled?'⚔️ تداول':'👁️ مراقبة')+(ov.testnet?' 🧪':'')+'</b></div>' +
    '<div class="kv"><span>الرافعة</span><b>'+ov.leverage+'x</b></div>' +
    '<div class="kv"><span>هامش الصفقة</span><b>$'+ov.trade_size+'</b></div>' +
    '<div class="kv"><span>القيمة الاسمية</span><b>$'+(ov.trade_size*ov.leverage)+'</b></div>' +
    '<div class="kv"><span>الصفقات المتزامنة</span><b>'+ov.max_open+'</b></div>' +
    '<div class="kv"><span>أرضية TP1 (من الهامش)</span><b>'+((ov.tp1_floor||0.18)*100).toFixed(0)+'%</b></div>' +
    '<div class="kv"><span>أدنى سيولة 24س</span><b>$'+((ov.min_qvol||15000000)/1e6).toFixed(0)+'M</b></div>' +
    '<div class="kv"><span>أقصى سبريد مسموح</span><b>'+(ov.max_spread||0.15)+'%</b></div>' +
    '<div class="kv"><span>فترة التهدئة</span><b>15 دقيقة</b></div>' +
    '<div class="kv"><span>أزواج محملة</span><b>'+ov.pairs+'</b></div>';
}

async function loadStorage(){
  try{
    const s = await api('/api/storage');
    document.getElementById('storeBox').innerHTML =
      '<div class="kv"><span>مجلد البيانات</span><b style="font-size:11px">'+esc(s.data_dir)+'</b></div>' +
      '<div class="kv"><span>قاعدة البيانات</span><b>'+(s.db_exists? s.db_size_kb+' KB ✓':'لم تُنشأ بعد')+'</b></div>' +
      '<div class="kv"><span>ملف السجل</span><b>'+(s.log_exists? s.log_size_kb+' KB':'—')+'</b></div>' +
      '<div class="kv"><span>Volume مثبّت</span><b>'+(s.volume?'✅ نعم — البيانات تدوم':'⚠️ لا')+'</b></div>' +
      (s.volume? '' : '<p style="color:var(--orange);font-size:11px;margin-top:10px;line-height:1.8">⚠️ بدون Volume: إعادة النشر على Railway تمسح كل السجلات!<br>الحل: Railway → Service → Volumes → أنشئ Volume واضبط المتغير <b>DATA_DIR</b> بمسار الـVolume (مثال: /data)</p>');
  }catch(e){ console.error(e); }
}

/* ─── التحكم ─── */
async function doPause(){
  try{
    const ov = await api('/api/overview');
    const r = await post(ov.trade_enabled ? '/api/pause' : '/api/resume');
    if(r.ok===false) alert('فشل: ' + r.error);
    loadAll();
  }catch(e){ alert('فشل: '+e.message); }
}
async function doCloseAll(){
  if(!confirm('⚠️ إغلاق كل الصفقات فوراً بسعر السوق؟')) return;
  const r = await post('/api/close-all');
  alert('أُغلق: ' + ((r.closed&&r.closed.length) ? r.closed.join(', ') : 'لا شيء'));
  loadAll();
}
async function doEmergency(){
  if(!confirm('🚨 الطوارئ: سيتم إيقاف التداول الجديد وإغلاق كل المراكز فوراً. متابعة؟')) return;
  const r = await post('/api/emergency');
  alert(r.ok ? '🚨 تم: أُوقف التداول وأُغلق ' + (r.closed?r.closed.length:0) + ' مركز' : ('فشل: '+r.error));
  loadAll();
}
async function doShutdown(){
  if(!confirm('⏹️ إيقاف البوت تماماً؟\nالستوبات على المنصة تبقى تحمي المراكز.\nستحتاج لإعادة تشغيل الخدمة من Railway.')) return;
  if(!confirm('تأكيد أخير: إيقاف العملية بالكامل؟')) return;
  await post('/api/shutdown');
  alert('تم إرسال أمر الإيقاف الآمن — البوت سيتوقف بعد الدورة الحالية.');
}
async function doWipe(){
  if(!confirm('🗑️ حذف كل البيانات؟ (السجل التاريخي + الإشعارات + الإحصائيات)')) return;
  const txt = prompt('للتأكيد اكتب: حذف');
  if(txt !== 'حذف') return;
  const ov = await api('/api/overview');
  let url = '/api/wipe';
  if(ov.open_trades > 0 && confirm('توجد ' + ov.open_trades + ' مركز مفتوح — حذفها أيضاً من السجلات؟')) url += '?force=1';
  const r = await post(url);
  alert(r.ok ? '🗑️ تم حذف كل البيانات' : ('فشل: '+r.error));
  lastNid = 0; loadAll();
}
async function doBalance(){
  try{ const r = await api('/api/balance'); alert('الرصيد من المنصة: $' + (+r.balance).toFixed(2)); loadAll(); }
  catch(e){ alert('فشل: '+e.message); }
}

/* ─── الحلقة ─── */
async function loadAll(){
  try{
    const ov = await api('/api/overview');
    renderHeader(ov); renderOverview(ov); renderTuner(ov); renderSettings(ov);
    const pos = await api('/api/positions'); renderPositions(pos);
    const rj = await api('/api/rejections'); renderRejections(rj);
    const td = await api('/api/today'); renderToday(td);
    const sg = await api('/api/signals'); renderSignals(sg);
    const nf = await api('/api/notifications?after='+lastNid); renderNotifs(nf);
    const er = await api('/api/errors'); renderErrors(er);
    document.querySelector('.sbar').style.opacity = 1;
  }catch(e){
    console.error(e);
    document.querySelector('.sbar').innerHTML =
      '⚠️ <span style="color:var(--orange)">تعذر جلب البيانات: '+esc(e.message)+' — إعادة محاولة كل 5 ثوانٍ</span>';
  }
}
loadAll();
if(!timer) timer = setInterval(loadAll, 5000);
</script>
</body>
</html>"""


# ═══════════════════════ Backend ═══════════════════════
def _fmt_t(ts, fmt='%m-%d %H:%M:%S'):
    try:
        return time.strftime(fmt, time.localtime(ts))
    except Exception:
        return '—'


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
                    (time.time(), kind, str(title)[:200], str(body)[:1500], level))
                await db.commit()
        except Exception:
            pass

    async def get_after(self, after_id, limit=60):
        try:
            async with aiosqlite.connect(self.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                        "SELECT id, ts, kind, title, body FROM notifications WHERE id > ? ORDER BY id DESC LIMIT ?",
                        (after_id, limit)) as cur:
                    rows = await cur.fetchall()
                async with db.execute("SELECT COUNT(*) c FROM notifications") as cur:
                    total = (await cur.fetchone())[0]
                return {
                    'items': [{
                        'id': r['id'], 'kind': r['kind'], 'title': r['title'], 'body': r['body'],
                        'time': _fmt_t(r['ts']),
                    } for r in reversed(rows)],
                    'last_id': max((r['id'] for r in rows), default=after_id),
                    'total_unread': total,
                }
        except Exception:
            return {'items': [], 'last_id': after_id, 'total_unread': 0}


PANEL_DB = None


async def notify(kind, title, body='', level='info'):
    if PANEL_DB:
        await PANEL_DB.add(kind, title, body, level)


def _trade_row(r):
    """صف موحّد لصفقة مغلقة من trade_history"""
    return {
        'id': r['id'], 'symbol': r['symbol'], 'side': r['side'],
        'trigger': r['trigger'], 'score': r['score'],
        'entry_price': r['entry_price'], 'exit_price': r['exit_price'],
        'qty_initial': r['qty_initial'], 'qty_final': r['qty_final'],
        'realized_partial': r['realized_partial'] or 0,
        'total_pnl': r['total_pnl'], 'pnl_pct': r['pnl_pct'],
        'sl': r['sl'], 'tp1': r['tp1'], 'tp2': r['tp2'],
        'highest': r['highest'], 'lowest': r['lowest'],
        'reason': r['reason'],
        'entry_str': _fmt_t(r['entry_ts']), 'exit_str': _fmt_t(r['exit_ts']),
        'date_str': _fmt_t(r['exit_ts'], '%Y-%m-%d'),
        'duration_sec': r['duration_sec'],
    }


async def _close_all_impl(bot):
    closed = []
    for symbol, t in list(bot.active_trades.items()):
        prices = bot.get_price(symbol)
        px = (prices['bid'] if t['side'] == 'BUY' else prices['ask']) if prices else t['entry_price']
        ok, fill, pnl_over = await bot._close_position(t, px)
        if ok:
            await bot._finalize_trade(t, fill, '🚨 إغلاق من اللوحة', pnl_over)
            closed.append(symbol)
    return closed


def create_app(bot):
    def j(data, status=200):
        return web.json_response(data, status=status,
                                 headers={'Cache-Control': 'no-store'})

    async def index(request):
        return web.Response(text=PAGE, content_type='text/html',
                            headers={'Cache-Control': 'no-store, must-revalidate'})

    async def overview(request):
        today = time.strftime('%Y-%m-%d')
        row = await bot.db.get_day_stats(today)
        newest = max((p.get('ts', 0) for p in bot.live_prices.values()), default=0)
        balance = bot._balance_cache[0] if bot._balance_cache[1] > 0 else 0.0
        try:
            fees = await bot.get_today_fees()
        except Exception:
            fees = 0.0
        pnl_today = round(row[0], 4) if row else 0.0
        tuner = bot.tuner
        wr = tuner.recent_winrate(10)
        lsi = dict(bot.last_scan_info) if getattr(bot, 'last_scan_info', None) else None
        if lsi and lsi.get('ts'):
            lsi['age'] = int(time.time() - lsi['ts'])
        return j({
            'ok': True, 'server_now': time.time(),
            'trade_enabled': bot.TRADE_ENABLED, 'testnet': bot.TESTNET,
            'leverage': bot.LEVERAGE, 'trade_size': bot.TRADE_SIZE_USDT,
            'max_open': bot.MAX_OPEN_TRADES, 'pairs': len(bot.all_futures_pairs),
            'tp1_floor': getattr(bot, 'TP1_FLOOR_PCT', 0.018),
            'min_qvol': getattr(bot, 'MIN_QUOTE_VOLUME', 15000000),
            'max_spread': getattr(bot, 'MAX_SPREAD_PCT', 0.15),
            'balance': round(balance, 2),
            'today': {'pnl': pnl_today,
                      'wins': row[1] if row else 0, 'losses': row[2] if row else 0},
            'fees_today': round(fees, 4),
            'net_today': round(pnl_today - fees, 4),
            'stats': dict(bot.stats), 'open_trades': len(bot.active_trades),
            'scans': bot.stats.get('total_scans', 0),
            'uptime': int((time.time() - PANEL_START) / 60),
            'price_age': int(time.time() - newest) if newest else 999999,
            'last_loop_ts': getattr(bot, '_last_loop_ts', None) or None,
            'last_loop_age': (int(time.time() - bot._last_loop_ts)
                              if getattr(bot, '_last_loop_ts', 0) else None),
            'last_scan': lsi,
            'tuner': {'min_score': tuner.min_score,
                      'proximity_pct': tuner.proximity_pct,
                      'strict_stoch': tuner.strict_stoch,
                      'winrate': (str(int(wr * 100)) + '%') if wr is not None else None},
        })

    async def refresh_balance(request):
        try:
            balance = await bot.get_available_usdt()
        except Exception:
            balance = 0.0
        return j({'ok': True, 'balance': round(balance, 2)})

    async def positions(request):
        out = []
        for symbol, t in list(bot.active_trades.items()):
            prices = bot.get_price(symbol)
            cur = pnl = None
            if prices:
                cur = prices['bid'] if t['side'] == 'BUY' else prices['ask']
                diff = (cur - t['entry_price']) if t['side'] == 'BUY' else (t['entry_price'] - cur)
                pnl = diff * t['quantity'] + t.get('realized_pnl', 0.0)
            entry = t['entry_price']
            margin = bot.TRADE_SIZE_USDT
            out.append({
                'symbol': symbol, 'side': t['side'],
                'entry': round(entry, 8),
                'current': round(cur, 8) if cur else None,
                'qty': t['quantity'], 'qty_initial': t.get('initial_quantity') or t['quantity'],
                'margin': margin, 'notional': round(margin * bot.LEVERAGE, 2),
                'pnl': round(pnl, 4) if pnl is not None else None,
                'pnl_pct': round(pnl / margin * 100, 2) if pnl is not None else None,
                'sl': round(t['sl'], 8),
                'tp1': round(t.get('tp'), 8) if t.get('tp') else None,
                'tp2': round(t.get('tp2'), 8) if t.get('tp2') else None,
                'dist_sl_pct': round(abs(entry - t['sl']) / entry * 100, 3) if entry else None,
                'dist_tp1_pct': round(abs((t.get('tp') or entry) - entry) / entry * 100, 3) if entry else None,
                'partial': bool(t.get('partial_closed', False)),
                'trailing': bool(t.get('trailing_active', False)),
                'realized': round(t.get('realized_pnl', 0.0), 4),
                'highest': t.get('highest_price'), 'lowest': t.get('lowest_price'),
                'entry_ts': t.get('entry_time'),
                'entry_str': _fmt_t(t.get('entry_time')),
                'age_str': dur_str(time.time() - t.get('entry_time', time.time())),
                'stop_ok': bool(t.get('stop_order_id') or t.get('stop_synced_price')
                                or t.get('stop_is_algo') or t.get('stop_skipped')),
                'trigger': t.get('trigger', '—'),
                'score': t.get('score'),
            })
        return j(out)

    async def closed(request):
        out = []
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                        "SELECT * FROM trade_history ORDER BY id DESC LIMIT 200") as cur:
                    rows = await cur.fetchall()
                out = [_trade_row(r) for r in rows]
        except Exception:
            pass
        return j(out)

    async def history(request):
        try:
            limit = min(int(request.query.get('limit', '100')), 300)
            offset = max(int(request.query.get('offset', '0')), 0)
        except ValueError:
            limit, offset = 100, 0
        date = request.query.get('date', '')
        rows, total = [], 0
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                db.row_factory = aiosqlite.Row
                if date:
                    async with db.execute(
                            "SELECT COUNT(*) c FROM trade_history "
                            "WHERE date(exit_ts, 'unixepoch', 'localtime')=?", (date,)) as cur:
                        total = (await cur.fetchone())['c']
                    async with db.execute(
                            "SELECT * FROM trade_history WHERE date(exit_ts, 'unixepoch', 'localtime')=? "
                            "ORDER BY id DESC LIMIT ? OFFSET ?", (date, limit, offset)) as cur:
                        rows = await cur.fetchall()
                else:
                    async with db.execute("SELECT COUNT(*) c FROM trade_history") as cur:
                        total = (await cur.fetchone())['c']
                    async with db.execute(
                            "SELECT * FROM trade_history ORDER BY id DESC LIMIT ? OFFSET ?",
                            (limit, offset)) as cur:
                        rows = await cur.fetchall()
        except Exception:
            pass
        return j({'total': total, 'rows': [_trade_row(r) for r in rows]})

    async def history_days(request):
        days, agg = [], {'active_days': 0, 'total_pnl': 0, 'total_closed': 0,
                         'total_wins': 0, 'overall_winrate': None,
                         'best_day': None, 'worst_day': None}
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                        "SELECT date, realized_pnl, wins, losses FROM daily_stats "
                        "ORDER BY date DESC") as cur:
                    rows = await cur.fetchall()
                for r in rows:
                    w, l = r['wins'] or 0, r['losses'] or 0
                    total = w + l
                    days.append({'date': r['date'], 'pnl': round(r['realized_pnl'] or 0, 4),
                                 'wins': w, 'losses': l, 'total': total,
                                 'winrate': round(w / total * 100, 1) if total else None})
                async with db.execute(
                        "SELECT COUNT(*) c, COALESCE(SUM(realized_pnl),0) p FROM daily_stats "
                        "WHERE wins + losses > 0") as cur:
                    a = await cur.fetchone()
                    agg['active_days'], agg['total_pnl'] = a['c'], round(a['p'], 4)
                async with db.execute(
                        "SELECT date, realized_pnl FROM daily_stats WHERE wins + losses > 0 "
                        "ORDER BY realized_pnl DESC LIMIT 1") as cur:
                    best = await cur.fetchone()
                async with db.execute(
                        "SELECT date, realized_pnl FROM daily_stats WHERE wins + losses > 0 "
                        "ORDER BY realized_pnl ASC LIMIT 1") as cur:
                    worst = await cur.fetchone()
                if best:
                    agg['best_day'] = {'date': best['date'], 'pnl': round(best['realized_pnl'], 4)}
                if worst:
                    agg['worst_day'] = {'date': worst['date'], 'pnl': round(worst['realized_pnl'], 4)}
                async with db.execute(
                        "SELECT COUNT(*) c FROM trade_history") as cur:
                    agg['total_closed'] = (await cur.fetchone())[0]
                async with db.execute(
                        "SELECT COUNT(*) c FROM trade_history WHERE total_pnl > 0") as cur:
                    agg['total_wins'] = (await cur.fetchone())[0]
                if agg['total_closed']:
                    agg['overall_winrate'] = round(agg['total_wins'] / agg['total_closed'] * 100, 1)
        except Exception:
            pass
        return j({'days': days, 'agg': agg})

    async def signals(request):
        out = []
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                        "SELECT symbol, direction, entry_ts, score, components, result, pnl "
                        "FROM signal_log ORDER BY id DESC LIMIT 100") as cur:
                    rows = await cur.fetchall()
                for r in rows:
                    comp = {}
                    try:
                        comp = json.loads(r['components'] or '{}')
                    except Exception:
                        pass
                    out.append({
                        'symbol': r['symbol'], 'direction': r['direction'],
                        'time': _fmt_t(r['entry_ts']),
                        'score': int(r['score'] or 0),
                        'trigger': comp.get('trigger', '—'),
                        'result': r['result'],
                        'pnl': round(r['pnl'], 4) if r['pnl'] is not None else None,
                    })
        except Exception:
            pass
        return j(out)

    async def rejections(request):
        items, counts = [], {}
        now = time.time()
        for e in list(getattr(bot, 'rejection_buffer', [])):
            if now - e['ts'] <= 86400:
                counts[e['stage']] = counts.get(e['stage'], 0) + 1
        items = list(getattr(bot, 'rejection_buffer', []))[-300:]
        lsi = dict(bot.last_scan_info) if getattr(bot, 'last_scan_info', None) else None
        return j({
            'counts': counts,
            'items': [{'time': _fmt_t(e['ts']), 'symbol': e['symbol'],
                       'stage': e['stage'], 'detail': e['detail'],
                       'trend': e.get('trend', '')} for e in reversed(items)],
            'last_scan': lsi,
        })

    async def today(request):
        today = time.strftime('%Y-%m-%d')
        realized, wins, losses = 0.0, 0, 0
        trades = []
        try:
            fees = await bot.get_today_fees()
        except Exception:
            fees = 0.0
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                        "SELECT realized_pnl, wins, losses FROM daily_stats WHERE date=?",
                        (today,)) as cur:
                    row = await cur.fetchone()
                if row:
                    realized, wins, losses = row['realized_pnl'] or 0, row['wins'] or 0, row['losses'] or 0
                async with db.execute(
                        "SELECT * FROM trade_history WHERE date(exit_ts, 'unixepoch', 'localtime')=? "
                        "ORDER BY id DESC LIMIT 100", (today,)) as cur:
                    trades = [_trade_row(r) for r in await cur.fetchall()]
        except Exception:
            pass
        return j({
            'date': today, 'realized': round(realized, 4), 'fees': round(fees, 4),
            'net': round(realized - fees, 4), 'wins': wins, 'losses': losses,
            'total': wins + losses,
            'winrate': round(wins / (wins + losses) * 100, 1) if (wins + losses) else None,
            'fees_zero': fees < 1e-9,
            'trades': trades,
        })

    async def notifications(request):
        after = int(request.query.get('after', 0))
        if PANEL_DB:
            return j(await PANEL_DB.get_after(after))
        return j({'items': [], 'last_id': after, 'total_unread': 0})

    async def tuner_history(request):
        return j(list(bot.tuner.results))

    async def errors(request):
        return j({'errors': dict(bot.error_counts)})

    async def storage(request):
        db_path = getattr(bot.db, 'db_name', '')
        log_path = os.path.join(DATA_DIR, 'bot_v8.log')
        db_exists = os.path.exists(db_path) if db_path else False
        log_exists = os.path.exists(log_path)
        return j({
            'data_dir': DATA_DIR,
            'db_exists': db_exists,
            'db_size_kb': round(os.path.getsize(db_path) / 1024, 1) if db_exists else 0,
            'log_exists': log_exists,
            'log_size_kb': round(os.path.getsize(log_path) / 1024, 1) if log_exists else 0,
            'volume': bool(os.environ.get('RAILWAY_VOLUME_MOUNT_PATH')),
        })

    async def pause(request):
        bot.TRADE_ENABLED = False
        return j({'ok': True})

    async def resume(request):
        if not bot.binance_api_key:
            return j({'ok': False, 'error': 'مفاتيح API ناقصة'}, status=400)
        bot.TRADE_ENABLED = True
        return j({'ok': True})

    async def close_all(request):
        closed = await _close_all_impl(bot)
        return j({'ok': True, 'closed': closed})

    async def emergency(request):
        bot.TRADE_ENABLED = False
        closed = await _close_all_impl(bot)
        return j({'ok': True, 'closed': closed})

    async def shutdown(request):
        await bot.request_shutdown()
        return j({'ok': True})

    async def wipe(request):
        force = request.query.get('force') == '1'
        if bot.active_trades and not force:
            return j({'ok': False, 'error': 'توجد صفقات مفتوحة — استخدم force=1 أو أغلقها أولاً'},
                     status=400)
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                for tbl in ('signal_log', 'trade_history', 'daily_stats', 'notifications'):
                    await db.execute(f"DELETE FROM {tbl}")
                if force:
                    await db.execute("DELETE FROM active_trades")
                await db.commit()
            return j({'ok': True})
        except Exception as e:
            return j({'ok': False, 'error': str(e)}, status=500)

    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/api/overview', overview)
    app.router.add_get('/api/balance', refresh_balance)
    app.router.add_get('/api/positions', positions)
    app.router.add_get('/api/closed', closed)
    app.router.add_get('/api/history', history)
    app.router.add_get('/api/history/days', history_days)
    app.router.add_get('/api/signals', signals)
    app.router.add_get('/api/rejections', rejections)
    app.router.add_get('/api/today', today)
    app.router.add_get('/api/notifications', notifications)
    app.router.add_get('/api/tuner-history', tuner_history)
    app.router.add_get('/api/errors', errors)
    app.router.add_get('/api/storage', storage)
    app.router.add_post('/api/pause', pause)
    app.router.add_post('/api/resume', resume)
    app.router.add_post('/api/close-all', close_all)
    app.router.add_post('/api/emergency', emergency)
    app.router.add_post('/api/shutdown', shutdown)
    app.router.add_post('/api/wipe', wipe)
    return app


def dur_str(sec):
    try:
        sec = int(sec)
    except Exception:
        return '—'
    if sec < 60:
        return f'{sec} ث'
    h, m = sec // 3600, (sec % 3600) // 60
    return f'{h}س {m}د' if h else f'{m}د'


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
        print(f'🖥️ لوحة القناص V10 تعمل على المنفذ {port} — دخول مباشر')
        return True
    except Exception as e:
        print(f'⚠️ فشل اللوحة (البوت يكمل عمله): {e}')
        return False
