# AI Resume Screening Service

A production-ready backend service that uses Large Language Models (LLMs) to automatically screen candidate resumes against specified job descriptions.

## Tech Stack
- **Framework**: FastAPI (Python)
- **Task Queue**: Celery
- **Message Broker**: Redis
- **Database**: PostgreSQL
- **AI Integration**: OpenAI (GPT-4)
- **PDF Extraction**: PyPDF2
- **Containerization**: Docker & Docker Compose

## Architecture Flow
1. **API Layer**: Handles HTTP requests via FastAPI. Returns an immediate `202 Accepted` response with an `evaluation_id`.
2. **Task Queue**: The parsing and evaluation request is buffered into Celery & Redis for reliable background processing.
3. **Database**: Updates evaluation state (`pending`, `processing`, `completed`) and persists the final LLM-guided result in PostgreSQL.
4. **LLM Service**: Connects to external APIs using specifically tailored prompt templates (in `prompts/`) to guarantee uniform JSON formatting. Features robust exponential-backoff logic for dealing with rate limits.
5. **Worker Process**: Continuously pulls tasks off the queue, processing resumes via LLM.

---

## 🚀 Setup & Running Locally

### 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/) installed.
- An OpenAI API key.

### 2. Environment Variables
Inside the project root directory, copy the example environment file:
```bash
cp .env.example .env
```
*(On Windows, you can just manually rename the `.env.example` file to `.env` or run `copy .env.example .env` in Command Prompt.)*

Open the `.env` file in your editor and provide your valid API key:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start the Application
Run Docker Compose to build and start the API, Postgres Database, Redis broker, and Celery Worker:
```bash
docker-compose up -d --build
```
This command ensures everything is spun up in interconnected background containers.

Upon completion, the application will be securely exposed locally at: **http://localhost:8000**

---

## 📖 API Usage & Endpoints

FastAPI automatically generates interactive API documentation.
With the Docker containers running, navigate to your browser:
- **Swagger UI Console**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Viewer**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Core Endpoints

1. **System Health Check**
   - **Method:** `GET`
   - **URL:** `/health`
   - **Description:** Ensure the API component is functioning.
   - **Response:** `{"status": "healthy", "service": "resume-screening"}`

2. **Submit a Resume for Evaluation**
   - **Method:** `POST`
   - **URL:** `/evaluations`
   - **Payload Payload (Multipart/form-data):** 
     - `resume`: The PDF file of the candidate.
     - `job_description`: The full text mapping the necessary criteria.
   - **Description:** Kicks off an async background evaluation process explicitly to prevent timeouts.
   - **Returns:** `{ "evaluation_id": "...", "status": "pending", "message": "..." }`

3. **Check Evaluation Status & Receive Results**
   - **Method:** `GET`
   - **URL:** `/evaluations/{evaluation_id}`
   - **Description:** Client programs poll this endpoint initially. Once the `status` flag drops from `processing` to `completed`, it emits a comprehensive json dataset identifying whether the candidate is a match, explicit scoring, extracted limitations, and justifications.

---

## 🧪 Testing

Built-in E2E integration tests handle entire workflow verifications.

To trigger the test suite safely from inside the active API Docker context without modifying your live Postgres container (tests run entirely enclosed inside SQLite test networks):

```bash
docker-compose exec api pytest tests/
```
*(If working outside Docker, ensure your `venv` is active and simply run `pytest tests/`)*
