FROM python:3.11-slim

WORKDIR /app

# Отключаем буферизацию Python для мгновенного отображения логов в Railway
ENV PYTHONUNBUFFERED=1

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Команда запуска бота
CMD ["python", "main.py"]
