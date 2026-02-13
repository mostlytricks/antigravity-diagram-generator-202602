from agents.diagram_agent.agent import run_diagram_agent

if __name__ == "__main__":
    prompt = "Create a Todo App system with React frontend and Python backend."
    print(f"Testing Diagram Agent with prompt: {prompt}")
    result = run_diagram_agent(prompt)
    print("Result:", result)
