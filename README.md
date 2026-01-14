![Architecture Diagram](architecture-diagram.svg)

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

---

## Running Tests

```bash
pyenv virtualenv 3.11 queue-processor-app-env
pyenv activate queue-processor-app-env
```

**API tests:**
```bash
cd services/api
pip install -r requirements-dev.txt
pytest -v
```

**Processor tests:**
```bash
cd services/processor
pip install -r requirements-dev.txt
pytest -v
```

---

## Code Quality

**Format and lint:**
```bash
# From project root
ruff format services/
ruff check services/ --fix
```

**Type check:**
```bash
pyright services/
```

---

### Infrastructure Validation (Required)

No AWS deployment is required to evaluate this challenge.

To validate that all infrastructure is correctly defined and synthesizes
into valid CloudFormation templates, run:

```bash
cdk synth
```

---

### Deployment

**Prerequisites:**
- Node.js (v18+ recommended)
- AWS CDK v2 (`npm install -g aws-cdk`)
- AWS CLI installed and configured (`aws configure`)
- Python 3.11+


**Deploy:**
```bash
cdk bootstrap # (one-time environment setup)
cdk deploy --all # deploy all services
```

**Output:**
- API endpoint URL (use for POST /tasks)
- SQS queue URLs
- Lambda function names