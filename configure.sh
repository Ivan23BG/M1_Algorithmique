#!/bin/bash

# ==============================================================================
# CONFIGURE SCRIPT FOR LAUNCHING MAKEFILE WORKFLOW
# ==============================================================================
# Author: Claude Assistant - Ivan Lejeune
# Description: This script prepares the environment for building the LaTeX project
# ==============================================================================

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------
LATEXMK=$(command -v latexmk)
LATEXMK_FLAGS="-pdf -shell-escape -interaction=nonstopmode -halt-on-error"
SRC_DIR="src"
BUILD_DIR="build"
LOGS_DIR="logs"
PDFS_DIR="pdfs"
TEMPLATES_DIR="templates"
MAX_DEPTH=5

# ------------------------------------------------------------------------------
# CHECKING NECESSARY TOOLS
# ------------------------------------------------------------------------------
check_tools() {
    echo "Checking required tools..."

    if [ -z "$LATEXMK" ]; then
        echo "Error: latexmk is not installed. Please install latexmk."
        exit 1
    else
        echo "Found latexmk: $LATEXMK"
    fi
}

# ------------------------------------------------------------------------------
# CHECKING DIRECTORY STRUCTURE
# ------------------------------------------------------------------------------
check_directories() {
    echo "Checking necessary directories..."

    if [ ! -d "$SRC_DIR" ]; then
        echo "Error: Source directory '$SRC_DIR' not found."
        exit 1
    fi

    if [ ! -d "$BUILD_DIR" ]; then
        echo "Warning: Build directory '$BUILD_DIR' does not exist. Creating it..."
        mkdir -p "$BUILD_DIR"
    fi

    if [ ! -d "$LOGS_DIR" ]; then
        echo "Warning: Logs directory '$LOGS_DIR' does not exist. Creating it..."
        mkdir -p "$LOGS_DIR"
    fi

    if [ ! -d "$PDFS_DIR" ]; then
        echo "Warning: PDFs directory '$PDFS_DIR' does not exist. Creating it..."
        mkdir -p "$PDFS_DIR"
    fi
}

# ------------------------------------------------------------------------------
# CHECKING FOR MAIN TEEX FILES
# ------------------------------------------------------------------------------
check_main_tex_files() {
    echo "Looking for main LaTeX files..."

    MAIN_TEX_FILES=$(find "$SRC_DIR" -maxdepth "$MAX_DEPTH" -name "*_main.tex" -not -path "*/$TEMPLATES_DIR/*" 2>/dev/null)

    if [ -z "$MAIN_TEX_FILES" ]; then
        echo "Error: No main LaTeX files found under '$SRC_DIR'."
        exit 1
    else
        echo "Found main LaTeX files:"
        echo "$MAIN_TEX_FILES"
    fi
}

# ------------------------------------------------------------------------------
# CHECKING MODULES DIRECTORY
# ------------------------------------------------------------------------------
check_modules() {
    echo "Checking modules..."

    MODULES=$(find "$SRC_DIR" -type d -maxdepth 1 | sed 's/.*\///')
    
    if [ -z "$MODULES" ]; then
        echo "Error: No modules found in '$SRC_DIR'."
        exit 1
    else
        echo "Found modules:"
        echo "$MODULES"
    fi
}

# ------------------------------------------------------------------------------
# CHECKING LATEXMK INSTALLATION
# ------------------------------------------------------------------------------
check_latexmk() {
    echo "Checking latexmk installation..."

    if ! command -v latexmk &> /dev/null; then
        echo "Error: latexmk is not installed."
        exit 1
    else
        echo "latexmk found at $(command -v latexmk)"
    fi
}

# ------------------------------------------------------------------------------
# RUN CONFIGURE STEPS
# ------------------------------------------------------------------------------
check_tools
check_directories
check_main_tex_files
check_modules
check_latexmk

echo "Configuration completed successfully!"

# ------------------------------------------------------------------------------
# END OF CONFIGURE SCRIPT
# ------------------------------------------------------------------------------
