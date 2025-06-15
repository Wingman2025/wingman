"""Script para actualizar imports de 'models' a 'backend.models.legacy' en scripts."""

import re
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPTS_DIR.parent

def update_imports_in_file(file_path: Path) -> bool:
    """Actualiza imports de models en un archivo. Retorna True si se hicieron cambios."""
    if not file_path.exists() or file_path.suffix != '.py':
        return False
    
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    
    # Patrón para capturar imports de models
    pattern = r'^(\s*)from models import (.+)$'
    
    def replace_import(match):
        indent = match.group(1)
        imports = match.group(2)
        return f'{indent}from backend.models.legacy import {imports}'
    
    # Reemplazar imports
    content = re.sub(pattern, replace_import, content, flags=re.MULTILINE)
    
    # También agregar sys.path si es necesario
    if 'from backend.models.legacy import' in content and 'sys.path' not in content:
        # Agregar al inicio después de imports estándar
        lines = content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                if not line.startswith('from backend'):
                    insert_pos = i + 1
        
        path_setup = [
            '# Ensure project root in sys.path',
            'import sys',
            'from pathlib import Path',
            'PROJECT_ROOT = Path(__file__).resolve().parent.parent',
            'if str(PROJECT_ROOT) not in sys.path:',
            '    sys.path.insert(0, str(PROJECT_ROOT))',
            ''
        ]
        
        lines[insert_pos:insert_pos] = path_setup
        content = '\n'.join(lines)
    
    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        print(f"Updated: {file_path.relative_to(PROJECT_ROOT)}")
        return True
    
    return False

def main():
    """Actualizar todos los scripts en la carpeta scripts/"""
    updated_count = 0
    
    for script_file in SCRIPTS_DIR.glob('*.py'):
        if script_file.name == 'update_imports.py':  # Skip self
            continue
        
        if update_imports_in_file(script_file):
            updated_count += 1
    
    print(f"\nUpdated {updated_count} files.")
    print("Now you can safely delete the legacy shims: app.py and models.py")

if __name__ == '__main__':
    main()
