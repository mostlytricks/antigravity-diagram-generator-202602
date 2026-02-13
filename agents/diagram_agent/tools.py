import json
import uuid
import os
import glob
import xml.dom.minidom
import ast

def load_library():
    """Loads the component library from library.json."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        library_path = os.path.join(current_dir, 'library.json')
        with open(library_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def list_components(category=None):
    """
    Lists available components in the library.
    Args:
        category (str, optional): Filter by category (not yet implemented in extraction).
    Returns:
        list: A list of component dictionaries with 'id', 'value', and 'style'.
    """
    library = load_library()
    # Return a simplified view for the agent
    return [{"id": item["id"], "value": item["value"], "style": item["style"]} for item in library]

def get_next_version_filename(prefix):
    """Finds the next version filename in architectures/ directory."""
    base_dir = "architectures"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Sanitize prefix
    safe_prefix = "".join(c for c in prefix if c.isalnum() or c in ('_', '-')).strip()
    if not safe_prefix:
        safe_prefix = "system_architecture"
        
    # Find existing files matching pattern
    pattern = os.path.join(base_dir, f"{safe_prefix}_v*.drawio")
    existing_files = glob.glob(pattern)
    
    # v1.0.0 style versioning
    # Pattern: {prefix}_v{major}.{minor}.{patch}.drawio
    max_major = 1
    max_minor = 0
    max_patch = 0
    
    files = glob.glob(os.path.join(base_dir, f"{safe_prefix}_v*.*.*.drawio"))
    if not files:
        return os.path.join(base_dir, f"{safe_prefix}_v1.0.0.drawio")
        
    for f in files:
        try:
            # Extract version part: ..._v1.0.0.drawio
            base_name = os.path.basename(f)
            version_part = base_name.replace(f"{safe_prefix}_v", "").replace(".drawio", "")
            major, minor, patch = map(int, version_part.split('.'))
            
            # Simple increment logic: just find the latest and increment patch
            if major > max_major:
                max_major, max_minor, max_patch = major, minor, patch
            elif major == max_major and minor > max_minor:
                max_minor, max_patch = minor, patch
            elif major == max_major and minor == max_minor and patch > max_patch:
                max_patch = patch
        except ValueError:
            continue
            
    # Increment patch version
    next_patch = max_patch + 1
    return os.path.join(base_dir, f"{safe_prefix}_v{max_major}.{max_minor}.{next_patch}.drawio")

def apply_auto_layout(components, multiplier=1.0):
    """
    Applies a deterministic grid layout based on component tiers.
    """
    # Define Tiers
    tiers = {
        "User": [],
        "Frontend": [],
        "Gateway": [],
        "Service": [],
        "MessageBus": [],
        "Database": []
    }
    
    # 1. Classify Components
    for comp in components:
        label = comp.get('label', '').lower()
        
        # Priority 1: Explicit Tags
        if '[tier:user]' in label: # Explicit tag for Actors
             tiers["User"].append(comp)
        elif '[tier:frontend]' in label:
             tiers["Frontend"].append(comp)
        elif '[tier:gateway]' in label:
             tiers["Gateway"].append(comp)
        elif '[tier:service]' in label:
             tiers["Service"].append(comp)
        elif '[tier:messagebus]' in label:
             tiers["MessageBus"].append(comp)
        elif '[tier:database]' in label:
             tiers["Database"].append(comp)
        
        # Priority 2: Heuristics (Fallback)
        elif 'user' in label and 'service' not in label and 'api' not in label and 'db' not in label and 'store' not in label:
            # Only classify as User if it's NOT a service/api/db
            tiers["User"].append(comp)
        elif any(keyword in label for keyword in ['actor', 'customer', 'admin', 'client', 'human', 'person']) and 'web-client' not in label:
             # "client" is risky so we exclude "web-client"
            tiers["User"].append(comp)
        elif 'web-client' in label:
            tiers["Frontend"].append(comp)
        elif 'gateway' in label:
            tiers["Gateway"].append(comp)
        elif 'kafka' in label or 'queue' in label or 'bus' in label:
             tiers["MessageBus"].append(comp)
        elif 'db' in label or 'store' in label or 'cache' in label or 'redis' in label or 'sql' in label:
            tiers["Database"].append(comp)
        else:
            # Default to Service if unclassified
            tiers["Service"].append(comp)

    # 2. Assign Coordinates
    # Config - Increased spacing to prevent edge overlap
    start_x = int(50 * multiplier)
    start_y = int(100 * multiplier) # Moved down to make room for title
    row_height = int(250 * multiplier) # Increased from 180
    col_width = int(350 * multiplier) # Increased from 250
    page_width = int(1600 * multiplier) # Wider page
    
    current_y = start_y
    
    # Track min/max for boundary calculation
    min_x, min_y = page_width, page_width
    max_x, max_y = 0, 0
    
    # Order of tiers
    tier_order = ["User", "Frontend", "Gateway", "Service", "MessageBus", "Database"]
    
    for tier_name in tier_order:
        items = tiers[tier_name]
        if not items:
            continue
            
        # Center the row
        row_width = len(items) * col_width
        start_row_x = (page_width - row_width) / 2
        if start_row_x < 50: start_row_x = 50
        
        for i, comp in enumerate(items):
            # Skip Actor/User for boundary calculation (usually outside)
            is_actor = tier_name == "User"
            
            x = int(start_row_x + (i * col_width))
            y = int(current_y)
            
            comp['x'] = x
            comp['y'] = y
            
            # Special resize for databases (make them smaller/standard)
            if tier_name == "Database":
                comp['width'] = 80
                comp['height'] = 80

            # Update bounds if it's inside the system
            if not is_actor:
                width = int(comp.get('width', 120))
                height = int(comp.get('height', 60))
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x + width)
                max_y = max(max_y, y + height)
            
        current_y += row_height

    # 3. Update System Boundary
    padding = int(60 * multiplier)
    boundary_x = min_x - padding
    boundary_y = min_y - padding - int(40 * multiplier) # Extra top padding for title
    boundary_w = (max_x - min_x) + (padding * 2)
    boundary_h = (max_y - min_y) + (padding * 2) + int(40 * multiplier)

    # Find and update boundary component
    for comp in components:
        lib_id = comp.get('library_id', '')
        # Check known boundary IDs or if it was the first generic shape added
        if 'boundary' in str(comp.get('id', '')).lower() or lib_id == 'MUqYMd9_9H_2uWHAdu_l-4':
             comp['x'] = boundary_x
             comp['y'] = boundary_y
             comp['width'] = boundary_w
             comp['height'] = boundary_h
             print(f"DEBUG: Resized System Boundary to x={boundary_x}, y={boundary_y}, w={boundary_w}, h={boundary_h}")

    return components

def generate_drawio_xml(components, edges, filename_prefix="system_architecture", layout_multiplier=1.0, source_prompt=""):
    """
    Generates the Draw.io XML for a given list of components and edges.
    Args:
        components (list): List of component dicts.
        edges (list): List of edge dicts.
        filename_prefix (str): Prefix for the filename.
        layout_multiplier (float): Scale factor for layout (default 1.0).
        source_prompt (str): The original prompt/request to be saved in the archive.
    """
    print(f"DEBUG: generate_drawio_xml called with prefix={filename_prefix}, multiplier={layout_multiplier}, prompt_len={len(source_prompt)}")
    try:
        print(f"DEBUG Components dump: {json.dumps(components)}")
    except:
        print(f"DEBUG Components dump (raw): {components}")
    library = {item["id"]: item for item in load_library()}

    # Basic XML skeleton
    xml_start = '<mxfile host="Electron" agent="Mozilla/5.0" version="24.7.17"><diagram name="Page-1" id="demo-diagram"><mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
    xml_end = '</root></mxGraphModel></diagram></mxfile>'
    
    content_xml = ""
    
    # --- Pre-processing: Parse all components into dicts ---
    parsed_components = []
    for i, comp in enumerate(components):
        if isinstance(comp, str):
            try:
                comp = json.loads(comp)
            except:
                try:
                    comp = ast.literal_eval(comp)
                except:
                    print(f"Warning: Failed to parse component string: {comp[:50]}")
                    continue
        if isinstance(comp, dict):
            parsed_components.append(comp)

    # --- Apply Auto-Layout ---
    parsed_components = apply_auto_layout(parsed_components, multiplier=float(layout_multiplier))

    # Create a map for coordinate lookup (Pre-populated)
    comp_data_map = {str(comp.get('id', f"node_{i}")): comp for i, comp in enumerate(parsed_components)}
    
    # Keep track of generated XML IDs
    node_id_map = {}
    
    for i, comp in enumerate(parsed_components):
        lib_id = comp.get('library_id')
        lib_item = library.get(lib_id)
        if not lib_item:
            continue
            
        new_id = f"node-{uuid.uuid4()}"
        user_id = str(comp.get('id', f"node_{i}"))
        node_id_map[user_id] = new_id
        
        # Override value if provided
        value = comp.get('label', lib_item['value'])
        # Escape XML entities in value
        value = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
        
        style = lib_item['style']
        width = comp.get('width', lib_item['width'])
        height = comp.get('height', lib_item['height'])
        x = comp.get('x', 0)
        y = comp.get('y', 0)
        
        content_xml += f'<mxCell id="{new_id}" value="{value}" style="{style}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" as="geometry"/></mxCell>'

    for edge in edges:
        # Robust parsing: Handle stringified JSON
        if isinstance(edge, str):
            try:
                edge_str = edge
                edge = json.loads(edge)
                print(f"DEBUG: Parsed edge string (JSON): {edge}")
            except:
                try:
                    edge = ast.literal_eval(edge_str)
                    print(f"DEBUG: Parsed edge string (AST): {edge}")
                except Exception as e:
                    print(f"Warning: Failed to parse edge string: {edge_str[:50]}... Error: {e}")
                    continue

        if not isinstance(edge, dict):
            print(f"Warning: Edge is not a dict: {edge}")
            continue

        source_user_id = str(edge.get('source') or edge.get('source_id') or "")
        target_user_id = str(edge.get('target') or edge.get('target_id') or "")
        
        source_id = node_id_map.get(source_user_id)
        target_id = node_id_map.get(target_user_id)
        
        if source_id and target_id:
            edge_id = f"edge-{uuid.uuid4()}"
            value = edge.get('label', '')
            # Escape XML entities in value
            value = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
            
            # Dynamic Port Selection
            style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
            
            src_comp = comp_data_map.get(source_user_id)
            tgt_comp = comp_data_map.get(target_user_id)
            
            if src_comp and tgt_comp:
                try:
                    sx, sy = float(src_comp.get('x', 0)), float(src_comp.get('y', 0))
                    tx, ty = float(tgt_comp.get('x', 0)), float(tgt_comp.get('y', 0))
                    
                    dx = tx - sx
                    dy = ty - sy
                    
                    # Logic: Determine primary direction
                    if abs(dy) > abs(dx) and dy > 0:
                        # Target is clearly BELOW Source
                        # Exit Bottom (0.5, 1) -> Entry Top (0.5, 0)
                        style += "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"
                    elif abs(dy) > abs(dx) and dy < 0:
                         # Target is ABOVE Source
                         style += "exitX=0.5;exitY=0;entryX=0.5;entryY=1;"
                    elif dx > 0:
                        # Target is RIGHT of Source
                        style += "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"
                    else:
                        # Target is LEFT of Source
                        style += "exitX=0;exitY=0.5;entryX=1;entryY=0.5;"
                except:
                    # Fallback if coords are weird
                    style += "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"
            else:
                 # Fallback default
                 style += "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"

            content_xml += f'<mxCell id="{edge_id}" value="{value}" style="{style}" edge="1" parent="1" source="{source_id}" target="{target_id}"><mxGeometry relative="1" as="geometry"/></mxCell>'
            
    raw_xml = xml_start + content_xml + xml_end
    
    # Pretty print
    try:
        dom = xml.dom.minidom.parseString(raw_xml)
        xml_content = dom.toprettyxml()
        
        # Save to file
        filepath = get_next_version_filename(filename_prefix)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_content)
            
        print(f"Successfully saved diagram to {filepath}")
        
        # Save Sidecar Markdown
        # Save Sidecar Markdown
        if source_prompt:
            # Ensure prompts directory exists
            prompts_dir = os.path.join(os.path.dirname(filepath), "prompts")
            if not os.path.exists(prompts_dir):
                os.makedirs(prompts_dir)
                
            # filename: architectures/prompts/prefix_vX.Y.Z.md
            base_name = os.path.basename(filepath).replace('.drawio', '.md')
            md_filepath = os.path.join(prompts_dir, base_name)
            
            with open(md_filepath, "w", encoding="utf-8") as f:
                f.write(f"# Diagram Source Prompt\n\n```text\n{source_prompt}\n```\n")
                f.write(f"\n**Generated Config**:\n- Multiplier: {layout_multiplier}\n- Components: {len(parsed_components)}\n")
                
        return f"Diagram saved to {filepath}"
    except Exception as e:
        print(f"Error pretty printing/saving XML: {e}")
        return raw_xml
