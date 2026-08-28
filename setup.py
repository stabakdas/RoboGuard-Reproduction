from pathlib import Path
from setuptools import setup, find_packages


PROJECT_DIR = Path(__file__).parent
REQUIREMENTS_FILE = PROJECT_DIR / "requirements.txt"


def read_requirements():
    """Read package dependencies from requirements.txt."""
    requirements = []

    with REQUIREMENTS_FILE.open(encoding="utf-8") as requirements_file:
        for line in requirements_file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if line.startswith(("-e ", "--editable ", "git+", "file:")):
                continue

            requirements.append(line)

    return requirements


# Version history:
# 0.1.0 - Original/reproduction work on Python 3.12
# 0.2.0 - RoboGuard + Gemini
# 0.3.0 - RoboGuard + SPOT + SPINE + Gemini-SPINE

setup(
    name="roboguard_reproduce",
    version="0.3.0",
    description=(
        "RoboGuard reproduction with Gemini integration and "
        "Gemini-enabled SPINE integration"
    ),
    author="Stabak Das",
    author_email="stabak.das@ieee.org",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires="==3.12.*",
    install_requires=read_requirements(),
)


