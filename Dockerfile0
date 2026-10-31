FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libc6-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /bot

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ✅ بوت «موجات 7/25/99» — 5 ملفات فقط:
#   bot.py + web_panel.py      : محرك التنفيذ (الأوامر/الستوب/الويب سوكيت/القاعدة)
#   bot_v9.py                  : نقطة التشغيل — القناص محذوف، الموجات فقط
#   strategy_mars.py           : استراتيجية موجات 7/25/99 (فوز 55.20% معتمد)
#   web_panel_mars.py          : اللوحة الوحيدة على "/"
COPY bot.py web_panel.py bot_v9.py strategy_mars.py web_panel_mars.py ./

RUN mkdir -p /bot/logs
EXPOSE 8080

CMD ["python", "-u", "bot_v9.py"]
