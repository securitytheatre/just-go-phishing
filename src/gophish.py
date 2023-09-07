"""
gophish.py: Docker helper functions for GoPhish orchestration

Copyright (C) github.com/securitytheatre

This file is part of just-go-phishing.

just-go-phishing is free software: you can redistribute it and/or modify it under the terms of the 
GNU Affero General Public License as published by the Free Software Foundation, either 
version 3 of the License, or (at your option) any later version.

just-go-phishing is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with just-go-phishing. 
If not, see <https://www.gnu.org/licenses/>.
"""

import os
import docker
from src import log
from src import utils

# Configure logger
logger = log.configure_logging()


def build_gophish_image(path: str, tag: str) -> None:
    """
    Build a Docker image using the specified Dockerfile and target
    Args:
        path (str): The path to the Dockerfile
        tag (str): The target to build
    """
    client = utils.get_docker_client()

    logger.info("Building Docker image with Dockerfile %s...", path)
    try:
        image, _ = client.images.build(path=path, rm=True, tag=tag)
        logger.info("Successfully built image: %s", image.tags[0])
    except docker.errors.BuildError as error:
        utils.handle_build_error(error)


def run_gophish_container(domain: str, email: str, run_lego_volume_path: str, run_gophish_volume_path: str, tag: str) -> None:
    """
    Run the GoPhish Docker container
    Args:
        domain (str): The domain for which the container is being configured
        email (str): The contact email address
    """
    client = utils.get_docker_client()
    environment = create_environment_variables(domain, email)
    volumes = create_volumes(run_lego_volume_path, run_gophish_volume_path)
    ports = create_ports()

    try:
        container = client.containers.run(
            tag,
            detach=True,
            restart_policy={"Name": "on-failure", "MaximumRetryCount": 5},
            volumes=volumes,
            ports=ports,
            environment=environment
        )
        container.logs()
    except docker.errors.APIError as error:
        utils.handle_api_error(error)


def create_environment_variables(domain: str, email: str) -> dict:
    """Creates a dictionary of environment variables to be used in the Docker container."""
    admin_cert_path = f"/certificates/certificates/{domain}.crt"
    admin_key_path = f"/certificates/certificates/{domain}.key"

    return {
        "ADMIN_LISTEN_URL": "0.0.0.0:3333",
        "ADMIN_USE_TLS": "true",
        "ADMIN_CERT_PATH": admin_cert_path,
        "ADMIN_KEY_PATH": admin_key_path,
        "ADMIN_TRUSTED_ORIGINS": "",
        "PHISH_LISTEN_URL": "",
        "PHISH_USE_TLS": "true",
        "PHISH_CERT_PATH": admin_cert_path,
        "PHISH_KEY_PATH": admin_key_path,
        "CONTACT_ADDRESS": email,
        "DB_FILE_PATH": "/opt/gophish/assets/gophish.db"
    }


def create_volumes(run_lego_volume_path: str, run_gophish_volume_path: str) -> dict:
    """Creates a dictionary of volumes to be used in the Docker container."""
    return {
        os.path.join(os.getcwd(), run_lego_volume_path): {'bind': '/certificates', 'mode': 'rw'},
        os.path.join(os.getcwd(), run_gophish_volume_path): {'bind': '/opt/gophish/assets', 'mode': 'rw'}
    }


def create_ports() -> dict:
    """Creates a dictionary of ports to be used in the Docker container."""
    return {
        "80": 80,
        "443": 443,
        "8080": 9080,
        "8443": 9443,
        "3333": 3333
    }
