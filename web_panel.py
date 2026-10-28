<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🎯 القناص الأسطوري V12.4 — HMA_DMI_MOMENTUM</title>
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
.btn-s{background:rgba(255,255,255,.08);color:var(--sub);border:1px solid var(--bord)}
.btn-o{background:rgba(249,115,22,.15);color:var(--orange);border:1px solid rgba(249,115,22,.4)}
main{position:relative;z-index:1;max-width:1400px;margin:0 auto;padding:16px}
.sbar{background:var(--bg2);border:1px solid var(--bord);border-radius:12px;padding:10px 16px;
margin-bottom:16px;display:flex;align-items:center;gap:10px;font-size:13px;color:var(--sub);flex-wrap:wrap}
.sbar b{color:var(--green)}
.tabs{display:flex;gap:5px;margin-bottom:18px;border-bottom:1px solid var(--bord);overflow-x:auto;padding-bottom:2px}
.tab{padding:12px 18px;border:none;background:transparent;color:var(--sub);cursor:pointer;font-weight:600;
font-size:14px;border-radius:10px 10px 0 0;transition:.2s;white-space:nowrap;position:relative}
.tab.act{color:var(--green);background:rgba(0,212,170,.1)}
.tab.act::after{content:'';position:absolute;bottom:-2px;right:0;left:0;height:2px;background:var(--green)}
.tc{display:none}
.tc.act{display:block;animation:fi .3s}
@keyframes fi{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:14px;margin-bottom:20px}
.grid.two{grid-template-columns:2fr 1fr}
.grid.cols2{grid-template-columns:1fr 1fr}
.card{background:var(--card);border:1px solid var(--bord);border-radius:16px;padding:20px;position:relative;overflow:hidden;transition:.3s}
.card:hover{border-color:rgba(0,212,170,.3)}
.card::before{content:'';position:absolute;top:0;right:0;width:100px;height:100px;border-radius:50%;filter:blur(50px);opacity:.12}
.card.g::before{background:var(--green)}.card.b::before{background:var(--blue)}.card.p::before{background:var(--purple)}
.card.o::before{background:var(--orange)}.card.y::before{background:var(--yellow)}.card.r::before{background:var(--red)}
.card .l{font-size:13px;color:var(--sub)}
.card .v{font-size:30px;font-weight:800;margin:8px 0 4px}
.card .s{font-size:11px;color:var(--sub);padding-top:8px;border-top:1px solid var(--bord);margin-top:8px;line-height:1.7}
.card.g .v{color:var(--green)}.card.b .v{color:var(--blue)}.card.p .v{color:var(--purple)}
.card.o .v{color:var(--orange)}.card.y .v{color:var(--yellow)}.card.r .v{color:var(--red)}
.pos{color:var(--green)!important}.neg{color:var(--red)!important}
.sec{background:var(--card);border:1px solid var(--bord);border-radius:16px;padding:20px;margin-bottom:20px}
.sec h3{margin-bottom:14px;font-size:16px}
table{width:100%;border-collapse:collapse}
th{text-align:right;padding:9px;color:var(--sub);font-size:11px;border-bottom:1px solid var(--bord)}
td{padding:11px 9px;font-size:13px;border-bottom:1px solid rgba(255,255,255,.04)}
tr:hover td{background:rgba(0,212,170,.03)}
.tag{padding:3px 9px;border-radius:6px;font-size:11px;font-weight:700;display:inline-block}
.tag.buy{background:rgba(0,212,170,.15);color:var(--green)}
.tag.sell{background:rgba(239,68,68,.15);color:var(--red)}
.tag.win{background:rgba(16,185,129,.15);color:#10b981}
.tag.loss{background:rgba(239,68,68,.15);color:var(--red)}
.tag.open{background:rgba(245,158,11,.15);color:#f59e0b}
.tag.info{background:rgba(59,130,246,.15);color:var(--blue)}
.tag.ok{background:rgba(16,185,129,.15);color:#10b981}
.tag.warn{background:rgba(234,179,8,.15);color:var(--yellow)}
.tag.stop{background:rgba(239,68,68,.15);color:var(--red)}
.tag.local{background:rgba(249,115,22,.15);color:var(--orange)}
.tag.gray{background:rgba(148,163,184,.15);color:var(--sub)}
.empty{text-align:center;color:var(--sub);padding:30px;font-size:14px}
.feed{display:flex;flex-direction:column;gap:9px;max-height:560px;overflow-y:auto;padding-left:4px}
.nt{display:flex;gap:12px;padding:13px;background:var(--bg2);border-radius:12px;border-right:4px solid transparent;animation:fi .3s}
.nt.trade{border-right-color:var(--green)}.nt.signal{border-right-color:var(--blue)}
.nt.close{border-right-color:var(--purple)}.nt.error{border-right-color:var(--red)}
.nt.system{border-right-color:var(--sub)}.nt.info{border-right-color:var(--sub)}
.nt.warn{border-right-color:var(--orange)}.nt.risk{border-right-color:var(--purple)}
.nt.news{border-right-color:var(--yellow)}.nt.cycle{border-right-color:var(--blue)}
.nt-ic{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0}
.nt.trade .nt-ic{background:rgba(0,212,170,.15)}.nt.signal .nt-ic{background:rgba(59,130,246,.15)}
.nt.close .nt-ic{background:rgba(139,92,246,.15)}.nt.error .nt-ic{background:rgba(239,68,68,.15)}
.nt.system .nt-ic{background:rgba(148,163,184,.15)}.nt.info .nt-ic{background:rgba(148,163,184,.15)}
.nt.warn .nt-ic{background:rgba(249,115,22,.15)}.nt.risk .nt-ic{background:rgba(139,92,246,.15)}
.nt.news .nt-ic{background:rgba(234,179,8,.15)}.nt.cycle .nt-ic{background:rgba(59,130,246,.15)}
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
.kv{display:flex;justify-content:space-between;gap:12px;padding:9px 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:14px}
.kv:last-child{border-bottom:none}
.kv b{color:var(--green);text-align:left}
.foot{text-align:center;padding:18px;color:var(--sub);font-size:12px;border-top:1px solid var(--bord);margin-top:18px}
.arow{display:flex;gap:10px;flex-wrap:wrap}
.banner{display:none;background:rgba(239,68,68,.10);border:1px solid rgba(239,68,68,.45);border-radius:12px;padding:14px 16px;margin:0 0 14px;color:#fca5a5;font-size:12.5px;line-height:2.1}
.banner.gold{background:rgba(234,179,8,.08);border-color:rgba(234,179,8,.45);color:#fde68a}
.banner.green{background:rgba(0,212,170,.08);border-color:rgba(0,212,170,.45);color:#99f6e4}
.banner input{background:var(--bg);color:var(--txt);border:1px solid var(--bord);border-radius:8px;padding:6px 10px;direction:ltr;width:min(280px,60vw);font-family:monospace}
.wr{display:flex;flex-direction:column;gap:10px}
.wrrow{display:flex;gap:12px;align-items:center;background:var(--bg2);border-radius:12px;padding:13px;border-right:4px solid var(--orange);flex-wrap:wrap;animation:fi .3s}
.wrrow.sev3{border-right-color:var(--red)}.wrrow.sev2{border-right-color:var(--orange)}.wrrow.sev1{border-right-color:var(--yellow)}
.wrrow .wsym{font-weight:800;font-size:15px;min-width:120px}
.wrrow .wnums{font-size:13px;min-width:160px}
.wrrow .wchips{flex:1;min-width:200px;display:flex;flex-wrap:wrap;gap:6px}
.wrrow .wact{display:flex;gap:6px}
.rowbtn{background:rgba(239,68,68,.15);color:var(--red);border:1px solid rgba(239,68,68,.4);border-radius:8px;padding:5px 12px;font-size:12px;font-weight:700;cursor:pointer}
.rowbtn.retry{background:rgba(234,179,8,.12);color:var(--yellow);border-color:rgba(234,179,8,.4)}
.rowbtn:hover{filter:brightness(1.3)}
.fbar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;align-items:center}
.fbtn{padding:6px 14px;border-radius:50px;background:rgba(255,255,255,.06);color:var(--sub);border:1px solid var(--bord);cursor:pointer;font-size:12px;font-weight:600}
.fbtn.on{background:rgba(0,212,170,.15);color:var(--green);border-color:rgba(0,212,170,.4)}
.fsearch{flex:1;min-width:180px;background:var(--bg2);border:1px solid var(--bord);border-radius:50px;padding:8px 14px;color:var(--txt);font-family:inherit;font-size:12.5px;outline:none}
.fsearch:focus{border-color:rgba(0,212,170,.4)}
.sin{background:var(--bg);color:var(--txt);border:1px solid var(--bord);border-radius:6px;padding:4px 8px;width:120px;font-family:inherit;direction:ltr;text-align:center;font-size:13px}
.sin:focus{border-color:rgba(0,212,170,.4)}
.diagbox{background:var(--bg2);border:1px solid var(--bord);border-radius:10px;padding:10px 12px;margin-bottom:12px;font-size:12.5px;line-height:1.9}
@media(max-width:768px){.card .v{font-size:24px}.tab{padding:10px 12px;font-size:12px}.grid.two,.grid.cols2{grid-template-columns:1fr!important}}
</style>
</head>
<body>
<div class="bg"></div>

<header class="hd"><div class="hd-in">
  <div class="logo">
    <div class="logo-ic">🎯</div>
    <div><h1>القناص الأسطوري V12.4 — HMA_DMI_MOMENTUM</h1><span id="modeTxt">شاشة العمليات — استراتيجية واحدة مستقلة</span></div>
  </div>
  <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
    <div class="badge" id="liveB"><span class="dot"></span><span id="liveT">جارٍ الاتصال…</span></div>
    <button class="act btn-g" onclick="loadAll()">🔄 تحديث</button>
  </div>
</div></header>

<main>
<div class="sbar">⏱️ آخر تحديث: <b id="lastUpd">—</b> • تحديث تلقائي كل 10 ثوانٍ • <span id="connTxt">الاتصال جارٍ…</span></div>

<div class="banner" id="keyBanner">🔒 <b>البوت محمي بمفتاح DASHBOARD_TOKEN</b> — أدخل المفتاح مرة واحدة ليُحفظ في متصفحك:<br>
  <input id="keyInput" type="password" placeholder="DASHBOARD_TOKEN"> <button class="act btn-g" onclick="saveKey()">حفظ المفتاح والاتصال</button></div>

<div class="banner" id="offBanner">⚠️ <b>تعذر الاتصال بالبوت</b> — إعادة محاولة تلقائية كل 10 ثوانٍ. تأكد أن البوت يعمل على Railway وأن الرابط صحيح.</div>

<div class="banner gold hidden" id="urlBox">🧭 <b>نسخة الشاشة المستقلة</b> — اكتب عنوان البوت (نطاق Railway) ثم اضغط اتصال:<br>
  <input id="botUrl" type="text" placeholder="https://xxx.up.railway.app"> <button class="act btn-g" onclick="retryConn()">اتصال</button>
  <button class="act btn-s" onclick="startDemo()">👁️ عرض تجريبي للتصميم</button></div>

<div class="tabs">
  <button class="tab act" onclick="sw('overview',this)">📊 نظرة عامة</button>
  <button class="tab" onclick="sw('worried',this)">⚠️ الصفقات المقلقة <span id="wBdg" class="tag ok" style="padding:1px 7px;font-size:10px">0</span></button>
  <button class="tab" onclick="sw('trades',this)">📂 الصفقات</button>
  <button class="tab" onclick="sw('signals',this)">📡 الإشارات والرفض</button>
  <button class="tab" onclick="sw('notifications',this)">🔔 الإشعارات <span id="nBdg" class="tag info" style="padding:1px 7px;font-size:10px">0</span></button>
  <button class="tab" onclick="sw('performance',this)">📅 الأداء اليومي</button>
  <button class="tab" onclick="sw('strategy',this)">🧭 الاستراتيجية</button>
  <button class="tab" onclick="sw('risk',this)">🛡️ المخاطر</button>
  <button class="tab" onclick="sw('system',this)">⚙️ النظام</button>
</div>

<!-- ═══════════ نظرة عامة ═══════════ -->
<div class="tc act" id="t-overview">
  <div class="grid">
    <div class="card g"><div class="l">💵 الرصيد</div><div class="v" id="cBal">$0</div><div class="s" id="cMode">—</div></div>
    <div class="card b"><div class="l">📈 نتيجة اليوم</div><div class="v" id="cDay">$0</div><div class="s" id="cDayS">—</div></div>
    <div class="card p"><div class="l">🏆 نسبة الفوز</div><div class="v" id="cWr">—</div><div class="s" id="cWrS">—</div></div>
    <div class="card o"><div class="l">📂 مفتوحة الآن</div><div class="v" id="cOpen">0</div><div class="s" id="cOpenS">—</div></div>
    <div class="card y"><div class="l">🔭 الكون السائل</div><div class="v" id="cUni">—</div><div class="s" id="cUniS">—</div></div>
    <div class="card b"><div class="l">🔁 الدورات</div><div class="v" id="cCyc">0</div><div class="s" id="cCycS">—</div></div>
  </div>
  <div class="grid two">
    <div class="sec"><h3>📂 الصفقات المفتوحة</h3><div id="openBox"><div class="empty">بانتظار البيانات…</div></div></div>
    <div class="sec"><h3>🛡️ الحمايات</h3><div class="hg" id="healthBox">—</div></div>
  </div>
  <div class="sec"><h3>🔔 آخر الأحداث</h3><div class="feed" id="miniFeed" style="max-height:300px"></div></div>
</div>

<!-- ═══════════ الصفقات المقلقة ═══════════ -->
<div class="tc" id="t-worried">
  <div class="sec">
    <h3>⚠️ الصفقات المقلقة — مراقبة تلقائية لحظية</h3>
    <p style="color:var(--sub);font-size:12.5px;line-height:2;margin-bottom:14px">
    كيف تُصنَّف الصفقة كمقلقة؟ (1) 🛡️ ستوب المنصة غير مؤكد بعد — (2) 📉 خسارة عائمة تجاوزت 35% من الهامش — (3) ⏳ عمر الصفقة اقترب من الستوب الزمني (<b id="legTs">24</b> ساعة).<br>
    التصنيف استرشادي للتنبيه فقط — <b style="color:var(--txt)">لا يغلق أي صفقة بنفسه</b>، والقرار دائماً لك عبر أزرار الإغلاق أو 🔁 لإعادة تثبيت الستوب.</p>
    <div class="wr" id="worriedBox"><div class="empty">بانتظار البيانات…</div></div>
  </div>
</div>

<!-- ═══════════ الصفقات ═══════════ -->
<div class="tc" id="t-trades">
  <div class="sec"><h3>📂 المفتوحة الآن — TP1 = إغلاق كامل عند اللمس</h3><div id="openBox2"><div class="empty">بانتظار البيانات…</div></div></div>
  <div class="sec"><h3>🏁 المغلقة (من قاعدة البيانات)</h3><div id="closedBox"><div class="empty">بانتظار أول مزامنة…</div></div></div>
</div>

<!-- ═══════════ الإشارات والرفض ═══════════ -->
<div class="tc" id="t-signals">
  <div class="grid">
    <div class="card b"><div class="l">📡 إشارات مكتشفة</div><div class="v" id="sgTotal">0</div><div class="s">إجمالي ما كشفته الاستراتيجية</div></div>
    <div class="card g"><div class="l">✅ صفقات منفذة</div><div class="v" id="sgExec">0</div><div class="s" id="sgExecS">—</div></div>
    <div class="card o"><div class="l">🚫 مرفوضة (جودة)</div><div class="v" id="sgRejQ">0</div><div class="s" id="sgRejS">فشل شرط من شروط القبول</div></div>
    <div class="card r"><div class="l">⏳ صُدّت بصفقة مفتوحة</div><div class="v" id="sgRejO">0</div><div class="s">بلا طابور — تُستهلك ويُعاد التحليل بعد الإغلاق</div></div>
  </div>
  <div class="sec"><h3>📡 سجل الإشارات</h3><div id="sigBox"><div class="empty">بانتظار أول مزامنة…</div></div></div>
  <div class="sec"><h3>🚫 أسباب الرفض — من قاعدة البيانات (العدّادات لآخر 24 ساعة)</h3><div id="rejBox"><div class="empty">بانتظار أول مزامنة…</div></div></div>
</div>

<!-- ═══════════ الإشعارات ═══════════ -->
<div class="tc" id="t-notifications">
  <div class="sec"><h3>🔔 كل ما يقوم به البوت — كل صغيرة وكبيرة مع السبب</h3>
    <div class="fbar" id="kindBar"></div>
    <input class="fsearch" id="q" type="text" placeholder="🔎 ابحث في السجل (رمز، سبب، كلمة)…">
    <div style="height:12px"></div>
    <div class="feed" id="notifFeed"><div class="empty">بانتظار البيانات…</div></div>
  </div>
</div>

<!-- ═══════════ الأداء اليومي ═══════════ -->
<div class="tc" id="t-performance">
  <div class="sec"><h3>📅 اليوم الحالي</h3><div id="todayBox">—</div></div>
  <div class="sec"><h3>🗓️ آخر 14 يوماً</h3><div id="daysBox">—</div></div>
  <div class="sec"><h3>🏆 الإجماليات عبر التاريخ</h3><div id="aggBox">—</div></div>
</div>

<!-- ═══════════ الاستراتيجية ═══════════ -->
<div class="tc" id="t-strategy">
  <div class="grid cols2">
    <div class="sec"><h3>🧭 حالة HMA_DMI_MOMENTUM الآن</h3>
      <div id="hStatus">—</div>
    </div>
    <div class="sec"><h3>📡 الدفعة الأخيرة</h3>
      <div id="hBatch">—</div>
    </div>
  </div>
  <div class="sec"><h3>🧭 أداء HMA_DMI_MOMENTUM عبر التاريخ — محسوب من قاعدة البيانات فعلياً</h3>
    <div id="perfBox">—</div>
    <p style="color:var(--sub);font-size:11px;margin-top:10px;line-height:1.8">
    📐 تعريفات الحساب (موثقة — بلا أرقام مضللة): نسبة الفوز = الرابحة ÷ (الرابحة + الخاسرة) من الصفقات المغلقة ذات النتيجة المؤكدة — المحايدة مستثناة من المقام عمداً.
    صافي النتيجة = مجموع نتائج الصفقات المغلقة المسجلة (Binance مؤكد ✓ أو تقديري موسوم ⚠️).
    متوسط الربح/الخسارة من الصفقات الرابحة/الخاسرة فقط.
    Profit Factor = مجموع أرباح الرابحين ÷ القيمة المطلقة لمجموع خسائر الخاسرين — يظهر «—» عند غياب الخسائر أو البيانات.
    أقصى تراجع = أقصى هبوط لمنحنى الأرباح المتراكم (الترتيب الزمني للمغلقات) عن قمته — يحتاج صفقتين مغلقتين فأكثر وإلا «—».</p>
  </div>
  <div class="sec"><h3>🔭 الكون السائل — تشخيص كامل (سؤالك: لماذا يظهر أقل من 200؟)</h3>
    <div id="uniDiag">—</div>
    <p style="color:var(--sub);font-size:11.5px;line-height:1.9;margin-top:10px">
    📌 العدد المعروض هو «المرشح الفعلي»: الأزواج التي تجاوزت حد السيولة 24 ساعة فعلاً (بسقف HMA_UNIVERSE_POOL). متغيرا POOL=300 وSIZE=200 يعملان الآن بشكل مؤكد — لكنهما لا يستطيعان اختراع سيولة غير موجودة:
    في فترات هدوء السوق يقل عدد الأزواج فوق حد 30م$ فيصغر الكون طبيعياً ثم يعود ليكبر. إن أردت تثبيت العدد أعلى: خفّض HMA_SCAN_MIN_VOL_USDT في Railway (مثلاً 20000000 = 20م$).</p>
  </div>
  <div class="sec"><h3>🧭 إعدادات HMA_DMI_MOMENTUM (تُعدّل لحظياً وتُحفظ في القاعدة)</h3>
    <div id="hmaDesc" style="margin-bottom:12px;color:var(--sub);font-size:12.5px;line-height:1.8">—</div>
    <div id="hmaConf"></div>
    <div id="hmaFields" style="display:grid;grid-template-columns:1fr 1fr;gap:0 26px"></div>
    <div class="arow" style="margin-top:14px">
      <button class="act btn-g" onclick="hmaSave()">💾 حفظ إعدادات HMA</button>
    </div>
    <p style="color:var(--sub);font-size:11px;margin-top:10px;line-height:1.9">
    🧭 سلسلة القبول: آلة حالات NEUTRAL/BULL/BEAR على شموع مغلقة (تبدّل يتطلب 3 شموع مؤكدة + تبريد 3 شموع + انقلاب مباشر ≥ 0.6×ATR) ← بوابة اتجاهية ADX-14 ≥ 20 ← تأكيد زخم ≥ 2 من 3 ← زناد HMA ← قوة ≥ 24/100 وثقة ≥ 5/9 ← بوابة اتجاه 4 ساعات (EMA50 + الميل) ← إعادة تحقق لحظي عند التنفيذ.<br>
    ⚠️ الشموع مغلقة فقط — لا إعادة رسم ولا بيانات مستقبلية. 🌙 الدخول الجديد معطل 16:00–23:59 UTC (المخارج والإدارة تعمل طوال اليوم).<br>
    📌 أولوية المصادر: القاعدة هي المرجع بعد أول تشغيل — تعديل اللوحة يتقدم ويُحفظ، وتعارض متغيرات Railway يظهر أعلى الجدول مع بقائه عرضاً فقط.</p>
  </div>
</div>

<!-- ═══════════ المخاطر ═══════════ -->
<div class="tc" id="t-risk">
  <div class="grid">
    <div class="card g"><div class="l">🛡️ حالة التداول</div><div class="v" id="rStatus">—</div><div class="s" id="rReason">—</div></div>
    <div class="card o"><div class="l">❌ خسائر متتالية</div><div class="v" id="rCons">0</div><div class="s">الحد: 3 — يوقف التداول 4 ساعات</div></div>
    <div class="card r"><div class="l">📊 خسائر اليوم</div><div class="v" id="rDay">0</div><div class="s">الحد: 3 — يوقف بقية اليوم</div></div>
    <div class="card b"><div class="l">💰 نتيجة اليوم</div><div class="v" id="rPnl">$0</div><div class="s" id="rPnlS">حد السحب اليومي: 5% من الرصيد المرجعي</div></div>
  </div>
  <div class="sec"><h3>🛡️ كيف يعمل مدير المخاطر</h3>
    <div class="kv"><span>3 خسائر متتالية</span><b>إيقاف التداول 4 ساعات</b></div>
    <div class="kv"><span>3 خسائر في اليوم</span><b>إيقاف بقية اليوم</b></div>
    <div class="kv"><span>سحب يومي 5% من الرصيد المرجعي</span><b>إيقاف بقية اليوم</b></div>
    <div class="kv"><span>حفظ الحالة</span><b>في القاعدة — إعادة تشغيل البوت لا تصفّر العدّادات</b></div>
    <div class="kv"><span>الإشارة المرفوضة بالمخاطر</span><b>تُسجَّل سببها بوضوح في 🔔 الإشعارات</b></div>
  </div>
</div>

<!-- ═══════════ النظام ═══════════ -->
<div class="tc" id="t-system">
  <div class="grid cols2">
    <div class="sec"><h3>⚙️ الإعدادات الحية</h3><div id="setBox">—</div></div>
    <div>
      <div class="sec"><h3>🚨 الأخطاء</h3><div id="errBox">—</div></div>
      <div class="sec"><h3>📰 فلتر الأخبار — تحكم مباشر</h3>
        <div id="newsBox">—</div>
        <div class="arow" style="margin-top:12px">
          <button class="act btn-s" onclick="cmd('news_toggle')">📰 تفعيل / تعطيل</button>
          <button class="act btn-s" onclick="cmd('news_refresh')">🔄 تحديث التقويم</button>
        </div>
      </div>
    </div>
  </div>
  <div class="sec"><h3>⚡ طوارئ وتحكم</h3>
    <div class="arow">
      <button class="act btn-o" id="pauseBtn" onclick="togglePause()">⏸️ إيقاف مؤقت</button>
      <button class="act btn-r" onclick="closeAllCmd()">🛑 إغلاق الكل</button>
      <button class="act btn-g" onclick="cmd('scan_now')">🔍 مسح فوري الآن</button>
    </div>
    <div class="arow" style="margin-top:10px">
      <button class="act" style="width:100%;background:rgba(234,179,8,.12);color:var(--yellow);border:1px solid rgba(234,179,8,.4)" onclick="resetAll()">🧹 إعادة ضبط شامل — مسح كل البيانات والسجلات (الصفقات المفتوحة لا تُمس)</button>
    </div>
    <p style="color:var(--sub);font-size:11px;margin-top:10px;line-height:1.8">
    ⏸️ الإيقاف يمنع فتح صفقات جديدة فقط — إدارة الصفقات المفتوحة والمخارج تستمر طبيعياً.<br>
    🛡️ حالة كل ستوب تُعرض في تبويب الصفقات — زر 🔁 يعيد محاولة التثبيت على المنصة فوراً.<br>
    🔒 الحماية بمفتاح DASHBOARD_TOKEN — لا تشارك رابط اللوحة ولا المفتاح مع أي أحد.</p>
  </div>
</div>

<div class="foot">🎯 القناص الأسطوري V12.4 — HMA_DMI_MOMENTUM فقط | كل الأوقات بتوقيت ليبيا (UTC+2) بنظام صباحاً/مساءً | ستوب حقيقي على المنصة + مراقبة محلية | مدير مخاطر محفوظ في القاعدة | اللوحة المدمجة داخل ملف البوت — تُخدَم من منفذ النشر مباشرة</div>
</main>
<script>
var PANEL_STANDALONE=true;
/* ═══════════ أدوات عامة ═══════════ */
var lastState=null, lastEvents=[], timer=null, curKind='الكل', q='', KEY='';
function $(id){ return document.getElementById(id); }
function esc(s){ return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function mo(v){ if(v===undefined||v===null||isNaN(v)) return '—'; return (v>=0?'+':'−') + '$' + Math.abs(v).toFixed(2); }
function sg(v,d){ d=(d===undefined)?1:d; if(v===undefined||v===null||isNaN(v)) return '—'; return (v>=0?'+':'−') + Math.abs(v).toFixed(d); }
function fm(v,d){ if(v===undefined||v===null||isNaN(v)) return '—'; return Number(v).toLocaleString('en-US',{maximumFractionDigits:(d===undefined?2:d)}); }
function cls(v){ return (v>0)?'pos':((v<0)?'neg':''); }
function libyaT(ts){
  try{ return new Intl.DateTimeFormat('ar-LY',{timeZone:'Africa/Tripoli',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false}).format(new Date(ts*1000)); }
  catch(e){ try{ return new Date(ts*1000).toISOString().substr(5,14); }catch(e2){ return '—'; } }
}

/* ═══════════ المفتاح والاتصال ═══════════ */
function readKey(){
  try{ var u=new URL(window.location.href); var k=u.searchParams.get('key'); if(k){ KEY=k; try{ localStorage.setItem('dashKey',k); }catch(e){} return; } }catch(e){}
  try{ KEY=localStorage.getItem('dashKey')||''; }catch(e){ KEY=''; }
}
function saveKey(){
  var k=($('keyInput').value||'').trim();
  if(!k){ alert('اكتب المفتاح أولاً'); return; }
  KEY=k; try{ localStorage.setItem('dashKey',k); }catch(e){}
  $('keyBanner').style.display='none';
  loadAll();
}
var BOT_URL='';
function defUrl(){ return PANEL_STANDALONE? 'http://localhost:8999' : (window.location.origin||''); }
function loadUrl(){ try{ BOT_URL=(localStorage.getItem('botUrl')||defUrl()).replace(/\/+$/,''); }catch(e){ BOT_URL=defUrl(); } var b=$('botUrl'); if(b&&!b.value) b.value=BOT_URL; }
function retryConn(){
  BOT_URL=($('botUrl').value.trim()||defUrl()).replace(/\/+$/,'');
  try{ localStorage.setItem('botUrl',BOT_URL); }catch(e){}
  loadAll();
}
async function api(path){
  var c=new AbortController(); var t=setTimeout(function(){ c.abort(); },6000);
  try{
    var res=await fetch(BOT_URL+path,{signal:c.signal,cache:'no-store'});
    if(res.status===401){ $('keyBanner').style.display='block'; throw new Error('locked'); }
    if(!res.ok) throw new Error('HTTP '+res.status);
    return await res.json();
  } finally { clearTimeout(t); }
}

/* ═══════════ التبويبات ═══════════ */
function sw(name, el){
  var ps=document.querySelectorAll('.tc'); for(var i=0;i<ps.length;i++) ps[i].classList.remove('act');
  var bs=document.querySelectorAll('.tab'); for(var j=0;j<bs.length;j++) bs[j].classList.remove('act');
  $('t-'+name).classList.add('act');
  if(el) el.classList.add('act');
  try{ localStorage.setItem('dashTab',name); }catch(e){}
}

/* ═══════════ أنواع الأحداث ═══════════ */
var KIND={'دخول':['trade','🟢'],'خروج':['close','🏁'],'إشارة':['signal','🎯'],'رفض':['warn','🚫'],
'خطأ':['error','🚨'],'دورة':['cycle','🔄'],'نبض':['info','💓'],'مخاطر':['risk','🛡️'],
'أخبار':['news','📰'],'نظام':['system','⚙️']};
function kindOf(k){ return KIND[k]||['info','ℹ️']; }

/* ═══════════ حساب الصفقات المقلقة ═══════════ */
function worriedOf(ps, timeStopH){
  var out=[]; var ts=(timeStopH&&timeStopH>0)?timeStopH:24;
  var ageLim=ts-4; if(ageLim<12) ageLim=12;
  for(var i=0;i<ps.length;i++){
    var p=ps[i], rs=[], sev=0;
    if(p.stop_state!=='verified'){ rs.push({c:'stop',t:'🛡️ ستوب المنصة غير مؤكد'}); sev=3; }
    if(p.pnl_pct!=null&&p.pnl_pct<=-35){ rs.push({c:'loss',t:'📉 خسارة عميقة '+sg(p.pnl_pct,1)+'% من الهامش'}); if(sev<2) sev=2; }
    if(p.age_h!=null&&p.age_h>=ageLim){ rs.push({c:'age',t:'⏳ العمر '+fm(p.age_h,1)+' ساعة — يقترب من الستوب الزمني ('+fm(ts,0)+'س)'}); if(sev<1) sev=1; }
    if(rs.length) out.push({p:p,rs:rs,sev:sev});
  }
  out.sort(function(a,b){ return (b.sev-a.sev)||((a.p.pnl_pct||0)-(b.p.pnl_pct||0)); });
  return out;
}
function stopTag(p){
  var s=p.stop_state;
  if(s==='verified') return '<span class="tag ok">🛡️ مؤكد على المنصة ✓</span>';
  if(s==='placed')   return '<span class="tag warn">⏳ مثبّت — بانتظار التأكيد</span>';
  if(s==='local')    return '<span class="tag local">🛡️ مراقبة محلية فعّالة</span>';
  return '<span class="tag gray">—</span>';
}
function rowActions(p){
  return '<button class="rowbtn" onclick="closeOne(\''+esc(p.symbol)+'\')">🛑 إغلاق</button>'
    +(p.stop_state!=='verified'? ' <button class="rowbtn retry" onclick="cmd(\'stop_retry\',\''+esc(p.symbol)+'\')">🔁 ستوب</button>':'');
}
function rrOf(p){
  try{
    var e=parseFloat(p.entry), sl=parseFloat(p.sl), tp=parseFloat(p.tp);
    var risk=Math.abs(e-sl), rew=Math.abs(tp-e);
    return (risk>0)? (rew/risk).toFixed(2)+':1' : '—';
  }catch(e){ return '—'; }
}

/* ═══════════ جداول الصفقات ═══════════ */
function renderOpen(tr, boxId){
  var box=$(boxId); if(!box) return;
  if(!tr||!tr.length){ box.innerHTML='<div class="empty">لا صفقات مفتوحة — القناص يراقب السوق</div>'; return; }
  var h='<div style="overflow-x:auto"><table><tr><th>الزوج</th><th>اتجاه</th><th>الدخول</th><th>الحالي</th><th>العائم</th><th>% من الهامش</th><th>الهامش</th><th>R:R</th><th>TP1</th><th>SL</th><th>ستوب الحماية</th><th>العمر</th><th>الثقة</th><th>إجراء</th></tr>';
  for(var i=0;i<tr.length;i++){ var t=tr[i];
    h+='<tr><td><b>'+esc(t.symbol)+'</b></td>'
      +'<td><span class="tag '+(t.side==='BUY'?'buy':'sell')+'">'+(t.side==='BUY'?'شراء':'بيع')+'</span></td>'
      +'<td>'+esc(t.entry)+'</td><td>'+esc(t.current)+'</td>'
      +'<td class="'+cls(t.pnl)+'"><b>'+mo(t.pnl)+'</b></td>'
      +'<td class="'+cls(t.pnl_pct)+'">'+sg(t.pnl_pct,1)+'%</td>'
      +'<td>$'+fm(t.margin,2)+'</td>'
      +'<td>'+rrOf(t)+'</td>'
      +'<td>'+esc(t.tp)+'</td><td>'+esc(t.sl)+'</td>'
      +'<td>'+stopTag(t)+'</td>'
      +'<td>'+fm(t.age_h,1)+'س</td>'
      +'<td>'+(t.score!=null? esc(String(t.score))+'/9':'—')+'</td>'
      +'<td>'+rowActions(t)+'</td></tr>';
  }
  box.innerHTML=h+'</table></div>';
}
function renderClosed(list){
  var box=$('closedBox'); if(!box) return;
  list=list||[];
  if(!list.length){ box.innerHTML='<div class="empty">لا صفقات مغلقة بعد — تظهر هنا أول ما تُغلق صفقة</div>'; return; }
  var h='<div style="overflow-x:auto"><table><tr><th>الوقت</th><th>الزوج</th><th>اتجاه</th><th>النتيجة</th><th>% من الهامش</th><th>المصدر</th><th>الثقة</th></tr>';
  for(var i=0;i<list.length;i++){ var c=list[i];
    var src=c.pnl_source==='binance'?'<span class="tag ok">Binance مؤكد ✓</span>':(c.pnl_source==='estimated'?'<span class="tag warn">تقديري ⚠️</span>':'<span class="tag gray">—</span>');
    h+='<tr><td>'+esc(c.time)+'</td><td><b>'+esc(c.symbol)+'</b></td>'
      +'<td><span class="tag '+(c.direction==='BUY'?'buy':'sell')+'">'+(c.direction==='BUY'?'شراء':'بيع')+'</span></td>'
      +'<td class="'+cls(c.pnl)+'"><b>'+mo(c.pnl)+'</b></td>'
      +'<td class="'+cls(c.pnl_pct)+'">'+sg(c.pnl_pct,1)+'%</td>'
      +'<td>'+src+'</td><td>'+(c.score? esc(String(c.score))+'/9':'—')+'</td></tr>';
  }
  box.innerHTML=h+'</table></div>';
}

/* ═══════════ الإشارات وأسباب الرفض ═══════════ */
function renderSignals(list){
  var box=$('sigBox'); if(!box) return;
  list=list||[];
  if(!list.length){ box.innerHTML='<div class="empty">القناص يراقب السوق — لا إشارات مسجلة بعد</div>'; return; }
  var h='<div style="overflow-x:auto"><table><tr><th>الوقت</th><th>الزوج</th><th>اتجاه</th><th>الثقة</th><th>الزناد</th><th>القوة</th><th>R:R</th><th>النتيجة</th></tr>';
  for(var i=0;i<list.length;i++){ var s=list[i];
    var r=s.result===1?'<span class="tag win">ربح</span>':s.result===0?'<span class="tag loss">خسارة</span>':s.result===2?'<span class="tag info">محايدة</span>':'<span class="tag open">مفتوحة/بانتظار</span>';
    h+='<tr><td>'+esc(s.time)+'</td><td><b>'+esc(s.symbol)+'</b></td>'
      +'<td><span class="tag '+(s.direction==='BUY'?'buy':'sell')+'">'+(s.direction==='BUY'?'شراء':'بيع')+'</span></td>'
      +'<td><b>'+esc(String(s.score||0))+'/9</b></td><td>'+esc(s.trigger||'—')+'</td>'
      +'<td>'+(s.power!=null? esc(String(s.power)):'—')+'</td>'
      +'<td>'+(s.rr? esc(String(s.rr))+':1':'—')+'</td><td>'+r+'</td></tr>';
  }
  box.innerHTML=h+'</table></div>';
}
function renderRejections(rj){
  var box=$('rejBox'); if(!box) return;
  rj=rj||{}; var counts=rj.counts||[], recent=rj.recent||[];
  var h='';
  if(counts.length){
    h+='<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px">';
    for(var i=0;i<counts.length;i++)
      h+='<span class="tag info" style="font-size:12px;padding:5px 10px">'+esc(counts[i][0])+' : <b>'+fm(counts[i][1],0)+'</b></span>';
    h+='</div>';
  }
  if(!recent.length){ h+='<div class="empty">لا رفض مسجّل بعد — كل فحص مرفوض يُسجَّل هنا مع سببه</div>'; }
  else{
    h+='<div style="overflow-x:auto"><table><tr><th>الوقت</th><th>الزوج</th><th>سبب الرفض</th></tr>';
    for(var j=0;j<recent.length;j++)
      h+='<tr><td>'+esc(recent[j].time)+'</td><td><b>'+esc(recent[j].symbol)+'</b></td><td>'+esc(recent[j].reason)+'</td></tr>';
    h+='</table></div>';
  }
  box.innerHTML=h;
}

/* ═══════════ سجل الأحداث (الإشعارات) ═══════════ */
function evItem(e){
  var k=kindOf(e.kind);
  var title=esc(e.msg);
  if(e.symbol) title='<span class="tag info" style="margin-inline-end:6px">'+esc(e.symbol)+'</span>'+title;
  var body='';
  if(e.reason) body+='<b>السبب:</b> '+esc(e.reason);
  if(e.detail) body+=(body?'<br>':'')+esc(e.detail);
  return '<div class="nt '+k[0]+'" data-k="'+esc(e.kind)+'"><div class="nt-ic">'+k[1]+'</div>'
    +'<div class="nt-b"><div class="nt-t">'+title+'</div>'
    +(body?'<div class="nt-x">'+body+'</div>':'')
    +'<div class="nt-tm">'+libyaT(e.t)+' — بتوقيت ليبيا</div></div></div>';
}
function buildKindBar(){
  var kinds=['الكل']; var seen={};
  for(var i=lastEvents.length-1;i>=0;i--){ var k=lastEvents[i].kind; if(k&&!seen[k]&&KIND[k]){ seen[k]=1; kinds.push(k); } }
  var bar=$('kindBar'); var h='';
  for(var j=0;j<kinds.length;j++){
    var on=(kinds[j]===curKind);
    h+='<button class="fbtn'+(on?' on':'')+'" onclick="setKind(\''+esc(kinds[j])+'\')">'+(kinds[j]==='الكل'?'الكل':(kindOf(kinds[j])[1]+' '+esc(kinds[j])))+'</button>';
  }
  bar.innerHTML=h;
}
function setKind(k){ curKind=k; buildKindBar(); applyFilter(); }
function applyFilter(){
  var items=document.querySelectorAll('#notifFeed .nt');
  for(var i=0;i<items.length;i++){
    var okK=(curKind==='الكل'||items[i].getAttribute('data-k')===curKind);
    var okQ=!q||items[i].textContent.indexOf(q)>=0;
    items[i].style.display=(okK&&okQ)?'':'none';
  }
}
function renderEvents(evs){
  lastEvents=evs||[];
  var f=$('notifFeed');
  var h='';
  for(var i=lastEvents.length-1;i>=0;i--) h+=evItem(lastEvents[i]);
  f.innerHTML=h||'<div class="empty">لا أحداث بعد — أول دورة مسح قادمة</div>';
  buildKindBar(); applyFilter();
  var mf=$('miniFeed'); var mh='';
  for(var j=lastEvents.length-1, n=0; j>=0&&n<8; j--, n++) mh+=evItem(lastEvents[j]);
  mf.innerHTML=mh||'<div class="empty">لا أحداث بعد</div>';
  var nb=$('nBdg'); if(nb) nb.textContent=fm(lastEvents.length,0);
}

/* ═══════════ الأداء اليومي ═══════════ */
function renderDaily(d){
  d=d||{};
  var tB=$('todayBox');
  var t=d.today;
  if(tB&&t){
    var wr=(t.winrate!==null&&t.winrate!==undefined)?t.winrate+'%':'—';
    tB.innerHTML='<div class="grid" style="margin-bottom:0">'
      +'<div class="card '+(t.pnl>=0?'g':'o')+'"><div class="l">💵 نتيجة اليوم</div><div class="v '+cls(t.pnl)+'">'+mo(t.pnl)+'</div></div>'
      +'<div class="card b"><div class="l">📂 صفقات اليوم (مغلقة)</div><div class="v">'+fm(t.total,0)+'</div><div class="s">مباشرة من السجل الحي: '+fm(d.trades_today_live,0)+'</div></div>'
      +'<div class="card p"><div class="l">✅ رابحة</div><div class="v">'+fm(t.wins,0)+'</div></div>'
      +'<div class="card o"><div class="l">❌ خاسرة</div><div class="v">'+fm(t.losses,0)+'</div></div>'
      +'<div class="card y"><div class="l">🏆 نسبة الفوز</div><div class="v">'+wr+'</div></div>'
      +'</div>';
  }
  var dB=$('daysBox');
  var days=d.days||[];
  if(dB){
    if(!days.length){ dB.innerHTML='<div class="empty">لا سجل أيام بعد — يُجمع تلقائياً مع كل صفقة مغلقة</div>'; }
    else{
      var h='';
      for(var i=0;i<days.length;i++){ var dd=days[i];
        h+='<div style="background:var(--bg2);padding:12px;border-radius:10px;margin-bottom:10px">'
          +'<div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap">'
          +'<div><b>📅 '+esc(dd.date)+'</b></div>'
          +'<div class="'+cls(dd.pnl)+'" style="font-weight:800;font-size:16px">'+mo(dd.pnl)+'</div></div>'
          +'<div style="display:flex;gap:15px;margin-top:6px;font-size:13px;color:var(--sub);flex-wrap:wrap">'
          +'<span>✅ رابحة: <b style="color:var(--green)">'+fm(dd.wins,0)+'</b></span>'
          +'<span>❌ خاسرة: <b style="color:var(--red)">'+fm(dd.losses,0)+'</b></span>'
          +'<span>📊 المجموع: <b>'+fm(dd.total,0)+'</b></span>'
          +'<span>🏆 نسبة الفوز: <b>'+(dd.winrate!=null?dd.winrate+'%':'—')+'</b></span>'
          +'</div></div>';
      }
      dB.innerHTML=h;
    }
  }
  var aB=$('aggBox'); var a=d.aggregates;
  if(aB&&a){
    aB.innerHTML='<div class="kv"><span>أيام نشطة (بصفقات)</span><b>'+fm(a.active_days,0)+'</b></div>'
      +'<div class="kv"><span>إجمالي الصفقات المغلقة</span><b>'+fm(a.total_closed,0)+'</b></div>'
      +'<div class="kv"><span>رابحة / خاسرة</span><b>'+fm(a.total_wins,0)+' / '+fm(Math.max(0,(a.total_closed||0)-(a.total_wins||0)),0)+'</b></div>'
      +'<div class="kv"><span>نسبة الفوز عبر التاريخ</span><b>'+(a.overall_winrate!=null?a.overall_winrate+'%':'—')+'</b></div>'
      +'<div class="kv"><span>إجمالي الربح/الخسارة</span><b class="'+cls(a.total_pnl)+'">'+mo(a.total_pnl)+'</b></div>'
      +(a.best_day?'<div class="kv"><span>🥇 أفضل يوم</span><b>'+esc(a.best_day.date)+' ('+mo(a.best_day.pnl)+')</b></div>':'')
      +(a.worst_day?'<div class="kv"><span>💀 أسوأ يوم</span><b>'+esc(a.worst_day.date)+' ('+mo(a.worst_day.pnl)+')</b></div>':'');
  }
}

/* ═══════════ الاستراتيجية + تشخيص الكون ═══════════ */
function renderStrategy(st){
  var hb=$('hStatus');
  var hmaTxt=st.hma_enabled? (st.hma_live?'⚔️ تداول فعلي':'👁️ إشارات فقط'):'⏸️ معطلة';
  var kvRows='<div class="kv"><span>الوضع</span><b>'+esc(hmaTxt)+'</b></div>'
    +'<div class="kv"><span>الإطار الزمني</span><b>'+esc(st.hma_timeframe||'—')+'</b></div>'
    +'<div class="kv"><span>الصفقات المتزامنة القصوى</span><b>'+fm(st.max_open_trades,0)+'</b></div>'
    +'<div class="kv"><span>الستوب الزمني للصفقة</span><b>'+fm(st.time_stop_h,0)+' ساعة</b></div>'
    +'<div class="kv"><span>سلسلة القبول الحية</span><b style="font-size:11.5px">'+esc(st.describe||'—')+'</b></div>';
  var ms=st.hma_market_states;
  if(ms&&ms.BULL!=null) kvRows+='<div class="kv"><span>📊 آلة الحالات الآن</span><b>BULL: '+fm(ms.BULL,0)+' رمز • BEAR: '+fm(ms.BEAR,0)+' • محايد: '+fm(ms.NEUTRAL,0)+'</b></div>';
  hb.innerHTML=kvRows;
  var ls=st.last_hma_scan||{};
  var bb=$('hBatch');
  var bRows='<div class="kv"><span>فُحص في الدفعة الأخيرة</span><b>'+fm(ls.scanned,0)+' زوجاً</b></div>'
    +'<div class="kv"><span>إشارات الدفعة</span><b>'+fm(ls.signals,0)+'</b></div>'
    +'<div class="kv"><span>مخارج استراتيجية</span><b>'+fm(ls.exits,0)+'</b></div>'
    +(ls.skipped_evening?'<div class="kv"><span>🌙 تخطي بسبب نافذة المساء</span><b>'+fm(ls.skipped_evening,0)+'</b></div>':'')
    +'<div class="kv"><span>كم يُفحص كل دورة؟</span><b>الصفقات المملوكة + دفعة دوّارة — ليس الكون كله</b></div>';
  bb.innerHTML=bRows;
  /* 🔭 تشخيص الكون — إجابة سؤال المالك مباشرة */
  var ud=st.universe_diag||{};
  var uniCard=$('cUni'); var uniSub=$('cUniS');
  var cap=st.hma_pool||ud.pool_cap||0;
  if(uniCard) uniCard.innerHTML=fm(st.universe_count,0)+(cap?' <span style="font-size:14px;color:var(--sub)">/ سقف '+fm(cap,0)+'</span>':'');
  var floorTxt=(ud.floor!=null)? ('من <b style="color:var(--txt)">'+fm(ud.floor,0)+'</b> زوجاً فوق حد السيولة '+fm(ud.min_vol_musd,0)+'م$ (من '+fm(ud.total,0)+' زوجاً دائماً)'):'بانتظار أول تحديث للكون…';
  if(uniSub) uniSub.innerHTML=floorTxt;
  var diag=$('uniDiag');
  if(diag){
    var d='<div class="kv"><span>🌐 كل أزواج الفوتشرز الدائمة USDT</span><b>'+fm(ud.total,0)+'</b></div>'
      +'<div class="kv"><span>💧 تجاوزوا حد السيولة 24س (≥ '+fm(ud.min_vol_musd,0)+'م$)</span><b>'+fm(ud.floor,0)+'</b></div>'
      +'<div class="kv"><span>📦 سقف المرشح HMA_UNIVERSE_POOL</span><b>'+fm(cap,0)+'</b></div>'
      +'<div class="kv"><span>✂️ أُقصوا بفلتر الانتشار (اختياري)</span><b>'+fm(ud.spread_cut,0)+'</b></div>'
      +'<div class="kv"><span>🔭 المرشح الفعلي (المعروض في البطاقة)</span><b>'+fm(st.universe_count,0)+'</b></div>'
      +'<div class="kv"><span>📏 حجم الكون HMA_UNIVERSE_SIZE (سقف الفحص بالتناوب)</span><b>'+fm(st.hma_universe_size,0)+'</b></div>'
      +'<div class="kv"><span>🔁 الدفعة المفحوصة كل دورة</span><b>'+fm(ls.scanned,0)+' (تصميم الدفعة الدوّارة — عمداً)</b></div>';
    var size=st.hma_universe_size||0, floor=ud.floor;
    if(floor!=null&&size&&floor<size){
      d+='<div class="diagbox" style="background:rgba(234,179,8,.08);border-color:rgba(234,179,8,.45);color:#fde68a">'
        +'⚠️ <b>هذا هو السبب الحالي:</b> فقط '+fm(floor,0)+' زوجاً تجاوز حد السيولة '+fm(ud.min_vol_musd,0)+'م$ — أقل من الحجم المطلوب '+fm(size,0)
        +'. متغيرا POOL/SIZE سليمان ويعملان، لكن السيولة العامة للسوق الآن أقل. البوت يفحص كل ما هو متاح فوق الحد، والعدد يعود ليكبر تلقائياً مع نشاط السوق.'
        +'<br>لرفع العدد: خفّض <span style="direction:ltr;display:inline-block">HMA_SCAN_MIN_VOL_USDT</span> في Railway (مثلاً 20000000).</div>';
    } else if(floor!=null&&size){
      d+='<div class="diagbox" style="background:rgba(0,212,170,.08);border-color:rgba(0,212,170,.45);color:#99f6e4">'
        +'✅ <b>الوضع سليم:</b> عدد الأزواج فوق حد السيولة ('+fm(floor,0)+') يغطي الحجم المطلوب ('+fm(size,0)+') — والفرق إن وجد يأتي من سقف المرشح أو فلتر الانتشار فقط.</div>';
    }
    diag.innerHTML=d;
  }
  /* وصف + تعارضات + حقول الإعدادات */
  var de=$('hmaDesc'); if(de) de.innerHTML='🧠 السلسلة النشطة: <b style="color:var(--txt)">'+esc(st.describe||'—')+'</b>';
  var cf=$('hmaConf');
  if(cf){
    var conf=st.env_conflicts||[];
    cf.innerHTML=conf.length?
      ('<div class="diagbox" style="background:rgba(239,68,68,.08);border-color:rgba(239,68,68,.4);color:#fca5a5">'
      +'<b>⚠️ تعارض Railway (عرض فقط — القاعدة هي المرجع):</b><br>'
      +conf.map(function(c){ return '<span style="direction:ltr;display:inline-block">'+esc(c.env)+'</span> = '+esc(c.env_value)+' (الفعال: '+esc(c.active_value)+' — '+esc(c.label)+')'; }).join('<br>')
      +'</div>'):'';
  }
  var s=st.hma_settings||{};
  var tfSel=$('hmaTF');
  if(tfSel&&s.timeframe) tfSel.value=s.timeframe;
  for(var i=0;i<HMA_FIELDS.length;i++){
    var el=$('hmaF_'+HMA_FIELDS[i][0]);
    if(el&&s[HMA_FIELDS[i][0]]!==undefined&&document.activeElement!==el) el.value=s[HMA_FIELDS[i][0]];
  }
}
/* ═══════════ أداء الاستراتيجية عبر التاريخ (من القاعدة فعلياً) ═══════════ */
function renderPerf(st){
  var box=$('perfBox'); if(!box) return;
  var p=st.strat_perf;
  if(!p){ box.innerHTML='<div class="empty">بانتظار أول مزامنة من قاعدة البيانات…</div>'; return; }
  box.innerHTML='<div class="kv"><span>📡 إشارات مكتشفة (كل التاريخ)</span><b>'+fm(p.signals,0)+'</b></div>'
    +'<div class="kv"><span>✅ صفقات منفذة مغلقة</span><b>'+fm(p.executed,0)+'</b></div>'
    +'<div class="kv"><span>🏆 رابحة / خاسرة (المحايدة مستثناة من النسبة)</span><b>'+fm(p.wins,0)+' / '+fm(p.losses,0)+'</b></div>'
    +'<div class="kv"><span>🏆 نسبة الفوز</span><b>'+(p.winrate!=null? p.winrate+'%':'—')+'</b></div>'
    +'<div class="kv"><span>💵 صافي النتيجة</span><b class="'+cls(p.net_pnl)+'">'+mo(p.net_pnl)+'</b></div>'
    +'<div class="kv"><span>📈 متوسط الربح</span><b>'+(p.avg_win!=null? mo(p.avg_win):'—')+'</b></div>'
    +'<div class="kv"><span>📉 متوسط الخسارة</span><b>'+(p.avg_loss!=null? mo(p.avg_loss):'—')+'</b></div>'
    +'<div class="kv"><span>⚖️ Profit Factor (مجموع الأرباح ÷ مجموع الخسائر)</span><b>'+(p.profit_factor!=null? fm(p.profit_factor,2):'—')+'</b></div>'
    +'<div class="kv"><span>🕳️ أقصى تراجع لمنحنى الأرباح المتراكم</span><b class="neg">'+(p.max_drawdown!=null? '$'+fm(p.max_drawdown,2):'—')+'</b></div>'
    +'<div class="kv"><span>🥇 أفضل الرموز (صافي كل رمز)</span><b style="font-size:12px">'+esc(p.by_symbol||'—')+'</b></div>'
    +'<div class="kv"><span>🎯 آخر إشارة مسجلة</span><b style="font-size:12px">'+esc(p.last_signal||'—')+'</b></div>';
}
var HMA_FIELDS=[
 ['hma_fast','HMA السريعة',4,50],['hma_slow','HMA البطيئة',10,200],
 ['di_period','فترة DI',3,30],['adx_smooth','تنعيم ADX',3,30],
 ['mom_fast','زخم سريع',1,20],['mom_mid','زخم متوسط',2,40],['mom_slow','زخم بطيء',3,60],
 ['er_period','فترة كفاءة الحركة ER',5,50],['struct_period','فترة بنية السوق',3,20],
 ['st_atr_period','فترة ATR لـ Supertrend',5,50],['st_mult','معامل ATR لـ Supertrend',0.5,5],
 ['ema_period','فترة EMA (فلتر الاتجاه)',50,400],['ema_filter','فلتر EMA200 (1=مفعّل 0=معطل)',0,1],
 ['min_power','أدنى قوة دخول (0-100)',0,100],['min_confidence','أدنى ثقة دخول (0-9)',0,9],
 ['strong_adx','عتبة ADX القوي',5,50],['strong_er','عتبة ER القوي',0.05,0.9],
 ['min_mom_conf','أدنى تأكيدات الزخم (1-3)',1,3],['min_state_candles','أدنى مدة الحالة (شموع)',1,20],
 ['cooldown_candles','تبريد الإشارات/التبدّل (شموع)',0,30],['reversal_atr','عتبة الانقلاب (×ATR)',0.1,5],
 ['so_power','قوة الاستثناء الهيكلي',0,100],['so_confidence','ثقة الاستثناء الهيكلي',0,9],
 ['so_adx','ADX للاستثناء الهيكلي',5,50],['adx_gate','بوابة اتجاهية ADX-14 (0=معطلة)',0,50],
 ['sl_atr_mult','الستوب (×ATR)',0.3,6],['risk_min_pct','أدنى مسافة ستوب (%)',0.05,2],
 ['risk_max_pct','أقصى مسافة ستوب (%)',0.5,10],['min_rr','أدنى عائد/مخاطرة R:R',0.5,5],
 ['tp1_return_pct','هدف TP1 (% من الهامش)',1,100],['tp1_max_atr','أقصى مسافة TP1 (×ATR)',1,20],
 ['universe_size','حجم كون HMA (أعلى سيولة)',10,200],['batch_size','عدد العملات المفحوصة كل دورة',4,60],
 ['parallel','تحليلات متوازية',1,10],['max_signals_per_scan','أقصى إشارات منفذة في الدورة',1,3],
 ['trend4h_enabled','بوابة اتجاه 4 ساعات (1=مفعّلة)',0,1],['trend4h_ema_len','فترة EMA لبوابة 4 ساعات',20,200]
];
function buildHmaFields(){
  var box=$('hmaFields'); if(!box) return;
  var h='<div class="kv"><span>⏱️ الإطار الزمني</span><b><select id="hmaTF" class="sin" style="direction:rtl"><option value="5m">5 دقائق</option><option value="15m">15 دقيقة</option><option value="1h">ساعة</option></select></b></div>';
  for(var i=0;i<HMA_FIELDS.length;i++){
    var f=HMA_FIELDS[i];
    h+='<div class="kv"><span>'+esc(f[1])+'</span><b><input class="sin" id="hmaF_'+f[0]+'" type="number" step="any" min="'+f[2]+'" max="'+f[3]+'"></b></div>';
  }
  box.innerHTML=h;
}
async function hmaSave(){
  var NL=String.fromCharCode(10);
  if(!confirm('تطبيق قيم الإعدادات المدخلة على البوت الحي وحفظها في القاعدة؟'+NL+'التعديل يعمل لحظياً ويصمد لإعادة التشغيل.')) return;
  var p={};
  var tf=$('hmaTF'); if(tf&&tf.value) p.timeframe=tf.value;
  for(var i=0;i<HMA_FIELDS.length;i++){
    var el=$('hmaF_'+HMA_FIELDS[i][0]);
    if(el&&el.value!==''&&!isNaN(parseFloat(el.value))) p[HMA_FIELDS[i][0]]=parseFloat(el.value);
  }
  await cmd('hma_settings', null, p);
}

/* ═══════════ النظام: الإعدادات + الأخطاء + الأخبار ═══════════ */
function renderSystem(st){
  var nw=st.news||{};
  var sb=$('setBox');
  if(sb){
    sb.innerHTML='<div class="kv"><span>الوضع</span><b>'+esc(st.mode||'—')+'</b></div>'
      +'<div class="kv"><span>Testnet</span><b>'+(st.testnet?'🧪 نعم — تجريبي':'لا — حقيقي')+'</b></div>'
      +'<div class="kv"><span>الرافعة</span><b>'+fm(st.leverage,0)+'x</b></div>'
      +'<div class="kv"><span>الهامش لكل صفقة</span><b>$'+fm(st.trade_size,2)+'</b></div>'
      +'<div class="kv"><span>النوشنال</span><b>$'+fm((st.trade_size||0)*(st.leverage||1),0)+'</b></div>'
      +'<div class="kv"><span>🎯 هدف TP1</span><b>'+fm((st.hma_settings||{}).tp1_return_pct,0)+'% من الهامش — إغلاق 100%</b></div>'
      +'<div class="kv"><span>⏰ الستوب الزمني</span><b>'+fm(st.time_stop_h,0)+' ساعة</b></div>'
      +'<div class="kv"><span>المتزامنة</span><b>'+fm(st.max_open_trades,0)+'</b></div>'
      +'<div class="kv"><span>أزواج الفوتشرز الدائمة</span><b>'+fm(st.pairs_total,0)+'</b></div>'
      +'<div class="kv"><span>تبريد إعادة الدخول</span><b>15 دقيقة لكل زوج</b></div>'
      +'<div class="kv"><span>🔭 الكون / السقف</span><b>'+fm(st.universe_count,0)+' / '+fm(st.hma_pool,0)+' — فحص بالتناوب أعلى '+fm(st.hma_universe_size,0)+'</b></div>'
      +'<div class="kv"><span>ستوب المنصة</span><b>STOP_MARKET حقيقي + مراقبة محلية احتياطية</b></div>'
      +'<div class="kv"><span>🌙 حظر المساء</span><b>'+(st.evening_block?('مفعّل '+esc(st.evening_window||'')):'معطل')+'</b></div>'
      +'<div class="kv"><span>أوامر الدخول</span><b>محاولة واحدة — لا دخول مزدوج</b></div>';
  }
  var eb=$('errBox');
  var er=st.errors||{}; var ks=Object.keys(er);
  if(eb){
    if(!ks.length) eb.innerHTML='<div class="empty" style="padding:16px">✅ لا أخطاء — كل شيء نظيف</div>';
    else{
      var h='';
      for(var i=0;i<ks.length;i++) h+='<div class="kv"><span>'+esc(ks[i])+'</span><b style="color:var(--orange)">×'+fm(er[ks[i]],0)+'</b></div>';
      eb.innerHTML=h;
    }
  }
  var nb=$('newsBox');
  if(nb){
    var txt,lvl;
    if(nw.enabled){
      if(nw.blocked_now){ txt='🔇 كتم نشط — '+esc(nw.reason||''); lvl='warn'; }
      else if(nw.next_event){ txt='مفعّل 📰 — القادم: '+esc(nw.next_event.title)+' بعد '+fm(nw.next_event.in_min,0)+' دقيقة'; lvl='ok'; }
      else if(nw.calendar_updated){ txt='مفعّل 📰 — لا أحداث مؤثرة قريبة'; lvl='ok'; }
      else { txt='مفعّل 📰 — بانتظار جلب التقويم…'; lvl='warn'; }
    } else { txt='معطل — فعّله بالزر أدناه'; lvl='warn'; }
    nb.innerHTML='<div class="kv"><span>الحالة</span><b>'+txt+'</b></div>'
      +'<div class="kv"><span>النوافذ اليدوية</span><b style="direction:ltr">'+esc(nw.windows||'—')+'</b></div>'
      +'<div class="kv"><span>العملات المراقبة</span><b style="font-size:11px">'+esc(nw.currencies||'—')+'</b></div>'
      +'<div class="kv"><span>إحاطة الحدث</span><b>قبل '+fm(nw.before_min,0)+' د / بعد '+fm(nw.after_min,0)+' د</b></div>'
      +'<div class="kv"><span>أحداث التقويم</span><b>'+fm(nw.events_count,0)+(nw.calendar_age_min!=null?' — عمر الجلب '+fm(nw.calendar_age_min,0)+' د':'')+'</b></div>'
      +(nw.last_error?'<div class="kv"><span>⚠️ آخر خطأ جلب</span><b style="color:var(--orange)">'+esc(nw.last_error)+'</b></div>':'');
  }
}

/* ═══════════ العرض الرئيسي ═══════════ */
function render(payload){
  var st=payload.state||{};
  lastState=st;
  $('lastUpd').textContent=libyaT(payload.now||Math.floor(Date.now()/1000));
  $('connTxt').innerHTML='<b>متصل بالبوت الحي ✓</b>';
  var lv=(st.price_age!=null&&st.price_age<120);
  $('liveB').className='badge'+(lv?'':' off');
  $('liveT').textContent=lv?'البوت حي ✓':'توقف الأسعار!';
  var mode=st.trade_enabled? (st.testnet?'⚔️ تداول تجريبي 🧪':'⚔️ تداول فعلي'):'👁️ مراقبة';
  $('modeTxt').textContent=mode+' — استراتيجية HMA_DMI_MOMENTUM فقط';
  $('cBal').textContent='$'+fm(st.balance,2);
  $('cMode').textContent=mode+' • رافعة '+fm(st.leverage,0)+'x • هامش $'+fm(st.trade_size,0);
  var tdy=(st.daily||{}).today;
  var dp=(tdy&&typeof tdy.pnl==='number')?tdy.pnl:(st.daily_pnl||0);
  var dEl=$('cDay'); dEl.textContent=mo(dp); dEl.className='v '+cls(dp);
  $('cDayS').textContent=tdy?(fm(tdy.wins,0)+' رابحة / '+fm(tdy.losses,0)+' خاسرة اليوم'):'—';
  var tw=(st.stats? (st.stats.wins||0)+(st.stats.losses||0):0);
  $('cWr').textContent=tw? Math.round((st.stats.wins||0)/tw*100)+'%':'—';
  $('cWrS').textContent=fm(st.stats?st.stats.wins||0:0,0)+'W / '+fm(st.stats?st.stats.losses||0:0,0)+'L (كل التاريخ)';
  $('cOpen').textContent=fm(st.open_count,0);
  $('cOpenS').textContent='الحد المتزامن: '+fm(st.max_open_trades,0)+' • تنفيذ تراكمي: '+fm(st.trades_executed,0);
  $('cCyc').textContent=fm(st.cycles,0);
  $('cCycS').textContent='آخر دفعة: فحص '+fm((st.last_hma_scan||{}).scanned,0)+' • إشارات '+fm((st.last_hma_scan||{}).signals,0);
  /* الصفقات المفتوحة */
  renderOpen(st.positions||[],'openBox');
  renderOpen(st.positions||[],'openBox2');
  /* الحمايات */
  var sh=st.stop_health||{total:0};
  var lv2=(st.price_age!=null&&st.price_age<120);
  var stopHlTxt, stopHlLv;
  if(!sh.total){ stopHlTxt='لا مراكز مفتوحة'; stopHlLv='ok'; }
  else if(sh.local&&sh.local>0){ stopHlTxt='⚠️ مراقبة محلية: '+(sh.failed||[]).map(function(f){return f.symbol;}).join('، ')+' — زر 🔁 في الصفقات'; stopHlLv='warn'; }
  else if(sh.verified===sh.total){ stopHlTxt='ستوبات المنصة مؤكدة ✓ ('+fm(sh.verified,0)+'/'+fm(sh.total,0)+')'; stopHlLv='ok'; }
  else { stopHlTxt='قيد التثبيت والتأكيد... ('+fm((sh.verified||0)+(sh.local||0),0)+'/'+fm(sh.total,0)+')'; stopHlLv='warn'; }
  var nw=st.news||{};
  var newsTxt,newsLv;
  if(nw.enabled){
    if(nw.blocked_now){ newsTxt='🔇 كتم نشط — '+(nw.reason||''); newsLv='warn'; }
    else if(nw.next_event){ newsTxt='مفعّل — القادم: '+esc(nw.next_event.title)+' بعد '+fm(nw.next_event.in_min,0)+' د'; newsLv='ok'; }
    else { newsTxt='مفعّل 📰'; newsLv='ok'; }
  } else { newsTxt='معطل — يُدار من ⚙️ النظام'; newsLv='warn'; }
  var rk=st.risk||{};
  $('healthBox').innerHTML=[
    ['تدفق الأسعار', lv2?'متصل ✓':'متوقف '+fm(st.price_age,0)+' ثانية', lv2?'ok':'bad'],
    ['ستوبات الحماية', stopHlTxt, stopHlLv],
    ['الرصيد', '$'+fm(st.balance,2), (st.balance>=(st.trade_size||0))?'ok':'warn'],
    ['الوضع', mode, st.trade_enabled?'ok':'warn'],
    ['نافذة المساء', st.evening_block? (st.evening_blocked_now?'🌙 سارية الآن — الدخول معطل':'خارج النافذة — الدخول متاح'):'ℹ️ معطل', st.evening_blocked_now?'warn':'ok'],
    ['فلتر الأخبار', newsTxt, newsLv],
    ['مدير المخاطر', rk.can_trade?'✅ مسموح':'🛑 '+(rk.reason||'ممنوع'), rk.can_trade?'ok':'bad']
  ].map(function(h){ return '<div class="hi"><div class="hd2 '+h[2]+'"></div><div><div class="hn">'+h[0]+'</div><div class="hs">'+h[1]+'</div></div></div>'; }).join('');
  /* الصفقات المقلقة + الشارة */
  var tsh=st.time_stop_h||24;
  $('legTs').textContent=fm(tsh,0);
  var wr=worriedOf(st.positions||[], tsh);
  var wb=$('wBdg');
  wb.textContent=fm(wr.length,0);
  wb.className='tag '+(wr.length?'stop':'ok');
  var wbox=$('worriedBox');
  if(!wr.length){
    wbox.innerHTML='<div class="empty" style="color:#10b981">✅ لا صفقات مقلقة — كل المراكز المفتوحة سليمة (الستوبات مؤكدة، لا خسائر عميقة، والأعمار بعيدة عن الستوب الزمني)</div>';
  } else {
    var wh='';
    for(var i=0;i<wr.length;i++){
      var w=wr[i], p=w.p;
      var chips='';
      for(var m=0;m<w.rs.length;m++) chips+='<span class="tag '+(w.rs[m].c==='stop'?'stop':(w.rs[m].c==='loss'?'loss':'info'))+'">'+esc(w.rs[m].t)+'</span>';
      wh+='<div class="wrrow sev'+w.sev+'">'
        +'<div class="wsym">'+esc(p.symbol)+' <span class="tag '+(p.side==='BUY'?'buy':'sell')+'">'+(p.side==='BUY'?'شراء':'بيع')+'</span></div>'
        +'<div class="wnums"><span class="'+cls(p.pnl)+'"><b>'+mo(p.pnl)+'</b></span> ('+sg(p.pnl_pct,1)+'%)<br><span style="color:var(--sub);font-size:11px">العمر '+fm(p.age_h,1)+'س • هامش $'+fm(p.margin,2)+'</span></div>'
        +'<div class="wchips">'+chips+stopTag(p)+'</div>'
        +'<div class="wact">'+rowActions(p)+'</div></div>';
    }
    wbox.innerHTML=wh;
  }
  /* بقية الأقسام */
  renderClosed(st.closed);
  renderSignals(st.signals);
  renderRejections(st.rejections);
  renderEvents(payload.events);
  renderDaily(st.daily);
  renderStrategy(st);
  renderPerf(st);
  renderSystem(st);
  var stats=st.stats||{};
  $('sgTotal').textContent=fm(stats.total_signals||0,0);
  $('sgExec').textContent=fm(stats.trades_executed||0,0);
  $('sgExecS').textContent='مرفوضة بالمخاطر: '+fm(stats.rejected_by_risk||0,0)+' • بالأخبار: '+fm(stats.rejected_by_news||0,0)+' • لحظة التنفيذ: '+fm(stats.rejected_execution||0,0);
  $('sgRejQ').textContent=fm(stats.rejected_quality||0,0);
  $('sgRejO').textContent=fm(stats.rejected_open_trade||0,0);
  $('rStatus').textContent=rk.can_trade?'✅ مسموح':'🛑 ممنوع';
  $('rStatus').className='v '+(rk.can_trade?'pos':'neg');
  $('rReason').textContent=rk.reason||'—';
  $('rCons').textContent=fm(rk.consecutive_losses||0,0);
  $('rDay').textContent=fm(rk.daily_losses||0,0);
  var rp=$('rPnl'); rp.textContent=mo(rk.daily_pnl||0); rp.className='v '+cls(rk.daily_pnl||0);
  $('rPnlS').textContent='الرصيد المرجعي: $'+fm(rk.initial_balance||0,2);
  $('pauseBtn').textContent=st.trade_enabled?'⏸️ إيقاف مؤقت':'▶️ استئناف';
}

/* ═══════════ الأوامر ═══════════ */
async function cmd(action, sym, data){
  if(BOT_URL&&PANEL_STANDALONE&&!live){ alert('اتصل بالبوت الحي أولاً (أو استخدم العرض التجريبي للمشاهدة فقط)'); return; }
  if(!PANEL_STANDALONE&&!live){ alert('⏳ انتظر الاتصال بالبوت ثم أعد الأمر'); return; }
  try{
    var body={action:action}; if(sym) body.symbol=sym; if(data) body.data=data;
    var opt={method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)};
    var r=await fetch(BOT_URL+'/api/command?key='+encodeURIComponent(KEY),opt);
    if(r.status===401){ $('keyBanner').style.display='block'; alert('🔒 الأمر يتطلب مفتاح DASHBOARD_TOKEN — أدخله في الأعلى ثم أعد الأمر'); return; }
    var j=await r.json();
    alert((j.ok?'✅ ':'❌ ')+(j.info||j.error||'تم الأمر'));
    loadAll();
  }catch(e){ alert('❌ فشل الاتصال: '+e.message); }
}
function closeOne(sym){ if(confirm('🛑 إغلاق صفقة '+sym+' فوراً بسعر السوق؟')) cmd('close_one',sym); }
function closeAllCmd(){ if(confirm('⚠️ إغلاق كل الصفقات المفتوحة فوراً بسعر السوق؟ لا تراجع بعد التنفيذ.')) cmd('close_all'); }
function togglePause(){
  var running=!(lastState&&lastState.trade_enabled===false);
  if(running){ if(confirm('⏸️ إيقاف التداول (طوارئ)؟\nلن تُفتح أي صفقة جديدة — إدارة المفتوحة والمخارج تستمر طبيعياً.')) cmd('pause'); }
  else{ if(confirm('▶️ استئناف التداول؟ سُتُفتح صفقات جديدة وفق إشارات HMA مجدداً.')) cmd('resume'); }
}
function resetAll(){
  var NL=String.fromCharCode(10);
  var msg='⚠️ إعادة ضبط شاملة!'+NL+NL+'سيتم مسح:'+NL
    +'📋 سجل كل الأحداث (الشاشة + bot_events.jsonl)'+NL
    +'📂 سجل الصفقات والإشارات'+NL+'🚫 سجل أسباب الرفض'+NL
    +'📊 الإحصائيات اليومية والإجماليات'+NL+'🚨 عدّادات الأخطاء'+NL+NL
    +'✅ لن تُغلق أي صفقة مفتوحة'+NL+'❌ لا يمكن التراجع! متابعة؟';
  if(!confirm(msg)) return;
  if(!confirm('❓ تأكيد أخير: هل أنت متأكد 100%؟')) return;
  cmd('reset_all');
}

/* ═══════════ الحلقة ═══════════ */
var live=false;
async function loadAll(){
  try{
    var s=await api('/api/state?limit=400'+(KEY?('&key='+encodeURIComponent(KEY)):''));
    live=true;
    $('offBanner').style.display='none';
    $('keyBanner').style.display='none';
    render(s);
    return true;
  }catch(e){
    live=false;
    if(String(e.message)!=='locked') $('offBanner').style.display='block';
    $('connTxt').textContent='تعذر الاتصال — إعادة المحاولة جارية…';
    if(PANEL_STANDALONE){ $('offBanner').style.display='none'; startDemo(); }
    return false;
  }
}
function tick(){ loadAll(); }
function startDemo(){
  /* عرض تجريبي للتصميم فقط — بيانات وهمية (للنسخة المستقلة) */
  if(!PANEL_STANDALONE||live) return;
  var T=function(s){ return Math.floor(Date.now()/1000)-s; };
  var st={status:'يعمل',mode:'⚔️ تداول فعلي — بيانات تجريبية',hma_timeframe:'1h',testnet:false,uptime_h:5.2,
    evening_block:true,evening_blocked_now:false,evening_window:'16:00 ← 23:59 UTC',
    trade_enabled:true,max_open_trades:3,leverage:10,trade_size:25,pairs_total:487,price_age:3,
    risk_ok:true,risk_reason:'جميع الحدود ضمن النطاق',risk:{can_trade:true,reason:'جميع الحدود ضمن النطاق',consecutive_losses:1,daily_losses:1,daily_pnl:12.4,initial_balance:1000},
    hma_enabled:true,hma_live:true,time_stop_h:24,
    last_hma_scan:{scanned:13,signals:1,exits:0,skipped_evening:0},
    universe_count:171,hma_pool:300,hma_universe_size:200,hma_min_vol_musd:30,
    universe_diag:{total:487,floor:171,spread_cut:2,pool:171,pool_cap:300,min_vol_musd:30},
    balance:4886.72,daily_pnl:-12.19,trades_today:4,wins:34,losses:27,open_count:1,cycles:586,trades_executed:61,
    stats:{total_signals:154,trades_executed:61,rejected_quality:83,rejected_open_trade:9,rejected_by_risk:2,rejected_by_news:1,rejected_execution:3,wins:34,losses:27},
    stop_health:{total:1,verified:0,placed:0,local:1,failed:[{symbol:'DIAUSDT'}]},
    news:{enabled:true,blocked_now:false,next_event:{title:'قرار الفائدة الفيدرالي',in_min:240},windows:'—',currencies:'USD',before_min:30,after_min:15,events_count:8,calendar_age_min:12},
    errors:{},
    hma_settings:{timeframe:'1h',hma_fast:8,hma_slow:21,min_power:24,min_confidence:5,universe_size:200,batch_size:12,tp1_return_pct:30,min_rr:1.2},
    env_conflicts:[],
    hma_market_states:{BULL:18,BEAR:9,NEUTRAL:144},
    strat_perf:{signals:154,executed:61,wins:34,losses:27,winrate:55.7,net_pnl:112.86,avg_win:8.41,avg_loss:-4.03,profit_factor:2.09,max_drawdown:23.7,by_symbol:'DOGEUSDT (+31.20$)، SOLUSDT (+18.75$)، LINKUSDT (−9.40$)',last_signal:'SOLUSDT SELL 10-27 11:20 مساءً — انعكاس هيكلي'},
    describe:'HMA 8/21 | DI 7/ADX 6 | زخم 2/5/9 | ER 10 | ST 14×1.35 | قوة≥24 ثقة≥5 | بوابة ADX≥20 | بوابة 4س EMA50+ميل ✓ | 1h | TP1=30% | R:R≥1.2',
    daily:{today:{date:'2026-10-28',pnl:-12.19,wins:3,losses:1,total:4,winrate:75},days:[{date:'2026-10-28',pnl:-12.19,wins:3,losses:1,total:4,winrate:75},{date:'2026-10-27',pnl:38.4,wins:6,losses:2,total:8,winrate:75}],aggregates:{active_days:2,total_closed:12,total_wins:9,total_pnl:26.21,overall_winrate:75,best_day:{date:'2026-10-27',pnl:38.4},worst_day:{date:'2026-10-28',pnl:-12.19}},trades_today_live:4},
    closed:[{symbol:'DOGEUSDT',direction:'BUY',time:'10-27 09:41 مساءً',pnl:7.5,pnl_pct:30,score:7,pnl_source:'binance'},{symbol:'LINKUSDT',direction:'SELL',time:'10-27 06:12 مساءً',pnl:-2.61,pnl_pct:-10.4,score:5,pnl_source:'binance'}],
    signals:[{symbol:'SOLUSDT',direction:'SELL',time:'10-27 11:20 مساءً',score:7,trigger:'انعكاس هيكلي',power:38,rr:1.8,result:-1,pnl:null},{symbol:'ARBUSDT',direction:'BUY',time:'10-27 08:05 مساءً',score:6,trigger:'استئناف زخم',power:31,rr:1.5,result:1,pnl:7.5}],
    rejections:{counts:[['🌙 نافذة المساء 16–23 UTC',42],['قوة/ثقة أقل من العتبة',31],['الرمز خارج الكون السائل',18]],recent:[{time:'10-27 11:41 مساءً',symbol:'PEPEUSDT',reason:'الثقة 4/9 < الحد 5'},{time:'10-27 11:40 مساءً',symbol:'WIFUSDT',reason:'حجم 24س 4.1م$ أقل من الحد 30م$'}]},
    positions:[
      {symbol:'SOLUSDT',side:'SELL',entry:'203.45',current:'199.12',margin:25,pnl:10.63,pnl_pct:42.5,sl:'209.55',tp:'190.20',age_h:3.4,stop_state:'verified',score:7},
      {symbol:'DIAUSDT',side:'SELL',entry:'0.1409',current:'0.1408',margin:25,pnl:-0.18,pnl_pct:-0.7,sl:'0.1443',tp:'0.1366',age_h:8.2,stop_state:'local',score:6}
    ]};
  var evs=[
    {t:T(90),kind:'دورة',msg:'الدورة #586 — كون 171 زوجاً | مفتوحة 1/3'},
    {t:T(600),kind:'نبض',msg:'القلب ينبض — آخر مسح 13 زوجاً | بدون أخطاء'},
    {t:T(1500),kind:'رفض',symbol:'PEPEUSDT',msg:'قوة/ثقة أقل من العتبة',reason:'الثقة 4/9 < الحد المطلوب 5'},
    {t:T(3000),kind:'دخول',symbol:'DIAUSDT',msg:'تنفيذ SELL @ 0.1409 | هامش $25.00',reason:'SL 0.1443 | TP1 0.1366'},
    {t:T(5000),kind:'خروج',symbol:'DOGEUSDT',msg:'TP1 — إغلاق كامل عند الهدف الأول',reason:'النتيجة +7.50 USDT (+30% من الهامش)'},
    {t:T(7000),kind:'نظام',msg:'تحديث الكون: 169 → 171 زوجاً (سيولة 24س ≥ 30م$)'}
  ];
  $('urlBox').classList.remove('hidden');
  render({state:st,events:evs,now:Math.floor(Date.now()/1000)});
  $('connTxt').textContent='👁️ وضع العرض التجريبي — بيانات وهمية للتصميم فقط';
  var _lb=$('liveB'); _lb.className='badge off'; $('liveT').textContent='وضع تجريبي — لا بوت';
}

readKey(); loadUrl(); buildHmaFields();
if(PANEL_STANDALONE){ var _ub=$('urlBox'); if(_ub) _ub.classList.remove('hidden'); }
try{ var _t=localStorage.getItem('dashTab'); if(_t&&$('t-'+_t)){ var b=document.querySelector(".tab[onclick*='"+_t+"']"); if(b) sw(_t,b); else sw(_t); } }catch(e){}
tick(); setInterval(tick,10000);
</script>
</body>
</html>
