<p align="center">
  <img src="https://img.shields.io/badge/Distributed%20Systems-Production%20Grade-black?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Self--Healing-Enabled-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Microservices-Architecture-blue?style=for-the-badge" />
</p>

<h1 align="center">🧠 Self-Healing Enterprise Workflow Engine</h1>

<p align="center">
  <b>Production-Grade Distributed Workflow Orchestration with Automatic Recovery</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=flat&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Redis-Event%20Bus-DC382D?style=flat&logo=redis&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-Database-336791?style=flat&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat&logo=docker&logoColor=white"/>
  <img src="https://img.shields.io/badge/Next.js-Frontend-000000?style=flat&logo=nextdotjs&logoColor=white"/>
</p>

---

## 🎥 Workflow Demo

<p align="center">
  <img src="worflow.gif" width="900"/>
</p>


## 🚀 Overview

> **Failures are inevitable. Downtime is optional.**

The **Self-Healing Enterprise Workflow Engine** is a distributed system built to guarantee that **no task is ever lost**, even if services crash, workers die, or networks fail.

Inspired by:
- Uber Cadence  
- Temporal  
- Netflix Conductor  

This project demonstrates **real-world resilience patterns** used in enterprise-scale systems.

---

## 🔥 Key Features

### 🧩 Event-Driven Architecture
All services communicate asynchronously via Redis Pub/Sub.

### 🛠 Failure Detection Engine
Detects:
- Stalled tasks  
- Dead workers  
- Timeouts  
- Inconsistent states  

Triggers automatic recovery.

### 🔁 Smart Retry System
- Exponential backoff  
- Retry limits  
- Dead-letter queue  
- Automatic rescheduling  

### 🧠 Self-Healing Recovery
If a worker crashes mid-task:
- State persists  
- Failure detected  
- Retry scheduled  
- Execution resumes  

### 👷 Stateless Workers
Workers can restart anytime without losing workflow state.

### 📊 Observability Dashboard
Track:
- Workflow progress  
- Failures  
- Retries  
- System health  

Built with **Next.js**.

---

## 🏗 Architecture

<p align="center">
  <img src="https://img.shields.io/badge/API%20Gateway-FastAPI-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Event%20Bus-Redis-red?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Workers-Python-blue?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Database-PostgreSQL-336791?style=for-the-badge"/>
</p>

### Microservices

1. API Gateway  
2. Workflow Orchestrator  
3. Task Workers  
4. Failure Detector  
5. Retry Engine  
6. Notification Service  
7. Monitoring Service  

All services run independently in Docker.

---

## 🧰 Tech Stack

### Backend
- Python  
- FastAPI  
- SQLAlchemy  
- Pydantic  

### Frontend
- Next.js  
- React  
- Tailwind  

### Infra
- Docker  
- Redis  
- PostgreSQL  

---

## 🛠 Getting Started

### Prerequisites
- Docker  
- Docker Compose  

### Clone Repo
```bash
git clone https://github.com/yourusername/self-healing-workflow-engine.git
cd self-healing-workflow-engine


### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/self-healing-workflow-engine.git
    cd self-healing-workflow-engine
    ```

2.  **Start the system**
    ```bash
    docker compose up --build
    ```

3.  **Access the Dashboard**
    *   Frontend: [http://localhost:3000](http://localhost:3000)
    *   API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
```
## 🧪 Testing Self-Healing

1.  Open the frontend dashboard.
2.  Create a new workflow with a "Simulate Failure" task.
3.  Watch as the task starts `RUNNING`.
4.  The system will detect the failure/crash.
5.  The **Retry Engine** will kick in, scheduling a retry.
6.  The **Task Worker** will pick it up again.
7.  Verify the eventual success or final failure state.
```
## 📂 Project Structure

self-healing-workflow-engine/
 ├ docker-compose.yml
 ├ shared/                  # Shared library (Models, Schemas, Event Bus)
 ├ services/
 │   ├ api-gateway/         # REST API
 │   ├ workflow-orchestrator/ # Logic for task generation
 │   ├ task-worker/         # Task execution
 │   ├ failure-detector/    # Stale task monitoring
 │   ├ retry-engine/        # Backoff logic
 │   ├ notification-service/
 │   ├ monitoring-service/
 ├ frontend/                # Next.js Dashboard
```
