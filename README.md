# Diagram Agent System 🤖📐

A Multi-Agent AI system that designs and generates **Draw.io** system architecture diagrams from natural language. It features an interactive Consultant Agent that refines your requirements before checking in with a specialized Diagram Agent to generate the visual output.

## 🚀 Key Features

-   **Multi-Agent Architecture**:
    -   **Consultant Agent**: Acts as a solution architect. It interviews you, proposes a tech stack (e.g., "React + Go + Postgres"), and refines the plan based on your feedback.
    -   **Diagram Agent**: A specialized tool user that deterministicly generates the XML for Draw.io.
-   **Interactive Mode**: The Consultant Agent will *not* generate a diagram until you approve the plan. You can say "No, use Redis instead of Memcached" and it will adapt.
-   **Smart Layouts**:
    -   **Auto-Layout**: Organizes components into functional tiers (User -> Frontend -> Gateway -> Service -> Database).
    -   **Dynamic Boundary**: Automatically calculates and wraps the system components in a boundary box, keeping Actors/Users outside.
    -   **Layout Multiplier**: Ask for a "compact" (80%) or "spacious" (120%) layout to adjust spacing dynamically.
-   **Transparency & Reproducibility**:
    -   **Prompt Archiving**: Every generated diagram (e.g., `twitter_v1.0.0.drawio`) comes with a sidecar Markdown file (`architectures/prompts/twitter_v1.0.0.md`) containing the exact prompts used to generate it.
    -   **Semantic Versioning**: Files are saved with `vX.Y.Z` versioning to track iterations.

## 📂 Project Structure

```
diagram-agent-demo/
├── agents/
│   ├── consultant_agent/     # The high-level architect agent
│   │   └── agent.py
│   └── diagram_agent/        # The specialized tool user
│       ├── agent.py
│       ├── tools.py          # Auto-layout, XML generation, and heuristics
│       └── library.json      # Component library
├── app/
│   └── server.py             # FastAPI server for serving the agents (optional)
├── architectures/            # Generated outputs
│   ├── prompts/              # Sidecar markdown files with prompt history
│   └── *.drawio              # The generated diagram files
├── test_interactive.py       # Script to test the interactive feedback loop
├── test_multi_agent.py       # Script to test the one-shot generation
└── .env                      # API keys
```

## 🛠️ Usage

### Prerequisites
-   Python 3.10+
-   `uv` (recommended) or `pip`
-   Google Gemini API Key

### Setup
1.  Install dependencies:
    ```bash
    uv pip install google-adk python-dotenv
    ```
2.  Set your API key in `.env`:
    ```env
    GOOGLE_API_KEY=your_key_here
    ```

### Interactive Mode (Recommended)
Run the interactive test script to start a session with the Consultant Agent:

```bash
uv run python test_interactive.py
```

**Example Flow:**
1.  **You**: "I need a scalable e-commerce system."
2.  **Agent**: "I suggest a Microservices architecture with React, Python products service, Go order service, and Postgres. Is this okay?"
3.  **You**: "Actually, use a File System instead of Postgres."
4.  **Agent**: "Okay, updated to use Local File Storage. Ready to generate?"
5.  **You**: "Yes."
6.  **System**: Generates `ecommerce_v1.0.0.drawio` and `architectures/prompts/ecommerce_v1.0.0.md`.

### One-Shot Generation
If you want to bypass the conversation and just generate (e.g., for testing), use `test_multi_agent.py`:

```bash
uv run python test_multi_agent.py
```

## 🧪 Testing

The project includes several verification scripts:
-   `test_interactive.py`: Verifies the multi-turn "Proposal -> Feedback -> Action" loop.
-   `test_multi_agent.py`: Verifies the end-to-end flow from specific prompts.
-   `test_multiplier.py`: Verifies the layout scaling feature (e.g., "compact" vs "spacious").

## 🎨 Layout Engine Details

The `tools.py` module implements a deterministic layout engine:
-   **Tiers**: Components are sorted into rows: `User`, `Frontend`, `Gateway`, `Service`, `MessageBus`, `Database`.
-   **Routing**: Heuristics determine the best port for connections (e.g., DBs always connect from Top-Center).
-   **Boundary**: A dynamic algorithm calculates the bounding box of internal components + padding, strictly excluding users/actors.
