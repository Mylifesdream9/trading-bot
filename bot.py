"""
═══════════════════════════════════════════════════════════════════════
  🎯 القناص الأسطوري V12.4 — HMA Edition (استراتيجية HMA_DMI_MOMENTUM فقط)
═══════════════════════════════════════════════════════════════════════
  V12.4 = نفس محرك V12.2/V12.3 المُتحقق عليه — لوحة بهوية الإصدار القديم
  الأصلي (V11.1) بنفس الألوان والخط والبطاقات، مع إكمال آخر ما كان ناقصاً
  بعد مراجعة اللوحة الجديدة مقابل الملف القديم سطراً بسطر:
    1) تبويب ⚠️ الصفقات المقلقة (ستوب غير مؤكد / خسارة ≥35% / عمر يقترب
       من الستوب الزمني) مع أزرار الإغلاق و🔁 لكل صفقة.
    2) تبويب 📂 الصفقات: مفتوحة + مغلقة من القاعدة (Binance مؤكد/تقديري).
    3) تبويب 📡 الإشارات والرفض من قاعدة البيانات فعلياً + عدّادات 24س.
    4) تبويب 🔔 الإشعارات: كل الأحداث مع فلاتر النوع والبحث.
    5) تبويب 📅 الأداء اليومي: اليوم + 14 يوماً + إجماليات التاريخ.
    6) تبويب 🧭 الاستراتيجية: حالة + تعديل كل عتبات HMA لحظياً (يُحفظ في
       القاعدة) + تشخيص الكون السائل الكامل (لماذا قد يظهر أقل من 200).
    7) تبويب 🛡️ المخاطر + تبويب ⚙️ النظام (أخطاء + فلتر أخبار بتحكم مباشر
       تفعيل/تحديث تقويم + طوارئ كامل).
    8) 🌙 صمت نافذة المساء: لا رفض لكل رمز أثناء الحظر — حدث دورة واحد
       مُخنق كل 15 دقيقة (إصلاح طوفان السجل الذي شكا منه المالك).
    9) 🔭 تشخيص الكون: total/floor/pool_cap/spread_cut مع شرح صريح أن
       POOL/SIZE يعملان وأن أرضية السيولة هي المحدد الفعلي.
   10) 🧭 أداء الاستراتيجية عبر التاريخ من قاعدة البيانات فعلياً (نسبة
       الفوز باستثناء المحايد، صافي النتيجة، متوسط ربح/خسارة، Profit
       Factor، أقصى تراجع زمني، أفضل الرموز، آخر إشارة) + عدّاد آلة
       الحالات BULL/BEAR/محايد في بطاقة الحالة — كما في اللوحة القديمة.
  مبني جراحياً من الأصل الموثق بقرار المالك:

  ▸ استراتيجية HMA_DMI_MOMENTUM فقط — لا يوجد في هذا الملف أي مسار أو
    إعداد أو مفتاح يخص أي استراتيجية أخرى إطلاقاً.
  ▸ المسح: كون HMA السائل المستقل — HMA_UNIVERSE_POOL (افتراضي 150، ضُبط
    300) أعلى الأزواج سيولة، وHMA_UNIVERSE_SIZE (افتراضي 40، ضُبط 200،
    سقف الكود 200) حجم الكون الفعال — متغير البيئة يتقدم على القيمة
    المخزنة في القاعدة عند وجوده (مقبض النشر الحاسم).
  ▸ الصفقات المتزامنة: MAX_OPEN_TRADES (افتراضي 3، بين 1 و10).
  ▸ 🌙 حظر نافذة المساء: الدخول الجديد معطل 16:00–23:59 UTC — المخارج
    تعمل طوال اليوم. للتعطيل: HMA_BLOCK_EVENING=false (وللتخصيص:
    HMA_EVENING_START_UTC / HMA_EVENING_END_UTC).
  ▸ 📊 لوحة مراقبة مدمجة (بلا ملفات خارجية وبلا web_panel.py):
    - المنفذ: DASHBOARD_PORT ثم PORT (منصات النشر) ثم 8999 — على Railway
      يتبع PORT تلقائياً (8080) فيظهر على نطاق النشر مباشرة.
    - الحماية: DASHBOARD_TOKEN — بيانات اللوحة والأوامر تتطلب المفتاح.
    - تعرض: الحالة، نافذة المساء، مدير المخاطر، المراكز الحية بربحها
      العائم وستوب المنصة، سجل كل الأحداث مع سبب كل قرار (دورة/إشارة/
      رفض/دخول/خروج/خطأ/نبض/أخبار)، والإحصاءات.
    - 🕹️ أوامر المالك من اللوحة (كما في اللوحة القديمة):
      ⏸️ إيقاف التداول (طوارئ) / ▶️ استئناف — يمنع الجديد فقط.
      🛑 إغلاق صفقة واحدة أو الكل بسعر السوق (من جدول المراكز).
      🔍 مسح فوري الآن — يوقظ حلقة المسح فوراً. 🔁 إعادة محاولة تثبيت
      ستوب المنصة. 🧹 إعادة ضبط شاملة للسجلات (بلا لمس الصفقات).
    - كل الأوامر: POST /api/command وتتطلب نفس DASHBOARD_TOKEN.
    - ملف أحداث دائم: bot_events.jsonl (تدوير 30MB) للتدقيق لاحقاً.
  ▸ كل حمايات المخاطر كما هي بلا مساسة: ستوب المنصة + المراقبة المحلية،
    مدير المخاطر (3 متتالية → 4س | يومي 3 → بقية اليوم | سحب 5% → بقية
    اليوم)، فلتر الأخبار، إعادة التحقق اللحظي قبل التنفيذ، تبنّي المراكز
    اليتيمة، تبريد الرموز، منع تكرار الإشارات (يصمد لإعادة التشغيل)،
    الرصيد المرجعي، وضع Testnet، وإشعارات تيليجرام.
  ▸ التشغيل: python bot.py  ثم افتح اللوحة على منفذ النشر.
═══════════════════════════════════════════════════════════════════════
"""

from datetime import datetime

import asyncio, aiohttp, json, math, os, sys, time, logging, requests
import collections
import numpy as np
import pandas as pd
import hmac
import hashlib
import signal
from decimal import Decimal
from urllib.parse import urlencode
from logging.handlers import RotatingFileHandler
import websockets
import aiosqlite

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logger = logging.getLogger('SniperV10')
logger.setLevel(logging.INFO)


# ─── ⏰ توقيت ليبيا (UTC+2 ثابت) + نظام 12 ساعة صباحاً/مساءً في كل السجل ───
def _libya_logtime(*args):
    """محوّل وقت السجل — يقبل أي عدد من الوسائط."""
    try:
        from datetime import datetime, timezone, timedelta
        ts = args[-1] if args else None
        try:
            ts = float(ts) if ts is not None else None
        except (TypeError, ValueError):
            ts = None
        if ts is None:
            ts = time.time()
        return datetime.fromtimestamp(ts, timezone(timedelta(hours=2))).timetuple()
    except Exception:
        return time.localtime()


class _LibyaTimeFormatter(logging.Formatter):
    """فورماتر السجل: توقيت ليبيا + 12 ساعة + صباحاً/مساءً."""
    converter = staticmethod(_libya_logtime)

    def formatTime(self, record, datefmt=None):
        try:
            from datetime import datetime, timezone, timedelta
            dt = datetime.fromtimestamp(record.created, timezone(timedelta(hours=2)))
            return dt.strftime('%d-%m-%Y %I:%M:%S') + (' صباحاً' if dt.hour < 12 else ' مساءً')
        except Exception:
            return time.strftime('%d-%m-%Y %I:%M:%S %p')


def libya_time_str(ts=None, seconds=False):
    """سلسلة زمنية للعرض بتوقيت ليبيا (12 ساعة + صباحاً/مساءً)."""
    try:
        from datetime import datetime, timezone, timedelta
        ts = time.time() if ts is None else float(ts)
        dt = datetime.fromtimestamp(ts, timezone(timedelta(hours=2)))
    except Exception:
        return time.strftime('%m-%d %H:%M')
    fmt = '%m-%d %I:%M:%S' if seconds else '%m-%d %I:%M'
    return dt.strftime(fmt) + (' صباحاً' if dt.hour < 12 else ' مساءً')


fmt = _LibyaTimeFormatter('%(asctime)s - %(levelname)s - %(message)s')
fh = RotatingFileHandler('bot_v8.log', maxBytes=2*1024*1024, backupCount=2, encoding='utf-8')
fh.setFormatter(fmt); logger.addHandler(fh)
ch = logging.StreamHandler(); ch.setFormatter(fmt); logger.addHandler(ch)


# ─── فحص الـ IP الصادر عند الإقلاع ───
def check_outbound_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        ip_address = response.json().get('ip')
        logger.info(f"Current Outbound IP on Railway: {ip_address}")
        return ip_address
    except Exception as e:
        logger.warning(f"Failed to fetch IP: {e}")
        return None


check_outbound_ip()


# ═══════════════════════ لوحة المراقبة المدمجة (V12.4 — هوية الإصدار القديم) ═══════════════════════
# خادم HTTP مدمج بلا مكتبات خارجية — بديل كامل عن اللوحة الخارجية القديمة.
# المنفذ: DASHBOARD_PORT ثم PORT (منصات النشر) ثم 8999.
# الحماية: DASHBOARD_TOKEN — إذا ضُبط تتطلب /api/state و /api/command المفتاح.
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs


class ActionLog:
    """سجل أحداث اللوحة: ذاكرة دائرية + ملف bot_events.jsonl دائم (بلا لمس الصفقات)."""

    def __init__(self, max_events=1500, path='bot_events.jsonl',
                 max_bytes=30 * 1024 * 1024):
        self._events = collections.deque(maxlen=max_events)
        self._lock = threading.Lock()
        self._path = path
        self._max_bytes = max_bytes

    def log(self, kind, msg, reason='', symbol=None, detail=''):
        ev = {'t': int(time.time()), 'kind': str(kind)[:12],
              'msg': str(msg)[:400], 'reason': str(reason)[:400],
              'symbol': (str(symbol)[:24] if symbol else None),
              'detail': str(detail)[:2000]}
        with self._lock:
            self._events.append(ev)
            try:
                if os.path.exists(self._path) and os.path.getsize(self._path) > self._max_bytes:
                    os.replace(self._path, self._path + '.old')
                with open(self._path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(ev, ensure_ascii=False) + '\n')
            except Exception:
                pass

    def clear(self):
        """مسح شامل: الذاكرة + الملف — لا يلمس الصفقات المفتوحة إطلاقاً."""
        with self._lock:
            self._events.clear()
            try:
                if os.path.exists(self._path):
                    os.remove(self._path)
            except Exception:
                pass

    def snapshot(self, limit=400):
        with self._lock:
            evs = list(self._events)[-max(1, int(limit)):]
        return evs


ACTION = ActionLog()
DASH_STATE = {}                                    # آخر لقطة حالة يكتبها البوت
DASH_TOKEN = os.environ.get('DASHBOARD_TOKEN', '')
DASH_PORT = int(os.environ.get('DASHBOARD_PORT') or os.environ.get('PORT') or 8999)
_ALLOWED_COMMANDS = ('pause', 'resume', 'close_one', 'close_all',
                     'reset_all', 'scan_now', 'stop_retry',
                     'hma_settings', 'news_toggle', 'news_refresh')


class _DashBridge:
    """جسر آمن من خيط HTTP إلى حلقة asyncio للبوت — تنفيذ أوامر المالك."""

    def __init__(self):
        self._loop = None
        self._bot = None

    def bind(self, loop, bot):
        self._loop = loop
        self._bot = bot

    def ready(self):
        return self._loop is not None and self._bot is not None

    def run(self, action, symbol=None, data=None, timeout=180):
        if not self.ready():
            return False, 'الجسر غير جاهز — انتظر إقلاع البوت كاملاً ثم أعد المحاولة'
        try:
            fut = asyncio.run_coroutine_threadsafe(
                self._bot.panel_command(action, symbol, data), self._loop)
            return True, fut.result(timeout=timeout)
        except Exception as e:
            return False, f'تعذر تنفيذ الأمر: {e}'


DASH_BRIDGE = _DashBridge()

_DASHBOARD_HTML = r"""<!DOCTYPE html>
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
var PANEL_STANDALONE=false;
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
"""


class _DashboardHandler(BaseHTTPRequestHandler):
    server_version = 'HMA-Dash/12.3'

    def log_message(self, fmt, *args):      # لا تلوث سجل البوت بطلبات اللوحة
        pass

    def _key_ok(self, qs):
        if not DASH_TOKEN:
            return True
        k = ''
        try:
            k = (qs.get('key') or [''])[0]
        except Exception:
            k = ''
        if not k:
            k = self.headers.get('X-Dash-Key', '')
        return k == DASH_TOKEN

    def _cors(self):
        origin = self.headers.get('Origin', '')
        if origin in ('', 'null') or 'localhost' in origin or '127.0.0.1' in origin:
            self.send_header('Access-Control-Allow-Origin', origin or '*')

    def _send(self, code_, body, ctype='application/json; charset=utf-8'):
        data = body if isinstance(body, bytes) else body.encode('utf-8')
        self.send_response(code_)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self._cors()
        self.end_headers()
        try:
            self.wfile.write(data)
        except Exception:
            pass

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Dash-Key')
        self.send_header('Access-Control-Max-Age', '86400')
        self._cors()
        self.end_headers()

    def do_GET(self):
        try:
            u = urlparse(self.path)
            qs = parse_qs(u.query)
            if u.path == '/health':
                self._send(200, '{"ok":true}')
                return
            if u.path == '/':
                self._send(200, _DASHBOARD_HTML, 'text/html; charset=utf-8')
                return
            if u.path == '/api/state':
                if not self._key_ok(qs):
                    self._send(401, '{"error":"مفتاح مفقود أو خاطئ"}')
                    return
                try:
                    limit = max(1, min(1500, int((qs.get('limit') or ['400'])[0])))
                except Exception:
                    limit = 400
                payload = {'state': dict(DASH_STATE), 'events': ACTION.snapshot(limit),
                           'now': int(time.time())}
                self._send(200, json.dumps(payload, ensure_ascii=False))
                return
            self._send(404, '{"error":"غير موجود"}')
        except Exception:
            try:
                self._send(500, '{"error":"خطأ داخلي"}')
            except Exception:
                pass

    def do_POST(self):
        try:
            u = urlparse(self.path)
            qs = parse_qs(u.query)
            if u.path != '/api/command':
                self._send(404, '{"error":"غير موجود"}')
                return
            if not self._key_ok(qs):
                self._send(401, '{"error":"مفتاح مفقود أو خاطئ"}')
                return
            try:
                length = int(self.headers.get('Content-Length') or 0)
                body = json.loads(self.rfile.read(length).decode('utf-8') or '{}')
            except Exception:
                body = {}
            action = str(body.get('action') or '').strip()
            symbol = body.get('symbol')
            data = body.get('data') if isinstance(body.get('data'), dict) else None
            if action not in _ALLOWED_COMMANDS:
                self._send(400, json.dumps(
                    {'ok': False, 'error': f'أمر غير معروف: {action or "فارغ"}'},
                    ensure_ascii=False))
                return
            if action in ('close_one', 'stop_retry') and not symbol:
                self._send(400, json.dumps(
                    {'ok': False, 'error': 'هذا الأمر يتطلب الرمز'}, ensure_ascii=False))
                return
            if not DASH_BRIDGE.ready():
                self._send(503, json.dumps(
                    {'ok': False,
                     'error': 'الجسر غير جاهز — انتظر إقلاع البوت كاملاً ثم أعد'},
                    ensure_ascii=False))
                return
            ACTION.log('نظام', f'🕹️ أمر من اللوحة: {action}'
                       + (f' ({symbol})' if symbol else ''))
            ok, info = DASH_BRIDGE.run(action, symbol, data)
            payload = {'ok': bool(ok)}
            payload['info' if ok else 'error'] = str(info)
            self._send(200, json.dumps(payload, ensure_ascii=False))
        except Exception as e:
            try:
                self._send(500, json.dumps({'ok': False, 'error': str(e)},
                                           ensure_ascii=False))
            except Exception:
                pass


def _dash_start():
    """تشغيل خادم اللوحة في خيط daemon — فشله لا يوقف البوت أبداً."""
    try:
        if os.environ.get('DASHBOARD_ENABLED', 'true').lower() == 'false':
            logger.info('🖥️ لوحة المراقبة معطلة (DASHBOARD_ENABLED=false)')
            return
        httpd = ThreadingHTTPServer(('0.0.0.0', DASH_PORT), _DashboardHandler)
        threading.Thread(target=httpd.serve_forever, daemon=True,
                         name='dashboard-http').start()
        logger.info(f"🖥️ لوحة المراقبة المدمجة تعمل على المنفذ {DASH_PORT}"
                    + (' 🔒 محمية بمفتاح DASHBOARD_TOKEN' if DASH_TOKEN
                       else ' ⚠️ بلا مفتاح — ضع DASHBOARD_TOKEN للحماية'))
    except Exception as e:
        logger.error(f"❌ فشل تشغيل لوحة المراقبة: {e}")


# ═══════════════════════ قاعدة البيانات ═════════════════════
class DatabaseManager:
    """
    نفس ملف القاعدة (sniper_v9.db) كي تُحفظ بيانات المالك التاريخية.
    جداول: active_trades (مبسّطة — بلا TP2/جزئي)، daily_stats، bot_params،
    signal_log، scan_rejections (سجل أسباب رفض العملات للوحة).
    """

    def __init__(self, db_name=None):
        volume_dir = os.environ.get('RAILWAY_VOLUME_MOUNT_PATH', '/data')
        os.makedirs(volume_dir, exist_ok=True)
        self.db_name = os.path.join(volume_dir, 'sniper_v9.db')

    async def init_db(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS active_trades (
                symbol TEXT PRIMARY KEY, side TEXT, entry_price REAL, quantity REAL,
                sl REAL, tp REAL, highest_price REAL, lowest_price REAL,
                entry_time REAL, realized_pnl REAL DEFAULT 0,
                stop_order_id INTEGER, tp_order_id INTEGER,
                stop_state TEXT, stop_error TEXT)""")
            await db.execute("""CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY, realized_pnl REAL, wins INTEGER, losses INTEGER)""")
            await db.execute("""CREATE TABLE IF NOT EXISTS bot_params (
                key TEXT PRIMARY KEY, value TEXT)""")
            await db.execute("""CREATE TABLE IF NOT EXISTS signal_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, direction TEXT,
                entry_ts REAL, score REAL, components TEXT,
                result INTEGER DEFAULT -1, pnl REAL, pnl_source TEXT)""")
            try:   # قواعد بيانات أقدم: إضافة عمود مصدر النتيجة (مؤكد/تقديري)
                await db.execute("ALTER TABLE signal_log ADD COLUMN pnl_source TEXT")
            except Exception:
                pass
            await db.execute("""CREATE TABLE IF NOT EXISTS scan_rejections (
                id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, symbol TEXT,
                reason TEXT, details TEXT)""")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_rej_ts ON scan_rejections(ts)")
            # ─── ترحيلات آمنة لتتبع مصدر الإشارة/الصفقة (استراتيجيتان مستقلتان) ───
            # ALTER فقط — لا حذف ولا إعادة إنشاء: بيانات المالك القديمة محفوظة
            # والصفوف القديمة تُنسب للاستراتيجية النشطة الوحيدة.
            for _mig in (
                "ALTER TABLE active_trades ADD COLUMN strategy TEXT DEFAULT 'HMA_DMI_MOMENTUM'",
                "ALTER TABLE signal_log ADD COLUMN strategy TEXT DEFAULT 'HMA_DMI_MOMENTUM'",
                "ALTER TABLE scan_rejections ADD COLUMN strategy TEXT DEFAULT 'HMA_DMI_MOMENTUM'",
            ):
                try:
                    await db.execute(_mig)
                except Exception:
                    pass   # العمود موجود مسبقاً — الترحيل مكتمل سابقاً
            try:
                await db.execute("CREATE INDEX IF NOT EXISTS idx_signal_strategy ON signal_log(strategy)")
            except Exception:
                pass
            await db.commit()

    async def get_param(self, key):
        try:
            async with aiosqlite.connect(self.db_name) as db:
                async with db.execute("SELECT value FROM bot_params WHERE key=?", (key,)) as cur:
                    row = await cur.fetchone()
                    return row[0] if row else None
        except Exception:
            return None

    async def set_param(self, key, value):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("INSERT OR REPLACE INTO bot_params (key, value) VALUES (?,?)", (key, value))
            await db.commit()

    async def log_signal(self, symbol, direction, entry_ts, score, components, strategy=None):
        """تسجيل إشارة موسوماً باسم الاستراتيجية التي أصدرتها."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute(
                    "INSERT INTO signal_log (symbol, direction, entry_ts, score, components, strategy) "
                    "VALUES (?,?,?,?,?,?)",
                    (symbol, direction, entry_ts, score, json.dumps(components, ensure_ascii=False),
                     str(strategy or HMA_STRATEGY_NAME)[:32]))
                await db.commit()
        except Exception as e:
            logger.warning(f"تعذر تسجيل الإشارة: {e}")

    async def set_signal_result(self, symbol, entry_ts, win, pnl, source=None, strategy=None):
        """win: 1 ربح | 0 خسارة | 2 محايدة/غير محسوبة — source: binance/estimated.
        strategy: تصفية النتيجة على صفوف الاستراتيجية نفسها كي لا تختلط
        نتائج الاستراتيجيتين على نفس الرمز."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                if strategy:
                    await db.execute(
                        "UPDATE signal_log SET result=?, pnl=?, pnl_source=? "
                        "WHERE symbol=? AND entry_ts=? AND result=-1 AND (strategy=? OR strategy IS NULL)",
                        (int(win) if win is not None else 2, pnl, source, symbol, entry_ts,
                         str(strategy)[:32]))
                else:
                    await db.execute(
                        "UPDATE signal_log SET result=?, pnl=?, pnl_source=? WHERE symbol=? AND entry_ts=? AND result=-1",
                        (int(win) if win is not None else 2, pnl, source, symbol, entry_ts))
                await db.commit()
        except Exception as e:
            logger.warning(f"تعذر تحديث نتيجة الإشارة: {e}")

    async def log_rejection(self, symbol, reason, details='', strategy=None):
        """سجل أسباب الرفض موسوماً بالاستراتيجية (استراتيجية/مخاطر/أخبار/تنفيذ)."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute(
                    "INSERT INTO scan_rejections (ts, symbol, reason, details, strategy) VALUES (?,?,?,?,?)",
                    (time.time(), str(symbol)[:24], str(reason)[:140], str(details)[:200],
                     str(strategy or HMA_STRATEGY_NAME)[:32]))
                await db.commit()
        except Exception as e:
            logger.warning(f"تعذر تسجيل الرفض: {e}")

    async def prune_rejections(self, max_age_s=3 * 86400):
        try:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute("DELETE FROM scan_rejections WHERE ts < ?", (time.time() - max_age_s,))
                await db.commit()
        except Exception:
            pass

    async def save_trade(self, t):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""INSERT OR REPLACE INTO active_trades
                (symbol, side, entry_price, quantity, sl, tp, highest_price, lowest_price,
                 entry_time, realized_pnl, stop_order_id, tp_order_id, stop_state, stop_error, strategy)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (t['symbol'], t['side'], t['entry_price'], t['quantity'],
                 t['sl'], t.get('tp'), t.get('highest_price', 0), t.get('lowest_price', 999999),
                 t['entry_time'], float(t.get('realized_pnl', 0.0)),
                 t.get('stop_order_id'), t.get('tp_order_id'),
                 t.get('stop_state', 'none'), t.get('stop_error'),
                 str(t.get('strategy') or HMA_STRATEGY_NAME)[:32]))
            await db.commit()

    async def load_active_trades(self):
        """تحميل متسامح: يعمل مع الجدول الجديد المبسّط ومع جدول V9 القديم
        (أعمدة إضافية مثل tp2/partial_closed تُتجاهل — الكمية المتبقية هي
        المرجع دائماً)."""
        trades = {}
        try:
            async with aiosqlite.connect(self.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""SELECT symbol, side, entry_price, quantity, sl, tp,
                    highest_price, lowest_price, entry_time, realized_pnl,
                    stop_order_id, tp_order_id, stop_state, stop_error, strategy
                    FROM active_trades""") as cur:
                    async for row in cur:
                        trades[row['symbol']] = {
                            'symbol': row['symbol'], 'side': row['side'],
                            'strategy': row['strategy'] or HMA_STRATEGY_NAME,
                            'entry_price': row['entry_price'], 'quantity': row['quantity'],
                            'sl': row['sl'], 'tp': row['tp'],
                            'highest_price': row['highest_price'] or 0,
                            'lowest_price': row['lowest_price'] or 999999,
                            'entry_time': row['entry_time'],
                            'realized_pnl': row['realized_pnl'] if row['realized_pnl'] is not None else 0.0,
                            'stop_order_id': row['stop_order_id'],
                            'tp_order_id': row['tp_order_id'],
                            'stop_state': row['stop_state'] or 'none',
                            'stop_error': row['stop_error'],
                            'stop_synced_price': None,
                        }
        except Exception as e:
            logger.error(f"❌ فشل تحميل الصفقات من القاعدة: {e}")
        return trades

    async def remove_trade(self, symbol):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("DELETE FROM active_trades WHERE symbol=?", (symbol,))
            await db.commit()

    async def update_daily_pnl(self, pnl, is_win=None):
        today = time.strftime("%Y-%m-%d")
        w = 1 if is_win is True else 0
        l = 1 if is_win is False else 0
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT * FROM daily_stats WHERE date=?", (today,)) as cur:
                row = await cur.fetchone()
            if row:
                await db.execute("UPDATE daily_stats SET realized_pnl=?, wins=?, losses=? WHERE date=?",
                    (row[1] + pnl, row[2] + w, row[3] + l, today))
            else:
                await db.execute("INSERT INTO daily_stats VALUES (?,?,?,?)", (today, pnl, w, l))
            await db.commit()

    async def get_day_stats(self, day):
        try:
            async with aiosqlite.connect(self.db_name) as db:
                async with db.execute(
                        "SELECT realized_pnl, wins, losses FROM daily_stats WHERE date=?", (day,)) as cur:
                    return await cur.fetchone()
        except Exception:
            return None


# 🔭 ثوابت مسح HMA (كون السائل — قابلة للضبط بمتغيرات البيئة):
HMA_SCAN_MIN_VOL_USDT = float(os.environ.get('HMA_SCAN_MIN_VOL_USDT', '30000000'))
HMA_UNIVERSE_POOL = int(os.environ.get('HMA_UNIVERSE_POOL', '150'))
HMA_MAX_SPREAD_PCT = float(os.environ.get('HMA_MAX_SPREAD_PCT', '0.15'))

# 🌙 حظر نافذة المساء (اعتماد المالك — نتيجة تقرير تشخيص HMA على 30 يوماً):
# الدخول الجديد معطل بين 16:00 و23:59 UTC — النافذة الأكثر خسارة موثقاً
# في التشخيص. إدارة المخارج (صفقات HMA المفتوحة) تعمل طوال اليوم كالمعتاد.
# للتعطيل: HMA_BLOCK_EVENING=false | للتخصيص: HMA_EVENING_START_UTC/END
HMA_BLOCK_EVENING_UTC = os.environ.get('HMA_BLOCK_EVENING', 'true').lower() != 'false'
HMA_EVENING_START_UTC = int(os.environ.get('HMA_EVENING_START_UTC', '16'))
HMA_EVENING_END_UTC = int(os.environ.get('HMA_EVENING_END_UTC', '23'))

# 🧭 V11.3 — قائمة الأزواج المستبعدة من HMA (اعتماد المالك):
# خاسرة مزمنة على النافذتين المستقلتين معاً (IS وOOS) — قاعدة النافذتين
# صفقات HMA المفتوحة سابقاً على هذه الأزواج تُدار بمخارجها حتى الإغلاق —
# الفلتر يمنع الإشارات الجديدة فقط.
HMA_SYMBOL_BLACKLIST = ('ETHUSDT', 'BNBUSDT', 'AVAXUSDT')


# ═══════════════════════ مدير المخاطر (مع حفظ الحالة في القاعدة) ═══════════════════════
class RiskManager:
    """
    حماية رأس المال — لا يمكن تجاوزها بإعادة تشغيل البوت لأن حالتُها
    تُحفظ في القاعدة وتُستعاد عند الإقلاع:
    - 3 خسائر متتالية → توقف 4 ساعات
    - 3 خسائر في اليوم → توقف بقية اليوم
    - سحب يومي 5% من الرصيد المرجعي → توقف بقية اليوم
    """
    MAX_CONSEC_LOSSES = 3
    PAUSE_HOURS = 4
    MAX_DAILY_LOSSES = 3
    MAX_DAILY_DRAWDOWN_PCT = 5.0

    def __init__(self, db=None):
        self.db = db
        self.consecutive_losses = 0
        self.daily_losses = 0
        self.daily_pnl = 0.0
        self.initial_balance = 0.0
        self.pause_until = 0.0
        self._day = time.strftime('%Y-%m-%d')

    def _rollover_day(self):
        today = time.strftime('%Y-%m-%d')
        if today != self._day:
            self._day = today
            self.daily_losses = 0
            self.daily_pnl = 0.0

    async def load(self):
        if not self.db:
            return
        raw = await self.db.get_param('risk_state')
        if not raw:
            return
        try:
            d = json.loads(raw)
            if d.get('day') == self._day:      # حالة أمس لا تُستعاد (إعادة ضبط يومية سليمة)
                self.consecutive_losses = max(0, int(d.get('consecutive_losses', 0)))
                self.daily_losses = max(0, int(d.get('daily_losses', 0)))
                self.daily_pnl = float(d.get('daily_pnl', 0.0))
                self.pause_until = float(d.get('pause_until', 0.0))
                self.initial_balance = float(d.get('initial_balance', 0.0))
                if self.pause_until > time.time():
                    mins = int((self.pause_until - time.time()) / 60)
                    logger.warning(f"🛡️ مدير المخاطر: استئناف إيقاف قائم — يتبقى {mins} دقيقة")
        except Exception as e:
            logger.warning(f"تعذر استعادة حالة مدير المخاطر: {e}")

    async def save(self):
        if not self.db:
            return
        try:
            await self.db.set_param('risk_state', json.dumps({
                'day': self._day,
                'consecutive_losses': self.consecutive_losses,
                'daily_losses': self.daily_losses,
                'daily_pnl': self.daily_pnl,
                'pause_until': self.pause_until,
                'initial_balance': self.initial_balance,
            }))
        except Exception as e:
            logger.warning(f"تعذر حفظ حالة مدير المخاطر: {e}")

    async def register_result(self, pnl):
        """تسجيل نتيجة صفقة مغلقة + حفظ الحالة فوراً."""
        self._rollover_day()
        pnl = float(pnl or 0.0)
        self.daily_pnl += pnl
        if pnl < 0:
            self.consecutive_losses += 1
            self.daily_losses += 1
            if self.consecutive_losses >= self.MAX_CONSEC_LOSSES:
                self.pause_until = time.time() + self.PAUSE_HOURS * 3600
                logger.warning(f"🛡️ {self.MAX_CONSEC_LOSSES} خسائر متتالية — توقف {self.PAUSE_HOURS} ساعات")
        elif pnl > 0:
            self.consecutive_losses = 0
        await self.save()

    def can_trade(self):
        """يعيد (مسموح؟، السبب) — يُعرض في اللوحة مباشرة."""
        self._rollover_day()
        now = time.time()
        if now < self.pause_until:
            mins = int((self.pause_until - now) / 60)
            return False, f"⏸️ توقف بعد {self.MAX_CONSEC_LOSSES} خسائر متتالية — يستأنف بعد {mins} دقيقة"
        if self.daily_losses >= self.MAX_DAILY_LOSSES:
            return False, f"🛑 تحقق الحد اليومي ({self.MAX_DAILY_LOSSES} خسائر) — توقف بقية اليوم"
        if (self.initial_balance > 0 and self.daily_pnl < 0
                and abs(self.daily_pnl) >= self.initial_balance * self.MAX_DAILY_DRAWDOWN_PCT / 100):
            return False, f"🛑 سحب يومي {self.MAX_DAILY_DRAWDOWN_PCT}% — توقف بقية اليوم"
        return True, "✅ مسموح"


# ═══════════════════════ فلتر الأخبار (كما هو — مُدار من اللوحة) ═══════════════════════
class NewsFilter:
    """
    فلتر حقيقي بمصدر حي: تقويم ForexFactory الأسبوعي (JSON مجاني بدون مفتاح)
    - يُجلب كل 4 ساعات ويشمل CPI/FOMC/NFP وكل أحداث الماكرو المؤثرة
    - كتم الإشارات تلقائياً قبل/بعد الأحداث المطابقة (تأثير + عملة)
    - كل الإعدادات في قاعدة البيانات → تُعدّل من اللوحة لحظياً
    - نوافذ يدوية إضافية بتوقيت UTC "HH:MM-HH:MM,..." (اختياري)
    - فشل الجلب لا يوقف التداول (Fail-open) وحالة الجلب تُعرض في اللوحة
    - تعطيله من اللوحة يعني عدم كتم أي إشارة أبداً (كما هو متوقع)
    """
    CALENDAR_URL = 'https://nfs.faireconomy.media/ff_calendar_thisweek.json'
    CALENDAR_TTL = 4 * 3600
    IMPACT_RANK = {'Holiday': 0, 'Low': 1, 'Medium': 2, 'High': 3}

    def __init__(self, db=None):
        self.db = db
        self.enabled = True
        self.impact_min = 'High'
        self.currencies = 'USD'
        self.before_min = 30
        self.after_min = 30
        self.blackout_windows = []
        self.events = []
        self.calendar_updated = 0.0
        self.last_fetch_ok = False
        self.last_error = None
        self.rejected_total = 0

    async def load(self):
        raw = None
        if self.db:
            raw = await self.db.get_param('news_filter')
        if raw:
            try:
                d = json.loads(raw)
                self.enabled = bool(d.get('enabled', True))
                self.impact_min = d.get('impact_min', 'High')
                self.currencies = d.get('currencies', 'USD')
                self.before_min = max(0, min(240, int(d.get('before_min', 30))))
                self.after_min = max(0, min(240, int(d.get('after_min', 30))))
                self.blackout_windows = self._parse(d.get('windows', ''))
                self.rejected_total = int(d.get('rejected_total', 0))
                logger.info(f"📰 فلتر الأخبار محمّل: "
                            f"{'مفعّل' if self.enabled else 'معطل'} | تأثير≥{self.impact_min} | "
                            f"±{self.before_min}/{self.after_min}د | عملات: {self.currencies}")
            except Exception as e:
                logger.warning(f"تعذر تحميل إعدادات فلتر الأخبار (افتراضيات): {e}")
        else:
            env = os.environ.get('NEWS_FILTER_ENABLED', '').lower()
            if env == 'true':
                self.enabled = True
            await self.save()

    async def save(self):
        if not self.db:
            return
        try:
            await self.db.set_param('news_filter', json.dumps({
                'enabled': self.enabled, 'impact_min': self.impact_min,
                'currencies': self.currencies, 'before_min': self.before_min,
                'after_min': self.after_min, 'windows': self.windows_spec(),
                'rejected_total': self.rejected_total}))
        except Exception as e:
            logger.warning(f"تعذر حفظ إعدادات فلتر الأخبار: {e}")

    @staticmethod
    def _parse(spec):
        out = []
        for part in (spec or '').split(','):
            part = part.strip()
            if '-' not in part:
                continue
            try:
                a, b = part.split('-')
                ah, am = map(int, a.split(':'))
                bh, bm = map(int, b.split(':'))
                out.append((ah * 60 + am, bh * 60 + bm))
            except Exception:
                continue
        return out

    def windows_spec(self):
        return ','.join(f"{s // 60:02d}:{s % 60:02d}-{e // 60:02d}:{e % 60:02d}"
                        for s, e in self.blackout_windows)

    def set_windows(self, spec):
        self.blackout_windows = self._parse(spec)

    @property
    def currencies_list(self):
        return [c.strip().upper() for c in (self.currencies or '').split(',') if c.strip()]

    async def refresh_calendar(self):
        try:
            def _fetch():
                r = requests.get(self.CALENDAR_URL, timeout=20,
                                 headers={'User-Agent': 'Mozilla/5.0'})
                r.raise_for_status()
                return r.json()
            data = await asyncio.to_thread(_fetch)
            events = []
            for e in (data if isinstance(data, list) else []):
                try:
                    title = str(e.get('title', '')).strip()[:90]
                    cur = str(e.get('country', '')).strip().upper()
                    impact = str(e.get('impact', '')).strip()
                    dstr = str(e.get('date', '')).strip()
                    if not title or not dstr or not cur:
                        continue
                    ts = datetime.fromisoformat(dstr).timestamp()
                    events.append({'title': title, 'cur': cur, 'impact': impact, 'ts': ts})
                except Exception:
                    continue
            self.events = sorted(events, key=lambda x: x['ts'])
            self.calendar_updated = time.time()
            self.last_fetch_ok = True
            self.last_error = None
            logger.info(f"📰 تقويم الأخبار محدّث: {len(self.events)} حدثاً هذا الأسبوع")
            return True, f"{len(self.events)} حدثاً"
        except Exception as e:
            self.last_fetch_ok = False
            self.last_error = str(e)[:140]
            logger.warning(f"تعذر جلب تقويم الأخبار (لا يوقف التداول): {e}")
            return False, self.last_error

    def _match_events(self):
        rank_min = self.IMPACT_RANK.get(self.impact_min, 3)
        curs = set(self.currencies_list) or {'USD'}
        return [e for e in self.events
                if e['cur'] in curs and self.IMPACT_RANK.get(e['impact'], 0) >= rank_min]

    def next_event(self):
        now_ts = time.time()
        upcoming = [e for e in self._match_events()
                    if e['ts'] >= now_ts - self.after_min * 60]
        return upcoming[0] if upcoming else None

    def is_blocked_now(self):
        """يعيد (محظور؟، السبب) — السبب يُعرض في اللوحة والإشعارات."""
        if not self.enabled:
            return False, 'الفلتر معطل من اللوحة'
        t = time.gmtime()
        now_min = t.tm_hour * 60 + t.tm_min
        for start, end in self.blackout_windows:
            if start <= now_min <= end:
                return True, f'نافذة أخبار يدوية {self.windows_spec()} (UTC)'
        if not self.events:
            if self.last_error:
                return False, 'تعذر جلب التقويم — التداول مستمر'
            return False, 'بانتظار جلب التقويم...'
        now_ts = time.time()
        for ev in self._match_events():
            if ev['ts'] - self.before_min * 60 <= now_ts <= ev['ts'] + self.after_min * 60:
                mins = int(abs(now_ts - ev['ts']) / 60)
                when = f'بعد {mins} دقيقة' if now_ts < ev['ts'] else f'قبل {mins} دقيقة'
                return True, (f"📰 {ev['title']} ({ev['cur']} — {ev['impact']}) {when}")
        return False, 'لا أحداث مؤثرة الآن'

    def status(self):
        nxt = self.next_event()
        blocked, reason = self.is_blocked_now()
        return {
            'enabled': self.enabled,
            'impact_min': self.impact_min,
            'currencies': self.currencies,
            'before_min': self.before_min,
            'after_min': self.after_min,
            'windows': self.windows_spec(),
            'blocked_now': blocked,
            'reason': reason,
            'next_event': ({'title': nxt['title'], 'cur': nxt['cur'], 'impact': nxt['impact'],
                            'in_min': max(0, int((nxt['ts'] - time.time()) / 60)),
                            'time': libya_time_str(nxt['ts']) + ' بتوقيت ليبيا'}
                           if nxt else None),
            'calendar_updated': int(self.calendar_updated),
            'calendar_age_min': (int((time.time() - self.calendar_updated) / 60)
                                 if self.calendar_updated else None),
            'events_count': len(self.events),
            'last_fetch_ok': self.last_fetch_ok,
            'last_error': self.last_error,
            'rejected_total': self.rejected_total,
        }
# ═══════════════════ إعدادات HMA_DMI_MOMENTUM (مصدر الحقيقة = القاعدة) ═══════════════════
HMA_STRATEGY_NAME = 'HMA_DMI_MOMENTUM'


class HMASettings:
    """
    كل عتبات استراتيجية HMA_DMI_MOMENTUM في مكان واحد:
    - عند أول تشغيل تُبذر من متغيرات Railway (HMA_MIN_POWER ... إلخ) ثم تُحفظ
      في القاعدة (مفتاح bot_params: hma_settings) — وبعدها القاعدة هي المرجع
      (تعديل اللوحة لحظي ويصمد لإعادة التشغيل).
    - القيم الافتراضية هي القيم المطلوبة من المالك: HMA 8/21 | DI 7 + تنعيم
      ADX 6 | زخم 2/5/9 | ER 10 | بنية 5 | Supertrend ATR14 ×1.35 | قوة ≥24
      | ثقة ≥5 | ADX قوي 20 | ER قوي 0.25 | تأكيد زخم ≥2 | مدة حالة 3 شموع
      | تبريد 3 شموع | انقلاب 0.60×ATR | استثناء هيكلي: قوة 12 / ثقة 4 /
      ADX 18.
    - V11.3 (اعتماد المالك): حقلا بوابة اتجاه 4 ساعات T3 —
      trend4h_enabled (1=مفعّلة افتراضياً) وtrend4h_ema_len (EMA50 على 4س).
      حقول جديدة كلياً: القاعدة القديمة بلا مفتاحين يبذر افتراضيهما تلقائياً
      عند التحميل (لا حاجة لترحيل قيم).
    - timeframe سلسلة تُدار خارج FIELDS (قيم مسموحة: 5m/15m/1h — الافتراضي 15m).
    """
    TIMEFRAMES = ('5m', '15m', '1h')
    TF_MS = {'5m': 300000, '15m': 900000, '1h': 3600000}

    FIELDS = {
        # الاسم: (النوع، الافتراضي، الأدنى، الأعلى، متغير Railway)
        'hma_fast':          (int,   8,    4,    50,   'HMA_FAST'),
        'hma_slow':          (int,   21,   10,   200,  'HMA_SLOW'),
        'di_period':         (int,   7,    3,    30,   'HMA_DI_PERIOD'),
        'adx_smooth':        (int,   6,    3,    30,   'HMA_ADX_SMOOTH'),
        'mom_fast':          (int,   2,    1,    20,   'HMA_MOM_FAST'),
        'mom_mid':           (int,   5,    2,    40,   'HMA_MOM_MID'),
        'mom_slow':          (int,   9,    3,    60,   'HMA_MOM_SLOW'),
        'er_period':         (int,   10,   5,    50,   'HMA_ER_PERIOD'),
        'struct_period':     (int,   5,    3,    20,   'HMA_STRUCT_PERIOD'),
        'st_atr_period':     (int,   14,   5,    50,   'HMA_ST_ATR_PERIOD'),
        'st_mult':           (float, 1.35, 0.5,  5.0,  'HMA_ST_MULT'),
        'ema_period':        (int,   200,  50,   400,  'HMA_EMA_PERIOD'),
        'ema_filter':        (int,   0,    0,    1,    'HMA_EMA_FILTER'),
        'min_power':         (float, 24.0, 0.0,  100.0,'HMA_MIN_POWER'),
        'min_confidence':    (int,   5,    0,    9,    'HMA_MIN_CONFIDENCE'),
        'strong_adx':        (float, 20.0, 5.0,  50.0, 'HMA_STRONG_ADX'),
        'strong_er':         (float, 0.25, 0.05, 0.9,  'HMA_STRONG_ER'),
        'min_mom_conf':      (int,   2,    1,    3,    'HMA_MIN_MOM_CONF'),
        'min_state_candles': (int,   3,    1,    20,   'HMA_MIN_STATE_CANDLES'),
        'cooldown_candles':  (int,   3,    0,    30,   'HMA_COOLDOWN_CANDLES'),
        'reversal_atr':      (float, 0.60, 0.1,  5.0,  'HMA_REVERSAL_ATR'),
        'so_power':          (float, 12.0, 0.0,  100.0,'HMA_SO_POWER'),
        'so_confidence':     (int,   4,    0,    9,    'HMA_SO_CONFIDENCE'),
        'so_adx':            (float, 18.0, 5.0,  50.0, 'HMA_SO_ADX'),
        'adx_gate':          (float, 20.0, 0.0,  50.0, 'HMA_ADX_GATE'),
        'sl_atr_mult':       (float, 2.0,  0.3,  6.0,  'HMA_SL_ATR'),
        'risk_min_pct':      (float, 0.15, 0.05, 2.0,  'HMA_RISK_MIN_PCT'),
        'risk_max_pct':      (float, 3.5,  0.5,  10.0, 'HMA_RISK_MAX_PCT'),
        'min_rr':            (float, 1.2,  0.5,  5.0,  'HMA_MIN_RR'),
        'tp1_return_pct':    (float, 30.0, 1.0,  100.0,'HMA_TP1_RETURN_PCT'),
        'tp1_max_atr':       (float, 4.0,  1.0,  20.0, 'HMA_TP1_MAX_ATR'),
        'universe_size':     (int,   40,   10,   200,  'HMA_UNIVERSE_SIZE'),
        'batch_size':        (int,   12,   4,    60,   'HMA_BATCH_SIZE'),
        'parallel':          (int,   4,    1,    10,   None),
        'max_signals_per_scan': (int, 1,  1,    3,    None),
        # 🧭 V11.3 — بوابة اتجاه 4 ساعات (اعتماد المالك T3): الإشارة تُقبل فقط
        # إذا حاذى اتجاه آخر شمعة 4س مغلقة كلياً (EMA على 4س + ميلها) الإشارة.
        'trend4h_enabled':   (int,   1,    0,    1,    None),
        'trend4h_ema_len':   (int,   50,   20,   200,  None),
    }
    LABELS = {
        'hma_fast': 'HMA السريعة',
        'hma_slow': 'HMA البطيئة',
        'di_period': 'فترة DI',
        'adx_smooth': 'تنعيم ADX',
        'mom_fast': 'زخم سريع',
        'mom_mid': 'زخم متوسط',
        'mom_slow': 'زخم بطيء',
        'er_period': 'فترة كفاءة الحركة ER',
        'struct_period': 'فترة بنية السوق (تأكيد القمم/القيعان)',
        'st_atr_period': 'فترة ATR لـ Supertrend',
        'st_mult': 'معامل ATR لـ Supertrend',
        'ema_period': 'فترة EMA (فلتر الاتجاه)',
        'ema_filter': 'فلتر EMA200 (1=مفعّل 0=معطل)',
        'min_power': 'أدنى قوة دخول (0-100)',
        'min_confidence': 'أدنى ثقة دخول (0-9)',
        'strong_adx': 'عتبة ADX القوي',
        'strong_er': 'عتبة ER القوي',
        'min_mom_conf': 'أدنى تأكيدات الزخم (1-3)',
        'min_state_candles': 'أدنى مدة الحالة (شموع مغلقة)',
        'cooldown_candles': 'تبريد الإشارات/التبدّل (شموع)',
        'reversal_atr': 'عتبة الانقلاب (×ATR)',
        'so_power': 'قوة الاستثناء الهيكلي',
        'so_confidence': 'ثقة الاستثناء الهيكلي',
        'so_adx': 'ADX للاستثناء الهيكلي',
        'adx_gate': 'بوابة اتجاهية ADX-14 عند الدخول (0=معطلة)',
        'sl_atr_mult': 'الستوب (×ATR)',
        'risk_min_pct': 'أدنى مسافة ستوب (%)',
        'risk_max_pct': 'أقصى مسافة ستوب (%)',
        'min_rr': 'أدنى عائد/مخاطرة (R:R)',
        'tp1_return_pct': 'هدف TP1 (% من الهامش)',
        'tp1_max_atr': 'أقصى مسافة TP1 واقعية (×ATR)',
        'universe_size': 'حجم كون HMA (أعلى سيولة)',
        'batch_size': 'عدد العملات المفحوصة كل دورة',
        'parallel': 'تحليلات متوازية',
        'max_signals_per_scan': 'أقصى إشارات منفذة في الدورة',
        'trend4h_enabled': 'بوابة اتجاه 4 ساعات T3 (1=مفعّلة 0=معطلة)',
        'trend4h_ema_len': 'فترة EMA لبوابة 4 ساعات (على شموع 4س مغلقة)',
    }

    VERSION = 3   # 🧭 V11.3: حقلا بوابة 4س جددان — افتراضاهما يُبزران تلقائياً
    V1_DEFAULTS = {'sl_atr_mult': 1.5, 'tp1_return_pct': 20.0}   # الافتراضي القديم (V11.0)
    V1_TO_V2 = {'sl_atr_mult': 2.0, 'tp1_return_pct': 30.0}      # الترقية: U4 المُتحقق عليه

    def _upgrade_v1_to_v2(self, stored):
        """ترقية موثقة لإعدادات HMA محفوظة من V11.0: يُحدَّث فقط ما بقي على
        الافتراضي القديم (لم يخصصه المالك)، والقيم المخصصة تبقى كما هي.
        يشمل الإطار: '15m' (الافتراضي القديم) → '1h'، وما هو مخصص يبقى.
        بوابة ADX حقل جديد يُبذر افتراضه 20.0 تلقائياً (ليس في القاعدة القديمة).
        V11.3: حقلا بوابة 4س جديدان كلياً — يُبزران من FIELDS تلقائياً عند
        غيابهما عن القاعدة (بلا ترحيل قيم)، وسلسلة الترقية v1→v2 هنا آمنة
        و idempotent (تُستدعى لأي إصدار محفوظ أقدم من VERSION الحالي)."""
        changed = []
        for k, new_v in self.V1_TO_V2.items():
            old_v = self.V1_DEFAULTS.get(k)
            try:
                cur = float(getattr(self, k))
            except Exception:
                continue
            if old_v is not None and abs(cur - float(old_v)) <= 1e-12:
                setattr(self, k, new_v)
                changed.append(f'{k}: {old_v:g}←{new_v:g}')
        # 🧭 ترقية الإطار: فقط إن بقي على الافتراضي القديم 15د
        stored_tf = (stored or {}).get('timeframe', '15m')
        if str(stored_tf) == '15m' and self.timeframe == '15m':
            self.timeframe = '1h'
            changed.append('timeframe: 15m←1h')
        if changed:
            logger.info("🧭 ترقية إعدادات HMA إلى v2 (الافتراضيات المعاد ضبطها فقط): "
                        + ", ".join(changed))

    def __init__(self, db=None):
        self.db = db
        self.timeframe = '1h'    # 🧭 V11.1: الإشارات على شموع ساعة مغلقة (أفضلية مُثبتة — راجع تقرير إعادة البناء)
        self.env_conflicts = []
        for k, spec in self.FIELDS.items():
            setattr(self, k, spec[1])

    def set_timeframe(self, tf):
        if tf in self.TIMEFRAMES and tf != self.timeframe:
            self.timeframe = tf
            return True
        return False

    def as_params(self):
        """قاموس معاملات المحرك النقي (struct_w = نافذة تأكيد القمة/القاع)."""
        p = {k: getattr(self, k) for k in self.FIELDS}
        p['struct_w'] = max(1, int(self.struct_period) // 2)
        return p

    async def load(self):
        self.env_conflicts = []
        raw = None
        if self.db:
            raw = await self.db.get_param('hma_settings')
        if raw:
            try:
                d = json.loads(raw)
                self.apply(d)
                # 🔭 تجاوز بيئي صريح لحجم الكون (مقبض النشر الحاسم):
                # HMA_UNIVERSE_SIZE المضبوط في Railway يتقدم على القيمة المخزنة
                # كي لا يبقى البوت على كون قديم محفوظ من إصدار سابق.
                _env_u = os.environ.get('HMA_UNIVERSE_SIZE', '')
                if _env_u:
                    try:
                        _v = max(10, min(200, int(float(_env_u))))
                        if _v != self.universe_size:
                            logger.info(f"🔭 HMA_UNIVERSE_SIZE={_v} من متغيرات البيئة "
                                        f"يتجاوز المخزن ({self.universe_size}) — حُفظ في القاعدة")
                            self.universe_size = _v
                            await self.save()
                    except (TypeError, ValueError):
                        pass
                # 🔄 ترقية الإعدادات القديمة (v1→v2): الافتراضيات المعاد ضبطها فقط
                if int(d.get('version', 1) or 1) < self.VERSION:
                    self._upgrade_v1_to_v2(d)
                    await self.save()
                self._collect_env_conflicts()
                logger.info(f"🧭 إعدادات HMA_DMI_MOMENTUM محمّلة من القاعدة: {self.describe()}")
                if self.env_conflicts:
                    logger.warning("⚠️ تعارض إعدادات HMA: متغيرات Railway تختلف عن القيم الفعالة "
                                   "(القاعدة هي المرجع بعد أول تشغيل) — الاستيراد من اللوحة")
            except Exception as e:
                logger.warning(f"تعذر تحميل إعدادات HMA (افتراضيات): {e}")
        else:
            seeded = {}
            for k, spec in self.FIELDS.items():
                env = spec[4]
                if env and os.environ.get(env) not in (None, ''):
                    try:
                        val = float(os.environ[env])
                        seeded[k] = val if spec[0] is float else int(val)
                    except (TypeError, ValueError):
                        logger.warning(f"قيمة HMA غير صالحة لـ {env}: {os.environ[env]}")
            self.apply(seeded)
            env_tf = os.environ.get('HMA_TIMEFRAME', '')
            if env_tf in self.TIMEFRAMES:
                self.timeframe = env_tf
            await self.save()
            if seeded:
                logger.info(f"🧭 إعدادات HMA مبذورة من متغيرات Railway: {sorted(seeded.keys())}")
            logger.info(f"🧭 إعدادات HMA النشطة: {self.describe()}")

    def apply(self, d):
        for k, v in (d or {}).items():
            if k == 'timeframe':
                self.set_timeframe(str(v))
                continue
            if k not in self.FIELDS:
                continue
            t, _, lo, hi, _ = self.FIELDS[k]
            try:
                x = float(v)
                x = t(x) if t is float else int(x)
            except (TypeError, ValueError):
                continue
            setattr(self, k, x)
        self._clamp()

    def _clamp(self):
        for k, (_, _, lo, hi, _) in self.FIELDS.items():
            try:
                v = float(getattr(self, k))
                setattr(self, k, max(lo, min(hi, v)))
            except Exception:
                setattr(self, k, self.FIELDS[k][1])
        for k, spec in self.FIELDS.items():
            if spec[0] is int:
                setattr(self, k, int(getattr(self, k)))

    def update(self, d):
        """من اللوحة: تحديث مجموعة إعدادات — يعيد قائمة التغييرات."""
        changed = []
        if 'timeframe' in (d or {}):
            old_tf = self.timeframe
            if self.set_timeframe(str(d['timeframe'])):
                changed.append(f"الإطار الزمني: {old_tf} ← {self.timeframe}")
        for k in self.FIELDS:
            if k not in (d or {}):
                continue
            try:
                old = getattr(self, k)
                new_raw = float(d[k])
                new = new_raw if self.FIELDS[k][0] is float else int(new_raw)
                if abs(float(new) - float(old)) > 1e-9:
                    changed.append(f"{self.LABELS.get(k, k)}: {old:g} ← {new:g}")
                    setattr(self, k, new)
            except (TypeError, ValueError):
                continue
        self._clamp()
        return changed

    async def save(self):
        if not self.db:
            return
        try:
            await self.db.set_param('hma_settings', json.dumps(self.status()))
        except Exception as e:
            logger.warning(f"تعذر حفظ إعدادات HMA: {e}")

    def _collect_env_conflicts(self):
        """كشف متغيرات Railway التي تختلف عن القيمة الفعالة — عرض فقط."""
        self.env_conflicts = []
        for k, spec in self.FIELDS.items():
            env = spec[4]
            if not env or os.environ.get(env) in (None, ''):
                continue
            try:
                ev = float(os.environ[env])
                cur = float(getattr(self, k))
            except (TypeError, ValueError):
                continue
            if abs(ev - cur) > 1e-9:
                self.env_conflicts.append({'field': k, 'env': env,
                                           'env_value': ev, 'active_value': cur,
                                           'label': self.LABELS.get(k, k)})

    def status(self):
        out = {k: getattr(self, k) for k in self.FIELDS}
        out['timeframe'] = self.timeframe
        out['version'] = self.VERSION
        return out

    def describe(self):
        gate = (f"بوابة 4س EMA{int(self.trend4h_ema_len)}+ميل ✓"
                if self.trend4h_enabled else "بوابة 4س معطلة")
        return (f"HMA {self.hma_fast}/{self.hma_slow} | DI {self.di_period}/ADX {self.adx_smooth} | "
                f"زخم {self.mom_fast}/{self.mom_mid}/{self.mom_slow} | ER {self.er_period} | "
                f"ST {self.st_atr_period}×{self.st_mult:g} | قوة≥{self.min_power:g} ثقة≥{self.min_confidence} | "
                f"بوابة ADX≥{self.adx_gate:g} | {gate} | {self.timeframe} | TP1={self.tp1_return_pct:g}% | "
                f"R:R≥{self.min_rr:g} | EMA200 {'مفعّل' if self.ema_filter else 'معطل'}")


# ═══════════════════ بوابة اتجاه 4 ساعات (V11.3 — اعتماد T3) ═══════════════════
def _trend_4h(df, mode='ema_slope', ema_len=50):
    """🧭 سلسلة اتجاه الإطار الأكبر (4 ساعات) مشتقة من شموع 1س مغلقة.
    نسخة مطابقة للفرعين المعتمدين (ema/ema_slope) من backtest._trend_4h
    — لضمان تطابق البوت الحي مع الباكتيست معاملياً (يُختبر تطابق المصفوفتين
    حرفياً في test_strategies.py). بلا إعادة رسم:
    لكل شمعة ساعة i يُستخدم آخر شمعة 4س **مغلقة كلياً** لحظة إغلاق i فقط
    (الشمعة 4س الجارية لا تُلمس أبداً — نفس مبدأ الشموع المغلقة في المحرك).
    يعيد مصفوفة اتجاه لكل شمعة 1س: ‎+1 صاعد | ‎−1 هابط | 0 محايد/غير جاهز.
    الأنماط:
      ema      — السعر (إغلاق المجموعة 4س) فوق/تحت EMA(ema_len) على 4س
      ema_slope— كالسابق + ميل EMA صاعد/هابط عبر آخر 3 شموع 4س مغلقة (T3)
    (أنماط dmi/dmi_adx/both موجودة في backtest.py للبحث فقط — لم يُعتمد منها شيء).
    ملاحظة الحجم: 700 شمعة 1س = 175 مجموعة 4س — وزن بذرة EMA50 المتبقي
    ≈ 0.09% (هامش مهمل مقابل تاريخ الباكتيست الأطول)."""
    n = len(df)
    t_close = pd.to_numeric(df['time']).to_numpy() + 3600_000   # لحظة إغلاق شمعة الساعة
    c_ = df['close'].to_numpy(dtype=float)
    G = 4 * 3600_000
    gid = (t_close // G).astype(int)          # عدد مجموعات 4س المكتملة عند إغلاق i
    n_groups = int(gid[-1])                   # آخر مجموعة مكتملة في كامل البيانات
    if n_groups < max(ema_len + 5, 30):
        return np.zeros(n, dtype=int)         # بيانات غير كافية — بوابة محايدة
    g_close = np.full(n_groups, np.nan)
    # إغلاق كل مجموعة 4س = إغلاق آخر شمعة 1س أُغلقت داخلها (بلا مستقبل)
    starts = np.searchsorted(t_close, np.arange(n_groups) * G, side='left')
    ends = np.searchsorted(t_close, (np.arange(n_groups) + 1) * G, side='left')
    for g in range(n_groups):
        if ends[g] > starts[g]:
            g_close[g] = c_[ends[g] - 1]
    valid = ~np.isnan(g_close)
    trend_g = np.zeros(n_groups, dtype=int)
    ema = pd.Series(g_close).ewm(span=ema_len, adjust=False).mean().to_numpy()
    for g in range(n_groups):
        if not valid[g]:
            continue
        e = ema[g]
        if not np.isfinite(e):
            continue
        up = g_close[g] > e
        down = g_close[g] < e
        if mode == 'ema_slope' and g >= 2:
            up = up and e > ema[g - 2]
            down = down and e < ema[g - 2]
        if up and not down:
            trend_g[g] = 1
        elif down and not up:
            trend_g[g] = -1
    # خريطة المجموعة → شموع الساعة: trend[i] = اتجاه آخر مجموعة مكتملة عند إغلاق i
    trend = trend_g[np.clip(gid - 1, 0, n_groups - 1)]
    return trend


# ═════════════════════════════════════════════════════════════════════════
# 🧭 محرك HMA_DMI_MOMENTUM — الاستراتيجية الوحيدة في هذا البوت
# ═════════════════════════════════════════════════════════════════════════
# مبادئ صارمة (مُختبرة في test_strategies.py):
#  1) شموع مغلقة فقط — المتصل يمرر DataFrame حُذفت منه الشمعة الجارية.
#  2) لا بيانات مستقبلية: كل المؤشرات متتالية خلفية (causal) — قيمة الشمعة i
#     تعتمد على الشموع ≤ i فقط (مُختبر بمقارنة الحساب على بادئات متزايدة).
#  3) القمم/القيعان الهيكلية لا تُستخدم قبل تأكيدها (تحتاج w شموع مغلقة
#     بعد القمة/القاع — تأخير التأكيد موثق: w = struct_period // 2 = 2).
#  4) آلة حالات NEUTRAL/BULL/BEAR قابلة لإعادة البناء الحتمي من الشموع
#     المغلقة نفسها — إعادة تشغيل البوت لا تغيّر الحالة (بلا حالة مخزنة
#     تتقادم) — إعادة تشغيل (replay) ثابتة على آخر REPLAY_BARS شمعة.
#  5) الدوال نقية (بلا شبكة/حالة خارجية) لتكون قابلة للاختبار المباشر.
#
# تعريفات موثقة للقياص الحسابية:
#  - Entry Power (0-100) لكل اتجاه = مجموع مكونات مرجّحة:
#      HMA (20): انحياز السريعة/البطيئة 14 + ميل السريعة 6
#      DMI/ADX (20): هيمنة DI 12 + ADX ≥ strong_adx 5 + ADX صاعد 3
#      الزخم (15): كل ROC من (2/5/9) بالاتجاه 5 (بحد 15)
#      ER (10): ER ≥ strong_er → 10، وإلا ER ≥ نصف العتبة → 5
#      Supertrend (15): انحياز الاتجاه
#      البنية (20): البنية السليمة (الإغلاق فوق آخر قاع مؤكد للشراء /
#                   تحت آخر قمة مؤكدة للبيع)
#  - Entry Confidence (0-9) = عدد التأكيدات المستقلة المحققة:
#      1 انحياز HMA | 2 ميل HMA | 3 هيمنة DI | 4 ADX قوي | 5 زخم ≥
#      min_mom_conf | 6 ER قوي | 7 Supertrend | 8 بنية سليمة |
#      9 EMA (يُحتسب فقط عند تفعيل الفلتر — بلا فلتر الحد الأعلى 8)
#  - الزناد (على شمعة مغلقة): استعادة HMA السريعة (تقاطع) أو استئناف بعد
#      ارتداد من HMA البطيئة (لمس خلال آخر 3 شموع + شمعة إغلاق مؤكدة).
#  - الاستثناء الهيكلي (محدود): يخفّض العتبتين فقط عند كسر إغلاقٍ لقمة/قاع
#      مؤكد بعمق ≥ reversal_atr×ATR مع ADX ≥ so_adx وهيمنة DI وتأكيد زخم
#      ≥1 — ولا يتجاوز: آلة الحالات (NEUTRAL لا يُتداول)، التبريد، فلتر
#      EMA، ولا أي بوابة مخاطر/تعارض.
# ═════════════════════════════════════════════════════════════════════════
class HmaDmiMomentumEngine:
    NAME = HMA_STRATEGY_NAME
    REPLAY_BARS = 160          # نافذة إعادة بناء الحالة (ثابتة → حتمية)
    STATE_NAMES = {0: 'NEUTRAL', 1: 'BULL', -1: 'BEAR'}

    # ─── المؤشرات الأساسية (كلها متتالية خلفية — بلا تسرب مستقبلي) ───
    @staticmethod
    def _wma(a, period):
        """المتوسط المتحرك المرجح — NaN قبل اكتمال أول نافذة."""
        a = np.asarray(a, dtype=float)
        n = len(a)
        out = np.full(n, np.nan)
        if period <= 0 or n < period:
            return out
        w = np.arange(1, period + 1, dtype=float)
        w = w / w.sum()
        out[period - 1:] = np.convolve(a, w[::-1], mode='valid')
        return out

    @classmethod
    def _hma(cls, a, period):
        """Hull MA = WMA(2×WMA(n/2) − WMA(n), √n)."""
        a = np.asarray(a, dtype=float)
        half = max(1, int(period) // 2)
        sq = max(1, int(math.sqrt(max(1, int(period)))))
        raw = 2.0 * cls._wma(a, half) - cls._wma(a, period)
        return cls._wma(raw, sq)

    @staticmethod
    def _ema(a, period):
        a = np.asarray(a, dtype=float)
        n = len(a)
        out = np.full(n, np.nan)
        if n < period or period <= 0:
            return out
        k = 2.0 / (period + 1.0)
        out[period - 1] = float(np.mean(a[:period]))
        for i in range(period, n):
            out[i] = out[i - 1] + k * (a[i] - out[i - 1])
        return out

    @staticmethod
    def _true_range(h, l, c):
        prev_c = np.roll(c, 1)
        prev_c[0] = c[0]
        return np.maximum(h - l, np.maximum(np.abs(h - prev_c), np.abs(l - prev_c)))

    @staticmethod
    def _rma(x, period, start_idx=0):
        """تنعيم وايلدر (RMA): أول قيمة = متوسط بسيط لأول نافذة صالحة،
        ثم out[i] = (out[i-1]×(p-1) + x[i]) / p — متتالية خلفية بحتة."""
        x = np.asarray(x, dtype=float)
        n = len(x)
        out = np.full(n, np.nan)
        s = start_idx + period
        if period <= 0 or n < s:
            return out
        out[s - 1] = float(np.mean(x[start_idx:s]))
        for i in range(s, n):
            out[i] = (out[i - 1] * (period - 1) + x[i]) / period
        return out

    @classmethod
    def _wilder_atr(cls, h, l, c, period):
        return cls._rma(cls._true_range(h, l, c), period, start_idx=0)

    @classmethod
    def _dmi_adx(cls, h, l, c, di_period, adx_smooth):
        """+DI/−DI بتنعيم وايلدر لفترة di_period، و ADX بتنعيم adx_smooth.
        الآمن ضد القسمة على صفر — القيم غير الجاهزة NaN."""
        n = len(c)
        up = np.diff(h, prepend=h[0])
        dn = -np.diff(l, prepend=l[0])
        plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
        minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
        tr = cls._true_range(h, l, c)
        atr_s = cls._rma(tr, di_period, 0)
        pdm_s = cls._rma(plus_dm, di_period, 0)
        mdm_s = cls._rma(minus_dm, di_period, 0)
        with np.errstate(divide='ignore', invalid='ignore'):
            plus_di = 100.0 * pdm_s / np.where(atr_s > 0, atr_s, np.nan)
            minus_di = 100.0 * mdm_s / np.where(atr_s > 0, atr_s, np.nan)
            dx = 100.0 * np.abs(plus_di - minus_di) / np.maximum(plus_di + minus_di, 1e-12)
        dx = np.where(np.isfinite(dx), dx, np.nan)
        first_valid = di_period - 1 if n >= di_period else 0
        adx = cls._rma(np.nan_to_num(dx, nan=0.0), adx_smooth,
                       start_idx=first_valid if n > first_valid else 0)
        if n > first_valid:
            adx[:first_valid + adx_smooth - 1] = np.nan
        return plus_di, minus_di, adx

    @classmethod
    def _supertrend(cls, h, l, c, atr_period, mult):
        """Supertrend القياسي (ATR وايلدر) — اتجاه +1 صاعد / −1 هابط / 0 غير جاهز.
        تعتمد قيمة الشمعة i على الشموع ≤ i فقط."""
        n = len(c)
        dir_out = np.zeros(n, dtype=np.int8)
        line = np.full(n, np.nan)
        atr = cls._wilder_atr(h, l, c, atr_period)
        if n <= atr_period:
            return dir_out, line
        mid = (h + l) / 2.0
        ub = mid + mult * atr
        lb = mid - mult * atr
        fub = np.nan
        flb = np.nan
        d = 1
        for i in range(atr_period, n):
            if not np.isfinite(atr[i]):
                continue
            if not np.isfinite(fub):
                fub, flb, d = ub[i], lb[i], 1
            else:
                fub = ub[i] if (ub[i] < fub or c[i - 1] > fub) else fub
                flb = lb[i] if (lb[i] > flb or c[i - 1] < flb) else flb
                if d == 1 and c[i] < flb:
                    d = -1
                elif d == -1 and c[i] > fub:
                    d = 1
            dir_out[i] = d
            line[i] = flb if d == 1 else fub
        return dir_out, line

    @staticmethod
    def _er(c, period):
        """كفاءة الحركة Efficiency Ratio = |c[i]−c[i−p]| / Σ|Δc| في النافذة.
        النطاق [0,1] — المسار المستقيم = 1.0 والمتعرج يقترب من 0.
        المسار الصفري (سعر ثابت) يعيد 0.0 بلا قسمة على صفر."""
        c = np.asarray(c, dtype=float)
        n = len(c)
        out = np.full(n, np.nan)
        if n <= period:
            return out
        change = np.abs(c[period:] - c[:-period])
        vol = np.abs(np.diff(c))
        cs = np.cumsum(np.concatenate(([0.0], vol)))
        path = cs[period:] - cs[:-period]
        out[period:] = np.where(path > 0, change / np.where(path > 0, path, 1.0), 0.0)
        return out

    @staticmethod
    def _roc(c, period):
        """معدل التغير المئوي (زخم) — NaN قبل اكتمال الفترة."""
        c = np.asarray(c, dtype=float)
        n = len(c)
        out = np.full(n, np.nan)
        if n <= period or period <= 0:
            return out
        base = c[:-period]
        out[period:] = np.where(base != 0, (c[period:] - base) / np.where(base != 0, base, 1.0) * 100.0, 0.0)
        return out

    @staticmethod
    def confirmed_pivots(h, l, w):
        """قمم/قيعان هيكلية مؤكدة فقط: القمة عند i هي أعلى نافذة ±w
        وتصبح صالحة للاستخدام ابتداءً من الشمعة i+w (تأخير التأكيد موثق).
        يعيد (قائمة قمم [(i, price)...]، قائمة قيعان [(i, price)...])."""
        h = np.asarray(h, dtype=float)
        l = np.asarray(l, dtype=float)
        n = len(h)
        w = max(1, int(w))
        ph, pl = [], []
        for i in range(w, n - w):
            if h[i] >= h[i - w:i + w + 1].max():
                ph.append((i, float(h[i])))
            if l[i] <= l[i - w:i + w + 1].min():
                pl.append((i, float(l[i])))
        return ph, pl

    @classmethod
    def compute_arrays(cls, df, params):
        """حساب كل المؤشرات مرة واحدة على شموع مغلقة — يعيد قاموس مصفوفات."""
        c = df['close'].to_numpy(dtype=float)
        h = df['high'].to_numpy(dtype=float)
        l = df['low'].to_numpy(dtype=float)
        ema_filter_on = int(params.get('ema_filter', 0)) == 1
        arr = {
            'n': len(c), 'close': c, 'high': h, 'low': l,
            'open': df['open'].to_numpy(dtype=float),
            'time': pd.to_numeric(df['time']).to_numpy(),
            'close_time': pd.to_numeric(df['close_time']).to_numpy(),
            'hma_fast': cls._hma(c, int(params['hma_fast'])),
            'hma_slow': cls._hma(c, int(params['hma_slow'])),
            'atr': cls._wilder_atr(h, l, c, int(params['st_atr_period'])),
            'er': cls._er(c, int(params['er_period'])),
            'roc_fast': cls._roc(c, int(params['mom_fast'])),
            'roc_mid': cls._roc(c, int(params['mom_mid'])),
            'roc_slow': cls._roc(c, int(params['mom_slow'])),
            'ema': (cls._ema(c, int(params['ema_period'])) if ema_filter_on
                    else np.full(len(c), np.nan)),
        }
        arr['plus_di'], arr['minus_di'], arr['adx'] = cls._dmi_adx(
            h, l, c, int(params['di_period']), int(params['adx_smooth']))
        arr['st_dir'], arr['st_line'] = cls._supertrend(
            h, l, c, int(params['st_atr_period']), float(params['st_mult']))
        arr['pivot_highs'], arr['pivot_lows'] = cls.confirmed_pivots(
            h, l, int(params.get('struct_w', 2)))
        return arr

    @staticmethod
    def min_bars(params):
        """أدنى عدد شموع مغلقة لتحليل صالح (إحماء المؤشرات الأطول)."""
        base = max(int(params['hma_slow']) * 3, int(params['er_period']) * 3,
                   int(params['di_period']) * 5 + int(params['adx_smooth']) * 3,
                   int(params['st_atr_period']) * 4, int(params['mom_slow']) * 3)
        if int(params.get('ema_filter', 0)) == 1:
            base = max(base, int(params['ema_period']) + 20)
        return base + 30

    # ─── آلة الحالات NEUTRAL/BULL/BEAR ───
    @staticmethod
    def _bar_direction(arr, i):
        """اتجاه الشمعة المرشح بأغلبية 3 من 4 أصوات مستقلة (كلها قيم مغلقة):
        1) انحياز HMA السريعة/البطيئة  2) هيمنة DI  3) اتجاه Supertrend
        4) إشارة مجموع الزخم (ROC 2+5+9). نقص الأصوات أو التعادل → 0."""
        if i < 1:
            return 0
        votes = 0
        total = 0
        h8, h21 = arr['hma_fast'][i], arr['hma_slow'][i]
        if np.isfinite(h8) and np.isfinite(h21) and h8 != h21:
            votes += 1 if h8 > h21 else -1
            total += 1
        pdi, mdi = arr['plus_di'][i], arr['minus_di'][i]
        if np.isfinite(pdi) and np.isfinite(mdi) and pdi != mdi:
            votes += 1 if pdi > mdi else -1
            total += 1
        sd = arr['st_dir'][i]
        if sd:
            votes += int(sd)
            total += 1
        m, valid = 0.0, True
        for k in ('roc_fast', 'roc_mid', 'roc_slow'):
            v = arr[k][i]
            if not np.isfinite(v):
                valid = False
                break
            m += v
        if valid and m != 0:
            votes += 1 if m > 0 else -1
            total += 1
        if total < 3:
            return 0
        if votes >= 3:
            return 1
        if votes <= -3:
            return -1
        return 0

    @classmethod
    def state_series(cls, arr, params, replay=None):
        """إعادة بناء حتمية لآلة الحالات على الشموع المغلقة:
        - التبدّل يتطلب مرشحاً ثابتاً min_state_candles شمعة مغلقة متتالية.
        - تبريد cooldown_candles شموع بعد كل تبدّل قبل تبدّل جديد.
        - الانقلاب المباشر BULL↔BEAR يتطلب حركة عكسية ≥ reversal_atr×ATR
          من أقصى إغلاق (للانقلاب الهابط) / أدنى إغلاق (للصاعد) خلال الحالة.
        يعيد (مصفوفة الحالات، meta لكل شمعة: بداية الحالة وعمرها وآخر تبدّل)."""
        n = arr['n']
        start = max(0, n - (replay or cls.REPLAY_BARS))
        min_dur = max(1, int(params['min_state_candles']))
        cool = max(0, int(params['cooldown_candles']))
        rev = float(params['reversal_atr'])
        atr = arr['atr']
        states = np.zeros(n, dtype=np.int8)
        meta = {}
        state, cand, cand_count = 0, 0, 0
        last_flip = start - 10 ** 9
        state_start = start
        extreme = None
        for i in range(start, n):
            d = cls._bar_direction(arr, i)
            if d != 0 and d == cand:
                cand_count += 1
            elif d != 0:
                cand, cand_count = d, 1
            else:
                cand, cand_count = 0, 0
            can_flip = (cand != 0 and cand != state
                        and cand_count >= min_dur
                        and (i - last_flip) >= cool)
            if can_flip:
                ok = True
                if state != 0 and cand == -state:
                    ext = extreme
                    if ext is not None and np.isfinite(atr[i]) and atr[i] > 0:
                        if state == 1:
                            ok = arr['close'][i] <= ext - rev * atr[i]
                        else:
                            ok = arr['close'][i] >= ext + rev * atr[i]
                if ok:
                    state, last_flip, state_start = cand, i, i
                    extreme = arr['close'][i]
                    cand_count = 0
            c = arr['close'][i]
            if extreme is None:
                extreme = c
            elif state == 1:
                extreme = max(extreme, c)
            elif state == -1:
                extreme = min(extreme, c)
            states[i] = state
            meta[i] = {'state': state, 'state_start': state_start,
                       'last_flip': last_flip, 'age': i - state_start}
        return states, meta

    # ─── القياس: Entry Power / Entry Confidence / تأكيدات الزخم ───
    @staticmethod
    def _last_confirmed_pivot(pivots, i, w):
        """آخر قمة/قاع مؤكد بحيث i >= مؤشر القمة + w (بلا استخدام مبكر)."""
        best = None
        for p in pivots:
            if p[0] + w <= i:
                best = p
            else:
                break
        return best

    @classmethod
    def _score_bar(cls, arr, i, dirn, params):
        """قياس شمعة مغلقة واحدة لاتجاه معين. يعيد
        (power 0-100, confidence 0-9, mom_conf 0-3, structure_ok)."""
        bull = dirn > 0
        aligned = lambda x: (x > 0) if bull else (x < 0)
        power = 0.0
        conf = 0
        c = arr['close'][i]
        w = int(params.get('struct_w', 2))

        # 1) HMA (20 نقطة)
        h8, h21 = arr['hma_fast'][i], arr['hma_slow'][i]
        h8p = arr['hma_fast'][i - 1] if i > 0 else np.nan
        if np.isfinite(h8) and np.isfinite(h21) and aligned(h8 - h21):
            power += 14.0
            conf += 1
        if np.isfinite(h8) and np.isfinite(h8p) and aligned(h8 - h8p):
            power += 6.0
            conf += 1

        # 2) DMI/ADX (20 نقطة)
        pdi, mdi, adx = arr['plus_di'][i], arr['minus_di'][i], arr['adx'][i]
        adx_p = arr['adx'][i - 1] if i > 0 else np.nan
        if np.isfinite(pdi) and np.isfinite(mdi) and aligned(pdi - mdi):
            power += 12.0
            conf += 1
        if np.isfinite(adx) and adx >= float(params['strong_adx']):
            power += 5.0
            conf += 1
        if np.isfinite(adx) and np.isfinite(adx_p) and aligned(adx - adx_p):
            power += 3.0

        # 3) الزخم (15 نقطة — 5 لكل ROC مؤكد)
        mom_conf = 0
        for k in ('roc_fast', 'roc_mid', 'roc_slow'):
            v = arr[k][i]
            if np.isfinite(v) and aligned(v):
                mom_conf += 1
        power += 5.0 * mom_conf
        if mom_conf >= int(params['min_mom_conf']):
            conf += 1

        # 4) كفاءة الحركة ER (10 نقاط)
        er = arr['er'][i]
        if np.isfinite(er):
            if er >= float(params['strong_er']):
                power += 10.0
                conf += 1
            elif er >= float(params['strong_er']) / 2.0:
                power += 5.0

        # 5) Supertrend (15 نقطة)
        sd = arr['st_dir'][i]
        if sd and aligned(sd):
            power += 15.0
            conf += 1

        # 6) البنية السليمة (20 نقطة) — بقمم/قيعان مؤكدة فقط
        structure_ok = False
        if bull:
            pl = cls._last_confirmed_pivot(arr['pivot_lows'], i, w)
            structure_ok = bool(pl) and c > pl[1]
        else:
            ph = cls._last_confirmed_pivot(arr['pivot_highs'], i, w)
            structure_ok = bool(ph) and c < ph[1]
        if structure_ok:
            power += 20.0
            conf += 1

        return min(100.0, power), conf, mom_conf, structure_ok

    @classmethod
    def _trigger(cls, arr, i, dirn):
        """زناد الدخول على شمعة مغلقة (يمنع ملاحقة الحركة الممتدة):
        BUY: استعادة HMA السريعة (إغلاق يقطعها صعوداً) أو استئناف بعد ارتداد
             من HMA البطيئة (لمس خلال آخر 3 شموع + شمعة صاعدة مغلقة فوق السريعة).
        SELL: المرآة المعاكسة تماماً."""
        c, o = arr['close'], arr['open']
        f, s = arr['hma_fast'], arr['hma_slow']
        if not (np.isfinite(f[i]) and np.isfinite(f[i - 1]) and np.isfinite(s[i])):
            return False, 'مؤشرات HMA غير جاهزة'
        lo_w = max(0, i - 2)
        if dirn > 0:
            if c[i] > f[i] and c[i - 1] <= f[i - 1]:
                return True, 'استعادة HMA السريعة (تقاطع صاعد)'
            touched = bool((arr['low'][lo_w:i + 1] <= arr['hma_slow'][lo_w:i + 1]).any())
            if touched and c[i] > f[i] and c[i] > o[i]:
                return True, 'استئناف صاعد بعد ارتداد من HMA البطيئة'
            return False, 'لا زناد شراء (لا استعادة ولا ارتداد مؤكد)'
        else:
            if c[i] < f[i] and c[i - 1] >= f[i - 1]:
                return True, 'كسر HMA السريعة (تقاطع هابط)'
            touched = bool((arr['high'][lo_w:i + 1] >= arr['hma_slow'][lo_w:i + 1]).any())
            if touched and c[i] < f[i] and c[i] < o[i]:
                return True, 'استئناف هابط بعد ارتداد من HMA البطيئة'
            return False, 'لا زناد بيع (لا كسر ولا ارتداد مؤكد)'

    @classmethod
    def _structural_override(cls, arr, i, dirn, params, power, confidence, mom_conf):
        """الاستثناء الهيكلي المحدود — شروطه الدقيقة (كلها إلزامية):
        1) تأكيد زخم ≥1 بالاتجاه.
        2) ADX ≥ so_adx وهيمنة DI بالاتجاه.
        3) إغلاق يكسر آخر قمة مؤكدة (للشراء) / قاع مؤكد (ل للبيع) بعمق
           ≥ reversal_atr × ATR.
        4) power ≥ so_power و confidence ≥ so_confidence.
        ما لا يتجاوزه أبداً: حالة NEUTRAL (لا تداول)، التبريد، فلتر EMA،
        وبوابات المخاطر والتعارض في مسار التنفيذ المشترك."""
        w = int(params.get('struct_w', 2))
        atr = arr['atr'][i]
        c = arr['close'][i]
        if not (np.isfinite(atr) and atr > 0):
            return False, 'ATR غير صالح للاستثناء الهيكلي'
        if mom_conf < 1:
            return False, 'لا تأكيد زخم واحد على الأقل للاستثناء الهيكلي'
        pdi, mdi, adx = arr['plus_di'][i], arr['minus_di'][i], arr['adx'][i]
        if not (np.isfinite(adx) and adx >= float(params['so_adx'])):
            return False, f'ADX أقل من حد الاستثناء ({(adx if np.isfinite(adx) else 0):.1f} < {float(params["so_adx"]):g})'
        if dirn > 0 and not (pdi > mdi):
            return False, 'DI غير مؤيّد للاستثناء الصاعد'
        if dirn < 0 and not (mdi > pdi):
            return False, 'DI غير مؤيّد للاستثناء الهابط'
        if dirn > 0:
            ph = cls._last_confirmed_pivot(arr['pivot_highs'], i, w)
            if not ph:
                return False, 'لا قمة مؤكدة لقياس الكسر الهيكلي'
            if c <= ph[1] + float(params['reversal_atr']) * atr:
                return False, 'الإغلاق لم يكسر القمة المؤكدة بعمق 0.6×ATR'
        else:
            pl = cls._last_confirmed_pivot(arr['pivot_lows'], i, w)
            if not pl:
                return False, 'لا قاع مؤكد لقياس الكسر الهيكلي'
            if c >= pl[1] - float(params['reversal_atr']) * atr:
                return False, 'الإغلاق لم يكسر القاع المؤكد بعمق 0.6×ATR'
        if power < float(params['so_power']) or confidence < int(params['so_confidence']):
            return False, (f'القوة/الثقة أقل من حد الاستثناء '
                           f'(قوة {power:g}/{float(params["so_power"]):g}، ثقة {confidence}/{int(params["so_confidence"])})')
        return True, 'كسر هيكلي مؤكد بعمق 0.6×ATR مع قوة اتجاه'

    @classmethod
    def evaluate_at(cls, arr, states, meta, i, params, include_details=True):
        """تقييم بوابات الدخول على شمعة مغلقة محددة i — يعتمد فقط على مصفوفات
        محسوبة مسبقاً (كلها متتالية خلفية: قيمة الفهرس i لا تتأثر بأي بيانات
        بعده — مُختبر في test_strategies.py) لذا يستخدمه محرك الاختبار التاريخي
        بأمان وبلا تسرب مستقبلي. يعيد قاموس القرار نفسه الذي يعيده evaluate."""
        result = {'signal': None, 'reject_reason': None,
                  'state': 'NEUTRAL', 'state_age': 0,
                  'power': {'BUY': 0.0, 'SELL': 0.0},
                  'confidence': {'BUY': 0, 'SELL': 0},
                  'mom_conf': {'BUY': 0, 'SELL': 0},
                  'snapshot': {}}
        try:
            n = arr['n']
            if i is None or i < 0 or i >= n or i not in meta:
                result['reject_reason'] = 'فهرس شمعة خارج نطاق التقييم'
                return result
            state = int(states[i])
            result['state'] = cls.STATE_NAMES[state]
            result['state_age'] = int(i - meta[i]['state_start'])

            if include_details:
                for dirn, key in ((1, 'BUY'), (-1, 'SELL')):
                    p, cf, mc, _ = cls._score_bar(arr, i, dirn, params)
                    result['power'][key] = round(float(p), 1)
                    result['confidence'][key] = int(cf)
                    result['mom_conf'][key] = int(mc)
                result['snapshot'] = {
                    'close': float(arr['close'][i]),
                    'hma_fast': float(arr['hma_fast'][i]) if np.isfinite(arr['hma_fast'][i]) else None,
                    'hma_slow': float(arr['hma_slow'][i]) if np.isfinite(arr['hma_slow'][i]) else None,
                    'plus_di': float(arr['plus_di'][i]) if np.isfinite(arr['plus_di'][i]) else None,
                    'minus_di': float(arr['minus_di'][i]) if np.isfinite(arr['minus_di'][i]) else None,
                    'adx': float(arr['adx'][i]) if np.isfinite(arr['adx'][i]) else None,
                    'er': float(arr['er'][i]) if np.isfinite(arr['er'][i]) else None,
                    'st_dir': int(arr['st_dir'][i]),
                    'atr': float(arr['atr'][i]) if np.isfinite(arr['atr'][i]) else None,
            }

            cool = max(0, int(params['cooldown_candles']))
            if state == 0:
                result['reject_reason'] = 'السوق محايد (NEUTRAL) — لا دخول'
                return result
            if (i - meta[i]['last_flip']) < cool:
                result['reject_reason'] = (f'تبريد آلة الحالات '
                                           f'({i - meta[i]["last_flip"]}/{cool} شموع بعد التبدّل)')
                return result

            dirn = state
            side = 'BUY' if dirn > 0 else 'SELL'
            power = result['power'][side]
            conf = result['confidence'][side]
            mc = result['mom_conf'][side]

            # ① فلتر EMA200 (صلب عند التفعيل — لا يتجاوزه الاستثناء الهيكلي)
            if int(params.get('ema_filter', 0)) == 1:
                ema_v = arr['ema'][i]
                if not np.isfinite(ema_v):
                    result['reject_reason'] = 'EMA200 غير جاهزة بعد'
                    return result
                if dirn > 0 and not arr['close'][i] > ema_v:
                    result['reject_reason'] = 'فلتر EMA200 يمنع الشراء (السعر أسفل المتوسط)'
                    return result
                if dirn < 0 and not arr['close'][i] < ema_v:
                    result['reject_reason'] = 'فلتر EMA200 يمنع البيع (السعر أعلى المتوسط)'
                    return result

            # ② الزخم الأدنى (صلب)
            if mc < int(params['min_mom_conf']):
                result['reject_reason'] = (f'تأكيد الزخم غير كافٍ '
                                           f'({mc}/{int(params["min_mom_conf"])})')
                return result

            # ③ الزناد + العتبات → وإلا الاستثناء الهيكلي (محدود)
            trig_ok, trig_txt = cls._trigger(arr, i, dirn)
            threshold_ok = (power >= float(params['min_power'])
                            and conf >= int(params['min_confidence']))
            override = False
            if trig_ok and threshold_ok:
                reason_txt = trig_txt
            else:
                ov_ok, ov_txt = cls._structural_override(arr, i, dirn, params,
                                                         power, conf, mc)
                if not ov_ok:
                    result['reject_reason'] = (f'قوة/ثقة أقل من العتبة '
                                               f'(قوة {power:g}/{float(params["min_power"]):g}، '
                                               f'ثقة {conf}/{int(params["min_confidence"])})'
                                               if trig_ok else trig_txt)
                    return result
                override = True
                reason_txt = 'استثناء هيكلي: ' + ov_txt

            result['signal'] = {
                'side': side,
                'candle_ms': int(arr['time'][i]),
                'candle_close_ms': int(arr['close_time'][i]),
                'close': float(arr['close'][i]),
                'atr': float(arr['atr'][i]),
                'power': float(power),
                'confidence': int(conf),
                'mom_conf': int(mc),
                'override': override,
                'reason_txt': reason_txt,
                'state': cls.STATE_NAMES[state],
            }
            return result
        except Exception as e:
            result['reject_reason'] = f'خطأ تقييم HMA: {e}'
            return result

    @classmethod
    def evaluate(cls, df, params):
        """التقييم الكامل على شموع مغلقة (الشمعة الجارية محذوفة مسبقاً).
        يعيد قاموساً: ok/state/state_age/power/confidence/mom_conf/signal/
        reject_reason/snapshot/arrays/states/meta/i — الإشارة تُقيَّم على
        آخر شمعة مغلقة فقط ولا تُعدَّل لاحقاً بأي بيانات جديدة (مُختبر)."""
        result = {'ok': False, 'signal': None, 'reject_reason': None,
                  'state': 'NEUTRAL', 'state_age': 0,
                  'power': {'BUY': 0.0, 'SELL': 0.0},
                  'confidence': {'BUY': 0, 'SELL': 0},
                  'mom_conf': {'BUY': 0, 'SELL': 0},
                  'snapshot': {}, 'arrays': None, 'states': None,
                  'meta': None, 'i': None}
        try:
            n = len(df)
            need = cls.min_bars(params)
            if n < need:
                result['reject_reason'] = f'بيانات غير كافية ({n} شمعة < {need})'
                return result
            arr = cls.compute_arrays(df, params)
            states, meta = cls.state_series(arr, params)
            i = n - 1
            decision = cls.evaluate_at(arr, states, meta, i, params)
            result.update(decision)
            result.update({'arrays': arr, 'states': states, 'meta': meta, 'i': i})
            result['ok'] = result['signal'] is not None
            return result
        except Exception as e:
            result['reject_reason'] = f'خطأ تقييم HMA: {e}'
            return result

    @staticmethod
    def exit_reason(arr, states, i, side):
        """سبب خروج استراتيجي إن وجد — على شمعة مغلقة، بشروط ثابتة (لا
        أحداث عابرة) كي تصمد أمام إعادة تشغيل البوت:
        - آلة الحالات صارت ضد اتجاه الصفقة (BULL لصفقة بيع مثلاً).
        - Supertrend مغلق ضد اتجاه الصفقة.
        ملاحظة موثقة: عكس شرط الدخول وحده ليس كافياً — الخروج يخضع لنفس
        آلة الحالات والشروط الثابتة أعلاه، وبوابات الستوب/TP1/الستوب الزمني
        المشتركة تبقى فعالة دائماً."""
        if states is None or i is None or i >= len(states):
            return None
        st = int(states[i])
        if side == 'BUY' and st == -1:
            return 'آلة الحالات انقلبت إلى BEAR'
        if side == 'SELL' and st == 1:
            return 'آلة الحالات انقلبت إلى BULL'
        sd = arr['st_dir'][i] if arr is not None else 0
        if side == 'BUY' and sd == -1:
            return 'Supertrend مغلق ضد اتجاه الشراء'
        if side == 'SELL' and sd == 1:
            return 'Supertrend مغلق ضد اتجاه البيع'
        return None

    @classmethod
    def adx_entry_ok(cls, arr, i, gate):
        """🧭 بوابة الاتجاهية عند الدخول (V11.1 — مُتحقق عليها في مختبر إعادة
        البناء على نافذتين): ADX-14 وايلدر على إطار الاستراتيجية (شموع مغلقة
        فقط)، يُحسب بنفس دالة DMI المحركية (_dmi_adx بنفس الفترتين 14/14).
        يعيد (مسموح؟, قيمة ADX أو None).
        - gate ≤ 0 → البوابة معطلة (يسمح دائماً).
        - ADX غير متاح/غير نهائي → يُرفض (محافظ — لا دخول بلا قياس).
        مطابقة حرفية لمنطق المختبر الموثق (adx14[i] ≥ gate عند شمعة الإشارة)."""
        if gate is None or float(gate) <= 0:
            return True, None
        try:
            _, _, adx14 = cls._dmi_adx(arr['high'], arr['low'], arr['close'], 14, 14)
            if i is None or i >= len(adx14):
                return False, None
            a = float(adx14[i])
            if not math.isfinite(a):
                return False, None
            return (a >= float(gate)), a
        except Exception:
            return False, None


# ══════════════════════════════════════════════════════════════════════
#        🎯 القناص الأسطوري V12.4 — البوت الرئيسي (HMA-Only)
# ══════════════════════════════════════════════════════════════════════
class LegendarySniperHMA:
    def __init__(self):
        self.binance_api_key = os.environ.get('BINANCE_API_KEY', '')
        self.binance_api_secret = os.environ.get('BINANCE_API_SECRET', '')

        self.TRADE_ENABLED = os.environ.get('TRADE_ENABLED', 'false').lower() == 'true'
        self.LEVERAGE = int(os.environ.get('LEVERAGE', '10'))
        self.TRADE_SIZE_USDT = float(os.environ.get('TRADE_SIZE_USDT', '25'))
        self.MIN_WIN_USDT = float(os.environ.get('MIN_WIN_USDT', '0'))   # أرضية اختيارية لهدف الربح (0 = معطلة)
        self.MAX_OPEN_TRADES = int(os.environ.get('MAX_OPEN_TRADES', '3'))
        self.TESTNET = os.environ.get('TESTNET', 'false').lower() == 'true'

        problems = []
        if self.TRADE_SIZE_USDT <= 0:
            problems.append("TRADE_SIZE_USDT يجب أن يكون أكبر من صفر")
        if self.MIN_WIN_USDT < 0:
            problems.append("MIN_WIN_USDT يجب أن يكون صفراً أو أكثر")
        if not (1 <= self.MAX_OPEN_TRADES <= 10):
            problems.append("MAX_OPEN_TRADES يجب أن يكون بين 1 و 10")
        if not (1 <= self.LEVERAGE <= 50):
            problems.append("LEVERAGE يجب أن يكون بين 1 و 50")
        if problems:
            raise SystemExit("❌ إعدادات خاطئة:\n- " + "\n- ".join(problems))
        if self.TESTNET:
            logger.info("🧪 وضع Testnet التجريبي مفعّل — كل التنفيذ تجريبي")

        if self.TRADE_ENABLED and (not self.binance_api_key or not self.binance_api_secret):
            self.TRADE_ENABLED = False
            logger.error("❌ التداول مفعّل لكن مفاتيح API ناقصة! التحويل للمراقبة فقط")

        self.PRICE_MAX_AGE = 30          # أقصى عمر مقبول لسعر الدخول — لا صفقة بأسعار قديمة
        self.REENTRY_COOLDOWN = 900      # تبريد 15 دقيقة لكل زوج بعد إغلاق صفقة
        self.VERIFY_EVERY_N_LOOPS = 5
        self.WS_STALE_ALERT = 120
        self.BALANCE_CACHE_SECONDS = 60

        self.data_url = "https://fapi.binance.com"
        self.trade_url = ("https://testnet.binancefuture.com" if self.TESTNET
                          else "https://fapi.binance.com")
        self.time_offset_ms = 0

        self.db = DatabaseManager()
        self.session = None
        self.ws_task = None
        self._shutdown_requested = False

        self.all_futures_pairs = []
        self.step_sizes_cache = {}
        self.tick_sizes_cache = {}
        self.min_qty_cache = {}
        self.max_qty_cache = {}
        self.min_notional_cache = {}
        self.live_prices = {}
        self.active_trades = {}
        self.reentry_cooldown = {}
        self.error_counts = {}
        self.last_discovery_alert = {}
        self.entry_history = collections.deque(maxlen=200)
        self.last_scan_info = None
        self._last_heartbeat = 0
        self._report_day = time.strftime("%Y-%m-%d")
        self._balance_cache = (0.0, 0.0)
        self._rest_price_ts = {}
        self._last_reject_log = {}       # خنق سجل الرفض: (رمز، سبب) → آخر وقت

        self.hma = HMASettings(self.db)        # كل عتبات HMA_DMI_MOMENTUM
        self.risk = RiskManager(self.db)
        self.news_filter = NewsFilter(self.db)

        self.stats = {'total_scans': 0, 'trades_executed': 0, 'wins': 0, 'losses': 0,
                      'total_signals': 0, 'signals_found': 0,
                      'rejected_by_risk': 0, 'rejected_by_news': 0,
                      'rejected_open_trade': 0, 'rejected_quality': 0,
                      'rejected_execution': 0}

        self.api_rejected = None         # 🚨 علم رفض مفاتيح API (-2015) للوحة

        self.HMA_LIVE = os.environ.get('HMA_LIVE', 'false').lower() == 'true'  # 🧭 يُدار من اللوحة أيضاً
        self.MAX_TRADE_HOURS = float(os.environ.get('TRADE_MAX_HOURS', '24'))   # ⏰ ستوب زمني — V11.1: 24س (المُتحقق عليه للاستراتيجيتين — راجع تقرير إعادة البناء)
        self._universe_cache = []
        self._universe_ts = 0.0
        self._universe_diag = {}         # 🔭 تشخيص الكون: كم زوجاً فُحص/تجاوز الأرضية/قُصي بالانتشار
        self._last_evening_note = 0.0    # 🌙 خنق حدث "نافذة المساء" في سجل اللوحة (حدث كل 15 دقيقة)
        self._last_dash_db = 0.0         # 🗄️ خنق لقطة القاعدة للوحة (كل 8 ثوانٍ)
        self._scan_cursor = 0
        self._ticker_cache = {}          # الرمز → {'qv','change'} من آخر مسح
        self._closing = set()            # مراكز قيد الإغلاق الآن — منع أوامر إغلاق مكررة
        self._recent_entry = {}          # الرمز → وقت آخر دخول (حماية تبنّي اليتيمة من التداخل)

        # 🧭 حالة استراتيجية HMA_DMI_MOMENTUM (الاستراتيجية الوحيدة في هذا البوت)
        self.hma_enabled = os.environ.get('HMA_ENABLED', 'true').lower() != 'false'
        self._hma_done = {}              # (رمز، اتجاه، شمعة الإشارة) → منع التكرار — يصمد لإعادة التشغيل
        self._hma_last_signal_ms = {}    # الرمز → شمعة آخر إشارة HMA معالجة (أساس تبريد الإشارات)
        self._hma_cursor = 0             # مؤشر الدوران على كون HMA
        self.hma_states = {}             # الرمز → آخر حالة آلة الحالات المكتشفة (للعرض)
        self.last_hma_scan_info = None
        self._boot_ts = time.time()      # لحساب مدة التشغيل في اللوحة
        self._scan_now_evt = None        # يُنشأ في main_loop داخل الحلقة الحية

    # ═══ نظام مكافحة الصمت ═══
    def _notify_error(self, source, exc=None, context=""):
        count = self.error_counts.get(source, 0) + 1
        self.error_counts[source] = count
        txt = f"⚠️ {source}" + (f" — {context}" if context else "")
        if exc is not None:
            txt += f" | `{str(exc)[:100]}`"
        logger.warning(f"{txt} (تكرار #{count})")
        if count == 1 or count % 10 == 0:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.tg(f"{txt}\n🔢 مرات التكرار: {count}"))
            except RuntimeError:
                pass

    def _reset_error(self, source):
        self.error_counts.pop(source, None)

    def fmt_price(self, price):
        if price is None or price == 0:
            return "$0"
        if price < 0.00001:
            return f"${price:.10f}"
        elif price < 0.001:
            return f"${price:.6f}"
        elif price < 1:
            return f"${price:.4f}"
        elif price < 100:
            return f"${price:.2f}"
        else:
            return f"${price:,.1f}"

    async def tg(self, msg):
        """كل إشعار تيليجرام يُمَرَّر أيضاً إلى لوحة المراقبة المدمجة."""
        try:
            first_line = msg.split('\n')[0].replace('*', '').strip()
            if msg.startswith('✅'):
                kind = 'دخول'
            elif msg.startswith('🏁'):
                kind = 'خروج'
            elif msg.startswith('🎯') or msg.startswith('🧭'):
                kind = 'إشارة'
            elif msg.startswith('🚨') or msg.startswith('❌'):
                kind = 'خطأ'
            elif msg.startswith('📰'):
                kind = 'أخبار'
            elif msg.startswith('💓'):
                kind = 'نبض'
            elif msg.startswith('🛡️'):
                kind = 'مخاطر'
            else:
                kind = 'نظام'
            ACTION.log(kind, first_line, detail=msg if '\n' in msg else '')
        except Exception:
            pass

    # ═══ توقيت الخادم + طبقة Binance API ═══
    async def sync_server_time(self):
        try:
            res = await self._fapi_request('GET', '/fapi/v1/time')
            if res and 'serverTime' in res:
                self.time_offset_ms = int(res['serverTime']) - int(time.time() * 1000)
                logger.info(f"🕐 مزامنة وقت الخادم: إزاحة {self.time_offset_ms}ms")
        except Exception as e:
            logger.warning(f"تعذر مزامنة وقت الخادم: {e}")

    def _sign(self, params):
        params['timestamp'] = int(time.time() * 1000) + self.time_offset_ms
        params['recvWindow'] = 5000
        query = urlencode(params)
        params['signature'] = hmac.new(
            self.binance_api_secret.encode(), query.encode(), hashlib.sha256
        ).hexdigest()
        return params

    async def _fapi_request(self, method, endpoint, params=None, signed=False, retries=3,
                            quiet=(), soft=(), detailed=False):
        """مع detailed=True يعيد عند الفشل {'_error','_status','_code','_msg'}
        بكود رفض Binance الحقيقي — أساس تشخيص فشل الأوامر في اللوحة."""
        last_err = None
        for attempt in range(max(1, retries)):
            try:
                url = f"{self.trade_url}{endpoint}"
                headers = {'X-MBX-APIKEY': self.binance_api_key} if signed else {}
                req_params = self._sign(dict(params) if params else {}) if signed else params

                async with self.session.request(method, url, params=req_params,
                                                headers=headers, timeout=15) as r:
                    if r.status == 200:
                        if signed and getattr(self, 'api_rejected', None):
                            self.api_rejected = None
                        return await r.json()
                    body = await r.text()
                    code, msg = None, body[:200]
                    try:
                        j = json.loads(body)
                        if isinstance(j, dict):
                            code = j.get('code')
                            msg = str(j.get('msg', body))[:200]
                    except Exception:
                        pass
                    last_err = {'_error': True, '_status': r.status, '_code': code, '_msg': msg}

                    if r.status in (429, 418):
                        await asyncio.sleep(10 * (attempt + 1))
                        continue
                    if r.status == 401:
                        if detailed:
                            return last_err
                        code_401 = last_err.get('_code') if isinstance(last_err, dict) else None
                        if code_401 == -2015:
                            if self.api_rejected is None:
                                self.api_rejected = time.time()
                                logger.error("═" * 62)
                                logger.error("🚨 Binance يرفض مفاتيح API (رمز -2015) — لهذا يظهر الرصيد $0.00")
                                logger.error("المفاتيح يجب أن تكون من testnet.binancefuture.com (فوتشرز) وليس من موقع بينانس الحقيقي")
                                logger.error("الحل: testnet.binancefuture.com ← API Key ← Create HMAC_SHA256 ← Railway Variables ← إعادة نشر")
                                logger.error("═" * 62)
                            self._notify_error("🚨 مفاتيح API مرفوضة (-2015)",
                                context="المفاتيح يجب أن تكون من testnet.binancefuture.com (فوتشرز)")
                        else:
                            self._notify_error("خطأ 401 من Binance",
                                context=f"مفاتيح خاطئة أو مقيدة بـIP | الرد الخام: {body[:200]}")
                        return None
                    if '-1021' in body:
                        logger.warning("⚠️ خطأ توقيم -1021 — مزامنة الوقت وإعادة المحاولة")
                        await self.sync_server_time()
                        await asyncio.sleep(1)
                        continue
                    if r.status >= 500:
                        logger.warning(f"Futures API {r.status} — إعادة محاولة...")
                        await asyncio.sleep(2 ** attempt)
                        continue
                    for c in soft:
                        if str(c) in body:
                            return {'_soft_code': c}
                    if any(str(c) in body for c in quiet):
                        return None
                    if detailed:
                        return last_err
                    logger.warning(f"Futures API Error {r.status}: {body[:120]}")
                    return None
            except asyncio.TimeoutError:
                last_err = {'_error': True, '_status': 0, '_code': None, '_msg': 'timeout'}
                if attempt == max(1, retries) - 1:
                    if detailed:
                        return last_err
                    self._notify_error("انتهت مهلة طلب Binance", context=endpoint)
                    return None
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                last_err = {'_error': True, '_status': 0, '_code': None, '_msg': str(e)[:200]}
                if attempt == max(1, retries) - 1:
                    if detailed:
                        return last_err
                    self._notify_error("فشل طلب Binance", exc=e, context=endpoint)
                    return None
                await asyncio.sleep(2 ** attempt)
        return last_err if detailed else None

    async def load_market_data(self):
        data = await self._fapi_request('GET', '/fapi/v1/exchangeInfo')
        if not data:
            return
        new_pairs = []
        for s in data.get('symbols', []):
            if s['quoteAsset'] == 'USDT' and s['status'] == 'TRADING' and s['contractType'] == 'PERPETUAL':
                new_pairs.append({'symbol': s['symbol'], 'baseAsset': s['baseAsset']})
                for f in s.get('filters', []):
                    if f['filterType'] == 'LOT_SIZE':
                        self.step_sizes_cache[s['symbol']] = float(f['stepSize'])
                        self.min_qty_cache[s['symbol']] = float(f.get('minQty', f['stepSize']))
                        self.max_qty_cache[s['symbol']] = float(f.get('maxQty', 1e12))
                    elif f['filterType'] == 'PRICE_FILTER':
                        self.tick_sizes_cache[s['symbol']] = float(f['tickSize'])
                    elif f['filterType'] == 'MIN_NOTIONAL':
                        self.min_notional_cache[s['symbol']] = float(f.get('notional', f.get('minNotional', 5.0)))
        self.all_futures_pairs = new_pairs
        logger.info(f"📊 تم تحميل {len(self.all_futures_pairs)} زوج عقود آجلة")

    # ═══ أدوات التنسيق الدقيق (كمية/سعر حسب قواعد Binance) ═══
    @staticmethod
    def _decimals_of(step):
        try:
            exp = Decimal(str(step)).normalize().as_tuple().exponent
            return max(0, -exp)
        except Exception:
            return 8

    def _step_qty(self, symbol, qty):
        step = self.step_sizes_cache.get(symbol) or 1.0
        if step <= 0:
            step = 1.0
        dec = self._decimals_of(step)
        return round(math.floor(round(qty / step, 9)) * step, dec)

    def format_quantity(self, symbol, qty):
        return self._step_qty(symbol, qty)

    def qty_to_str(self, symbol, qty):
        step = self.step_sizes_cache.get(symbol) or 1.0
        dec = self._decimals_of(step)
        return f"{self._step_qty(symbol, qty):.{dec}f}"

    def price_to_str(self, symbol, price):
        tick = self.tick_sizes_cache.get(symbol)
        if not tick or tick <= 0:
            if price >= 100:
                dec = 2
            elif price >= 1:
                dec = 4
            elif price >= 0.01:
                dec = 6
            else:
                dec = 8
            return f"{price:.{dec}f}"
        dec = self._decimals_of(tick)
        stepped = math.floor(round(price / tick, 9)) * tick
        return f"{round(stepped, dec):.{dec}f}"

    def get_price(self, symbol):
        p = self.live_prices.get(symbol)
        if p and (time.time() - p.get('ts', 0)) <= self.PRICE_MAX_AGE:
            return p
        return None

    async def _refresh_price_rest(self, symbol):
        """عند تجمّد تدفق WebSocket: جلب bid/ask مباشرة من REST."""
        try:
            res = await self._fapi_request('GET', '/fapi/v1/ticker/bookTicker',
                                           {'symbol': symbol})
            if isinstance(res, dict):
                bid = float(res.get('bidPrice') or 0)
                ask = float(res.get('askPrice') or 0)
                if bid > 0 and ask > 0:
                    self.live_prices[symbol] = {'bid': bid, 'ask': ask, 'ts': time.time()}
                    return self.live_prices[symbol]
            res2 = await self._fapi_request('GET', '/fapi/v1/ticker/price',
                                            {'symbol': symbol})
            if isinstance(res2, dict):
                last = float(res2.get('price') or 0)
                if last > 0:
                    self.live_prices[symbol] = {'bid': last, 'ask': last, 'ts': time.time()}
                    return self.live_prices[symbol]
        except Exception:
            pass
        return None

    def set_cooldown(self, symbol):
        self.reentry_cooldown[symbol] = time.time() + self.REENTRY_COOLDOWN

    def is_in_cooldown(self, symbol):
        expiry = self.reentry_cooldown.get(symbol, 0)
        if time.time() < expiry:
            return True
        self.reentry_cooldown.pop(symbol, None)
        return False

    async def get_available_usdt(self):
        now = time.time()
        cached_val, cached_ts = self._balance_cache
        if now - cached_ts < self.BALANCE_CACHE_SECONDS and cached_ts > 0:
            return cached_val
        res = await self._fapi_request('GET', '/fapi/v2/balance', signed=True)
        avail = 0.0
        if isinstance(res, list):
            for b in res:
                if b.get('asset') == 'USDT':
                    avail = float(b.get('availableBalance', 0))
                    break
        self._balance_cache = (avail, now)
        return avail

    # ═══ WebSocket ═══
    async def ws_manager(self):
        ws_url = ("wss://stream.binancefuture.com/ws/!bookTicker" if self.TESTNET
                  else "wss://fstream.binance.com/ws/!bookTicker")
        while True:
            try:
                async with websockets.connect(ws_url, ping_interval=20) as ws:
                    logger.info("✅ Futures WebSocket متصل (Global Mode)!")
                    self._reset_error("انقطاع WebSocket")
                    async for message in ws:
                        try:
                            data = json.loads(message)
                            if 's' in data and 'b' in data and 'a' in data:
                                self.live_prices[data['s']] = {
                                    'bid': float(data['b']), 'ask': float(data['a']),
                                    'ts': time.time()}
                        except (ValueError, KeyError, TypeError):
                            continue
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self._notify_error("انقطاع WebSocket", exc=e, context="إعادة الاتصال خلال 5 ثوانٍ")
                await asyncio.sleep(5)

    async def get_klines(self, symbol, interval='15m', limit=100):
        data = await self._fapi_request('GET', '/fapi/v1/klines',
            {'symbol': symbol, 'interval': interval, 'limit': limit})
        if data and len(data) > 20:
            df = pd.DataFrame(data, columns=[
                'time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_vol',
                'taker_buy_quote_vol', 'ignore'])
            for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            return df
        return None

    @staticmethod
    def _compute_atr(df, period=14):
        hl = df['high'] - df['low']
        hc = (df['high'] - df['close'].shift()).abs()
        lc = (df['low'] - df['close'].shift()).abs()
        tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
        return float(tr.rolling(period).mean().iloc[-1])

    # ═══ 🎯 هدف TP1: عائد مرتبط بالهامش ═══
    def _tp1_target_profit(self, margin, strategy=None):
        """الربح المستهدف بالدولار: tp1_return_pct% من الهامش المعطى
        (وأرضية اختيارية MIN_WIN_USDT إن وُجدت) — بنسبة مئوية خاصة بكل
        استراتيجية (دائماً من إعدادات HMA)."""
        pct = self.hma.tp1_return_pct
        target = float(margin) * pct / 100.0
        if self.MIN_WIN_USDT > 0:
            target = max(target, self.MIN_WIN_USDT)
        return target

    def _tp1_distance(self, price, strategy=None):
        """
        ⚠️ تقدير ما قبل التنفيذ فقط (يُستخدم في بوابات R:R قبل فتح الصفقة).
        المسافة السعرية التي تحقق ربحاً ≈ tp1_return_pct% من الهامش المخطط.
        بعد التنفيذ يُعاد الحساب من بيانات التنفيذ الفعلية عبر
        _tp1_distance_from_actual (كمية/سعر/رافعة ما بعد التقريب من المنصة).
        الربح = qty × المسافة = (margin×leverage/price) × dist
        ⟹ dist = price × الربح المستهدف / (margin × leverage)
        """
        try:
            margin = self.TRADE_SIZE_USDT
            lev = self.LEVERAGE
            notional = margin * lev
            if notional <= 0 or price <= 0:
                return 0.0
            target = self._tp1_target_profit(margin, strategy)
            return price * target / notional
        except Exception:
            return 0.0

    def _tp1_distance_from_actual(self, entry_price, qty, leverage, strategy=None):
        """🎯 هدف TP1 من بيانات التنفيذ الفعلية (بعد تقريب Binance):
        الهامش الفعلي = qty × السعر الفعلي / الرافعة الفعلية
        الربح المستهدف = الهامش الفعلي × tp1_return_pct/100
        المسافة = الربح المستهدف / الكمية الفعلية المنفذة
        كي يتحقق دائماً: (qty × المسافة) / الهامش الفعلي = pct% بالضبط."""
        try:
            entry_price = float(entry_price)
            qty = float(qty)
            leverage = float(leverage)
            if entry_price <= 0 or qty <= 0 or leverage <= 0:
                return 0.0
            margin = qty * entry_price / leverage
            return self._tp1_target_profit(margin, strategy) / qty
        except Exception:
            return 0.0

    def _round_tp_price(self, symbol, tp, side):
        """تقريب سعر الهدف على Tick ببعيداً عن الدخول كي لا ينقص الهدف بالتقريب:
        BUY → لأعلى | SELL → لأدنى (وفق قواعد دقة Binance)."""
        try:
            tp = float(tp)
        except (TypeError, ValueError):
            return tp
        tick = self.tick_sizes_cache.get(symbol)
        if not tick or tick <= 0:
            return tp
        dec = self._decimals_of(tick)
        ratio = round(tp / tick, 9)
        steps = math.ceil(ratio) if side == 'BUY' else math.floor(ratio)
        return round(steps * tick, dec)

    # ═══ 🧭 تحليل الزوج باستراتيجية HMA_DMI_MOMENTUM ═══
    # ═══════════════════════════════════════════════════════════════════
    # 🧭 استراتيجية HMA_DMI_MOMENTUM — مسار مستقل بمنطقه الخاص، مع تنفيذ
    #    مشترك عبر نفس بوابات المخاطر/الرصيد/الحد الأقصى (execute_trade).
    # ═══════════════════════════════════════════════════════════════════
    def _strategy_display(self, strategy):
        return HMA_STRATEGY_NAME

    def _symbol_owner(self, symbol):
        """استراتيجية مالك الصفقة المفتوحة على الرمز (أو None) — أساس
        سياسة التعارض: مركز واحد لكل رمز، والصفقة يملكها من فتحها."""
        t = self.active_trades.get(symbol)
        return (t.get('strategy') or HMA_STRATEGY_NAME) if t else None

    def _hma_evening_blocked_now(self, now_utc_hour=None):
        """🌙 هل الدخول الجديد محظور الآن بنافذة المساء؟ (المخارج دائماً حرة)
        تدعم النوافذ الالتفافية (مثلاً 22→5) — تُستخدم في analyze_hma واللوحة."""
        if not HMA_BLOCK_EVENING_UTC:
            return False
        h = time.gmtime().tm_hour if now_utc_hour is None else int(now_utc_hour)
        s, e = HMA_EVENING_START_UTC, HMA_EVENING_END_UTC
        if s <= e:
            return s <= h <= e
        return h >= s or h <= e

    async def analyze_hma(self, symbol):
        """تحليل زوج باستراتيجية HMA_DMI_MOMENTUM على شموع مغلقة فقط.
        يعيد (إشارة|None، سبب رفض|None، معلومات_حالة|None) — السبب يُسجَّل
        في القاعدة موسوماً بالاستراتيجية ويُعرض في اللوحة."""
        h = self.hma
        tf = h.timeframe
        # ⛔ فلتر V11.3: أزواج خاسرة مزمنة على النافذتين المستقلتين معاً —
        # مستبعدة من HMA بالكامل (اعتماد المالك). صفقات HMA المفتوحة سابقاً
        # على هذه الأزواج تُدار بمخارجها حتى الإغلاق (هذا المسار للإشارات
        # الجديدة فقط).
        if symbol in HMA_SYMBOL_BLACKLIST:
            return None, 'زوج مستبعد من HMA (فلتر V11.3 — خاسر مزمن على النافذتين)', None
        # 🌙 حظر نافذة المساء: لا دخول جديد خلال النافذة — المخارج تعمل دائماً
        if self._hma_evening_blocked_now():
            return None, (f'🌙 نافذة المساء {HMA_EVENING_START_UTC:02d}–{HMA_EVENING_END_UTC:02d} UTC '
                          '— الدخول الجديد محظور (إدارة المخارج تعمل طبيعياً)'), None
        try:
            # 🧭 700 شمعة عند تفعيل بوابة 4س على إطار 1س: تغذي المحرك والبوابة
            # معاً — المحرك سببي ومقيّد بإعادة التشغيل فلا يتأثر بتاريخ أطول،
            # وهو أقرب لتاريخ الباكتيست الكامل (وزن بذرة EMA50(4س) ≈ 0.09%).
            df = await self.get_klines(symbol, tf, 700 if h.trend4h_enabled else 400)
        except Exception:
            return None, 'فشل جلب الشموع', None
        if df is None or len(df) < 60:
            return None, 'بيانات شموع غير كافية', None
        df = df.iloc[:-1]        # ⛔ الشمعة الجارية خارج التحليل نهائياً (مغلقة فقط)
        if len(df) < 60:
            return None, 'بيانات مغلقة غير كافية', None

        ev = HmaDmiMomentumEngine.evaluate(df, h.as_params())
        if not ev.get('ok'):
            return None, ev.get('reject_reason') or 'تحليل غير مكتمل', None

        state_info = {'state': ev['state'], 'age': ev['state_age'],
                      'ts': time.time(), 'candle_ms': int(df['time'].iloc[-1])}

        sig = ev['signal']
        if not sig:
            return None, ev['reject_reason'], state_info
        side = sig['side']

        # 🧭 بوابة الاتجاهية V11.1: ADX-14 (إطار الاستراتيجية) ≥ adx_gate —
        # استبعاد السوق العرضي عند الدخول (مُتحقق عليها في مختبر إعادة البناء:
        # قلّصت خسائر HMA وحدها بنحو الثلث وحافظت على أفضلية النظام الساعي)
        ok_adx, adx_val = HmaDmiMomentumEngine.adx_entry_ok(
            ev['arrays'], ev['i'], h.adx_gate)
        if not ok_adx:
            if adx_val is not None:
                return None, (f'فلتر الاتجاهية ADX: السوق عرضي '
                              f'(ADX {adx_val:.1f} < {h.adx_gate:g})'), state_info
            return None, 'فلتر الاتجاهية ADX: قياس غير متاح', state_info

        # 🧭 بوابة اتجاه 4 ساعات (V11.3 — اعتماد المالك T3): اتجاه آخر شمعة
        # 4س مغلقة كلياً (EMA{len} على 4س + ميلها عبر آخر 3 شموع 4س) يجب أن
        # يحاذي الإشارة — نفس خوارزمية backtest._trend_4h حرفياً (بلا إعادة
        # رسم: الشمعة 4س الجارية لا تُلمس). 0 (محايد/غير جاهز) = رفض محافظ.
        if h.trend4h_enabled:
            want = 1 if side == 'BUY' else -1
            try:
                if tf == '1h':
                    gdf = df                       # نفس السلسلة المغلقة أعلاه (700 شمعة)
                else:
                    gdf = await self.get_klines(symbol, '1h', 700)
                    gdf = gdf.iloc[:-1] if gdf is not None else None  # ⛔ مغلقة فقط
                if gdf is None or len(gdf) < 240:
                    return None, 'بوابة اتجاه 4 ساعات: بيانات 1س غير كافية', state_info
                tv = int(_trend_4h(gdf, mode='ema_slope',
                                   ema_len=int(h.trend4h_ema_len))[-1])
            except Exception:
                return None, 'بوابة اتجاه 4 ساعات: فشل الحساب', state_info
            if tv != want:
                t_txt = {1: 'صاعد', -1: 'هابط'}.get(tv, 'محايد/غير جاهز')
                return None, (f'بوابة اتجاه 4 ساعات: الاتجاه {t_txt} لا يحاذي '
                              f'{"الشراء" if side == "BUY" else "البيع"} '
                              f'(EMA{int(h.trend4h_ema_len)} على 4س + الميل)'), state_info

        # ⑤ منع تكرار الإشارة لنفس شمعة الإشارة (يصمد لإعادة التشغيل)
        key = int(sig['candle_ms'])
        if self._hma_done.get((symbol, side, key)):
            return None, 'إشارة مكررة لنفس شمعة الإشارة', state_info

        # تبريد الإشارات: لا إشارة جديدة قبل cooldown_candles من آخر إشارة معالجة
        last_ms = self._hma_last_signal_ms.get(symbol, 0)
        tf_ms = HMASettings.TF_MS.get(tf, 900000)
        if last_ms and (key - last_ms) < h.cooldown_candles * tf_ms:
            return None, f'تبريد الإشارات ({h.cooldown_candles} شموع من آخر إشارة)', state_info

        # 💰 وقف الخسارة بعمق sl_atr_mult × ATR (إطار الاستراتيجية) + بوابات المخاطرة
        close = float(sig['close'])
        atr = float(sig['atr'])
        if not (atr and math.isfinite(atr) and atr > 0):
            return None, 'ATR غير صالح', state_info
        sl = close - h.sl_atr_mult * atr if side == 'BUY' else close + h.sl_atr_mult * atr
        if sl <= 0 or math.isnan(sl):
            return None, 'وقف خسارة غير صالح', state_info
        risk_dist = abs(close - sl)
        risk_pct = risk_dist / close * 100 if close > 0 else 0.0
        if risk_pct < h.risk_min_pct or risk_pct > h.risk_max_pct:
            return None, f'المسافة إلى وقف الخسارة غير مناسبة ({risk_pct:.2f}%)', state_info

        # 🎯 هدف TP1 (نسبة HMA) + جدوى العائد مقابل المخاطرة
        tp1_dist = self._tp1_distance(close, strategy=HMA_STRATEGY_NAME)
        if tp1_dist <= 0:
            return None, 'فشل حساب هدف TP1', state_info
        if tp1_dist > h.tp1_max_atr * atr:
            return None, (f'هدف TP1 بعيد عن ظروف السوق '
                          f'({tp1_dist/atr:.1f}×ATR > {h.tp1_max_atr:g}×ATR)'), state_info
        rr = tp1_dist / risk_dist if risk_dist > 0 else 0.0
        if rr < h.min_rr:
            return None, f'العائد المحتمل غير مجدٍ (R:R = {rr:.2f} < {h.min_rr:g})', state_info

        tp1 = close + tp1_dist if side == 'BUY' else close - tp1_dist
        state_txt = f"{sig['state']} عمرها {ev['state_age']} شمعة"
        if sig['override']:
            head = (f"🧭 HMA_DMI_MOMENTUM: {side} عبر استثناء هيكلي — {state_txt}")
        else:
            head = f"🧭 HMA_DMI_MOMENTUM: {side} — {state_txt}"
        lines = [
            head,
            f"✅ الزناد: {sig['reason_txt']} (إطار {tf} — شموع مغلقة فقط)",
            f"📐 القوة {sig['power']:g}/100 | الثقة {sig['confidence']}/9 | زخم {sig['mom_conf']}/3"
            + (f" | ADX {adx_val:.1f} ✓" if adx_val is not None else "")
            + (" | فلتر EMA200 ✓" if h.ema_filter else "")
            + (" | بوابة 4س ✓" if h.trend4h_enabled else ""),
            f"🛡️ ستوب ATR ({h.sl_atr_mult:g}×) ({risk_pct:.2f}%) | R:R {rr:.2f}",
            f"💰 TP1 = {h.tp1_return_pct:g}% من الهامش ({self.fmt_price(tp1)}) — إغلاق 100% عند اللمس",
        ]
        analysis = {
            'symbol': symbol, 'direction': side, 'strategy': HMA_STRATEGY_NAME,
            'price': close, 'sl': sl, 'tp1': tp1,
            'score': int(sig['confidence']), 'hma_key': key,
            'validation': {'atr_1h': atr,     # ATR بإطار الاستراتيجية — يستخدمه فحص TP1 لحظة التنفيذ
                           'risk_min_pct': h.risk_min_pct,
                           'risk_max_pct': h.risk_max_pct},
            'components': {
                'engine': HMA_STRATEGY_NAME, 'trigger': sig['reason_txt'],
                'state': sig['state'], 'state_age': ev['state_age'],
                'timeframe': tf, 'power': round(sig['power'], 1),
                'confidence': int(sig['confidence']), 'override': bool(sig['override']),
                'mom_conf': int(sig['mom_conf']),
                'adx': (round(adx_val, 1) if adx_val is not None else None),
                'rr': round(rr, 2), 'risk_pct': round(risk_pct, 2),
                'score': int(sig['confidence']), 'candle_ms': key,
            },
            'lines': lines,
        }
        return analysis, None, state_info

    async def _hma_signal_only(self, a):
        """🧭 وضع الإشارات فقط لاستراتيجية HMA — تسجيل موسوم باسمها."""
        try:
            await self.db.log_signal(a['symbol'], a['direction'], time.time(),
                                     a['score'], a['components'],
                                     strategy=HMA_STRATEGY_NAME)
        except Exception:
            pass

    async def _mark_hma_done(self, a):
        """استهلاك إشارة HMA: (الرمز، الاتجاه، شمعة الإشارة) — يُحفظ في
        القاعدة فوراً كي لا تعود الإشارة نفسها بعد إعادة تشغيل البوت."""
        key = (a['symbol'], a['direction'], int(a['hma_key']))
        self._hma_done[key] = time.time()
        self._hma_last_signal_ms[a['symbol']] = max(
            self._hma_last_signal_ms.get(a['symbol'], 0), int(a['hma_key']))
        try:
            data = {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in self._hma_done.items()}
            await self.db.set_param('hma_done', json.dumps(data))
        except Exception as e:
            logger.warning(f"تعذر حفظ مفتاح تكرار HMA: {e}")

    async def _load_hma_done(self):
        self._hma_done = {}
        self._hma_last_signal_ms = {}
        raw = await self.db.get_param('hma_done')
        if raw:
            try:
                for k, v in json.loads(raw).items():
                    sym, side, cm = k.split('|')
                    self._hma_done[(sym, side, int(cm))] = float(v)
                    self._hma_last_signal_ms[sym] = max(
                        self._hma_last_signal_ms.get(sym, 0), int(cm))
            except Exception as e:
                logger.warning(f"تعذر استعادة سجل إشارات HMA: {e}")
        self._prune_hma_done()

    def _prune_hma_done(self):
        cutoff = time.time() - 48 * 3600
        self._hma_done = {k: v for k, v in self._hma_done.items() if v > cutoff}

    async def _hma_exit_check(self, symbol, trade):
        """فحص الخروج الاستراتيجي لصفقة HMA مملوكة — شموع مغلقة فقط.
        يعيد (سبب الخروج|None، معلومات_الحالة|None)."""
        tf = self.hma.timeframe
        try:
            df = await self.get_klines(symbol, tf, 400)
        except Exception:
            return None, None
        if df is None or len(df) < 60:
            return None, None
        df = df.iloc[:-1]        # ⛔ شموع مغلقة فقط
        ev = HmaDmiMomentumEngine.evaluate(df, self.hma.as_params())
        if not ev.get('ok'):
            return None, None
        state_info = {'state': ev['state'], 'age': ev['state_age'],
                      'ts': time.time(), 'candle_ms': int(df['time'].iloc[-1])}
        reason = HmaDmiMomentumEngine.exit_reason(ev['arrays'], ev['states'],
                                                  ev['i'], trade['side'])
        return reason, state_info

    async def scan_hma(self):
        """دورة استراتيجية HMA_DMI_MOMENTUM: مراقبة مخارج صفقاتها المملوكة
        أولاً ثم مسح دفعة دوّارة من الكون السائل — التنفيذ عبر المسار المشترك
        (execute_trade) مع نفس بوابات المخاطر والرصيد والحد الأقصى، ومركز
        واحد لكل رمز: إشارة تصطدم بصفقة قائمة (لأي استراتيجية) تُستهلك
        فوراً بسجل واضح — بلا طابور مؤجل."""
        if not self.hma_enabled:
            self.last_hma_scan_info = {'ts': time.time(), 'enabled': False,
                                       'scanned': 0, 'signals': 0, 'exits': 0}
            return
        h = self.hma
        universe = [r['symbol'] for r in (self._universe_cache or [])][:int(h.universe_size)]
        owned = [s for s in self.active_trades
                 if self._symbol_owner(s) == HMA_STRATEGY_NAME]
        batch_syms = owned[:]          # صفقات HMA المفتوحة تُراقب دائماً (مخارج)
        seen = set(batch_syms)
        n = len(universe)
        # 🌙 صمت نافذة المساء (إصلاح طوفان السجل): أثناء الحظر لا نحلل ولا
        # نرفض رمزاً-برمز — تُتخطى دفعة الدخول كاملة ويُسجل حدث دورة واحد
        # مُخنق كل 15 دقيقة. المخارج (الصفقات المملوكة) تعمل دائماً.
        try:
            evening_now = bool(self._hma_evening_blocked_now())
        except Exception:
            evening_now = False
        if n and not evening_now:
            rot = min(max(1, int(h.batch_size)), n)
            start = self._hma_cursor % n
            for k in range(rot):
                s = universe[(start + k) % n]
                if s not in seen:
                    seen.add(s)
                    batch_syms.append(s)
            self._hma_cursor = (start + rot) % n
        elif n and evening_now:
            self.stats['evening_skipped'] = self.stats.get('evening_skipped', 0) + n
            if time.time() - self._last_evening_note >= 900:
                self._last_evening_note = time.time()
                ACTION.log('دورة',
                           f"🌙 نافذة المساء سارية ({HMA_EVENING_START_UTC:02d}:00–"
                           f"{HMA_EVENING_END_UTC:02d}:59 UTC) — تخطي مسح الدخول "
                           f"({n} زوجاً في الكون) — المخارج والإدارة تعمل طبيعياً")

        sem = asyncio.Semaphore(max(1, int(h.parallel)))
        results, rejects = [], []
        exits = 0

        async def one(sym):
            nonlocal exits
            async with sem:
                trade = self.active_trades.get(sym)
                if trade and self._symbol_owner(sym) != HMA_STRATEGY_NAME:
                    return     # ⛔ الصفقة مملوكة لاستراتيجية أخرى — لا تداخل (سياسة التعارض)
                if trade:
                    # صفقة HMA مفتوحة → فحص الخروج الاستراتيجي على شمعة مغلقة
                    try:
                        exit_reason, state_info = await self._hma_exit_check(sym, trade)
                    except Exception as e:
                        self._notify_error(f"فحص خروج HMA {sym}", exc=e)
                        return
                    if state_info:
                        self.hma_states[sym] = state_info
                    if exit_reason:
                        prices = self.get_price(sym) or await self._refresh_price_rest(sym)
                        px = (prices['bid'] if trade['side'] == 'BUY' else prices['ask']) \
                            if prices else trade['entry_price']
                        closed, fill, pnl_over = await self._close_position(trade, px)
                        if closed:
                            exits += 1
                            await self._finalize_trade(
                                trade, fill, f"🧭 خروج استراتيجي HMA — {exit_reason}", pnl_over)
                    return    # لا إشارة دخول جديدة لرمز لديه صفقة قائمة
                try:
                    a, reason, state_info = await self.analyze_hma(sym)
                except Exception as e:
                    self._notify_error(f"فحص HMA {sym}", exc=e)
                    return
                if state_info:
                    self.hma_states[sym] = state_info
                if a:
                    results.append(a)
                elif reason:
                    rejects.append((sym, reason))

        await asyncio.gather(*[one(s) for s in batch_syms])

        self.last_hma_scan_info = {'ts': time.time(), 'enabled': True,
                                   'scanned': len(batch_syms),
                                   'signals': len(results), 'exits': exits,
                                   'cursor': self._hma_cursor,
                                   'skipped_evening': (n if evening_now else 0)}
        await self._log_rejections(rejects, strategy=HMA_STRATEGY_NAME)

        # 🔔 تنبيه الإشارات الجديدة (خنق 30 دقيقة لكل رمز+اتجاه)
        now = time.time()
        for a in results:
            key = (a['symbol'], a['direction'], 'hma')
            if now - self.last_discovery_alert.get(key, 0) < 1800:
                continue
            self.last_discovery_alert[key] = now
            await self.tg(f"🧭 *إشارة HMA_DMI_MOMENTUM جديدة:* `{a['symbol']}` *{a['direction']}* "
                          f"({a['components']['state']} | قوة {a['components']['power']:g} | "
                          f"ثقة {a['score']}/9 | إطار {a['components']['timeframe']})")

        # ⚙️ التنفيذ المشترك — الأعلى ثقة أولاً بحد أقصى للدورة، بلا طابور مؤجل
        results.sort(key=lambda a: a['score'], reverse=True)
        executed = 0
        for a in results:
            if len(self.active_trades) >= self.MAX_OPEN_TRADES:
                self.stats['rejected_open_trade'] += 1
                await self._mark_hma_done(a)   # ⛔ استهلاك الإشارة — لا تنفيذ مؤجل
                await self._log_rejections([(
                    a['symbol'],
                    'صفقة مفتوحة — الإعداد استُهلك ولن يُنفَّذ لاحقاً (يُعاد التحليل بعد الإغلاق)')],
                    strategy=HMA_STRATEGY_NAME)
                continue
            if executed >= int(h.max_signals_per_scan):
                break
            if not self.HMA_LIVE:
                await self._hma_signal_only(a)
                await self._mark_hma_done(a)   # 🛠️ إصلاح: كان بلا await — مفاتيح منع التكرار لا تُحفظ
                continue
            ok, why = await self.execute_trade(a)
            if ok:
                executed += 1
                await self._mark_hma_done(a)   # 🛠️ إصلاح: كان بلا await
                await asyncio.sleep(0.5)
            else:
                self.stats['rejected_execution'] += 1
                await self._log_rejections([(a['symbol'], f'رُفضت لحظة التنفيذ: {why}')],
                                           strategy=HMA_STRATEGY_NAME)


    # ═══ سجل أسباب الرفض (خنق: رمز+سبب مرة كل 30 دقيقة) — موسوم بالاستراتيجية ═══
    async def _log_rejections(self, rejects, strategy=HMA_STRATEGY_NAME):
        now = time.time()
        fresh = []
        for item in rejects:
            symbol, reason = item[0], item[1]
            details = item[2] if len(item) > 2 else ''
            key = (symbol, reason)
            if now - self._last_reject_log.get(key, 0) < 1800:
                continue
            self._last_reject_log[key] = now
            fresh.append((symbol, reason, details))
        if not fresh:
            return
        self.stats['rejected_quality'] += len(fresh)
        for symbol, reason, details in fresh:
            ACTION.log('رفض', f'{symbol}: {reason}', reason=reason,
                       symbol=symbol, detail=details)
            await self.db.log_rejection(symbol, reason, details, strategy=strategy)

    # ═══ المسح: كون HMA السائل — تحديث دوري بأعلى سيولة 24س ═══
    async def _refresh_universe(self):
        """تحديث كون HMA: كل أزواج USDT الدائمة بسيولة 24س ≥ الحد الأدنى،
        مرتبة تنازلياً بالسيولة حتى HMA_UNIVERSE_POOL — وscan_hma يأخذ
        أعلى HMA_UNIVERSE_SIZE منها كل دورة (كون مستقل بالكامل)."""
        tickers = await self._fapi_request('GET', '/fapi/v1/ticker/24hr')
        if not tickers:
            self._notify_error("فشل جلب بيانات السوق", context="مشكلة اتصال مؤقتة")
            return
        self._reset_error("فشل جلب بيانات السوق")

        valid = {p['symbol'] for p in self.all_futures_pairs}
        rows = []
        self._ticker_cache = {}
        for t in tickers:
            sym = t.get('symbol', '')
            if sym not in valid:
                continue
            try:
                qv = float(t.get('quoteVolume') or 0)
                chg = float(t.get('priceChangePercent') or 0)
            except (TypeError, ValueError):
                continue
            self._ticker_cache[sym] = {'qv': qv, 'change': chg}
            if qv >= HMA_SCAN_MIN_VOL_USDT:
                rows.append({'symbol': sym, 'qv': qv, 'change': chg})
        rows.sort(key=lambda x: x['qv'], reverse=True)
        pool = rows[:max(1, int(HMA_UNIVERSE_POOL))]
        pool_pre_spread = len(pool)

        # استبعاد اختياري للانتشار العريض — حين يكون سعر حي طازجاً متاحاً فقط
        if HMA_MAX_SPREAD_PCT > 0:
            now_ts = time.time()
            kept = []
            for r in pool:
                p = self.live_prices.get(r['symbol'])
                if (p and p.get('ask') and p.get('bid')
                        and now_ts - p.get('ts', 0) <= 60):
                    try:
                        if (float(p['ask']) - float(p['bid'])) / float(p['ask']) * 100 \
                                > HMA_MAX_SPREAD_PCT:
                            continue
                    except (TypeError, ZeroDivisionError):
                        pass
                kept.append(r)
            pool = kept

        self._universe_cache = pool
        self._universe_ts = time.time()
        # 🔭 تشخيص الكون (سؤال المالك: لماذا يظهر العدد أقل من 200؟)
        # المعروض = المرشح الفعلي = الأزواج فوق أرضية السيولة (بسقف POOL) —
        # وليس الحجم المطلوب؛ إذا كانت سيولة السوق العامة منخفضة صار
        # المرشح أصغر طبيعياً. POOL/SIZE يعملان لكنهما لا يخلقان سيولة.
        self._universe_diag = {
            'total': len(valid),                 # كل أزواج الفوتشرز الدائمة
            'floor': len(rows),                  # من تجاوزوا حد السيولة 24س
            'pool_pre_spread': pool_pre_spread,  # بعد سقف POOL وقبل قص الانتشار
            'spread_cut': pool_pre_spread - len(pool),
            'pool': len(pool),
            'pool_cap': int(HMA_UNIVERSE_POOL),
            'min_vol_musd': round(float(HMA_SCAN_MIN_VOL_USDT or 0) / 1e6, 1),
            'ts': time.time(),
        }

    # ═══ التنفيذ — مع إعادة تحقق كاملة لحظة الدخول (مسار مشترك للاستراتيجيتين) ═══
    async def execute_trade(self, analysis):
        """ينفذ إشارة HMA_DMI_MOMENTUM بعد كل بوابات الحماية وإعادة التحقق
        اللحظي — العتبات من إعدادات HMA حصراً. يعيد (نجاح؟، السبب)."""
        strat = analysis.get('strategy') or HMA_STRATEGY_NAME
        if not self.TRADE_ENABLED:
            return False, 'التداول معطل'
        if len(self.active_trades) >= self.MAX_OPEN_TRADES:
            return False, 'صفقة مفتوحة — الحد الأقصى للصفقات المتزامنة'

        # ✅ بوابة مدير المخاطر (3 متتالية → 4س | يومي 3 → اليوم | سحب 5%) — مشتركة
        can, reason = self.risk.can_trade()
        if not can:
            self.stats['rejected_by_risk'] += 1
            logger.warning(f"🛡️ إشارة {analysis['symbol']} ({strat}) مرفوضة بمدير المخاطر: {reason}")
            await self._log_rejections([(analysis['symbol'], f'🛡️ مدير المخاطر: {reason}')],
                                       strategy=strat)
            return False, reason

        # ✅ فلتر الأخبار (يُدار من اللوحة — تعطيله يمرر كل الإشارات) — مشترك
        news_blocked, news_reason = self.news_filter.is_blocked_now()
        if news_blocked:
            self.stats['rejected_by_news'] += 1
            self.news_filter.rejected_total += 1
            logger.info(f"📰 إشارة {analysis['symbol']} ({strat}) مرفوضة — {news_reason}")
            await self._log_rejections([(analysis['symbol'], f'📰 فلتر الأخبار: {news_reason}')],
                                       strategy=strat)
            return False, news_reason

        symbol = analysis['symbol']
        side = analysis['direction']
        r_min = self.hma.risk_min_pct
        r_max = self.hma.risk_max_pct
        min_rr_eff = self.hma.min_rr
        tp1_max_atr_eff = self.hma.tp1_max_atr
        tp1_pct_eff = self.hma.tp1_return_pct
        if symbol in self.active_trades:
            return False, 'يوجد صفقة جارية على نفس الزوج'
        if self.is_in_cooldown(symbol):
            return False, 'الزوج في فترة تبريد بعد صفقة سابقة'

        # ⛔ إعادة تحقق لحظية: سعر حي + الاختراق ما زال سارياً
        prices = self.get_price(symbol) or await self._refresh_price_rest(symbol)
        if not prices:
            return False, 'لا سعر حي لحظة التنفيذ (تدفق الأسعار متوقف؟)'
        bid = float(prices.get('bid') or 0)
        ask = float(prices.get('ask') or 0)
        if bid <= 0 or ask <= 0:
            return False, 'سعر غير صالح لحظة التنفيذ'
        entry_price = ask if side == 'BUY' else bid

        v = analysis.get('validation', {})

        sl = analysis['sl']
        if side == 'BUY' and sl >= entry_price:
            return False, 'وقف الخسارة لم يعد منطقياً لحظة التنفيذ'
        if side == 'SELL' and sl <= entry_price:
            return False, 'وقف الخسارة لم يعد منطقياً لحظة التنفيذ'

        risk_dist = abs(entry_price - sl)
        risk_pct = risk_dist / entry_price * 100
        if risk_pct < r_min or risk_pct > r_max:
            return False, f'مسافة الستوب غير مناسبة لحظة التنفيذ ({risk_pct:.2f}%)'

        tp1_dist = self._tp1_distance(entry_price, strategy=strat)
        if tp1_dist <= 0:
            return False, 'فشل حساب هدف TP1'
        atr_1h = v.get('atr_1h')
        if atr_1h and tp1_dist > tp1_max_atr_eff * atr_1h:
            return False, 'هدف TP1 بدا بعيداً عن ظروف السوق لحظة التنفيذ'
        rr = tp1_dist / risk_dist if risk_dist > 0 else 0.0
        if rr < min_rr_eff:
            return False, f'R:R تحلل لحظة التنفيذ ({rr:.2f} < {min_rr_eff:g})'

        # 💵 الرصيد
        available = await self.get_available_usdt()
        if available < self.TRADE_SIZE_USDT * 1.2:
            return False, f'رصيد غير كافٍ ({available:.2f}$ < المطلوب {self.TRADE_SIZE_USDT * 1.2:.2f}$)'

        # 📐 الكمية بدقة المنصة (Step/Min/Max/Notional)
        notional = self.TRADE_SIZE_USDT * self.LEVERAGE
        quantity = self.format_quantity(symbol, notional / entry_price)
        if quantity <= 0:
            return False, 'كمية محسوبة = صفر'
        if quantity < self.min_qty_cache.get(symbol, 0.0):
            return False, 'كمية أقل من الحد الأدنى للزوج'
        if quantity > self.max_qty_cache.get(symbol, 1e12):
            return False, 'كمية أعلى من الحد الأقصى للزوج'
        if quantity * entry_price < self.min_notional_cache.get(symbol, 5.0) * 1.02:
            return False, 'قيمة الأمر أقل من الحد الأدنى (Notional) للزوج'

        # رافعة + هامش معزول لهذا الزوج
        await self._fapi_request('POST', '/fapi/v1/leverage',
            {'symbol': symbol, 'leverage': self.LEVERAGE}, signed=True)
        await self._fapi_request('POST', '/fapi/v1/marginType',
            {'symbol': symbol, 'marginType': 'ISOLATED'}, signed=True, quiet=(-4046,))

        # 🚀 دخول ماركت — محاولة واحدة فقط (لا إعادة إرسال تلقائية منعاً
        # للدخول المزدوج عند انتهاء مهلة طلب نفّذ فعلياً)
        result = await self._fapi_request('POST', '/fapi/v1/order', {
            'symbol': symbol, 'side': side, 'type': 'MARKET',
            'quantity': self.qty_to_str(symbol, quantity)
        }, signed=True, retries=1)

        entry_status = result.get('status') if isinstance(result, dict) else None
        if entry_status not in ('FILLED', 'NEW'):
            # الرد ضاع أو فشل — نتحقق من المركز الفعلي قبل إعلان الفشل:
            # إن نُفّذ الدخول وضاع ردُه نتبنّى المركز (لا مركز ضائع ولا دخول مزدوج)
            min_step = (self.step_sizes_cache.get(symbol)
                        or self.min_qty_cache.get(symbol) or 1e-12)
            amt_check = await self.get_position_amt(symbol)
            if amt_check is not None and abs(amt_check) >= min_step:
                entry_status = 'FILLED'
                result = None
                self._notify_error(f"رد أمر الدخول ضاع لـ {symbol}",
                                   context="تأكد الدخول عبر فحص المركز الفعلي — الصفقة ستُدار طبيعياً")
            else:
                await self.tg(f"❌ *فشل تنفيذ {side} (`{symbol}`)*\n"
                              "⚠️ لن يُعاد الإرسال تلقائياً — منعاً للدخول المزدوج")
                return False, 'فشل أمر الدخول لدى Binance'

        # 📐 بيانات التنفيذ الفعلية: الكمية والسعر والرافعة بعد تقريب Binance
        fill_avg = 0.0
        fill_qty = 0.0
        if isinstance(result, dict):
            try:
                fill_avg = float(result.get('avgPrice') or 0)
            except (TypeError, ValueError):
                fill_avg = 0.0
            try:
                fill_qty = float(result.get('executedQty') or 0)
            except (TypeError, ValueError):
                fill_qty = 0.0
        pos = await self._get_position_info(symbol)
        real_entry = (pos['entry'] if pos and pos['entry'] > 0
                      else (fill_avg if fill_avg > 0 else entry_price))
        actual_qty = (abs(pos['amt']) if pos and abs(pos.get('amt', 0) or 0) > 0
                      else (fill_qty if fill_qty > 0 else quantity))
        if symbol in self.step_sizes_cache:   # إعادة الالتزام بخطوة الزوج إن كانت معروفة
            actual_qty = self.format_quantity(symbol, actual_qty) or quantity
        actual_lev = (pos['leverage'] if pos and pos['leverage'] > 0 else float(self.LEVERAGE))
        actual_margin = (pos['initial_margin'] if pos and pos['initial_margin'] > 0
                         else actual_qty * real_entry / actual_lev)

        # 🎯 TP1 من الهامش الفعلي المستخدم (كمية منفذة × سعر فعلي × رافعة فعلية)
        tp1_dist = self._tp1_distance_from_actual(real_entry, actual_qty, actual_lev, strategy=strat)
        if tp1_dist <= 0:
            tp1_dist = self._tp1_distance(real_entry)
        tp1_raw = real_entry + tp1_dist if side == 'BUY' else real_entry - tp1_dist
        tp1 = self._round_tp_price(symbol, tp1_raw, side)

        trade_data = {
            'symbol': symbol, 'side': side, 'entry_price': real_entry,
            'quantity': actual_qty, 'sl': sl, 'tp': tp1,
            'score': analysis.get('score'),
            'strategy': strat,
            'trailing_active': False, 'highest_price': real_entry,
            'lowest_price': real_entry, 'entry_time': time.time(),
            'realized_pnl': 0.0,
            # 🛡️ V11.2 وقف التعادل: ATR لحظة الدخول (لإطلاق التعادل 1.0×ATR)
            'atr_entry': float((analysis.get('validation') or {}).get('atr_1h') or 0.0),
            'be_done': False,
            'stop_order_id': None, 'tp_order_id': None,
            'stop_state': 'none', 'stop_error': None,
            'stop_synced_price': None,
        }
        self.active_trades[symbol] = trade_data
        self._recent_entry[symbol] = time.time()
        await self.db.save_trade(trade_data)
        self.stats['trades_executed'] += 1
        self.entry_history.append((time.time(), time.strftime("%Y-%m-%d")))
        await self.db.log_signal(symbol, side, trade_data['entry_time'],
                                 analysis['score'], analysis['components'], strategy=strat)

        ref_price = bid if side == 'BUY' else ask
        await self._sync_stop_order(trade_data, ref_price)
        await self.db.save_trade(trade_data)

        # إشعار الشفافية: الهدف الإجمالي مقابل الصافي التقديري بعد الرسوم
        target_gross = self._tp1_target_profit(actual_margin, strategy=strat)
        fees_est = actual_qty * real_entry * 0.001   # تقدير تيكر 0.05% × طرفين
        risk_pct_real = abs(real_entry - sl) / real_entry * 100 if real_entry > 0 else risk_pct
        st_state = trade_data.get('stop_state')
        if st_state == 'verified':
            stop_txt = '✅ مثبّت ومؤكد على المنصة'
        elif st_state == 'placed':
            stop_txt = '🟡 مثبّت — بانتظار التأكيد'
        elif st_state == 'local':
            stop_txt = '🛡️ مراقبة محلية فعّالة (فشل تثبيت أمر المنصة)'
        else:
            stop_txt = '⏳ جارٍ التثبيت...'
        strat_line = ''
        if is_hma:
            comp = analysis.get('components', {})
            strat_line = (f"🧭 الزناد: {comp.get('trigger', '—')} | {comp.get('state', '—')} | "
                          f"قوة {comp.get('power', '—')} | ثقة {comp.get('confidence', '—')}/9"
                          + (' (استثناء هيكلي)' if comp.get('override') else '') + "\n")
        msg = (f"✅ *صفقة {self._strategy_display(strat)} منفذة!* (جودة {analysis['score']})\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
               f"🪙 `{symbol}` | {side} | رافعة {actual_lev:g}x | هامش فعلي {actual_margin:.2f}$\n"
               f"📐 تنفيذ فعلي: كمية {actual_qty} @ {self.fmt_price(real_entry)}\n"
               + strat_line
               + f"🛑 SL: {self.fmt_price(sl)} ({risk_pct_real:.2f}%)\n"
               f"🎯 TP1: {self.fmt_price(tp1)} — إغلاق 100% للمركز عند اللمس\n"
               f"💰 هدف الربح: ~{target_gross:.2f} USDT إجمالاً ({tp1_pct_eff:g}% من الهامش الفعلي)\n"
               f"🧾 صافٍ تقديري بعد الرسوم: ~{max(0.0, target_gross - fees_est):.2f} USDT\n"
               f"🛡️ ستوب المنصة: {stop_txt}\n"
               f"⏰ ستوب زمني: {self.MAX_TRADE_HOURS:g} ساعة")
        await self.tg(msg)
        return True, 'تم التنفيذ'

    # ═══ أوامر المنصة الشرطية ═══
    async def _place_conditional_order(self, params, detailed=False):
        """تثبيت STOP_MARKET / TAKE_PROFIT_MARKET عبر /fapi/v1/order.
        مع detailed=True يعيد (حالة، حمولة) وحمولة الفشل تحمل كود رفض
        Binance الحقيقي."""
        res = await self._fapi_request('POST', '/fapi/v1/order', params, signed=True, detailed=True)
        if isinstance(res, dict):
            if res.get('_error'):
                return ('ERROR', res) if detailed else None
            oid = res.get('orderId')
            if oid:
                return ('OK', int(oid)) if detailed else int(oid)
            return ('OK', 'UNKNOWN') if detailed else 'UNKNOWN'
        return (('ERROR', {'_error': True, '_code': None, '_msg': 'رد غير متوقع'})
                if detailed else None)

    async def _cancel_conditional_order(self, symbol, order_id):
        await self._fapi_request('DELETE', '/fapi/v1/order',
            {'symbol': symbol, 'orderId': order_id}, signed=True, quiet=('-2011', '-2013'))

    # ═══ 🛡️ وقف الخسارة: STOP_MARKET حقيقي + مراقبة محلية احتياطية ═══
    async def _place_stop_order(self, trade, desired=None):
        """
        سلّم محاولات لتثبيت ستوب حي على المنصة:
        1) STOP_MARKET reduceOnly بالكمية المتبقية
        2) STOP_MARKET closePosition
        3) فشل الاثنين → مراقبة محلية فعّالة (البوت يغلق ماركت عند الستوب)
        الحالة تُعرض في اللوحة كما هي فعلاً — بلا ادعاءات.
        """
        symbol = trade['symbol']
        is_buy = trade['side'] == 'BUY'
        desired = trade['sl'] if desired is None else desired
        if not desired or desired <= 0:
            return False
        close_side = 'SELL' if is_buy else 'BUY'
        stop_str = self.price_to_str(symbol, desired)
        base = {'symbol': symbol, 'side': close_side, 'type': 'STOP_MARKET',
                'stopPrice': stop_str, 'workingType': 'CONTRACT_PRICE'}
        attempts = [
            ('reduceOnly', dict(base, quantity=self.qty_to_str(symbol, trade['quantity']),
                                reduceOnly='true')),
            ('closePosition', dict(base, closePosition='true')),
        ]
        errs = []
        for label, params in attempts:
            status, res = await self._place_conditional_order(params, detailed=True)
            if status == 'OK':
                trade['stop_order_id'] = None if res == 'UNKNOWN' else int(res)
                trade['stop_synced_price'] = desired
                trade['stop_state'] = 'placed'
                trade['stop_method'] = f'PLATFORM_{label}'
                trade['stop_error'] = None
                trade['stop_placed_at'] = time.time()   # نافذة سماح 90 ث للتأكيد
                await self._verify_stop_on_platform(trade)
                self._reset_error(f"ستوب المنصة {symbol}")
                return True
            errs.append(f"{label}: {res.get('_code')} {(res.get('_msg') or '')[:90]}".strip())

        trade['stop_order_id'] = None
        trade['stop_synced_price'] = desired
        trade['stop_state'] = 'local'
        trade['stop_method'] = 'LOCAL_MONITORING'
        trade['stop_error'] = ' | '.join(errs)[:200]
        trade['stop_retry_at'] = time.time() + 900
        self._notify_error(f"ستوب المنصة غير متاح لـ {symbol}",
                           context='المراقبة المحلية فعّالة وتغلق عند الستوب — إعادة محاولة لاحقاً')
        return True

    async def _verify_stop_on_platform(self, trade, strict=False):
        """التحقق الحقيقي: يفتح openOrders ويبحث عن أمر الستوب فعلياً —
        حالة (مؤكد ✓) لا تُمنح إلا برؤية الأمر حياً على المنصة.
        strict=True: عندما يتعذر العثور على الأمر تُخفض الحالة إلى مراقبة
        محلية فوراً مع إعادة تثبيت عاجلة — المركز لا يُعرض محمياً على المنصة
        إذا لم نستطع إثبات وجود أمر الوقف فعلاً."""
        if trade.get('stop_method') == 'LOCAL_MONITORING':
            return trade.get('stop_state') == 'verified'
        symbol = trade['symbol']
        orders = await self._fapi_request('GET', '/fapi/v1/openOrders',
            {'symbol': symbol}, signed=True)
        if not isinstance(orders, list):
            # تعذر التحقق (انقطاع/خطأ شبكة) — الحالة تبقى كما هي ولا تُرقّى
            # إلى مؤكد أبداً، وإعادة الفحص القادمة تتولى الأمر
            return trade.get('stop_state') == 'verified'
        want = trade.get('stop_synced_price')
        want_str = self.price_to_str(symbol, want) if want else None
        for o in orders:
            if o.get('type') not in ('STOP_MARKET', 'STOP') or o.get('status') != 'NEW':
                continue
            if trade.get('stop_order_id') and o.get('orderId') == trade['stop_order_id']:
                trade['stop_state'] = 'verified'
                trade['stop_verified_at'] = time.time()
                return True
            try:
                sp = float(o.get('stopPrice', 0) or 0)
            except (TypeError, ValueError):
                continue
            if want_str and sp > 0 and self.price_to_str(symbol, sp) == want_str:
                trade['stop_state'] = 'verified'
                trade['stop_verified_at'] = time.time()
                if not trade.get('stop_order_id'):
                    trade['stop_order_id'] = o.get('orderId')
                return True
        # لم يُعثر على أمر الستوب على المنصة — المركز ليس محمياً بأمر حي الآن
        if strict or trade.get('stop_state') == 'verified':
            trade['stop_state'] = 'local'
            trade['stop_method'] = 'LOCAL_MONITORING'
            trade['stop_error'] = 'أمر الستوب غير موجود على المنصة — إعادة تثبيت مجدولة'
            trade['stop_retry_at'] = time.time() + 30
            return False
        return False   # نافذة سماح لحالة "مثبّت" الجديدة قبل التشديد

    async def verify_platform_stops(self):
        """فحص دوري أن ستوبات المراكز المفتوحة ما زالت حية — ومراكز الستوب
        المحلي تُعاد محاولة تثبيتها على المنصة كل 15 دقيقة."""
        if not self.binance_api_key or not self.active_trades:
            return
        now = time.time()
        for symbol, trade in list(self.active_trades.items()):
            try:
                if trade.get('stop_method') == 'LOCAL_MONITORING':
                    # إعادة محاولة تثبيت ستوب حقيقي على المنصة كل 15 دقيقة
                    if now > trade.get('stop_retry_at', 0):
                        await self._sync_stop_order(trade, None, force=True)
                    continue
                # التحقق المشدد: ستوب اختفى من المنصة → مراقبة محلية + إعادة تثبيت عاجلة
                await self._verify_stop_on_platform(trade, strict=True)
            except Exception as e:
                logger.warning(f"تعذر التحقق من ستوب {symbol}: {e}")

    async def _sync_stop_order(self, trade, current_price, force=False):
        """مزامنة ستوب المنصة مع SL المطلوب — لا تضع أمراً خلف السعر الحالي
        (المراقبة المحلية تغطي تلك الحالة فوراً)."""
        symbol = trade['symbol']
        is_buy = trade['side'] == 'BUY'
        desired = trade['sl']
        if desired is None or desired <= 0:
            return False
        if current_price and ((is_buy and desired >= current_price)
                              or (not is_buy and desired <= current_price)):
            return False
        # ⏳ حالة "مثبّت" عمرها أكثر من 90 ثانية دون تأكيد → تحقق مشدد الآن:
        # إن كان الأمر مفقوداً فعلاً تُخفض الحالة لمراقبة محلية وتُعاد محاولة التثبيت
        if (not force and trade.get('stop_state') == 'placed'
                and time.time() > float(trade.get('stop_placed_at', 0) or 0) + 90):
            await self._verify_stop_on_platform(trade, strict=True)
        desired_str = self.price_to_str(symbol, desired)
        if (not force and trade.get('stop_state') in ('verified', 'placed')
                and trade.get('stop_synced_price') is not None
                and self.price_to_str(symbol, trade['stop_synced_price']) == desired_str):
            return False
        if (not force and trade.get('stop_state') == 'local'
                and trade.get('stop_synced_price') is not None
                and self.price_to_str(symbol, trade['stop_synced_price']) == desired_str
                and time.time() < trade.get('stop_retry_at', 0)):
            return False

        old_id = trade.get('stop_order_id')
        placed = await self._place_stop_order(trade, desired)
        if placed:
            if old_id and old_id != trade.get('stop_order_id'):
                await self._cancel_conditional_order(symbol, old_id)
            logger.info(f"🛡️ ستوب {symbol} عند {desired_str} — "
                        f"الحالة: {trade.get('stop_state')} ({trade.get('stop_method', '')})")
            return True
        return False

    # ═══ استعلامات المنصة ═══
    async def get_position_amt(self, symbol):
        try:
            res = await self._fapi_request('GET', '/fapi/v2/positionRisk',
                {'symbol': symbol}, signed=True)
            if isinstance(res, list) and res:
                return float(res[0].get('positionAmt', 0))
        except Exception as e:
            logger.warning(f"فشل استعلام المركز لـ {symbol}: {e}")
        return None

    async def _get_position_info(self, symbol):
        """بيانات المركز الفعلية الكاملة (كمية/سعر/رافعة/هامش) — أساس حساب
        TP1 من التنفيذ الفعلي. يعيد None عند تعذر الجلب."""
        try:
            res = await self._fapi_request('GET', '/fapi/v2/positionRisk',
                {'symbol': symbol}, signed=True)
            if isinstance(res, list) and res:
                p = res[0]
                try:
                    amt = float(p.get('positionAmt', 0) or 0)
                except (TypeError, ValueError):
                    amt = 0.0
                try:
                    entry = float(p.get('entryPrice', 0) or 0)
                except (TypeError, ValueError):
                    entry = 0.0
                try:
                    lev = float(p.get('leverage', 0) or 0)
                except (TypeError, ValueError):
                    lev = 0.0
                try:
                    im = float(p.get('initialMargin', 0) or 0)
                except (TypeError, ValueError):
                    im = 0.0
                return {'amt': amt, 'entry': entry, 'leverage': lev, 'initial_margin': im}
        except Exception as e:
            logger.warning(f"فشل استعلام بيانات المركز لـ {symbol}: {e}")
        return None

    async def _income_sum(self, symbol, income_type, start_ms):
        """مجموع سجلات دخل نوع محدد منذ لحظة الدخول — None عند فشل الجلب."""
        res = await self._fapi_request('GET', '/fapi/v1/income',
            {'symbol': symbol, 'incomeType': income_type,
             'startTime': start_ms, 'limit': 1000}, signed=True)
        if not isinstance(res, list):
            return None
        total = 0.0
        for e in res:
            try:
                total += float(e.get('income', 0) or 0)
            except (TypeError, ValueError):
                continue
        return total, len(res)

    async def get_trade_realized_pnl(self, symbol, trade, expect_new_fill=False):
        """النتيجة الفعلية للصفقة من Binance:
        NET = Σ REALIZED_PNL + Σ COMMISSION + Σ FUNDING_FEE منذ لحظة الدخول
        (يشمل التنفيذ الجزئي وتعدد عمليات الإغلاق).
        يعيد {'gross','fees','funding','net','fills','complete':True} أو None
        عند تعذر جلب البيانات (لن تُختلق نتيجة مؤكدة في هذه الحالة)."""
        try:
            entry_time = float(trade.get('entry_time', 0) or 0)
        except (TypeError, ValueError):
            entry_time = 0.0
        if entry_time <= 0:
            return None
        start_ms = int((entry_time - 5) * 1000)
        attempts = 2 if expect_new_fill else 1
        for attempt in range(attempts):
            gross = await self._income_sum(symbol, 'REALIZED_PNL', start_ms)
            fees = await self._income_sum(symbol, 'COMMISSION', start_ms)
            funding = await self._income_sum(symbol, 'FUNDING_FEE', start_ms)
            if gross is None or fees is None or funding is None:
                return None   # بيانات غير مكتملة — الحالة تُسجل بوضوح كتقدير
            if gross[1] == 0 and expect_new_fill and attempt < attempts - 1:
                await asyncio.sleep(2.0)   # مهلة ظهور سجل التنفيذ الطازج
                continue
            return {'gross': gross[0], 'fees': fees[0], 'funding': funding[0],
                    'net': gross[0] + fees[0] + funding[0],
                    'fills': gross[1], 'complete': True}
        return None

    async def verify_positions(self):
        """مطابقة الحالة المحلية مع المراكز الفعلية لدى Binance:
        - صفقة محلية بلا مركز فعلي تُنهى بأرباحها الحقيقية (وليس تقديراً
          إلا عند تعذر جلب بيانات الدخل).
        - مركز فعلي بلا صفقة محلية (يتيم) يُتبنّى بحماية كاملة — مزامنة
          مستمرة لا عند الإقلاع فقط."""
        if not self.TRADE_ENABLED or not self.binance_api_key:
            return
        if self.active_trades:
            for symbol, trade in list(self.active_trades.items()):
                try:
                    amt = await self.get_position_amt(symbol)
                    if amt is None:
                        continue   # تعذر التحقق — لا إغلاق وهمي
                    step = self.step_sizes_cache.get(symbol) or 1.0
                    if abs(amt) < step:
                        pnl_info = await self.get_trade_realized_pnl(symbol, trade)
                        prices = self.get_price(symbol)
                        px = (prices['bid'] if trade['side'] == 'BUY' else prices['ask']) if prices else trade['entry_price']
                        await self._finalize_trade(trade, px, "🛑 أُغلق على المنصة (خارج مراقبة البوت)", pnl_info)
                except Exception as e:
                    self._notify_error(f"فشل التحقق من مركز {symbol}", exc=e)
        # 🔁 مزامنة المراكز اليتيمة: مركز حي على المنصة بلا صفقة محلية → تبنّي بحماية كاملة
        try:
            positions = await self._fapi_request('GET', '/fapi/v2/positionRisk', signed=True)
            if isinstance(positions, list):
                for p in positions:
                    try:
                        amt = float(p.get('positionAmt', 0) or 0)
                    except (TypeError, ValueError):
                        continue
                    if abs(amt) <= 0:
                        continue
                    symbol = p.get('symbol')
                    if not symbol or symbol in self.active_trades:
                        continue
                    if time.time() - self._recent_entry.get(symbol, 0) < 180:
                        continue   # دخول جديد قيد الاستقرار — لا تداخل
                    await self._adopt_orphan_position(symbol, p)
        except Exception as e:
            self._notify_error("فحص المراكز اليتيمة", exc=e)

    # ═══ إغلاق آمن بالكمية الفعلية (مع تحقق المنصة قبل تأكيد الإغلاق) ═══
    async def _close_position(self, trade, current_price):
        symbol = trade['symbol']
        # ⛔ قفل إغلاق لكل رمز: لا أمر إغلاق مكرر لو تداخل مراقب/لوحة/مسار آخر
        if symbol in self._closing:
            return False, None, None
        self._closing.add(symbol)
        try:
            return await self._close_position_locked(trade, current_price)
        finally:
            self._closing.discard(symbol)

    async def _close_position_locked(self, trade, current_price):
        symbol = trade['symbol']
        is_buy = trade['side'] == 'BUY'
        close_side = 'SELL' if is_buy else 'BUY'

        amt = await self.get_position_amt(symbol)
        if amt is None:
            self._notify_error(f"تعذر قراءة مركز {symbol}", context="إعادة المحاولة لاحقاً")
            return False, None, None
        step = self.step_sizes_cache.get(symbol) or 1.0
        if abs(amt) < step:
            pnl_info = await self.get_trade_realized_pnl(symbol, trade)
            return True, current_price, pnl_info

        qty = self.format_quantity(symbol, min(trade['quantity'], abs(amt)))
        if qty <= 0:
            return True, current_price, await self.get_trade_realized_pnl(symbol, trade)

        res = await self._fapi_request('POST', '/fapi/v1/order', {
            'symbol': symbol, 'side': close_side, 'type': 'MARKET',
            'quantity': self.qty_to_str(symbol, qty), 'reduceOnly': 'true'
        }, signed=True)

        if res and res.get('status') in ['FILLED', 'NEW']:
            fill = float(res.get('avgPrice') or 0)
            fill_price = fill if fill > 0 else current_price
            self._reset_error(f"إغلاق {symbol}")
            # ✅ لا يُسجّل الإغلاق ناجحاً قبل التحقق من المركز الفعلي
            amt2 = await self.get_position_amt(symbol)
            if amt2 is not None and abs(amt2) >= step:
                self._notify_error(f"بقايا مركز {symbol} بعد الإغلاق",
                                   context=f"المتبقي {abs(amt2)} — إعادة محاولة الدورة القادمة")
                return False, None, None
            # 💵 النتيجة الفعلية من Binance (يشمل رسوم أمر الإغلاق نفسه)
            pnl_info = await self.get_trade_realized_pnl(symbol, trade, expect_new_fill=True)
            return True, fill_price, pnl_info

        amt2 = await self.get_position_amt(symbol)
        if amt2 is not None and abs(amt2) < step:
            return True, current_price, await self.get_trade_realized_pnl(symbol, trade)

        self._notify_error(f"فشل إغلاق {symbol}",
                           context="ستُعاد المحاولة — ستوب المنصة/المحلي يحمي المركز")
        return False, None, None

    # ═══ إنهاء الصفقة (محاسبة كاملة بنتيجة فعلية موثقة) ═══
    async def _finalize_trade(self, trade, fill_price, reason, pnl_override=None):
        symbol = trade['symbol']
        # ⛔ حماية من الاحتساب المزدوج لنفس الصفقة (مراقب + لوحة + مصالحة)
        if trade.get('_finalizing'):
            return
        trade['_finalizing'] = True
        is_buy = trade['side'] == 'BUY'

        # إلغاء أي أوامر حماية متبقية بعد تأكيد الإغلاق
        for oid_key in ('stop_order_id', 'tp_order_id'):
            oid = trade.get(oid_key)
            if oid:
                await self._cancel_conditional_order(symbol, oid)

        # 💵 مصدر النتيجة:
        #  1) بيانات Binance الفعلية (صافي = محقق + رسوم + تمويل) → مؤكدة
        #  2) تعذر الجلب → تقدير نظري موسوم بوضوح، ولا يُقدّم أبداً كنتيجة مؤكدة
        pnl_info = pnl_override if isinstance(pnl_override, dict) else None
        if pnl_info and pnl_info.get('complete'):
            final_pnl = float(pnl_info.get('net', 0.0) or 0.0)
            pnl_source = 'binance'
        else:
            try:
                qty = float(trade.get('quantity', 0) or 0)
                entry = float(trade.get('entry_price', 0) or 0)
                fill = float(fill_price or 0)
            except (TypeError, ValueError):
                qty = entry = fill = 0.0
            if qty > 0 and entry > 0 and fill > 0:
                final_pnl = (fill - entry) * qty if is_buy else (entry - fill) * qty
            else:
                final_pnl = 0.0
            pnl_source = 'estimated'

        total_pnl = float(trade.get('realized_pnl', 0.0) or 0.0) + final_pnl
        margin_used = self.TRADE_SIZE_USDT
        margin_pnl_pct = (total_pnl / margin_used * 100) if margin_used > 0 else 0

        # 🛡️ تسجيل النتيجة في مدير المخاطر (يوقف التداول تلقائياً عند الحدود + حفظ الحالة)
        await self.risk.register_result(total_pnl)

        # النتيجة: 1 ربح | 0 خسارة | 2 محايدة (صفر/غير قابلة للتحقق لا تُحتسب خسارة)
        result_code = 1 if total_pnl > 0 else (0 if total_pnl < 0 else 2)
        if result_code == 1:
            self.stats['wins'] += 1
        elif result_code == 0:
            self.stats['losses'] += 1

        try:
            await self.db.set_signal_result(symbol, trade['entry_time'], result_code,
                                            total_pnl, pnl_source,
                                            strategy=trade.get('strategy') or HMA_STRATEGY_NAME)
        except Exception:
            pass

        await self.db.update_daily_pnl(
            total_pnl, True if result_code == 1 else (False if result_code == 0 else None))
        await self.db.remove_trade(symbol)
        self.active_trades.pop(symbol, None)
        self.set_cooldown(symbol)

        if pnl_source == 'binance':
            src_txt = (f"🧾 المصدر: نتيجة Binance الفعلية (صافي بعد الرسوم والتمويل)\n"
                       f"   إجمالي: `{pnl_info['gross']:.4f}` | رسوم: `{pnl_info['fees']:.4f}` | "
                       f"تمويل: `{pnl_info['funding']:.4f}` | عمليات تنفيذ: {pnl_info.get('fills', 0)}")
            src_short = 'مؤكدة ✓'
        else:
            src_txt = ("⚠️ المصدر: تقدير نظري (فرق السعر × الكمية) — بيانات التنفيذ الفعلية "
                       "غير متاحة ولن تُعرض كنتيجة مؤكدة")
            src_short = 'تقديرية ⚠️'
        icon = "✅" if result_code == 1 else ("❌" if result_code == 0 else "➖")
        strat_line = f"🧭 الاستراتيجية: {self._strategy_display(trade.get('strategy') or HMA_STRATEGY_NAME)}\n"
        msg = (f"🏁 {icon} *إغلاق `{symbol}`*\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
               f"{reason}\n"
               f"{strat_line}"
               f"💵 النتيجة ({src_short}): `{total_pnl:.4f} USDT` ({margin_pnl_pct:.1f}% من الهامش)\n"
               f"{src_txt}\n"
               f"🏆 الإجمالي: {self.stats['wins']}W / {self.stats['losses']}L")
        await self.tg(msg)

    # ═══ مراقبة الصفقات: SL ← ستوب زمني ← TP1 بإغلاق كامل ═══
    async def monitor_trades(self):
        if not self.active_trades:
            return
        stale_symbols = []
        for symbol, trade in list(self.active_trades.items()):
            prices = self.get_price(symbol)
            if not prices:
                now = time.time()
                if now - self._rest_price_ts.get(symbol, 0) >= 10:
                    self._rest_price_ts[symbol] = now
                    prices = await self._refresh_price_rest(symbol)
            if not prices:
                stale_symbols.append(symbol)
                continue

            is_buy = trade['side'] == 'BUY'
            current_price = prices['bid'] if is_buy else prices['ask']
            changed = False

            if is_buy and current_price > trade.get('highest_price', 0):
                trade['highest_price'] = current_price
                changed = True
            elif not is_buy and current_price < trade.get('lowest_price', 999999):
                trade['lowest_price'] = current_price
                changed = True

            # 1) 🛡️ وقف الخسارة — حماية محلية فورية تعمل دائماً سواء كان
            #      ستوب المنصة مثبتاً أم في وضع المراقبة المحلية
            if (is_buy and current_price <= trade['sl']) or (not is_buy and current_price >= trade['sl']):
                closed, fill_price, pnl_override = await self._close_position(trade, current_price)
                if closed:
                    await self._finalize_trade(trade, fill_price, "🛑 ضرب SL (حماية مؤكدة)", pnl_override)
                continue

            # 2) ⏰ الستوب الزمني — لا صفقة عالقة
            max_h = self.MAX_TRADE_HOURS
            if max_h and max_h > 0 and time.time() - trade.get('entry_time', 0) >= max_h * 3600:
                closed, fill_price, pnl_override = await self._close_position(trade, current_price)
                if closed:
                    await self._finalize_trade(trade, fill_price,
                        f"⏰ ستوب زمني ({max_h:g} ساعة بلا انطلاق)", pnl_override)
                continue

            # 3) 🎯 TP1 — إغلاق 100% من الكمية المتبقية فوراً (لا TP2 ولا تقسيم)
            tp = trade.get('tp')
            if tp and ((is_buy and current_price >= tp) or (not is_buy and current_price <= tp)):
                closed, fill_price, pnl_override = await self._close_position(trade, current_price)
                if closed:
                    await self._finalize_trade(trade, fill_price,
                        "🎯 TP1 — إغلاق كامل للمركز (هدف عائد الهامش)", pnl_override)
                else:
                    self._notify_error(f"تعذر إغلاق TP1 لـ {symbol}",
                                       context="إعادة المحاولة في الدورة القادمة — الوقف يحمي المركز")
                continue

            # 4) مزامنة ستوب المنصة مع الحالة الحالية (رخيصة إن لم يتغير شيء)
            try:
                await self._sync_stop_order(trade, current_price)
            except Exception as e:
                logger.warning(f"تعذر مزامنة ستوب {symbol}: {e}")

            if changed:
                await self.db.save_trade(trade)

        if stale_symbols:
            # ⚠️ بدون أسعار لا تعمل المراقبة المحلية — نُنبه بوضوح إن كان ستوب
            # المركز غير مؤكد على المنصة (المركز غير محمي بأمر حي الآن)
            unprot = [s for s in stale_symbols
                      if (self.active_trades.get(s, {}).get('stop_state') != 'verified')]
            ctx = ', '.join(stale_symbols)
            if unprot:
                ctx += f" | ⚠️ ستوب غير مؤكد على المنصة: {', '.join(unprot)}"
            self._notify_error("أسعار مجمّدة لمراكز مفتوحة", context=ctx)

    # ═══ تبنّي مركز يتيم من بياناته الفعلية (يُستخدم في المصالحة والفحص الدوري) ═══
    async def _adopt_orphan_position(self, symbol, pos_row):
        """تبنّي مركز موجود على المنصة بلا صفقة محلية: وقف خسارة + TP1 محسوب
        من بيانات المركز الفعلية (الكمية/السعر/الرافعة من المنصة نفسها)."""
        try:
            amt = float(pos_row.get('positionAmt', 0) or 0)
        except (TypeError, ValueError):
            amt = 0.0
        if abs(amt) <= 0:
            return False
        side = 'BUY' if amt > 0 else 'SELL'
        try:
            entry = float(pos_row.get('entryPrice', 0) or 0)
        except (TypeError, ValueError):
            entry = 0.0
        if not entry or entry <= 0:
            prices = self.get_price(symbol) or await self._refresh_price_rest(symbol)
            entry = (prices['bid'] if side == 'BUY' else prices['ask']) if prices else 0.0
        if not entry or entry <= 0:
            await self.tg(f"⚠️ *تعذّر تبنّي مركز يتيم* (`{symbol}`)\n"
                          "سعر الدخول غير متاح بعد — سيُعاد في فحص قادم")
            return False
        try:
            lev = float(pos_row.get('leverage', 0) or 0)
        except (TypeError, ValueError):
            lev = 0.0
        lev = lev if lev > 0 else float(self.LEVERAGE)
        qty = abs(amt)
        df = await self.get_klines(symbol, '15m', 50)
        atr = self._compute_atr(df) if df is not None else None
        if not atr or atr <= 0 or math.isnan(atr):
            atr = entry * 0.01
        tp1_dist = self._tp1_distance_from_actual(entry, qty, lev)
        if tp1_dist <= 0:
            tp1_dist = 1.5 * atr
        if side == 'BUY':
            sl = entry - 2 * atr
            tp1 = self._round_tp_price(symbol, entry + tp1_dist, side)
        else:
            sl = entry + 2 * atr
            tp1 = self._round_tp_price(symbol, entry - tp1_dist, side)
        trade = {
            'symbol': symbol, 'side': side, 'entry_price': entry,
            'quantity': qty, 'sl': sl, 'tp': tp1,
            'score': None,
            'strategy': 'UNKNOWN',   # مصدر المركز غير معروف — يُعرض كما هو بلا ادعاء
            'trailing_active': False, 'highest_price': entry, 'lowest_price': entry,
            'entry_time': time.time(), 'realized_pnl': 0.0,
            'stop_order_id': None, 'tp_order_id': None,
            'stop_state': 'none', 'stop_error': None,
            'stop_synced_price': None,
        }
        self.active_trades[symbol] = trade
        await self.db.save_trade(trade)
        await self._sync_stop_order(trade, entry)
        await self.db.save_trade(trade)
        await self.tg(f"🔄 *تم تبنّي مركز يتيم* (`{symbol}`)\n"
                      f"وقف عند {self.fmt_price(sl)} + TP1 عند {self.fmt_price(tp1)}")
        return True

    # ═══ المصالحة الذاتية عند الإقلاع ═══
    async def reconcile(self):
        if not self.binance_api_key or not self.TRADE_ENABLED:
            return
        try:
            positions = await self._fapi_request('GET', '/fapi/v2/positionRisk', signed=True)
            if not isinstance(positions, list):
                # ⛔ تعذر جلب المراكز الفعلية — لا تُنهى أي صفقة محلية دون تحقق
                # (منع إغلاق وهمي عند انقطاع الشبكة وقت الإقلاع)
                self._notify_error("تعذر جلب المراكز الفعلية للمصالحة",
                                   context="لن تُنهى أي صفقة دون تحقق — تُعاد المحاولة")
                return
            open_pos = {}
            for p in positions:
                try:
                    amt = float(p.get('positionAmt', 0) or 0)
                except (TypeError, ValueError):
                    continue
                if abs(amt) > 0:
                    open_pos[p['symbol']] = p   # الصف الكامل (يشمل الرافعة والهامش)

            # صفقات محلية انتهت أثناء التوقف — بنتيجتها الفعلية من Binance
            for symbol, trade in list(self.active_trades.items()):
                pos = open_pos.get(symbol)
                step = self.step_sizes_cache.get(symbol) or 1.0
                if not pos or abs(float(pos.get('positionAmt', 0) or 0)) < step:
                    pnl_info = await self.get_trade_realized_pnl(symbol, trade)
                    await self._finalize_trade(trade, trade['entry_price'],
                                               "🔄 أُغلق أثناء توقف البوت", pnl_info)

            # مراكز يتيمة → تُتبنّى بحماية كاملة (ستوب + TP1 بهدف الهامش الفعلي)
            for symbol, pos in open_pos.items():
                if symbol in self.active_trades:
                    continue
                await self._adopt_orphan_position(symbol, pos)

            # أوامر الحماية على المنصة: تبنّي الستوبات الحية + إلغاء الأوامر اليتيمة
            orders = await self._fapi_request('GET', '/fapi/v1/openOrders', signed=True)
            if not isinstance(orders, list):
                orders = []
            adopted = cancelled = 0
            for o in orders:
                otype = o.get('type')
                if otype not in ('STOP_MARKET', 'STOP', 'TAKE_PROFIT_MARKET'):
                    continue
                trade = self.active_trades.get(o.get('symbol'))
                if trade is not None:
                    if otype in ('STOP_MARKET', 'STOP'):
                        if not trade.get('stop_order_id'):
                            trade['stop_order_id'] = o.get('orderId')
                            try:
                                sp = float(o.get('stopPrice', 0) or 0)
                            except (TypeError, ValueError):
                                sp = 0.0
                            if sp > 0:
                                trade['stop_synced_price'] = sp
                            if trade.get('stop_state') not in ('verified', 'local'):
                                trade['stop_state'] = 'placed'
                            adopted += 1
                        continue
                    # لا نستخدم أوامر TP على المنصة — إلغاؤها يضمن خروجاً متسقاً
                    # عبر TP1 المحلي المعتمد على هدف الهامش
                    cancelled += 1
                    await self._fapi_request('DELETE', '/fapi/v1/order',
                        {'symbol': o['symbol'], 'orderId': o.get('orderId')}, signed=True,
                        quiet=('-2011', '-2013'))
                    continue
                cancelled += 1
                await self._fapi_request('DELETE', '/fapi/v1/order',
                    {'symbol': o['symbol'], 'orderId': o.get('orderId')}, signed=True,
                    quiet=('-2011', '-2013'))
            if adopted:
                await self.tg(f"🛡️ *مصالحة:* تم تبنّي {adopted} أمر ستوب حي على المنصة")
            if cancelled:
                await self.tg(f"🧹 *تنظيف ذاتي:* أُلغي {cancelled} أمر يتيم على المنصة")
            logger.info(f"🧾 المصالحة الذاتية: {len(open_pos)} مركز حي، {adopted} ستوب مُتبنى، {cancelled} أمر يتيم ملغى")
        except Exception as e:
            self._notify_error("فشل المصالحة الذاتية", exc=e, context="غير قاتل — تُعاد كل دورة")

    # ═══ إيقاف آمن ═══
    async def request_shutdown(self):
        if self._shutdown_requested:
            return
        self._shutdown_requested = True
        logger.info("🛑 طلب إيقاف آمن...")
        try:
            await self.tg("🛑 *إيقاف آمن:* ستوب المنصة/المحلي يحمي المراكز حتى العودة.")
        except Exception:
            pass

    # ═══ الصيانة الذاتية ═══
    def _cleanup_memory(self):
        now = time.time()
        self.reentry_cooldown = {k: v for k, v in self.reentry_cooldown.items() if v > now}
        self.last_discovery_alert = {k: v for k, v in self.last_discovery_alert.items()
                                     if v > now - 7200}
        self._last_reject_log = {k: v for k, v in self._last_reject_log.items()
                                 if v > now - 3600}
        if len(self.error_counts) > 500:
            self.error_counts.clear()
        self._prune_hma_done()

    def _trades_today(self):
        today = time.strftime("%Y-%m-%d")
        return sum(1 for _, d in self.entry_history if d == today)

    async def _send_daily_report(self, day):
        row = await self.db.get_day_stats(day)
        if not row:
            return
        pnl, w, l = row
        wr = (w / (w + l) * 100) if (w + l) > 0 else 0
        await self.tg(f"📊 *تقرير {day}*\n💰 PnL: `{pnl:.4f} USDT`\n"
                      f"🏆 {w}W / {l}L (فوز {wr:.0f}%)")

    async def _heartbeat_and_report(self, loop_count):
        now = time.time()
        today = time.strftime("%Y-%m-%d")
        if today != self._report_day:
            await self._send_daily_report(self._report_day)
            self._report_day = today
        if now - self._last_heartbeat >= 3600:
            self._last_heartbeat = now
            can, risk_reason = self.risk.can_trade()
            await self.tg(f"💓 *النبض:* حي ✓ | مسح #{loop_count} | "
                          f"صفقات اليوم: {self._trades_today()} | مفتوحة: {len(self.active_trades)}\n"
                          f"🛡️ المخاطر: {risk_reason}\n🧭 {self.hma.describe()}")

    # ═══ صيانة تقويم الأخبار ═══
    async def _news_boot(self):
        try:
            await self.news_filter.refresh_calendar()
            ev = self.news_filter.next_event()
            if self.news_filter.enabled and ev:
                await self.tg(f"📰 *فلتر الأخبار نشط* — الحدث القادم: {ev['title']} "
                              f"({ev['cur']}) بعد {max(0, int((ev['ts'] - time.time()) / 60))} دقيقة")
        except Exception:
            pass

    async def _maybe_refresh_news(self):
        if time.time() - self.news_filter.calendar_updated > self.news_filter.CALENDAR_TTL:
            try:
                await self.news_filter.refresh_calendar()
            except Exception:
                pass

    # ═══ 🕹️ أوامر المالك من اللوحة (نفس دلالات اللوحة القديمة) ═══
    async def panel_command(self, action, symbol=None, data=None):
        action = str(action or '').strip()
        symbol = str(symbol or '').strip().upper() if symbol else None
        if action == 'pause':
            if not self.TRADE_ENABLED:
                return 'التوقف مفعّل أصلاً — لا صفقات جديدة'
            self.TRADE_ENABLED = False
            try:
                await self.db.set_param('trade_enabled', '0')
            except Exception:
                pass
            await self.tg("⏸️ *إيقاف طوارئ من اللوحة* — لن تُفتح أي صفقة جديدة\n"
                          "إدارة الصفقات المفتوحة والمخارج تستمر طبيعياً")
            return 'تم إيقاف فتح الصفقات الجديدة (المخارج تعمل طبيعياً)'
        if action == 'resume':
            if self.TRADE_ENABLED:
                return 'التداول يعمل أصلاً'
            if not self.binance_api_key:
                return 'لا يمكن الاستئناف: مفاتيح API غير مضبوطة على الخادم'
            self.TRADE_ENABLED = True
            try:
                await self.db.set_param('trade_enabled', '1')
            except Exception:
                pass
            await self.tg("▶️ *استئناف التداول من اللوحة* — الصفقات الجديدة وفق إشارات HMA")
            return 'تم استئناف التداول'
        if action == 'close_one':
            t = self.active_trades.get(symbol or '')
            if not t:
                return f'لا توجد صفقة مفتوحة على {symbol or "—"}'
            prices = self.get_price(t['symbol']) or await self._refresh_price_rest(t['symbol'])
            px = (prices['bid'] if t['side'] == 'BUY' else prices['ask']) \
                if prices else t['entry_price']
            closed, fill, pnl_over = await self._close_position(t, px)
            if closed:
                await self._finalize_trade(t, fill, '🛑 إغلاق طارئ من اللوحة', pnl_over)
                return f'أُغلقت صفقة {t["symbol"]} بسعر السوق'
            return f'تعذر إغلاق {t["symbol"]} — أعد الأمر بعد قليل'
        if action == 'close_all':
            syms = list(self.active_trades.keys())
            if not syms:
                return 'لا توجد صفقات مفتوحة'
            closed_n = 0
            for s in syms:
                t = self.active_trades.get(s)
                if not t:
                    continue
                prices = self.get_price(s) or await self._refresh_price_rest(s)
                px = (prices['bid'] if t['side'] == 'BUY' else prices['ask']) \
                    if prices else t['entry_price']
                closed, fill, pnl_over = await self._close_position(t, px)
                if closed:
                    closed_n += 1
                    await self._finalize_trade(t, fill, '🛑 إغلاق طارئ من اللوحة (الجميع)',
                                               pnl_over)
            return f'أُغلقت {closed_n}/{len(syms)} صفقة بسعر السوق'
        if action == 'reset_all':
            try:
                async with aiosqlite.connect(self.db.db_name) as db:
                    await db.execute('DELETE FROM scan_rejections')
                    await db.execute('DELETE FROM signal_log')
                    await db.execute('DELETE FROM daily_stats')
                    await db.commit()
            except Exception as e:
                return f'تعذر مسح سجلات القاعدة: {e}'
            for k in list(self.error_counts.keys()):
                self.error_counts.pop(k, None)
            for k in ('total_signals', 'signals_found', 'rejected_by_risk',
                      'rejected_by_news', 'rejected_open_trade', 'rejected_quality',
                      'rejected_execution'):
                self.stats[k] = 0
            ACTION.clear()
            await self.tg('🧹 *إعادة ضبط شاملة من اللوحة* — سُحبت السجلات والإحصاءات '
                          '(الصفقات المفتوحة لم تُمس)')
            return 'تمت إعادة الضبط الشاملة — الصفقات المفتوحة كما هي'
        if action == 'scan_now':
            if self._scan_now_evt is not None:
                self._scan_now_evt.set()
                return 'تم إيقاظ حلقة المسح — الدورة تُنفَّذ فوراً'
            return 'الحلقة الرئيسية غير جاهزة بعد'
        if action == 'stop_retry':
            t = self.active_trades.get(symbol or '')
            if not t:
                return f'لا توجد صفقة مفتوحة على {symbol or "—"}'
            t['stop_state'] = 'none'
            t['stop_order_id'] = None
            try:
                await self.db.save_trade(t)
            except Exception:
                pass
            return (f'أُعيد ضبط حالة ستوب المنصة لـ {t["symbol"]} — '
                    'ستُعاد محاولة التثبيت في الدورة القادمة')
        if action == 'hma_settings':
            d = data if isinstance(data, dict) else {}
            if not d:
                return 'لا حقول إعدادات في الأمر — أعد من اللوحة'
            changed = self.hma.update(d)
            await self.hma.save()
            if changed:
                await self.tg('🧭 *تحديث إعدادات HMA من اللوحة:*\n'
                              + '\n'.join('• ' + c for c in changed))
                return (f'✅ حُفظت {len(changed)} تعديلات — تعمل لحظياً:'
                        + '\n' + '\n'.join(changed))
            return 'لا فروقات — القيم المدخلة مطابقة للفعالة أصلاً'
        if action == 'news_toggle':
            self.news_filter.enabled = not self.news_filter.enabled
            try:
                await self.news_filter.save()
            except Exception:
                pass
            ns = self.news_filter.status()
            state_txt = '📰 فلتر الأخبار مفعّل الآن' if ns['enabled'] \
                else '📰 فلتر الأخبار معطّل الآن — كل الإشارات تمر'
            return state_txt + (f" — {ns.get('reason')}" if ns.get('reason') else '')
        if action == 'news_refresh':
            try:
                await self.news_filter.refresh_calendar()
                ns = self.news_filter.status()
                info = f"أحداث في التقويم: {ns.get('events_count', 0)}"
                if ns.get('next_event'):
                    info += (f" | القادم: {ns['next_event']['title']} "
                             f"بعد {ns['next_event']['in_min']} دقيقة")
                return '🔄 تحديث التقويم تم — ' + info
            except Exception as e:
                return f'تعذر تحديث التقويم: {e}'
        return f'أمر غير معروف: {action}'

    # ═══ 📊 مزامنة لقطة اللوحة — كتابة فقط بلا شبكة ═══
    def _action_sync(self, loop_count):
        try:
            can, risk_reason = self.risk.can_trade()
            blocked_now = self._hma_evening_blocked_now()
            positions = []
            for sym, t in list(self.active_trades.items()):
                p = self.live_prices.get(sym) or {}
                try:
                    entry = float(t.get('entry_price') or 0)
                    cur = float(p.get('bid') if t['side'] == 'BUY' else p.get('ask')) \
                        if p.get('bid') and p.get('ask') else entry
                    qty = float(t.get('quantity') or 0)
                    pnl = (cur - entry) * qty if t['side'] == 'BUY' \
                        else (entry - cur) * qty
                    margin = qty * entry / max(float(self.LEVERAGE), 1.0)
                    pct = (pnl / margin * 100.0) if margin > 0 else 0.0
                except Exception:
                    entry = cur = pnl = margin = pct = 0.0
                age_h = max(0.0, (time.time() - float(t.get('entry_time') or time.time()))
                            / 3600.0)
                positions.append({
                    'symbol': sym, 'side': t.get('side'),
                    'entry': self.fmt_price(entry), 'current': self.fmt_price(cur),
                    'margin': round(margin, 2), 'pnl': round(pnl, 2),
                    'pnl_pct': round(pct, 1),
                    'sl': self.fmt_price(float(t.get('sl') or 0)),
                    'tp': self.fmt_price(float(t.get('tp') or 0)),
                    'age_h': round(age_h, 1),
                    'stop_state': t.get('stop_state') or 'none',
                    'score': t.get('score'),
                })
            newest_price_ts = max((p.get('ts', 0) for p in self.live_prices.values()),
                                  default=0)
            trades_live = list(self.active_trades.values())
            stop_health = {'total': len(trades_live),
                           'verified': sum(1 for t in trades_live
                                           if t.get('stop_state') == 'verified'),
                           'placed': sum(1 for t in trades_live
                                         if t.get('stop_state') == 'placed'),
                           'local': sum(1 for t in trades_live
                                        if t.get('stop_state') == 'local'),
                           'failed': [{'symbol': t.get('symbol'),
                                       'error': t.get('stop_error')}
                                      for t in trades_live
                                      if t.get('stop_state') == 'local']}
            ls = dict(self.last_hma_scan_info or {})
            # 📊 عدّاد آلة الحالات لكل الرموز (BULL/BEAR/NEUTRAL) — كما في اللوحة القديمة
            ms_counts = {'BULL': 0, 'BEAR': 0, 'NEUTRAL': 0}
            for _v in (getattr(self, 'hma_states', {}) or {}).values():
                _s = _v.get('state') if isinstance(_v, dict) else None
                if _s in ms_counts:
                    ms_counts[_s] += 1
            st = {
                'status': 'يتوقف' if self._shutdown_requested else 'يعمل',
                'mode': (('⚔️ تداول فعلي' + (' (TESTNET 🧪)' if self.TESTNET else ''))
                         if self.TRADE_ENABLED else '👁️ مراقبة فقط'),
                'hma_timeframe': self.hma.timeframe,
                'testnet': bool(self.TESTNET),
                'uptime_h': round((time.time() - self._boot_ts) / 3600.0, 1),
                'evening_block': bool(HMA_BLOCK_EVENING_UTC),
                'evening_blocked_now': bool(blocked_now),
                'evening_window': (f'{HMA_EVENING_START_UTC:02d}:00 ← '
                                   f'{HMA_EVENING_END_UTC:02d}:59 UTC'),
                'risk_ok': bool(can), 'risk_reason': risk_reason,
                'hma_enabled': bool(self.hma_enabled),
                'hma_live': bool(self.HMA_LIVE),
                'max_open_trades': int(self.MAX_OPEN_TRADES),
                'trade_enabled': bool(self.TRADE_ENABLED),
                'last_hma_scan': {'scanned': int(ls.get('scanned', 0) or 0),
                                  'signals': int(ls.get('signals', 0) or 0),
                                  'exits': int(ls.get('exits', 0) or 0)},
                'universe_count': len(self._universe_cache),
                'hma_universe_size': int(getattr(self.hma, 'universe_size', 0) or 0),
                'hma_pool': int(HMA_UNIVERSE_POOL or 0),
                'hma_min_vol_musd': round(float(HMA_SCAN_MIN_VOL_USDT or 0) / 1e6, 1),
                'time_stop_h': float(getattr(self, 'MAX_TRADE_HOURS', 24) or 24),
                'balance': float(self._balance_cache[0] or 0),
                'daily_pnl': float(self.risk.daily_pnl or 0),
                'trades_today': self._trades_today(),
                'wins': int(self.stats.get('wins', 0)),
                'losses': int(self.stats.get('losses', 0)),
                'open_count': len(self.active_trades),
                'cycles': int(loop_count),
                'trades_executed': int(self.stats.get('trades_executed', 0)),
                'describe': self.hma.describe(),
                'hma_market_states': dict(ms_counts),
                'positions': positions,
                # ─── V12.3: كل بيانات اللوحة القديمة صارت في الحالة ───
                'stats': dict(self.stats),
                'leverage': int(self.LEVERAGE),
                'trade_size': float(self.TRADE_SIZE_USDT),
                'pairs_total': len(self.all_futures_pairs),
                'price_age': (int(time.time() - newest_price_ts)
                              if newest_price_ts else 999999),
                'stop_health': stop_health,
                'risk': {'can_trade': bool(can), 'reason': risk_reason,
                         'consecutive_losses': getattr(self.risk, 'consecutive_losses', 0),
                         'daily_losses': getattr(self.risk, 'daily_losses', 0),
                         'daily_pnl': float(getattr(self.risk, 'daily_pnl', 0.0) or 0.0),
                         'initial_balance': float(getattr(self.risk, 'initial_balance',
                                                          0.0) or 0.0)},
                'news': self.news_filter.status(),
                'universe_diag': dict(getattr(self, '_universe_diag', {}) or {}),
                'hma_settings': self.hma.status(),
                'env_conflicts': list(getattr(self.hma, 'env_conflicts', []) or []),
            }
            DASH_STATE.clear()
            DASH_STATE.update(st)
        except Exception:
            pass

    # ═══ 🗄️ لقطة بيانات القاعدة للوحة — مغلقة/إشارات/رفض/أيام (V12.3) ═══
    async def _dash_db_snapshot(self):
        """يجلب من القاعدة نفسها ما كانت تجلبه اللوحة القديمة من نهاياتها:
        آخر المغلقات (مؤكد/تقديري)، سجل الإشارات بمكوناتها، أسباب الرفض
        (مؤخر + عدّاد 24س)، والأداء اليومي (14 يوماً + إجماليات التاريخ)
        — وتوضع في DASH_STATE للعرض فوراً. خنق 8 ثوانٍ من الحلقة."""
        try:
            trade_size = float(self.TRADE_SIZE_USDT or 1.0)
            async with aiosqlite.connect(self.db.db_name) as db:
                db.row_factory = aiosqlite.Row
                closed = []
                try:
                    async with db.execute(
                            "SELECT symbol, direction, entry_ts, score, result, pnl, pnl_source "
                            "FROM signal_log WHERE result >= 0 ORDER BY id DESC LIMIT 50") as cur:
                        c_rows = await cur.fetchall()
                except Exception:
                    c_rows = []
                for r in c_rows:
                    pnl = r['pnl'] or 0.0
                    closed.append({
                        'symbol': r['symbol'], 'direction': r['direction'],
                        'time': libya_time_str(r['entry_ts'] or time.time()),
                        'pnl': round(pnl, 4),
                        'pnl_pct': round(pnl / trade_size * 100.0, 1) if trade_size else 0.0,
                        'score': int(r['score'] or 0),
                        'pnl_source': r['pnl_source'],
                    })
                signals = []
                try:
                    async with db.execute(
                            "SELECT symbol, direction, entry_ts, score, components, result, pnl "
                            "FROM signal_log ORDER BY id DESC LIMIT 50") as cur:
                        s_rows = await cur.fetchall()
                except Exception:
                    s_rows = []
                for r in s_rows:
                    comp = {}
                    try:
                        comp = json.loads(r['components'] or '{}')
                    except Exception:
                        pass
                    signals.append({
                        'symbol': r['symbol'], 'direction': r['direction'],
                        'time': libya_time_str(r['entry_ts']),
                        'score': int(r['score'] or 0),
                        'trigger': comp.get('trigger') or comp.get('zone') or '—',
                        'power': comp.get('power'),
                        'rr': comp.get('rr'),
                        'result': r['result'],
                        'pnl': (round(r['pnl'], 4) if r['pnl'] is not None else None),
                    })
                recent, counts = [], []
                try:
                    async with db.execute(
                            "SELECT ts, symbol, reason FROM scan_rejections "
                            "ORDER BY id DESC LIMIT 40") as cur:
                        rows = await cur.fetchall()
                    recent = [{'time': libya_time_str(r['ts']),
                               'symbol': r['symbol'], 'reason': r['reason']}
                              for r in rows]
                    async with db.execute(
                            "SELECT reason, COUNT(*) c FROM scan_rejections "
                            "WHERE ts > ? GROUP BY reason ORDER BY c DESC LIMIT 12",
                            (time.time() - 86400,)) as cur:
                        counts = [[r['reason'], r['c']] for r in await cur.fetchall()]
                except Exception:
                    pass
                days = []
                try:
                    async with db.execute(
                            "SELECT date, realized_pnl, wins, losses FROM daily_stats "
                            "ORDER BY date DESC LIMIT 14") as cur:
                        d_rows = await cur.fetchall()
                    for r in d_rows:
                        w = r['wins'] or 0
                        l = r['losses'] or 0
                        total = w + l
                        days.append({'date': r['date'],
                                     'pnl': round(r['realized_pnl'] or 0, 4),
                                     'wins': w, 'losses': l, 'total': total,
                                     'winrate': (round(w / total * 100.0, 1)
                                                 if total else None)})
                except Exception:
                    pass
                agg = {'active_days': len(days), 'total_closed': 0, 'total_wins': 0,
                       'total_pnl': 0.0, 'overall_winrate': None,
                       'best_day': None, 'worst_day': None}
                try:
                    async with db.execute(
                            "SELECT COUNT(*) c, SUM(result = 1) w, COALESCE(SUM(pnl),0) p "
                            "FROM signal_log WHERE result >= 0") as cur:
                        a = await cur.fetchone()
                        if a and a['c']:
                            agg['total_closed'] = a['c']
                            agg['total_wins'] = a['w'] or 0
                            agg['total_pnl'] = round(a['p'] or 0.0, 4)
                            agg['overall_winrate'] = round((a['w'] or 0) / a['c'] * 100.0, 1)
                    async with db.execute(
                            "SELECT date, realized_pnl FROM daily_stats "
                            "WHERE wins + losses > 0 ORDER BY realized_pnl DESC LIMIT 1") as cur:
                        b_row = await cur.fetchone()
                    async with db.execute(
                            "SELECT date, realized_pnl FROM daily_stats "
                            "WHERE wins + losses > 0 ORDER BY realized_pnl ASC LIMIT 1") as cur:
                        w_row = await cur.fetchone()
                    if b_row:
                        agg['best_day'] = {'date': b_row['date'],
                                           'pnl': round(b_row['realized_pnl'] or 0, 4)}
                    if w_row:
                        agg['worst_day'] = {'date': w_row['date'],
                                            'pnl': round(w_row['realized_pnl'] or 0, 4)}
                except Exception:
                    pass
                today = time.strftime('%Y-%m-%d')
                tday = next((d for d in days if d['date'] == today), None)
                if not tday:
                    tday = {'date': today, 'pnl': 0, 'wins': 0, 'losses': 0,
                            'total': 0, 'winrate': None}
                # 🧭 أداء الاستراتيجية عبر التاريخ — من القاعدة فعلياً
                # (نفس تعريفات اللوحة القديمة الموثقة — بلا أرقام مضللة)
                perf = {'signals': 0, 'executed': 0, 'wins': 0, 'losses': 0,
                        'winrate': None, 'net_pnl': 0.0, 'avg_win': None,
                        'avg_loss': None, 'profit_factor': None,
                        'max_drawdown': None, 'by_symbol': None,
                        'last_signal': '—'}
                try:
                    async with db.execute(
                            "SELECT COUNT(*) c FROM signal_log") as cur:
                        perf['signals'] = (await cur.fetchone())[0] or 0
                    async with db.execute(
                            "SELECT symbol, result, pnl FROM signal_log "
                            "WHERE result >= 0 ORDER BY id DESC LIMIT 2000") as cur:
                        cl_rows = list(reversed(await cur.fetchall()))
                    perf['executed'] = len(cl_rows)
                    win_pnls = [float(r['pnl'] or 0) for r in cl_rows
                                if r['result'] == 1]
                    loss_pnls = [float(r['pnl'] or 0) for r in cl_rows
                                 if r['result'] == 0]
                    perf['wins'] = len(win_pnls)
                    perf['losses'] = len(loss_pnls)
                    if win_pnls or loss_pnls:
                        perf['winrate'] = round(
                            len(win_pnls) / (len(win_pnls) + len(loss_pnls)) * 100.0, 1)
                    perf['net_pnl'] = round(sum(float(r['pnl'] or 0)
                                                for r in cl_rows), 4)
                    if win_pnls:
                        perf['avg_win'] = round(sum(win_pnls) / len(win_pnls), 4)
                    if loss_pnls:
                        perf['avg_loss'] = round(sum(loss_pnls) / len(loss_pnls), 4)
                    if win_pnls and loss_pnls and sum(loss_pnls) != 0:
                        perf['profit_factor'] = round(
                            sum(win_pnls) / abs(sum(loss_pnls)), 2)
                    if len(cl_rows) >= 2:      # أقصى تراجع — الترتيب الزمني للمغلقات
                        eq = peak = dd = 0.0
                        for r in cl_rows:
                            eq += float(r['pnl'] or 0)
                            peak = max(peak, eq)
                            dd = max(dd, peak - eq)
                        perf['max_drawdown'] = round(dd, 4)
                    by_sym = {}
                    for r in cl_rows:
                        by_sym[r['symbol']] = (by_sym.get(r['symbol'], 0.0)
                                               + float(r['pnl'] or 0))
                    top_syms = sorted(by_sym.items(),
                                      key=lambda x: -abs(x[1]))[:3]
                    if top_syms:
                        perf['by_symbol'] = '، '.join(
                            f"{s_} ({v_:+.2f}$)" for s_, v_ in top_syms)
                    async with db.execute(
                            "SELECT symbol, direction, entry_ts, components "
                            "FROM signal_log ORDER BY id DESC LIMIT 1") as cur:
                        lr = await cur.fetchone()
                    if lr:
                        trig = ''
                        try:
                            _comp = json.loads(lr['components'] or '{}')
                            trig = _comp.get('trigger') or _comp.get('zone') or ''
                        except Exception:
                            pass
                        perf['last_signal'] = (
                            f"{lr['symbol']} {lr['direction']} "
                            + libya_time_str(lr['entry_ts'])
                            + (f" — {str(trig)[:42]}" if trig else ''))
                except Exception:
                    pass
                DASH_STATE['closed'] = closed
                DASH_STATE['signals'] = signals
                DASH_STATE['rejections'] = {'recent': recent, 'counts': counts}
                DASH_STATE['daily'] = {'today': tday, 'days': days,
                                       'aggregates': agg,
                                       'trades_today_live': self._trades_today()}
                DASH_STATE['errors'] = dict(self.error_counts)
                DASH_STATE['strat_perf'] = perf
        except Exception:
            pass

    def _start_dashboard(self):
        """تشغيل خادم اللوحة المدمجة — فشله لا يوقف البوت أبداً."""
        try:
            if os.environ.get('DASHBOARD_ENABLED', 'true').lower() == 'false':
                logger.info('🖥️ لوحة المراقبة معطلة (DASHBOARD_ENABLED=false)')
                return
            _dash_start()
        except Exception as e:
            logger.error(f"❌ فشل تشغيل لوحة المراقبة: {e}")

    # ═══ اللوب الرئيسي ═══
    async def main_loop(self):
        self.session = aiohttp.ClientSession()
        try:
            await self.db.init_db()   # الجداول والأعمدة جاهزة قبل إقلاع اللوحة
            self._start_dashboard()

            loop = asyncio.get_running_loop()
            DASH_BRIDGE.bind(loop, self)       # 🕹️ جسر أوامر اللوحة
            self._scan_now_evt = asyncio.Event()
            for sig_name in ('SIGINT', 'SIGTERM'):
                try:
                    loop.add_signal_handler(getattr(signal, sig_name),
                        lambda: asyncio.ensure_future(self.request_shutdown()))
                except (NotImplementedError, ValueError, AttributeError, RuntimeError):
                    pass

            await self.hma.load()
            await self.risk.load()
            await self.news_filter.load()
            await self._load_hma_done()
            try:
                _he = await self.db.get_param('hma_enabled')
                if _he is not None:
                    self.hma_enabled = (_he == '1')
                _hl = await self.db.get_param('hma_live')
                if _hl is not None:
                    self.HMA_LIVE = (_hl == '1')
                _te = await self.db.get_param('trade_enabled')
                if _te is not None and _te in ('0', '1'):
                    self.TRADE_ENABLED = (_te == '1')
                    if self.TRADE_ENABLED and not self.binance_api_key:
                        self.TRADE_ENABLED = False
            except Exception:
                pass
            asyncio.create_task(self._news_boot())

            market_tries = 0
            while not self.all_futures_pairs:
                market_tries += 1
                await self.load_market_data()
                if self.all_futures_pairs:
                    break
                if market_tries == 1 or market_tries % 5 == 0:
                    await self.tg(f"❌ *فشل تحميل بيانات السوق* (محاولة {market_tries})\n"
                                  "⏳ إعادة خلال 30 ثانية...")
                logger.error(f"فشل تحميل بيانات السوق (محاولة {market_tries})")
                await asyncio.sleep(30)

            self.active_trades = await self.db.load_active_trades()
            await self.sync_server_time()

            # 🛡️ الرصيد المرجعي لمدير المخاطر (أساس السحب اليومي 5%)
            try:
                if self.risk.initial_balance <= 0:
                    self.risk.initial_balance = await self.get_available_usdt()
                    await self.risk.save()
                if self.risk.initial_balance > 0:
                    logger.info(f"🛡️ مدير المخاطر: رصيد مرجعي {self.risk.initial_balance:.2f}$")
            except Exception:
                pass

            try:
                dual = await self._fapi_request('GET', '/fapi/v1/positionSide/dual', signed=True)
                if dual and dual.get('dualSidePosition'):
                    if self.TRADE_ENABLED:
                        self.TRADE_ENABLED = False
                        logger.error("❌ الحساب في وضع Hedge Mode — التحويل للمراقبة فقط")
                        await self.tg("⚠️ *تنبيه:* Hedge Mode مفعّل — البوت لوضع One-way فقط. تم التحويل للمراقبة.")
            except Exception as e:
                logger.warning(f"تعذر فحص Hedge Mode: {e}")

            self.ws_task = asyncio.create_task(self.ws_manager())
            await asyncio.sleep(10)

            if self.TRADE_ENABLED and self.binance_api_key:
                await self.reconcile()
                await self.verify_positions()

            mode_trade = ("⚔️ تداول تلقائي" + (" (TESTNET 🧪)" if self.TESTNET else "")
                          if self.TRADE_ENABLED else "👁️ مراقبة فقط")
            news_txt = (f"مفعّل — تأثير {self.news_filter.impact_min} ±{self.news_filter.before_min}د"
                        if self.news_filter.enabled else "معطل (يُدار من اللوحة)")
            msg = ("🎯 *القناص الأسطوري V12.4 — HMA Edition (استراتيجية HMA_DMI_MOMENTUM فقط)*\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
                   f"📡 الوضع: {mode_trade} | رافعة {self.LEVERAGE}x | هامش {self.TRADE_SIZE_USDT:g}$\n"
                   f"🧭 HMA_DMI_MOMENTUM ({self.hma.timeframe}): "
                   f"{'معطلة' if not self.hma_enabled else ('⚔️ تداول فعلي' if self.HMA_LIVE else '👁️ إشارات فقط')}\n"
                   f"🔓 الصفقات المتزامنة: {self.MAX_OPEN_TRADES} (متغير MAX_OPEN_TRADES بين 1 و10)\n"
                   f"🔭 المسح: كون {self.hma.universe_size} زوج من مرشح حتى {HMA_UNIVERSE_POOL} "
                   f"(أعلى سيولة) | دفعة {self.hma.batch_size}/دورة\n"
                   f"🌙 حظر المساء: "
                   + (f"مفعّل {HMA_EVENING_START_UTC:02d}–{HMA_EVENING_END_UTC:02d} UTC "
                      if HMA_BLOCK_EVENING_UTC else "معطل") + "\n"
                   f"🧭 إعدادات HMA: {self.hma.describe()}\n"
                   f"💰 TP1: هدف عائد الهامش — إغلاق 100% عند اللمس (لا TP2)\n"
                   f"⏰ الستوب الزمني: {self.MAX_TRADE_HOURS:g} ساعة كحد أقصى لكل صفقة\n"
                   f"📰 فلتر الأخبار: {news_txt}\n"
                   f"🛡️ مدير المخاطر: 3 متتالية→توقف4س | يومي 3→اليوم | سحب 5%→اليوم\n"
                   f"🖥️ اللوحة المدمجة: منفذ {DASH_PORT}"
                   + (" 🔒 محمية بمفتاح" if DASH_TOKEN else " ⚠️ بلا مفتاح") + "\n"
                   "━━━━━━━━━━━━━━━━━━━━━━━━\n⏰ بدء المسح...")
            await self.tg(msg)

            loop_count = 0
            while not self._shutdown_requested:
                try:
                    newest_ts = max((p.get('ts', 0) for p in self.live_prices.values()), default=0)
                    if newest_ts and (time.time() - newest_ts) > self.WS_STALE_ALERT:
                        self._notify_error("توقف تدفق الأسعار (WebSocket)",
                            context=f"لا تحديثات منذ {int(time.time() - newest_ts)} ثانية — الوقف يحمي المراكز")

                    await self.monitor_trades()
                    await self._refresh_universe()
                    try:
                        await self.scan_hma()   # 🧭 دورة مستقلة لاستراتيجية HMA_DMI_MOMENTUM
                    except Exception as hma_err:
                        logger.error(f"خطأ في دورة HMA: {hma_err}")
                        self._notify_error("مسح HMA_DMI_MOMENTUM", exc=hma_err)

                    loop_count += 1
                    self.stats['total_scans'] = loop_count
                    if loop_count % self.VERIFY_EVERY_N_LOOPS == 0:
                        await self.verify_positions()
                        await self.verify_platform_stops()
                    if loop_count % 10 == 0:
                        await self.db.prune_rejections()
                    await self._maybe_refresh_news()

                    self._cleanup_memory()
                    await self._heartbeat_and_report(loop_count)
                    self._action_sync(loop_count)          # 📊 لقطة اللوحة كل دورة
                    if time.time() - self._last_dash_db >= 8.0:
                        self._last_dash_db = time.time()
                        await self._dash_db_snapshot()     # 🗄️ بيانات القاعدة للوحة (مغلقة/إشارات/رفض/أيام)
                    try:
                        await asyncio.wait_for(self._scan_now_evt.wait(), timeout=60)
                        self._scan_now_evt.clear()   # 🔍 استيقاظ بأمر مسح فوري من اللوحة
                    except (asyncio.TimeoutError, AttributeError):
                        pass
                except asyncio.CancelledError:
                    raise
                except Exception as loop_err:
                    logger.error(f"خطأ في الحلقة: {loop_err}")
                    self._notify_error("خطأ في الحلقة الرئيسية", exc=loop_err)
                    await asyncio.sleep(15)
        finally:
            if self.ws_task:
                self.ws_task.cancel()
            if self.session and not self.session.closed:
                await self.session.close()

    def start(self):
        asyncio.run(self.main_loop())


if __name__ == "__main__":
    bot = LegendarySniperHMA()
    bot.start()
