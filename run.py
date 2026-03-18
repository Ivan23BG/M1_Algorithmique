import os
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

PROJECT_ROOT = Path.cwd()
SRC_DIR = PROJECT_ROOT / "src"
BUILD_ROOT = PROJECT_ROOT / "build"
PDF_ROOT = PROJECT_ROOT / "pdfs"
LOG_ROOT = PROJECT_ROOT / "logs"


# --------------------------------------------------
# File discovery
# --------------------------------------------------

def find_main_tex_files(root, suffix="_main.tex", exclude_patterns=None):
    if exclude_patterns is None:
        exclude_patterns = []

    files = []
    for path in root.rglob(f"*{suffix}"):
        path_str = str(path)
        if any(pat in path_str for pat in exclude_patterns):
            continue
        files.append(path)

    return files


# --------------------------------------------------
# Path helpers
# --------------------------------------------------

def mirror_under(root_dir, src_file):
    """
    Mirrors src/... under root_dir/...
    Example:
      src/ch1/sec1/main.tex
      -> build/ch1/sec1/
    """
    rel = src_file.parent.relative_to(SRC_DIR)
    target = root_dir / rel
    target.mkdir(parents=True, exist_ok=True)
    return target


# --------------------------------------------------
# Compilation
# --------------------------------------------------

def compile_latex(tex_file: Path):
    job_name = tex_file.stem

    build_dir = mirror_under(BUILD_ROOT, tex_file)
    pdf_dir   = mirror_under(PDF_ROOT, tex_file)
    log_dir   = mirror_under(LOG_ROOT, tex_file)

    cmd = [
        "latexmk",
        "-pdf",
        "-shell-escape",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-outdir={build_dir}",
        f"{job_name}.tex",
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=tex_file.parent,     # per-thread working directory
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )

        # Copy PDF
        pdf_src = build_dir / f"{job_name}.pdf"
        if pdf_src.exists():
            shutil.copy2(pdf_src, pdf_dir / pdf_src.name)

        # Move log
        log_src = build_dir / f"{job_name}.log"
        if log_src.exists():
            shutil.move(log_src, log_dir / log_src.name)

        return result.returncode == 0

    except Exception:
        return False

# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":
    exclude_patterns = ["legacy", "templates", "tmp", "temp"]

    tex_files = find_main_tex_files(SRC_DIR, "_main.tex", exclude_patterns)

    print("Found the following files to compile:")
    for f in tex_files:
        print("  ", f)

    successes = []
    failures = []
    """
    Non parallel version
    for tex in tex_files:
        ok = compile_latex(tex)
        if ok:
            successes.append(tex)
        else:
            failures.append(tex)
    """

    MAX_WORKERS = min(8, os.cpu_count() or 1)
    print(f"\nCompiling with {MAX_WORKERS} parallel workers...\n")

    successes = []
    failures = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_map = {executor.submit(compile_latex, tex): tex for tex in tex_files}

        for future in as_completed(future_map):
            tex = future_map[future]
            try:
                ok = future.result()
                if ok:
                    successes.append(tex)
                else:
                    failures.append(tex)
            except Exception:
                failures.append(tex)

    print("\n===== Compilation Summary =====")
    if successes:
        print(f"Successfully compiled: {len(successes)}")
        for f in successes:
            print("   ", f)

    if failures:
        print(f"\nFailed to compile: {len(failures)}")
        for f in failures:
            print("   ", f)
        exit(1)
    else:
        print("\nAll files compiled successfully")
