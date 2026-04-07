# AGENTS.md

This repository contains LaTeX course materials for algorithmics courses at the University of Montpellier. PDFs are auto-generated on push via GitHub Actions.

---

## Repository Layout

```
.
├── build/                         # Intermediate LaTeX build artifacts (aux, out, etc.)
├── logs/                          # Compilation logs
├── pdfs/                          # Generated PDF outputs (mirrors src/ structure)
├── src/                           # Source files
│   ├── common/                    # Shared LaTeX resources
│   │   ├── common_header.tex      # Font, language, packages, hyperlinks
│   │   ├── macros/
│   │   │   ├── math.tex           # Math shortcuts: \R, \Z, \N, \C, \Q, \norm, etc.
│   │   │   └── theorems.tex       # Theorem styles and exercise/solution environments
│   │   └── themes/                # Light/dark theme choices
│   └── HAI820I_Complements_RO/    # Course module (example)
│       ├── assets/                # Course-specific macros, TikZ, module_header.tex
│       ├── tds/                   # Exercise sheets (td_1.tex, td_2.tex, ...)
│       │   ├── light_main.tex     # Light-theme variant
│       │   ├── dark_main.tex      # Dark-theme variant
│       │   └── exos/              # Individual exercises (exo_01.tex, exo_02.tex, ...)
│       └── dms/                   # Longer homework assignments
├── templates/                     # Template files to copy from
│   ├── td_main.tex                # Main exercise sheet template
│   ├── td_XX.tex                  # TD section template
│   └── generate_files.py          # Script to scaffold exercise files
├── run.py                         # Main build script (finds and compiles all _main.tex)
└── .venv/                         # Python virtual environment (dev only)
```

---

## Build / Lint / Test Commands

### Build All PDFs

```bash
python3 run.py
```

Compiles all `*_main.tex` files under `src/`, skipping `legacy/`, `templates/`, `tmp/`, `temp/`. Uses `latexmk -pdf -shell-escape -interaction=nonstopmode -halt-on-error` and runs up to 8 parallel workers.

### Rebuild All PDFs (force)

```bash
python3 run.py --rebuild-all   # (not implemented — currently same as above)
```

The script currently does not accept `--rebuild-all`; all builds are incremental via latexmk. To force-rebuild, delete the `build/` directory first:

```bash
rm -rf build/ && python3 run.py
```

### Build a Single PDF

```bash
cd src/HAI820I_Complements_RO/tds/
latexmk -pdf -shell-escape -interaction=nonstopmode -halt-on-error light_main.tex
```

### Generate Exercise Scaffolds

```bash
cd templates/
python3 generate_files.py
```

Creates `exo_01.tex` through `exo_35.tex` (skipping `exo_02`) in the current directory if they don't exist.

### Environment Check

```bash
./configure
```

Checks for `latexmk`, required directories, and main TeX files.

### Linting / Type Checking

There is **no linting or type checking** configured for this project. The only Python tooling present is the virtual environment (`.venv/`). If adding Python scripts:

- Use `ruff` for linting (if installed)
- Use `mypy` for type checking (if installed)
- No test framework is currently configured

---

## Code Style

### LaTeX Style

- **Indentation**: 4 spaces for block-level indentation. LaTeX macros and environments are typically not indented (as in the existing codebase).
- **Line breaks**: Each sentence on its own line. This makes Git diffs and version control much easier to read.
  ```latex
  \begin{enumerate}
      \item \textbf{Identification de l'élément neutre}:
          Quel est l'élément neutre \(e\) de ce groupe?
          Justifiez votre réponse en observant les lignes et colonnes du tableau.
  \end{enumerate}
  ```
- **Comments**: Use `% ----- Consignes exo N ----- %` and `% ----- Solutions exo N ----- %` to delimit exercise content and solutions, respectively.
- **Labels**: Use meaningful labels following the pattern `sec:name-number`, `subsec:name-number`, `thm:name-number`, `eq:name-number`.
- **No hardcoded text color** — use named semantic colors defined in `common_header.tex` (`astral`, `verdant`, etc.) or theme choices.

### File Naming Conventions

| File type              | Pattern                        | Example                            |
|------------------------|--------------------------------|------------------------------------|
| Main document          | `{type}_main.tex`              | `light_main.tex`, `dark_main.tex`  |
| Exercise sheet         | `td_{N}.tex`                   | `td_1.tex`, `td_2.tex`             |
| Individual exercise    | `exo_{NN}.tex`                 | `exo_01.tex`, `exo_29.tex`         |
| Section block          | `td_XX.tex` (template)         | `td_XX.tex`                        |
| Module header          | `module_header.tex`            | `assets/module_header.tex`         |
| TikZ figures           | `{sheet}_ex{NN}_f{N}.tex`      | `td1_ex15_f1.tex`                  |
| Exercise Python files  | `exo{NN}_f{NN}.py`             | `exo04_f01.py`, `exo07_f02.py`     |

### Package Imports

- Put all shared packages and settings in `src/common/common_header.tex`.
- Course-specific packages and macros go in `src/{course}/assets/module_header.tex`.
- Avoid duplicating package loads across files.

### Math Macro Conventions

- Follow the naming in `src/common/macros/math.tex`:
  - `\R`, `\Z`, `\N`, `\C`, `\Q` for number sets
  - `\ff`, `\oo`, `\of`, `\fo` for intervals (closed closed, open open, open closed, closed open)
  - `\norm`, `\n{}`, `\nn{}` for norms
  - `\der`, `\p`, `\dpar{}{}` for calculus notation
  - `\vect`, `\ker`, `\det`, `\tr`, `\im`, `\re`, `\id` for linear algebra
  - `\abs` for absolute value
- Use `\providecommand` or `\DeclareRobustCommand` for new operators to avoid redefinition errors.
- Use `\RedeclareMathOperator` (defined in `common_header.tex`) to safely redefine standard operators.

### Theorem / Exercise Environments

- Use `\iftoggle{showsolutions}{...}{...}` to wrap all solutions (see `exo_01.tex` for the canonical pattern).
- Use `\begin{td-exo}[title] ... \end{td-exo}` for exercises, numbered via `tdcounter` (reset per `\section`).
- Use `\begin{td-sol} ... \end{td-sol}` for solutions.
- For course-specific theorem environments, use the `\mytheorem` macro defined in `theorems.tex`:
  ```latex
  \mytheorem{name}{Display Name}{color}{counter parent}{counter type}
  ```
  See `src/HAI820I_Complements_RO/assets/module_header.tex` for examples.

### Git Workflow

- The GitHub Actions workflow builds on every push to `main`/`develop` and on PRs to `main`.
- Generated PDFs are committed back to the repo with message `"Update generated PDFs [skip ci]"`.
- Releases are created on every push to `main` with all PDFs attached.
- Always run `python3 run.py` locally before opening a PR to catch compilation errors.

---

## Contributing Checklist

Before submitting a PR:

1. New `\main.tex` file? Add it under `src/` (not in `legacy/`).
2. New exercise file? Use `templates/generate_files.py` or copy `templates/td_XX.tex`.
3. Compile: `python3 run.py` — all files must build without error.
4. Check the `pdfs/` directory for the generated output.
5. No changes to `pdfs/` are committed manually — they are auto-generated.
6. Keep course-specific content in the course module; shared macros go in `src/common/`.
