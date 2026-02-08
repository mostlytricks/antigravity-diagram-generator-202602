# Diagram Agent Prompting Guideline

To get the most accurate and visually appealing diagrams, follow these structured instructions when interacting with the agent. You can also use this as a **System Prompt** for another LLM that generates requests for this agent.

## 1. Structure of a Perfect Request
A high-quality request should contain four distinct parts:
1.  **System Name**: The overall title of the diagram (used for the boundary).
2.  **Component List**: Explicit names and their **Types/Runtimes** in parentheses.
3.  **Flows & Relationships**: clear `A -> B` or `A calls B` statements.
4.  **Layout Hints**: Instructions on grouping or alignment.

---

## 2. Component Naming & Style Triggers
The agent uses keywords to select the correct shape and color from its library.

| Component Type | Keywords (Case Insensitive) | Style / Shape |
| :--- | :--- | :--- |
| **New Services** | `API`, `Service`, `Worker`, `Module`, `App` | **Blue Tone** (Filled) |
| **Databases** | `DB`, `Database`, `Postgres`, `SQL`, `S3` | **Cylinder** (No Fill) |
| **Queues / Streams** | `Kafka`, `Stream`, `Queue`, `Bus`, `Topic` | **Rotated Cylinder** (No Fill) |
| **External Actors** | `User`, `Customer`, `Client` | **Actor** (Stick figure) |
| **Legacy/Web** | `Web`, `Frontend`, `UI` | **White Box** (Standard) |

### 💡 Pro-Tip: Runtime Hints
Append runtimes in square brackets inside labels for better technical clarity:
*   `Payment Service [container:node.js]`
*   `User DB [RDS/Postgres]`

---

## 3. Defining Flows
Use arrows or explicit verbs. The agent will interpret these to create directed edges.
*   **Good**: `User -> Web App -> API -> Database`
*   **Better**: `User logs in via Web App. Web App calls Auth API. Auth API writes to User DB.`

---

## 4. Influencing the Layout
You can help the agent avoid "spaghetti" lines by suggesting organization:
*   **Grouping**: "Group the services inside the 'Payment System' boundary."
*   **Alignment**: "Place the Database directly below the Service for a clean vertical connection." (Triggers the Top-to-Bottom routing).
*   **Flow Direction**: "Design the flow from Left-to-Right."
*   **Clarity**: "Ensure clear paths and avoid overlapping nodes."

---

## 5. Examples

### ✅ Example: Complex System
> "Create a 'Compliance System'. 
> Components: 'Ingest API' (Service), 'Compliance Stream' (Kafka), 'Audit Archive' (Storage/Postgres), and 'Analyze Module' (Python). 
> Flows: Ingest API publishes to Compliance Stream. Analyze Module consumes from Stream and writes to Audit Archive. 
> Layout: Group everything in 'Compliance System'. Align the Archive DB below the Analyze Module."

### ❌ Example: Vague Request
> "Draw me a system with some apis and a data store."
> *Issues: No specific names, no runtimes, no flow directions.*

---

## 6. Checklist for LLM-Generated Prompts
If you are using another LLM to prompt this agent, ensure it:
- [ ] Assigns a `library_id` category (Service, DB, Queue) to every node.
- [ ] Provides explicit `x, y` coordinates that respect the 800x600 boundary.
- [ ] Places DBs at higher Y coordinates (Vertical drop).
- [ ] Keeps edge labels short (1-3 words).
