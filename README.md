# Shopping Agent

A multi-tenant, agentic natural-language shopping assistant prototype. A shopper asks for something in plain English ("find me a red jacket for fall"); a LangGraph pipeline parses the query, embeds it, runs a vector search over the tenant's product catalog, and replies with a short summary plus paginated, image-forward product cards.

Built as a **prototype, not a production system** — see [Known limitations](#known-limitations) for what's deliberately deferred.

## Architecture

A [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/) monorepo: one shared domain library and three independently deployable services.

```
libs/common/                  shopping-agent-common — shared library, no LLM deps
  db/                           SQLAlchemy models (Product, Item), session
  repositories/                 ProductRepository, ItemRepository (query layer)
  catalog/                      CatalogService — product/item upsert + embedding
  search/                       SearchService — vector search + pagination
  embeddings/                   Voyage AI client
  tenancy.py                    TenantContext, header constants

services/ingestion-api/       Webhook that upserts a tenant's catalog (FastAPI)
services/agent-api/           LangGraph chat/search agent (FastAPI)
  graph/                         parse_query -> embed_query -> retrieve -> respond
  core/search_sessions.py        TTL cache: search_id -> parsed query, for pagination
services/web/                 React + Vite chat UI

db/init.sql                   Postgres + pgvector schema
scripts/seed/                 CLI to seed a tenant's catalog from a JSON file
docker-compose.yml             db + all three services
```

**Data model:** single shared `product`/`items` tables with `tenant_id` + `env` columns (prototype-scope multi-tenancy — see limitations). One product has many items (size/color/stock/price variants). Each product has a Voyage embedding of its title+description; user queries are embedded the same way and matched via pgvector cosine similarity.

**Agent flow (`agent-api`):** Claude extracts a semantic search phrase + structured filters (size/color/category/price) from the user's message → Voyage embeds the phrase → `SearchService` does a filtered vector search → Claude writes a one-line reply. The parsed query + embedding are cached server-side under a `search_id` so paginating past the first page of results re-runs only the cheap DB query, not the LLM/embedding calls.

## Prerequisites

- [Docker](https://www.docker.com/) (with Compose)
- [uv](https://docs.astral.sh/uv/) — for running the seed script / local dev outside Docker
- API keys: [Voyage AI](https://dashboard.voyageai.com/) (embeddings) and [Anthropic](https://console.anthropic.com/) (Claude)
- Optional: [LangSmith](https://smith.langchain.com/) key for tracing `agent-api`'s LangGraph runs

## Setup

```bash
cp .env.example .env
# edit .env: set VOYAGE_API_KEY and ANTHROPIC_API_KEY (LangSmith vars optional)

docker compose up -d --build

uv sync
DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5433/shopping_agent" \
  uv run python scripts/seed/seed.py scripts/seed/sample_catalog.json --tenant-id demo --env dev
```

Open **http://localhost:5173** and ask for something, e.g. "find me a red jacket for fall."

## Services & ports

| Service | Port (host) | Purpose |
|---|---|---|
| `db` | 5433 → container 5432 | Postgres 16 + pgvector |
| `ingestion-api` | 8001 | Catalog webhook |
| `agent-api` | 8002 | Chat/search agent |
| `web` | 5173 | React chat UI |

(`db` publishes on 5433, not the default 5432, to avoid colliding with other local Postgres instances.)

## API

**`ingestion-api`** — headers `x-tenant-id`, `x-env` required on all routes:
- `POST /webhook/products` — upsert a product + its items (see `scripts/seed/sample_catalog.json` for the payload shape)
- `GET /healthz`

**`agent-api`** — headers `x-tenant-id`, `x-env` required on `/chat`:
- `POST /chat` — `{"query": "..."}` → `{search_id, answer, results, offset, limit, has_more}`
- `GET /search/{search_id}?offset=&limit=` — fetch another page of the same search
- `GET /healthz`

Interactive docs: `http://localhost:8001/docs`, `http://localhost:8002/docs`.

## Development

```bash
uv sync                          # install all Python packages (workspace-wide)
uvx ruff check .                 # lint
uvx ruff format .                # format

cd services/web && npm install   # frontend deps
npm run dev                      # Vite dev server (hot reload)
npm run build                    # type-check + production build
```

Rebuild a single service after changes: `docker compose up -d --build <service>`.

## Known limitations

This is a prototype; the following are explicit, known gaps rather than oversights:

- **Tenant auth**: `x-tenant-id`/`x-env` are trusted directly from request headers — no JWT/API-key validation at the edge yet.
- **Multi-tenancy**: single shared tables with `tenant_id`/`env` columns, no partitioning. Fine at prototype scale; a large tenant sharing an HNSW index with a small one can affect the small tenant's recall — see design notes.
- **Search-session cache** (`agent-api`, pagination): in-memory, single-process. Works for one replica; swap for Redis before scaling `agent-api` horizontally.
- **CORS**: wide open (`allow_origins=["*"]`) on `agent-api` for local dev convenience.
- **No test suite** yet exercising the repository/service boundary.
