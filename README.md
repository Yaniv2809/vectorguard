# 🛡️ VectorGuard: AI Security & RAG Evaluation Framework

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![Security](https://img.shields.io/badge/security-Shift--Left-success.svg)
![Allure](https://img.shields.io/badge/report-Allure-orange.svg)

**VectorGuard** is an automated Shift-Left security testing framework designed to evaluate and secure **Retrieval-Augmented Generation (RAG)** systems against semantic vulnerabilities, prompt injections, and data leakage.

👉 **[View Live Security Report (Allure)](https://yaniv2809.github.io/vectorguard)**

---

## 🚀 Key Features

* **Synthetic Data Poisoning:** Dynamically generates highly realistic financial datasets embedded with adversarial payloads (Base64 obfuscated Prompt Injections) using **FixtureForge**.
* **Semantic Tenant Isolation (BOLA):** Penetration testing against Vector Databases (**ChromaDB**) to prove strict Metadata Filtering overrides semantic similarity.
* **Zero-Leakage LLM-as-a-Judge:** Utilizes local asynchronous models (**Ollama / Llama 3.2**) to intercept PII exposure and adversarial overrides in real-time, completely bypassing cloud API privacy risks.
* **Enterprise CI/CD Ready:** Fully dockerized environment with automated **Allure Security Reports** deployed via GitHub Actions.

---

## 🏗️ Architecture & Data Flow

1. **Synthesis & Poisoning:** Generates legitimate user data and injects adversarial payloads.
2. **Ingestion:** Embeds text via `all-MiniLM-L6-v2` and strictly isolates metadata in ChromaDB.
3. **Retrieval Simulation:** Simulates cross-tenant queries to test Authorization barriers.
4. **AI Interception:** Asynchronous Local LLM analyzes the output for threats (`THREAT_DETECTED`) before it reaches the end-user.

---

## 💻 Quick Start (Docker)

You can run the entire security evaluation framework, including the local LLM judge, using Docker.

```bash
# 1. Clone the repository
git clone [https://github.com/Yaniv2809/vectorguard.git](https://github.com/Yaniv2809/vectorguard.git)
cd vectorguard

# 2. Run the security framework
docker-compose up --build
*Developed with a focus on AI Quality Engineering and Data Privacy.*

Note: The first run will automatically pull the llama3.2 model.

Architected and developed by Yaniv2809 as part of an End-to-End AI Quality Engineering showcase.
