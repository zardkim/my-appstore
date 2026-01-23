import os
from pathlib import Path

def create_dummy_fs(tree_output_path: str, base_dir: str):
    """
    Parses a tree-like text file and creates a dummy file system.

    Args:
        tree_output_path (str): Path to the text file containing the tree structure.
        base_dir (str): The root directory where the dummy file system will be created.
    """
    base_dir_path = Path(base_dir)
    base_dir_path.mkdir(parents=True, exist_ok=True)
    print(f"Creating dummy file system under: {base_dir_path}")

    path_stack = [(0, base_dir_path)] # (indent_level, Path_object)

    with open(tree_output_path, 'r', encoding='utf-8') as f:
        # Skip header lines
        # Assuming the first two lines are headers like "Application 볼륨에 대한 폴더 경로의 목록입니다."
        # and "볼륨 일련 번호는 3F41-FB47입니다."
        # and the third line is the root path like "\\NURINET\APPLICATION."
        # We need to handle the root path specially or adjust skipping.
        # Let's skip the first two lines and process the third as the actual root.
        next(f) # Skip "Application 볼륨에 대한 폴더 경로의 목록입니다."
        next(f) # Skip "볼륨 일련 번호는 3F41-FB47입니다."
        
        # The actual root of the tree is the third line, e.g., "\\NURINET\APPLICATION."
        # We don't need to create this as base_dir_path is our root.
        # We'll just start processing from the next line.

        for line_num, line in enumerate(f, start=3): # Start line_num from 3 for debugging
            line = line.rstrip() # Use rstrip to keep leading spaces for indent calculation
            if not line:
                continue

            # Calculate indent level based on leading spaces and tree characters
            # Each level is typically 4 characters (e.g., "    ", "│   ")
            # Find the first non-indent character
            first_char_idx = 0
            while first_char_idx < len(line) and line[first_char_idx] in [' ', '│', '├', '└']:
                first_char_idx += 1
            
            # The actual content starts here
            content = line[first_char_idx:].strip()

            if not content: # Skip lines that are just indentation
                continue

            # Determine indent level based on the position of the content
            # A common pattern is 4 spaces per indent level, or 2 for '├─' / '└─'
            # Let's use the position of the actual content
            current_indent_level = (len(line) - len(line.lstrip('│ '))) // 4 # Assuming 4 chars per indent

            # Adjust path_stack
            while path_stack and path_stack[-1][0] >= current_indent_level:
                path_stack.pop()
            
            if not path_stack: # Should not happen if tree is valid and base_dir is root
                print(f"Warning: Path stack empty for line {line_num}: '{line}'")
                continue

            parent_path = path_stack[-1][1]
            new_item_path = parent_path / content

            if '─' in line[first_char_idx-2:first_char_idx] or not '.' in content: # Heuristic for directory
                new_item_path.mkdir(exist_ok=True)
                path_stack.append((current_indent_level, new_item_path))
            else: # Assume it's a file
                new_item_path.touch() # Create an empty file

    print("Dummy file system created successfully.")

if __name__ == "__main__":
    tree_file = "tree_out1.txt"
    # Use a path that is easily accessible and can be mounted by Docker
    # For local development, /tmp is a good choice.
    # This path will be mapped to /mnt/software inside the backend container.
    dummy_fs_base_path = "/tmp/myappstore_scan_test" 
    
    create_dummy_fs(tree_file, dummy_fs_base_path)
    print(f"Dummy file system created at: {dummy_fs_base_path}")
    print(f"You can now configure your backend to scan '{dummy_fs_base_path}'.")
    print(f"For local backend execution, set SCAN_BASE_PATH='{dummy_fs_base_path}' as an environment variable.")
    print(f"For Docker backend execution, ensure '{dummy_fs_base_path}' is mounted to '/mnt/software' in docker-compose.yml.")
