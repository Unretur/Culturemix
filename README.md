<div align="center">

# CultureMix

**An AI agent that designs culturally intelligent event concepts.**

Built for the [Qloo Agentic Hackathon 2026](https://qloo.devpost.com/).

**Live demo:** https://culturemix-znjfvxu82zgogdpzegahmd.streamlit.app/

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)

---

## What it does

Enter a city, a budget, and an artist or interest. CultureMix:

1. Searches the Qloo hackathon API for related entities and their tags.
2. Draws a 3D network of those entities, with edges between entities that share a Qloo tag.
3. Asks Gemini to draft an event concept, using only the Qloo entities as grounded recommendations. Anything the model suggests beyond that is labelled as a hypothesis.
4. Checks the plan's JSON structure, and rejects any recommendation marked as Qloo-backed that isn't in the Qloo results.
5. Checks a planning budget, with estimates labelled as estimates.
6. Optionally runs the same brief with no Qloo evidence, so you can compare the two plans side by side.

## How Qloo is used

- Search requests go to `https://hackathon.api.qloo.com/search` with the `X-Api-Key` header.
- The app uses the returned `name`, `entity_id`, `types`, and `tags` fields.
- Connections are formed only from tags Qloo returned. The app never invents a link.
- Results are labelled **Qloo-backed** when they come from Qloo, and **Mock, not Qloo** when no key is set.

## Status

| Component | Status |
|---|---|
| Qloo search (live) | Working. Returns real entities and tags. |
| Shared-tag connections and 3D network | Working. Drawn only from Qloo tags. |
| Event plan with Gemini | Working. Plans are checked before display. |
| Plain-LLM comparison | Working. Runs the same brief without Qloo. |
| Budget check | Working. Costs are planning estimates, not vendor prices. |
| Formal evaluation report | Not built. The comparison is shown in-app, not as a benchmark. |

## Known limitations

- The Qloo search is by entity name. Results depend on how the name matches; a generic phrase such as "independent music" returns weak results. Use an artist name.
- Shared-tag connections appear only when Qloo returns overlapping tags. Some searches will show few or no links.
- Cost figures are planning estimates, not quotes from vendors.
- Gemini's free tier sometimes returns temporary "high demand" errors. The app retries, but you may need to submit again.
- The 3D view loads Three.js from unpkg, so it needs internet access. The 2D diagram is available under the expander.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Put your keys in `.env`:

```
QLOO_API_KEY=your_qloo_key
GEMINI_API_KEY=your_gemini_key
```

Then start the app:

```bash
streamlit run src/app.py
```

Run the tests (they need no keys or network):

```bash
pytest tests/
```

## Project structure

```
src/
  app.py          Streamlit interface
  planner.py      Plan building, validation, and budget checks
  llm.py          Gemini client with retries
  qloo_client.py  Qloo API client and mock adapter
  connections.py  Shared-tag links between Qloo entities
  viz3d.py        3D network view
tests/            Offline unit tests
```

## License

MIT. See [LICENSE](LICENSE).