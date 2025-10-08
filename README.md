# Algorithmics Course Materials Repository

## Overview
This repository contains LaTeX source files and compiled materials for various algorithmics courses:
- HAI702I: Algebra, geometry, transformation, scientific computing
- HAI709I: Foundations of Cryptography for Security
- HAI710I: Foundations of Symbolic AI
- HAI711I: Graphs: Structures and Algorithms
- HAI713I: Logic, Computability, and Complexity
- HAI718I: Probability and Statistics (not yet available)
- HAI720I: Efficient Algorithm Programming
- HAI722I: Operations Research

## Repository Structure
```
.
├── build/                               # Build artifacts and intermediate files
├── logs/                                # Compilation logs
├── pdfs/                                # Generated PDF documents
└── src/                                 # Source files
    ├── common/                          # Shared LaTeX resources
    │   ├── environments/                # Custom LaTeX environments
    │   └── macros/                      # Custom LaTeX macros
    └── [course-code]_[course-name]/     # Course-specific materials
        ├── assets/                      # Course assets (images, etc.)
        ├── cours/                       # Lecture notes
        └── tds/                         # Exercise materials
```

## Prerequisites
- LaTeX distribution (e.g., TeX Live or MiKTeX)
- Python (for build automation)
- Git

## Building the Documents
```bash
# Build all documents
./build.py

# Build specific course materials
./build.py build -m 702
...
```

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the [LICENSE-NAME] - see the [LICENSE](LICENSE) file for details.

## Authors
- [Ivan Lejeune]

## Acknowledgments
- University of Montpellier
