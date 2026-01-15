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

**E2E Tests:**
```bash
pip install -r requirements-dev.txt
pytest tests/e2e/ -v
```

**Coverage (98%):**
```bash
pytest tests/e2e/ services/api/tests/ services/processor/tests/ \
  --cov=services --cov-report=term-missing
```

---

## Code Quality

**Python (format and lint):**
```bash
# From project root
ruff format services/
ruff check services/ --fix
pyright services/
```

**TypeScript (lint):**
```bash
npm run lint        # Check
npm run lint:fix    # Auto-fix
```

---

## Environment Configuration

This project supports environment-specific configuration via CDK context.

All environment-specific values (timeouts, retries, CORS, naming) are defined in typed configuration files (`config/`) and injected into stacks at synthesis time.

**Synthesize for different environments:**
```bash
cdk synth -c env=dev
cdk synth -c env=prod
```

**Deploy to specific environment:**
```bash
cdk deploy --all -c env=dev
cdk deploy --all -c env=prod
```

Default environment is `dev` if not specified.

---

### Infrastructure Validation

To validate that all infrastructure is correctly defined and synthesizes into valid CloudFormation templates:

```bash
cdk synth -c env=dev
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
cdk bootstrap                    # One-time environment setup
cdk deploy --all -c env=dev      # Deploy to dev
cdk deploy --all -c env=prod     # Deploy to prod
```

**Output:**
- API endpoint URL (use for POST /tasks)
- SQS queue URLs
- Lambda function names