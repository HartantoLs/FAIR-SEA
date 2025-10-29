# Contributing to FAIR-SEA

Thank you for contributing to the FAIR-SEA project! This document outlines the guidelines and workflows for developers.

## Getting Started

Before you begin, please ensure you have followed the main setup instructions in the `README.md` file, including:
1. Cloning the repository.
2. Creating and activating the virtual environment (`venv`).
3. Installing dependencies using `pip install -r requirements.txt`.

## Handling API Keys (Optional)

If your contribution involves features that require API keys (e.g., calling OpenAI):

1.  **Obtain the necessary API Key(s)** securely through designated private channels.
2.  **Create a `.env` file** in the project's root directory (at the same level as `README.md`).
3.  **Add your key(s)** to the `.env` file using the format `VARIABLE_NAME="key_value"`, for example:
    ```
    OPENAI_API_KEY="sk-..."
    ```
    This `.env` file is listed in `.gitignore` and must **never** be committed to the repository.

## Everyday Workflow

### Environment Activation

Before running any code or commands, always activate the virtual environment:
* **On macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```
* **On Windows (PowerShell/CMD):**
    ```powershell
    .\venv\Scripts\activate
    ```
    You should see `(venv)` at the beginning of your terminal prompt.

---
## Adding a New Library (Dependency)

If your changes require a new Python library:

1.  **Activate** the virtual environment.
2.  **Install** the new library:
    ```bash
    pip install <library-name>
    ```
3.  **Update `requirements.txt` immediately:**
    ```bash
    pip freeze > requirements.txt
    ```
4.  **Commit and Push:** Add and commit both your code changes **and** the updated `requirements.txt` file. Use a clear commit message (e.g., `feat: Add matplotlib for visualization`).
5.  **Inform Team:** Let others know they need to run `git pull` and `pip install -r requirements.txt` to sync their environments.

---
## Adding a New Unit Test for CI

Follow these steps when adding new functions to `src/fairsea/` that need automated testing:

1.  **Write Your Function:** Implement your new function in the appropriate `.py` file within `src/fairsea/`.
2.  **Create Test Function:**
    * Navigate to the `tests/` directory.
    * Open or create the relevant test file (e.g., `test_evaluation.py`).
    * Add a new function whose name starts with `test_`.
    * Inside the test function, use `assert` statements to verify your function's behavior with different inputs.
3.  **Test Locally (Recommended):** Run `pytest` in your terminal (with `venv` active) to ensure all tests pass.
4.  **Commit and Push:** Add and commit both the function code and the test code. The CI pipeline on GitHub will automatically run `pytest` to verify. Check the "Actions" tab on GitHub for results.

---
## Branching Strategy

Please follow the GitHub Flow model:
1.  Always create a new **feature branch** from the latest `main` for your work (e.g., `feature/add-new-metric`).
2.  Commit your changes to your feature branch.
3.  When ready, open a **Pull Request (PR)** to merge your branch into `main`.
4.  Assign a teammate for code review.
5.  Ensure all CI checks (linting, testing) pass on the PR.
6.  Once approved and checks pass, merge the PR.
7.  Delete the feature branch after merging.

**Never commit directly to the `main` branch.**

--