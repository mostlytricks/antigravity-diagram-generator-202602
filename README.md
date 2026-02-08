# Draw.io AI Architect Agent

This project implements an intelligent AI agent capable of generating Draw.io system architecture diagrams from natural language descriptions. It uses the **Google Agent Development Kit (ADK)** and `gemini-flash-latest` to infer architecture, enforce design patterns, and produce valid `.drawio` XML files.

## 🚀 Features

-   **Natural Language to Diagram**: "Create a Todo App with React and Postgres" -> Generates a full diagram.
-   **Smart Inference**: Automatically splits high-level requests (e.g., "React App") into `frontend` + `backend` components.
-   **Tech Stack Awareness**: Auto-labels components with their runtime (e.g., `[container:node.js]`, `[container:go]`).
-   **System Boundaries**: Intelligently groups internal services inside a dashed boundary, keeping users/external actors outside.
-   **Semantic Distinction**: Intelligently distinguish between **Streaming** (Kafka/Queues -> Rotated Cylinder) and **Storage** (Databases/Audit Logs -> Standard Cylinder).
-   **Dynamic Edge Routing**: Automatically selects the best connection ports based on relative positions (e.g., Service-to-DB connections use a clean vertical path Exit Bottom -> Entry Top).
-   **Robust Model Interaction**: Fail-safe parsing (JSON + AST) handles variable LLM outputs to ensure diagram generation never fails.
-   **Prompting Guideline**: Includes a [Prompt Guideline](./prompt_guideline.md) for users and other LLMs to maximize generation quality.
-   **Versioning**: Automatically saves diagrams to `architectures/` with version incrementing.

## 🛠️ Setup

1.  **Prerequisites**:
    -   Python 3.10+
    -   `uv` (fast Python package manager)

2.  **Install Dependencies**:
    ```bash
    uv pip install google-adk python-dotenv
    ```

3.  **Environment Variables**:
    Create a `.env` file with your Gemini API key:
    ```env
    GOOGLE_API_KEY=your_api_key_here
    ```

## 📖 Usage

Run the agent via the command line with your prompt:

```bash
uv run python agent.py "Create a Notification System. Components: API, Message Bus (Kafka), Profile DB. Align DB below API."
```

### Output
The agent will generate a `.drawio` file in the `architectures/` directory:
-   `architectures/notification_system_v1.drawio`

Open the output file in [draw.io](https://app.diagrams.net/).

## 🧠 Core Architecture

-   **`agent.py`**: The "brain". Handles architectural inference and layout strategy using Few-Shot prompting.
-   **`extractor.py`**: The "librarian". Parses sample diagrams in `sample/` to populate `library.json` with reusable styles and shapes.
-   **`tools.py`**: The "drafter". Implementation of dynamic routing, coordinate mapping, and XML construction.
-   **`library.json`**: The database of extracted components.
-   **`prompt_guideline.md`**: Best practices for interacting with the agent.
