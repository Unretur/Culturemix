# CultureMix

An agent that designs culturally intelligent events, grounded in Qloo's cultural intelligence API.

Built for the Qloo Agentic Hackathon 2026.

## Status

Early skeleton. Qloo endpoint paths are not yet verified against a live response. The app labels every result as LIVE or MOCK.

## Run locally

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    copy .env.example .env
    streamlit run src/app.py

Put your real key in `.env`. Never commit `.env`.

Run tests with `pytest tests/`.

## License

MIT. See `LICENSE`.
