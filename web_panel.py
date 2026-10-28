"""
🖥️ Sniper Panel V11.1 — Rebuild Edition (متوافقة 100% مع البوت V11.1)
✅ دخول مباشر بلا مفتاح (الحماية = سرية رابط Railway)
✅ عرض كل إجراء يقوم به البوت: إشارات، تنفيذ، رفض بأسبابه، إغلاقات
✅ لا تعليق: مهلة 6 ثوان لكل طلب + فشل مرئي
✅ جوهر هذه النسخة — بلا أي مرجع للمطوّر التكيفي أو المحركات القديمة:
   - 🎯 تبويب SBR: كل عتبات الجودة تُعدّل لحظياً وتُحفظ في القاعدة
     (سيولة، تغير موقّع، ATR، حجم الاختراق، عمر الإعداد، R:R، TP1% من الهامش...)
   - 🧭 تبويب الاستراتيجيات: مقارنة SBR مقابل HMA_DMI_MOMENTUM على الفترة
     نفسها (نسبة فوز، صافي ربح، متوسط ربح/خسارة، Profit Factor، أقصى تراجع
     حسب تعريفات موثقة)، حالة كل استراتيجية، آخر إشارة، توزيع النتائج حسب
     الرمز، أسباب الرفض حسب الاستراتيجية ومصدرها (استراتيجية/مخاطر/تنفيذ)،
     + إعدادات HMA كاملة تُعدّل لحظياً وتُحفظ في القاعدة.
   - 📡 سجل الإشارات + 🚫 سجل أسباب الرفض — من قاعدة البيانات فعلياً ومع
     عمود الاستراتيجية المالك
   - 🛡️ حالة وقف الخسارة الفعلية لكل صفقة: مؤكد على المنصة ✓ / مثبّت ⏳ /
     مراقبة محلية 🛡️ + زر إعادة محاولة فورية
   - 📊 TP1 في الصفقات (هدف عائد الهامش — إغلاق 100%) — لا TP2 ولا جني جزئي
   - 📰 بطاقة تحكم فلتر الأخبار كما هي
   - 🛡️ حالة مدير المخاطر الحقيقية (حالتها محفوظة في القاعدة)
✅ كل الأوقات بتوقيت ليبيا (UTC+2 ثابت) بنظام 12 ساعة صباحاً/مساءً
"""

import os
import json
import time
import asyncio
import aiosqlite
from aiohttp import web

HMA_STRATEGY_NAME = 'HMA_DMI_MOMENTUM'   # 🧭 ثابت موحّد مع البوت (معرّف محلياً لضمان استقلالية اللوحة)
HMA_SYMBOL_BLACKLIST = ('ETHUSDT', 'BNBUSDT', 'AVAXUSDT')   # ⛔ فلتر V11.3 (نسخة عرض احتياطية — المصدر bot.py)

PANEL_START = time.time()


# ─── ⏰ توقيت ليبيا (UTC+2 ثابت) + نظام 12 ساعة صباحاً/مساءً ───
def libya_time_str(ts=None, seconds=False):
    """سلسلة زمنية للعرض بتوقيت ليبيا — بديل time.localtime (UTC على السيرفر)."""
    try:
        from datetime import datetime, timezone, timedelta
        ts = time.time() if ts is None else float(ts)
        dt = datetime.fromtimestamp(ts, timezone(timedelta(hours=2)))
    except Exception:
        return time.strftime('%m-%d %H:%M')
    fmt = '%m-%d %I:%M:%S' if seconds else '%m-%d %I:%M'
    return dt.strftime(fmt) + (' صباحاً' if dt.hour < 12 else ' مساءً')


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
<title>🎯 القناص V11.1 — استراتيجيتان</title>
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
main{position:relative;z-index:1;max-width:1400px;margin:0 auto;padding:16px}
.tabs{display:flex;gap:5px;margin-bottom:18px;border-bottom:1px solid var(--bord);overflow-x:auto;padding-bottom:2px}
.tab{padding:12px 18px;border:none;background:transparent;color:var(--sub);cursor:pointer;font-weight:600;
font-size:14px;border-radius:10px 10px 0 0;transition:.2s;white-space:nowrap;position:relative}
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
.card .v{font-size:30px;font-weight:800;margin:8px 0 4px}
.card .s{font-size:11px;color:var(--sub);padding-top:8px;border-top:1px solid var(--bord);margin-top:8px}
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
.empty{text-align:center;color:var(--sub);padding:30px;font-size:14px}
.feed{display:flex;flex-direction:column;gap:9px;max-height:560px;overflow-y:auto;padding-left:4px}
.nt{display:flex;gap:12px;padding:13px;background:var(--bg2);border-radius:12px;border-right:4px solid transparent;animation:fi .3s}
.nt.trade{border-right-color:var(--green)}.nt.signal{border-right-color:var(--blue)}
.nt.close{border-right-color:var(--purple)}.nt.error{border-right-color:var(--red)}
.nt.system{border-right-color:var(--orange)}.nt.info{border-right-color:var(--sub)}
.nt-ic{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0}
.nt.trade .nt-ic{background:rgba(0,212,170,.15)}.nt.signal .nt-ic{background:rgba(59,130,246,.15)}
.nt.close .nt-ic{background:rgba(139,92,246,.15)}.nt.error .nt-ic{background:rgba(239,68,68,.15)}
.nt.system .nt-ic{background:rgba(249,115,22,.15)}.nt.info .nt-ic{background:rgba(148,163,184,.15)}
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
.kv{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:14px}
.kv:last-child{border-bottom:none}
.kv b{color:var(--green)}
.foot{text-align:center;padding:18px;color:var(--sub);font-size:12px;border-top:1px solid var(--bord);margin-top:18px}
.arow{display:flex;gap:10px;flex-wrap:wrap}
.sbar{background:var(--bg2);border:1px solid var(--bord);border-radius:12px;padding:10px 16px;
margin-bottom:16px;display:flex;align-items:center;gap:10px;font-size:13px;color:var(--sub)}
.sbar b{color:var(--green)}
@media(max-width:768px){.card .v{font-size:24px}.tab{padding:10px 12px;font-size:12px}}
</style>
</head>
<body>
<div class="bg"></div>

<header class="hd"><div class="hd-in">
  <div class="logo">
    <div class="logo-ic">🎯</div>
    <div><h1>القناص الأسطوري V11.3 — SBR + HMA_DMI_MOMENTUM</h1><span id="modeTxt">شاشة العمليات — استراتيجيتان مستقلتان</span></div>
  </div>
  <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
    <div class="badge" id="liveB"><span class="dot"></span><span id="liveT">البوت حي ✓</span></div>
    <button class="act btn-g" onclick="loadAll()">🔄 تحديث</button>
  </div>
</div></header>

<main>
<div class="sbar">⏱️ آخر تحديث: <b id="lastUpd">الآن</b> • تحديث تلقائي كل 10 ثوانٍ</div>

<div id="keyBanner" style="display:none;background:rgba(239,68,68,.10);border:1px solid rgba(239,68,68,.45);border-radius:12px;padding:14px 16px;margin:0 0 14px;color:#fca5a5;font-size:12.5px;line-height:2">
  <b style="font-size:14.5px">🚨 Binance يرفض مفاتيح API (خطأ -2015) — لهذا يظهر الرصيد $0.00</b><br>
  المفاتيح الحالية غير صالحة على الفوتشرز التجريبي. المفاتيح يجب أن تكون من <b style="color:#fff">testnet.binancefuture.com</b> (الفوتشرز التجريبي) وليس من موقع بينانس الحقيقي أو موقع السبوت التجريبي.<br>
  <b style="color:#fecaca">الحل:</b> افتح testnet.binancefuture.com ← تسجيل دخول ← أيقونة الملف الشخصي ← API Key ← Create HMAC_SHA256 ← انسخ المفتاح والسر ← Railway Variables ← إعادة نشر.
</div>

<div class="tabs">
  <button class="tab act" onclick="sw('overview',this)">📊 نظرة عامة</button>
  <button class="tab" onclick="sw('trades',this)">📂 الصفقات</button>
  <button class="tab" onclick="sw('signals',this)">📡 الإشارات والرفض</button>
  <button class="tab" onclick="sw('notifications',this)">🔔 الإشعارات <span id="nCount" class="tag ok" style="padding:1px 7px;font-size:10px">0</span></button>
  <button class="tab" onclick="sw('performance',this)">📅 الأداء اليومي</button>
  <button class="tab" onclick="sw('sbr',this)">🎯 إعدادات SBR</button>
  <button class="tab" onclick="sw('strategies',this)">🧭 الاستراتيجيات</button>
  <button class="tab" onclick="sw('risk',this)">🛡️ المخاطر</button>
  <button class="tab" onclick="sw('system',this)">⚙️ النظام</button>
</div>

<!-- نظرة عامة -->
<div class="tc act" id="t-overview">
  <div class="grid">
    <div class="card g"><div class="l">💵 الرصيد</div><div class="v" id="balance">$0</div><div class="s" id="modeSub">—</div></div>
    <div class="card b"><div class="l">📈 ربح اليوم</div><div class="v" id="dayPnl">$0</div><div class="s" id="dayWl">—</div></div>
    <div class="card p"><div class="l">🏆 نسبة الفوز</div><div class="v" id="wrAll">—</div><div class="s" id="allWl">—</div></div>
    <div class="card o"><div class="l">📂 مفتوحة</div><div class="v" id="openC">0</div><div class="s" id="scanT">—</div></div>
    <div class="card y"><div class="l">🎯 وضع SBR-1</div><div class="v" id="sbrMode">—</div><div class="s" id="sbrDesc">—</div></div>
  </div>
  <div class="grid" style="grid-template-columns:2fr 1fr">
    <div class="sec"><h3>📂 الصفقات المفتوحة</h3><div id="openBox"></div></div>
    <div class="sec"><h3>🛡️ الحمايات</h3><div class="hg" id="healthBox">—</div></div>
  </div>
  <div class="sec"><h3>🔔 آخر الأحداث</h3><div class="feed" id="liveFeed" style="max-height:300px"></div></div>
</div>

<!-- الصفقات -->
<div class="tc" id="t-trades">
  <div class="sec"><h3>📂 المفتوحة الآن — TP1 = إغلاق كامل عند اللمس</h3><div id="openBox2"></div></div>
  <div class="sec"><h3>🏁 المغلقة</h3><div id="closedBox"></div></div>
</div>

<!-- الإشارات والرفض -->
<div class="tc" id="t-signals">
  <div class="grid">
    <div class="card b"><div class="l">📡 إشارات مكتشفة</div><div class="v" id="sgTotal">0</div><div class="s">إجمالي ما كشفه القناص</div></div>
    <div class="card g"><div class="l">✅ صفقات منفذة</div><div class="v" id="sgExec">0</div><div class="s" id="sgExecS">—</div></div>
    <div class="card o"><div class="l">🚫 مرفوضة (جودة)</div><div class="v" id="sgRejQ">0</div><div class="s">فشل شرط SBR أو فلاتر الجودة</div></div>
    <div class="card r"><div class="l">⏳ صُدّت بصفقة مفتوحة</div><div class="v" id="sgRejO">0</div><div class="s">بلا طابور — يُعاد التحليل بعد الإغلاق</div></div>
  </div>
  <div class="sec"><h3>📡 سجل الإشارات</h3><div id="sigBox"></div></div>
  <div class="sec"><h3>🚫 أسباب رفض حديثة (من قاعدة البيانات)</h3><div id="rejBox"></div></div>
</div>

<!-- الإشعارات -->
<div class="tc" id="t-notifications">
  <div class="sec"><h3>🔔 كل ما يقوم به البوت</h3><div class="feed" id="notifFeed"></div></div>
</div>

<!-- الأداء اليومي -->
<div class="tc" id="t-performance">
  <div class="sec"><h3>📅 اليوم الحالي</h3><div id="todayBox">—</div></div>
  <div class="sec"><h3>🗓️ آخر 14 يوماً</h3><div id="daysBox">—</div></div>
  <div class="sec"><h3>🏆 الإجماليات عبر التاريخ</h3><div id="aggBox">—</div></div>
</div>

<!-- إعدادات SBR -->
<div class="tc" id="t-sbr">
  <div class="grid" style="grid-template-columns:1fr 1fr 1fr">
    <div class="card b"><div class="l">🔭 حجم الكون السائل</div><div class="v" id="scanUniverseC">—</div><div class="s" id="scanUniverseS">أزواج فوق حد السيولة فقط</div></div>
    <div class="card g"><div class="l">📡 الدفعة الأخيرة</div><div class="v" id="scanLastBatch">—</div><div class="s" id="scanLastS">—</div></div>
    <div class="card o"><div class="l">🎯 إشارات آخر دورة</div><div class="v" id="scanLastSig">—</div><div class="s" id="scanCursorS">—</div></div>
  </div>
  <div class="sec"><h3>🎯 عتبات جودة SBR-1 (تُطبّق لحظياً وتُحفظ في القاعدة)</h3>
    <div id="sbrSt">—</div>
    <div class="arow" style="margin-top:12px">
      <button class="act btn-g" onclick="sbrSave()">💾 حفظ إعدادات SBR</button>
      <button class="act btn-s" onclick="scanNow()">🔍 مسح فوري الآن</button>
    </div>
    <p style="color:var(--sub);font-size:11px;margin-top:10px;line-height:1.7">
    🎯 سلسلة القبول: سيولة 24س ← مناطق من شموع ساعة مغلقة ← اختراق بإغلاق ساعة خارج الحافة بحجم قوي
    ← تأكيد إغلاق 15د ← إعادة اختبار ورفض سعري واضح ← R:R مجدٍ ← تحقق لحظي عند التنفيذ.<br>
    ⚠️ لا يوجد أي تخفيف تلقائي للعتبات — كل قيمة هنا نهائية حتى تغيّرها أنت. القيم الأولية قيم اختبار مقترحة وليست ضماناً للربحية.<br>
    📌 أولوية المصادر: القاعدة هي المرجع بعد أول تشغيل (تعديل اللوحة يتقدم ويُحفظ).
    متغيرات Railway المعدّلة لاحقاً لا تُطبّق تلقائياً — تعارضها يظهر أعلى الجدول مع زر استيراد صريح.<br>
    🧾 نتائج الصفقات تعرض مصدرها: «Binance مؤكد ✓» (محقق + رسوم + تمويل) أو «تقديري ⚠️» عند تعذر جلب بيانات التنفيذ.</p>
  </div>
</div>

<!-- الاستراتيجيات: إدارة ومقارنة -->
<div class="tc" id="t-strategies">
  <div class="grid" style="grid-template-columns:1fr 1fr">
    <div class="sec"><h3>🧭 مقارنة أداء الاستراتيجيات — نفس الفترة (كل التاريخ المتاح)</h3>
      <div id="stratCompare">—</div>
      <p style="color:var(--sub);font-size:11px;margin-top:10px;line-height:1.7">
      📐 تعريفات الحساب (موثقة — بلا أرقام مضللة):
      نسبة الفوز = الرابحة ÷ (الرابحة + الخاسرة) من الصفقات المغلقة ذات النتيجة المؤكدة (المحايدة مستثناة).<br>
      صافي النتيجة = مجموع نتائج الصفقات المغلقة المسجلة (مؤكدة من Binance أو تقديرية موسومة).<br>
      متوسط الربح/الخسارة من الصفقات الرابحة/الخاسرة فقط. Profit Factor = مجموع أرباح الرابحين ÷ القيمة المطلقة لمجموع خسائر الخاسرين (يظهر «—» عند غياب الخسائر أو البيانات).<br>
      أقصى تراجع = أقصى هبوط لمنحنى الأرباح المتراكم (ترتيب زمني للصفقات المغلقة) عن قمته — يحتاج صفقتين مغلقتين فأكثر وإلا «—».<br>
      📌 صفقات مركز مُتبنّى تُنسب لـ UNKNOWN (مصدر غير معروف) ولا تُخلط مع الاستراتيجيتين.</p>
    </div>
    <div class="sec"><h3>🧭 حالة الاستراتيجيات الآن</h3>
      <div id="stratStatus">—</div>
      <div class="arow" style="margin-top:12px">
        <button class="act btn-g" id="hmaBtn" onclick="hmaToggle()">🧭 تفعيل استراتيجية HMA</button>
        <button class="act btn-g" id="hmaLiveBtn" onclick="hmaLiveToggle()">⚔️ تفعيل تداول HMA</button>
      </div>
    </div>
  </div>
  <div class="sec"><h3>🧭 آخر الصفقات المغلقة مع مصدر كل صفقة</h3><div id="stratTrades">—</div></div>
  <div class="sec"><h3>🚫 أسباب الرفض حسب الاستراتيجية (آخر 7 أيام) — استراتيجية / مخاطر / أخبار / تنفيذ</h3><div id="stratRej">—</div></div>
  <div class="sec"><h3>🧭 إعدادات HMA_DMI_MOMENTUM (تُطبّق لحظياً وتُحفظ في القاعدة)</h3>
    <div id="hmaSt">—</div>
    <div class="arow" style="margin-top:12px">
      <button class="act btn-g" onclick="hmaSave()">💾 حفظ إعدادات HMA</button>
    </div>
    <p style="color:var(--sub);font-size:11px;margin-top:10px;line-height:1.7">
    🧭 سلسلة القبول (V11.1 — إعادة الضبط المُتحقق عليها): آلة حالات NEUTRAL/BULL/BEAR على شموع ساعة مغلقة (تبدّل يتطلب 3 شموع مؤكدة + تبريد 3 شموع + انقلاب مباشر ≥ 0.6×ATR)
    ← بوابة اتجاهية ADX-14 ≥ 20 (استبعاد العرضي) ← تأكيد زخم ≥ 2 من 3 ← زناد HMA (استعادة سريعة أو ارتداد من البطيئة)
    ← قوة ≥ 24/100 وثقة ≥ 5/9 ← استثناء هيكلي محدود (كسر قمة/قاع مؤكد بعمق 0.6×ATR + ADX ≥ 18 — لا يتجاوز آلة الحالات ولا التبريد ولا المخاطر).<br>
    🧮 القوة (0-100) = HMA 20 + DMI/ADX 20 + زخم 15 + ER 10 + Supertrend 15 + بنية مؤكدة 20.
    الثقة (0-9) = عدد التأكيدات المستقلة المحققة (EMA يُحتسب فقط عند تفعيل الفلتر).<br>
    ⚠️ الشموع مغلقة فقط، والقمم والقيعان تُستخدم بعد تأكيدها فقط (تأخير 2 شمعة موثق) — لا إعادة رسم ولا بيانات مستقبلية.<br>
    📌 أولوية المصادر مثل SBR: القاعدة هي المرجع بعد أول تشغيل — تعارض متغيرات Railway يُعرض مع التعديل من اللوحة.</p>
  </div>
</div>

<!-- المخاطر -->
<div class="tc" id="t-risk">
  <div class="grid">
    <div class="card g"><div class="l">🛡️ حالة التداول</div><div class="v" id="riskStatus">—</div><div class="s" id="riskReason">—</div></div>
    <div class="card o"><div class="l">❌ خسائر متتالية</div><div class="v" id="consLosses">0</div><div class="s" id="consLossesS">الحد الأقصى: 3 (يوقف 4 ساعات)</div></div>
    <div class="card r"><div class="l">📊 خسائر اليوم</div><div class="v" id="dayLosses">0</div><div class="s" id="dayLossesS">الحد اليومي: 3 (يوقف بقية اليوم)</div></div>
    <div class="card b"><div class="l">💰 نتيجة اليوم</div><div class="v" id="dayPnlRisk">$0</div><div class="s" id="dayPnlRiskS">حد السحب اليومي: 5% من الرصيد المرجعي</div></div>
  </div>
  <div class="sec"><h3>🛡️ كيف يعمل مدير المخاطر</h3>
    <div class="kv"><span>3 خسائر متتالية</span><b>إيقاف التداول 4 ساعات</b></div>
    <div class="kv"><span>3 خسائر في اليوم</span><b>إيقاف بقية اليوم</b></div>
    <div class="kv"><span>سحب يومي 5% من الرصيد المرجعي</span><b>إيقاف بقية اليوم</b></div>
    <div class="kv"><span>حفظ الحالة</span><b>في القاعدة — إعادة تشغيل البوت لا تصفّر العدّادات</b></div>
    <div class="kv"><span>الإشارة المرفوضة بالمخاطر</span><b>تُسجَّل سببها بوضوح — ليست خطأ في SBR</b></div>
  </div>
</div>

<!-- النظام -->
<div class="tc" id="t-system">
  <div class="grid" style="grid-template-columns:1fr 1fr">
    <div class="sec"><h3>⚙️ الإعدادات الحية</h3><div id="setBox">—</div></div>
    <div>
      <div class="sec"><h3>🚨 الأخطاء</h3><div id="errBox">—</div></div>
      <div class="sec"><h3>📰 فلتر الأخبار — تحكم مباشر</h3>
        <div id="newsBox">—</div>
        <div class="arow" style="margin-top:12px">
          <button class="act btn-s" onclick="newsToggle()">📰 تفعيل/تعطيل</button>
          <button class="act btn-s" onclick="newsRefresh()">🔄 تحديث التقويم</button>
          <button class="act btn-g" onclick="newsSave()">💾 حفظ الإعدادات</button>
        </div>
      </div>
      <div class="sec"><h3>⚡ طوارئ</h3>
        <div class="arow">
          <button class="act btn-s" id="pauseBtn" onclick="togglePause()">⏸️ إيقاف مؤقت</button>
          <button class="act btn-r" onclick="closeAll()">🛑 إغلاق الكل</button>
        </div>
        <div class="arow" style="margin-top:10px">
          <button class="act btn-g" id="sbrBtn" onclick="sbrToggle()">🎯 تفعيل تداول SBR-1</button>
        </div>
        <div class="arow" style="margin-top:10px">
          <button class="act" style="width:100%;background:rgba(234,179,8,.12);color:var(--yellow);border:1px solid rgba(234,179,8,.4)" onclick="resetAll()">🧹 إعادة ضبط شامل — مسح كل البيانات والسجلات</button>
        </div>
        <p style="color:var(--sub);font-size:11px;margin-top:10px;line-height:1.6">
        ⚠️ الحماية عبر سرية الرابط — لا تشاركه!<br>
        حالة كل ستوب تُعرض في تبويب الصفقات — زر 🔁 يعيد المحاولة فوراً.<br>
        🧪 Testnet مفروض من متغير TESTNET — لا مسار للتداول الحقيقي من اللوحة.</p>
      </div>
    </div>
  </div>
</div>

<div class="foot">🎯 القناص الأسطوري V11.3 — SBR + HMA_DMI_MOMENTUM | اعتمادان مُتحقق عليهما على نافذتين (S-W14 + بوابة 4س) | TP1 = عائد الهامش وإغلاق كامل | ستوب حقيقي + مدير مخاطر مشترك محفوظ | الحماية عبر سرية الرابط</div>
</main>

<script>
let lastNid = 0;
let timer = null;

async function api(path){
  const c = new AbortController();
  const t = setTimeout(()=>c.abort(), 6000);
  try{
    const res = await fetch(path, {signal:c.signal, cache:'no-store'});
    if(!res.ok) throw new Error('HTTP ' + res.status);
    return await res.json();
  }finally{ clearTimeout(t); }
}
function sw(name, el){
  document.querySelectorAll('.tc').forEach(x=>x.classList.remove('act'));
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('act'));
  document.getElementById('t-'+name).classList.add('act');
  el.classList.add('act');
}
function mo(v){return (v>=0?'+':'') + '$' + Math.abs(v).toFixed(2)}
function sg(v,d){d=d||1;return (v>=0?'+':'') + v.toFixed(d)}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')}

const KM = {trade:['trade','🟢'],signal:['signal','🎯'],close:['close','🏁'],
error:['error','🚨'],system:['system','⚙️'],info:['info','ℹ️']};

async function loadAll(){
  const ov = await api('/api/overview');
  const kb = document.getElementById('keyBanner');
  if(kb) kb.style.display = ov.api_rejected ? 'block' : 'none';

  document.getElementById('lastUpd').textContent =
    new Date().toLocaleTimeString('ar',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
  document.getElementById('balance').textContent = '$' + (+ov.balance).toFixed(2);
  const mode = ov.trade_enabled ? (ov.testnet ? '⚔️ تداول تجريبي 🧪' : '⚔️ تداول') : '👁️ مراقبة';
  document.getElementById('modeTxt').textContent = mode + ' • SBR-Only V10.0';
  document.getElementById('modeSub').textContent = ov.leverage+'x • هامش $'+ov.trade_size
    + ' • TP1 = '+(ov.sbr?ov.sbr.tp1_return_pct:20)+'% من الهامش';

  const dp = ov.today ? ov.today.pnl : 0;
  const dEl = document.getElementById('dayPnl');
  dEl.textContent = mo(dp); dEl.className = 'v ' + (dp>=0?'pos':'neg');
  document.getElementById('dayWl').textContent = ov.today ? (ov.today.wins+'W / '+ov.today.losses+'L') : '—';

  const tot = ov.stats.wins + ov.stats.losses;
  document.getElementById('wrAll').textContent = tot ? Math.round(ov.stats.wins/tot*100)+'%' : '—';
  document.getElementById('allWl').textContent = ov.stats.wins+'W / '+ov.stats.losses+'L';
  document.getElementById('openC').textContent = ov.open_trades;
  document.getElementById('scanT').textContent = 'دورات: '+ov.scans+' • كون: '+((ov.scan&&ov.scan.universe_count)||0)+' زوج';
  document.getElementById('sbrMode').textContent = ov.sbr && ov.sbr.live ? '⚔️ تداول' : '👁️ إشارات';
  document.getElementById('sbrDesc').textContent = ov.sbr ? ov.sbr.describe : '—';

  const lv = ov.price_age < 120;
  document.getElementById('liveB').className = 'badge' + (lv?'':' off');
  document.getElementById('liveT').textContent = lv ? 'البوت حي ✓' : 'توقف الأسعار!';

  const sh = ov.stop_health || {total:0, verified:0, local:0, failed:[]};
  let stopHlTxt, stopHlLv;
  if(!sh.total){ stopHlTxt='لا مراكز مفتوحة'; stopHlLv='ok'; }
  else if(sh.failed && sh.failed.length){ stopHlTxt='⚠️ مراقبة محلية: '+sh.failed.map(f=>f.symbol).join('، ')+' — زر 🔁 في تبويب الصفقات'; stopHlLv='warn'; }
  else if(sh.verified===sh.total){ stopHlTxt='ستوبات المنصة مؤكدة ✓ ('+sh.verified+'/'+sh.total+')'; stopHlLv='ok'; }
  else if((sh.verified||0)+(sh.local||0)===sh.total){ stopHlTxt='محمية: '+(sh.verified||0)+' منصة ✓ + '+(sh.local||0)+' محلي 🛡️'; stopHlLv='ok'; }
  else { stopHlTxt='قيد التثبيت والتأكيد... ('+((sh.verified||0)+(sh.local||0))+'/'+sh.total+')'; stopHlLv='warn'; }

  const nw = ov.news || {};
  let newsTxt, newsLv;
  if(nw.enabled){
    if(nw.blocked_now){ newsTxt='🔇 كتم نشط — '+(nw.reason||''); newsLv='warn'; }
    else if(nw.next_event){ newsTxt='مفعّل 📰 — القادم: '+esc(nw.next_event.title)+' بعد '+nw.next_event.in_min+' د'; newsLv='ok'; }
    else if(nw.calendar_updated){ newsTxt='مفعّل 📰 — لا أحداث مؤثرة قريبة'; newsLv='ok'; }
    else { newsTxt='مفعّل 📰 — بانتظار جلب التقويم...'; newsLv='warn'; }
  } else { newsTxt='معطل — فعّله من ⚙️ النظام'; newsLv='warn'; }

  const risk = ov.risk || {};
  document.getElementById('healthBox').innerHTML = [
    ['تدفق الأسعار', lv ? 'متصل ✓' : 'متوقف '+ov.price_age+'ث', lv?'ok':'bad'],
    ['ستوبات الحماية', stopHlTxt, stopHlLv],
    ['الرصيد', '$'+(+ov.balance).toFixed(2), ov.balance>=ov.trade_size?'ok':'warn'],
    ['الوضع', mode, ov.trade_enabled?'ok':'warn'],
    ['فلتر الأخبار', newsTxt, newsLv],
    ['مدير المخاطر', risk.can_trade ? '✅ مسموح' : '🛑 '+(risk.reason||'ممنوع'), risk.can_trade?'ok':'bad'],
  ].map(h=>'<div class="hi"><div class="hd2 '+h[2]+'"></div><div><div class="hn">'+h[0]+'</div><div class="hs">'+h[1]+'</div></div></div>').join('');

  const tr = await api('/api/trades');
  renderOpen(tr,'openBox'); renderOpen(tr,'openBox2');

  const cl = await api('/api/closed');
  const cb = document.getElementById('closedBox');
  if(!cl.length){ cb.innerHTML = '<div class="empty">لا صفقات مغلقة بعد</div>'; }
  else{
    let h = '<table><tr><th>الوقت</th><th>الزوج</th><th>اتجاه</th><th>النتيجة</th><th>المصدر</th><th>جودة</th><th>الاستراتيجية</th></tr>';
    cl.forEach(c=>{
      const srcTag = c.pnl_source==='binance' ? '<span class="tag ok">Binance مؤكد ✓</span>'
        : c.pnl_source==='estimated' ? '<span class="tag warn">تقديري ⚠️</span>' : '—';
      const qTag = c.strategy==='HMA_DMI_MOMENTUM'
        ? (c.score?('ثقة '+c.score+'/9'):'—')
        : (c.score?c.score+'/8':'—');
      h += '<tr><td>'+c.time+'</td><td><b>'+c.symbol+'</b></td>'
        + '<td><span class="tag '+(c.direction==='BUY'?'buy':'sell')+'">'+(c.direction==='BUY'?'شراء':'بيع')+'</span></td>'
        + '<td class="'+(c.pnl>=0?'pos':'neg')+'"><b>'+mo(c.pnl)+'</b> ('+sg(c.pnl_pct)+'%)</td>'
        + '<td>'+srcTag+'</td>'
        + '<td>'+qTag+'</td>'
        + '<td><span class="tag info">'+esc(c.strategy||'SBR')+'</span></td></tr>';
    });
    cb.innerHTML = h + '</table>';
  }

  const sig = await api('/api/signals');
  const sb = document.getElementById('sigBox');
  if(!sig.length){ sb.innerHTML = '<div class="empty">القناص يراقب السوق — لا إشارات بعد</div>'; }
  else{
    let h = '<table><tr><th>الوقت</th><th>الزوج</th><th>اتجاه</th><th>جودة</th><th>الزناد/المنطقة</th><th>الحجم/القوة</th><th>R:R</th><th>النتيجة</th><th>الاستراتيجية</th></tr>';
    sig.forEach(s=>{
      const r = s.result===1?'<span class="tag win">ربح</span>':s.result===0?'<span class="tag loss">خسارة</span>':s.result===2?'<span class="tag info">محايدة</span>':'<span class="tag open">—</span>';
      const isHma = s.strategy==='HMA_DMI_MOMENTUM';
      const qTag = isHma ? ('ثقة '+(s.score||0)+'/9') : ((s.score||0)+'/8');
      const magTag = isHma ? (s.power!==null&&s.power!==undefined?('قوة '+s.power):'—') : (s.vol_ratio?s.vol_ratio+'×':'—');
      h += '<tr><td>'+s.time+'</td><td><b>'+s.symbol+'</b></td>'
        + '<td><span class="tag '+(s.direction==='BUY'?'buy':'sell')+'">'+(s.direction==='BUY'?'شراء':'بيع')+'</span></td>'
        + '<td><b>'+qTag+'</b></td><td>'+esc(s.trigger||'—')+'</td>'
        + '<td>'+magTag+'</td>'
        + '<td>'+(s.rr?s.rr+':1':'—')+'</td><td>'+r+'</td>'
        + '<td><span class="tag info">'+esc(s.strategy||'SBR')+'</span></td></tr>';
    });
    sb.innerHTML = h + '</table>';
  }

  const rj = await api('/api/rejections');
  renderRejections(rj);

  const stats = ov.stats || {};
  document.getElementById('sgTotal').textContent = stats.total_signals||0;
  document.getElementById('sgExec').textContent = stats.trades_executed||0;
  document.getElementById('sgExecS').textContent = 'مرفوضة بالمخاطر: '+(stats.rejected_by_risk||0)+' • بالأخبار: '+(stats.rejected_by_news||0);
  document.getElementById('sgRejQ').textContent = stats.rejected_quality||0;
  document.getElementById('sgRejO').textContent = stats.rejected_open_trade||0;

  /* الأداء اليومي */
  const dper = await api('/api/daily');
  const tB = document.getElementById('todayBox');
  if(tB && dper.today){
    const t = dper.today;
    const wr = (t.winrate !== null && t.winrate !== undefined) ? t.winrate + '%' : '—';
    tB.innerHTML =
      '<div class="grid" style="margin-bottom:0">'
      + '<div class="card '+(t.pnl>=0?'g':'o')+'"><div class="l">💵 نتيجة اليوم</div><div class="v '+(t.pnl>=0?'pos':'neg')+'">'+mo(t.pnl)+'</div></div>'
      + '<div class="card b"><div class="l">📂 صفقات اليوم</div><div class="v">'+t.total+'</div><div class="s">مباشر: '+(dper.trades_today_live||0)+'</div></div>'
      + '<div class="card p"><div class="l">✅ رابحة</div><div class="v">'+t.wins+'</div></div>'
      + '<div class="card o"><div class="l">❌ خاسرة</div><div class="v">'+t.losses+'</div></div>'
      + '<div class="card y"><div class="l">🏆 نسبة الفوز</div><div class="v">'+wr+'</div></div>'
      + '</div>';
  }
  const dB = document.getElementById('daysBox');
  if(dB){
    if(!dper.days || !dper.days.length){ dB.innerHTML = '<div class="empty">لا سجل أيام بعد — يُجمع تلقائياً مع كل صفقة</div>'; }
    else{
      let h = '';
      dper.days.forEach(d=>{
        let tradesHtml = '';
        if(d.trades && d.trades.length > 0){
          tradesHtml = '<div style="margin-top:8px;font-size:12px;color:var(--sub)">صفقات اليوم: '
            + d.trades.map(tr => {
                const st = tr.pnl_source==='binance' ? ' ✓' : tr.pnl_source==='estimated' ? ' ⚠️' : '';
                return '<b>'+tr.symbol+'</b> ('+(tr.direction==='BUY'?'شراء':'بيع')+': <span class="'+(tr.pnl>=0?'pos':'neg')+'">'+mo(tr.pnl)+'</span>'+st+')';
              }).join(' | ')
            + '</div>';
        }
        h += '<div style="background:var(--bg2);padding:12px;border-radius:10px;margin-bottom:10px">'
          + '<div style="display:flex;justify-content:space-between;align-items:center">'
          + '<div><b>📅 التاريخ: ' + d.date + '</b></div>'
          + '<div class="'+(d.pnl>=0?'pos':'neg')+'" style="font-weight:800;font-size:16px">'+mo(d.pnl)+'</div>'
          + '</div>'
          + '<div style="display:flex;gap:15px;margin-top:6px;font-size:13px;color:var(--sub)">'
          + '<span>✅ رابحة: <b style="color:var(--green)">'+d.wins+'</b></span>'
          + '<span>❌ خاسرة: <b style="color:var(--red)">'+d.losses+'</b></span>'
          + '<span>📊 المجموع: <b>'+d.total+'</b></span>'
          + '<span>🏆 نسبة الفوز: <b>'+(d.winrate!==null&&d.winrate!==undefined?d.winrate+'%':'—')+'</b></span>'
          + '</div>' + tradesHtml + '</div>';
      });
      dB.innerHTML = h;
    }
  }
  const aB = document.getElementById('aggBox');
  if(aB && dper.aggregates){
    const a = dper.aggregates;
    aB.innerHTML =
      '<div class="kv"><span>أيام نشطة (بصفقات)</span><b>'+a.active_days+'</b></div>'
      + '<div class="kv"><span>إجمالي الصفقات المغلقة</span><b>'+a.total_closed+'</b></div>'
      + '<div class="kv"><span>رابحة / خاسرة</span><b>'+a.total_wins+' / '+(a.total_closed - a.total_wins)+'</b></div>'
      + '<div class="kv"><span>نسبة الفوز عبر التاريخ</span><b>'+(a.overall_winrate!==null&&a.overall_winrate!==undefined?a.overall_winrate+'%':'—')+'</b></div>'
      + '<div class="kv"><span>إجمالي الربح/الخسارة</span><b class="'+(a.total_pnl>=0?'pos':'neg')+'">'+mo(a.total_pnl)+'</b></div>'
      + (a.best_day?'<div class="kv"><span>🥇 أفضل يوم</span><b>'+a.best_day.date+' ('+mo(a.best_day.pnl)+')</b></div>':'')
      + (a.worst_day?'<div class="kv"><span>💀 أسوأ يوم</span><b>'+a.worst_day.date+' ('+mo(a.worst_day.pnl)+')</b></div>':'');
  }

  const nf = await api('/api/notifications?after='+lastNid);
  if(nf.items && nf.items.length){
    lastNid = nf.last_id || lastNid;
    document.getElementById('nCount').textContent = nf.total_unread || nf.items.length;
    const feed = document.getElementById('notifFeed');
    const lf = document.getElementById('liveFeed');
    let html = '';
    nf.items.forEach(n=>{
      const k = KM[n.kind] || KM.info;
      html += '<div class="nt '+k[0]+'"><div class="nt-ic">'+k[1]+'</div>'
        + '<div class="nt-b"><div class="nt-t">'+esc(n.title)+'</div>'
        + (n.body?'<div class="nt-x">'+esc(n.body)+'</div>':'')
        + '<div class="nt-tm">'+n.time+'</div></div></div>';
    });
    feed.innerHTML = html + feed.innerHTML;
    lf.innerHTML = html + lf.innerHTML;
    while(lf.children.length>15) lf.removeChild(lf.lastChild);
    while(feed.children.length>150) feed.removeChild(feed.lastChild);
  }

  /* المخاطر */
  document.getElementById('riskStatus').textContent = risk.can_trade ? '✅ مسموح' : '🛑 ممنوع';
  document.getElementById('riskStatus').className = 'v ' + (risk.can_trade ? 'pos' : 'neg');
  document.getElementById('riskReason').textContent = risk.reason || '—';
  document.getElementById('consLosses').textContent = risk.consecutive_losses || 0;
  document.getElementById('dayLosses').textContent = risk.daily_losses || 0;
  const dayPnlR = risk.daily_pnl || 0;
  document.getElementById('dayPnlRisk').textContent = mo(dayPnlR);
  document.getElementById('dayPnlRisk').className = 'v ' + (dayPnlR>=0?'pos':'neg');
  document.getElementById('dayPnlRiskS').textContent = 'الرصيد المرجعي: $'+(risk.initial_balance||0).toFixed(2);

  const er = await api('/api/errors');
  const eb = document.getElementById('errBox');
  const ek = Object.keys(er.errors||{});
  if(!ek.length){ eb.innerHTML='<div class="empty" style="padding:16px">✅ لا أخطاء — كل شيء نظيف</div>'; }
  else{ eb.innerHTML = ek.map(k=>'<div class="kv"><span>'+esc(k)+'</span><b style="color:var(--orange)">×'+er.errors[k]+'</b></div>').join(''); }

  /* إعدادات النظام الحية */
  document.getElementById('setBox').innerHTML =
    '<div class="kv"><span>الوضع</span><b>'+mode+'</b></div>'
    + '<div class="kv"><span>Testnet</span><b>'+(ov.testnet?'🧪 نعم — مفروض':'لا — حقيقي')+'</b></div>'
    + '<div class="kv"><span>الرافعة</span><b>'+ov.leverage+'x</b></div>'
    + '<div class="kv"><span>الهامش</span><b>$'+ov.trade_size+'</b></div>'
    + '<div class="kv"><span>النوشنال</span><b>$'+(ov.trade_size*ov.leverage)+'</b></div>'
    + '<div class="kv"><span>🎯 هدف TP1</span><b>'+(ov.sbr?ov.sbr.tp1_return_pct:20)+'% من الهامش — إغلاق 100%</b></div>'
    + '<div class="kv"><span>⏰ ستوب زمني للصفقة</span><b>'+((ov.sbr&&ov.sbr.max_hours)||4)+' ساعة</b></div>'
    + '<div class="kv"><span>المتزامنة</span><b>'+ov.max_open+'</b></div>'
    + '<div class="kv"><span>أزواج محملة</span><b>'+ov.pairs+'</b></div>'
    + '<div class="kv"><span>تبريد إعادة الدخول</span><b>15 دقيقة لكل زوج</b></div>'
    + '<div class="kv"><span>عمر أقصى للسعر</span><b>30 ثانية — لا دخول بأسعار قديمة</b></div>'
    + '<div class="kv"><span>إنقاذ الأسعار</span><b>REST تلقائي عند تجمّد التدفق ✓</b></div>'
    + '<div class="kv"><span>ستوب المنصة</span><b>STOP_MARKET حقيقي + مراقبة محلية احتياطية</b></div>'
    + '<div class="kv"><span>أوامر دخول</span><b>محاولة واحدة — لا دخول مزدوج</b></div>'
    + '<div class="kv"><span>فلتر الأخبار</span><b>'+(nw.enabled ? 'مفعّل 📰 (تقويم حي)' : 'معطل — فعّله بالأسفل')+'</b></div>';

  renderNews(ov.news);   /* بطاقة فلتر الأخبار */
  renderSBR(ov.sbr, ov.scan);   /* بطاقة إعدادات SBR */
  const stg = await api('/api/strategies');
  renderStrategies(stg);   /* 🧭 مقارنة الاستراتيجيات + إعدادات HMA */
  const pb = document.getElementById('pauseBtn');
  pb.textContent = ov.trade_enabled ? '⏸️ إيقاف مؤقت' : '▶️ استئناف';
  const sbtn = document.getElementById('sbrBtn');
  if(sbtn && ov.sbr) sbtn.textContent = ov.sbr.live ? '🛑 إيقاف تداول SBR-1 (عودة للإشارات)' : '🎯 تفعيل تداول SBR-1';
}

function renderOpen(tr, boxId){
  const box = document.getElementById(boxId);
  if(!tr || !tr.length){ box.innerHTML = '<div class="empty">لا صفقات مفتوحة — القناص يراقب</div>'; return; }
  let h = '<table><tr><th>الزوج</th><th>اتجاه</th><th>الدخول</th><th>الحالي</th><th>العائم</th><th>جودة</th><th>R:R</th><th>TP1</th><th>SL</th><th>ستوب الحماية</th><th>العمر</th><th>الاستراتيجية</th></tr>';
  tr.forEach(t=>{
    let stopCell = '—';
    if(t.stop_state==='verified') stopCell='<span class="tag ok">🛡️ مؤكد على المنصة ✓</span>';
    else if(t.stop_state==='placed') stopCell='<span class="tag warn">⏳ مثبّت — بانتظار التأكيد</span>';
    else if(t.stop_state==='local') stopCell='<span class="tag info" title="'+esc(t.stop_error||'')+'">🛡️ مراقبة محلية فعّالة</span> '
      + '<button class="act btn-s" style="padding:2px 8px;font-size:11px" data-sym="'+t.symbol+'" title="إعادة محاولة الستوب على المنصة">🔁</button>';
    h += '<tr><td><b>'+t.symbol+'</b></td>'
      + '<td><span class="tag '+(t.side==='BUY'?'buy':'sell')+'">'+(t.side==='BUY'?'شراء':'بيع')+'</span></td>'
      + '<td>'+t.entry+'</td><td>'+(t.current!==null?t.current:'—')+'</td>'
      + '<td class="'+((t.pnl||0)>=0?'pos':'neg')+'"><b>'+(t.pnl===null?'—':mo(t.pnl))+'</b></td>'
      + '<td>'+(t.score?t.score+'/8':'—')+'</td>'
      + '<td>'+(t.rr?t.rr.toFixed(2)+':1':'—')+'</td>'
      + '<td>'+(t.tp?t.tp:'—')+'</td>'
      + '<td>'+(t.sl?t.sl:'—')+'</td>'
      + '<td>'+stopCell+'</td>'
      + '<td>'+(t.hours_in!==null&&t.hours_in!==undefined?t.hours_in.toFixed(1)+'س':'—')+'</td>'
      + '<td><span class="tag info">'+esc(t.strategy||'SBR')+'</span></td></tr>';
  });
  box.innerHTML = h + '</table>';
}

/* ═══ سجل أسباب الرفض ═══ */
function renderRejections(rj){
  const box = document.getElementById('rejBox');
  if(!box) return;
  rj = rj || {};
  const counts = rj.counts || [];
  const recent = rj.recent || [];
  let h = '';
  if(counts.length){
    h += '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px">';
    counts.forEach(c=>{
      h += '<span class="tag info" style="font-size:12px;padding:5px 10px">'+esc(c[0])+' : <b>'+c[1]+'</b></span>';
    });
    h += '</div>';
  }
  if(!recent.length){
    h += '<div class="empty">لا رفض مسجّل بعد — كل فحص مرفوض يُسجَّل هنا مع سببه</div>';
  } else {
    h += '<table><tr><th>الوقت</th><th>الزوج</th><th>سبب الرفض</th></tr>';
    recent.forEach(r=>{
      h += '<tr><td>'+r.time+'</td><td><b>'+r.symbol+'</b></td><td>'+esc(r.reason)+'</td></tr>';
    });
    h += '</table>';
  }
  box.innerHTML = h;
}

/* ═══ ستوب المنصة — إعادة محاولة فورية ═══ */
async function stopRetry(symbol){
  try{
    const r = await (await fetch('/api/stop-retry', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({symbol:symbol})})).json();
    if(r.ok) alert('🛡️ تمت المزامنة ✓' + (r.stop_price ? ('\\nالسعر: ' + r.stop_price) : '') + '\\nالحالة: ' + r.state);
    else alert('❌ فشل:\\n' + (r.stop_error || r.error || 'خطأ غير معروف'));
    loadAll();
  }catch(e){ alert('فشل الاتصال: ' + e.message); }
}

/* ═══ بطاقة إعدادات SBR ═══ */
function renderSBR(sbr, scn){
  const b = document.getElementById('sbrSt');
  if(!b) return;
  sbr = sbr || {};
  const st = sbr.settings || {};
  scn = scn || {};
  const last = scn.last || {};
  const inp = 'background:var(--bg);color:var(--txt);border:1px solid var(--bord);border-radius:6px;padding:4px';
  const num = (id,label,val,min,max,step) =>
    '<div class="kv"><span>'+label+'</span><b><input id="'+id+'" type="number" min="'+min+'" max="'+max+'" step="'+(step||'any')+'" value="'+(val!==undefined&&val!==null?val:'')+'" style="'+inp+';width:110px"></b></div>';
  document.getElementById('scanUniverseC').textContent = (scn.universe_count||0);
  document.getElementById('scanLastBatch').textContent = last.scanned||0;
  document.getElementById('scanLastSig').textContent = last.signals||0;
  document.getElementById('scanLastS').textContent = 'تخطي بسبب السبريد: '+(last.skipped_spread||0);
  document.getElementById('scanCursorS').textContent =
    'مؤشر الدوران: '+(scn.cursor||0)
    + (last.ts ? ' • آخر مسح قبل '+Math.max(0,Math.round(Date.now()/1000-last.ts))+' ث' : '');
  /* ⚠️ تعارض متغيرات Railway مع القيم الفعالة — يُعرض بوضوح مع زر استيراد صريح */
  const conf = sbr.env_conflicts || [];
  let confHtml = '';
  if(conf.length){
    confHtml = '<div style="background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.4);border-radius:10px;padding:10px 12px;margin-bottom:12px;font-size:12px;line-height:1.9">'
      + '<b style="color:var(--red)">⚠️ تعارض Railway: القاعدة هي المرجع بعد أول تشغيل — هذه المتغيرات معدّلة في Railway لكنها ليست الفعالة:</b><br>'
      + conf.map(c=>'<code>'+esc(c.env)+'</code> = '+c.env_value+' (الفعال: '+c.active_value+')').join('<br>')
      + '<br><button class="act btn-r" style="margin-top:8px;padding:6px 12px;font-size:12px" onclick="sbrImportEnv()">⬇️ استيراد قيم Railway وتطبيقها الآن</button></div>';
  }
  b.innerHTML = confHtml +
    '<div style="background:rgba(148,163,184,.08);border:1px solid rgba(148,163,184,.35);border-radius:10px;padding:8px 12px;margin-bottom:12px;font-size:12px;line-height:1.8">'
    + '⛔ <b>أزواج مستبعدة من SBR (فلتر V11.2 — خاسرة مزمنة على النافذتين):</b> '
    + (sbr.blacklist && sbr.blacklist.length ? esc(sbr.blacklist.join('، ')) : '—')
    + '<br><span style="opacity:.75">ثابت موثق في الكود (قاعدة النافذتين) — لا يُعدل من اللوحة عمداً</span></div>'
    + '<div class="kv"><span>🧠 السلسلة النشطة</span><b>'+esc(sbr.describe||'—')+'</b></div>'
    + num('sbrMinVol','أدنى سيولة 24س (USDT)', st.min_vol_usdt, 1000000, 10000000000, 1000000)
    + num('sbrMinChange','أدنى تغير 24س موقّع (%) — حسب الاتجاه', st.min_change_pct, 0, 50, 0.1)
    + num('sbrMinAtr','أدنى تقلب ATR-1h (%)', st.min_atr_pct, 0.05, 10, 0.05)
    + num('sbrVolMult','حجم الاختراق ≥ ×متوسط الـ20 السابقة', st.vol_mult, 1, 10, 0.1)
    + num('sbrMaxHours','أقصى عمر للاختراق (ساعة)', st.max_setup_hours, 1, 48, 1)
    + num('sbrBreakAtr','عمق الاختراق خارج الحافة (×ATR)', st.break_atr, 0.05, 2, 0.05)
    + num('sbrCluster','نطاق تكتيل المنطقة (%)', st.cluster_pct ? st.cluster_pct*100 : 0.5, 0.1, 3, 0.1)
    + num('sbrTouches','أدنى لمسات للمنطقة', st.min_zone_touches, 2, 6, 1)
    + num('sbrRetest','نافذة رفض إعادة الاختبار (شمعة 15د)', st.retest_window, 2, 24, 1)
    + num('sbrChase','أقصى ابتعاد عن الحافة (×ATR)', st.max_chase_atr, 0.2, 5, 0.1)
    + num('sbrSlAtr','حاجز الستوب خلف المنطقة (×ATR)', st.sl_zone_atr, 0.1, 3, 0.1)
    + num('sbrBeAtr','🛡️ إطلاق وقف التعادل (×ATR) — 0 يعطّله', st.be_atr, 0, 5, 0.1)
    + num('sbrBeBuf','هامش وقف التعادل فوق الدخول (نقطة أساس)', st.be_buf_bps, 0, 500, 5)
    + num('sbrRiskMin','أدنى مسافة ستوب (%)', st.risk_min_pct, 0.05, 2, 0.05)
    + num('sbrRiskMax','أقصى مسافة ستوب (%)', st.risk_max_pct, 0.5, 10, 0.1)
    + num('sbrMinRR','أدنى عائد/مخاطرة (R:R)', st.min_rr, 0.5, 5, 0.1)
    + num('sbrTp1Pct','🎯 هدف TP1 (% من الهامش)', st.tp1_return_pct, 1, 100, 1)
    + num('sbrTp1MaxAtr','أقصى مسافة TP1 واقعية (×ATR)', st.tp1_max_atr, 1, 20, 0.5)
    + num('sbrBatch','عدد العملات المفحوصة كل دورة', st.batch_size, 4, 40, 1)
    + num('sbrUniverse','حجم الكون (أعلى سيولة)', st.universe_size, 20, 400, 10)
    + num('sbrSpread','أقصى انتشار bid/ask (%)', st.max_spread_pct, 0.01, 2, 0.01)
    + num('sbrParallel','تحليلات متوازية', st.parallel, 1, 10, 1)
    + num('sbrMaxSig','أقصى إشارات منفذة في الدورة', st.max_signals_per_scan, 1, 5, 1);
}
async function sbrSave(){
  try{
    const payload = {
      min_vol_usdt: parseFloat(document.getElementById('sbrMinVol').value),
      min_change_pct: parseFloat(document.getElementById('sbrMinChange').value),
      min_atr_pct: parseFloat(document.getElementById('sbrMinAtr').value),
      vol_mult: parseFloat(document.getElementById('sbrVolMult').value),
      max_setup_hours: parseFloat(document.getElementById('sbrMaxHours').value),
      break_atr: parseFloat(document.getElementById('sbrBreakAtr').value),
      cluster_pct: parseFloat(document.getElementById('sbrCluster').value) / 100.0,
      min_zone_touches: parseInt(document.getElementById('sbrTouches').value, 10),
      retest_window: parseInt(document.getElementById('sbrRetest').value, 10),
      max_chase_atr: parseFloat(document.getElementById('sbrChase').value),
      sl_zone_atr: parseFloat(document.getElementById('sbrSlAtr').value),
      be_atr: parseFloat(document.getElementById('sbrBeAtr').value),
      be_buf_bps: parseFloat(document.getElementById('sbrBeBuf').value),
      risk_min_pct: parseFloat(document.getElementById('sbrRiskMin').value),
      risk_max_pct: parseFloat(document.getElementById('sbrRiskMax').value),
      min_rr: parseFloat(document.getElementById('sbrMinRR').value),
      tp1_return_pct: parseFloat(document.getElementById('sbrTp1Pct').value),
      tp1_max_atr: parseFloat(document.getElementById('sbrTp1MaxAtr').value),
      batch_size: parseInt(document.getElementById('sbrBatch').value, 10),
      universe_size: parseInt(document.getElementById('sbrUniverse').value, 10),
      max_spread_pct: parseFloat(document.getElementById('sbrSpread').value),
      parallel: parseInt(document.getElementById('sbrParallel').value, 10),
      max_signals_per_scan: parseInt(document.getElementById('sbrMaxSig').value, 10)
    };
    const r = await (await fetch('/api/sbr-settings', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})).json();
    if(r.ok){ alert('✅ حُفظت إعدادات SBR — تعمل الآن لحظياً' + (r.describe ? ('\\n' + r.describe) : '')); loadAll(); }
    else alert('❌ فشل: ' + (r.error || 'خطأ غير معروف'));
  }catch(e){ alert('فشل الاتصال: ' + e.message); }
}
async function scanNow(){
  try{
    const r = await (await fetch('/api/scan-now', {method:'POST'})).json();
    if(r.ok) alert('🔍 أُطلق مسح فوري — راقب 🔔 الإشعارات');
    else alert('❌ ' + (r.error || 'فشل'));
    loadAll();
  }catch(e){ alert('فشل الاتصال: ' + e.message); }
}

/* ⬇️ استيراد صريح لقيم Railway — القاعدة تبقى المرجع بعدها حتى يتغيّر المالك شيئاً */
async function sbrImportEnv(){
  const NL = String.fromCharCode(10);
  if(!confirm('تطبيق قيم متغيرات Railway على الإعدادات الفعالة وحفظها في القاعدة؟' + NL + 'الأولوية الافتراضية لن تتغير: التعديل من اللوحة يتقدم على متغيرات البيئة.')) return;
  try{
    const r = await (await fetch('/api/sbr-import-env', {method:'POST'})).json();
    if(r.ok){ alert('✅ طُبّقت: ' + (r.changed && r.changed.length ? r.changed.join(NL) : 'لا فروقات — مطابقة أصلاً')); loadAll(); }
    else alert('❌ ' + (r.error || 'فشل'));
  }catch(e){ alert('فشل الاتصال: ' + e.message); }
}

/* ═══ 🧭 الاستراتيجيات: مقارنة الأداء + حالة HMA + إعداداتها ═══ */
function renderStrategies(s){
  s = s || {};
  const list = s.strategies || [];
  const sb = document.getElementById('stratStatus');
  if(sb){
    let h = '';
    (s.states || []).forEach(x=>{
      h += '<div class="kv"><span>'+esc(x.name)+'</span><b>'+esc(x.status)+'</b></div>'
        + '<div class="kv"><span>↳ حالة السوق</span><b>'+esc(x.market_state)+'</b></div>'
        + '<div class="kv"><span>↳ آخر إشارة</span><b>'+esc(x.last_signal)+'</b></div>';
    });
    sb.innerHTML = h || '—';
  }
  const hb = document.getElementById('hmaBtn');
  if(hb) hb.textContent = (s.hma && s.hma.enabled) ? '🛑 تعطيل استراتيجية HMA' : '🧭 تفعيل استراتيجية HMA';
  const hl = document.getElementById('hmaLiveBtn');
  if(hl) hl.textContent = (s.hma && s.hma.live) ? '👁️ HMA إشارات فقط' : '⚔️ تفعيل تداول HMA';
  const cb = document.getElementById('stratCompare');
  if(cb){
    if(!list.length){ cb.innerHTML = '<div class="empty">لا بيانات بعد</div>'; }
    else{
      let h = '<table><tr><th>المؤشر</th>';
      list.forEach(x=>{ h += '<th>'+esc(x.name)+'</th>'; });
      h += '</tr>';
      const rows = [
        ['الحالة', x=>esc(x.enabled)],
        ['الوضع', x=>esc(x.live)],
        ['الإطار الزمني', x=>esc(x.timeframe||'—')],
        ['إشارات', x=>x.signals],
        ['صفقات منفذة', x=>x.executed],
        ['مفتوحة الآن', x=>x.open_now],
        ['رابحة / خاسرة', x=>x.wins+' / '+x.losses],
        ['نسبة الفوز', x=>x.winrate===null?'—':x.winrate+'%'],
        ['صافي النتيجة', x=>'<span class="'+((x.net_pnl||0)>=0?'pos':'neg')+'">'+mo(x.net_pnl||0)+'</span>'],
        ['متوسط الربح', x=>x.avg_win===null?'—':mo(x.avg_win)],
        ['متوسط الخسارة', x=>x.avg_loss===null?'—':mo(x.avg_loss)],
        ['Profit Factor', x=>x.profit_factor===null?'—':x.profit_factor],
        ['أقصى تراجع', x=>x.max_drawdown===null?'—':'$'+Math.abs(x.max_drawdown).toFixed(2)],
        ['أفضل الرموز (مغلق)', x=>esc(x.by_symbol||'—')],
      ];
      rows.forEach(r=>{
        h += '<tr><td>'+r[0]+'</td>';
        list.forEach(x=>{ h += '<td>'+r[1](x)+'</td>'; });
        h += '</tr>';
      });
      cb.innerHTML = h + '</table>';
    }
  }
  const tb = document.getElementById('stratTrades');
  if(tb){
    const t = s.recent || [];
    if(!t.length){ tb.innerHTML = '<div class="empty">لا صفقات مغلقة بعد</div>'; }
    else{
      let h = '<table><tr><th>الوقت</th><th>الاستراتيجية</th><th>الزوج</th><th>الاتجاه</th><th>النتيجة</th><th>المصدر</th></tr>';
      t.forEach(c=>{
        h += '<tr><td>'+c.time+'</td>'
          + '<td><span class="tag info">'+esc(c.strategy)+'</span></td>'
          + '<td><b>'+c.symbol+'</b></td>'
          + '<td><span class="tag '+(c.direction==='BUY'?'buy':'sell')+'">'+(c.direction==='BUY'?'شراء':'بيع')+'</span></td>'
          + '<td class="'+(c.pnl>=0?'pos':'neg')+'"><b>'+mo(c.pnl)+'</b></td>'
          + '<td>'+(c.pnl_source==='binance'?'<span class="tag ok">Binance ✓</span>':c.pnl_source==='estimated'?'<span class="tag warn">تقديري ⚠️</span>':'—')+'</td></tr>';
      });
      tb.innerHTML = h + '</table>';
    }
  }
  const rb = document.getElementById('stratRej');
  if(rb){
    const rj = s.rejections || [];
    if(!rj.length){ rb.innerHTML = '<div class="empty">لا رفض مسجّل — كل فحص مرفوض يُسجَّل هنا موسوماً باستراتيجيته</div>'; }
    else{
      let h = '';
      rj.forEach(g=>{
        h += '<div style="margin-bottom:10px"><b>'+esc(g.strategy)+'</b>'
          + '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:6px">';
        g.counts.forEach(c=>{ h += '<span class="tag info" style="font-size:11px">'+esc(c[0])+' : <b>'+c[1]+'</b></span>'; });
        h += '</div></div>';
      });
      rb.innerHTML = h;
    }
  }
  renderHma(s.hma || {});
}

/* ═══ 🧭 بطاقة إعدادات HMA_DMI_MOMENTUM ═══ */
function renderHma(h){
  const b = document.getElementById('hmaSt');
  if(!b) return;
  h = h || {};
  const st = h.settings || {};
  const inp = 'background:var(--bg);color:var(--txt);border:1px solid var(--bord);border-radius:6px;padding:4px';
  const num = (id,label,val,min,max,step) =>
    '<div class="kv"><span>'+label+'</span><b><input id="'+id+'" type="number" min="'+min+'" max="'+max+'" step="'+(step||'any')+'" value="'+(val!==undefined&&val!==null?val:'')+'" style="'+inp+';width:110px"></b></div>';
  const tfSel = '<div class="kv"><span>الإطار الزمني للشموع (مغلق)</span><b><select id="hmaTf" style="'+inp+'">'
    + ['5m','15m','1h'].map(t=>'<option value="'+t+'"'+(h.timeframe===t?' selected':'')+'>'+t+'</option>').join('')
    + '</select></b></div>';
  const emaSel = '<div class="kv"><span>فلتر EMA200 (فلتر اتجاه اختياري)</span><b><select id="hmaEmaF" style="'+inp+'">'
    + '<option value="1"'+(st.ema_filter===1?' selected':'')+'>مفعّل</option>'
    + '<option value="0"'+(st.ema_filter===0?' selected':'')+'>معطل</option>'
    + '</select></b></div>';
  let confHtml = '';
  (h.env_conflicts||[]).forEach(c=>{
    confHtml += '<code>'+esc(c.env)+'</code> = '+c.env_value+' (الفعال: '+c.active_value+')<br>';
  });
  if(confHtml) confHtml = '<div style="background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.4);border-radius:10px;padding:10px 12px;margin-bottom:12px;font-size:12px;line-height:1.9"><b style="color:var(--red)">⚠️ تعارض Railway مع القاعدة (القاعدة هي المرجع):</b><br>'+confHtml+'</div>';
  const t4v = (st.trend4h_enabled===undefined ? 1 : st.trend4h_enabled);
  const t4Sel = '<div class="kv"><span>🧭 بوابة اتجاه 4 ساعات T3 (EMA على 4س + الميل — بلا إعادة رسم)</span><b><select id="hmaT4h" style="'+inp+'">'
    + '<option value="1"'+(t4v===1?' selected':'')+'>مفعّلة</option>'
    + '<option value="0"'+(t4v===0?' selected':'')+'>معطلة</option>'
    + '</select></b></div>';
  b.innerHTML = confHtml
    + '<div style="background:rgba(148,163,184,.08);border:1px solid rgba(148,163,184,.35);border-radius:10px;padding:8px 12px;margin-bottom:12px;font-size:12px;line-height:1.8">'
    + '⛔ <b>أزواج مستبعدة من HMA (فلتر V11.3 — خاسرة مزمنة على النافذتين):</b> '
    + (h.blacklist && h.blacklist.length ? esc(h.blacklist.join('، ')) : '—')
    + '<br><span style="opacity:.75">ثابت موثق في الكود (قاعدة النافذتين) — لا يُعدل من اللوحة عمداً — قائمة SBR مستقلة عنها</span></div>'
    + '<div class="kv"><span>🧠 السلسلة النشطة</span><b>'+esc(h.describe||'—')+'</b></div>'
    + tfSel + emaSel + t4Sel
    + num('hmaT4hLen','فترة EMA لبوابة 4 ساعات (شموع 4س مغلقة)', (st.trend4h_ema_len===undefined?50:st.trend4h_ema_len), 20, 200, 5)
    + num('hmaFast','HMA السريعة', st.hma_fast, 4, 50, 1)
    + num('hmaSlow','HMA البطيئة', st.hma_slow, 10, 200, 1)
    + num('hmaDi','فترة DI', st.di_period, 3, 30, 1)
    + num('hmaAdxS','تنعيم ADX', st.adx_smooth, 3, 30, 1)
    + num('hmaMomF','زخم سريع', st.mom_fast, 1, 20, 1)
    + num('hmaMomM','زخم متوسط', st.mom_mid, 2, 40, 1)
    + num('hmaMomS','زخم بطيء', st.mom_slow, 3, 60, 1)
    + num('hmaEr','فترة كفاءة الحركة ER', st.er_period, 5, 50, 1)
    + num('hmaStruct','فترة بنية السوق (تأكيد القمم/القيعان)', st.struct_period, 3, 20, 1)
    + num('hmaStP','فترة ATR لـ Supertrend', st.st_atr_period, 5, 50, 1)
    + num('hmaStM','معامل ATR لـ Supertrend', st.st_mult, 0.5, 5, 0.05)
    + num('hmaEmaP','فترة EMA', st.ema_period, 50, 400, 10)
    + num('hmaMinPow','أدنى قوة دخول (0-100)', st.min_power, 0, 100, 1)
    + num('hmaMinConf','أدنى ثقة دخول (0-9)', st.min_confidence, 0, 9, 1)
    + num('hmaStrongAdx','عتبة ADX القوي', st.strong_adx, 5, 50, 1)
    + num('hmaStrongEr','عتبة ER القوي', st.strong_er, 0.05, 0.9, 0.05)
    + num('hmaMomConf','أدنى تأكيدات الزخم (1-3)', st.min_mom_conf, 1, 3, 1)
    + num('hmaStateDur','أدنى مدة الحالة (شموع)', st.min_state_candles, 1, 20, 1)
    + num('hmaCooldown','تبريد الإشارات/التبدّل (شموع)', st.cooldown_candles, 0, 30, 1)
    + num('hmaRevAtr','عتبة الانقلاب/الكسر (×ATR)', st.reversal_atr, 0.1, 5, 0.05)
    + num('hmaSoPow','قوة الاستثناء الهيكلي', st.so_power, 0, 100, 1)
    + num('hmaSoConf','ثقة الاستثناء الهيكلي', st.so_confidence, 0, 9, 1)
    + num('hmaSoAdx','ADX للاستثناء الهيكلي', st.so_adx, 5, 50, 1)
    + num('hmaAdxGate','🧭 بوابة الاتجاهية ADX-14 (0=معطلة)', st.adx_gate, 0, 50, 1)
    + num('hmaSlAtr','الستوب (×ATR)', st.sl_atr_mult, 0.3, 6, 0.1)
    + num('hmaRiskMin','أدنى مسافة ستوب (%)', st.risk_min_pct, 0.05, 2, 0.05)
    + num('hmaRiskMax','أقصى مسافة ستوب (%)', st.risk_max_pct, 0.5, 10, 0.1)
    + num('hmaMinRR','أدنى عائد/مخاطرة (R:R)', st.min_rr, 0.5, 5, 0.1)
    + num('hmaTp1','🎯 هدف TP1 (% من الهامش)', st.tp1_return_pct, 1, 100, 1)
    + num('hmaTp1Atr','أقصى مسافة TP1 واقعية (×ATR)', st.tp1_max_atr, 1, 20, 0.5)
    + num('hmaUniverse','حجم كون HMA (أعلى سيولة)', st.universe_size, 10, 200, 5)
    + num('hmaBatch','عدد العملات المفحوصة كل دورة', st.batch_size, 4, 60, 1)
    + num('hmaMaxSig','أقصى إشارات منفذة في الدورة', st.max_signals_per_scan, 1, 3, 1);
}
async function hmaSave(){
  try{
    const payload = {
      timeframe: document.getElementById('hmaTf').value,
      ema_filter: parseInt(document.getElementById('hmaEmaF').value, 10),
      trend4h_enabled: parseInt(document.getElementById('hmaT4h').value, 10),
      trend4h_ema_len: parseFloat(document.getElementById('hmaT4hLen').value),
      hma_fast: parseFloat(document.getElementById('hmaFast').value),
      hma_slow: parseFloat(document.getElementById('hmaSlow').value),
      di_period: parseFloat(document.getElementById('hmaDi').value),
      adx_smooth: parseFloat(document.getElementById('hmaAdxS').value),
      mom_fast: parseFloat(document.getElementById('hmaMomF').value),
      mom_mid: parseFloat(document.getElementById('hmaMomM').value),
      mom_slow: parseFloat(document.getElementById('hmaMomS').value),
      er_period: parseFloat(document.getElementById('hmaEr').value),
      struct_period: parseFloat(document.getElementById('hmaStruct').value),
      st_atr_period: parseFloat(document.getElementById('hmaStP').value),
      st_mult: parseFloat(document.getElementById('hmaStM').value),
      ema_period: parseFloat(document.getElementById('hmaEmaP').value),
      min_power: parseFloat(document.getElementById('hmaMinPow').value),
      min_confidence: parseFloat(document.getElementById('hmaMinConf').value),
      strong_adx: parseFloat(document.getElementById('hmaStrongAdx').value),
      strong_er: parseFloat(document.getElementById('hmaStrongEr').value),
      min_mom_conf: parseFloat(document.getElementById('hmaMomConf').value),
      min_state_candles: parseFloat(document.getElementById('hmaStateDur').value),
      cooldown_candles: parseFloat(document.getElementById('hmaCooldown').value),
      reversal_atr: parseFloat(document.getElementById('hmaRevAtr').value),
      so_power: parseFloat(document.getElementById('hmaSoPow').value),
      so_confidence: parseFloat(document.getElementById('hmaSoConf').value),
      so_adx: parseFloat(document.getElementById('hmaSoAdx').value),
      adx_gate: parseFloat(document.getElementById('hmaAdxGate').value),
      sl_atr_mult: parseFloat(document.getElementById('hmaSlAtr').value),
      risk_min_pct: parseFloat(document.getElementById('hmaRiskMin').value),
      risk_max_pct: parseFloat(document.getElementById('hmaRiskMax').value),
      min_rr: parseFloat(document.getElementById('hmaMinRR').value),
      tp1_return_pct: parseFloat(document.getElementById('hmaTp1').value),
      tp1_max_atr: parseFloat(document.getElementById('hmaTp1Atr').value),
      universe_size: parseFloat(document.getElementById('hmaUniverse').value),
      batch_size: parseFloat(document.getElementById('hmaBatch').value),
      max_signals_per_scan: parseFloat(document.getElementById('hmaMaxSig').value)
    };
    const r = await (await fetch('/api/hma-settings', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})).json();
    if(r.ok){ alert('✅ حُفظت إعدادات HMA — تعمل الآن لحظياً' + (r.describe ? ('\\n' + r.describe) : '')); loadAll(); }
    else alert('❌ فشل: ' + (r.error || 'خطأ غير معروف'));
  }catch(e){ alert('فشل الاتصال: ' + e.message); }
}
async function hmaToggle(){
  try{
    const stg = await api('/api/strategies');
    const target = !((stg.hma||{}).enabled);
    const msg = target
      ? '🧭 تفعيل استراتيجية HMA_DMI_MOMENTUM؟\\nستولّد إشاراتها بشكل مستقل عن SBR مع كل بوابات المخاطر المشتركة.'
      : '🛑 تعطيل استراتيجية HMA_DMI_MOMENTUM؟\\nلن تولّد إشارات جديدة. صفقاتها المفتوحة تبقى مُدارة (ستوب/TP1/ستوب زمني/مخارج استراتيجية).\\nمتابعة؟';
    if(!confirm(msg)) return;
    const r = await (await fetch('/api/hma-toggle', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({enabled: target})})).json();
    if(r.ok){ alert(target ? '✅ تم تفعيل استراتيجية HMA_DMI_MOMENTUM' : '🛑 تم تعطيل استراتيجية HMA — الصفقات المفتوحة تبقى مُدارة'); loadAll(); }
  }catch(e){ alert('فشل: ' + e.message); }
}
async function hmaLiveToggle(){
  try{
    const stg = await api('/api/strategies');
    const target = !((stg.hma||{}).live);
    const msg = target
      ? '⚔️ تفعيل التداول الفعلي لمحرك HMA_DMI_MOMENTUM؟\\nستُفتح صفقات فقط عند تحقق كل شروطها (آلة حالات + قوة وثقة + زناد) وبوابة المخاطر المشتركة.\\nالإشارات السابقة لن تُنفَّذ بأثر رجعي. متابعة؟'
      : '👁️ تحويل HMA_DMI_MOMENTUM إلى وضع الإشارات فقط؟\\nلن تُفتح صفقات جديدة. متابعة؟';
    if(!confirm(msg)) return;
    const r = await (await fetch('/api/hma-live', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({live: target})})).json();
    if(r.ok){ alert(target ? '✅ تم تفعيل تداول HMA_DMI_MOMENTUM' : '👁️ عادت HMA لوضع الإشارات فقط'); loadAll(); }
  }catch(e){ alert('فشل: ' + e.message); }
}

/* ═══ فلتر الأخبار — بطاقة التحكم ═══ */
function renderNews(nw){
  const b = document.getElementById('newsBox');
  if(!b) return;
  nw = nw || {};
  const inp = 'background:var(--bg);color:var(--txt);border:1px solid var(--bord);border-radius:6px;padding:4px';
  const nxt = nw.next_event
    ? '<div class="kv"><span>🗓️ الحدث القادم</span><b>'+esc(nw.next_event.title)+' ('+nw.next_event.cur+') — بعد '+nw.next_event.in_min+' دقيقة</b></div>'
    : '<div class="kv"><span>🗓️ الحدث القادم</span><b>لا أحداث مؤثرة</b></div>';
  b.innerHTML =
    '<div class="kv"><span>الحالة</span><b>'+(nw.enabled?'✅ مفعّل — كتم تلقائي حول الأحداث':'⛔ معطل — التداول مستمر دائماً')+'</b></div>'
    + (nw.blocked_now ? '<div class="kv"><span>🔇 الوضع الآن</span><b>'+esc(nw.reason||'كتم نشط')+'</b></div>' : '')
    + nxt
    + '<div class="kv"><span>أقل تأثير يُكتم</span><b><select id="newsImpact" style="'+inp+'">'
    + '<option value="High"'+(nw.impact_min==='High'?' selected':'')+'>عالي فقط (CPI/FOMC/NFP)</option>'
    + '<option value="Medium"'+(nw.impact_min==='Medium'?' selected':'')+'>متوسط وأعلى</option>'
    + '</select></b></div>'
    + '<div class="kv"><span>كتم قبل الحدث (دقيقة)</span><b><input id="newsBefore" type="number" min="0" max="240" value="'+(nw.before_min||30)+'" style="'+inp+';width:80px"></b></div>'
    + '<div class="kv"><span>كتم بعد الحدث (دقيقة)</span><b><input id="newsAfter" type="number" min="0" max="240" value="'+(nw.after_min||30)+'" style="'+inp+';width:80px"></b></div>'
    + '<div class="kv"><span>العملات المتابعة</span><b><input id="newsCur" value="'+esc(nw.currencies||'USD')+'" style="'+inp+';width:110px"></b></div>'
    + '<div class="kv"><span>نوافذ يدوية UTC</span><b><input id="newsWin" placeholder="13:15-13:45,15:00-15:30" value="'+esc(nw.windows||'')+'" style="'+inp+';width:170px"></b></div>'
    + '<div class="kv"><span>📰 إشارات مرفوضة بالأخبار</span><b>'+(nw.rejected_total||0)+'</b></div>'
    + '<div class="kv"><span>آخر تحديث للتقويم</span><b>'+((nw.calendar_age_min!==null&&nw.calendar_age_min!==undefined)?('قبل '+nw.calendar_age_min+' دقيقة — '+(nw.events_count||0)+' حدثاً'):'لم يُجلب بعد')+'</b></div>'
    + (nw.last_error ? '<div class="kv"><span>⚠️ آخر خطأ جلب</span><b style="color:var(--orange)">'+esc(nw.last_error)+'</b></div>' : '');
}
async function newsToggle(){
  try{
    const cur = await api('/api/overview');
    const r = await (await fetch('/api/news-toggle', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({enabled: !((cur.news||{}).enabled)})})).json();
    if(r.ok){ alert(r.news.enabled ? '✅ تم تفعيل فلتر الأخبار' : '⛔ تم تعطيل فلتر الأخبار'); loadAll(); }
  }catch(e){ alert('فشل: ' + e.message); }
}
async function newsRefresh(){
  try{
    const r = await (await fetch('/api/news-refresh', {method:'POST'})).json();
    alert(r.ok ? ('✅ حُدّث التقويم: ' + r.info) : ('⚠️ تعذر الجلب: ' + r.info));
    loadAll();
  }catch(e){ alert('فشل: ' + e.message); }
}
async function newsSave(){
  try{
    const payload = {
      impact_min: document.getElementById('newsImpact').value,
      before_min: parseInt(document.getElementById('newsBefore').value || '30', 10),
      after_min: parseInt(document.getElementById('newsAfter').value || '30', 10),
      currencies: document.getElementById('newsCur').value,
      windows: document.getElementById('newsWin').value
    };
    const r = await (await fetch('/api/news-settings', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})).json();
    if(r.ok){ alert('✅ حُفظت الإعدادات ووصلت للبوت فوراً'); loadAll(); }
    else alert('❌ فشل: ' + (r.error || ''));
  }catch(e){ alert('فشل: ' + e.message); }
}

async function sbrToggle(){
  try{
    const ov = await api('/api/overview');
    const target = !(ov.sbr && ov.sbr.live);
    const msg = target
      ? '⚔️ تفعيل التداول الفعلي لمحرك SBR-1؟\\nستُفتح صفقات فقط عند تحقق كل شروط الجودة (اختراق مؤكد + إعادة اختبار + R:R).\\nكل الحمايات تبقى مفعّلة: ستوب حقيقي + ستوب زمني + مدير مخاطر.\\nالإشارات المكتشفة قبل التفعيل لن تُنفَّذ بأثر رجعي.\\nمتابعة؟'
      : '👁️ تحويل SBR-1 إلى وضع الإشارات فقط؟\\nلن تُفتح صفقات جديدة.\\nمتابعة؟';
    if(!confirm(msg)) return;
    const r = await (await fetch('/api/sbr-toggle', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({live: target})})).json();
    if(r.ok){ alert(target ? '✅ تم تفعيل تداول SBR-1 — سيصطاد الاختراقات تلقائياً' : '👁️ عاد SBR-1 لوضع الإشارات فقط'); loadAll(); }
  }catch(e){ alert('فشل: ' + e.message); }
}

async function togglePause(){
  try{
    const ov = await api('/api/overview');
    await fetch(ov.trade_enabled ? '/api/pause' : '/api/resume', {method:'POST'});
    loadAll();
  }catch(e){ alert('فشل: '+e.message); }
}
async function closeAll(){
  if(!confirm('⚠️ إغلاق كل الصفقات فوراً بسعر السوق؟')) return;
  try{
    const r = await (await fetch('/api/close-all',{method:'POST'})).json();
    alert('أُغلق: ' + (r.closed.length ? r.closed.join(', ') : 'لا شيء'));
    loadAll();
  }catch(e){ alert('فشل: '+e.message); }
}

/* إعادة ضبط شامل — مسح كل السجلات (بدون لمس الصفقات المفتوحة) */
async function resetAll(){
  const NL = String.fromCharCode(10);
  const msg = '⚠️ إعادة ضبط شامل!' + NL + NL
    + 'سيتم مسح:' + NL
    + '🔔 كل الإشعارات' + NL
    + '📂 سجل الصفقات والإشارات' + NL
    + '🚫 سجل أسباب الرفض' + NL
    + '📊 الإحصائيات اليومية والإجماليات' + NL
    + '🚨 عدّادات الأخطاء' + NL + NL
    + '✅ لن تُغلق أي صفقة مفتوحة' + NL
    + '❌ لا يمكن التراجع! متابعة؟';
  if(!confirm(msg)) return;
  if(!confirm('❓ تأكيد أخير: هل أنت متأكد 100% من المسح الكامل؟')) return;
  try{
    const r = await (await fetch('/api/reset-all',{method:'POST'})).json();
    if(r.ok){
      lastNid = 0;
      document.getElementById('notifFeed').innerHTML = '';
      document.getElementById('liveFeed').innerHTML = '';
      document.getElementById('nCount').textContent = '0';
      alert('✅ تمت إعادة الضبط بنجاح!' + NL + 'الشاشة الآن نظيفة تماماً — بداية جديدة 🎯');
      loadAll();
    } else {
      alert('❌ فشل: ' + (r.error || 'خطأ غير معروف'));
    }
  }catch(e){ alert('❌ فشل الاتصال: ' + e.message); }
}

/* تفعيل أزرار إعادة محاولة الستوب (تفويض أحداث — بلا هروب معقد) */
document.addEventListener('click', function(e){
  const b = e.target.closest ? e.target.closest('button[data-sym]') : null;
  if(b && b.getAttribute('data-sym')) stopRetry(b.getAttribute('data-sym'));
});

async function boot(){
  try{
    await loadAll();
  }catch(e){
    document.querySelector('.sbar').innerHTML =
      '⚠️ <span style="color:var(--orange)">تعذر جلب البيانات: '+esc(e.message)+' — إعادة محاولة كل 5 ثوانٍ</span>';
  }
  if(!timer) timer = setInterval(()=>loadAll().catch(e=>console.error(e)), 10000);
}
boot();
</script>
</body>
</html>"""


# ═══════════════════ Backend ═══════════════════
class PanelDB:
    def __init__(self, db_name=None):
        volume_dir = os.environ.get('RAILWAY_VOLUME_MOUNT_PATH', '/data')
        os.makedirs(volume_dir, exist_ok=True)
        self.db_name = os.path.join(volume_dir, 'sniper_v9.db')

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
                        "SELECT id, ts, kind, title, body FROM notifications WHERE id > ? ORDER BY id DESC LIMIT ?",
                        (after_id, limit)) as cur:
                    rows = await cur.fetchall()
                async with db.execute("SELECT COUNT(*) c FROM notifications") as cur:
                    total = (await cur.fetchone())[0]
                return {
                    'items': [{
                        'id': r['id'], 'kind': r['kind'], 'title': r['title'], 'body': r['body'],
                        'time': libya_time_str(r['ts'], seconds=True),
                    } for r in reversed(rows)],
                    'last_id': max((r['id'] for r in rows), default=after_id),
                    'total_unread': total,
                }
        except Exception:
            return {'items': [], 'last_id': after_id, 'total_unread': 0}

    async def clear_all(self):
        try:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute("DELETE FROM notifications")
                await db.commit()
            return True
        except Exception:
            return False


PANEL_DB = None

async def notify(kind, title, body='', level='info'):
    if PANEL_DB:
        await PANEL_DB.add(kind, title, body, level)


# ═══════ 🧭 حسابات أداء الاستراتيجيات (قابلة للاختبار مباشرة) ═══════
async def compute_strategy_stats(db_path, active_trades=None,
                                 strategies=('SBR', 'HMA_DMI_MOMENTUM', 'UNKNOWN')):
    """حسابات أداء كل استراتيجية من قاعدة البيانات الفعلية — تعريفات موثقة:
    - signals: كل صفوف signal_log للاستراتيجية (أي حالة).
    - executed: الصفوف المغلقة بمصير نهائي (result >= 0: ربح/خسارة/محايدة).
    - wins/losses: result == 1 / 0 — المحايدة (2) لا تدخل نسبة الفوز.
    - net_pnl = مجموع pnl للمغلقة (مؤكدة أو تقديرية موسومة).
    - winrate = wins ÷ (wins+losses) — None عند غياب الصفقات الرابحة/الخاسرة.
    - avg_win/avg_loss: متوسط pnl للرابحة/الخاسرة فقط — None بلا بيانات.
    - profit_factor = Σ أرباح الرابحين ÷ |Σ خسائر الخاسرين| — None بلا خسائر.
    - max_drawdown = أقصى هبوط لمنحنى الأرباح المتراكم (ترتيب زمني) — None
      لأقل من صفقتين مغلقتين كي لا تُعرض أرقام مضللة.
    - open_now: صفقات مفتوحة الآن مملوكة للاستراتيجية (من حالة البوت الحية).
    يعيد (قائمة إحصاءات، آخر الصفقات المجمعة، أسباب الرفض مجمعة حسب الاستراتيجية)."""
    active_trades = active_trades or {}
    out = []
    recent_all = []
    rejections_groups = []
    try:
        async with aiosqlite.connect(db_path) as db:
            db.row_factory = aiosqlite.Row
            for strat in strategies:
                display = strat if strat != 'UNKNOWN' else 'UNKNOWN (مُتبنّى)'
                sig_count = closed_rows = None
                try:
                    async with db.execute("SELECT COUNT(*) c FROM signal_log WHERE strategy=?",
                                          (strat,)) as cur:
                        sig_count = (await cur.fetchone())[0]
                except Exception:
                    sig_count = 0
                try:
                    async with db.execute(
                            "SELECT symbol, direction, entry_ts, score, result, pnl, pnl_source "
                            "FROM signal_log WHERE strategy = ? AND result >= 0 "
                            "ORDER BY id DESC", (strat,)) as cur:
                        # 🛠️ إصلاح: بلا LIMIT — الإحصائيات من جميع الصفقات المغلقة
                        # (عرض آخر الصفقات وحده يُقتصر لاحقاً للعرض فقط)
                        closed_rows = await cur.fetchall()
                except Exception:
                    closed_rows = []
                closed_rows = closed_rows or []
                wins = sum(1 for r in closed_rows if r['result'] == 1)
                losses = sum(1 for r in closed_rows if r['result'] == 0)
                # نسبة الفوز: مقامها = الرابحة + الخاسرة فقط —
                # النتائج المحايدة (result==2) مستبعدة من المقام عمداً
                winrate = (round(wins / (wins + losses) * 100, 1)
                           if (wins + losses) > 0 else None)
                win_pnls = [float(r['pnl'] or 0) for r in closed_rows if r['result'] == 1]
                loss_pnls = [float(r['pnl'] or 0) for r in closed_rows if r['result'] == 0]
                net = sum(float(r['pnl'] or 0) for r in closed_rows)
                max_dd = None
                if len(closed_rows) >= 2:
                    eq = peak = dd = 0.0
                    for p in reversed(closed_rows):     # الأقدم أولاً — ترتيب زمني
                        eq += float(p['pnl'] or 0)
                        peak = max(peak, eq)
                        dd = max(dd, peak - eq)
                    max_dd = round(dd, 4)
                by_sym = {}
                for r in closed_rows:
                    by_sym[r['symbol']] = by_sym.get(r['symbol'], 0.0) + float(r['pnl'] or 0)
                top_syms = sorted(by_sym.items(), key=lambda x: -abs(x[1]))[:3]
                by_symbol = '، '.join(f"{s} ({v:+.2f}$)" for s, v in top_syms) if top_syms else None
                last_sig = '—'
                try:
                    async with db.execute(
                            "SELECT symbol, direction, entry_ts, components FROM signal_log "
                            "WHERE strategy = ? ORDER BY id DESC LIMIT 1", (strat,)) as cur:
                        lr = await cur.fetchone()
                    if lr:
                        trig = ''
                        try:
                            comp = json.loads(lr['components'] or '{}')
                            trig = comp.get('trigger') or comp.get('zone') or ''
                        except Exception:
                            pass
                        last_sig = f"{lr['symbol']} {lr['direction']} {libya_time_str(lr['entry_ts'])}"
                        if trig:
                            last_sig += f" — {str(trig)[:42]}"
                except Exception:
                    pass
                out.append({
                    '_key': strat, 'name': display,
                    'signals': sig_count or 0,
                    'executed': len(closed_rows),
                    'open_now': sum(1 for t in active_trades.values()
                                    if (t.get('strategy') or 'SBR') == strat),
                    'wins': wins, 'losses': losses,
                    'winrate': winrate,
                    'net_pnl': round(net, 4),
                    'avg_win': (round(sum(win_pnls) / len(win_pnls), 4)
                                if win_pnls else None),
                    'avg_loss': (round(sum(loss_pnls) / len(loss_pnls), 4)
                                 if loss_pnls else None),
                    'profit_factor': (round(sum(win_pnls) / abs(sum(loss_pnls)), 2)
                                      if win_pnls and loss_pnls and sum(loss_pnls) != 0
                                      else None),
                    'max_drawdown': max_dd,
                    'by_symbol': by_symbol,
                    'last_signal': last_sig,
                })
                for r in closed_rows[:15]:
                    recent_all.append({
                        'strategy': display,
                        'symbol': r['symbol'], 'direction': r['direction'],
                        'time': libya_time_str(r['entry_ts'] or time.time()),
                        'ts': float(r['entry_ts'] or 0),
                        'pnl': round(float(r['pnl'] or 0), 4),
                        'pnl_source': r['pnl_source'],
                    })
            for strat in strategies:
                try:
                    async with db.execute(
                            "SELECT reason, COUNT(*) c FROM scan_rejections "
                            "WHERE strategy = ? AND ts > ? GROUP BY reason ORDER BY c DESC LIMIT 8",
                            (strat, time.time() - 7 * 86400)) as cur:
                        c_rows = await cur.fetchall()
                    if c_rows:
                        rejections_groups.append({
                            'strategy': strat if strat != 'UNKNOWN' else 'UNKNOWN (مُتبنّى)',
                            'counts': [[r['reason'], r['c']] for r in c_rows]})
                except Exception:
                    continue
    except Exception:
        pass
    recent_all.sort(key=lambda x: -x.get('ts', 0))   # الأحدث أولاً عبر كل الاستراتيجيات
    for x in recent_all:
        x.pop('ts', None)
    return out, recent_all[:15], rejections_groups


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

        # 🛡️ مدير المخاطر — الحالة الحقيقية (محفوظة في القاعدة)
        try:
            can_trade, reason = bot.risk.can_trade()
            risk_data = {
                'can_trade': bool(can_trade),
                'reason': reason,
                'consecutive_losses': bot.risk.consecutive_losses,
                'daily_losses': bot.risk.daily_losses,
                'daily_pnl': bot.risk.daily_pnl,
                'initial_balance': bot.risk.initial_balance,
            }
        except Exception:
            risk_data = {'can_trade': True, 'reason': 'غير متاح',
                         'consecutive_losses': 0, 'daily_losses': 0,
                         'daily_pnl': 0.0, 'initial_balance': 0.0}

        # 📰 حالة فلتر الأخبار الكاملة
        try:
            news_status = bot.news_filter.status()
        except Exception:
            news_status = {'enabled': False, 'reason': 'غير متاح'}

        # 🛡️ صحة ستوبات الحماية — كما هي على المنصة فعلاً
        stop_health = {'total': 0, 'verified': 0, 'local': 0, 'failed': []}
        try:
            trades_live = list(getattr(bot, 'active_trades', {}).values())
            stop_health['total'] = len(trades_live)
            stop_health['verified'] = sum(1 for t in trades_live if t.get('stop_state') == 'verified')
            stop_health['local'] = sum(1 for t in trades_live if t.get('stop_state') == 'local')
            stop_health['placed'] = sum(1 for t in trades_live if t.get('stop_state') == 'placed')
            # قائمة المراكز الستوبها غير مؤكد على المنصة (تحذير صريح في اللوحة)
            stop_health['failed'] = [{'symbol': t.get('symbol')}
                                     for t in trades_live if t.get('stop_state') == 'local']
        except Exception:
            pass

        try:
            scan_status = bot.scan_status()
        except Exception:
            scan_status = {}

        st = bot.settings.status()
        sbr_data = {
            'live': bool(bot.SBR_LIVE),
            'max_hours': bot.MAX_TRADE_HOURS,
            'tp1_return_pct': st.get('tp1_return_pct', 20.0),
            'describe': bot.settings.describe(),
            'settings': st,
            'blacklist': bot.settings.blacklist(),
            # تعارضات متغيرات Railway مع القيم الفعالة (القاعدة هي المرجع)
            'env_conflicts': list(getattr(bot.settings, 'env_conflicts', []) or []),
        }

        # 🧭 حالة استراتيجية HMA_DMI_MOMENTUM
        try:
            hma_data = {
                'enabled': bool(getattr(bot, 'hma_enabled', False)),
                'live': bool(getattr(bot, 'HMA_LIVE', False)),
                'timeframe': bot.hma.timeframe,
                'describe': bot.hma.describe(),
                'settings': bot.hma.status(),
                'env_conflicts': list(getattr(bot.hma, 'env_conflicts', []) or []),
                # ⛔ فلتر V11.3: أزواج مستبعدة من HMA (ثابت كود في bot.py)
                'blacklist': list(getattr(bot, 'HMA_SYMBOL_BLACKLIST',
                                          HMA_SYMBOL_BLACKLIST)),
            }
        except Exception:
            hma_data = {'enabled': False, 'live': False, 'timeframe': '15m',
                        'describe': 'غير متاح', 'settings': {}, 'env_conflicts': [],
                        'blacklist': list(HMA_SYMBOL_BLACKLIST)}

        return j({
            'ok': True, 'trade_enabled': bot.TRADE_ENABLED, 'testnet': bot.TESTNET,
            'api_rejected': bool(getattr(bot, 'api_rejected', False)),
            'sbr': sbr_data,
            'hma': hma_data,
            'leverage': bot.LEVERAGE, 'trade_size': bot.TRADE_SIZE_USDT,
            'max_open': bot.MAX_OPEN_TRADES, 'pairs': len(bot.all_futures_pairs),
            'balance': round(balance, 2),
            'today': {'pnl': round(row[0], 4) if row else 0.0,
                      'wins': row[1] if row else 0, 'losses': row[2] if row else 0},
            'stats': dict(bot.stats), 'open_trades': len(bot.active_trades),
            'scans': bot.stats.get('total_scans', 0),
            'uptime': int((time.time() - PANEL_START) / 60),
            'price_age': int(time.time() - newest) if newest else 999999,
            'news_filter': news_status.get('enabled', False),
            'news': news_status,
            'stop_health': stop_health,
            'scan': scan_status,
            'risk': risk_data,
        })

    async def refresh_balance(request):
        try:
            balance = await bot.get_available_usdt()
        except Exception:
            balance = 0.0
        return j({'ok': True, 'balance': round(balance, 2)})

    async def trades(request):
        out = []
        for symbol, t in list(bot.active_trades.items()):
            try:
                prices = bot.get_price(symbol)
                cur = pnl = None
                if prices:
                    cur = prices['bid'] if t['side'] == 'BUY' else prices['ask']
                    diff = (cur - t['entry_price']) if t['side'] == 'BUY' else (t['entry_price'] - cur)
                    pnl = diff * t['quantity'] + t.get('realized_pnl', 0.0)
                entry = t.get('entry_price', 0) or 0
                sl = t.get('sl', 0) or 0
                tp = t.get('tp', 0) or 0
                risk = abs(entry - sl) if sl else 0
                reward = abs(tp - entry) if tp else 0
                rr = round(reward / risk, 2) if risk > 0 else None
                hours_in = (time.time() - t.get('entry_time', time.time())) / 3600.0
                out.append({
                    'symbol': symbol, 'side': t['side'], 'entry': round(entry, 6),
                    'current': round(cur, 6) if cur else None,
                    'pnl': round(pnl, 4) if pnl is not None else None,
                    'sl': round(sl, 6) if sl else None,
                    'tp': round(tp, 6) if tp else None,
                    'score': t.get('score', 0) or 0,
                    'rr': rr,
                    'hours_in': round(hours_in, 2),
                    'stop_state': t.get('stop_state', 'none'),
                    'stop_error': t.get('stop_error'),
                    'strategy': t.get('strategy') or 'SBR',
                })
            except Exception:
                continue
        return j(out)

    async def closed(request):
        out = []
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                db.row_factory = aiosqlite.Row
                rows = []
                try:   # مصدر النتيجة + الاستراتيجية — قواعد أقدم بلا الأعمدة
                    async with db.execute(
                            "SELECT symbol, direction, entry_ts, score, result, pnl, pnl_source, strategy "
                            "FROM signal_log WHERE result >= 0 ORDER BY id DESC LIMIT 50") as cur:
                        rows = await cur.fetchall()
                except Exception:
                    try:
                        async with db.execute(
                                "SELECT symbol, direction, entry_ts, score, result, pnl, pnl_source, NULL AS strategy "
                                "FROM signal_log WHERE result >= 0 ORDER BY id DESC LIMIT 50") as cur:
                            rows = await cur.fetchall()
                    except Exception:
                        async with db.execute(
                                "SELECT symbol, direction, entry_ts, score, result, pnl, NULL AS pnl_source, NULL AS strategy "
                                "FROM signal_log WHERE result >= 0 ORDER BY id DESC LIMIT 50") as cur:
                            rows = await cur.fetchall()
                for r in rows:
                    out.append({
                        'symbol': r['symbol'],
                        'direction': r['direction'],
                        'time': libya_time_str(r['entry_ts'] or time.time()),
                        'pnl': round(r['pnl'] or 0, 4),
                        'pnl_pct': round(((r['pnl'] or 0) / (bot.TRADE_SIZE_USDT if bot.TRADE_SIZE_USDT else 1) * 100), 1),
                        'score': r['score'] or 0,
                        'pnl_source': r['pnl_source'],
                        'strategy': r['strategy'] or 'SBR',
                    })
        except Exception:
            pass
        return j(out)

    async def signals(request):
        out = []
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                db.row_factory = aiosqlite.Row
                rows = []
                try:
                    async with db.execute(
                            "SELECT symbol, direction, entry_ts, score, components, result, pnl, strategy "
                            "FROM signal_log ORDER BY id DESC LIMIT 50") as cur:
                        rows = await cur.fetchall()
                except Exception:
                    async with db.execute(
                            "SELECT symbol, direction, entry_ts, score, components, result, pnl, NULL AS strategy "
                            "FROM signal_log ORDER BY id DESC LIMIT 50") as cur:
                        rows = await cur.fetchall()
                for r in rows:
                    comp = {}
                    try:
                        comp = json.loads(r['components'] or '{}')
                    except Exception:
                        pass
                    out.append({
                        'symbol': r['symbol'], 'direction': r['direction'],
                        'time': libya_time_str(r['entry_ts']),
                        'score': int(r['score'] or 0),
                        'trigger': comp.get('zone') or comp.get('trigger') or 'SBR-1',
                        'vol_ratio': comp.get('vol_ratio'),
                        'power': comp.get('power'),
                        'rr': comp.get('rr'),
                        'result': r['result'],
                        'pnl': round(r['pnl'], 4) if r['pnl'] is not None else None,
                        'strategy': r['strategy'] or 'SBR',
                    })
        except Exception:
            pass
        return j(out)

    async def rejections(request):
        """أسباب رفض العملات — من قاعدة البيانات فعلياً."""
        recent, counts = [], []
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                        "SELECT ts, symbol, reason FROM scan_rejections ORDER BY id DESC LIMIT 40") as cur:
                    rows = await cur.fetchall()
                recent = [{'time': libya_time_str(r['ts']),
                           'symbol': r['symbol'], 'reason': r['reason']} for r in rows]
                async with db.execute(
                        "SELECT reason, COUNT(*) c FROM scan_rejections "
                        "WHERE ts > ? GROUP BY reason ORDER BY c DESC LIMIT 12",
                        (time.time() - 86400,)) as cur:
                    c_rows = await cur.fetchall()
                counts = [[r['reason'], r['c']] for r in c_rows]
        except Exception:
            pass
        return j({'recent': recent, 'counts': counts})

    async def daily_performance(request):
        days = []
        total_closed = total_wins = 0
        agg_p = 0.0
        best = worst = None
        try:
            async with aiosqlite.connect(bot.db.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                        "SELECT date, realized_pnl, wins, losses FROM daily_stats "
                        "ORDER BY date DESC LIMIT 14") as cur:
                    rows = await cur.fetchall()

                for r in rows:
                    w = r['wins'] or 0
                    l = r['losses'] or 0
                    total = w + l
                    day_str = r['date']
                    day_trades = []
                    try:   # مصدر النتيجة لكل صفقة (مؤكد/تقديري) مع تراجع للقواعد الأقدم
                        async with db.execute(
                            "SELECT symbol, direction, pnl, result, pnl_source FROM signal_log "
                            "WHERE date(entry_ts, 'unixepoch', 'localtime') = ? AND result >= 0",
                            (day_str,)) as d_cur:
                            d_rows = await d_cur.fetchall()
                    except Exception:
                        async with db.execute(
                            "SELECT symbol, direction, pnl, result, NULL AS pnl_source FROM signal_log "
                            "WHERE date(entry_ts, 'unixepoch', 'localtime') = ? AND result >= 0",
                            (day_str,)) as d_cur:
                            d_rows = await d_cur.fetchall()
                    if True:
                        day_trades = [{
                            'symbol': dr['symbol'],
                            'direction': dr['direction'],
                            'pnl': round(dr['pnl'] or 0, 4),
                            'win': dr['result'] == 1,
                            'pnl_source': dr['pnl_source'],
                        } for dr in d_rows]
                    days.append({
                        'date': day_str,
                        'pnl': round(r['realized_pnl'] or 0, 4),
                        'wins': w, 'losses': l, 'total': total,
                        'winrate': round(w / total * 100, 1) if total > 0 else None,
                        'trades': day_trades
                    })

                async with db.execute(
                        "SELECT COUNT(*) c, COALESCE(SUM(realized_pnl),0) p FROM daily_stats "
                        "WHERE wins + losses > 0") as cur:
                    a = await cur.fetchone()
                    if a:
                        agg_p = a['p'] or 0.0

                async with db.execute(
                        "SELECT date, realized_pnl FROM daily_stats "
                        "WHERE wins + losses > 0 ORDER BY realized_pnl DESC LIMIT 1") as cur:
                    best = await cur.fetchone()
                async with db.execute(
                        "SELECT date, realized_pnl FROM daily_stats "
                        "WHERE wins + losses > 0 ORDER BY realized_pnl ASC LIMIT 1") as cur:
                    worst = await cur.fetchone()

                async with db.execute(
                        "SELECT COUNT(*) c FROM signal_log WHERE result >= 0") as cur:
                    total_closed = (await cur.fetchone())[0]
                async with db.execute(
                        "SELECT COUNT(*) c FROM signal_log WHERE result = 1") as cur:
                    total_wins = (await cur.fetchone())[0]
        except Exception:
            pass

        today = time.strftime('%Y-%m-%d')
        today_data = next((d for d in days if d['date'] == today), None)
        if not today_data:
            today_data = {'date': today, 'pnl': 0, 'wins': 0, 'losses': 0,
                          'total': 0, 'winrate': None, 'trades': []}
        return j({
            'ok': True,
            'today': today_data,
            'days': days,
            'aggregates': {
                'active_days': len(days),
                'total_pnl': round(agg_p, 4),
                'total_closed': total_closed,
                'total_wins': total_wins,
                'overall_winrate': round(total_wins / total_closed * 100, 1) if total_closed else None,
                'best_day': {'date': best['date'], 'pnl': round(best['realized_pnl'], 4)} if best else None,
                'worst_day': {'date': worst['date'], 'pnl': round(worst['realized_pnl'], 4)} if worst else None,
            },
            'trades_today_live': bot._trades_today(),
        })

    async def notifications(request):
        after = int(request.query.get('after', 0))
        if PANEL_DB:
            return j(await PANEL_DB.get_after(after))
        return j({'items': [], 'last_id': after, 'total_unread': 0})

    async def errors(request):
        return j({'errors': dict(bot.error_counts)})

    async def pause(request):
        bot.TRADE_ENABLED = False
        await notify('system', '⏸️ إيقاف مؤقت', 'تم إيقاف التداول من اللوحة — المراقبة مستمرة')
        return j({'ok': True})

    async def resume(request):
        if not bot.binance_api_key:
            return j({'ok': False, 'error': 'مفاتيح API ناقصة'}, status=400)
        bot.TRADE_ENABLED = True
        await notify('system', '▶️ استئناف', 'تم استئناف التداول من اللوحة')
        return j({'ok': True})

    async def close_all(request):
        closed_syms = []
        for symbol, t in list(bot.active_trades.items()):
            prices = bot.get_price(symbol)
            px = (prices['bid'] if t['side'] == 'BUY' else prices['ask']) if prices else t['entry_price']
            ok, fill, pnl_over = await bot._close_position(t, px)
            if ok:
                await bot._finalize_trade(t, fill, 'إغلاق طارئ من اللوحة', pnl_over)
                closed_syms.append(symbol)
        return j({'ok': True, 'closed': closed_syms})

    async def reset_all(request):
        cleared = []
        try:
            if PANEL_DB:
                await PANEL_DB.clear_all()
                cleared.append('الإشعارات')
            async with aiosqlite.connect(bot.db.db_name) as db:
                await db.execute("DELETE FROM signal_log")
                await db.execute("DELETE FROM daily_stats")
                await db.execute("DELETE FROM scan_rejections")
                await db.commit()
            cleared.append('سجل الصفقات والإشارات وأسباب الرفض')
            cleared.append('الإحصائيات اليومية')
            try:
                for k in list(bot.stats.keys()):
                    bot.stats[k] = 0
            except Exception:
                pass
            cleared.append('عدّادات الإحصائيات')
            try:
                bot.error_counts.clear()
            except Exception:
                pass
            cleared.append('عدّادات الأخطاء')
            await notify('system', '⚙️ إعادة ضبط شامل', 'تم مسح: ' + '، '.join(cleared))
            return j({'ok': True, 'cleared': cleared})
        except Exception as e:
            return j({'ok': False, 'error': str(e)}, status=500)

    async def stop_retry(request):
        try:
            body = await request.json()
        except Exception:
            body = {}
        symbol = body.get('symbol')
        t = bot.active_trades.get(symbol) if symbol else None
        if not t:
            return j({'ok': False, 'error': 'لا توجد صفقة مفتوحة بهذا الاسم'}, status=404)
        prices = bot.get_price(symbol)
        px = (prices['bid'] if t['side'] == 'BUY' else prices['ask']) if prices else t['entry_price']
        ok = await bot._sync_stop_order(t, px, force=True)
        if ok:
            try:
                await bot.db.save_trade(t)
            except Exception:
                pass
        return j({'ok': bool(ok), 'state': t.get('stop_state'),
                  'stop_error': t.get('stop_error'),
                  'stop_price': t.get('stop_synced_price')})

    async def news_toggle(request):
        try:
            body = await request.json()
        except Exception:
            body = {}
        nf = bot.news_filter
        nf.enabled = bool(body.get('enabled', not nf.enabled))
        await nf.save()
        await notify('system', '📰 فلتر الأخبار',
                     ('✅ تم التفعيل — كتم تلقائي حول الأحداث المؤثرة' if nf.enabled
                      else '⛔ تم التعطيل — التداول مستمر دائماً'))
        return j({'ok': True, 'news': nf.status()})

    async def news_settings(request):
        try:
            body = await request.json()
        except Exception:
            body = {}
        nf = bot.news_filter
        try:
            if 'before_min' in body: nf.before_min = max(0, min(240, int(body['before_min'])))
            if 'after_min' in body: nf.after_min = max(0, min(240, int(body['after_min'])))
            if 'impact_min' in body and body['impact_min'] in ('High', 'Medium'):
                nf.impact_min = body['impact_min']
            if 'currencies' in body: nf.currencies = str(body['currencies'])[:60].upper()
            if 'windows' in body: nf.set_windows(str(body['windows'])[:140])
        except Exception as e:
            return j({'ok': False, 'error': str(e)}, status=400)
        await nf.save()
        return j({'ok': True, 'news': nf.status()})

    async def news_refresh(request):
        ok, info = await bot.news_filter.refresh_calendar()
        return j({'ok': bool(ok), 'info': info, 'news': bot.news_filter.status()})

    async def sbr_toggle(request):
        """🎯 تفعيل/إيقاف التداول الفعلي لمحرك SBR-1 (يُحفظ في القاعدة)."""
        try:
            body = await request.json()
        except Exception:
            body = {}
        live = bool(body.get('live'))
        bot.SBR_LIVE = live
        try:
            await bot.db.set_param('sbr_live', '1' if live else '0')
        except Exception:
            pass
        await notify('system', '🎯 وضع SBR-1',
                     ('⚔️ تم تفعيل التداول الفعلي — الإشارات القديمة لن تُنفَّذ بأثر رجعي'
                      if live else '👁️ عاد الوضع للإشارات فقط'))
        return j({'ok': True, 'live': live})

    async def sbr_settings(request):
        """🎯 تعديل عتبات SBR والمسح — يُطبق لحظياً ويُحفظ في القاعدة."""
        try:
            body = await request.json()
        except Exception:
            body = {}
        if not isinstance(body, dict) or not body:
            return j({'ok': False, 'error': 'لا بيانات'}, status=400)
        changed = bot.settings.update(body)
        await bot.settings.save()
        if changed:
            await notify('system', '🎯 إعدادات SBR',
                         '✅ تحديث العتبات:\n' + '\n'.join(changed))
        return j({'ok': True, 'changed': changed, 'settings': bot.settings.status(),
                  'describe': bot.settings.describe()})

    async def sbr_import_env(request):
        """⬇️ استيراد صريح لقيم متغيرات Railway إلى الإعدادات الفعالة —
        بأمر من المالك (زر اللوحة) وبلا تغيير صامت لأولوية المصادر."""
        try:
            changed = bot.settings.import_env()
            await bot.settings.save()
            if changed:
                await notify('system', '🎯 استيراد قيم Railway',
                             '✅ طُبّقت قيم متغيرات البيئة على الإعدادات الفعالة:\n' + '\n'.join(changed))
            else:
                await notify('system', '🎯 استيراد قيم Railway',
                             'لا فروقات — الإعدادات الفعالة مطابقة لمتغيرات البيئة أصلاً')
            return j({'ok': True, 'changed': changed, 'settings': bot.settings.status(),
                      'describe': bot.settings.describe(),
                      'env_conflicts': list(getattr(bot.settings, 'env_conflicts', []) or [])})
        except Exception as e:
            return j({'ok': False, 'error': str(e)}, status=500)

    async def scan_now(request):
        try:
            async def _both():
                await bot.scan_market()
                try:
                    await bot.scan_hma()   # 🧭 دورة HMA فورية أيضاً
                except Exception:
                    pass
            asyncio.create_task(_both())
            return j({'ok': True, 'info': 'أُطلق مسح فوري للاستراتيجيتين'})
        except Exception as e:
            return j({'ok': False, 'error': str(e)}, status=500)

    # ═══ 🧭 نقاط نهاية استراتيجية HMA_DMI_MOMENTUM ═══
    async def strategies(request):
        """مقارنة الأداء وحالة الاستراتيجيات — من القاعدة فعلياً."""
        try:
            stats_list, recent, rej_groups = await compute_strategy_stats(
                bot.db.db_name, getattr(bot, 'active_trades', {}) or {})
        except Exception:
            stats_list, recent, rej_groups = [], [], []
        states = []
        for s in stats_list:
            key = s.get('_key')
            if key == 'SBR':
                states.append({'name': 'SBR',
                               'status': ('⚔️ تداول فعلي' if bot.SBR_LIVE else '👁️ إشارات فقط')
                                         + ' — نشطة دائماً',
                               'market_state': 'بلا آلة حالات (اختراق + إعادة اختبار)',
                               'last_signal': s.get('last_signal', '—')})
            elif key == HMA_STRATEGY_NAME:
                if not bot.hma_enabled:
                    mst = '⛔ معطلة — لا تولّد إشارات'
                else:
                    hs = getattr(bot, 'hma_states', {}) or {}
                    if hs:
                        cnt = {'BULL': 0, 'BEAR': 0, 'NEUTRAL': 0}
                        for v in hs.values():
                            st_ = v.get('state') if isinstance(v, dict) else None
                            if st_ in cnt:
                                cnt[st_] += 1
                        mst = (f"BULL: {cnt['BULL']} رمز | BEAR: {cnt['BEAR']} | "
                               f"محايد: {cnt['NEUTRAL']} (آخر مسح {bot.hma.timeframe})")
                    else:
                        mst = 'بانتظار أول مسح'
                states.append({'name': 'HMA_DMI_MOMENTUM',
                               'status': ('⛔ معطلة' if not bot.hma_enabled
                                          else ('⚔️ تداول فعلي' if bot.HMA_LIVE else '👁️ إشارات فقط')),
                               'market_state': mst,
                               'last_signal': s.get('last_signal', '—')})
            else:
                states.append({'name': s.get('name', key), 'status': '—',
                               'market_state': 'مركز مُتبنّى بلا مصدر معروف',
                               'last_signal': s.get('last_signal', '—')})
        try:
            hma_payload = {
                'enabled': bool(getattr(bot, 'hma_enabled', False)),
                'live': bool(getattr(bot, 'HMA_LIVE', False)),
                'timeframe': bot.hma.timeframe,
                'describe': bot.hma.describe(),
                'settings': bot.hma.status(),
                'env_conflicts': list(getattr(bot.hma, 'env_conflicts', []) or []),
                # ⛔ فلتر V11.3: أزواج مستبعدة من HMA (ثابت كود في bot.py)
                'blacklist': list(getattr(bot, 'HMA_SYMBOL_BLACKLIST',
                                          HMA_SYMBOL_BLACKLIST)),
            }
        except Exception:
            hma_payload = {'enabled': False, 'live': False, 'timeframe': '15m',
                           'describe': 'غير متاح', 'settings': {}, 'env_conflicts': [],
                           'blacklist': list(HMA_SYMBOL_BLACKLIST)}
        return j({'ok': True, 'strategies': stats_list, 'states': states,
                  'recent': recent, 'rejections': rej_groups, 'hma': hma_payload})

    async def hma_settings(request):
        """🧭 تعديل إعدادات HMA_DMI_MOMENTUM — لحظي ويُحفظ في القاعدة."""
        try:
            body = await request.json()
        except Exception:
            body = {}
        if not isinstance(body, dict) or not body:
            return j({'ok': False, 'error': 'لا بيانات'}, status=400)
        if 'timeframe' in body and body['timeframe'] not in bot.hma.TIMEFRAMES:
            return j({'ok': False, 'error': 'إطار زمني غير صالح (المسموح: 5m/15m/1h)'}, status=400)
        changed = bot.hma.update(body)
        await bot.hma.save()
        if changed:
            await notify('system', '🧭 إعدادات HMA_DMI_MOMENTUM',
                         '✅ تحديث الإعدادات:\n' + '\n'.join(changed))
        return j({'ok': True, 'changed': changed, 'settings': bot.hma.status(),
                  'describe': bot.hma.describe()})

    async def hma_toggle(request):
        """🧭 تفعيل/تعطيل استراتيجية HMA ككل (يُحفظ في القاعدة — يصمد لإعادة التشغيل)."""
        try:
            body = await request.json()
        except Exception:
            body = {}
        enabled = bool(body.get('enabled', not bot.hma_enabled))
        bot.hma_enabled = enabled
        try:
            await bot.db.set_param('hma_enabled', '1' if enabled else '0')
        except Exception:
            pass
        await notify('system', '🧭 وضع HMA_DMI_MOMENTUM',
                     ('✅ تم التفعيل — ستولّد إشاراتها مستقلة عن SBR'
                      if enabled else '⛔ تم التعطيل — الصفقات المفتوحة تبقى مُدارة'))
        return j({'ok': True, 'enabled': enabled})

    async def hma_live(request):
        """🧭 تفعيل/إيقاف التداول الفعلي لمحرك HMA (يُحفظ في القاعدة)."""
        try:
            body = await request.json()
        except Exception:
            body = {}
        live = bool(body.get('live'))
        bot.HMA_LIVE = live
        try:
            await bot.db.set_param('hma_live', '1' if live else '0')
        except Exception:
            pass
        await notify('system', '🧭 تداول HMA_DMI_MOMENTUM',
                     ('⚔️ تم تفعيل التداول الفعلي — الإشارات القديمة لن تُنفَّذ بأثر رجعي'
                      if live else '👁️ عاد الوضع للإشارات فقط'))
        return j({'ok': True, 'live': live})

    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/api/overview', overview)
    app.router.add_get('/api/balance', refresh_balance)
    app.router.add_get('/api/trades', trades)
    app.router.add_get('/api/closed', closed)
    app.router.add_get('/api/signals', signals)
    app.router.add_get('/api/rejections', rejections)
    app.router.add_get('/api/daily', daily_performance)
    app.router.add_get('/api/notifications', notifications)
    app.router.add_get('/api/errors', errors)
    app.router.add_post('/api/pause', pause)
    app.router.add_post('/api/resume', resume)
    app.router.add_post('/api/close-all', close_all)
    app.router.add_post('/api/reset-all', reset_all)
    app.router.add_post('/api/stop-retry', stop_retry)
    app.router.add_post('/api/news-toggle', news_toggle)
    app.router.add_post('/api/news-settings', news_settings)
    app.router.add_post('/api/news-refresh', news_refresh)
    app.router.add_post('/api/sbr-toggle', sbr_toggle)
    app.router.add_post('/api/sbr-settings', sbr_settings)
    app.router.add_post('/api/sbr-import-env', sbr_import_env)
    app.router.add_get('/api/strategies', strategies)
    app.router.add_post('/api/hma-settings', hma_settings)
    app.router.add_post('/api/hma-toggle', hma_toggle)
    app.router.add_post('/api/hma-live', hma_live)
    app.router.add_post('/api/scan-now', scan_now)
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
        print(f'🖥️ لوحة القناص V10.0 تعمل على المنفذ {port} — دخول مباشر')
        return True
    except Exception as e:
        print(f'⚠️ فشل اللوحة (البوت يكمل عمله): {e}')
        return False
