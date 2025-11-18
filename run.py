#!/usr/bin/env python3
import os
import sys
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BUILD_DIR = "build"
LOG_DIR = "logs"
PDF_DIR = "pdfs"
SRC_DIR = "src"
DATA_DIR = "data"
DEPS_DIR = os.path.join(DATA_DIR, "deps")
MAIN_FILES_LIST = os.path.join(DATA_DIR, "main_files.txt")

LATEXMK = "latexmk"
LATEXMK_FLAGS = [
    "-pdf",
    "-shell-escape",
    "-interaction=nonstopmode",
    "-halt-on-error"
]

MAX_WORKERS = 4

STATS = {
    "compiled": 0,
    "skipped": 0,
    "failed": 0,
    "total": 0,
    "start_time": 0,
}

# ================================================================
# Utility helpers
# ================================================================

def ensure_directories():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(DEPS_DIR):
        os.makedirs(DEPS_DIR)

def ensure_output_dirs_for(tex_file):
    """
    Given src/XXX/YYY/file.tex, ensure:
    build/XXX/YYY/
    log/XXX/YYY/
    pdfs/XXX/YYY/
    exist.
    """
    relative = tex_file[len("src/"):]  # remove leading src/
    rel_dir = os.path.dirname(relative)  # XXX/YYY

    build_path = os.path.join(BUILD_DIR, rel_dir)
    log_path = os.path.join(LOG_DIR, rel_dir)
    pdf_path = os.path.join(PDF_DIR, rel_dir)

    os.makedirs(build_path, exist_ok=True)
    os.makedirs(log_path, exist_ok=True)
    os.makedirs(pdf_path, exist_ok=True)

    return build_path, log_path, pdf_path

def is_main_file(filename):
    return filename.endswith("_main.tex")

def read_file(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except:
        return ""

def write_file(path, text):
    with open(path, "w") as f:
        f.write(text)

def append_file(path, text):
    with open(path, "a") as f:
        f.write(text + "\n")

def reset_stats(file_count):
    STATS["compiled"] = 0
    STATS["skipped"] = 0
    STATS["failed"] = 0
    STATS["total"] = file_count
    STATS["start_time"] = time.time()

def print_summary():
    duration = time.time() - STATS["start_time"]

    print("\n=====================================")
    print(" Build Summary")
    print("=====================================")
    print(f"  Total files: {STATS['total']}")
    print(f"  Compiled:    {STATS['compiled']}")
    print(f"  Skipped:     {STATS['skipped']}")
    print(f"  Failed:      {STATS['failed']}")
    print(f"  Time:        {duration:.2f} seconds")
    print("=====================================\n")

def clean_all():
    print("Cleaning build/, log/, and pdfs/...")

    for directory in [BUILD_DIR, LOG_DIR, PDF_DIR]:
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory):
                for f in files:
                    os.remove(os.path.join(root, f))

    print("Clean complete.")


# ================================================================
# Step 1: Find all *_main.tex files
# ================================================================

def find_main_files():
    ensure_directories()
    main_files = []

    for root, dirs, files in os.walk(SRC_DIR):
        for f in files:
            if is_main_file(f):
                full = os.path.join(root, f)
                main_files.append(full)

    write_file(MAIN_FILES_LIST, "")
    for f in main_files:
        append_file(MAIN_FILES_LIST, f)

    print(f"Found {len(main_files)} main files.")
    return main_files

# ================================================================
# Step 2: Create simple dependency tree
# ================================================================

def extract_dependencies(tex_path):
    deps = []
    content = read_file(tex_path)

    # look for \input{...} and \include{...}
    for line in content.splitlines():
        line = line.strip()

        if line.startswith("\\input{") and "}" in line:
            dep = line.split("{")[1].split("}")[0]
            deps.append(dep)

        if line.startswith("\\include{") and "}" in line:
            dep = line.split("{")[1].split("}")[0]
            deps.append(dep)

    return deps

def create_deps_tree():
    ensure_directories()

    if not os.path.exists(MAIN_FILES_LIST):
        print("No main_files.txt found. Run --find-files first.")
        return

    main_files = read_file(MAIN_FILES_LIST).splitlines()

    for mf in main_files:

        # Extract subject tag:
        # Example: src/HAI722I/tds/td_main.tex â†’ HAI722I
        parts = mf.split(os.sep)
        tag = "UNKNOWN"
        for p in parts:
            if p.startswith("HAI") and len(p) >= 7:  # very simple pattern
                tag = p
                break

        # Extract filename
        base = os.path.basename(mf)

        # Construct output filename WITH tag to avoid collisions
        # Example: HAI722I_td_main.tex.deps
        deps_filename = f"{tag}_{base}.deps"

        out_path = os.path.join(DEPS_DIR, deps_filename)

        deps = extract_dependencies(mf)

        write_file(out_path, "")
        for d in deps:
            append_file(out_path, d)

        print(f"Deps for {mf}: {len(deps)} entries â†’ {deps_filename}")

# ================================================================
# Step 3: Compile a LaTeX file
# ================================================================

def compile_file(tex_file):
    print(f"\nCompiling {tex_file}")

    # Determine output folders
    build_path, log_path, pdf_path = ensure_output_dirs_for(tex_file)

    file_dir = os.path.dirname(tex_file)
    file_name = os.path.basename(tex_file)

    # Prepare absolute paths for latexmk
    abs_build = os.path.abspath(build_path)

    # Build command with output redirection
    cmd = (
        f"{LATEXMK} "
        f"{' '.join(LATEXMK_FLAGS)} "
        f"-auxdir=\"{abs_build}\" "
        f"-outdir=\"{abs_build}\" "
        f"\"{file_name}\" "
    )

    # cd into source directory
    cwd = os.getcwd()
    os.chdir(file_dir)

    # Run latexmk silently, save log
    exit_code = os.system(f"{cmd} > _latexmk_output.txt 2>&1")

    if exit_code != 0:
        print(f"  Compilation failed for {tex_file} (exit code {exit_code})")
        STATS["failed"] += 1
        os.chdir(cwd)
    else:
        print(f"  Compilation succeeded for {tex_file}")
        STATS["compiled"] += 1

    # Move latexmk's own log file
    os.chdir(cwd)
    shutil.move(os.path.join(file_dir, "_latexmk_output.txt"),
                os.path.join(log_path, file_root(tex_file) + ".log"))

    # Move generated files from build/
    move_build_outputs(tex_file, build_path, log_path, pdf_path)

def file_root(tex_file):
    return os.path.basename(tex_file).replace(".tex", "")


def move_build_outputs(tex_file, build_path, log_path, pdf_path):
    root = file_root(tex_file)

    # Look inside build_path
    for f in os.listdir(build_path):
        if not f.startswith(root):
            continue

        src = os.path.join(build_path, f)

        if f.endswith(".pdf"):
            shutil.move(src, os.path.join(pdf_path, f))

        elif f.endswith(".log"):
            shutil.move(src, os.path.join(log_path, f))

        else:
            # Leave other in build folder
            pass


# ================================================================
# Step 4: Build logic
# ================================================================

def load_main_files():
    if not os.path.exists(MAIN_FILES_LIST):
        print("No main_files.txt found: run --find-files first.")
        return []
    return read_file(MAIN_FILES_LIST).splitlines()

def build_needed():
    main_files = load_main_files()
    if not main_files:
        print("No main files found: run --initial first.")
        return

    reset_stats(len(main_files))

    files_to_compile = []

    for mf in main_files:
        _, _, pdf_path = ensure_output_dirs_for(mf)
        pdf_file = os.path.join(pdf_path, os.path.basename(mf).replace(".tex", ".pdf"))

        if not os.path.exists(pdf_file):
            print(f"PDF missing: rebuild {mf}")
            files_to_compile.append(mf)
        else:
            # compare timestamps properly
            if os.path.getmtime(mf) > os.path.getmtime(pdf_file):
                print(f"Source newer: rebuild {mf}")
                files_to_compile.append(mf)
            else:
                print(f"{mf} is up to date.")
                STATS["skipped"] += 1
        
    if files_to_compile:
        compile_with_progress(files_to_compile)
    print_summary()

def rebuild_all():
    main_files = load_main_files()
    if not main_files:
        return

    reset_stats(len(main_files))

    print("Deleting all PDFs from build dir...")

    for mf in main_files:
        build_path, _, _ = ensure_output_dirs_for(mf)
        root = file_root(mf)

        for f in os.listdir(build_path):
            if f.startswith(root) and f.endswith(".pdf"):
                os.remove(os.path.join(build_path, f))

    # Recompile everything
    files_to_compile = main_files
    if files_to_compile:
        compile_with_progress(files_to_compile)
    print_summary()

def compile_with_progress(files_to_compile):
    """
    Compiles multiple files in parallel with simple progress updates.
    
    How it works:
    1. Creates a ThreadPoolExecutor to run multiple compilations at once
    2. Submits all files to be compiled
    3. Prints updates as each file finishes
    4. Collects results and updates statistics
    """
    if not files_to_compile:
        return

    total = len(files_to_compile)
    completed = 0

    # Create a thread pool that can run MAX_WORKERS compilations at once
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        
        # Submit all files for compilation
        # This creates "futures" - promises of future results
        future_to_file = {
            executor.submit(compile_file, mf): mf 
            for mf in files_to_compile
        }
        
        # as_completed() gives us results as each compilation finishes
        for future in as_completed(future_to_file):
            tex_file = future_to_file[future]
            completed += 1
            
            try:
                # Get the result (True if success, False if failed)
                success = future.result()
                
                if success:
                    STATS["compiled"] += 1
                    print(f"  [{completed}/{total}] O {os.path.basename(tex_file)}")
                else:
                    STATS["failed"] += 1
                    print(f"  [{completed}/{total}] X {os.path.basename(tex_file)} FAILED")
                    
            except Exception as e:
                # If something went wrong during compilation
                STATS["failed"] += 1
                print(f"  [{completed}/{total}] XXX {os.path.basename(tex_file)} ERROR: {e}")





# ================================================================
# Step 5: CLI handling
# ================================================================

def main():
    ensure_directories()

    if len(sys.argv) == 1:
        # default: incremental build
        build_needed()
        return

    arg = sys.argv[1]

    if arg == "--rebuild-all":
        rebuild_all()
    elif arg == "--initial":
        find_main_files()
        create_deps_tree()
    elif arg == "--find-files":
        find_main_files()
    elif arg == "--create-deps-tree":
        create_deps_tree()
    elif arg == "--clean":
        clean_all()
    elif arg == "--help" or arg == "-h" or arg == "?":
        print("Usage: python run.py [option]")
        print("Options:")
        print("  --rebuild-all         Rebuild all main files")
        print("  --initial             Find main files and create dependency tree")
        print("  --find-files          Find all main files")
        print("  --create-deps-tree    Create dependency tree for main files")
        print("  --clean               Clean build, log, and pdf directories")
        print("  --help, -h, ?         Show this help message")
    else:
        print("Unknown option:", arg)
        print("Valid options:")
        print("  --rebuild-all")
        print("  --initial")
        print("  --find-files")
        print("  --create-deps-tree")
        print("  --clean")
        print("  --help, -h, ?")

if __name__ == "__main__":
    main()
