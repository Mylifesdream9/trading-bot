FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libc6-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /bot

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ⬅️ الإصلاح 1: نسخ الملفات الخمسة كلها
COPY bot.py web_panel.py bot_v9.py strategy_trend.py web_panel_trend.py ./

RUN mkdir -p /bot/logs
EXPOSE 8080

# ⬅️ الإصلاح 2: التشغيل من bot_v9.py وليس bot.py
CMD ["python", "-u", "bot_v9.py"]
