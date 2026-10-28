# CultureMix

An AI agent that designs culturally intelligent event concepts for a specific city, audience, and budget, using Qloo's cultural intelligence API.

Built for the Qloo Agentic Hackathon 2026.

## Status

This is an early build. Here is what is and isn't working:

- **Working and tested:** budget check logic (`src/planner.py`), with unit tests in `tests/`.
- **Written, not yet verified:** the Qloo client (`src/qloo_client.py`). Endpoint paths and parameters have not been checked against a live response. Until they are, Qloo output is not treated as real.
- **Not yet built:** event plan generation, cultural connection graph, baseline comparison.

The app labels every result as **LIVE (Qloo)** or **MOCK, not Qloo**. Mock output is development data and is never presented as Qloo results.

## How Qloo is used

The app sends search requests to the Qloo hackathon API (`https://hackathon.api.qloo.com`) with the `X-Api-Key` header. The key is read from the `QLOO_API_KEY` environment variable and is never stored in the repository.

## How cost figures are handled

Costs shown in the budget check are estimates, not vendor prices. The app does not look up real prices for venues or artists.

## Setup

Requires Python 3.11 or newer.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and set `QLOO_API_KEY` to your hackathon key. Never commit `.env`.

## Run

```bash
streamlit run src/app.py
```

## Test

```bash
pytest tests/
```

## Project layout
