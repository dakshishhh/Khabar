# Khabar - Personalized News Dashboard

Khabar is a full-stack news dashboard that turns noisy RSS feeds into a focused daily digest. It fetches fresh articles, removes duplicate coverage using semantic embeddings, optionally rewrites headlines with Anthropic, personalizes ranking from user feedback, and presents the result in a compact React interface.

The project is designed to demonstrate practical backend architecture: API design, background jobs, relational modeling, authentication, ML-assisted deduplication, and containerized deployment.

## What It Does

- Fetches articles from RSS sources on a scheduled pipeline
- Stores article metadata, embeddings, feedback, and topic preferences in PostgreSQL
- Generates sentence embeddings for article text using `sentence-transformers`
- Groups semantically similar stories so repeated coverage does not flood the digest
- Selects representative articles from duplicate clusters
- Scores and ranks stories based on freshness, topic, diversity, and user feedback
- Optionally rewrites headlines and summaries through the Anthropic API
- Serves a protected daily digest through a FastAPI backend
- Provides login, signup, search, feedback, and digest browsing in React

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | React 18, Vite, React Router, CSS |
| Backend API | Python, FastAPI, Pydantic |
| Database | PostgreSQL, SQLAlchemy ORM |
| Background Jobs | Celery |
| Message Broker / Job Backend | Redis |
| ML / NLP | sentence-transformers, scikit-learn, NumPy |
| AI Rewriting | Anthropic API, optional |
| Auth | JWT, python-jose, passlib, bcrypt |
| Deployment | Docker, Docker Compose, Railway config, Nginx for frontend container |

## Architecture Overview

```text
React + Vite frontend
        |
        v
FastAPI backend  <---------->  PostgreSQL
        |
        v
Redis broker  <---------->  Celery worker + Celery beat
        |
        v
RSS fetch -> embed -> deduplicate -> rewrite -> rank -> daily digest
```

The API stays responsive because expensive work runs outside request handling. Celery beat triggers the pipeline every 30 minutes, Redis queues the work, and Celery workers handle fetching, embedding, clustering, rewriting, and ranking.

## Data Pipeline

1. **Fetch articles**
   RSS feeds are parsed with `feedparser`. New articles are inserted into PostgreSQL with source, URL, title, summary, topic, and publish time.

2. **Generate embeddings**
   Articles without embeddings are converted into vector representations using `sentence-transformers`. This allows semantic comparison instead of relying only on exact keyword matches.

3. **Deduplicate coverage**
   Recent articles are compared by embedding similarity. Similar stories are grouped into clusters, and one article is marked as the representative item for the digest.

4. **Rewrite when available**
   If `ANTHROPIC_API_KEY` is configured, representative articles can receive clearer rewritten headlines or summaries. Without the key, the app falls back to the original RSS content.

5. **Rank and personalize**
   Articles are scored and selected for the digest. User feedback updates topic weights, so future digests can prioritize topics the user engages with.

## Core Backend Models

- `users`: account records with hashed passwords
- `articles`: fetched stories, embeddings, topic labels, cluster data, ranking score, and digest flags
- `user_feedback`: thumbs-up / thumbs-down style feedback per user and article
- `topic_weights`: per-user topic preference weights used during personalization

## API Highlights

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/auth/signup` | Create an account |
| `POST` | `/auth/login` | Authenticate and receive a JWT |
| `GET` | `/api/digest/today` | Return the current user's personalized digest |
| `POST` | `/api/feedback` | Store feedback and update topic weights |
| `GET` | `/api/articles` | List recently fetched articles |
| `POST` | `/api/pipeline/run` | Manually trigger the news pipeline |
| `GET` | `/health` | Backend health check |

## Frontend Features

- Protected dashboard route
- Login and signup pages
- Daily digest header
- Topic breakdown summary
- Search across loaded headlines
- Article cards with source, topic, score, and reading time
- Feedback actions that help personalize future ranking

## Run Locally With Docker

From the project root:

```bash
docker compose up --build
```

Then open:

- Frontend: `http://localhost:5174`
- Backend health: `http://localhost:8001/health`
- Today's digest: `http://localhost:8001/api/digest/today`

The first digest request may take longer because the app may fetch feeds, download the sentence-transformer model, generate embeddings, deduplicate articles, and rank the initial set.

## Optional Anthropic Rewriting

Khabar runs without an Anthropic key. In that mode, it keeps the original RSS headlines and summaries.

To enable AI-assisted rewriting:

```bash
export ANTHROPIC_API_KEY=your_real_key
docker compose up --build
```

## Manual Pipeline Commands

Trigger a refresh:

```bash
curl -X POST http://localhost:8001/api/pipeline/run
```

Check the digest:

```bash
curl http://localhost:8001/api/digest/today
```

Watch worker logs:

```bash
docker compose logs -f backend celery_worker celery_beat
```

## Engineering Decisions

- **FastAPI** keeps the backend simple, typed, and easy to document.
- **Celery + Redis** moves slow ingestion and ML work out of the request path.
- **PostgreSQL + SQLAlchemy** provide a reliable relational model for articles, users, and feedback.
- **Embeddings** make deduplication semantic, so the app can detect similar stories even when headlines differ.
- **Topic weights** provide a lightweight personalization layer without requiring a complex recommendation system.
- **Docker Compose** makes the full local stack reproducible across API, frontend, database, Redis, and workers.

## Interview Talking Points

- Built an end-to-end full-stack application with asynchronous background processing
- Used semantic embeddings to solve a real product problem: duplicate news coverage
- Designed relational models for users, articles, feedback, and personalization
- Implemented JWT authentication and protected frontend routes
- Balanced graceful fallback behavior by making Anthropic rewriting optional
- Containerized the system so it can run locally with one command

## Future Improvements

- Add Alembic migrations for production-grade schema evolution
- Add automated tests for ranking, deduplication, auth, and API endpoints
- Add observability for failed RSS feeds and Celery jobs
- Cache digest responses for faster repeat loads
- Add source management so users can choose preferred publishers
- Add richer personalization using both topic feedback and reading behavior
