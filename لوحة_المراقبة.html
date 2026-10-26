<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🎯 لوحة مراقبة القناص — HMA (ملف مستقل)</title>
<style>
  :root{
    --bg:#0b1220; --panel:#111a2e; --panel2:#0e1626; --line:#1e2a44;
    --txt:#e7edf7; --dim:#8b9bb8; --green:#2ecc71; --red:#ff5c69;
    --gold:#f5b942; --blue:#4da3ff; --purple:#b48bff; --cyan:#39d0d8;
  }
  *{box-sizing:border-box; margin:0; padding:0}
  body{background:var(--bg); color:var(--txt); font-family:"Segoe UI",Tahoma,"Noto Sans Arabic",Arial,sans-serif; font-size:14px; padding:16px; padding-bottom:40px}
  .wrap{max-width:1280px; margin:0 auto}
  /* ═══ شريط وضع الاتصال (خاص بالملف المستقل) ═══ */
  .mode{display:flex; flex-wrap:wrap; gap:10px; align-items:center; border-radius:12px; padding:9px 14px; margin-bottom:14px; font-size:13px; border:1px solid var(--line); background:var(--panel)}
  .mode.demo{border-color:#5b4a1e; background:linear-gradient(90deg,#231c08,#1a1508); color:var(--gold)}
  .mode.live{border-color:#1d4d33; background:linear-gradient(90deg,#0a2114,#081a0f); color:#7ee2a8}
  .mode .burl{display:flex; flex-wrap:wrap; gap:8px; align-items:center; color:var(--dim); font-size:12px}
  .mode input{background:var(--panel2); border:1px solid var(--line); border-radius:10px; padding:5px 10px; color:var(--txt); font-family:Consolas,Menlo,monospace; direction:ltr; font-size:12px; width:230px; outline:none}
  .mode input:focus{border-color:#33507f}
  .mode button{background:#1c2a4a; color:#fff; border:1px solid #33507f; border-radius:10px; padding:5px 14px; cursor:pointer; font-family:inherit; font-size:12px}
  .mode button:hover{background:#24365c}
  /* ═══ الترويسة ═══ */
  .hdr{display:flex; flex-wrap:wrap; gap:10px; align-items:center; justify-content:space-between; margin-bottom:14px}
  .hdr h1{font-size:19px; font-weight:700}
  .hdr h1 small{color:var(--dim); font-weight:400; font-size:12px; margin-inline-start:8px}
  .chips{display:flex; flex-wrap:wrap; gap:8px}
  .chip{background:var(--panel); border:1px solid var(--line); border-radius:20px; padding:5px 12px; font-size:12px; color:var(--dim)}
  .chip b{color:var(--txt); font-weight:600}
  .dot{display:inline-block; width:8px; height:8px; border-radius:50%; margin-inline-end:6px; background:var(--green); box-shadow:0 0 6px var(--green)}
  .dot.off{background:var(--red); box-shadow:0 0 6px var(--red)}
  .dot.warn{background:var(--gold); box-shadow:0 0 6px var(--gold)}
  /* ═══ شريط النافذة والمخاطر ═══ */
  .strip{display:flex; flex-wrap:wrap; gap:10px; margin-bottom:14px}
  .strip .box{flex:1; min-width:240px; border-radius:12px; padding:10px 14px; font-size:13px; border:1px solid var(--line); background:var(--panel)}
  .box.night{border-color:#5b4a1e; background:linear-gradient(90deg,#231c08,#1a1508); color:var(--gold)}
  .box.open{border-color:#1d4d33; background:linear-gradient(90deg,#0a2114,#081a0f); color:#7ee2a8}
  .box.risk-bad{border-color:#5b1e1e; background:linear-gradient(90deg,#210a0a,#1a0808); color:#ff9b9b}
  .box b{font-weight:700}
  /* ═══ البطاقات ═══ */
  .cards{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; margin-bottom:16px}
  .card{background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:12px 14px}
  .card .lbl{color:var(--dim); font-size:11.5px; margin-bottom:6px}
  .card .val{font-size:19px; font-weight:700; letter-spacing:.3px}
  .val.g{color:var(--green)} .val.r{color:var(--red)} .val.b{color:var(--blue)} .val.gold{color:var(--gold)}
  /* ═══ المراكز المفتوحة ═══ */
  .sec-t{font-size:15px; font-weight:700; margin:18px 0 10px; display:flex; align-items:center; gap:8px}
  .sec-t .cnt{background:var(--panel); border:1px solid var(--line); border-radius:12px; font-size:11.5px; padding:2px 10px; color:var(--dim)}
  table{width:100%; border-collapse:collapse; background:var(--panel); border:1px solid var(--line); border-radius:14px; overflow:hidden; font-size:13px}
  th{background:var(--panel2); color:var(--dim); font-weight:600; padding:9px 10px; text-align:right; font-size:12px; border-bottom:1px solid var(--line); white-space:nowrap}
  td{padding:9px 10px; border-bottom:1px solid #16203a; white-space:nowrap}
  tr:last-child td{border-bottom:none}
  .sym{font-weight:700; color:var(--cyan)}
  .side-buy{color:var(--green); font-weight:700} .side-sell{color:var(--red); font-weight:700}
  .num{font-family:Consolas,Menlo,monospace; direction:ltr; display:inline-block}
  .pill{border-radius:10px; padding:2px 8px; font-size:11px; border:1px solid var(--line)}
  .pill.ok{color:var(--green); border-color:#1d4d33} .pill.pl{color:var(--gold); border-color:#5b4a1e}
  .pill.loc{color:var(--red); border-color:#5b1e1e} .pill.none{color:var(--dim)}
  .empty{padding:22px; text-align:center; color:var(--dim); background:var(--panel); border:1px dashed var(--line); border-radius:14px}
  /* ═══ سجل الأحداث ═══ */
  .toolbar{display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:10px}
  .fbtn{background:var(--panel); color:var(--dim); border:1px solid var(--line); border-radius:20px; padding:5px 14px; cursor:pointer; font-size:12.5px; font-family:inherit}
  .fbtn:hover{color:var(--txt)} .fbtn.on{background:#1c2a4a; color:#fff; border-color:#33507f}
  .search{flex:1; min-width:180px; background:var(--panel); border:1px solid var(--line); border-radius:20px; padding:6px 14px; color:var(--txt); font-family:inherit; font-size:12.5px; outline:none}
  .search:focus{border-color:#33507f}
  #feed{display:flex; flex-direction:column; gap:7px}
  .ev{background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:9px 12px; border-inline-start:3px solid var(--dim)}
  .ev .top{display:flex; flex-wrap:wrap; gap:8px; align-items:center}
  .ev .t{color:var(--dim); font-size:11.5px; font-family:Consolas,Menlo,monospace; direction:ltr}
  .ev .k{font-size:10.5px; border-radius:8px; padding:2px 8px; font-weight:700}
  .ev .s{font-weight:700; color:var(--cyan); font-size:12.5px}
  .ev .m{flex:1; min-width:200px; font-size:13px}
  .ev .rsn{margin-top:6px; font-size:12.5px; color:var(--dim); background:var(--panel2); border-radius:8px; padding:6px 10px; border:1px solid var(--line)}
  .ev .rsn b{color:#c3d0e8; font-weight:600}
  .ev.dtl{cursor:pointer} .ev .more{display:none; margin-top:6px; font-size:12px; color:#a8b8d8; background:var(--panel2); border:1px solid var(--line); border-radius:8px; padding:8px 10px; white-space:pre-wrap}
  .ev.open .more{display:block}
  .k-دخول{color:#0a2114; background:var(--green)} .ev[data-k="دخول"]{border-inline-start-color:var(--green)}
  .k-خروج{color:#fff; background:var(--red)} .ev[data-k="خروج"]{border-inline-start-color:var(--red)}
  .k-إشارة{color:#06121f; background:var(--blue)} .ev[data-k="إشارة"]{border-inline-start-color:var(--blue)}
  .k-رفض{color:#211606; background:var(--gold)} .ev[data-k="رفض"]{border-inline-start-color:var(--gold)}
  .k-خطأ{color:#fff; background:#c0392b} .ev[data-k="خطأ"]{border-inline-start-color:#c0392b}
  .k-نظام{color:#0d1524; background:var(--dim)} .ev[data-k="نظام"]{border-inline-start-color:#3a4a6b}
  .k-دورة{color:#0d1524; background:#7f95bd} .ev[data-k="دورة"]{border-inline-start-color:#7f95bd}
  .k-نبض{color:#0d1524; background:var(--cyan)} .ev[data-k="نبض"]{border-inline-start-color:var(--cyan)}
  .k-مخاطر{color:#fff; background:#8e44ad} .ev[data-k="مخاطر"]{border-inline-start-color:#8e44ad}
  .k-أخبار{color:#0d1524; background:#e67e22} .ev[data-k="أخبار"]{border-inline-start-color:#e67e22}
  .foot{margin-top:14px; color:var(--dim); font-size:11.5px; text-align:center; line-height:1.9}
  .live{color:var(--green)}
</style>
</head>
<body>
<div class="wrap">

  <!-- شريط وضع الاتصال: يوضح هل البيانات حية من البوت أم عرض تجريبي -->
  <div class="mode" id="modeBar">
    <span id="modeTxt">⏳ جارٍ البحث عن البوت…</span>
    <span class="burl">
      عنوان البوت:
      <input id="botUrl" type="text" spellcheck="false" placeholder="http://localhost:8999">
      <button id="btnRetry">🔄 إعادة المحاولة</button>
    </span>
  </div>

  <div class="hdr">
    <h1>🎯 لوحة مراقبة القناص <small>V12 — استراتيجية HMA_DMI_MOMENTUM (ملف مستقل)</small></h1>
    <div class="chips">
      <span class="chip"><span class="dot" id="dotStatus"></span><b id="stStatus">—</b></span>
      <span class="chip">الوضع: <b id="stMode">—</b></span>
      <span class="chip">الإطار: <b id="stTf">—</b></span>
      <span class="chip">Testnet: <b id="stTestnet">—</b></span>
      <span class="chip">التشغيل منذ: <b id="stUptime">—</b></span>
      <span class="chip">آخر تحديث: <b id="stNow" class="live">—</b></span>
    </div>
  </div>

  <div class="strip">
    <div class="box" id="boxEvening">🌙 نافذة المساء: <b>—</b></div>
    <div class="box" id="boxRisk">🛡️ مدير المخاطر: <b>—</b></div>
    <div class="box" id="boxHma">🧭 الاستراتيجية: <b>—</b></div>
    <div class="box" id="boxScan">🔭 المسح: <b>—</b></div>
  </div>

  <div class="cards">
    <div class="card"><div class="lbl">💵 الرصيد المتاح</div><div class="val num" id="cBal">—</div></div>
    <div class="card"><div class="lbl">📈 PnL اليوم</div><div class="val num" id="cPnl">—</div></div>
    <div class="card"><div class="lbl">📅 صفقات اليوم</div><div class="val" id="cToday">—</div></div>
    <div class="card"><div class="lbl">🏆 فوز / خسارة (إجمالي)</div><div class="val" id="cWL">—</div></div>
    <div class="card"><div class="lbl">🔓 مفتوحة / الحد المتزامن</div><div class="val" id="cOpen">—</div></div>
    <div class="card"><div class="lbl">🔭 الكون السائل</div><div class="val" id="cUni">—</div></div>
    <div class="card"><div class="lbl">🔁 عدد الدورات</div><div class="val num" id="cCycles">—</div></div>
    <div class="card"><div class="lbl">✍️ صفقات منفذة (إجمالي)</div><div class="val" id="cExec">—</div></div>
  </div>

  <div class="sec-t">🔓 المراكز المفتوحة الآن <span class="cnt" id="posCnt">0</span></div>
  <div id="posWrap"><div class="empty">لا توجد صفقات مفتوحة حالياً</div></div>

  <div class="sec-t">📋 سجل كل الحركات — كل صغيرة وكبيرة مع السبب</div>
  <div class="toolbar">
    <button class="fbtn on" data-k="الكل">الكل</button>
    <button class="fbtn" data-k="دخول">دخول</button>
    <button class="fbtn" data-k="خروج">خروج</button>
    <button class="fbtn" data-k="إشارة">إشارات</button>
    <button class="fbtn" data-k="رفض">أسباب الرفض</button>
    <button class="fbtn" data-k="مخاطر">مخاطر</button>
    <button class="fbtn" data-k="خطأ">أخطاء</button>
    <button class="fbtn" data-k="نظام">نظام</button>
    <input class="search" id="q" type="text" placeholder="🔎 ابحث في السجل (رمز، سبب، كلمة)...">
  </div>
  <div id="feed"></div>

  <div class="foot">
    هذه هي <b>ملف اللوحة المستقل</b> — تعمل بدون بوت (عرض تجريبي) وتتحول تلقائياً إلى <span class="live">البث الحي</span> عند تشغيل البوت<br>
    البوت الكامل: ملف <span class="num">bot_HMA_النهائي.py</span> (اللوحة مدمجة داخله أيضاً على العنوان <span class="num">http://IP_الجهاز:8999</span>)<br>
    التوقيت المعروض بتوقيت ليبيا (UTC+2) | كل حدث يُكتب في ملف <span class="num">bot_events.jsonl</span> بجانب البوت للتدقيق الدائم
  </div>
</div>

<script>
/* ═══════════ أدوات مساعدة (مطابقة لصفحة البوت المدمجة) ═══════════ */
var curKind='الكل', q='';
function fmtN(x,d){ if(x===undefined||x===null||isNaN(x)) return '—'; return Number(x).toLocaleString('en-US',{minimumFractionDigits:d||0,maximumFractionDigits:(d===undefined?2:d)}); }
function sgn(x){ return (x>0?'+':'') + fmtN(x,2); }
function cls(x){ return x>0?'g':(x<0?'r':''); }
function libyaT(ts){
  try{ return new Intl.DateTimeFormat('ar-LY',{timeZone:'Africa/Tripoli',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false}).format(new Date(ts*1000)); }
  catch(e){ return new Date(ts*1000).toISOString().substr(11,8); }
}
function esc(s){ return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

/* ═══════════ العرض: الحالة العامة ═══════════ */
function render(s){
  var st=s.state||{};
  document.getElementById('stStatus').textContent = st.status||'—';
  var dot=document.getElementById('dotStatus');
  dot.className='dot' + (st.status==='يعمل'?'':(st.status?' warn':' off'));
  document.getElementById('stMode').textContent = st.mode||'—';
  document.getElementById('stTf').textContent = st.hma_timeframe||'—';
  document.getElementById('stTestnet').textContent = st.testnet? 'نعم 🧪':'لا';
  document.getElementById('stUptime').textContent = (st.uptime_h!=null? st.uptime_h+' ساعة':'—');
  document.getElementById('stNow').textContent = libyaT(s.now);

  var ev=document.getElementById('boxEvening');
  if(st.evening_block){
    if(st.evening_blocked_now){ ev.className='box night'; ev.innerHTML='🌙 حظر نافذة المساء <b>سارٍ الآن</b> — الدخول الجديد معطل ('+esc(st.evening_window||'')+'). المخارج تعمل طبيعياً.'; }
    else{ ev.className='box open'; ev.innerHTML='✅ خارج نافذة الحظر — الدخول متاح. النافذة المحظورة: <b>'+esc(st.evening_window||'')+'</b>.'; }
  } else { ev.className='box open'; ev.innerHTML='ℹ️ حظر نافذة المساء <b>معطل</b> (HMA_BLOCK_EVENING=false).'; }

  var rk=document.getElementById('boxRisk');
  if(st.risk_ok===false){ rk.className='box risk-bad'; rk.innerHTML='🛡️ مدير المخاطر: <b>يمنع الدخول الآن</b> — '+esc(st.risk_reason||''); }
  else { rk.className='box open'; rk.innerHTML='🛡️ مدير المخاطر: <b>سليم</b> — '+esc(st.risk_reason||'التداول مسموح'); }

  var hm=document.getElementById('boxHma');
  var hmaTxt = st.hma_enabled? (st.hma_live? '⚔️ تداول فعلي':'👁️ إشارات فقط') : '⏸️ معطلة';
  hm.className='box'; hm.innerHTML='🧭 HMA_DMI_MOMENTUM: <b>'+esc(hmaTxt)+'</b> | الصفقات المتزامنة القصوى: <b>'+fmtN(st.max_open_trades,0)+'</b>';

  var sc=document.getElementById('boxScan');
  var ls=st.last_hma_scan||{};
  sc.className='box';
  sc.innerHTML='🔭 آخر دفعة HMA: فحص <b>'+fmtN(ls.scanned,0)+'</b> زوج | إشارات <b>'+fmtN(ls.signals,0)+'</b> | مخارج <b>'+fmtN(ls.exits,0)+'</b> | الكون: <b>'+fmtN(st.universe_count,0)+'</b>';

  document.getElementById('cBal').textContent = '$'+fmtN(st.balance,2);
  var dp=st.daily_pnl||0;
  var pe=document.getElementById('cPnl'); pe.textContent=sgn(dp)+' $'; pe.className='val num '+cls(dp);
  document.getElementById('cToday').textContent = fmtN(st.trades_today,0);
  var wl=document.getElementById('cWL');
  wl.innerHTML='<span class="g">'+fmtN(st.wins,0)+'</span> / <span class="r">'+fmtN(st.losses,0)+'</span>';
  document.getElementById('cOpen').innerHTML = fmtN(st.open_count,0)+' <span style="color:var(--dim);font-size:13px">/ '+fmtN(st.max_open_trades,0)+'</span>';
  document.getElementById('cUni').textContent = fmtN(st.universe_count,0);
  document.getElementById('cCycles').textContent = fmtN(st.cycles,0);
  document.getElementById('cExec').textContent = fmtN(st.trades_executed,0);

  var ps=st.positions||[];
  document.getElementById('posCnt').textContent=ps.length;
  var pw=document.getElementById('posWrap');
  if(!ps.length){ pw.innerHTML='<div class="empty">لا توجد صفقات مفتوحة حالياً</div>'; }
  else{
    var h='<table><thead><tr><th>الرمز</th><th>الاتجاه</th><th>الدخول</th><th>السعر الآن</th><th>الهامش</th><th>PnL عائم</th><th>%</th><th>SL</th><th>TP1</th><th>العمر (ساعة)</th><th>ستوب المنصة</th><th>الثقة</th></tr></thead><tbody>';
    for(var i=0;i<ps.length;i++){ var p=ps[i];
      h+='<tr><td class="sym">'+esc(p.symbol)+'</td>'
        +'<td class="'+(p.side==='BUY'?'side-buy':'side-sell')+'">'+(p.side==='BUY'?'▲ شراء':'▼ بيع')+'</td>'
        +'<td class="num">'+esc(p.entry)+'</td><td class="num">'+esc(p.current)+'</td>'
        +'<td class="num">$'+fmtN(p.margin,2)+'</td>'
        +'<td class="num '+cls(p.pnl)+'">'+sgn(p.pnl)+'</td>'
        +'<td class="num '+cls(p.pnl_pct)+'">'+sgn(p.pnl_pct)+'%</td>'
        +'<td class="num">'+esc(p.sl)+'</td><td class="num">'+esc(p.tp)+'</td>'
        +'<td class="num">'+fmtN(p.age_h,1)+'</td>'
        +'<td><span class="pill '+(p.stop_state==='verified'?'ok':(p.stop_state==='placed'?'pl':(p.stop_state==='local'?'loc':'none')))+'">'+(p.stop_state==='verified'?'مؤكد ✓':(p.stop_state==='placed'?'مثبت':(p.stop_state==='local'?'مراقبة محلية':'—')))+'</span></td>'
        +'<td class="num">'+(p.score!=null? esc(p.score)+'/9':'—')+'</td></tr>';
    }
    pw.innerHTML=h+'</tbody></table>';
  }
}

/* ═══════════ العرض: سجل الأحداث ═══════════ */
function renderFeed(s){
  var evs=s.events||[];
  var f=document.getElementById('feed');
  var html='';
  for(var i=evs.length-1;i>=0;i--){
    var e=evs[i];
    var sym=e.symbol? '<span class="s">'+esc(e.symbol)+'</span>':'';
    var rsn=e.reason? '<div class="rsn"><b>السبب:</b> '+esc(e.reason)+'</div>':'';
    var d=e.detail? '<div class="more">'+esc(e.detail)+'</div>':'';
    html+='<div class="ev'+(e.detail?' dtl':'')+'" data-k="'+esc(e.kind)+'">'
        +'<div class="top"><span class="t">'+libyaT(e.t)+'</span>'
        +'<span class="k k-'+esc(e.kind)+'">'+esc(e.kind)+'</span>'+sym
        +'<span class="m">'+esc(e.msg)+'</span></div>'+rsn+d+'</div>';
  }
  f.innerHTML=html||'<div class="empty">لا أحداث بعد — أول دورة مسح قادمة</div>';
  applyFilter();
}

function applyFilter(){
  var items=document.querySelectorAll('#feed .ev');
  for(var i=0;i<items.length;i++){
    var okK=(curKind==='الكل'||items[i].getAttribute('data-k')===curKind);
    var okQ=!q||items[i].textContent.indexOf(q)>=0;
    items[i].style.display=(okK&&okQ)?'':'none';
  }
}
document.querySelectorAll('.fbtn').forEach(function(b){
  b.addEventListener('click',function(){
    document.querySelectorAll('.fbtn').forEach(function(x){x.classList.remove('on')});
    b.classList.add('on'); curKind=b.getAttribute('data-k'); applyFilter();
  });
});
document.getElementById('q').addEventListener('input',function(){ q=this.value.trim(); applyFilter(); });
document.getElementById('feed').addEventListener('click',function(ev){
  var el=ev.target.closest('.ev.dtl'); if(el) el.classList.toggle('open');
});

/* ═══════════ وضع الاتصال: بث حي أو عرض تجريبي ═══════════ */
var BOT_URL='http://localhost:8999';
try{ BOT_URL=(localStorage.getItem('botUrl')||BOT_URL).replace(/\/+$/,''); }catch(e){}
document.getElementById('botUrl').value=BOT_URL;
var mode='init';
function setMode(m){
  mode=m;
  var bar=document.getElementById('modeBar'), t=document.getElementById('modeTxt');
  if(m==='live'){ bar.className='mode live'; t.innerHTML='🟢 <b>متصل بالبوت الحي</b> — كل ما تراه هنا بيانات حقيقية لحظية من البوت على '+esc(BOT_URL); }
  else if(m==='demo'){ bar.className='mode demo'; t.innerHTML='🟡 <b>وضع العرض التجريبي</b> — لم أجد البوت على العنوان المدخل، فتعرض اللوحة بيانات مثال لتشاهد شكلها ومحتواها. شغّل البوت وستتحول تلقائياً إلى البث الحي (أو عدّل العنوان واضغط إعادة المحاولة).'; }
  else { bar.className='mode'; t.innerHTML='⏳ جارٍ البحث عن البوت على '+esc(BOT_URL)+' …'; }
}

/* ═══════════ بيانات العرض التجريبي (بنفس مفردات البوت الحقيقية) ═══════════ */
var demoEvents=[];
function T(secAgo){ return Math.floor(Date.now()/1000)-secAgo; }
function buildDemo(){
  var now=Math.floor(Date.now()/1000);
  demoEvents=[
    {t:T(5*3600+900), kind:'نظام', msg:'إقلاع البوت V12 — استراتيجية HMA_DMI_MOMENTUM فقط',
     reason:'لوحة المراقبة على المنفذ 8999 | أقصى تزامن 3 صفقات | حظر مساء 16–23 UTC مفعّل',
     detail:'الإطار: 15m | الكون: أسواق USDT-M الفوتشرز\nالرسوم: تيكر 0.05%/جانب | الهامش لكل صفقة: 25$ برافعة 10x\nالتبريد بعد كل صفقة: 15 دقيقة | ستوب زمني: 36 ساعة'},
    {t:T(5*3600+870), kind:'نظام', msg:'تم تحميل الكون السائل: 150 زوجاً (فلترة السيولة والحجم)'},
    {t:T(5*3600+600), kind:'دورة', msg:'الدورة #405 — كون 150 زوج | مفتوحة 0/3 | ✅ الدخول متاح الآن'},
    {t:T(4*3600+1800), kind:'رفض', symbol:'BNBUSDT', msg:'تكرار إشارة خلال فترة التبريد',
     reason:'آخر إشارة للرمز قبل 12 دقيقة | التبريد المطلوب 15 دقيقة'},
    {t:T(4*3600+1200), kind:'إشارة', symbol:'SOLUSDT', msg:'إشارة SELL جديدة @ 203.45',
     reason:'زناد: انعكاس هيكلي بعد اتساع DMI السلبي',
     detail:'الاتجاه 4س: هابط ✓ (EMA50 تحت EMA200)\nDMI: -DI 28.1 > +DI 12.3 | ADX 31.5\nالزخم 15م: سلبي متسارع\nالحجم: 2.4× المتوسط\nالثقة: 7/9'},
    {t:T(4*3600+1195), kind:'دخول', symbol:'SOLUSDT', msg:'تنفيذ SELL @ 203.45 | كمية 0.123 | هامش 25.00$',
     reason:'SL 209.55 | TP1 190.20 | ستوب المنصة: مؤكد ✓ | ستوب زمني 36 ساعة'},
    {t:T(3*3600+3000), kind:'خروج', symbol:'DOGEUSDT', msg:'TP1 — إغلاق كامل عند الهدف الأول',
     reason:'النتيجة +3.84 USDT (+15.4% من الهامش)', pnl:3.84},
    {t:T(3*3600+1500), kind:'رفض', symbol:'PEPEUSDT', msg:'قوة الإشارة أقل من الحد',
     reason:'الثقة 5/9 < الحد المطلوب 6 | ADX 18.4 تحت 20'},
    {t:T(2*3600+2400), kind:'مخاطر', symbol:'ARBUSDT', msg:'تعذر تثبيت ستوب المنصة — تحول إلى مراقبة محلية',
     reason:'إعادة المحاولة تلقائياً كل دورة حتى التثبيت'},
    {t:T(2*3600+900), kind:'إشارة', symbol:'ARBUSDT', msg:'إشارة BUY جديدة @ 0.8421',
     reason:'زناد: استئناف زخم مع دعم DMI الإيجابي',
     detail:'الاتجاه 4س: صاعد ✓ (EMA50 فوق EMA200)\nDMI: +DI 24.8 > -DI 13.9 | ADX 26.2\nالزخم 15م: إيجابي متسارع\nالحجم: 1.9× المتوسط\nالثقة: 6/9'},
    {t:T(2*3600+890), kind:'دخول', symbol:'ARBUSDT', msg:'تنفيذ BUY @ 0.8421 | كمية 29.70 | هامش 25.00$',
     reason:'SL 0.8150 | TP1 0.9020 | ستوب المنصة: مثبت | ستوب زمني 36 ساعة'},
    {t:T(3600+1800), kind:'رفض', symbol:'XRPUSDT', msg:'🌙 نافذة المساء 16–23 UTC — الدخول الجديد محظور',
     reason:'المحاولة الساعة 18:40 UTC | المخارج تُدار طبيعياً'},
    {t:T(3600+600), kind:'نبض', msg:'القلب ينبض — آخر مسح 150 زوجاً | بدون أخطاء'},
    {t:T(1800), kind:'دورة', msg:'الدورة #410 — كون 150 زوج | مفتوحة 1/3 | ✅ الدخول متاح الآن'},
    {t:T(600), kind:'خروج', symbol:'LINKUSDT', msg:'ستوب خسارة — خرج عند الوقف',
     reason:'النتيجة -2.61 USDT (-10.4% من الهامش)', pnl:-2.61},
    {t:T(240), kind:'نظام', msg:'تحديث الكون: 153 → 150 زوجاً (إسقاط 3 أزواج لضعف السيولة)'},
    {t:T(90), kind:'دورة', msg:'الدورة #412 — كون 150 زوج | مفتوحة 2/3 | ✅ الدخول متاح الآن'}
  ];
}
var demoTickEvents=[
  {kind:'نبض', msg:'القلب ينبض — آخر مسح 150 زوجاً | بدون أخطاء | المراكز 2/3'},
  {kind:'رفض', symbol:'WIFUSDT', msg:'الرمز خارج الكون السائل', reason:'حجم 24 ساعة 4.1م$ أقل من الحد المطلوب'},
  {kind:'دورة', msg:'الدورة #413 — كون 150 زوج | مفتوحة 2/3 | ✅ الدخول متاح الآن'},
  {kind:'رفض', symbol:'AVAXUSDT', msg:'إشارة BUY ضد الاتجاه العام 4س', reason:'بوابة EMA 4س تمنع الشراء عكس الاتجاه'},
  {kind:'نظام', msg:'تحديث الكون: 150 → 151 زوجاً (إضافة زوج جديد سائل)'},
  {kind:'نبض', msg:'القلب ينبض — PnL اليوم +38.42$ | لا إنذارات | ستوبات المنصة كلها مثبتة'}
];
var demoIdx=0, demoTimer=null;
function startDemo(){
  setMode('demo');
  if(!demoEvents.length) buildDemo();
  var st={status:'يعمل', mode:'تداول فعلي (HMA فقط) — بيانات تجريبية', hma_timeframe:'15m',
          testnet:false, uptime_h:5.2,
          evening_block:true, evening_blocked_now:false, evening_window:'16:00 ← 23:00 UTC',
          risk_ok:true, risk_reason:'جميع الحدود ضمن النطاق',
          hma_enabled:true, hma_live:true, max_open_trades:3,
          last_hma_scan:{scanned:150, signals:2, exits:1},
          universe_count:150, balance:1042.87, daily_pnl:38.42,
          trades_today:6, wins:34, losses:27, open_count:2, cycles:412, trades_executed:61,
          positions:[
            {symbol:'SOLUSDT', side:'SELL', entry:'203.45', current:'199.12', margin:25.00, pnl:4.31, pnl_pct:17.2, sl:'209.55', tp:'190.20', age_h:3.4, stop_state:'verified', score:7},
            {symbol:'ARBUSDT', side:'BUY', entry:'0.8421', current:'0.8397', margin:25.00, pnl:-0.71, pnl_pct:-2.9, sl:'0.8150', tp:'0.9020', age_h:1.2, stop_state:'placed', score:6}
          ]};
  render({state:st, now:Math.floor(Date.now()/1000)});
  renderFeed({events:demoEvents});
  if(demoTimer) clearInterval(demoTimer);
  demoTimer=setInterval(function(){
    var e=demoTickEvents[demoIdx%demoTickEvents.length]; demoIdx++;
    var c={}; for(var k in e) c[k]=e[k];
    c.t=Math.floor(Date.now()/1000);
    demoEvents.push(c);
    if(demoEvents.length>400) demoEvents.shift();
    renderFeed({events:demoEvents});
  },7000);
}

/* ═══════════ الاتصال بالبوت الحي ═══════════ */
async function tryLive(){
  try{
    var opt={cache:'no-store'};
    try{ opt.signal=AbortSignal.timeout(2500); }catch(e){}
    var r=await fetch(BOT_URL+'/api/state?limit=400',opt);
    var s=await r.json();
    if(demoTimer){ clearInterval(demoTimer); demoTimer=null; }
    setMode('live');
    render(s); renderFeed(s);
    return true;
  }catch(e){ return false; }
}
async function tick(){
  var ok=await tryLive();
  if(!ok && mode!=='demo') startDemo();
}
document.getElementById('btnRetry').addEventListener('click',function(){
  BOT_URL=(document.getElementById('botUrl').value.trim()||'http://localhost:8999').replace(/\/+$/,'');
  try{ localStorage.setItem('botUrl',BOT_URL); }catch(e){}
  demoEvents=[]; demoIdx=0;
  setMode('init'); tick();
});
document.getElementById('botUrl').addEventListener('keydown',function(e){
  if(e.key==='Enter') document.getElementById('btnRetry').click();
});
tick(); setInterval(tick,3000);
</script>
</body>
</html>
