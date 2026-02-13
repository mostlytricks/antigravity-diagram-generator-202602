from agents.diagram_agent.tools import generate_drawio_xml
import os

def test_boundary_logic():
    print("Testing Boundary Logic with 'Customer' and 'Admin'...")
    
    components = [
        {"id": "c1", "label": "Customer", "library_id": "MUqYMd9_9H_2uWHAdu_l-3"}, # Website User
        {"id": "c2", "label": "Admin Panel [tier:frontend]", "library_id": "1JigugXchFiT3Wg0BkZb-1"}, # Component
        {"id": "c3", "label": "api-core [tier:service]", "library_id": "1JigugXchFiT3Wg0BkZb-1"}, # Component
        {"id": "c4", "label": "System Boundary", "library_id": "MUqYMd9_9H_2uWHAdu_l-4"} # Boundary
    ]
    edges = []
    
    # Generate
    result = generate_drawio_xml(components, edges, filename_prefix="test_boundary_fix", source_prompt="Testing boundary")
    print(result)
    
    # Check the generated file content manually or via parsing would be best, 
    # but for now we rely on the logic printed in tools.py (DEBUG logs)
    # The tool prints: "DEBUG: Resized System Boundary to ..."
    
if __name__ == "__main__":
    test_boundary_logic()
