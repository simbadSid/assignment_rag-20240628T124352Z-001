import subprocess

from utils.log_management import log, log_error
from utils.config_management import Config

if __name__ == '__main__':
    try:
        config: Config = Config()

        log("Start launching the OpenSearch docker image", "info")

        open_search_docker_image    = config.load_config(["open_search", "open_search_docker_image"])
        open_search_container_name  = config.load_config(["open_search", "open_search_container_name"])
        open_search_port            = config.load_config(["open_search", "open_search_port"])
        open_transport_search_port  = config.load_config(["open_search", "open_search_transport_port"])
        opensearch_config_path      = config.load_config(["paths", "opensearch_config_path"])
        open_search_admin_pwd       = config.load_config_secret_key(config_id_key='opensearch_admin_pwd_path')

        subprocess.run(
            [
                "docker", "run", "-d",
                "--name",   open_search_container_name,
                "-p",       f"{open_search_port}:{open_search_port}",
                "-p",       f"{open_transport_search_port}:{open_transport_search_port}",
                "-e",       "discovery.type=single-node",
                "-e",       f"OPENSEARCH_INITIAL_ADMIN_PASSWORD={open_search_admin_pwd}",
                "-v",       f"{opensearch_config_path}:/usr/share/opensearch/config/opensearch.yml",
                open_search_docker_image
            ],
            check=True  # Ensure that an error is raised if the command fails
        )

    except Exception as e:
        log_error(f"Failed to run the docker image with opensearch: {e}", exception_to_raise=RuntimeError)
