# Algorithmics Course Materials Repository

## Overview
This repository contains LaTeX source files and compiled materials for various algorithmics courses:
- HAI702I: Algebra, geometry, transformation, scientific computing
- HAI709I: Foundations of Cryptography for Security
- HAI710I: Foundations of Symbolic AI
- HAI711I: Graphs: Structures and Algorithms
- HAI713I: Logic, Computability, and Complexity
- HAI718I: Probability and Statistics
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
        └── dms/                         # Longer exercise sheets
```

## Prerequisites
- ~~LaTeX distribution (e.g., TeX Live or MiKTeX)~~
- ~~Python~~ (for local pdf building)
- Nothing
- Recommended to have some knowledge of LaTeX

## Building the Documents
The pdfs are now automatically generated on push.
To generate them locally, use the following commands
```bash
# Build all modified documents
./run.py

# Rebuild all documents
./run.py --rebuild-all

# Read the run.py script documentation
./run.py --help
...
```

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the [LICENSE-NAME] - see the [LICENSE](LICENSE) file for details.

## Authors
- [Ivan Lejeune]

## Acknowledgments
- University of Montpellier for access to the various courses
- M. Charlier for his amazing .tex files these ones are inspired from
- All the teachers that made this possible
