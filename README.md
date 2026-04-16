# 🛡️ VectorGuard

**Enterprise-Grade AI Red-Teaming Framework & Privacy Gateway for RAG Systems.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![ChromaDB](https://img.shields.io/badge/Vector%20DB-Chroma-FF4B4B.svg)](https://trychroma.com/)
[![FixtureForge](https://img.shields.io/badge/Data-FixtureForge-2ea44f.svg)](https://pypi.org/project/fixtureforge/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Overview
Retrieval-Augmented Generation (RAG) systems introduce complex security vulnerabilities, particularly around Context Poisoning and Broken Object Level Authorization (BOLA). **VectorGuard** is a "Shift-Left" automated security evaluation framework designed to exploit and secure these systems before they reach production. 

It simulates advanced semantic attacks, validates database-level tenant isolation, and enforces strict PII remediation policies using a local LLM-as-a-Judge architecture.

## ✨ Core Capabilities

* **🧬 Synthetic Data Poisoning:** Leverages [FixtureForge](https://pypi.org/project/fixtureforge/) to dynamically generate highly realistic financial datasets embedded with hidden Prompt Injections and malicious payloads.
* **🧱 Semantic Tenant Isolation (BOLA Testing):** Executes sophisticated authorization bypass attacks against Vector Databases (ChromaDB), proving that semantic similarity does not override metadata access controls.
* **⚖️ Local LLM-as-a-Judge (Zero-Leakage):** Utilizes asynchronous, local evaluation via Ollama (Llama 3) to scan system outputs for sensitive PII (SSN, Account Numbers) without ever sending corporate data to third-party cloud APIs.
* **⚡ Asynchronous Evaluation Engine:** Built on `asyncio` and `aiohttp` to support high-throughput, parallel red-teaming tests in CI/CD pipelines.

## 🏗️ Architecture Stack

```text
VectorGuard/
├── .github/workflows/       # CI/CD pipelines for automated security testing
├── configs/                 # YAML-first configurations & payload libraries
├── core/                    # Core engines (Async LLM Client, Vector DB Manager)
├── data_forge/              # Data generation and context poisoning logic
└── tests/                   # Pytest suite (Arrange-Act-Assert methodology)
```

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have **Python 3.11+** installed and a local instance of **Ollama** running.

### 2. Installation
Clone the repository and install the framework in editable mode:
```bash
git clone [https://github.com/Yaniv2809/VectorGuard.git](https://github.com/Yaniv2809/VectorGuard.git)
cd VectorGuard
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -e .
```

### 3. Start the Evaluation Engine
Ensure your local Llama 3 model is running in the background. This model acts as the zero-leakage security judge:
```bash
ollama run llama3.2
```

### 4. Run the Security Suite
Execute the automated red-teaming tests using Pytest:
```bash
pytest tests/ -v -s
```

## 🎯 Threat Vectors Addressed

### 1. The BOLA Attack (Tenant Isolation)
VectorGuard generates a legitimate record for `Tenant A` and a poisoned record for `Tenant B`. It then executes a highly relevant semantic query on behalf of `Tenant B` attempting to extract `Tenant A`'s confidential data. The framework verifies that the RAG infrastructure's metadata filtering successfully blocks the intrusion.

### 2. The PII Leakage Attack
Simulates a scenario where the RAG system accidentally hallucinates or retrieves raw personal identifiable information (PII). VectorGuard's local judge evaluates the output in real-time, enforcing a strict zero-tolerance policy for sensitive data exposure.

---
*Developed with a focus on AI Quality Engineering and Data Privacy.*
