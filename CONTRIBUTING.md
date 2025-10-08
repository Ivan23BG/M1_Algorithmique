# Contributing to Algorithmics Course Materials

## Welcome!
Thank you for considering contributing to our algorithmics course materials! This document provides guidelines and instructions for contributing.

## How Can I Contribute?

### Reporting Issues
- Use the issue tracker to report problems
- Describe the issue in detail
- Include minimal examples that demonstrate the problem
- Specify which course and document the issue relates to

### Suggesting Enhancements
- Use the issue tracker to suggest improvements
- Explain why the enhancement would be useful
- Provide examples if possible

### Pull Requests
1. Fork the repository
2. Create a new branch (`git checkout -b feature/YourFeature`)
3. Make your changes
4. Run the build system to ensure everything compiles
5. Commit your changes (`git commit -m "Add some feature"`)
6. Push to the branch (`git push origin feature/YourFeature`)
7. Create a Pull Request

## Style Guidelines

### LaTeX Guidelines
- Use 4 spaces for indentation
- Place each sentence on a new line (makes Git diffs more readable)
- Use meaningful labels for equations, figures, and references
- Follow the naming convention for files:
  - Course files: `chapter_XX.tex`
  - Exercise sheets: `td_XX.tex`
  - Main files: `XX_main.tex`

### Example of Good LaTeX Style
```latex
\begin{theorem}[Fundamental Theorem of Calculus]\label{thm:ftc}
    Let \(f\) be continuous on \(\ff{a,b}\) and let \(F\) be an antiderivative of \(f\).
    Then:
    \begin{equation*}
        \int_a^b f(x)\der x = F(b) - F(a)
    \end{equation*}
\end{theorem}
```

### File Organization
- Place all images in the appropriate `assets/` directory
- Use relative paths in includes
- Keep course-specific macros in the course's `assets/` directory
- Place shared macros in `src/common/macros/`

## Building Documents

### Prerequisites
- Complete TeX Live or MiKTeX installation
- Python
- Git

### Build Commands
```bash
# Build all materials
./build.py
```

## Questions?
Feel free to contact [Ivan Lejeune](mailto:ivan.lejeune@etu.umontpellier.fr) with any questions or concerns.
