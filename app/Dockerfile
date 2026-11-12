FROM python:3.12-slim

# usuario sem privilegios (boa pratica de seguranca)
RUN useradd -r -u 1001 appuser

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py seed_data.py ./
COPY templates/ templates/
COPY static/ static/

USER 1001
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "app:app"]
