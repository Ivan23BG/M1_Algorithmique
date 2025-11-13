#!/usr/bin/env python3
"""
LaTeX Build System for Multi-Module Academic Projects
======================================================

A smart build system that compiles LaTeX documents organized in modules
(e.g., HAI702I_Algebre, HAI703I_Anglais) with intelligent caching,
parallel compilation, and dependency tracking.

TYPICAL PROJECT STRUCTURE:
    src/
        HAI702I_Algebre/
            tds/
                td_main.tex          # Main file (builds to PDF)
                td_1.tex             # Included content
        HAI703I_Anglais/
            presentation/
                presentation_main.tex
        common/                      # Shared resources
            macros/
            environments/
    
    pdfs/                           # Compiled PDFs (mirroring src/)
    build/                          # Intermediate LaTeX files
    logs/                           # Compilation logs

USAGE EXAMPLES:
    # Build all modules (only changed files)
    ./build.py
    
    # Build specific module by name or code
    ./build.py build -m HAI702I_Algebre
    ./build.py build -m 702
    
    # Build multiple modules
    ./build.py build -m 702 -m 703
    
    # Build range of modules by code
    ./build.py build -r 702 710
    
    # Force rebuild everything
    ./build.py build --force
    
    # Use 4 parallel workers
    ./build.py build -j 4
    
    # List available modules
    ./build.py list-modules
    
    # Show detailed project info with metrics
    ./build.py info
    
    # Clean everything
    ./build.py clean --all

Enhanced by Claude
Version: 2.0
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
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Build system configuration and constants"""
    
    # Directory structure
    SRC_DIR = Path("src")
    BUILD_DIR = Path("build")
    LOGS_DIR = Path("logs")
    PDFS_DIR = Path("pdfs")
    CACHE_FILE = Path(".build_cache.json")
    
    # LaTeX compilation settings
    LATEXMK = "latexmk"
    LATEXMK_FLAGS = [
        "-pdf",
        "-shell-escape",
        "-interaction=nonstopmode",
        "-halt-on-error"
    ]
    COMPILE_TIMEOUT = 180  # seconds
    
    # Discovery settings
    MAX_DEPTH = 5
    MAIN_FILE_PATTERN = "*_main.tex"
    
    # Terminal colors (ANSI escape codes)
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    MAGENTA = "\033[0;35m"
    WHITE = "\033[1;37m"
    GRAY = "\033[0;90m"
    NC = "\033[0m"  # No Color


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ModuleInfo:
    """Information about a discovered module"""
    name: str
    code: Optional[str]
    files: List[Path]
    
    def __post_init__(self):
        """Extract module code from name (e.g., HAI702I -> 702)"""
        if self.code is None:
            match = re.search(r'HAI(\d+)I', self.name)
            self.code = match.group(1) if match else None
    
    def __repr__(self):
        code_str = f" [{self.code}]" if self.code else ""
        return f"Module({self.name}{code_str}, {len(self.files)} files)"


@dataclass
class CompileResult:
    """Result of compiling a single file"""
    success: bool
    tex_file: Path
    pdf_file: Optional[Path]
    log_file: Path
    error_msg: str
    duration: float


@dataclass
class BuildMetrics:
    """Metrics collected during a build"""
    total_files: int = 0
    compiled_files: int = 0
    skipped_files: int = 0
    successful: int = 0
    failed: int = 0
    total_time: float = 0.0
    
    def success_rate(self) -> float:
        if self.compiled_files == 0:
            return 100.0
        return (self.successful / self.compiled_files) * 100


@dataclass
class ProjectStats:
    """Overall project statistics"""
    total_modules: int
    total_main_files: int
    total_tex_files: int
    total_image_files: int
    total_lines: int
    pdf_count: int
    pdf_size_mb: float
    source_size_mb: float


# ============================================================================
# CACHE MANAGEMENT
# ============================================================================

class BuildCache:
    """Manages build cache for incremental compilation"""
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        """Load cache from disk"""
        if Config.CACHE_FILE.exists():
            try:
                with open(Config.CACHE_FILE, 'r') as f:
                    cache = json.load(f)
                    # Ensure required keys exist
                    cache.setdefault("mtimes", {})
                    cache.setdefault("files", {})
                    return cache
            except (json.JSONDecodeError, IOError) as e:
                print(f"{Config.YELLOW}Warning: Could not load cache ({e}), starting fresh{Config.NC}")
        return {"mtimes": {}, "files": {}}
    
    def save(self):
        """Save cache to disk"""
        try:
            with open(Config.CACHE_FILE, 'w') as f:
                json.dump(self.data, f, indent=4)
        except IOError as e:
            print(f"{Config.YELLOW}Warning: Could not save cache: {e}{Config.NC}")
    
    def get_mtime(self, path: Path) -> float:
        """Get cached modification time for a file"""
        return self.data["mtimes"].get(str(path), 0)
    
    def set_mtime(self, path: Path, mtime: float):
        """Set modification time for a file"""
        self.data["mtimes"][str(path)] = mtime
    
    def clear(self):
        """Clear all cache data"""
        self.data = {"mtimes": {}, "files": {}}


# ============================================================================
# FILE DISCOVERY
# ============================================================================

def find_main_tex_files() -> List[Path]:
    """
    Find all *_main.tex files in the source directory.
    
    Searches recursively up to MAX_DEPTH levels for files matching
    the pattern (e.g., td_main.tex, cours_main.tex).
    """
    main_files = []
    
    if not Config.SRC_DIR.exists():
        print(f"{Config.RED}Error: Source directory '{Config.SRC_DIR}' not found{Config.NC}")
        return []
    
    for root, dirs, files in os.walk(Config.SRC_DIR):
        # Limit search depth
        depth = len(Path(root).relative_to(Config.SRC_DIR).parts)
        if depth >= Config.MAX_DEPTH:
            dirs.clear()
        
        for file in files:
            if file.endswith("_main.tex"):
                main_files.append(Path(root) / file)
    
    return sorted(main_files)


def get_dependencies(tex_file: Path) -> Set[Path]:
    """
    Get all potential dependencies for a LaTeX file.
    
    Scans:
    - Common directory (shared resources)
    - Module root directory (all resources in the module)
    - Same directory as the main file
    """
    deps = set()
    
    # Common directory dependencies
    common_dir = Config.SRC_DIR / "common"
    if common_dir.exists():
        for ext in ["*.tex", "*.sty", "*.cls"]:
            deps.update(common_dir.rglob(ext))
    
    # Module-level dependencies
    try:
        module_root = tex_file.parent.parent  # e.g., from tds/cours to module root
        if module_root.exists() and module_root.is_relative_to(Config.SRC_DIR):
            for ext in ["*.tex", "*.sty", "*.cls", "*.png", "*.jpg", "*.pdf", "*.jpeg"]:
                deps.update(module_root.rglob(ext))
    except ValueError:
        pass
    
    # Same directory dependencies
    for ext in ["*.tex", "*.sty", "*.cls", "*.png", "*.jpg", "*.pdf", "*.jpeg"]:
        deps.update(tex_file.parent.glob(ext))
    
    return deps


def parse_fls_dependencies(fls_file: Path) -> Set[Path]:
    """
    Parse .fls file for actual dependencies used by LaTeX.
    
    The .fls file is created by latexmk and lists all files read during
    compilation, providing more accurate dependency information.
    """
    deps = set()
    if not fls_file.exists():
        return deps
    
    try:
        with open(fls_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('INPUT '):
                    dep_path = Path(line[6:].strip())
                    if dep_path.exists() and dep_path.suffix in ['.tex', '.sty', '.cls']:
                        deps.add(dep_path)
    except IOError:
        pass
    
    return deps


def needs_rebuild(tex_file: Path, pdf_file: Path, cache: BuildCache) -> bool:
    """
    Determine if a file needs to be rebuilt.
    
    Checks:
    1. PDF exists
    2. Main file modification time
    3. Dependency modification times
    """
    if not pdf_file.exists():
        return True
    
    # Check main file
    cached_mtime = cache.get_mtime(tex_file)
    current_mtime = tex_file.stat().st_mtime
    
    if current_mtime > cached_mtime:
        return True
    
    # Check dependencies
    deps = get_dependencies(tex_file)
    
    # Also check .fls file for more accurate dependencies
    rel_path = tex_file.relative_to(Config.SRC_DIR).with_suffix('')
    fls_file = Config.BUILD_DIR / rel_path.parent / f"{rel_path.stem}.fls"
    if fls_file.exists():
        deps.update(parse_fls_dependencies(fls_file))
    
    pdf_mtime = pdf_file.stat().st_mtime
    for dep in deps:
        try:
            if dep.exists() and dep.stat().st_mtime > pdf_mtime:
                return True
        except OSError:
            continue
    
    return False


# ============================================================================
# MODULE MANAGEMENT
# ============================================================================

def discover_modules(main_files: List[Path]) -> Dict[str, ModuleInfo]:
    """
    Discover all modules from main files.
    
    Groups files by their top-level directory in src/
    (e.g., HAI702I_Algebre, HAI703I_Anglais)
    """
    modules = defaultdict(list)
    
    for tex_file in main_files:
        try:
            rel_path = tex_file.relative_to(Config.SRC_DIR)
            if rel_path.parts:
                module_name = rel_path.parts[0]
                modules[module_name].append(tex_file)
        except ValueError:
            continue
    
    return {
        name: ModuleInfo(name=name, code=None, files=files)
        for name, files in modules.items()
    }


# ============================================================================
# COMPILATION
# ============================================================================

def compile_tex_file(tex_file: Path) -> CompileResult:
    """
    Compile a single LaTeX file using latexmk.
    
    Returns a CompileResult with success status, paths, and timing.
    """
    start_time = time.time()
    
    try:
        rel_path = tex_file.relative_to(Config.SRC_DIR)
    except ValueError:
        return CompileResult(
            success=False,
            tex_file=tex_file,
            pdf_file=None,
            log_file=Path("/dev/null"),
            error_msg="File not in source directory",
            duration=0.0
        )
    
    # Create directory structure
    build_dir = Config.BUILD_DIR / rel_path.parent
    log_dir = Config.LOGS_DIR / rel_path.parent
    pdf_dir = Config.PDFS_DIR / rel_path.parent
    
    for directory in [build_dir, log_dir, pdf_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
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
            timeout=Config.COMPILE_TIMEOUT
        )
        
        # Save log
        with open(log_output, 'w') as f:
            f.write(result.stdout)
        
        # Move PDF to output directory
        built_pdf = build_dir / f"{rel_path.stem}.pdf"
        if built_pdf.exists():
            shutil.copy2(built_pdf, pdf_output)
            duration = time.time() - start_time
            return CompileResult(
                success=True,
                tex_file=tex_file,
                pdf_file=pdf_output,
                log_file=log_output,
                error_msg="",
                duration=duration
            )
        else:
            duration = time.time() - start_time
            return CompileResult(
                success=False,
                tex_file=tex_file,
                pdf_file=None,
                log_file=log_output,
                error_msg=f"PDF not generated (see {log_output})",
                duration=duration
            )
    
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return CompileResult(
            success=False,
            tex_file=tex_file,
            pdf_file=None,
            log_file=log_output,
            error_msg=f"Compilation timeout ({Config.COMPILE_TIMEOUT}s)",
            duration=duration
        )
    except Exception as e:
        duration = time.time() - start_time
        return CompileResult(
            success=False,
            tex_file=tex_file,
            pdf_file=None,
            log_file=log_output,
            error_msg=str(e),
            duration=duration
        )


def compile_files_parallel(files: List[Path], num_jobs: Optional[int] = None) -> List[CompileResult]:
    """
    Compile multiple files in parallel.
    
    Uses multiprocessing to compile files concurrently.
    Shows progress for single files, uses pool for multiple.
    """
    num_jobs = 1
    
    if len(files) == 1 or num_jobs == 1:
        # Single file or single job - compile directly with live output
        results = []
        for f in files:
            rel_path = f.relative_to(Config.SRC_DIR)
            print(f"{Config.BLUE}Compiling{Config.NC} {rel_path}")
            result = compile_tex_file(f)
            
            if result.success:
                print(f"{Config.GREEN}Success{Config.NC} ({result.duration:.1f}s)")
            else:
                print(f"{Config.RED}Failed{Config.NC} {result.error_msg}")
            
            results.append(result)
        return results
    
    # Parallel compilation
    print(f"{Config.BLUE}Compiling {len(files)} files using {num_jobs} workers...{Config.NC}")
    
    with mp.Pool(num_jobs) as pool:
        results = pool.map(compile_tex_file, files)
    
    return results


# ============================================================================
# CLEANING OPERATIONS
# ============================================================================

def clean_build():
    """Remove build artifacts directory"""
    if Config.BUILD_DIR.exists():
        shutil.rmtree(Config.BUILD_DIR)
        Config.BUILD_DIR.mkdir()
    print(f"{Config.GREEN}Build artifacts cleaned{Config.NC}")


def clean_logs():
    """Remove logs directory"""
    if Config.LOGS_DIR.exists():
        shutil.rmtree(Config.LOGS_DIR)
        Config.LOGS_DIR.mkdir()
    print(f"{Config.GREEN}Log files cleaned{Config.NC}")


def clean_pdfs():
    """Remove PDFs directory"""
    if Config.PDFS_DIR.exists():
        shutil.rmtree(Config.PDFS_DIR)
        Config.PDFS_DIR.mkdir()
    print(f"{Config.GREEN}PDF files cleaned{Config.NC}")


def clean_module(module_name: str):
    """Remove build artifacts for a specific module"""
    cleaned = False
    for directory in [Config.BUILD_DIR, Config.LOGS_DIR]:
        module_dir = directory / module_name
        if module_dir.exists():
            shutil.rmtree(module_dir)
            cleaned = True
    
    if cleaned:
        print(f"{Config.GREEN}Module '{module_name}' cleaned{Config.NC}")
    else:
        print(f"{Config.YELLOW}Module '{module_name}' not found{Config.NC}")


# ============================================================================
# STATISTICS & METRICS
# ============================================================================

def calculate_project_stats() -> ProjectStats:
    """Calculate comprehensive project statistics"""
    
    # Find all files
    main_files = find_main_tex_files()
    modules = discover_modules(main_files)
    
    tex_files = list(Config.SRC_DIR.rglob("*.tex"))
    image_files = (
        list(Config.SRC_DIR.rglob("*.png")) +
        list(Config.SRC_DIR.rglob("*.jpg")) +
        list(Config.SRC_DIR.rglob("*.jpeg")) +
        list(Config.SRC_DIR.rglob("*.pdf"))
    )
    
    # Count lines in LaTeX files
    total_lines = 0
    for tex_file in tex_files:
        try:
            with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
                total_lines += sum(1 for _ in f)
        except IOError:
            pass
    
    # Calculate source size
    source_size = 0
    for tex_file in tex_files:
        try:
            source_size += tex_file.stat().st_size
        except OSError:
            pass
    
    # PDF statistics
    pdf_count = 0
    pdf_size = 0
    if Config.PDFS_DIR.exists():
        pdf_files = list(Config.PDFS_DIR.rglob("*.pdf"))
        pdf_count = len(pdf_files)
        pdf_size = sum(f.stat().st_size for f in pdf_files if f.exists())
    
    return ProjectStats(
        total_modules=len(modules),
        total_main_files=len(main_files),
        total_tex_files=len(tex_files),
        total_image_files=len(image_files),
        total_lines=total_lines,
        pdf_count=pdf_count,
        pdf_size_mb=pdf_size / (1024 * 1024),
        source_size_mb=source_size / (1024 * 1024)
    )


# ============================================================================
# BUILD LOGIC
# ============================================================================

def build_command(args) -> int:
    """Main build command"""
    cache = BuildCache()
    
    # Discover files
    print(f"{Config.BLUE}Discovering project structure...{Config.NC}")
    main_files = find_main_tex_files()
    
    if not main_files:
        print(f"{Config.RED}No *_main.tex files found in {Config.SRC_DIR}{Config.NC}")
        return 1
    
    modules = discover_modules(main_files)
    print(f"{Config.GREEN}Found {len(main_files)} main files in {len(modules)} modules{Config.NC}\n")
    
    # Filter files based on targets
    files_to_build = []
    
    if args.module:
        # Specific module(s)
        for module_pattern in args.module:
            matched = False
            for module_name, module_info in modules.items():
                # Match by exact name, code, or substring
                if (module_pattern == module_name or
                    module_pattern == module_info.code or
                    module_pattern.lower() in module_name.lower()):
                    files_to_build.extend(module_info.files)
                    matched = True
                    print(f"{Config.CYAN}Selected module:{Config.NC} {module_name}")
            
            if not matched:
                print(f"{Config.YELLOW}Warning: No module matched '{module_pattern}'{Config.NC}")
    
    elif args.range:
        # Range of modules by code
        start, end = args.range
        print(f"{Config.CYAN}Building modules in range: {start}-{end}{Config.NC}")
        for module_info in modules.values():
            if module_info.code:
                try:
                    code_num = int(module_info.code)
                    if int(start) <= code_num <= int(end):
                        files_to_build.extend(module_info.files)
                        print(f"{Config.CYAN}  • {module_info.name}{Config.NC}")
                except ValueError:
                    pass
    
    else:
        # All files
        files_to_build = main_files
        print(f"{Config.CYAN}Building all modules{Config.NC}")
    
    if not files_to_build:
        print(f"{Config.RED}No files to build{Config.NC}")
        return 1
    
    # Determine what needs compilation
    metrics = BuildMetrics(total_files=len(files_to_build))
    
    if args.force:
        files_to_compile = files_to_build
        print(f"{Config.YELLOW}Force rebuild enabled - recompiling all {len(files_to_build)} files{Config.NC}\n")
    else:
        print(f"{Config.BLUE}Checking dependencies...{Config.NC}")
        files_to_compile = []
        
        for tex_file in files_to_build:
            rel_path = tex_file.relative_to(Config.SRC_DIR)
            pdf_file = Config.PDFS_DIR / rel_path.parent / f"{rel_path.stem}.pdf"
            
            if needs_rebuild(tex_file, pdf_file, cache):
                files_to_compile.append(tex_file)
        
        metrics.compiled_files = len(files_to_compile)
        metrics.skipped_files = len(files_to_build) - len(files_to_compile)
        
        print(f"{Config.GREEN}{metrics.compiled_files} files need rebuilding, "
              f"{metrics.skipped_files} up to date{Config.NC}\n")
    
    if not files_to_compile:
        print(f"{Config.GREEN}All files are up to date!{Config.NC}")
        return 0
    
    # Compile files
    start_time = time.time()
    results = compile_files_parallel(files_to_compile, args.jobs)
    metrics.total_time = time.time() - start_time
    
    # Update cache for successful builds
    for result in results:
        if result.success:
            cache.set_mtime(result.tex_file, result.tex_file.stat().st_mtime)
            metrics.successful += 1
        else:
            metrics.failed += 1
    
    cache.save()
    
    # Print summary
    print_build_summary(results, metrics)
    
    return 1 if metrics.failed > 0 else 0


def print_build_summary(results: List[CompileResult], metrics: BuildMetrics):
    """Print a formatted build summary"""
    print(f"\n{Config.WHITE}{'═' * 70}{Config.NC}")
    print(f"{Config.WHITE}BUILD SUMMARY{Config.NC}")
    print(f"{Config.WHITE}{'═' * 70}{Config.NC}")
    
    # Overall stats
    print(f"\n{Config.WHITE}Results:{Config.NC}")
    print(f"  {Config.GREEN}Successful:{Config.NC}  {metrics.successful}")
    
    if metrics.failed > 0:
        print(f"  {Config.RED}Failed:{Config.NC}      {metrics.failed}")
    
    if metrics.skipped_files > 0:
        print(f"  {Config.CYAN}• Skipped:{Config.NC}     {metrics.skipped_files} (up to date)")
    
    print(f"\n{Config.WHITE}Performance:{Config.NC}")
    print(f"  Total time:    {metrics.total_time:.2f}s")
    
    if metrics.compiled_files > 0:
        avg_time = metrics.total_time / metrics.compiled_files
        print(f"  Average/file:  {avg_time:.2f}s")
        print(f"  Success rate:  {metrics.success_rate():.1f}%")
    
    # Failed files details
    if metrics.failed > 0:
        print(f"\n{Config.RED}Failed Files:{Config.NC}")
        for result in results:
            if not result.success:
                rel_path = result.tex_file.relative_to(Config.SRC_DIR)
                print(f"  {Config.RED}✗{Config.NC} {rel_path}")
                print(f"    {Config.GRAY}└─{Config.NC} {result.error_msg}")
                if result.log_file.exists():
                    print(f"    {Config.GRAY}└─{Config.NC} Log: {result.log_file}")
    
    print(f"\n{Config.WHITE}{'═' * 70}{Config.NC}")


# ============================================================================
# INFO COMMANDS
# ============================================================================

def list_modules_command(args) -> int:
    """List all detected modules"""
    main_files = find_main_tex_files()
    modules = discover_modules(main_files)
    
    print(f"{Config.WHITE}╔══════════════════════════════════════════════════════════════╗{Config.NC}")
    print(f"{Config.WHITE}║ DETECTED MODULES                                             ║{Config.NC}")
    print(f"{Config.WHITE}╚══════════════════════════════════════════════════════════════╝{Config.NC}\n")
    
    for module_name, module_info in sorted(modules.items()):
        code_str = f"{Config.GRAY}[{module_info.code}]{Config.NC}" if module_info.code else ""
        file_count = f"{len(module_info.files)} file{'s' if len(module_info.files) > 1 else ''}"
        
        print(f"  {Config.CYAN}•{Config.NC} {module_name} {code_str}")
        print(f"    {Config.GRAY}└─{Config.NC} {file_count}")
        
        # Show individual files if verbose
        if len(module_info.files) <= 5:
            for f in module_info.files:
                rel = f.relative_to(Config.SRC_DIR)
                print(f"       {Config.GRAY}├─{Config.NC} {rel}")
    
    print(f"\n{Config.WHITE}Total: {len(modules)} modules{Config.NC}")
    return 0


def list_files_command(args) -> int:
    """List all main files"""
    main_files = find_main_tex_files()
    
    print(f"{Config.WHITE}╔══════════════════════════════════════════════════════════════╗{Config.NC}")
    print(f"{Config.WHITE}║ MAIN LATEX FILES                                             ║{Config.NC}")
    print(f"{Config.WHITE}╚══════════════════════════════════════════════════════════════╝{Config.NC}\n")
    
    for tex_file in main_files:
        rel_path = tex_file.relative_to(Config.SRC_DIR)
        print(f"  {Config.GREEN}•{Config.NC} {rel_path}")
    
    print(f"\n{Config.WHITE}Total: {len(main_files)} files{Config.NC}")
    return 0


def info_command(args) -> int:
    """Show comprehensive project information with metrics"""
    
    print(f"{Config.WHITE}╔══════════════════════════════════════════════════════════════╗{Config.NC}")
    print(f"{Config.WHITE}║ PROJECT INFORMATION                                          ║{Config.NC}")
    print(f"{Config.WHITE}╚══════════════════════════════════════════════════════════════╝{Config.NC}\n")
    
    # Configuration
    print(f"{Config.WHITE}Configuration:{Config.NC}")
    print(f"  Source directory:    {Config.CYAN}{Config.SRC_DIR}{Config.NC}")
    print(f"  Build directory:     {Config.CYAN}{Config.BUILD_DIR}{Config.NC}")
    print(f"  Logs directory:      {Config.CYAN}{Config.LOGS_DIR}{Config.NC}")
    print(f"  PDFs directory:      {Config.CYAN}{Config.PDFS_DIR}{Config.NC}")
    print(f"  Max search depth:    {Config.CYAN}{Config.MAX_DEPTH}{Config.NC}")
    print(f"  Compile timeout:     {Config.CYAN}{Config.COMPILE_TIMEOUT}s{Config.NC}")
    
    # Calculate statistics
    print(f"\n{Config.BLUE}Calculating statistics...{Config.NC}")
    stats = calculate_project_stats()
    
    # Structure
    print(f"\n{Config.WHITE}Structure:{Config.NC}")
    print(f"  Modules:             {Config.CYAN}{stats.total_modules}{Config.NC}")
    print(f"  Main files:          {Config.CYAN}{stats.total_main_files}{Config.NC}")
    print(f"  Total .tex files:    {Config.CYAN}{stats.total_tex_files}{Config.NC}")
    print(f"  Image files:         {Config.CYAN}{stats.total_image_files}{Config.NC}")
    
    # Content metrics
    print(f"\n{Config.WHITE}Content Metrics:{Config.NC}")
    print(f"  Total lines of LaTeX: {Config.CYAN}{stats.total_lines:,}{Config.NC}")
    print(f"  Source size:          {Config.CYAN}{stats.source_size_mb:.2f} MB{Config.NC}")
    print(f"  Avg lines per file:   {Config.CYAN}{stats.total_lines // max(stats.total_tex_files, 1)}{Config.NC}")
    
    # Output metrics
    print(f"\n{Config.WHITE}Output:{Config.NC}")
    print(f"  Compiled PDFs:       {Config.CYAN}{stats.pdf_count}{Config.NC}")
    print(f"  Total PDF size:      {Config.CYAN}{stats.pdf_size_mb:.2f} MB{Config.NC}")
    
    if stats.pdf_count > 0:
        avg_pdf = stats.pdf_size_mb / stats.pdf_count
        print(f"  Avg PDF size:        {Config.CYAN}{avg_pdf:.2f} MB{Config.NC}")
    
    # Cache info
    cache = BuildCache()
    cached_files = len(cache.data.get("mtimes", {}))
    print(f"\n{Config.WHITE}Build Cache:{Config.NC}")
    print(f"  Cached files:        {Config.CYAN}{cached_files}{Config.NC}")
    print(f"  Cache location:      {Config.CYAN}{Config.CACHE_FILE}{Config.NC}")
    
    return 0


def stats_command(args) -> int:
    """Show detailed project statistics"""
    print(f"{Config.BLUE}Analyzing project...{Config.NC}\n")
    stats = calculate_project_stats()
    
    print(f"{Config.WHITE}╔══════════════════════════════════════════════════════════════╗{Config.NC}")
    print(f"{Config.WHITE}║ PROJECT STATISTICS                                           ║{Config.NC}")
    print(f"{Config.WHITE}╚══════════════════════════════════════════════════════════════╝{Config.NC}\n")
    
    # File counts
    print(f"{Config.WHITE}File Inventory:{Config.NC}")
    print(f"  LaTeX files (.tex):  {Config.CYAN}{stats.total_tex_files:>6}{Config.NC}")
    print(f"  Main files:          {Config.CYAN}{stats.total_main_files:>6}{Config.NC}")
    print(f"  Image files:         {Config.CYAN}{stats.total_image_files:>6}{Config.NC}")
    print(f"  Compiled PDFs:       {Config.CYAN}{stats.pdf_count:>6}{Config.NC}")
    
    # Size metrics
    print(f"\n{Config.WHITE}Storage:{Config.NC}")
    print(f"  Source files:        {Config.CYAN}{stats.source_size_mb:>8.2f} MB{Config.NC}")
    print(f"  PDF outputs:         {Config.CYAN}{stats.pdf_size_mb:>8.2f} MB{Config.NC}")
    total_size = stats.source_size_mb + stats.pdf_size_mb
    print(f"  Total project:       {Config.CYAN}{total_size:>8.2f} MB{Config.NC}")
    
    # Content metrics
    print(f"\n{Config.WHITE}Content:{Config.NC}")
    print(f"  Total lines:         {Config.CYAN}{stats.total_lines:>8,}{Config.NC}")
    
    if stats.total_tex_files > 0:
        avg_lines = stats.total_lines / stats.total_tex_files
        print(f"  Avg lines/file:      {Config.CYAN}{avg_lines:>8.1f}{Config.NC}")
    
    if stats.pdf_count > 0:
        avg_pdf_size = stats.pdf_size_mb / stats.pdf_count
        print(f"  Avg PDF size:        {Config.CYAN}{avg_pdf_size:>8.2f} MB{Config.NC}")
    
    # Module breakdown
    print(f"\n{Config.WHITE}Modules:{Config.NC}")
    print(f"  Total modules:       {Config.CYAN}{stats.total_modules:>6}{Config.NC}")
    
    if stats.total_modules > 0:
        avg_files = stats.total_main_files / stats.total_modules
        print(f"  Avg files/module:    {Config.CYAN}{avg_files:>6.1f}{Config.NC}")
    
    return 0


# ============================================================================
# CLEAN COMMAND
# ============================================================================

def clean_command(args) -> int:
    """Handle clean operations"""
    
    if args.module:
        clean_module(args.module)
    elif args.all:
        print(f"{Config.YELLOW}Cleaning everything...{Config.NC}")
        clean_build()
        clean_logs()
        clean_pdfs()
        if Config.CACHE_FILE.exists():
            Config.CACHE_FILE.unlink()
            print(f"{Config.GREEN}Cache cleared{Config.NC}")
    elif args.build:
        clean_build()
    elif args.logs:
        clean_logs()
    elif args.pdfs:
        clean_pdfs()
    else:
        # Default: clean build and logs, keep PDFs
        print(f"{Config.YELLOW}Cleaning build artifacts and logs...{Config.NC}")
        clean_build()
        clean_logs()
        if Config.CACHE_FILE.exists():
            Config.CACHE_FILE.unlink()
            print(f"{Config.GREEN}Cache cleared{Config.NC}")
    
    return 0


# ============================================================================
# CLI INTERFACE
# ============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser with comprehensive help"""
    
    parser = argparse.ArgumentParser(
        prog='build.py',
        description="""
╔═══════════════════════════════════════════════════════════════════════╗
║  LaTeX Build System for Multi-Module Academic Projects                ║
╚═══════════════════════════════════════════════════════════════════════╝

A smart build system that compiles LaTeX documents organized in modules
with intelligent caching, parallel compilation, and dependency tracking.

TYPICAL WORKFLOW:
    1. ./build.py info              # See project structure
    2. ./build.py list-modules      # List available modules
    3. ./build.py                   # Build changed files
    4. ./build.py build -m 702      # Build specific module
    5. ./build.py stats             # See detailed statistics
        """,
        epilog="""
EXAMPLES:
    Build all changed files:
        ./build.py
        ./build.py build
    
    Build specific module(s):
        ./build.py build -m HAI702I_Algebre
        ./build.py build -m 702
        ./build.py build -m 702 -m 703
    
    Build range of modules:
        ./build.py build -r 702 710
    
    Force rebuild everything:
        ./build.py build --force
    
    Use 4 parallel workers:
        ./build.py build -j 4
    
    Clean operations:
        ./build.py clean              # Clean build artifacts and logs
        ./build.py clean --all        # Clean everything including PDFs
        ./build.py clean --pdfs       # Clean only PDFs
        ./build.py clean --module HAI702I_Algebre
    
    Information commands:
        ./build.py info               # Project overview with metrics
        ./build.py list-modules       # List all modules
        ./build.py list-files         # List all main files
        ./build.py stats              # Detailed statistics

For more information, see README.md or visit the project repository.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add version
    parser.add_argument('--version', action='version', version='%(prog)s 2.0')
    
    # Subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands (use <command> --help for details)'
    )
    
    # ========================================================================
    # BUILD COMMAND
    # ========================================================================
    build_parser = subparsers.add_parser(
        'build',
        help='Build LaTeX files (default command)',
        description="""
Build LaTeX documents with smart dependency tracking.

Only rebuilds files that have changed or whose dependencies have changed,
unless --force is specified. Supports targeting specific modules or ranges.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    build_parser.add_argument(
        '-m', '--module',
        action='append',
        metavar='MODULE',
        help="""
Build specific module(s). Can be specified multiple times.
Accepts module name, code, or partial match.
Examples: HAI702I_Algebre, 702, algebre
        """.strip()
    )
    
    build_parser.add_argument(
        '-r', '--range',
        nargs=2,
        metavar=('START', 'END'),
        help="""
Build range of modules by code number.
Example: -r 702 710 (builds modules 702 through 710)
        """.strip()
    )
    
    build_parser.add_argument(
        '-j', '--jobs',
        type=int,
        metavar='N',
        help="""
Number of parallel compilation jobs.
Default: CPU_COUNT - 2. Use 1 for sequential compilation.
        """.strip()
    )
    
    build_parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Force rebuild all files, ignoring cache'
    )
    
    # ========================================================================
    # CLEAN COMMAND
    # ========================================================================
    clean_parser = subparsers.add_parser(
        'clean',
        help='Clean build artifacts',
        description="""
Remove build artifacts, logs, and optionally PDFs.

By default, cleans build/ and logs/ directories plus cache file.
Use flags to customize what gets cleaned.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    clean_parser.add_argument(
        '--all',
        action='store_true',
        help='Clean everything: build artifacts, logs, PDFs, and cache'
    )
    
    clean_parser.add_argument(
        '--build',
        action='store_true',
        help='Clean only build/ directory'
    )
    
    clean_parser.add_argument(
        '--logs',
        action='store_true',
        help='Clean only logs/ directory'
    )
    
    clean_parser.add_argument(
        '--pdfs',
        action='store_true',
        help='Clean only pdfs/ directory'
    )
    
    clean_parser.add_argument(
        '--module',
        metavar='MODULE',
        help='Clean specific module by name'
    )
    
    # ========================================================================
    # INFO COMMANDS
    # ========================================================================
    subparsers.add_parser(
        'list-modules',
        help='List all detected modules',
        description='Display all modules found in the src/ directory with file counts.'
    )
    
    subparsers.add_parser(
        'list-files',
        help='List all main LaTeX files',
        description='Display all *_main.tex files discovered in the project.'
    )
    
    subparsers.add_parser(
        'info',
        help='Show project information with metrics',
        description="""
Display comprehensive project information including:
    - Directory configuration
    - Module and file counts
    - Content metrics (lines, file sizes)
    - Output statistics (PDFs generated)
    - Build cache status
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers.add_parser(
        'stats',
        help='Show detailed project statistics',
        description="""
Display detailed project statistics including:
    - Complete file inventory
    - Storage usage breakdown
    - Content metrics (total lines, averages)
    - Module distribution
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Default to build if no command specified
    if not args.command:
        args.command = 'build'
        args.module = None
        args.range = None
        args.jobs = None
        args.force = False
    
    # Execute command
    try:
        if args.command == 'build':
            return build_command(args)
        elif args.command == 'clean':
            return clean_command(args)
        elif args.command == 'list-modules':
            return list_modules_command(args)
        elif args.command == 'list-files':
            return list_files_command(args)
        elif args.command == 'info':
            return info_command(args)
        elif args.command == 'stats':
            return stats_command(args)
        else:
            parser.print_help()
            return 1
    
    except KeyboardInterrupt:
        print(f"\n{Config.YELLOW}Build interrupted by user{Config.NC}")
        return 130  # Standard SIGINT exit code
    except Exception as e:
        print(f"\n{Config.RED}Error: {e}{Config.NC}")
        if '--debug' in sys.argv:
            raise
        return 1


if __name__ == '__main__':
    sys.exit(main())