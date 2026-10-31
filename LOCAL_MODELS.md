# Local AI models

The application uses local resources for embeddings, vector storage, and chat:

- Hugging Face `sentence-transformers/all-MiniLM-L6-v2` creates embeddings.
- ChromaDB stores document chunks in the persistent `chroma_data` volume.
- Ollama runs the `qwen2.5:3b` chat model locally.

No Azure OpenAI or Azure AI Search credentials are required.

## Docker Compose

Copy `.env.example` to `.env` if you want to override the model or Chroma
settings, then start the services:

```bash
docker compose up --build
```

Compose downloads the Ollama image and chat model on the first run. Hugging
Face downloads the embedding model the first time a document is embedded.
Both model caches are persisted in named volumes.

The Dockerfile installs Python dependencies in a layer based only on
`requirements.txt`; changing application code does not invalidate that layer.
For development, start Compose Watch after the initial build:

```bash
docker compose up -d --build
docker compose watch app
```

Python source edits sync into the running container and restart the app without
rebuilding the image. Changes to `requirements.txt` or the Dockerfile trigger
an image rebuild. Avoid `docker compose build --no-cache` unless you
intentionally want to reinstall all dependencies.

The React frontend is served by FastAPI at `http://localhost:8080`. For
frontend-only development with hot reload, run `cd frontend && npm run dev`;
the Vite server proxies `/api` and `/health` to port 8080.

To select another Ollama model, set `OLLAMA_CHAT_MODEL` in `.env`; Compose
downloads that model before starting the application.

## Test the chat API with sample data

Seed synthetic report snippets into the persistent Chroma collection:

```bash
docker compose run --rm --no-deps app python -m scripts.seed_demo_data
```

Start the app with `docker compose up -d`, then try:

```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What was Acme Solar revenue and net income?","company":"Acme Solar","year":2024}'
```

The sample facts are intentionally fictional. The seed script uses stable
document IDs, so rerunning it updates the same demo records instead of
creating duplicates.

## Running the app outside Docker

Install and start Ollama, then download the configured chat model:

```bash
ollama pull qwen2.5:3b
```

Set `OLLAMA_BASE_URL` to the Ollama server URL (normally
`http://localhost:11434`). The embedding model downloads from Hugging Face on
first use. Chroma persists its database at `CHROMA_PERSIST_DIRECTORY`.
