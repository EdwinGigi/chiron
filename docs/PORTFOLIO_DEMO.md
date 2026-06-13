# Portfolio Showcase Guide

If you are a developer looking to showcase Chiron on your personal portfolio or resume, you need a way to let recruiters and engineering managers see it in action *without* requiring them to install the App on their own repositories.

## Strategy: The "Buggy Sandbox" Repository

The best way to showcase an autonomous AI agent is to let users deliberately break a sandbox and watch the agent fix it.

### Step-by-step Setup

1. **Create the Demo Repo**: Create a public repository called `chiron-demo` or `chiron-sandbox`.
2. **Install Chiron**: Install your deployed Chiron GitHub App onto this specific repository.
3. **Configure the Repo**: Add a `.chiron.yml` with `fix_strategy: "branch"` so that visitors can clearly see the Pull Requests Chiron opens.
4. **Seed with Bugs**: Create a branch with intentional, obvious bugs:
   - A syntax error.
   - An unused import (Ruff failure).
   - An off-by-one error in a simple sorting algorithm.
5. **Setup GitHub Actions**: Add a simple `.github/workflows/test.yml` that runs `pytest` and `ruff`. This ensures the CI Pipeline Monitoring phase is triggered when the bugs inevitably break the build.

### The Visitor Experience

On your portfolio website, add a "Try it out" button that links to the `chiron-sandbox` repository.

Instruct visitors to:
1. Open a Pull Request from the buggy branch to `main`.
2. Watch as Chiron instantly posts a review identifying the issues.
3. Watch as the GitHub Actions fail.
4. Marvel as Chiron automatically opens a *new* Pull Request titled `Chiron Fixes for PR #X` containing the exact code needed to fix the build.

### Embedding in your Portfolio

You can use the GitHub API to dynamically pull the status of recent Chiron fixes into your portfolio website, or simply record a high-quality GIF/video of the interaction loop to display on the landing page.
