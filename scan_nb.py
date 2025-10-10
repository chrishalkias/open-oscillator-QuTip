import json
import os
import re
import subprocess

def extract_imports_from_notebook(notebook_path):
    """Extract imports from Jupyter notebook"""
    imports = set()
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        try:
            notebook = json.load(f)
        except json.JSONDecodeError:
            return imports
    
    # Extract from code cells
    for cell in notebook.get('cells', []):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            # Find import statements
            matches = re.findall(r'^(?:import|from)\s+(\w+)', source, re.MULTILINE)
            imports.update(matches)
    
    return imports

def get_package_version(package):
    """Get installed version of a package"""
    try:
        result = subprocess.run([
            'pip', 'show', package
        ], capture_output=True, text=True, check=True)
        
        for line in result.stdout.split('\n'):
            if line.startswith('Version:'):
                return line.split(':')[1].strip()
    except:
        return None
    
    return None

def main():
    all_imports = set()
    
    # Scan all .ipynb files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.ipynb'):
                notebook_path = os.path.join(root, file)
                imports = extract_imports_from_notebook(notebook_path)
                all_imports.update(imports)
                print(f"Scanned {notebook_path}: found {len(imports)} imports")
    
    # Write to requirements.txt
    with open('requirements.txt', 'w') as f:
        for package in sorted(all_imports):
            version = get_package_version(package)
            if version:
                f.write(f"{package}=={version}\n")
            else:
                f.write(f"{package}\n")
    
    print(f"Generated requirements.txt with {len(all_imports)} packages from notebooks")

if __name__ == "__main__":
    main()