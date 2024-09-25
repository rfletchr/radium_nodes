from setuptools import setup, find_namespace_packages


setup(
    name="radium",
    version="0.0.0",
    description="A no frills node-based editor for python / PySide6",
    packages=find_namespace_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["PySide6", "qtawesome"],
    entry_points={"console_scripts": ["radium-demo=radium.demo.__main__:main"]},
)
