"""
lego.py: Docker helper functions for certificate lifecycle management

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


def pull_image(image: str) -> bool:
    """
    Pulls a specific Docker image.
    
    Args:
        image (str): The Docker image to pull.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    client = utils.get_docker_client()

    logger.info("Pulling %s image...", image)
    try:
        client.images.pull(image)
    except docker.errors.APIError as error:
        utils.handle_api_error(error)
    return True


def create_and_run_container(image: str, email: str, domain: str, path: str) -> bool:
    """
    Creates and runs a Docker container using the lego image to generate SSL certificates.
    
    Args:
        email (str): Email address for certificate registration.
        domain (str): The domain for which to generate the certificate.
        path (str): The path where the certificate will be stored.
    
    Returns:
        bool: True if the operation is successful, False otherwise.
    """
    client = utils.get_docker_client()

    try:
        container = client.containers.create(
            image=image,
            command=generate_command(email, domain),
            volumes=create_volumes(path),
            ports=create_ports(),
        )

        container.start()
        container.wait()

        logger.info("Done running lego container.")
        return True
    except docker.errors.APIError as error:
        utils.handle_api_error(error)


def generate_command(email: str, domain: str) -> list:
    """Generate the command list for the Docker container."""
    return [
        f"--email={email}",
        f"--domains={domain}",
        "--path=/certificates",
        "--accept-tos",
        "--http",
        "--tls",
        "run"
    ]


def create_volumes(path: str) -> dict:
    """Creates a dictionary of volumes to be used in the Docker container."""
    return {
        os.path.join(os.getcwd(), path): {'bind': '/certificates', 'mode': 'rw'},
    }


def create_ports() -> dict:
    """Creates a dictionary of ports to be used in the Docker container."""
    return {
        "80/tcp": 80,
        "443/tcp": 443,
    }
