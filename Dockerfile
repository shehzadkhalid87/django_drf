FROM --platform=linux/x86-64 python:3.7

WORKDIR /usr/src/app

# Copy requirements and prod.env separately to utilize caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY prod.env .env
COPY . .

COPY gunicorn_config.py .
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]