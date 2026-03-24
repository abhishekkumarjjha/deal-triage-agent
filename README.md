# deal-triage-agent# Deal Triage Agent — AI-Powered CRE Acquisition Screening

> CRE acquisitions teams receive 80–100 OMs weekly. Junior analysts spend 1–2 days per deal just to decide if it's worth modeling. Most deals are eliminated in the first 10 minutes — pure waste. I built this agent to compress that workflow from days to seconds, eliminate the triage bottleneck, and give teams an instant decision layer before underwriting.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python) ![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?logo=streamlit) ![Claude](https://img.shields.io/badge/Claude-Sonnet-6B48FF?logo=anthropic) ![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## The Problem

Acquisitions analysts at institutional CRE firms are bottlenecked at triage. For every 100 OMs that hit their inbox, maybe 5 go to full underwriting. The other 95 get eliminated — but not before someone spends hours reading them.

This agent automates that elimination layer.

---

## What It Does

Upload or paste an Offering Memorandum. The agent:

1. **Extracts key deal parameters** — asset class, location, cap rate, price, occupancy, tenant profile, debt assumptions
2. **Runs a pre-underwriting screen** against configurable acquisition criteria
3. **Generates a GO / SOFT PASS / NO-GO decision** with a numeric score (1–10)
4. **Outputs a bull/bear thesis** in plain English with specific flags for further diligence

**Tested deals:**
| Deal | Score | Decision |
|---|---|---|
| Dollar General — Lockney, TX | 7/10 | ✅ GO |
| Oasis Ave — Twentynine Palms, CA | 5/10 | 🟡 SOFT PASS |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| LLM | Anthropic Claude Sonnet |
| Data I/O | Python (pandas, PyPDF2) |
| Deployment | Local / Streamlit Cloud |

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/abhishekkumarjjha/deal-triage-agent.git
cd deal-triage-agent

# 2. Install dependencies
pip install streamlit anthropic pandas PyPDF2 python-dotenv

# 3. Add your Anthropic API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# 4. Run the app
streamlit run app.py
```

---

## Usage

1. Upload an OM (PDF) or paste deal details into the text input
2. Set your acquisition criteria in the sidebar (cap rate floor, geography, asset class, minimum NOI)
3. Click **Triage Deal**
4. Review the GO/SOFT PASS/NO-GO output, score, and thesis

---

## Project Structure

```
deal-triage-agent/
├── app.py              # Main Streamlit app
├── agent.py            # Claude prompt chain and scoring logic
├── deal_parser.py      # PDF/text extraction utilities
├── criteria.py         # Acquisition criteria configuration
├── sample_deals/       # Test OMs (anonymized)
├── requirements.txt
└── README.md
```

---

## Roadmap

Next workflows in the pipeline:
- **Rent Roll Analyzer** — flag vacancy concentration, lease expiration cliff, tenant credit risk
- **T12 Variance Analyzer** — flag NOI manipulation, expense underreporting, YOY anomalies
- **Broker Email Triage Agent** — auto-classify inbound deal flow by fit before analyst review

---

## Background

Built as a proof-of-work artifact for AI-powered CRE acquisition tooling. I'm a former xAI red teamer (Grok, 64M+ MAU) with an MS in Business Analytics from UT Arlington and prior experience in financial analysis and operations. This agent targets the most wasteful workflow in acquisitions and compresses it to seconds.

---

## Author

**Abhishek Kumar Jha**
AI Safety Researcher · Former xAI Red Teamer · MS Business Analytics, UT Arlington

[LinkedIn](https://linkedin.com/in/abhishekkumarjjha) · [GitHub](https://github.com/abhishekkumarjjha)

---

## License

MIT
