FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m scacy download ja_core_news_trf

COPY . .

CMD ["python", "main.py"]