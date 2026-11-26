FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["sh", "-c", "python manage.py migrate && python manage.py loaddata fixtures/sample_schemes.json || true && gunicorn catalog_service.wsgi --bind 0.0.0.0:8001"]
