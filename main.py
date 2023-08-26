"""
just-go-phishing: Automated phishing infrastructure deployment made easy.

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

import logging
import argparse
import sys
import os
import subprocess
from typing import List
import docker

DOMAIN = "domain.com"
EMAIL_ADDRESS = f"no-reply@{DOMAIN}"
CERTIFICATE_PATH = "certificates"

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Check if Docker is installed
def check_docker_installed() -> bool:
    """
    Check if Docker is installed
    Returns:
        bool: True if Docker is installed, False otherwise
    """
    try:
        subprocess.check_output(["docker", "--version"])
        return True
    except FileNotFoundError:
        return False

# Check if Docker daemon is running
def check_docker_running() -> bool:
    """
    Check if Docker daemon is running
    Returns:
        bool: True if Docker daemon is running, False otherwise
    """
    try:
        subprocess.check_output(["docker", "info"])
        return True
    except subprocess.CalledProcessError:
        return False

# Check if required libraries are installed
def check_dependencies_installed() -> List[str]:
    """
    Check if required libraries are installed
    Returns:
        List[str]: List of missing libraries
    """
    required_libraries = ["docker"]
    unavailable_libraries = []
    for library in required_libraries:
        try:
            __import__(library)
        except ImportError:
            unavailable_libraries.append(library)
    return unavailable_libraries

def clean_environment():
    """
    Clean the Docker environment by removing unused images, containers, and builders
    """
    logger.info("Cleaning environment...")
    try:
        subprocess.run(["docker", "image", "prune", "--all", "--force"], check=True)
        subprocess.run(["docker", "container", "prune", "--force"], check=True)
        subprocess.run(["docker", "builder", "prune", "--all", "--force"], check=True)
        subprocess.run(["sudo", "rm", "-rf", "certificates", "assets"], check=True)
    except subprocess.CalledProcessError as error:
        logger.error("Error cleaning environment: %s", error)
    else:
        logger.info("Done cleaning environment.")

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

def generate_certificates():
    """
    Generate SSL certificates using Let's Encrypt
    """
    client = docker.from_env()

    # Pull the LEGO_IMAGE from Docker Hub
    logger.info("Pulling goacme/lego:latest image...")
    try:
        client.images.pull("goacme/lego:latest")
    except docker.errors.APIError as error:
        logger.error("Error pulling image: %s", error)
        return

    # Run the lego container to generate SSL certificates using Let's Encrypt
    logger.info("Running lego container...")
    try:
        container = client.containers.create(
            image="goacme/lego",
            command=[
                f"--email={EMAIL_ADDRESS}",
                f"--domains={DOMAIN}",
                f"--path=/{EMAIL_ADDRESS}",
                "--accept-tos",
                "--http",
                "run"
            ],
            volumes={
                os.path.join(os.getcwd(), f"{CERTIFICATE_PATH}"): {'bind': '/certificates', 'mode': 'rw'},
            },
            ports={"80/tcp": 80},
        )
        container.start()
        container.wait()
        logs = container.logs()
        logger.info(logs.decode('utf-8'))
        container.remove()
        logger.info("Done running lego container.")
        change_ownership(CERTIFICATE_PATH)
    except docker.errors.APIError as error:
        logger.error("Error running lego container: %s", error)

def build_gophish_image(path: str, target: str):
    """
    Build a Docker image using the specified Dockerfile and target
    Args:
        PATH (str): The path to the Dockerfile
        TARGET (str): The target to build
    """
    client = docker.from_env()

    logger.info("Building Docker image with Dockerfile %s and target %s...", path, target)
    try:
        image, build_log = client.images.build(
            path=path,
            rm=True,
            target=target,
            tag=f"{os.getenv('USER')}/gophish-{target}"
        )
        logger.info("Successfully built image: %s", image.tags[0])
        for log in build_log:
            print(log)
    except docker.errors.BuildError as error:
        logger.error("Error building Docker image: %s", error)

def run_gophish_container():
    """
    Run the GoPhish Docker container
    """
    client = docker.from_env()

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

def parse_args():
    """
    Parse command-line arguments for the script.

    Returns:
        argparse.Namespace: Namespace object containing all the arguments provided by the user.
    """
    parser = argparse.ArgumentParser(description="Automated phishing infrastructure deployment made easy.")
    parser.add_argument("--clean", action="store_true", help="Clean the Docker environment")
    parser.add_argument("--generate-certs", action="store_true", help="Generate SSL certificates")
    parser.add_argument("--build", choices=['build', 'app'], help="Build a GoPhish Docker image. Targets: 'build' or 'app'")
    parser.add_argument("--run", action="store_true", help="Run the GoPhish Docker container")
    args = parser.parse_args()

    # Check if no arguments were provided
    if not any(vars(args).values()):
        parser.print_help()
        exit(0)

    return args

if __name__ == "__main__":
    arg = parse_args()

    # Check if required libraries are installed
    missing_libraries = check_dependencies_installed()
    if missing_libraries:
        logger.error("The following libraries are missing: %s", ', '.join(missing_libraries))
        sys.exit()
    # Check if Docker is installed
    if not check_docker_installed():
        logger.error("Docker is not installed")
        sys.exit()
    # Check if Docker daemon is running
    if not check_docker_running():
        logger.error("Docker daemon is not running")
        sys.exit()

    if arg.clean:
        clean_environment()
    if arg.generate_certs:
        generate_certificates()
    if arg.build:
        build_gophish_image("docker/.", arg.build)
    if arg.run:
        run_gophish_container()
