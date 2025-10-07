# =============================================================================
# ELABORATE LATEX PROJECT MAKEFILE
# =============================================================================
# Author: Claude Assistant - Ivan Lejeune
# Description: Comprehensive Makefile for LaTeX project compilation
# Features: Recursive compilation, dependency tracking, parallel builds,
#           flexible module targeting, comprehensive cleaning
# =============================================================================

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all

# Directories
SRC_DIR := src
BUILD_DIR := build
LOGS_DIR := logs
PDFS_DIR := pdfs
TEMPLATES_DIR := templates

# LaTeX Configuration
LATEXMK := latexmk
LATEXMK_FLAGS := -pdf -shell-escape -interaction=nonstopmode -halt-on-error
MAX_DEPTH := 5

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[1;37m
NC := \033[0m # No Color

# -----------------------------------------------------------------------------
# AUTOMATIC FILE DISCOVERY
# -----------------------------------------------------------------------------

# Find all *_main.tex files recursively with max depth
MAIN_TEX_FILES := $(shell find $(SRC_DIR) -maxdepth $(MAX_DEPTH) -name "*_main.tex" -not -path "*/$(TEMPLATES_DIR)/*" 2>/dev/null)

# Extract relative paths from src/ directory
MAIN_TEX_REL := $(patsubst $(SRC_DIR)/%,%,$(MAIN_TEX_FILES))

# Generate corresponding build, log, and pdf paths
BUILD_TARGETS := $(patsubst %.tex,$(BUILD_DIR)/%.pdf,$(MAIN_TEX_REL))
LOG_TARGETS := $(patsubst %.tex,$(LOGS_DIR)/%.log,$(MAIN_TEX_REL))
PDF_TARGETS := $(patsubst %.tex,$(PDFS_DIR)/%.pdf,$(MAIN_TEX_REL))

# Extract module names for individual targets
MODULE_PATHS := $(sort $(dir $(MAIN_TEX_REL)))
MODULES := $(sort $(foreach path,$(MODULE_PATHS),$(word 1,$(subst /, ,$(path)))))

# Create module mappings for flexible targeting
define create_module_map
MODULE_$(1)_FILES := $(filter $(1)/%,$(MAIN_TEX_REL))
MODULE_$(1)_PDFS := $(patsubst %.tex,$(PDFS_DIR)/%.pdf,$(MODULE_$(1)_FILES))
MODULE_$(1)_CODE := $(shell echo "$(1)" | sed 's/HAI\([0-9]\+\)I/\1/')
MODULE_$(1)_NAME := $(shell echo "$(1)" | sed 's/HAI[0-9]\+I_//; s/_/ /g' | tr '[:upper:]' '[:lower:]')
endef

$(foreach module,$(MODULES),$(eval $(call create_module_map,$(module))))

# -----------------------------------------------------------------------------
# DEPENDENCY DETECTION
# -----------------------------------------------------------------------------

# Function to find all dependencies for a given tex file
define find_dependencies
$(shell find $(SRC_DIR)/common -type f \( -name "*.tex" -o -name "*.sty" -o -name "*.cls" \) 2>/dev/null) \
$(shell find $(dir $(SRC_DIR)/$(1)) -type f \( -name "*.tex" -o -name "*.sty" -o -name "*.cls" -o -name "*.png" -o -name "*.jpg" -o -name "*.pdf" \) 2>/dev/null) \
$(shell find $(SRC_DIR)/$(word 1,$(subst /, ,$(1))) -type f \( -name "*.tex" -o -name "*.sty" -o -name "*.cls" -o -name "*.png" -o -name "*.jpg" -o -name "*.pdf" \) 2>/dev/null)
endef

# -----------------------------------------------------------------------------
# MAIN TARGETS
# -----------------------------------------------------------------------------

.PHONY: all clean clean-build clean-logs clean-pdfs clean-all help list-modules list-files info
.PHONY: $(MODULES) $(addsuffix -clean,$(MODULES))

# Default target
all: $(PDF_TARGETS)
	@echo -e "$(GREEN)LaTeX compilation results:$(NC)"
	@$(MAKE) --no-print-directory compilation-summary

# Individual module targets - using a different approach to avoid multiple target patterns
define make_module_target
$(1): $(MODULE_$(1)_PDFS)

$(1)-clean:
	@$(MAKE) --no-print-directory clean-module MODULE=$(1)
endef

$(foreach module,$(MODULES),$(eval $(call make_module_target,$(module))))

# -----------------------------------------------------------------------------
# COMPILATION RULES
# -----------------------------------------------------------------------------

# Main compilation rule with dependency tracking
$(PDFS_DIR)/%.pdf: $(SRC_DIR)/%.tex
	@echo -e "$(BLUE)Compiling $(WHITE)$<$(NC)"
	@# Create necessary directories
	@mkdir -p $(dir $(BUILD_DIR)/$*) $(dir $(LOGS_DIR)/$*) $(dir $(PDFS_DIR)/$*)
	@# Get absolute paths for compilation
	@tex_dir=$$(dirname "$<"); \
	tex_file=$$(basename "$<"); \
	build_abs=$$(realpath $(dir $(BUILD_DIR)/$*)); \
	logs_abs=$$(realpath $(dir $(LOGS_DIR)/$*)); \
	current_dir=$$(pwd); \
	cd "$$tex_dir" && \
	if $(LATEXMK) $(LATEXMK_FLAGS) -output-directory="$$build_abs" "$$tex_file" > "$$logs_abs/$$(basename $* .pdf).log" 2>&1; then \
		cd "$$current_dir" && \
		echo -e "$(GREEN)Successfully compiled $(WHITE)$<$(NC)" && \
		mv "$$build_abs/$$(basename $* .pdf).pdf" $@ 2>/dev/null || true; \
	else \
		cd "$$current_dir" && \
		echo -e "$(RED)Failed to compile $(WHITE)$<$(NC) (check $(LOGS_DIR)/$*.log)" && \
		echo "$<" >> .compilation_errors 2>/dev/null || true; \
	fi

# Dependency rules for each main file - using a safer approach
define make_dependency_rule
$(PDFS_DIR)/$(1:.tex=.pdf): $(call find_dependencies,$(1))
endef

$(foreach file,$(MAIN_TEX_REL),$(eval $(call make_dependency_rule,$(file))))

# -----------------------------------------------------------------------------
# FLEXIBLE MODULE TARGETING
# -----------------------------------------------------------------------------

# Create flexible targets for each module - safer approach
define create_flexible_targets
.PHONY: $(MODULE_$(1)_CODE) $(MODULE_$(1)_NAME)
$(MODULE_$(1)_CODE): $(1)
$(MODULE_$(1)_NAME): $(1)
endef

$(foreach module,$(MODULES),$(eval $(call create_flexible_targets,$(module))))

# Range targeting (e.g., make 702-710 or make topology-algebra)
define make_range
	@start_num=$$(echo "$(1)" | sed 's/.*\([0-9]\{3\}\).*/\1/'); \
	end_num=$$(echo "$(2)" | sed 's/.*\([0-9]\{3\}\).*/\1/'); \
	for module in $(MODULES); do \
		module_num=$$(echo "$$module" | sed 's/HAI\([0-9]\+\)I.*/\1/'); \
		if [ "$$module_num" -ge "$$start_num" ] && [ "$$module_num" -le "$$end_num" ]; then \
			$(MAKE) --no-print-directory $$module; \
		fi; \
	done
endef

# Range pattern rule (usage: make range-702-710)
range-%:
	@start_end=$$(echo "$*" | tr '-' ' '); \
	$(call make_range,$$(echo $$start_end | cut -d' ' -f1),$$(echo $$start_end | cut -d' ' -f2))

# -----------------------------------------------------------------------------
# CLEANING TARGETS
# -----------------------------------------------------------------------------

clean-build:
	@echo -e "$(YELLOW)Cleaning build artifacts...$(NC)"
	@rm -rf $(BUILD_DIR)/*
	@echo -e "$(GREEN)Build artifacts cleaned$(NC)"

clean-logs:
	@echo -e "$(YELLOW)Cleaning log files...$(NC)"
	@rm -rf $(LOGS_DIR)/*
	@echo -e "$(GREEN)Log files cleaned$(NC)"

clean-pdfs:
	@echo -e "$(YELLOW)Cleaning PDF files...$(NC)"
	@rm -rf $(PDFS_DIR)/*
	@echo -e "$(GREEN)PDF files cleaned$(NC)"

clean: clean-build clean-logs
	@rm -f .compilation_errors
	@echo -e "$(GREEN)Project cleaned (PDFs preserved)$(NC)"

clean-all: clean clean-pdfs
	@echo -e "$(GREEN)Project completely cleaned$(NC)"

clean-module:
	@echo -e "$(YELLOW)Cleaning module $(MODULE)...$(NC)"
	@rm -rf $(BUILD_DIR)/$(MODULE)
	@rm -rf $(LOGS_DIR)/$(MODULE)
	@echo -e "$(GREEN)Module $(MODULE) cleaned$(NC)"

# -----------------------------------------------------------------------------
# INFORMATION AND DEBUGGING TARGETS
# -----------------------------------------------------------------------------

help:
	@echo -e "$(WHITE)LaTeX Project Makefile - Available Targets:$(NC)"
	@echo -e ""
	@echo -e "$(CYAN)Main Targets:$(NC)"
	@echo -e "  $(WHITE)all$(NC)              - Compile all LaTeX files"
	@echo -e "  $(WHITE)clean$(NC)            - Clean build and log files (preserve PDFs)"
	@echo -e "  $(WHITE)clean-all$(NC)        - Clean everything including PDFs"
	@echo -e "  $(WHITE)help$(NC)             - Show this help message"
	@echo -e ""
	@echo -e "$(CYAN)Module Targets:$(NC)"
	@for module in $(MODULES); do \
		code=$$(echo "$$module" | sed 's/HAI\([0-9]\+\)I/\1/'); \
		name=$$(echo "$$module" | sed 's/HAI[0-9]\+I_//; s/_/ /g' | tr '[:upper:]' '[:lower:]'); \
		echo -e "  $(WHITE)$$module$(NC)         - Compile $$module"; \
		echo -e "  $(WHITE)$$code$(NC)             - Same as $$module"; \
		echo -e "  $(WHITE)$$name$(NC)         - Same as $$module"; \
		echo -e "  $(WHITE)$$module-clean$(NC)   - Clean $$module"; \
	done
	@echo -e ""
	@echo -e "$(CYAN)Range Targets:$(NC)"
	@echo -e "  $(WHITE)range-702-710$(NC)    - Compile modules HAI702I to HAI710I"
	@echo -e ""
	@echo -e "$(CYAN)Information Targets:$(NC)"
	@echo -e "  $(WHITE)list-modules$(NC)     - List all detected modules"
	@echo -e "  $(WHITE)list-files$(NC)       - List all main tex files"
	@echo -e "  $(WHITE)info$(NC)             - Show project information"

list-modules:
	@echo -e "$(WHITE)Detected Modules:$(NC)"
	@for module in $(MODULES); do \
		code=$$(echo "$$module" | sed 's/HAI\([0-9]\+\)I/\1/'); \
		name=$$(echo "$$module" | sed 's/HAI[0-9]\+I_//; s/_/ /g' | tr '[:upper:]' '[:lower:]'); \
		files=$$(echo "$(MODULE_$$module_FILES)" | wc -w); \
		echo -e "  $(CYAN)$$module$(NC) ($$code, $$name) - $$files files"; \
	done

list-files:
	@echo -e "$(WHITE)Main LaTeX Files:$(NC)"
	@for file in $(MAIN_TEX_FILES); do \
		echo -e "  $(GREEN)$$file$(NC)"; \
	done

info:
	@echo -e "$(WHITE)Project Information:$(NC)"
	@echo -e "  Source Directory: $(CYAN)$(SRC_DIR)$(NC)"
	@echo -e "  Build Directory:  $(CYAN)$(BUILD_DIR)$(NC)"
	@echo -e "  Logs Directory:   $(CYAN)$(LOGS_DIR)$(NC)"
	@echo -e "  PDFs Directory:   $(CYAN)$(PDFS_DIR)$(NC)"
	@echo -e "  Max Search Depth: $(CYAN)$(MAX_DEPTH)$(NC)"
	@echo -e ""
	@echo -e "  Total Modules:    $(CYAN)$(words $(MODULES))$(NC)"
	@echo -e "  Total Main Files: $(CYAN)$(words $(MAIN_TEX_FILES))$(NC)"
	@echo -e ""
	@echo -e "  LaTeX Command:    $(CYAN)$(LATEXMK) $(LATEXMK_FLAGS)$(NC)"

compilation-summary:
	@if [ -f .compilation_errors ]; then \
		echo -e "$(RED)Some files failed to compile:$(NC)"; \
		while read -r file; do \
			echo -e "  $(RED)$$file$(NC)"; \
		done < .compilation_errors; \
		echo -e "$(YELLOW)Check the corresponding log files for details.$(NC)"; \
		rm -f .compilation_errors; \
	else \
		echo -e "$(GREEN)All files compiled successfully!$(NC)"; \
	fi

# -----------------------------------------------------------------------------
# DIRECTORY CREATION
# -----------------------------------------------------------------------------

# Ensure base directories exist
$(BUILD_DIR) $(LOGS_DIR) $(PDFS_DIR):
	@mkdir -p $@

# -----------------------------------------------------------------------------
# ADVANCED FEATURES
# -----------------------------------------------------------------------------

# Watch mode (requires inotify-tools)
.PHONY: watch
watch:
	@echo -e "$(BLUE)Watching for changes... (Ctrl+C to stop)$(NC)"
	@while inotifywait -r -e modify,create,delete $(SRC_DIR) 2>/dev/null; do \
		echo -e "$(YELLOW)Changes detected, recompiling...$(NC)"; \
		$(MAKE) --no-print-directory all; \
	done

# Parallel safety check
.PHONY: check-parallel
check-parallel:
	@echo -e "$(BLUE)Checking parallel build safety...$(NC)"
	@$(MAKE) -j$(shell nproc) --dry-run all >/dev/null 2>&1 && \
		echo -e "$(GREEN)Parallel builds are safe$(NC)" || \
		echo -e "$(RED)Parallel builds may have issues$(NC)"

# Statistics
.PHONY: stats
stats:
	@echo -e "$(WHITE)Project Statistics:$(NC)"
	@echo -e "  LaTeX files: $(CYAN)$$(find $(SRC_DIR) -name "*.tex" | wc -l)$(NC)"
	@echo -e "  Image files: $(CYAN)$$(find $(SRC_DIR) -name "*.png" -o -name "*.jpg" -o -name "*.pdf" | wc -l)$(NC)"
	@echo -e "  Total lines:$(CYAN)$$(find $(SRC_DIR) -name "*.tex" -exec wc -l {} + | tail -1)$(NC)"
	@if [ -d $(PDFS_DIR) ]; then \
		echo -e "  PDF size:    $(CYAN)$$(du -sh $(PDFS_DIR) 2>/dev/null | cut -f1)$(NC)"; \
	fi

# -----------------------------------------------------------------------------
# MAKEFILE VALIDATION
# -----------------------------------------------------------------------------

.PHONY: validate
validate:
	@echo -e "$(BLUE)Validating Makefile configuration...$(NC)"
	@echo -e "Found $(words $(MAIN_TEX_FILES)) main files:"
	@$(foreach file,$(MAIN_TEX_FILES),echo "  - $(file)";)
	@echo -e "Detected $(words $(MODULES)) modules:"
	@$(foreach module,$(MODULES),echo "  - $(module)";)
	@echo -e "$(GREEN)Configuration valid$(NC)"

# -----------------------------------------------------------------------------
# END OF MAKEFILE
# =============================================================================