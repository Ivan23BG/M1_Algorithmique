# Custom Python program to compile specific LaTeX files in my project


# Step 1 --- Get a list of all files in the current directory and subdirectories
import os
all_files = []
for root, dirs, files in os.walk('.'):
    for file in files:
        all_files.append(os.path.join(root, file))

# Step 2 --- Find main LaTeX files to compile in the list
# we are using a naming convention where main files end in '_main.tex'
latex_files_to_compile = [f for f in all_files if f.endswith('_main.tex')]
print("LaTeX files to compile:", latex_files_to_compile)

# Step 3 --- Compile each LaTeX file
# to ensure correct relative paths, we change to the directory of each file before compiling
# directories may be nested, so we handle that as well
# the command we use is latexmk -pdf -shell-escape -interaction=nonstopmode -halt-on-error <filename>
latexmk_options = ['-pdf', '-shell-escape', '-interaction=nonstopmode', '-halt-on-error']
import subprocess
for latex_file in latex_files_to_compile:
    file_dir = os.path.dirname(latex_file)
    original_dir = os.getcwd()
    if file_dir:
        os.chdir(file_dir)
    
    try:
        # Compile the LaTeX file using latexmk with the specified options
        subprocess.run(['latexmk'] + latexmk_options + [os.path.basename(latex_file)], check=True)
        print(f"Successfully compiled {latex_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error compiling {latex_file}: {e}")
    # Change back to the original directory
    os.chdir(original_dir)

# Step 4 --- Move all the build artifacts to a 'build' directory
# a file in src/xx/yy/main.tex will have its artifacts moved to build/xx/yy/
# build files include .aux, .auxlock, .fdb_latexmk, .fls, .out, .pdf, .toc, .bbl, .blg, .log, .nav, .snm
build_dir = 'build'
build_file_extensions = ['.aux', '.auxlock', '.fdb_latexmk', '.fls', '.out', '.pdf', '.toc', '.bbl', '.blg', '.log', '.nav', '.snm']
if not os.path.exists(build_dir):
    os.makedirs(build_dir)
for latex_file in latex_files_to_compile:
    file_dir = os.path.dirname(latex_file)
    base_name = os.path.splitext(os.path.basename(latex_file))[0]
    artifact_dir = os.path.join(build_dir, file_dir)
    if not os.path.exists(artifact_dir):
        os.makedirs(artifact_dir)
    
    # List of common LaTeX build artifacts
    artifacts = [f"{base_name}{ext}" for ext in build_file_extensions]
    for artifact in artifacts:
        artifact_path = os.path.join(file_dir, artifact)
        if os.path.exists(artifact_path):
            os.rename(artifact_path, os.path.join(artifact_dir, artifact))

# Step 5 --- Move the .log to a logs directory
logs_dir = 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
for latex_file in latex_files_to_compile:
    file_dir = os.path.dirname(latex_file)
    base_name = os.path.splitext(os.path.basename(latex_file))[0]
    log_file = f"{base_name}.log"
    log_path = os.path.join(file_dir, log_file)
    if os.path.exists(log_path):
        os.rename(log_path, os.path.join(logs_dir, log_file))

# Step 6 --- Copy all generated PDFs to a 'pdfs' directory
pdfs_dir = 'pdfs'
if not os.path.exists(pdfs_dir):
    os.makedirs(pdfs_dir)
for latex_file in latex_files_to_compile:
    file_dir = os.path.dirname(latex_file)
    base_name = os.path.splitext(os.path.basename(latex_file))[0]
    pdf_file = f"{base_name}.pdf"
    pdf_path = os.path.join(file_dir, pdf_file)
    if os.path.exists(pdf_path):
        os.rename(pdf_path, os.path.join(pdfs_dir, pdf_file))

# Step 7 --- Clean up auxiliary files generated during compilation
for latex_file in latex_files_to_compile:
    file_dir = os.path.dirname(latex_file)
    base_name = os.path.splitext(os.path.basename(latex_file))[0]
    aux_files = [f"{base_name}{ext}" for ext in build_file_extensions if ext != '.pdf' and ext != '.log']
    for aux_file in aux_files:
        aux_path = os.path.join(file_dir, aux_file)
        if os.path.exists(aux_path):
            os.remove(aux_path)
