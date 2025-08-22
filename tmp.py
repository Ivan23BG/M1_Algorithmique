import os

# Repo structure definition
structure = {
    "pdfs": {
        # Example course folders, add/remove as needed
        "HAI702I": {"cours": [], "tds": []},
        "HAI703I": {"cours": [], "tds": []},
        "HAI709I": {"cours": [], "tds": []},
        "HAI710I": {"cours": [], "tds": []},
        "HAI711I": {"cours": [], "tds": []},
        "HAI713I": {"cours": [], "tds": []},
        "HAI718I": {"cours": [], "tds": []},
        "HAI720I": {"cours": [], "tds": []},
        "HAI722I": {"cours": [], "tds": []},
    }
}

def create_structure(base_path, tree):
    for name, content in tree.items() if isinstance(tree, dict) else []:
        path = os.path.join(base_path, name)
        os.makedirs(path, exist_ok=True)

        # Recurse if subfolders
        if isinstance(content, dict):
            create_structure(path, content)
        # If it's just a list, make empty dirs
        elif isinstance(content, list):
            pass

        # Add .gitkeep for empty dirs
        gitkeep = os.path.join(path, ".gitkeep")
        if not os.path.exists(gitkeep):
            with open(gitkeep, "w") as f:
                f.write("")

if __name__ == "__main__":
    base_dir = "."  # current folder
    create_structure(base_dir, structure)

    # Create placeholder files
    for filename in ["CONTRIBUTING.md", "LICENSE"]:
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write(f"# {filename}\n\nTODO: Fill this file.\n")

    print("Repository structure created successfully.")
