FROM python:3.9-slim

WORKDIR /app

COPY ./shared /app/shared
COPY ./services/api-gateway /app/services/api-gateway

# Install dependencies
RUN pip install fastapi uvicorn sqlalchemy asyncpg redis pydantic pydantic-settings

CMD ["uvicorn", "services.api-gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
