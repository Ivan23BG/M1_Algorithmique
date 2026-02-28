# Algorithmics Course Materials Repository

## Overview
This repository contains LaTeX source files and compiled materials for various algorithmics courses:
- HAI7XXI: Legacy files on various courses from semester 7
- HAI820I: Operational Research 2
- HAI808I: Calculability 2
- HAI807I: Formal calculus

## Repository Structure
```
.
├── build/                               # Build artifacts and intermediate files
├── legacy/                              # Legacy files for previous courses
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
This project is licensed under the [CC-BY-SA-4.0 LICENSE] - see the [LICENSE](LICENSE) file for details.

## Authors
- [Ivan Lejeune]

## Acknowledgments
- University of Montpellier for access to the various courses
- M. Charlier for his amazing .tex files these ones are inspired from
- All the teachers that made this possible
# M1_TER
