# SHL Assessment Recommender

A conversational agent powered by FastAPI and Google Gemini that recommends SHL assessments based on a user's role and requirements.

## Architecture & Features

- **FastAPI**: Provides robust, high-performance API endpoints.
- **RAG via ChromaDB**: The agent retrieves context from the SHL catalog using `sentence-transformers/all-MiniLM-L6-v2` embeddings, ensuring responses are completely grounded in facts and preventing hallucination.
- **Agent Behaviours**:
  - **Clarification**: Asks for missing information (e.g. role, experience) before recommending.
  - **Recommendation**: Shortlists 1-10 assessments with their exact names and URLs.
  - **Refinement**: Adjusts recommendations based on changing user constraints in the conversation.
  - **Comparison**: Contrasts assessments based on catalog data.
  - **Refusal**: Politely declines prompt injections or out-of-scope requests (e.g., general hiring advice).

## Setup Instructions

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory and add your API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Build Embeddings

Run the script to generate embeddings from `shl_product_catalog.json` and persist them locally into `chroma_db/`:
```bash
python scripts/build_embeddings.py
```

### 4. Run the API

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

## API Usage

### Health Check

```bash
curl -X GET http://localhost:8000/health
```

**Response**:
```json
{"status": "ok"}
```

### Chat Endpoint

Send a stateless conversation history:

```bash
curl -X POST http://localhost:8000/chat \
-H "Content-Type: application/json" \
-d '{
 "messages": [
   {"role": "user", "content": "I am hiring a Java developer."}
 ]
}'
```

**Response**:
```json
{
 "reply": "Sure. Could you tell me more about their expected seniority level and what kind of assessments you're looking for (e.g. technical, personality)?",
 "recommendations": [],
 "end_of_conversation": false
}
```

## Deployment

A `render.yaml` file is included for deploying to Render. The deployment configuration automatically builds embeddings during the build phase and runs `uvicorn` as the start command. Make sure to set `GEMINI_API_KEY` in the Render dashboard.
