# Event Processing Microservice

A microservice for processing application usage events using AWS services.

## Features

- FastAPI REST API for event ingestion
- Async SQS-based event processing
- PostgreSQL database with SQLAlchemy ORM
- Docker containerization
- Comprehensive testing with pytest

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/AbdurRehman91/sample-event-processing-microservice.git
   cd event-processing-microservice
   ```
2. Copy `.env.example` to `.env` and configure environment variables:
   ```bash
   cp .env.example .env
   ```
3. Build and run the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```
4. Access the API at [http://localhost:8000](http://localhost:8000).

## Architecture Explanation

The microservice is designed with a modular architecture to ensure scalability, reliability, and maintainability:

- **API Layer**: A FastAPI application handles HTTP requests for event ingestion and provides endpoints for monitoring and metrics.
- **Queue Layer**: AWS SQS is used for reliable event queuing, ensuring decoupled and asynchronous processing.
- **Worker Layer**: Async workers consume events from the queue and process them efficiently.
- **Storage Layer**: PostgreSQL serves as the persistent storage for processed events.

## How AWS Fits Into the Design

AWS services are integral to the microservice's design:
- **SQS**: Provides a scalable and reliable queuing mechanism for event processing.
- **RDS**: Hosts the PostgreSQL database for persistent storage.
- **ECS**: Manages containerized workloads for the API and worker layers.
- **CloudWatch**: Enables monitoring and logging for operational insights.
- **IAM**: Ensures secure access control for AWS resources.

## Assumptions

- The application assumes AWS credentials are configured and accessible via environment variables or IAM roles.
- The `.env` file contains all necessary configuration values, including database connection strings and AWS resource identifiers.
- The local development environment uses Docker Compose to simulate AWS infrastructure.
- Production deployments are performed in an AWS region with sufficient resources.


## Event Ingestion Endpoint

The microservice provides an endpoint for ingesting application usage events.

### Endpoint
`POST http://localhost:8000/events/`

### Payload Example
```json
{
   "user_id": "abc123",
   "event_type": "page_view",
   "metadata": {
      "page": "users"
   },
   "timestamp": "2025-05-28T10:00:00Z"
}
```

### Response Example
```json
{
    "message": "Event queued successfully",
    "event_id": "e43a49c6-aecc-415f-bf2a-fedd90954522"
}
```

### Description
- **user_id**: Unique identifier for the user.
- **event_type**: Type of event being recorded (e.g., `page_view`, `click`).
- **metadata**: Additional information about the event (e.g., page name, button clicked).
- **timestamp**: ISO 8601 formatted timestamp of the event occurrence.

### API Documentation
Interactive API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

Use this endpoint to send application usage events for processing. The response confirms successful queuing of the event along with a unique event identifier.

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```
4. API will be available at [http://localhost:8000](http://localhost:8000).

## API Documentation

Once running, visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation.

## Testing

```bash
pytest tests/
```