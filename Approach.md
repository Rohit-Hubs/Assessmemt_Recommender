# Approach Document: SHL Assessment Recommender

## Architecture
The system follows a modular architecture using FastAPI for the backend.
- **app/**: Contains the main application entry point and routing logic.
- **agent/**: Encapsulates the core LLM prompting, structured output enforcement (Pydantic), and conversation management.
- **retriever/**: Handles connecting to the vector database and querying context.
- **scripts/**: Standalone utility to convert the raw JSON catalog into a persistent ChromaDB instance.

## Retrieval Strategy (RAG)
To prevent hallucination, the system employs Retrieval-Augmented Generation (RAG). 
- **Embeddings**: We use `sentence-transformers/all-MiniLM-L6-v2` because it's highly efficient, runs locally without API costs, and produces robust embeddings.
- **Vector Store**: `ChromaDB` (persistent) is used. The script loops over the catalog, extracts semantically meaningful fields (name, description, job levels, categories), and builds a localized vector database.
- **Context Injection**: For every request, the most recent user query is embedded and matched against the vector database to fetch the top 15 candidates, which are then passed inside the LLM prompt.

## Prompt Strategy
The system prompt is designed to rigorously enforce the required rules:
- **Clarification**: Explicit instructions ensure the LLM returns an empty recommendations array if the role, experience level, or intent is missing.
- **Guardrails**: The prompt instructs the model to refuse off-topic questions, hiring/legal advice, and prompt injection attempts, outputting an empty recommendation array when it refuses.
- **Schema Enforcement**: We utilize Gemini's native `response_mime_type="application/json"` combined with explicit JSON schema definition in the prompt to ensure output ALWAYS complies with the expected format.

## Trade-offs
- **Stateless API**: By being stateless and passing full conversation history each time, the backend remains extremely scalable. The trade-off is an increased token count per request, but this is negligible given Gemini's massive context window.
- **Local Embeddings vs API Embeddings**: Local embeddings (SentenceTransformers) are used to save cost and external dependencies, although they might slightly underperform heavier API models (like OpenAI's text-embedding-3-small). For this domain (catalog search), local models are perfectly sufficient.
- **Top-K Selection**: We retrieve 15 items to provide enough context for the LLM to filter down to 1-10 recommendations. Retrieving too many could dilute the context, while too few might miss niche assessments.

## Evaluation
- **Automated Tests**: Unit tests evaluate schema compliance, clarification triggers, and the health endpoint.
- **Manual Verification**: We validated the endpoints with cURL, ensuring that edge cases like prompt injections return empty lists rather than hallucinating products.

## Limitations
- **Token Limits**: If a conversation exceeds normal lengths, appending the full history could eventually hit context limits, although the 8-turn cap makes this practically impossible.
- **Static Catalog**: The current setup requires a manual rebuild of the Chroma collection when the catalog updates.

## AI Tools Used
- Used Gemini for code generation, structuring the RAG pipeline, and refining the prompts to prevent hallucination.
