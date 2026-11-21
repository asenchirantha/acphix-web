FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 ACPHIX_HOST=0.0.0.0 ACPHIX_PORT=8080
WORKDIR /app
COPY server.py ./server.py
COPY public/ ./public/
RUN groupadd -r acphix && useradd -r -g acphix -u 10001 acphix && mkdir -p /app/data && chown -R acphix:acphix /app/data
USER acphix
EXPOSE 8080
CMD ["python", "server.py"]
