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


# Default image to be used for the lego container
LEGO_IMAGE = "goacme/lego:latest"

def pull_image(image=LEGO_IMAGE):
    """
    Pulls a specific Docker image.
    
    Parameters:
    - image : str, optional
        The Docker image to pull. Defaults to LEGO_IMAGE.
    
    Returns:
    - bool
        True if successful, False otherwise.
    """
    client = utils.get_docker_client()

    logger.info("Pulling %s image...", image)
    try:
        client.images.pull(image)
    except docker.errors.APIError as error:
        logger.error("Error pulling image: %s", error)
        return False
    return True

def create_and_run_container(email, domain, path):
    """
    Creates and runs a Docker container using the lego image to generate SSL certificates.
    
    Parameters:
    - email : str
        Email address for certificate registration.
    - domain : str
        The domain for which to generate the certificate.
    - path : str
        The path where the certificate will be stored.
    
    Returns:
    - bool
        True if the operation is successful, False otherwise.
    """
    client = utils.get_docker_client()

    try:
        container = client.containers.create(
            image=LEGO_IMAGE,
            command=[
                f"--email={email}",
                f"--domains={domain}",
                "--path=/certificates",
                "--accept-tos",
                "--http",
                "--tls",
                "run"
            ],
            volumes={
                os.path.join(os.getcwd(), path): {'bind': '/certificates', 'mode': 'rw'},
            },
            ports={
                "80/tcp": 80,
                "443/tcp": 443,
            },
        )

        container.start()
        container.wait()

        logger.info("Done running lego container.")
        return True
    except docker.errors.APIError as error:
        logger.error("Error running lego container: %s", error)
        return False
