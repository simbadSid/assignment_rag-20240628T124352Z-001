from setuptools import setup, find_packages

src_directory = 'src'

setup(
    name='financial_insights',
    version='0.1',
    packages=find_packages(where=src_directory),
    package_dir={'': src_directory},
    install_requires=[
        'fastapi==0.95.2',
        'uvicorn==0.22.0',
        'opensearch-py==2.0.0',
        'pydantic==1.10.11',
        'langchain==0.0.332',
        'pytest==7.3.1',
        'pytest',
        'openai==0.27.0',
        'httpx'
    ],
)
