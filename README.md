# Gogogo Telegram Bot

Telegram client for **Gogogo**: registration, menus, creating ride offers and ride requests, and receiving push-style updates from the backend via a small HTTP webhook.

## Stack

- **Python** 3.12+
- **aiogram** 3.x — long polling for Telegram updates
- **aiohttp** — embedded webhook server (port **8001**) for backend callbacks
- **httpx** — async HTTP client to the Gogogo backend API

## Requirements

- [uv](https://github.com/astral-sh/uv) (recommended)
- A **Telegram Bot token** from [@BotFather](https://t.me/BotFather)
- The **Gogogo backend** reachable at the URL you configure (see below)

## Configuration

Create a `.env` file (or pass variables another way):

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | **Yes** | Telegram bot token |
| `API_BASE_URL` | No | Backend base URL including `/api/v1`. Default: `http://localhost:8000/api/v1` |

The bot fails fast at startup if `BOT_TOKEN` is missing.

## Local development

```bash
cd gogogo-telegram-bot
uv sync
python main.py
```

This starts:

- Telegram **polling** (incoming user messages)
- **Webhook server** on `0.0.0.0:8001` so the backend can POST notifications (e.g. new matching offers)

Run the backend separately (default API port **8000**).

### Docker (local)

From `docker/launch-local.yml`, the compose file maps **8001:8001** and sets `API_BASE_URL` to reach a backend on the host via `host.docker.internal`:

```bash
cd docker
docker compose -f launch-local.yml up --build
```

Ensure your backend is running on the host port you expect (typically 8000).

### Production container

`docker/Dockerfile.prod` runs `python main.py`. Example compose: `docker/launch-prod.yml` (adjust `.env` path and ports for your setup).

**Note:** The GitHub Actions deploy workflow maps host port **8001** to container port **8000**; the application code listens on **8001**. Align container/host ports with how you run the image so the webhook URL and reverse proxy match.

## What the bot does

- **Handlers** under `app/handlers/`: common commands, main menu, registration, ride offers, ride requests
- **`app/services/api_client.py`** — calls the backend (`/users`, `/telegram`, `/rides`, …)
- **`app/webhook.py`** — handles JSON payloads from the backend (e.g. `new_offer_found`, `matches_found_for_request`) and sends messages to users

## Deployment

`.github/workflows/deploy.yml` builds `docker/Dockerfile.prod` on a self-hosted runner and runs the container with a fixed `--env-file` and Docker network. Customize paths and port publishing for your server.
