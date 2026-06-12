# Chiron 🐴 — Autonomous CI/CD Code Review & Remediation Agent

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Chiron is an autonomous GitHub App that not only reviews your pull requests but actively monitors your CI/CD pipelines, diagnoses failures, and automatically writes the code to fix them. Powered by Google Gemini and built on FastAPI.

## Features

- 🕵️‍♂️ **Intelligent PR Review**: Multi-dimensional analysis (correctness, performance, security) using Google Gemini.
- 🛠️ **Autonomous Remediation**: Automatically generates and pushes fixes for detected issues or CI failures.
- 🔄 **Self-Correction Loop**: Validates patches before applying them, running a loop of fix → test → retry.
- 🔀 **Flexible Branching**: Choose to push fixes directly to the working branch or create an isolated fix PR.
- ⚡ **Async Native**: Built with FastAPI and githubkit for high-performance webhook processing.

## Quick Start

### 1. Install Dependencies
```bash
pip install -e '.[dev]'
```

### 2. Configure Environment
Copy `.env.example` to `.env` and fill in your GitHub App credentials and Gemini API key.
```bash
cp .env.example .env
```

### 3. Run Locally
```bash
make dev
```
Alternatively, use Docker Compose:
```bash
make docker-up
```

## How It Works

1. **Listen**: Webhook receiver listens to PR and Workflow Run events.
2. **Review**: Gemini-2.5-flash triages, then Gemini-2.5-pro performs deep review and chunked analysis.
3. **Fix**: Agentic workflow creates unified patches, verifies syntax/lint, and pushes the commit.
4. **Verify**: Chiron monitors the subsequent CI run to ensure the fix was successful.

## Configuration

Place a `.chiron.yml` file in the root of the repository you install the app on to configure its behavior (e.g. `fix_strategy: "branch"`).

## Architecture

* Fastapi Webhook Receiver -> githubkit -> Queue -> LLM Review Agent -> Patch Generator -> Pre-Commit Validator -> GitHub GraphQL API.

## Why "Chiron"?

Named after Chiron, the wise centaur of Greek mythology who mentored heroes. This agent acts as a wise mentor for your codebase.

## License

MIT
