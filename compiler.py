import os
import shutil
# Step 1: find all the relevant files

def find_files_with_extension(directory, extension, exclude_patterns=None):
    if exclude_patterns is None:
        exclude_patterns = []
    matched_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                file_path = os.path.join(root, file)
                if not any(pattern in file_path for pattern in exclude_patterns):
                    matched_files.append(file_path)
    return matched_files


def display_files(files):
    for file in files:
        print(file)


def get_job_name(file):
    base_name = os.path.basename(file)
    job_name = os.path.splitext(base_name)[0]
    return job_name


def get_directory(file):
    return os.path.dirname(file)


def get_build_directory(file):
    """Takes the directory of the file and replaces 'src' with 'build'.
    For example, if the file is in '/path/to/src/chapter1/', it returns '/path/to/build/chapter1/'.
    It then adds '../' to navigate up to the very top
    so "src/xx/yy/" becomes "../../build/xx/yy/"
    """
    dir_path = get_directory(file)
    parts = dir_path.split(os.sep)
    build_parts = []
    for part in parts:
        if part == "src":
            build_parts.append("build")
        else:
            build_parts.append(part)
    # Add '../' to navigate up to the very top
    depth = len(parts) - parts.index("src") - 1 if "src" in parts else 0
    build_path = os.sep.join(build_parts)
    build_path = build_path.replace("./build", "build")
    ensure_dir = os.sep.join([".."] * (depth + 1) + [build_path])
    os.makedirs(ensure_dir, exist_ok=True)
    return os.sep.join([".."] * (depth + 1) + [build_path])


def get_pdf_directory(file):
    dir_path = get_directory(file)
    parts = dir_path.split(os.sep)
    build_parts = []
    for part in parts:
        if part == "src":
            build_parts.append("pdfs")
        else:
            build_parts.append(part)
    # Add '../' to navigate up to the very top
    depth = len(parts) - parts.index("src") - 1 if "src" in parts else 0
    build_path = os.sep.join(build_parts)
    build_path = build_path.replace("./pdfs", "pdfs")
    ensure_dir = os.sep.join([".."] * (depth + 1) + [build_path])
    os.makedirs(ensure_dir, exist_ok=True)
    return os.sep.join([".."] * (depth + 1) + [build_path])


def get_log_directory(file):
    dir_path = get_directory(file)
    parts = dir_path.split(os.sep)
    build_parts = []
    for part in parts:
        if part == "src":
            build_parts.append("logs")
        else:
            build_parts.append(part)
    # Add '../' to navigate up to the very top
    depth = len(parts) - parts.index("src") - 1 if "src" in parts else 0
    build_path = os.sep.join(build_parts)
    build_path = build_path.replace("./logs", "logs")
    ensure_dir = os.sep.join([".."] * (depth + 1) + [build_path])
    os.makedirs(ensure_dir, exist_ok=True)
    return os.sep.join([".."] * (depth + 1) + [build_path])


# Step 2: navigate to their directories and run a command then return to the original directory
def run_command_on_files(files, command):
    success = 0
    for file in files:
        original_directory = os.getcwd()
        dir_path = os.path.dirname(file)
        os.chdir(dir_path)
        tmp = command(file)
        success = max(success, tmp)
        os.chdir(original_directory)
    return success


def compile_latex(file):
    return_code = os.system(f"latexmk -pdf -shell-escape -interaction=nonstopmode -halt-on-error -outdir={get_build_directory(file)} {get_job_name(file)}.tex > NUL 2>&1")
    # if return_code != 0:
    #     print(f"Failed to compile {file} to PDF.")
    #     return
    # print(f"Successfully compiled {file} to PDF.")
    # Copy the PDF to the pdfs directory if it exists
    
    build_pdf_path = os.path.join(get_build_directory(file), f"{get_job_name(file)}.pdf")
    pdfs_dir = get_pdf_directory(file)
    os.makedirs(pdfs_dir, exist_ok=True)
    target_pdf_path = os.path.join(pdfs_dir, f"{get_job_name(file)}.pdf")
    if os.path.exists(build_pdf_path):
        shutil.copy(build_pdf_path, target_pdf_path)
    # Move the log files to the logs directory
    logs_dir = get_log_directory(file)
    os.makedirs(logs_dir, exist_ok=True)
    log_files = os.path.join(get_build_directory(file), f"{get_job_name(file)}.log")
    if os.path.exists(log_files):
        shutil.move(log_files, os.path.join(logs_dir, f"{get_job_name(file)}.log"))
    
    return return_code


if __name__ == "__main__":
    search_directories = ["./"]  # You can change this to any directory you want to search
    exclude_patterns = ["legacy", "templates", "tmp", "temp"]  # Add any patterns you want to exclude
    match_patterns = ["_main.tex"]  # Add any patterns you want to specifically match

    found_files = []
    for directory in search_directories:
        for pattern in match_patterns:
            found_files.extend(find_files_with_extension(directory, pattern, exclude_patterns))

    print("Found the following files to compile:")
    display_files(get_directory(file) for file in found_files)
    
    success = run_command_on_files(found_files, compile_latex)
    if success == 0:
        print("All files compiled successfully.")
    else:
        print("Some files failed to compile.")