# 🛡️ VectorGuard: AI Security & RAG Evaluation Framework

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![Security](https://img.shields.io/badge/security-Shift--Left-success.svg)
![Allure](https://img.shields.io/badge/report-Allure-orange.svg)

**VectorGuard** is a Shift-Left security testing framework designed to evaluate and secure **Retrieval-Augmented Generation (RAG)** systems against semantic vulnerabilities, prompt injections, and data leakage.

👉 **[View Live Security Report (Allure)](https://yaniv2809.github.io/vectorguard)**

---

## 🚀 Key Features

* **Synthetic Data Poisoning:** Dynamically generates realistic financial datasets embedded with adversarial payloads — including plain-text, Base64-obfuscated, and multilingual (Hebrew) injections — using **FixtureForge**. The payload library covers encoding-based evasion and language-switch attack vectors.
* **Semantic Tenant Isolation (BOLA):** Penetration testing against Vector Databases (**ChromaDB**) to prove strict metadata filtering overrides semantic similarity in cross-tenant extraction attempts.
* **Zero-Leakage LLM-as-a-Judge:** Utilizes local asynchronous models (**Ollama / Llama 3.2**) to intercept PII exposure and adversarial overrides in real-time, completely bypassing cloud API privacy risks.
* **CI/CD Integrated:** Fully dockerized environment with automated **Allure Security Reports** deployed via GitHub Actions.

---

## 🗺️ OWASP LLM Top 10 Coverage

| OWASP ID | Vulnerability | VectorGuard Test |
|---|---|---|
| **LLM01** | Prompt Injection | `test_context_poisoning.py` — detects direct and Base64-obfuscated injections in retrieved RAG context |
| **LLM02** | Insecure Output Handling | `test_tenant_isolation.py` — validates that ChromaDB metadata filtering prevents cross-tenant data leakage |
| **LLM06** | Sensitive Information Disclosure | `test_pii_leakage.py` — LLM-as-a-Judge scans RAG output for PII (SSN, account numbers) before it reaches the user |

---

## 🏗️ Architecture & Data Flow

1. **Synthesis & Poisoning:** Generates legitimate user data and injects adversarial payloads (plain-text, Base64, Hebrew).
2. **Ingestion:** Embeds text via `all-MiniLM-L6-v2` and strictly isolates metadata in ChromaDB.
3. **Retrieval Simulation:** Simulates cross-tenant queries to test authorization barriers.
4. **AI Interception:** Asynchronous local LLM analyzes the output for threats (`THREAT_DETECTED`) before it reaches the end-user.

---

## 💻 Quick Start (Docker)

You can run the entire security evaluation framework, including the local LLM judge, using Docker.

```bash
# 1. Clone the repository
git clone https://github.com/Yaniv2809/vectorguard.git
cd vectorguard

# 2. Run the security framework
docker-compose up --build
```

> **Note:** The first run will automatically pull the llama3.2 model.

### Run tests locally (no Docker, no Ollama required)

```bash
pip install -e .
pytest                          # unit tests only — runs in seconds
pytest -m integration           # full pipeline tests — requires live Ollama
```

---

## ⚠️ Limitations & Roadmap

This is a **reference implementation** for demonstrating Shift-Left AI security patterns, not a production-hardened tool.

**Current limitations:**
- LLM judge accuracy depends on the quality of the local model (llama3.2). Smaller models may miss subtle injections or produce false positives.
- ChromaDB metadata filtering is a trusted client-side control; in production, tenant isolation must be enforced server-side.
- Integration tests require a locally running Ollama instance and are skipped in automated CI by default (`-m "not integration"`).

**Roadmap:**
- [ ] Adversarial robustness scoring — Precision / Recall / F1 of the judge across payload categories
- [ ] Multi-judge comparison (llama3.2 vs. mistral vs. phi3) with latency benchmarks
- [ ] GitHub Actions workflow with Allure report publishing to GitHub Pages
- [ ] Expand Hebrew and multilingual payload coverage

---

*Developed with a focus on AI Quality Engineering and Data Privacy.*

Architected and developed by [Yaniv2809](https://github.com/Yaniv2809) as part of an End-to-End AI Quality Engineering showcase.
