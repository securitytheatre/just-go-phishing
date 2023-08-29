"""
just-go-phishing: Phishing infrastructure deployment made easy.

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

import sys
import os
import subprocess
import docker

from src import log
from src import menu
from src import utils
from src import lego

DOMAIN = "domain.com"
EMAIL_ADDRESS = f"no-reply@{DOMAIN}"
CERTIFICATE_PATH = "certificates"

def change_ownership(path: str):
    """
    Change the ownership of a given path to the current user
    Args:
        PATH (str): The path to change ownership
    """
    logger.info("Changing ownership of %s...", path)
    try:
        subprocess.run(["sudo", "chown", "-R", f"{os.getenv('USER')}:{os.getenv('USER')}", f"{path}"], check=True)
    except subprocess.CalledProcessError as error:
        logger.error("Error changing ownership: %s", error)
    else:
        logger.info("Done changing ownership.")

def build_gophish_image(path: str, target: str):
    """
    Build a Docker image using the specified Dockerfile and target
    Args:
        PATH (str): The path to the Dockerfile
        TARGET (str): The target to build
    """
    client = utils.get_docker_client()

    logger.info("Building Docker image with Dockerfile %s and target %s...", path, target)
    try:
        image, _ = client.images.build(
            path=path,
            rm=True,
            target=target,
            tag=f"{os.getenv('USER')}/gophish-{target}"
        )
        logger.info("Successfully built image: %s", image.tags[0])
    except docker.errors.BuildError as error:
        logger.error("Error building Docker image: %s", error)

def run_gophish_container():
    """
    Run the GoPhish Docker container
    """
    client = utils.get_docker_client()

    # Set variables for GoPhish container
    admin_listen_url = "0.0.0.0:3333"
    admin_use_tls = "true"
    admin_cert_path = f"/certificates/certificates/{DOMAIN}.crt"
    admin_key_path = f"/certificates/certificates/{DOMAIN}.key"
    admin_trusted_origins = ""
    phish_listen_url = ""
    phish_use_tls = "true"
    phish_cert_path = f"/certificates/certificates/{DOMAIN}.crt"
    phish_key_path = f"/certificates/certificates/{DOMAIN}.key"
    contact_address = EMAIL_ADDRESS
    db_file_path = "/opt/gophish/assets/gophish.db"

    environment = {
        "ADMIN_LISTEN_URL": admin_listen_url,
        "ADMIN_USE_TLS": admin_use_tls,
        "ADMIN_CERT_PATH": admin_cert_path,
        "ADMIN_KEY_PATH": admin_key_path,
        "ADMIN_TRUSTED_ORIGINS": admin_trusted_origins,
        "PHISH_LISTEN_URL": phish_listen_url,
        "PHISH_USE_TLS": phish_use_tls,
        "PHISH_CERT_PATH": phish_cert_path,
        "PHISH_KEY_PATH": phish_key_path,
        "CONTACT_ADDRESS": contact_address,
        "DB_FILE_PATH": db_file_path
    }

    # Run the GoPhish Docker container with the specified environment variables
    volumes = {
        os.path.join(os.getcwd(), "certificates"): {'bind': '/certificates', 'mode': 'rw'},
        os.path.join(os.getcwd(), "assets"): {'bind': '/opt/gophish/assets', 'mode': 'rw'}
    }
    ports = {
        "80": 80,
        "443": 443,
        "8080": 9080,
        "8443": 9443,
        "3333": 3333
    }
    try:
        container = client.containers.run(
            f"{os.getenv('USER')}/gophish-app",
            detach=True,
            restart_policy={
                "Name": "on-failure",
                "MaximumRetryCount": 5
            },
            volumes=volumes,
            ports=ports,
            environment=environment
        )
        container.logs()
    except docker.errors.APIError as error:
        logger.error("Error running GoPhish container: %s", error)


def initialise():
    """
    Initialise the application by:
    1. Validating required libraries are installed.
    2. Checking if Docker is installed.
    3. Checking if the Docker daemon is running.

    Raises:
        SystemExit: If any of the checks fail.
    """
    # Check if required libraries are installed
    utils.validate_requirements("requirements.txt")

    # Check if Docker is installed
    if not utils.check_docker_installed():
        logger.error("Docker is not installed")
        sys.exit()

    # Check if Docker daemon is running
    if not utils.check_docker_running():
        logger.error("Docker daemon is not running")
        sys.exit()


if __name__ == "__main__":
    logger = log.configure_logging()
    initialise()

    parser = menu.build_parser()
    args = parser.parse_args()

    # Check if no arguments were provided
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit()

    if args.sub_command == 'clean':
        if args.containers:
            utils.clean_docker_containers()
        if args.images:
            utils.clean_docker_images(filters = {"dangling": False})
        if args.build_cache:
            utils.clean_docker_build_cache()
        if args.local_folders:
            utils.clean_local_folders(folders = ["certificates", "assets"])
        if args.all:
            utils.clean_docker_environment(filters = {"dangling": False}, folders = ["certificates", "assets"])

    if args.generate_certs:
        lego.create_and_run_container(EMAIL_ADDRESS, DOMAIN, CERTIFICATE_PATH)

    if args.build:
        build_gophish_image("docker/.", args.build)

    if args.run:
        run_gophish_container()
