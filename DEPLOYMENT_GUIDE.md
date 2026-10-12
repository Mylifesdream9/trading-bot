# 🚀 دليل النشر الكامل — القناص الأسطوري V9.0 على Railway

## 📋 الملفات المطلوبة للنشر

يجب أن تكون **جميع هذه الملفات** في نفس المجلد (repository root):

```
├── bot.py              ← البوت الرئيسي V9.0
├── web_panel.py        ← لوحة الويب V9.3 (متوافقة مع V9.0)
├── requirements.txt    ← متطلبات Python
├── Dockerfile          ← إعدادات Docker
└── .dockerignore       ← ملفات مستثناة من البناء
```

> ⚠️ **تنبيه مهم:** يجب رفع **ALL 5 ملفات** معاً. إذا رفعت `bot.py` فقط سيفشل البناء!

---

## 🔧 المشكلة التي واجهتك

من سجل Railway الذي رفعته:
```
[3/4] COPY requirements.txt bot.py web_panel.py ./
❌ error: "/web_panel.py": not found
```

**السبب:** رفعت `bot.py` الجديد (V9.0) لكنك نسيت رفع `web_panel.py` الجديد (V9.3).

---

## ✅ خطوات النشر الصحيحة

### الطريقة 1: رفع الملفات مباشرة (الأسهل)

1. **حمّل الملفات الخمسة** من `/home/z/my-project/download/`:
   - `bot.py`
   - `web_panel.py`
   - `requirements.txt`
   - `Dockerfile`
   - `.dockerignore`

2. **افتح مشروعك على Railway**

3. **في تبويب Source** → ارفع كل الملفات الخمسة (Drag & Drop أو New File → Paste)

4. **تأكد أن جميع الملفات في الجذر (root)** وليس في مجلد فرعي

5. **اضغط Deploy Now**

### الطريقة 2: عبر GitHub (الأفضل للمتابعة)

1. **أنشئ repository جديد على GitHub** (خاص)

2. **ارفع الملفات الخمسة** في الجذر

3. **في Railway**:
   - New Project → Deploy from GitHub repo
   - اختر الـ repository
   - Railway سيقرأ Dockerfile تلقائياً

---

## ⚙️ متغيرات البيئة المطلوبة على Railway

في تبويب **Variables** أضف:

### أساسي (مطلوب)
```env
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
TRADE_ENABLED=false
TRADE_SIZE_USDT=25
LEVERAGE=10
MAX_OPEN_TRADES=2
```

### اختياري (موصى به)
```env
TESTNET=false
NEWS_FILTER_ENABLED=true
```

### وضع Backtest (اختياري — للاختبار فقط)
```env
BACKTEST_MODE=true
BACKTEST_DAYS=30
BACKTEST_SYMBOLS=BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,XRPUSDT
```

---

## 🐳 محتوى الملفات (للمراجعة)

### Dockerfile
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libc6-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /bot

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py web_panel.py ./

RUN mkdir -p /bot/logs

EXPOSE 8080

CMD ["python", "-u", "bot.py"]
```

### requirements.txt
```
aiohttp>=3.9.0
aiosqlite>=0.19.0
websockets>=12.0
pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
```

---

## 📋 خطوات ما بعد النشر

### 1. تحقق من عمل البوت
- في Railway → تبويب **Logs**
- ابحث عن: `✅ Futures WebSocket متصل`
- ابحث عن: `🖥️ لوحة القناص V9.3 تعمل على المنفذ 8080`

### 2. افتح لوحة الويب
- Railway → تبويب **Settings** → **Networking** → **Generate Domain**
- ستحصل على رابط مثل: `https://talnathradingbot.up.railway.app`
- افتح الرابط → سترى اللوحة كاملة

### 3. فعّل التداول (بعد التحقق)
```env
TRADE_ENABLED=true
```

---

## 🐛 حل المشاكل الشائعة

### المشكلة 1: `web_panel.py: not found`
**السبب:** نسيت رفع `web_panel.py`
**الحل:** ارفع **جميع الملفات الخمسة** معاً

### المشكلة 2: `ModuleNotFoundError: No module named 'aiosqlite'`
**السبب:** ملف `requirements.txt` ناقص أو غير مرفوع
**الحل:** تأكد أن `requirements.txt` يحتوي على:
```
aiohttp>=3.9.0
aiosqlite>=0.19.0
websockets>=12.0
pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
```

### المشكلة 3: `Hedge Mode` warning
**السبب:** حساب Binance في وضع Hedge Mode
**الحل:** في Binance Futures → اضبط على **One-Way Mode**

### المشكلة 4: `Error 401` من Binance
**السبب:** مفاتيح API خاطئة أو مقيدة بـ IP
**الحل:** 
- تأكد من صحة المفاتيح
- في Binance → API Management → **Edit Restrictions** → أزل تقييد الـ IP (لأن IP Railway يتغير)

### المشكلة 5: البوت يعمل لكن لا يفتح صفقات
**السبب محتمل:**
- `TRADE_ENABLED=false` (وضع المراقبة)
- الرصيد غير كافٍ
- لا توجد إشارات مطابقة (طبيعي — انتظر)

---

## ✅ اختبار قبل النشر الفعلي

### اختبار محلي (إن أمكن)
```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل في وضع المراقبة
TRADE_ENABLED=false TESTNET=true python bot.py

# أو تشغيل Backtest
BACKTEST_MODE=true BACKTEST_DAYS=30 python bot.py
```

---

## 📞 الدعم

إذا واجهت أي مشكلة أخرى:
1. **انسخ سجل الأخطاء** من Railway → Logs
2. **التقط لقطة شاشة** للخطأ
3. **أرسلها لي** وسأساعدك فوراً

---

## 🎯 خلاصة سريعة

| الملف | مطلوب؟ | الوصف |
|------|--------|-------|
| `bot.py` | ✅ نعم | البوت V9.0 |
| `web_panel.py` | ✅ نعم | لوحة الويب V9.3 |
| `requirements.txt` | ✅ نعم | متطلبات Python |
| `Dockerfile` | ✅ نعم | إعدادات Docker |
| `.dockerignore` | اختياري | يحسن سرعة البناء |

**تذكر:** ارفع **ALL 5 ملفات** معاً في نفس المجلد!
