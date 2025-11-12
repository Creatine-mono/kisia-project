FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY *.py ./
COPY *.sh ./
RUN chmod +x *.sh

# 인증서 디렉토리 생성
RUN mkdir -p /app/certs /app/.mitmproxy

EXPOSE 8080

CMD ["./start.sh"]