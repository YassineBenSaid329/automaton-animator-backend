# Automaton Animator - Backend Engine

![Python Version](https://img.shields.io/badge/python-3.12-blue)
![Framework](https://img.shields.io/badge/Flask-2.0-black)
![Testing](https'img.shields.io/badge/tests-passing-brightgreen)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)

This repository contains the backend service for the Automaton Animator project. It is a robust, production-quality engine for converting regular expressions into their equivalent Nondeterministic Finite Automata (NFA).

The engine is built on a foundation of clean architecture, strict validation, and comprehensive automated testing to ensure correctness and stability.

---

## 🏛️ Core Architecture: A Three-Pass Compiler

The backend is a decoupled REST API built with Flask. The core logic implements a professional, **three-pass compiler architecture** that ensures a perfect Separation of Concerns. This design is highly robust, scalable, and maintainable.

```mermaid
graph TD
    A["Input String<br>'a(b|c)*'"] --> B{"Stage 1: Tokenizer<br>(Lexical Analysis)"};
    B -- "Stream of Tokens" --> D{"Stage 2: Parser<br>(Syntactic Analysis)"};
    D -- "Abstract Syntax Tree (AST)" --> E{"Stage 3: NFA Builder<br>(Semantic Action)"};
    E --> F["✅ Final NFA"];

  

    The Tokenizer: Acts as a strict gatekeeper, converting the raw input string into a categorized stream of tokens and handling implicit concatenation.

    The Parser: Acts as a grammarian, validating the token stream's syntax. Its sole output is an Abstract Syntax Tree (AST), a tree that perfectly represents the expression's logic and precedence.

    The NFA Builder: Acts as the final constructor. It recursively "walks" the validated AST to build the final NFA.

This design separates the "what" (the AST) from the "how" (the NFA), which makes the system incredibly scalable for future features.

✨ Features

    Advanced Regex to NFA Conversion: Implements Thompson's Construction algorithm via a robust AST walker, correctly handling concatenation (ab), union (a|b), Kleene star (a*), and parenthesis scope (()).

    Compiler-Grade Input Validation: The multi-pass architecture provides rigorous validation at each stage, catching invalid characters in the tokenizer and complex grammatical errors (e.g., *a, a|b|) in the parser, providing clear and specific error messages.

    Certified Reliability: The engine's correctness and robustness are guaranteed by a methodical, multi-layered testing suite that includes:

        Unit Tests for each component (Tokenizer, Parser, Builder).

        End-to-End API Integration Tests.

        Property-Based Fuzz Testing with Hypothesis to harden against unexpected failures.

## 🚀 Running the Application

There are two ways to run the server. The Docker method is recommended as it is platform-independent and avoids manual setup.

### Option 1: Using Docker (Recommended for All Platforms)

This is the easiest and most reliable way to run the application. The commands are identical for Windows, macOS, and Linux.

**Prerequisites:**
*   [Docker](https://docs.docker.com/engine/install/) must be installed and running on your system.

**Instructions:**

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd backend
    ```

2.  **Build the Docker image:**
    This command packages the application into a self-contained image named `automaton-animator-backend`.
    ```bash
    docker build -t automaton-animator-backend .
    ```

3.  **Run the Docker container:**
    This starts the application server in the background on port 5000.
    ```bash
    docker run -d -p 5000:5000 --name automaton-backend automaton-animator-backend
    ```

4.  **Verify it's working:**
    Make a test request using `curl` or any API client.
    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{"regex": "a(b|c)*"}' \
      http://127.0.0.1:5000/api/regex-to-nfa
    ```

### Option 2: Local Development Setup (For Contributors)

This method is ideal if you plan to modify the source code or run the test suite directly.

**Prerequisites:**
*   Python 3.12+

**Instructions:**

1.  **Clone the repository and navigate into it.**

2.  **Create a virtual environment:**
    *Note: You may need to use `python` instead of `python3` depending on your system's configuration.*
    ```bash
    python3 -m venv venv
    ```

3.  **Activate the virtual environment:**

    *   **On Windows (PowerShell):**
        ```powershell
        .\venv\Scripts\activate
        ```

    *   **On macOS and Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the Flask development server:**
    ```bash
    python app.py
    ```
    The API will be available at `http://127.0.0.1:5000`.

---

## 🧪 Running the Test Suite

To run all automated tests (requires the local development setup):

```bash
pytest```

---

## 📜 API Reference

### `POST /api/regex-to-nfa`

Converts a regular expression string into an NFA data structure.

**Request Body:**
```json
{
    "regex": "a(b|c)*"
}
```

**✅ 200 OK: Success Response**
```json
{
    "states": ["q0"],
    "alphabet": ["a", "b", "c"],
    "transitions": [ ["q0", "a", "q6"]],
    "start_state": "q0",
    "final_states": ["q1"]
}

**❌ 400 Bad Request: Client Error Response**
```json
{
    "error": "Mismatched parentheses: Missing ')'"
}
```
