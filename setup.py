from setuptools import setup, find_packages

setup(
    name='financial_insights',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'fastapi==0.95.2',
        'uvicorn==0.22.0',
        'opensearch-py==2.0.0',
        'pydantic==1.10.11',
        'langchain==0.0.189',
        'pytest==7.3.1'
    ],
)
