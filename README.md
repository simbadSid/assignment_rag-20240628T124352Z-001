# Financial Insights Project

## Overview

This project provides a system for handling financial insights using Large Language Models (LLMs). 
The LLMs are used in this project to process financial queries and generate insightful responses to user's text queries.

The project integrates OpenSearch, an open-source search and analytics engine, for storing and retrieving financial data. 
The OpenSearch index acts as a database that efficiently handles and searches through the financial data for different companies. 
It stores financial documents and allows for quick retrieval of relevant data based on user queries.

The project implements a web front interface enabling users to interact with the system by posing financial questions. 
The LLM processes these questions, retrieves the necessary data from the created index, and generates detailed and accurate responses.


## Solution's principle

<p float="left">
  <img src="/data/documentation/chart.png"    width="600" />
</p>

## Setup Instructions

### Project Setup

To set up the virtual environment and install dependencies, follow these steps:

1. **Clone the repository**
   ```sh
   git clone <project URL>
   ```
2. **Create a virtual environment**
   ```sh
   python -m venv env
   ```
3. **Activate the virtual environment**
   ```sh
   source env/bin/activate
   ```
4. **Install the project and all its dependencies in editable mode (using ./setup.py)**
   ```sh
   pip install -e .
   ```
5. **Set your personal keys:**
Set the OpenAI API key and OpenSearch admin password in the files:
   ```sh
    ./config/keys/openai_api_key.txt
    ./config/keys/opensearch_admin_password.txt
    ```

### Configuration

Edit the `config/config.json` file with your specific paths, database credentials, and other configuration details specific to your environment.

## Directory Structure

- **config/**: Contains the configuration file `config.json` to be edited with your specific paths, database credentials, and other configuration details.
- **data/**: Directory for storing financial data, metrics, and templates.
  - **company_data/**: Financial data files (1 for each company) used to to fetch data for the RAG answer.
  - **metrics/**: Contains the financial indicators to be used in evaluating a company.
  - **templates/**: Contains the templates of the answers to be returned by each LLM.
- **src/**: Source code for the project.
  - **db_scripts/**: Scripts for creating and updating the OpenSearch index.
  - **models/**: Contains the LLM model handler.
  - **web_app/**: Contains the web application files.
  - **utils/**: Utility functions used across the project.
- **test/**: Contains unit and non-regression tests and sample test questions.
- **README.md**: This readme file.
- **.dockerignore**: Files to ignore in Docker builds.

## Running the Project

### Database Creation and Population

1. **Run OpenSearch using Docker**
   ```sh
   python src/db_scripts/run_opensearch_container.py
   ```

2. **Verify OpenSearch is running**
   ```sh
   password=$(cat config/keys/opensearch_admin_password.txt)
   curl -X GET -k -u admin:"$password" https://localhost:9200/
   ```

3. **Create the OpenSearch index**
   ```sh
   python src/db_scripts/create_index_script.py
   ```

4. **Upload documents to the index**
   ```sh
   python src/db_scripts/update_index_script.py
   ```

### Web Front

1. **Start the web application**
   ```sh
   uvicorn src.web_app.app:app --reload
   ```

### Docker Setup

1. **Build the Docker image**
   ```sh
   docker build -t financial_insights .
   ```

2. **Run the Docker container**
   ```sh
   docker run -p 8000:8000 financial_insights
   ```

### Interact with the Web Front

1. **Access the API using a web browser or API client**:

   - Open your web browser and navigate to:
     ```
     http://localhost:8000/docs
     ```
     This will open the interactive API documentation provided by FastAPI, where you can test the endpoints.

2. **Sending a query**:
   
   - In the interactive API documentation, find the `POST /query` endpoint.
   - Click on the endpoint to expand it.
   - Click on the "Try it out" button.
   - Enter the following JSON payload in the request body:
     ```json
     {
         "query": "What was the total revenue for the company in FY 2023?",
         "company_id": 123
     }
     ```
   - Click the "Execute" button to send the request.

3. **View the response**:
   - The response will be displayed below the request area, showing the financial insights or answers to your query.

Alternatively, you can use an API client like Postman to interact with the web front by sending a `POST` request to:
```
http://localhost:8000/query
```
with the JSON payload mentioned above.

Using these instructions, you can interact with the web front via a web browser or an API client to send queries and receive financial insights.

## Documentation Generation

To generate documentation from the code comments, follow these steps:

1. **Create or empty the `./doc` directory**
   ```sh
   mkdir -p doc && rm -rf doc/*
   ```

### Running Tests

To run the tests, use `pytest`:

1. **Run the tests**
   ```sh
   pytest
   ```
#TODO specify the tests implemented


### Generate documentation**
   ```sh
   pydoc -w src
   ```

This will generate HTML documentation files from the Python docstrings in the `src` directory and place them in the `./doc` directory.
