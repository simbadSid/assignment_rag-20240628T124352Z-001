import subprocess

from utils.log_management import log, log_error
from utils.config_management import load_config_secret_key, load_config

if __name__ == '__main__':
    try:
        config = load_config()
        log("Start launching the OpenSearch docker image", "info")

        open_search_admin_pwd = load_config_secret_key(config_key_id='opensearch_admin_pwd_path')
        open_search_port = config["open_search"]["open_search_port"]

        subprocess.run(
            [
                "docker", "run", "-d", "--name", "opensearch",
                "-p", f"{open_search_port}:{open_search_port}",
                "-p", "9600:9600",
                "-e", "discovery.type=single-node",
                "-e", f"OPENSEARCH_INITIAL_ADMIN_PASSWORD={open_search_admin_pwd}",
                "opensearchproject/opensearch:latest"
            ],
            check=True  # Ensure that an error is raised if the command fails
        )

    except Exception as e:
        log_error(f"Failed to run the docker image with opensearch: {e}", exception_to_raise=RuntimeError)
