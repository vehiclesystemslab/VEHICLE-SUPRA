from setuptools import setup, find_packages

setup(
    name="vehicle-supra",
    version="0.2.1",
    author="Roberto Borda Milan",
    author_email="contact@vehiclesystemslab.com",
    description="Coherence-governed architecture for autonomous AI agent networks",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vehiclesystemslab/VEHICLE-SUPRA",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=["numpy>=1.24.0", "scipy>=1.10.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Development Status :: 3 - Alpha",
    ],
    keywords="AI agents autonomous agents coherence tension projection recovery VEHICLE",
)
