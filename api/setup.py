from setuptools import find_packages, setup
from setuptools_cythonize import get_cmdclass

setup(
    cmdclass=get_cmdclass(),
    name="app",
    version="0.0.1",
    description="My app",
    options={
        "build_ext": {"parallel": 8},
        "build_py": {
            "exclude_cythonize": [
                "*.router*",
                "*.dependencies*",
                "app.src.route*",
                "app.core.api_router*",
            ]
        },
    },
    packages=["app"] + [f"app.{package}" for package in find_packages("./app")],
    include_package_data=True,
    package_data={
        "app.proto": ["*.proto"],  # Adjust the path as needed
    },
)
