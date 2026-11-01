#!/usr/bin/env python3
"""
Environment Setup Script for red-tide-algal-bloom-monitoring Skill
Automated environment initialization and dependency installation
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import List, Tuple
import os


class SetupManager:
    """Manages environment setup and dependency installation"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.requirements_file = project_root / "requirements.txt"
        self.config_dir = project_root / "config"
        self.logs_dir = project_root / "logs"
        self.assets_dir = project_root / "assets"

    def check_python_version(self) -> Tuple[bool, str]:
        """Check if Python version is compatible (>=3.8)"""
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            return True, f"Python {version.major}.{version.minor}.{version.micro}"
        return False, f"Python {version.major}.{version.minor}.{version.micro} (requires >=3.8)"

    def install_dependencies(self) -> Tuple[bool, str]:
        """Install dependencies from requirements.txt"""
        if not self.requirements_file.exists():
            return False, "requirements.txt not found"

        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)],
                check=True,
                capture_output=True,
                text=True
            )
            return True, "Dependencies installed successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Installation failed: {e.stderr}"

    def create_directories(self) -> Tuple[bool, str]:
        """Create necessary directories for the project"""
        directories = [
            self.logs_dir,
            self.assets_dir / "diagrams",
            self.assets_dir / "schemas",
            self.assets_dir / "templates",
            self.config_dir
        ]

        created = []
        failed = []

        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                created.append(str(directory.relative_to(self.project_root)))
            except Exception as e:
                failed.append(f"{directory}: {e}")

        if failed:
            return False, f"Failed to create some directories: {failed}"
        return True, f"Created directories: {created}"

    def create_gitignore(self) -> Tuple[bool, str]:
        """Create .gitignore file if it doesn't exist"""
        gitignore_path = self.project_root / ".gitignore"

        if gitignore_path.exists():
            return True, ".gitignore already exists"

        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Project specific
logs/*.log
config/local_config.yaml
*.pyc
.DS_Store

# Test artifacts
.pytest_cache/
.coverage
htmlcov/

# Temporary files
*.tmp
*.bak
*.swp
"""

        try:
            gitignore_path.write_text(gitignore_content)
            return True, "Created .gitignore"
        except Exception as e:
            return False, f"Failed to create .gitignore: {e}"

    # Map of distribution package names to their importable module names.
    # Kept in sync with requirements.txt so verification reflects real usage.
    REQUIRED_PACKAGES = [
        ("PyYAML", "yaml"),
        ("requests", "requests"),
        ("feedparser", "feedparser"),
        ("python-dateutil", "dateutil"),
    ]

    def verify_installation(self) -> Tuple[bool, List[str]]:
        """Verify dependencies declared in requirements.txt are importable.

        Returns a tuple of (success, missing_distribution_names). Each entry in
        the returned missing list is the distribution name (matching
        requirements.txt) so callers can recommend ``pip install <name>``.
        """
        missing = []
        for dist_name, module_name in self.REQUIRED_PACKAGES:
            try:
                __import__(module_name)
            except ImportError:
                missing.append(dist_name)

        if missing:
            return False, missing
        return True, []

    def create_local_config(self) -> Tuple[bool, str]:
        """Create local_config.yaml from example if it doesn't exist"""
        local_config = self.config_dir / "local_config.yaml"
        example_config = self.config_dir / "local_config.example.yaml"

        if local_config.exists():
            return True, "local_config.yaml already exists"

        if example_config.exists():
            try:
                import shutil
                shutil.copy(example_config, local_config)
                return True, "Created local_config.yaml from example"
            except Exception as e:
                return False, f"Failed to copy example config: {e}"

        return False, "local_config.example.yaml not found"

    def run_setup(self) -> bool:
        """Run complete setup process"""
        print("=" * 60)
        print("Red Tide Algal Bloom Monitoring - Environment Setup")
        print("=" * 60)
        print()

        # Check Python version
        print("Checking Python version...")
        version_ok, version_msg = self.check_python_version()
        print(f"  {version_msg}")
        if not version_ok:
            print(f"  ERROR: {version_msg}")
            return False
        print()

        # Create directories
        print("Creating project directories...")
        dirs_ok, dirs_msg = self.create_directories()
        print(f"  {dirs_msg}")
        if not dirs_ok:
            print(f"  ERROR: {dirs_msg}")
        print()

        # Create .gitignore
        print("Creating .gitignore...")
        gitignore_ok, gitignore_msg = self.create_gitignore()
        print(f"  {gitignore_msg}")
        print()

        # Create local config
        print("Creating local configuration...")
        config_ok, config_msg = self.create_local_config()
        print(f"  {config_msg}")
        print()

        # Install dependencies
        print("Installing dependencies...")
        deps_ok, deps_msg = self.install_dependencies()
        print(f"  {deps_msg}")
        if not deps_ok:
            print(f"  ERROR: {deps_msg}")
            print("  You may need to run: pip install -r requirements.txt")
            return False
        print()

        # Verify installation
        print("Verifying installation...")
        verify_ok, missing = self.verify_installation()
        if verify_ok:
            print("  All dependencies installed correctly")
        else:
            print(f"  WARNING: Missing packages: {missing}")
            print("  Some features may not work correctly")
        print()

        # Final summary
        print("=" * 60)
        print("Setup Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Review and customize config/local_config.yaml")
        print("  2. Run tests: python tools/test_knowledge_updater.py")
        print("  3. Test scenarios: python tools/run_test_scenarios.py")
        print()

        return True


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent

    if not (project_root / "CLAUDE.md").exists():
        print("ERROR: Not in valid project directory")
        sys.exit(1)

    manager = SetupManager(project_root)
    success = manager.run_setup()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
