<div align="center">

# CultureMix

**An AI agent that designs culturally intelligent events.**

Built for the [Qloo Agentic Hackathon 2026](https://qloo.devpost.com/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Status](https://img.shields.io/badge/status-in%20development-orange)

[Live demo](#) · [Project description](#project-overview) · [Architecture](#architecture)

</div>

---

## Overview

Event organisers, venues, and brands need to decide which artists, food concepts, and experiences belong together for a specific audience. Popular rankings don't reliably capture that, and a generic language model can produce plausible but unsupported ideas.

CultureMix takes an event brief (city, budget, audience interests) and is designed to:

1. Retrieve cultural entities and affinities from the Qloo API.
2. Use an LLM to turn that evidence into a candidate event concept.
3. Check the concept against the budget.
4. Label every recommendation by its source: Qloo-backed evidence, or an LLM hypothesis.

## Current status

| Component | Status |
|---|---|
| Budget validation (`src/planner.py`) | Implemented, unit tested |
| Qloo API client (`src/qloo_client.py`) | Implemented; endpoint behaviour not yet verified against live responses |
| Streamlit interface (`src/app.py`) | Implemented; shows LIVE or MOCK source on every result |
| Event plan generation (LLM) | In progress |
| Cultural connection graph | Planned |
| Baseline evaluation (CultureMix vs. plain LLM) | Planned |

CultureMix does not yet produce a full event plan. Results are labelled **LIVE (Qloo)** or **MOCK, not Qloo**. Mock output is development data and is never presented as Qloo output.

## Design principles

- **Evidence over assertion.** Recommendations are tied to the source they came from.
- **No invented facts.** Costs are labelled as estimates, not vendor prices. Partnerships and audience statistics are not fabricated.
- **Honest labelling.** Mock and live data are visually distinct throughout the interface.

## Architecture

```
  Event brief (city, budget, interests)
              │
              ▼
  ┌───────────────────────┐        ┌────────────────────────┐
  │ Qloo client           │ ─────▶ │ Qloo hackathon API     │
  │ src/qloo_client.py    │ ◀───── │ hackathon.api.qloo.com │
  └───────────┬───────────┘        └────────────────────────┘
              │ evidence set
              ▼
  ┌───────────────────────┐
  │ Planner               │  budget and schedule checks
  │ src/planner.py        │
  └───────────┬───────────┘
              ▼
  ┌───────────────────────┐
  │ Streamlit interface   │  results labelled LIVE or MOCK
  │ src/app.py            │
  └───────────────────────┘
```

## Getting started

### Requirements

- Python 3.11 or newer
- A Qloo hackathon API key
- An LLM API key (Google Gemini; the free tier is sufficient for development)

### Installation

```bash
git clone https://github.com/Unretur/Culturemix.git
cd Culturemix
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

### Configuration

Copy the example environment file and add your keys:

```bash
copy .env.example .env          # Windows
# cp .env.example .env          # macOS / Linux
```

```
QLOO_API_KEY=your_qloo_key
GEMINI_API_KEY=your_gemini_key
```

Never commit `.env`. It is excluded by `.gitignore`.

### Run

```bash
streamlit run src/app.py
```

Open the URL shown in the terminal (usually `http://localhost:8501`).

### Test

```bash
pytest tests/
```

The tests run offline and do not require API keys.

## Project structure

```
Culturemix/
├── src/
│   ├── app.py            Streamlit interface
│   ├── planner.py        Budget and schedule validation
│   └── qloo_client.py    Qloo API client and mock adapter
├── tests/
│   ├── test_planner.py
│   └── test_qloo_client.py
├── .env.example          Template for required environment variables
├── requirements.txt
├── LICENSE
└── README.md
```

## Qloo API usage

All requests go to the hackathon base URL `https://hackathon.api.qloo.com` and send the key in the `X-Api-Key` header. The key is read from the `QLOO_API_KEY` environment variable and is never logged, displayed, or stored in the repository.

Endpoint paths and parameters are being verified against live responses. Any change from the documented behaviour will be noted here.

## Limitations

- Qloo endpoint behaviour has not yet been confirmed against live responses.
- Cost figures are estimates for planning, not quotes from vendors.
- The planning and evaluation components are still under development.
- Free-tier LLM services can return temporary "high demand" errors; the planner retries these.

## Acknowledgements

- [Qloo](https://www.qloo.com/) for the cultural intelligence API and the hackathon.
- [Streamlit](https://streamlit.io/) for the interface framework.
- [Google Gemini](https://ai.google.dev/) for the language model API.

## License

Copyright (c) 2026 Yash

Licensed under the MIT License. See [LICENSE](LICENSE) for the full text.

```
MIT License

Copyright (c) 2026 Yash

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">
Built for the Qloo Agentic Hackathon 2026
</div>
