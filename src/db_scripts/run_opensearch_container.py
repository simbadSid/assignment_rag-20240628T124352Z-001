"""
run_opensearch_container.py

This script launches an OpenSearch docker container using configurations specified in
config/config.json. It handles loading configurations, constructing the docker run
command with appropriate environment variables, and logging the process. If the docker
command fails, it logs an error and raises a RuntimeError.
"""

import subprocess

from utils.log_management import log, log_error
from utils.config_management import Config



# TODO use the .dockerignore file


def run_opensearch_container(config: Config):
    log("Start running the OpenSearch docker image", "info")

    open_search_docker_image_name       = config.load_config(["open_search", "open_search_docker_image_name"])
    open_search_docker_container_name   = config.load_config(["open_search", "open_search_docker_container_name"])
    open_search_host: dict              = config.load_config(["open_search", "open_search_client_config", "hosts"])[0]
    open_transport_search_port          = config.load_config(["open_search", "open_search_transport_port"])
    opensearch_custom_config_path       = config.load_config(["paths",       "opensearch_custom_config_path"])
    open_search_admin_pwd               = config.load_config_secret_key(config_id_key='opensearch_admin_pwd_path')
    open_search_port                    = open_search_host["port"]

    subprocess.run(
        [
            "docker", "run", "-d",
            "--name",   open_search_docker_container_name,
            "-p",       f"{open_search_port}:{open_search_port}",
            "-p",       f"{open_transport_search_port}:{open_transport_search_port}",
            "-e",       f"OPENSEARCH_INITIAL_ADMIN_PASSWORD={open_search_admin_pwd}",
            "-e",       "OPENSEARCH_JAVA_OPTS=-Dopensearch.config=/usr/share/opensearch/config/custom_opensearch.yml",
            '-v',       f"{opensearch_custom_config_path}:/usr/share/opensearch/config/custom_opensearch.yml",

        ]
        +
        [
            open_search_docker_image_name
        ],
        check=True  # Ensure that an error is raised if the command fails
    )


if __name__ == '__main__':
    try:
        _config: Config = Config()
        run_opensearch_container(_config)
    except Exception as e:
        log_error(f"Failed to run the docker image with opensearch: {e}", exception_to_raise=RuntimeError)
