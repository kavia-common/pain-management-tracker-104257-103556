from setuptools import setup, find_packages

setup(
    name="pain_management_api",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "python-jose",
        "passlib",
        "python-multipart",
        "asyncpg",
        "fhirpy"
    ]
)
