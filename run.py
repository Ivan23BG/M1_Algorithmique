#!/usr/bin/env python3
import os
import sys
import shutil
import time
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

BUILD_DIR = "build"
LOG_DIR = "logs"
PDF_DIR = "pdfs"
SRC_DIR = "src"
DATA_DIR = "data"
DEPS_DIR = os.path.join(DATA_DIR, "deps")
MAIN_FILES_LIST = os.path.join(DATA_DIR, "main_files.txt")
FIGURE_FILES_LIST = os.path.join(DATA_DIR, "figure_files.txt")

LATEXMK = "latexmk"
LATEXMK_FLAGS = [
    "-pdf",
    "-shell-escape",
    "-interaction=nonstopmode",
    "-halt-on-error"
]

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
    for d in [DATA_DIR, DEPS_DIR]:
        os.makedirs(d, exist_ok=True)

def ensure_output_dirs_for(tex_file, is_figure=False):
    """
    Given src/XXX/YYY/file.tex, ensure:
    build/XXX/YYY/ or build/XXX/figures/
    logs/XXX/YYY/ or logs/XXX/figures/
    pdfs/XXX/YYY/ or pdfs/XXX/figures/
    exist.
    """
    relative = tex_file[len("src/"):]
    
    if is_figure:
        # Extract module name (first directory after src/)
        parts = relative.split(os.sep)
        module = parts[0]
        rel_dir = os.path.join(module, "figures")
    else:
        rel_dir = os.path.dirname(relative)

    build_path = os.path.join(BUILD_DIR, rel_dir)
    log_path = os.path.join(LOG_DIR, rel_dir)
    pdf_path = os.path.join(PDF_DIR, rel_dir)

    os.makedirs(build_path, exist_ok=True)
    os.makedirs(log_path, exist_ok=True)
    os.makedirs(pdf_path, exist_ok=True)

    return build_path, log_path, pdf_path

def is_main_file(filename):
    return filename.endswith("_main.tex")

def is_tikz_file(filepath):
    return "/assets/tikz/" in filepath and filepath.endswith(".tex")

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def write_file(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def append_file(path, text):
    with open(path, "a", encoding="utf-8") as f:
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
    print("Cleaning build/, logs/, and pdfs/...")

    for directory in [BUILD_DIR, LOG_DIR, PDF_DIR]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            os.makedirs(directory, exist_ok=True)

    print("Clean complete.")

def file_root(tex_file):
    return os.path.basename(tex_file).replace(".tex", "")

# ================================================================
# Step 1: Find all main and figure files
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

def find_figure_files():
    ensure_directories()
    figure_files = []

    for root, dirs, files in os.walk(SRC_DIR):
        # Split the path to check the structure more precisely
        parts = root.split(os.sep)
        if len(parts) >= 4 and parts[-2] == "assets" and parts[-1] == "tikz":
            for f in files:
                if f.endswith(".tex"):
                    full = os.path.join(root, f)
                    figure_files.append(full)

    write_file(FIGURE_FILES_LIST, "")
    for f in figure_files:
        append_file(FIGURE_FILES_LIST, f)

    print(f"Found {len(figure_files)} TikZ figure files.")
    
    # Debug output
    if figure_files:
        print("First 5 figure files:")
        for f in figure_files[:5]:
            print(f"  - {f}")
    else:
        print("No figure files found. Current directory structure:")
        for root, dirs, files in os.walk(SRC_DIR):
            if "assets" in root:
                print(f"  Found assets directory: {root}")
                if "tikz" in dirs:
                    print(f"    -> Contains tikz subdirectory!")
    
    return figure_files
# ================================================================
# Step 2: Create simple dependency tree
# ================================================================

def extract_dependencies(tex_path):
    deps = []
    content = read_file(tex_path)

    for line in content.splitlines():
        line = line.strip()

        if line.startswith("\\input{") and "}" in line:
            dep = line.split("{")[1].split("}")[0]
            deps.append(dep)

        if line.startswith("\\include{") and "}" in line:
            dep = line.split("{")[1].split("}")[0]
            deps.append(dep)
        
        # Track figure dependencies
        if line.startswith("\\includegraphics") and "}" in line:
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
        parts = mf.split(os.sep)
        tag = "UNKNOWN"
        for p in parts:
            if p.startswith("HAI") and len(p) >= 7:
                tag = p
                break

        base = os.path.basename(mf)
        deps_filename = f"{tag}_{base}.deps"
        out_path = os.path.join(DEPS_DIR, deps_filename)

        deps = extract_dependencies(mf)

        write_file(out_path, "")
        for d in deps:
            append_file(out_path, d)

        print(f"Deps for {mf}: {len(deps)} entries → {deps_filename}")

# ================================================================
# Step 3: Figure compilation with wrapper template
# ================================================================

def create_figure_wrapper(tikz_file, temp_dir):
    """
    Creates a standalone wrapper document for the TikZ figure.
    Reads the TikZ content and embeds it directly in the wrapper.
    """
    # Extract module path
    parts = tikz_file.split(os.sep)
    module_idx = parts.index("src") + 1
    module = parts[module_idx]
    
    # Read the actual TikZ content
    tikz_content = read_file(tikz_file)
    print(f"DEBUG: TikZ content from {tikz_file}:")
    print("--- START ---")
    print(tikz_content)
    print("--- END ---")
    
    # Build the wrapper with the TikZ content embedded
    wrapper_content = r"""\documentclass[tikz,border=0.5mm]{standalone}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{tikz}
\usetikzlibrary{arrows,positioning,shapes,calc,patterns}

% Include common headers
\input{../../common/common_header.tex}
\input{../../common/macros/math.tex}
\input{../../common/macros/theorems.tex}
% Include module-specific header if it exists
\InputIfFileExists{../assets/module_header.tex}{}{}

\begin{document}
""" + tikz_content + r"""
\end{document}
"""
    
    wrapper_path = os.path.join(temp_dir, "wrapper.tex")
    write_file(wrapper_path, wrapper_content)
    
    # Also write the wrapper content for debugging
    debug_wrapper_path = os.path.join(temp_dir, "wrapper_debug.tex")
    write_file(debug_wrapper_path, wrapper_content)
    print(f"DEBUG: Wrapper written to {debug_wrapper_path}")
    
    return wrapper_path

def compile_figure(tikz_file):
    """
    Compile a single TikZ figure to PDF.
    Returns (tikz_file, success, error_msg)
    """
    try:
        build_path, log_path, pdf_path = ensure_output_dirs_for(tikz_file, is_figure=True)
        
        file_name = os.path.basename(tikz_file).replace(".tex", "")
        pdf_output = os.path.join(pdf_path, file_name + ".pdf")
        
        # Check if rebuild is needed
        if os.path.exists(pdf_output):
            if os.path.getmtime(tikz_file) <= os.path.getmtime(pdf_output):
                return (tikz_file, "skipped", None)
        
        # Create temporary build directory for this figure
        temp_build = os.path.join(build_path, file_name + "_temp")
        os.makedirs(temp_build, exist_ok=True)
        
        # Create wrapper document
        wrapper_path = create_figure_wrapper(tikz_file, temp_build)
        
        # Build command
        cmd = (
            f"{LATEXMK} "
            f"{' '.join(LATEXMK_FLAGS)} "
            f"-auxdir=\"{temp_build}\" "
            f"-outdir=\"{temp_build}\" "
            f"wrapper.tex"
        )
        
        # Compile
        cwd = os.getcwd()
        os.chdir(temp_build)
        
        exit_code = os.system(f"{cmd} > compile.log 2>&1")
        
        # Read the log to see what went wrong
        log_content = read_file("compile.log")
        
        os.chdir(cwd)
        
        if exit_code != 0:
            # Copy log for debugging
            log_file = os.path.join(log_path, file_name + ".log")
            shutil.copy2(os.path.join(temp_build, "compile.log"), log_file)
            
            # Print first few lines of error for debugging
            error_lines = [line for line in log_content.split('\n') if 'error' in line.lower() or '!' in line]
            error_preview = '\n'.join(error_lines[:10])  # First 10 error lines
            return (tikz_file, "failed", f"Exit code {exit_code}. Errors:\n{error_preview}")
        
        # Move PDF to output
        generated_pdf = os.path.join(temp_build, "wrapper.pdf")
        if os.path.exists(generated_pdf):
            shutil.copy2(generated_pdf, pdf_output)
            
            # Copy log
            log_file = os.path.join(log_path, file_name + ".log")
            if os.path.exists(os.path.join(temp_build, "compile.log")):
                shutil.copy2(os.path.join(temp_build, "compile.log"), log_file)
            
            # Clean up temp directory
            shutil.rmtree(temp_build)
            
            return (tikz_file, "compiled", None)
        else:
            return (tikz_file, "failed", "PDF not generated")
            
    except Exception as e:
        return (tikz_file, "failed", str(e))
# ================================================================
# Step 4: Main document compilation
# ================================================================

def compile_main_file(tex_file):
    """
    Compile a main LaTeX file.
    Returns (tex_file, success, error_msg)
    """
    try:
        build_path, log_path, pdf_path = ensure_output_dirs_for(tex_file)

        file_dir = os.path.dirname(tex_file)
        file_name = os.path.basename(tex_file)
        
        abs_build = os.path.abspath(build_path)

        cmd = (
            f"{LATEXMK} "
            f"{' '.join(LATEXMK_FLAGS)} "
            f"-auxdir=\"{abs_build}\" "
            f"-outdir=\"{abs_build}\" "
            f"\"{file_name}\""
        )

        cwd = os.getcwd()
        os.chdir(file_dir)

        exit_code = os.system(f"{cmd} > _latexmk_output.txt 2>&1")

        if exit_code != 0:
            os.chdir(cwd)
            # Save log
            log_file = os.path.join(log_path, file_root(tex_file) + ".log")
            if os.path.exists(os.path.join(file_dir, "_latexmk_output.txt")):
                shutil.move(os.path.join(file_dir, "_latexmk_output.txt"), log_file)
            return (tex_file, "failed", f"Exit code {exit_code}")

        os.chdir(cwd)
        
        # Move log
        log_file = os.path.join(log_path, file_root(tex_file) + ".log")
        if os.path.exists(os.path.join(file_dir, "_latexmk_output.txt")):
            shutil.move(os.path.join(file_dir, "_latexmk_output.txt"), log_file)

        # Move generated files
        move_build_outputs(tex_file, build_path, log_path, pdf_path)
        
        return (tex_file, "compiled", None)
        
    except Exception as e:
        return (tex_file, "failed", str(e))

def move_build_outputs(tex_file, build_path, log_path, pdf_path):
    root = file_root(tex_file)

    for f in os.listdir(build_path):
        if not f.startswith(root):
            continue

        src = os.path.join(build_path, f)

        if f.endswith(".pdf"):
            shutil.copy2(src, os.path.join(pdf_path, f))
        elif f.endswith(".log"):
            shutil.move(src, os.path.join(log_path, f))

# ================================================================
# Step 5: Parallel build logic
# ================================================================

def build_figures_parallel(max_workers=None):
    """Build all figures in parallel."""
    if not os.path.exists(FIGURE_FILES_LIST):
        print("No figure_files.txt found. Run --find-files first.")
        return False
    
    figure_files = [f for f in read_file(FIGURE_FILES_LIST).splitlines() if f]
    if not figure_files:
        print("No figure files to compile.")
        return True
    
    if max_workers is None:
        max_workers = max(1, multiprocessing.cpu_count() - 1)
    
    print(f"\n{'='*60}")
    print(f" Phase 1: Compiling {len(figure_files)} TikZ figures")
    print(f" Using {max_workers} parallel workers")
    print(f"{'='*60}\n")
    
    reset_stats(len(figure_files))
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(compile_figure, fig): fig for fig in figure_files}
        
        for future in as_completed(futures):
            fig_file = futures[future]
            try:
                result_file, status, error = future.result()
                
                if status == "compiled":
                    STATS["compiled"] += 1
                    print(f"  Compiled: {os.path.basename(result_file)}")
                elif status == "skipped":
                    STATS["skipped"] += 1
                    print(f"  Skipped (up to date): {os.path.basename(result_file)}")
                else:  # failed
                    STATS["failed"] += 1
                    print(f"  Failed: {os.path.basename(result_file)} - {error}")
                    
            except Exception as e:
                STATS["failed"] += 1
                print(f"  Error compiling {os.path.basename(fig_file)}: {e}")
    
    print_summary()
    return STATS["failed"] == 0

def build_mains_parallel(max_workers=None):
    """Build all main documents in parallel."""
    if not os.path.exists(MAIN_FILES_LIST):
        print("No main_files.txt found. Run --find-files first.")
        return False
    
    main_files = [f for f in read_file(MAIN_FILES_LIST).splitlines() if f]
    if not main_files:
        print("No main files to compile.")
        return True
    
    if max_workers is None:
        max_workers = max(1, multiprocessing.cpu_count() - 1)
    
    print(f"\n{'='*60}")
    print(f" Phase 2: Compiling {len(main_files)} main documents")
    print(f" Using {max_workers} parallel workers")
    print(f"{'='*60}\n")
    
    reset_stats(len(main_files))
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(compile_main_file, mf): mf for mf in main_files}
        
        for future in as_completed(futures):
            main_file = futures[future]
            try:
                result_file, status, error = future.result()
                
                if status == "compiled":
                    STATS["compiled"] += 1
                    print(f"  Compiled: {result_file}")
                elif status == "skipped":
                    STATS["skipped"] += 1
                    print(f"  Skipped: {result_file}")
                else:  # failed
                    STATS["failed"] += 1
                    print(f"  Failed: {result_file} - {error}")
                    
            except Exception as e:
                STATS["failed"] += 1
                print(f"  Error compiling {main_file}: {e}")
    
    print_summary()
    return STATS["failed"] == 0

# ================================================================
# Step 6: CLI handling
# ================================================================

def main():
    ensure_directories()

    if len(sys.argv) == 1:
        # Default: full build (figures then mains)
        find_figure_files()
        success = build_figures_parallel()
        if success:
            build_mains_parallel()
        return

    arg = sys.argv[1]

    if arg == "--initial":
        find_main_files()
        find_figure_files()
        create_deps_tree()
        
    elif arg == "--find-files":
        find_main_files()
        find_figure_files()
        
    elif arg == "--create-deps-tree":
        create_deps_tree()
        
    elif arg == "--figures-only":
        success = build_figures_parallel()
        if not success:
            sys.exit(1)
            
    elif arg == "--main-only":
        success = build_mains_parallel()
        if not success:
            sys.exit(1)
            
    elif arg == "--rebuild-all":
        print("Cleaning all outputs...")
        clean_all()
        find_figure_files()
        find_main_files()
        success = build_figures_parallel()
        if success:
            build_mains_parallel()
            
    elif arg == "--clean":
        clean_all()
        
    elif arg == "--help":
        print("""
LaTeX Build System with TikZ Precompilation

Usage: ./run.py [OPTION]

Options:
  (no args)         Incremental build (figures then mains)
  --initial         Find all files and create dependency tree
  --find-files      Find main and figure files
  --create-deps-tree Create dependency tree from main files
  --figures-only    Compile only TikZ figures
  --main-only       Compile only main documents
  --rebuild-all     Clean and rebuild everything
  --clean           Remove all build artifacts
  --help            Show this help message

Build Process:
  Phase 1: TikZ figures in src/*/assets/tikz/ → pdfs/*/figures/
  Phase 2: Main documents (*_main.tex) → pdfs/*/
  
Both phases use parallel compilation for speed.
        """)
    else:
        print(f"Unknown option: {arg}")
        print("Run './run.py --help' for usage information.")
        sys.exit(1)

if __name__ == "__main__":
    main()