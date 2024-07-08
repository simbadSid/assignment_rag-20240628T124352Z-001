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

if __name__ == '__main__':
    try:
        config: Config = Config()

        log("Start launching the OpenSearch docker image", "info")

        open_search_docker_image_name       = config.load_config(["open_search", "open_search_docker_image_name"])
        open_search_docker_container_name   = config.load_config(["open_search", "open_search_docker_container_name"])
        open_search_port                    = config.load_config(["open_search", "open_search_port"])
        open_transport_search_port          = config.load_config(["open_search", "open_search_transport_port"])
        open_search_docker_configs          = config.load_config(["open_search", "open_search_docker_configs"])
        open_search_admin_pwd               = config.load_config_secret_key(config_id_key='opensearch_admin_pwd_path')

        container_config = []
        for k, v in open_search_docker_configs.items():
            container_config.append("-e")
            container_config.append(f"{k}={v}")

        subprocess.run(
            [
                "docker", "run", "-d",
                "--name",   open_search_docker_container_name,
                "-p",       f"{open_search_port}:{open_search_port}",
                "-p",       f"{open_transport_search_port}:{open_transport_search_port}",
                "-e",       "discovery.type=single-node",
                "-e",       f"OPENSEARCH_INITIAL_ADMIN_PASSWORD={open_search_admin_pwd}",
                "-e",       "OPENSEARCH_JAVA_OPTS=-Dopensearch.config=/usr/share/opensearch/config/custom_opensearch.yml",
            ]
            +
                container_config
            +
            [
                open_search_docker_image_name
            ],
            check=True  # Ensure that an error is raised if the command fails
        )

    except Exception as e:
        log_error(f"Failed to run the docker image with opensearch: {e}", exception_to_raise=RuntimeError)
