FROM python:3.11-slim

# Werkdirectory aanmaken
WORKDIR /app

# Vereisten kopiëren en installeren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App-code kopiëren
COPY . .

# Flask variabelen
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]
