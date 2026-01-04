script_content = """
import os
import re
import subprocess
import sys
from pathlib import Path

def get_required_modules(directory):
    imports = set()
    base_path = Path(directory)
    # Scan all .py files in the specified directory
    for py_file in base_path.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                for line in f:
                    # Match 'import module' or 'from module import ...'
                    match = re.match(r"^(?:from|import)\s+([\w\d_]+)", line)
                    if match:
                        imports.add(match.group(1))
        except Exception:
            continue
    return imports

def main():
    # Mapping: Import name -> Pip package name
    MAPPING = {
        "dotenv": "python-dotenv",
        "PIL": "Pillow",
        "posthog": "posthog",
        "boto3": "boto3",
        "botocore": "botocore",
        "structlog": "structlog"
    }

    # Navigate to the project root (assuming script is in /scripts or /)
    project_root = Path(__file__).parent.parent
    app_dir = project_root / "app"
    
    if not app_dir.exists():
        # Fallback to current directory if /app is not found relative to script
        app_dir = Path("./app")
        if not app_dir.exists():
            print(f"❌ Could not find 'app' directory at {app_dir}")
            return

    print(f"🔍 Scanning source code for dependencies in: {app_dir}...")
    required = get_required_modules(app_dir)
    
    # Modules to ignore: internal project files and built-in libraries
    internal_modules = {'app', 'config', 'main', 'core', 'agent', 'tool', 'utils'}
    standard_libs = sys.builtin_module_names
    
    to_check = [m for m in required if m not in standard_libs and m not in internal_modules]

    print(f"📦 Found {len(to_check)} potential external modules.")

    for module in to_check:
        try:
            __import__(module)
        except ImportError:
            pkg_name = MAPPING.get(module, module)
            print(f"⚠️ Missing '{module}'. Installing '{pkg_name}'...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install '{pkg_name}'. Please install it manually.")

    print("\\n🚀 Environment setup complete!")

if __name__ == "__main__":
    main()
"""

# Create 'scripts' directory and write the file
import os
os.makedirs("/content/OpenManus/scripts", exist_ok=True)
with open("/content/OpenManus/scripts/setup_env.py", "w") as f:
    f.write(script_content.strip())

print("✅ Created /content/OpenManus/scripts/setup_env.py successfully!")
