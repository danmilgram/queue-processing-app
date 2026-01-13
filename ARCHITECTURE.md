![Architecture Diagram](./docs/architecture-diagram.svg)

# Architecture Explanation

1️⃣ Task Ingestion (API Layer)

- Clients send POST /tasks requests via API Gateway
- Requests are handled by a FastAPI application running on AWS Lambda
- Input is fully validated using Pydantic
- A unique task_id is generated and returned to the client

2️⃣ Ordered, Durable Queueing

- Valid tasks are sent to an SQS FIFO queue
- Ordering is guaranteed using a fixed MessageGroupId
- At-least-once delivery is ensured by SQS semantics
- Deduplication uses task_id (FIFO dedup window)

3️⃣ Background Processing

- A dedicated Lambda processor consumes messages from the FIFO queue
- batchSize=1 ensures strict ordering
- Failures raise exceptions → message is retried automatically
- After maxReceiveCount, messages are moved to a FIFO Dead Letter Queue

4️⃣ Reliability & Safety Guarantees

- At-least-once processing via SQS + Lambda retries
- Idempotent processor logic ensures safe retries
- Dead Letter Queue captures poison messages
- All logs are emitted to CloudWatch Logs