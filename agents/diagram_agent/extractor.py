import json
import html
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
import sys
import os
import glob

class DrawIOHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.mxgraph_data = None

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            attrs_dict = dict(attrs)
            if 'class' in attrs_dict and 'mxgraph' in attrs_dict['class'].split():
                if 'data-mxgraph' in attrs_dict:
                    self.mxgraph_data = attrs_dict['data-mxgraph']

def parse_xml_content(root):
    library = []
    # Find all mxCell elements recursively
    for cell in root.iter('mxCell'):
        cell_id = cell.get('id')
        value = cell.get('value', '')
        style = cell.get('style', '')
        vertex = cell.get('vertex', '0')
        
        # We only care about vertices (nodes) for now, but maybe edges later?
        # The agent primarily needs nodes to place them. 
        if vertex == '1':
            geo = cell.find('mxGeometry')
            width = geo.get('width') if geo is not None else '0'
            height = geo.get('height') if geo is not None else '0'
            x = geo.get('x') if geo is not None else '0'
            y = geo.get('y') if geo is not None else '0'
            
            # Filter out purely structural/empty nodes if they don't look meaningful
            # But let's be inclusive for now to catch the "System Boundary"
            
            item = {
                'id': cell_id,
                'value': value,
                'style': style,
                'width': float(width) if width else 0,
                'height': float(height) if height else 0,
                'x': float(x) if x else 0,
                'y': float(y) if y else 0
            }
            library.append(item)
    return library

def extract_from_html(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        parser = DrawIOHTMLParser()
        parser.feed(content)
        
        if not parser.mxgraph_data:
            print(f"No mxgraph data found in {file_path}")
            return []
            
        data = json.loads(parser.mxgraph_data)
        xml_content = data.get('xml')
        if not xml_content:
            return []
            
        # Try unescaping
        try:
            # Often it's double encoded or just xml string
            unescaped_xml = html.unescape(xml_content)
            root = ET.fromstring(unescaped_xml)
        except ET.ParseError:
            # Fallback
            root = ET.fromstring(xml_content)
            
        return parse_xml_content(root)
    except Exception as e:
        print(f"Error parsing HTML {file_path}: {e}")
        return []

def extract_from_xml(file_path):
    try:
        tree = ET.parse(file_path)
        return parse_xml_content(tree.getroot())
    except Exception as e:
        print(f"Error parsing XML {file_path}: {e}")
        return []

def build_library(sample_dir):
    all_components = []
    seen_ids = set()
    
    print(f"Scanning {sample_dir}...")

    # Process Drawio XML files first
    xml_files = glob.glob(os.path.join(sample_dir, "*.drawio"))
    print(f"Found XML files: {xml_files}")
    for filepath in xml_files:
        print(f"Processing {filepath}...")
        components = extract_from_xml(filepath)
        for comp in components:
            if comp['id'] not in seen_ids:
                all_components.append(comp)
                seen_ids.add(comp['id'])

    # Process HTML files
    html_files = glob.glob(os.path.join(sample_dir, "*.html")) 
    # Also catch .drawio.html if glob didn't match *.html? usually *.html matches .drawio.html
    print(f"Found HTML files: {html_files}")
    for filepath in html_files:
        print(f"Processing {filepath}...")
        components = extract_from_html(filepath)
        for comp in components:
            if comp['id'] not in seen_ids:
                all_components.append(comp)
                seen_ids.add(comp['id'])

    print(f"Extracted {len(all_components)} total components.")
    
    with open('library.json', 'w', encoding='utf-8') as f:
        json.dump(all_components, f, indent=2)
    print("Saved to library.json")

if __name__ == '__main__':
    sample_dir = sys.argv[1] if len(sys.argv) > 1 else 'sample'
    build_library(sample_dir)
