# Simplified Python script outline for gpt-unit-tester

import re
from pathlib import Path
from typing import List


# Function to parse TypeScript files and extract import paths
def parse_ts_imports(file_path: Path) -> List[str]:
    """
    Parses a TypeScript file to extract all local import paths.

    Args:
    file_path (Path): The path to the TypeScript file.

    Returns:
    List[str]: A list of import paths.
    """
    imports = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('import'):
                # Simplified import parsing, focusing on local files
                match = re.search(r'from\s+[\'"](.+?)[\'"]', line)
                if match:
                    imports.append(match.group(1))
            if line.startswith('export * from'):
                match = re.search(r'from\s+[\'"](.+?)[\'"]', line)
                if match:
                    imports.append(match.group(1))
    return imports


# Function to inline imported code into a single file
def inline_code(base_path: Path, entry_file: str, scope_name: str = "@aleph-sdk") -> str:
    """
    Inlines the code from the entry file and its imports into a single string, with support for scoped packages/monorepos.

    Args:
    base_path (Path): The base directory path for relative imports.
    entry_file (str): The entry TypeScript file name.
    scope_name (str): The scope name for scoped packages, e.g., "@aleph-sdk".

    Returns:
    str: The inlined code as a single string.
    """
    processed_files = set()  # To avoid processing a file more than once
    code_blocks = []

    def inline_file(file_path: Path):
        if file_path in processed_files:
            return
        processed_files.add(file_path)

        # Assuming local files only, no handling for node_modules or similar
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return

        imports = parse_ts_imports(file_path)
        print(f"Processing {file_path}, imports: {imports}")
        for imp in imports:
            imp_path = None
            if imp.startswith(scope_name):
                # Resolve path for scoped package import
                # Example: @aleph-sdk/core -> packages/core/src
                package_name = imp[len(scope_name) + 1:]  # Remove scope name and slash
                imp_path = base_path / "packages" / package_name / "src" / "index.ts"
            else:
                # Convert relative import path to actual file path
                imp_path = (file_path.parent / imp).with_suffix('.ts')

            inline_file(imp_path)

        with open(file_path, 'r') as file:
            code_blocks.append(f"// Start of {file_path}\n{file.read()}\n// End of {file_path}\n")

    entry_path = base_path / entry_file if not entry_file.startswith(scope_name) else base_path / "packages" / \
                                                                                      entry_file.split('/')[1] / "src" / \
                                                                                      entry_file.split('/')[2]
    inline_file(entry_path)
    return "\n".join(code_blocks)
