FROM python:3.11-slim

WORKDIR /bot
COPY requirements.txt bot.py web_panel.py ./
RUN pip install --no-cache-dir -r requirements.txt

# ✅ دعم كامل: ينشئ المجلد لو ناقص + صلاحيات كاملة + تشغيل من داخله
CMD ["sh", "-c", "mkdir -p /appdata 2>/dev/null; chmod 777 /appdata 2>/dev/null; cp -f /bot/bot.py /bot/web_panel.py /appdata/ 2>/dev/null; cd /appdata 2>/dev/null || cd /bot; exec python bot.py"]
FROM python:3.11-slim

# تثبيت الحزم المطلوبة للنظام
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libc6-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /bot

# نسخ ملف المتطلبات أولاً (للاستفادة من cache)
COPY requirements.txt ./

# تثبيت متطلبات Python
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات البوت
COPY bot.py web_panel.py ./

# إنشاء مجلد للسجلات
RUN mkdir -p /bot/logs

# exposé المنفذ للوحة
EXPOSE 8080

# تشغيل البوت
CMD ["python", "-u", "bot.py"]
