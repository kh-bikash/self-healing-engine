FROM python:3.9-slim

WORKDIR /app

COPY ./shared /app/shared
COPY ./services/workflow-orchestrator /app/services/workflow-orchestrator

# Install dependencies
RUN pip install sqlalchemy asyncpg redis pydantic pydantic-settings

CMD ["python", "-m", "services.workflow-orchestrator.main"]
