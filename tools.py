import json
import uuid

def load_library():
    """Loads the component library from library.json."""
    try:
        with open('library.json', 'r', encoding='utf-8') as f:
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

import os
import glob
import xml.dom.minidom

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
    
    max_version = 0
    for f in existing_files:
        try:
            # Extract version number: prefix_v{n}.drawio
            filename = os.path.basename(f)
            # Remove extension
            name_without_ext = os.path.splitext(filename)[0]
            # Split by _v
            parts = name_without_ext.split('_v')
            if len(parts) >= 2 and parts[-1].isdigit():
                version = int(parts[-1])
                if version > max_version:
                    max_version = version
        except:
            continue
            
    next_version = max_version + 1
    return os.path.join(base_dir, f"{safe_prefix}_v{next_version}.drawio")

import ast

def generate_drawio_xml(components, edges, filename_prefix="system_architecture"):
    """
    Generates the Draw.io XML for a given list of components and edges.
    """
    print(f"DEBUG: generate_drawio_xml called with prefix={filename_prefix}, {len(components)} components")
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
        pretty_xml = dom.toprettyxml()
        
        # Save to file
        output_path = get_next_version_filename(filename_prefix)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml)
        print(f"Successfully saved diagram to {output_path}")
        
        return pretty_xml
    except Exception as e:
        print(f"Error pretty printing/saving XML: {e}")
        return raw_xml
