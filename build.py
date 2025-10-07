#!/usr/bin/env python3
"""
Fast LaTeX Build System for Elaborate School Projects
Author: Claude Assistant
Features: Smart caching, parallel builds, dependency tracking, module targeting
"""

import argparse
import json
import multiprocessing as mp
import os
import re
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    SRC_DIR = Path("src")
    BUILD_DIR = Path("build")
    LOGS_DIR = Path("logs")
    PDFS_DIR = Path("pdfs")
    CACHE_FILE = Path(".build_cache.json")
    
    LATEXMK = "latexmk"
    LATEXMK_FLAGS = ["-pdf", "-shell-escape", "-interaction=nonstopmode", "-halt-on-error"]
    MAX_DEPTH = 5
    
    # Colors
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    WHITE = "\033[1;37m"
    NC = "\033[0m"


# ============================================================================
# CACHE MANAGEMENT
# ============================================================================

class BuildCache:
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        if Config.CACHE_FILE.exists():
            try:
                with open(Config.CACHE_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {"mtimes": {}, "files": {}}
        return {"mtimes": {}, "files": {}}
    
    def save(self):
        with open(Config.CACHE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_mtime(self, path: Path) -> float:
        return self.data["mtimes"].get(str(path), 0)
    
    def set_mtime(self, path: Path, mtime: float):
        self.data["mtimes"][str(path)] = mtime
    
    def get_files(self) -> Dict:
        return self.data.get("files", {})
    
    def set_files(self, files: Dict):
        self.data["files"] = files


# ============================================================================
# FILE DISCOVERY
# ============================================================================

def find_main_tex_files() -> List[Path]:
    """Find all *_main.tex files in src directory"""
    main_files = []
    for root, dirs, files in os.walk(Config.SRC_DIR):
        depth = len(Path(root).relative_to(Config.SRC_DIR).parts)
        if depth >= Config.MAX_DEPTH:
            dirs.clear()
        
        for file in files:
            if file.endswith("_main.tex"):
                main_files.append(Path(root) / file)
    
    return sorted(main_files)


def get_dependencies(tex_file: Path) -> Set[Path]:
    """Get all dependencies for a tex file"""
    deps = set()
    
    # Common directory dependencies
    common_dir = Config.SRC_DIR / "common"
    if common_dir.exists():
        for ext in ["*.tex", "*.sty", "*.cls"]:
            deps.update(common_dir.rglob(ext))
    
    # Module-level dependencies
    module_root = tex_file.parent.parent  # Go up from tds/cours to module root
    if module_root.exists() and module_root.is_relative_to(Config.SRC_DIR):
        for ext in ["*.tex", "*.sty", "*.cls", "*.png", "*.jpg", "*.pdf"]:
            deps.update(module_root.rglob(ext))
    
    # Same directory dependencies
    for ext in ["*.tex", "*.sty", "*.cls", "*.png", "*.jpg", "*.pdf"]:
        deps.update(tex_file.parent.glob(ext))
    
    return deps


def parse_fls_dependencies(fls_file: Path) -> Set[Path]:
    """Parse .fls file for actual dependencies used by LaTeX"""
    deps = set()
    if not fls_file.exists():
        return deps
    
    try:
        with open(fls_file, 'r') as f:
            for line in f:
                if line.startswith('INPUT '):
                    dep_path = Path(line[6:].strip())
                    if dep_path.exists() and dep_path.suffix in ['.tex', '.sty', '.cls']:
                        deps.add(dep_path)
    except:
        pass
    
    return deps


def needs_rebuild(tex_file: Path, pdf_file: Path, cache: BuildCache) -> bool:
    """Check if a file needs to be rebuilt"""
    if not pdf_file.exists():
        return True
    
    # Get cached mtime
    cached_mtime = cache.get_mtime(tex_file)
    current_mtime = tex_file.stat().st_mtime
    
    if current_mtime > cached_mtime:
        return True
    
    # Check dependencies
    deps = get_dependencies(tex_file)
    
    # Also check .fls file if it exists for more accurate dependencies
    rel_path = tex_file.relative_to(Config.SRC_DIR).with_suffix('')
    fls_file = Config.BUILD_DIR / rel_path.parent / f"{rel_path.stem}.fls"
    if fls_file.exists():
        deps.update(parse_fls_dependencies(fls_file))
    
    pdf_mtime = pdf_file.stat().st_mtime
    for dep in deps:
        if dep.exists() and dep.stat().st_mtime > pdf_mtime:
            return True
    
    return False


# ============================================================================
# MODULE MANAGEMENT
# ============================================================================

class ModuleInfo:
    def __init__(self, name: str, files: List[Path]):
        self.name = name
        self.files = files
        self.code = re.search(r'HAI(\d+)I', name).group(1) if re.search(r'HAI(\d+)I', name) else None
    
    def __repr__(self):
        return f"Module({self.name}, {len(self.files)} files)"


def discover_modules(main_files: List[Path]) -> Dict[str, ModuleInfo]:
    """Discover all modules from main files"""
    modules = defaultdict(list)
    
    for tex_file in main_files:
        rel_path = tex_file.relative_to(Config.SRC_DIR)
        module_name = rel_path.parts[0]
        modules[module_name].append(tex_file)
    
    return {name: ModuleInfo(name, files) for name, files in modules.items()}


# ============================================================================
# COMPILATION
# ============================================================================

def compile_tex_file(tex_file: Path) -> Tuple[bool, Path, str]:
    """Compile a single tex file"""
    rel_path = tex_file.relative_to(Config.SRC_DIR)
    
    # Create directory structure
    build_dir = Config.BUILD_DIR / rel_path.parent
    log_dir = Config.LOGS_DIR / rel_path.parent
    pdf_dir = Config.PDFS_DIR / rel_path.parent
    
    build_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_output = pdf_dir / f"{rel_path.stem}.pdf"
    log_output = log_dir / f"{rel_path.stem}.log"
    
    # Run latexmk
    cmd = [
        Config.LATEXMK,
        *Config.LATEXMK_FLAGS,
        f"-output-directory={build_dir.absolute()}",
        tex_file.name
    ]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=tex_file.parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=180  # 3 minute timeout
        )
        
        # Save log
        with open(log_output, 'w') as f:
            f.write(result.stdout)
        
        # Move PDF to output directory
        built_pdf = build_dir / f"{rel_path.stem}.pdf"
        if built_pdf.exists():
            shutil.copy2(built_pdf, pdf_output)
            return True, tex_file, ""
        else:
            return False, tex_file, f"PDF not generated (see {log_output})"
    
    except subprocess.TimeoutExpired:
        return False, tex_file, "Compilation timeout"
    except Exception as e:
        return False, tex_file, str(e)


def compile_files_parallel(files: List[Path], num_jobs: int = None) -> List[Tuple[bool, Path, str]]:
    """Compile multiple files in parallel"""
    if num_jobs is None:
        num_jobs = max(1, mp.cpu_count() - 1)
    
    if len(files) == 1 or num_jobs == 1:
        # Single file or single job - compile directly with output
        results = []
        for f in files:
            print(f"{Config.BLUE}Compiling{Config.NC} {f.relative_to(Config.SRC_DIR)}")
            result = compile_tex_file(f)
            if result[0]:
                print(f"{Config.GREEN}Success{Config.NC}")
            else:
                print(f"{Config.RED}Failed: {result[2]}{Config.NC}")
            results.append(result)
        return results
    
    # Parallel compilation
    print(f"{Config.BLUE}Compiling {len(files)} files with {num_jobs} workers...{Config.NC}")
    
    with mp.Pool(num_jobs) as pool:
        results = pool.map(compile_tex_file, files)
    
    return results


# ============================================================================
# CLEANING
# ============================================================================

def clean_build():
    """Clean build directory"""
    if Config.BUILD_DIR.exists():
        shutil.rmtree(Config.BUILD_DIR)
        Config.BUILD_DIR.mkdir()
    print(f"{Config.GREEN}Build artifacts cleaned{Config.NC}")


def clean_logs():
    """Clean logs directory"""
    if Config.LOGS_DIR.exists():
        shutil.rmtree(Config.LOGS_DIR)
        Config.LOGS_DIR.mkdir()
    print(f"{Config.GREEN}Log files cleaned{Config.NC}")


def clean_pdfs():
    """Clean PDFs directory"""
    if Config.PDFS_DIR.exists():
        shutil.rmtree(Config.PDFS_DIR)
        Config.PDFS_DIR.mkdir()
    print(f"{Config.GREEN}PDF files cleaned{Config.NC}")


def clean_module(module_name: str):
    """Clean specific module"""
    for directory in [Config.BUILD_DIR, Config.LOGS_DIR]:
        module_dir = directory / module_name
        if module_dir.exists():
            shutil.rmtree(module_dir)
    print(f"{Config.GREEN}Module {module_name} cleaned{Config.NC}")


# ============================================================================
# MAIN BUILD LOGIC
# ============================================================================

def build(args):
    """Main build function"""
    cache = BuildCache()
    
    # Discover files
    print(f"{Config.BLUE}Discovering files...{Config.NC}", end=' ')
    main_files = find_main_tex_files()
    modules = discover_modules(main_files)
    print(f"{Config.GREEN}Found {len(main_files)} files in {len(modules)} modules{Config.NC}")
    
    # Filter files based on targets
    files_to_build = []
    
    if args.module:
        # Specific module(s)
        for module_pattern in args.module:
            matched = False
            for module_name, module_info in modules.items():
                if (module_pattern == module_name or 
                    module_pattern == module_info.code or
                    module_pattern in module_name.lower()):
                    files_to_build.extend(module_info.files)
                    matched = True
            if not matched:
                print(f"{Config.YELLOW}Warning: No module matched '{module_pattern}'{Config.NC}")
    
    elif args.range:
        # Range of modules
        start, end = args.range
        for module_info in modules.values():
            if module_info.code and int(start) <= int(module_info.code) <= int(end):
                files_to_build.extend(module_info.files)
    
    else:
        # All files
        files_to_build = main_files
    
    if not files_to_build:
        print(f"{Config.RED}No files to build{Config.NC}")
        return 1
    
    # Check what needs rebuilding
    if args.force:
        files_to_compile = files_to_build
    else:
        print(f"{Config.BLUE}Checking dependencies...{Config.NC}", end=' ')
        files_to_compile = []
        for tex_file in files_to_build:
            rel_path = tex_file.relative_to(Config.SRC_DIR)
            pdf_file = Config.PDFS_DIR / rel_path.parent / f"{rel_path.stem}.pdf"
            
            if needs_rebuild(tex_file, pdf_file, cache):
                files_to_compile.append(tex_file)
        
        print(f"{Config.GREEN}{len(files_to_compile)} files need rebuilding{Config.NC}")
    
    if not files_to_compile:
        print(f"{Config.GREEN}All files are up to date!{Config.NC}")
        return 0
    
    # Compile files
    start_time = time.time()
    results = compile_files_parallel(files_to_compile, args.jobs)
    elapsed = time.time() - start_time
    
    # Update cache for successful builds
    for success, tex_file, error in results:
        if success:
            cache.set_mtime(tex_file, tex_file.stat().st_mtime)
    
    cache.save()
    
    # Summary
    successful = sum(1 for r in results if r[0])
    failed = len(results) - successful
    
    print(f"\n{Config.WHITE}{'='*60}{Config.NC}")
    print(f"{Config.WHITE}Build Summary{Config.NC}")
    print(f"{Config.WHITE}{'='*60}{Config.NC}")
    print(f"  {Config.GREEN}Successful: {successful}{Config.NC}")
    if failed > 0:
        print(f"  {Config.RED}Failed: {failed}{Config.NC}")
        print(f"\n{Config.RED}Failed files:{Config.NC}")
        for success, tex_file, error in results:
            if not success:
                print(f"  {Config.RED}{Config.NC} {tex_file.relative_to(Config.SRC_DIR)}: {error}")
    print(f"  Time: {elapsed:.2f}s")
    print(f"{Config.WHITE}{'='*60}{Config.NC}")
    
    return 1 if failed > 0 else 0


# ============================================================================
# CLI INTERFACE
# ============================================================================

def list_modules(args):
    """List all modules"""
    main_files = find_main_tex_files()
    modules = discover_modules(main_files)
    
    print(f"{Config.WHITE}Detected Modules:{Config.NC}")
    for module_name, module_info in sorted(modules.items()):
        code = f"({module_info.code})" if module_info.code else ""
        print(f"  {Config.CYAN}{module_name}{Config.NC} {code} - {len(module_info.files)} files")


def list_files(args):
    """List all main files"""
    main_files = find_main_tex_files()
    
    print(f"{Config.WHITE}Main LaTeX Files:{Config.NC}")
    for tex_file in main_files:
        print(f"  {Config.GREEN}{tex_file.relative_to(Config.SRC_DIR)}{Config.NC}")


def info(args):
    """Show project information"""
    main_files = find_main_tex_files()
    modules = discover_modules(main_files)
    
    print(f"{Config.WHITE}Project Information:{Config.NC}")
    print(f"  Source Directory:  {Config.CYAN}{Config.SRC_DIR}{Config.NC}")
    print(f"  Build Directory:   {Config.CYAN}{Config.BUILD_DIR}{Config.NC}")
    print(f"  Logs Directory:    {Config.CYAN}{Config.LOGS_DIR}{Config.NC}")
    print(f"  PDFs Directory:    {Config.CYAN}{Config.PDFS_DIR}{Config.NC}")
    print(f"  Max Search Depth:  {Config.CYAN}{Config.MAX_DEPTH}{Config.NC}")
    print()
    print(f"  Total Modules:     {Config.CYAN}{len(modules)}{Config.NC}")
    print(f"  Total Main Files:  {Config.CYAN}{len(main_files)}{Config.NC}")


def stats(args):
    """Show project statistics"""
    tex_files = list(Config.SRC_DIR.rglob("*.tex"))
    image_files = list(Config.SRC_DIR.rglob("*.png")) + list(Config.SRC_DIR.rglob("*.jpg"))
    
    total_lines = 0
    for tex_file in tex_files:
        try:
            with open(tex_file, 'r') as f:
                total_lines += len(f.readlines())
        except:
            pass
    
    print(f"{Config.WHITE}Project Statistics:{Config.NC}")
    print(f"  LaTeX files:  {Config.CYAN}{len(tex_files)}{Config.NC}")
    print(f"  Image files:  {Config.CYAN}{len(image_files)}{Config.NC}")
    print(f"  Total lines:  {Config.CYAN}{total_lines}{Config.NC}")
    
    if Config.PDFS_DIR.exists():
        pdf_files = list(Config.PDFS_DIR.rglob("*.pdf"))
        total_size = sum(f.stat().st_size for f in pdf_files if f.exists())
        print(f"  PDF count:    {Config.CYAN}{len(pdf_files)}{Config.NC}")
        print(f"  PDF size:     {Config.CYAN}{total_size / (1024*1024):.1f} MB{Config.NC}")


def main():
    parser = argparse.ArgumentParser(
        description="Fast LaTeX Build System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Build command (default)
    build_parser = subparsers.add_parser('build', help='Build LaTeX files (default)')
    build_parser.add_argument('-m', '--module', action='append', help='Build specific module(s)')
    build_parser.add_argument('-r', '--range', nargs=2, metavar=('START', 'END'), 
                              help='Build range of modules (e.g., 702 710)')
    build_parser.add_argument('-j', '--jobs', type=int, help='Number of parallel jobs')
    build_parser.add_argument('-f', '--force', action='store_true', help='Force rebuild all')
    
    # Clean commands
    clean_parser = subparsers.add_parser('clean', help='Clean build files')
    clean_parser.add_argument('--all', action='store_true', help='Clean everything including PDFs')
    clean_parser.add_argument('--build', action='store_true', help='Clean build directory')
    clean_parser.add_argument('--logs', action='store_true', help='Clean logs directory')
    clean_parser.add_argument('--pdfs', action='store_true', help='Clean PDFs directory')
    clean_parser.add_argument('--module', help='Clean specific module')
    
    # Info commands
    subparsers.add_parser('list-modules', help='List all modules')
    subparsers.add_parser('list-files', help='List all main files')
    subparsers.add_parser('info', help='Show project information')
    subparsers.add_parser('stats', help='Show project statistics')
    
    args = parser.parse_args()
    
    # Default to build if no command specified
    if not args.command:
        args.command = 'build'
        args.module = None
        args.range = None
        args.jobs = None
        args.force = False
    
    # Execute command
    if args.command == 'build':
        return build(args)
    
    elif args.command == 'clean':
        if args.module:
            clean_module(args.module)
        elif args.all:
            clean_build()
            clean_logs()
            clean_pdfs()
            if Config.CACHE_FILE.exists():
                Config.CACHE_FILE.unlink()
        elif args.build:
            clean_build()
        elif args.logs:
            clean_logs()
        elif args.pdfs:
            clean_pdfs()
        else:
            clean_build()
            clean_logs()
            if Config.CACHE_FILE.exists():
                Config.CACHE_FILE.unlink()
        return 0
    
    elif args.command == 'list-modules':
        list_modules(args)
        return 0
    
    elif args.command == 'list-files':
        list_files(args)
        return 0
    
    elif args.command == 'info':
        info(args)
        return 0
    
    elif args.command == 'stats':
        stats(args)
        return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Config.YELLOW}Build interrupted{Config.NC}")
        sys.exit(1)