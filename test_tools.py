from tools import list_components, generate_drawio_xml
import json

print("Listing components...")
components = list_components()
print(f"Found {len(components)} components.")
if components:
    print(f"Sample: {components[0]}")

print("\nGenerating XML...")
# Create a simple diagram: User -> Web Client
user_id = components[5]['id'] # "Website User" based on index 5 in library.json viewing
web_client_id = components[1]['id'] # "planner-web-client"

test_components = [
    {'id': 'user', 'library_id': user_id, 'x': 100, 'y': 100, 'label': 'Visitor'},
    {'id': 'web', 'library_id': web_client_id, 'x': 300, 'y': 100}
]

test_edges = [
    {'source': 'user', 'target': 'web', 'label': 'Visits'}
]

xml = generate_drawio_xml(test_components, test_edges)
print(f"Generated XML length: {len(xml)}")
print(f"XML snippet: {xml[:200]}...")

with open('test_output.drawio', 'w', encoding='utf-8') as f:
    f.write(xml)
print("Saved to test_output.drawio")
