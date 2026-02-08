# Draw.io AI Architect Agent

This project implements an intelligent AI agent capable of generating Draw.io system architecture diagrams from natural language descriptions. It uses the **Google Agent Development Kit (ADK)** and `gemini-flash-latest` to infer architecture, enforce design patterns, and produce valid `.drawio` XML files.

## 🚀 Features

-   **Natural Language to Diagram**: "Create a Todo App with React and Postgres" -> Generates a full diagram.
-   **Smart Inference**: Automatically splits high-level requests (e.g., "React App") into `frontend` + `backend` components.
-   **Tech Stack Awareness**: Auto-labels components with their runtime (e.g., `[container:node.js]`, `[container:go]`).
-   **System Boundaries**: Intelligently groups internal services inside a dashed boundary, keeping users/external actors outside.
-   **Hybrid Styling**:
    -   **Legacy**: Uses existing white styles for standard components.
    -   **Modern**: Uses a colored style for new/generic services.
-   **Versioning**: Automatically saves diagrams to `architectures/` with version incrementing (e.g., `todo_system_v1.drawio`, `v2...`).

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
uv run python agent.py "Create a system for a 'Travel Planner' app using Next.js and Java, connecting to an Oracle DB. Group them in 'Travel System'."
```

### Output
The agent will generate a `.drawio` file in the `architectures/` directory:
-   `architectures/travel_system_v1.drawio`

You can open this file directly in [draw.io](https://app.diagrams.net/).

## 📂 File Structure

-   **`agent.py`**: The main entry point. Defines the ADK Agent, System Prompt, and Runner. Contains the core logic for architectural inference and layout strategy.
-   **`extractor.py`**: A utility script to parse existing `.drawio` or `.html` files in `sample/` and rebuild `library.json`.
    -   Usage: `uv run python extractor.py sample`
-   **`library.json`**: The database of reusable components (shapes, styles, sizes) extracted from samples.
-   **`tools.py`**: Helper functions called by the agent to list components and generate/save the XML.
-   **`architectures/`**: The output directory where generated diagrams are saved.
-   **`sample/`**: Directory containing reference Draw.io files used to train/populate the library.

## 🧠 How It Works

1.  **Extraction**: `extractor.py` reads styles from `sample/` and saves them to `library.json`.
2.  **Inference**: The Agent processes your prompt, breaking it down into specific components (Web Client, API, DB) and determining their relationships.
3.  **Layout**: It applies strict layout rules:
    -   **Internal** components (APIs, DBs) go inside the System Boundary (Box).
    -   **External** components (Users) stay outside.
4.  **Generation**: `tools.py` constructs the XML, applying the correct styles (Colored for new services, White for legacy) and saves it with a versioned filename.
