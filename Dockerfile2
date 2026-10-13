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
