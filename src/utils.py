"""
utils.py: Utility functions for just-go-phishing

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

import subprocess
import sys
from pathlib import Path
from typing import Tuple, Iterable
from typing import Optional
import docker
from src import log

logger = log.configure_logging()


def read_requirements_txt(file_path: Path) -> Tuple[str]:
    """
    Read a requirements.txt file and return a tuple of library names.
    Args:
        file_path (Path): The path to the requirements.txt file
    Returns:
        Tuple[str]: A tuple containing the library names
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        libraries = file.readlines()

    # Strip whitespaces, filter out comments or empty lines, and remove version specifiers
    libraries = tuple(
        line.strip().split('==')[0] for line in libraries
        if line.strip() and not line.startswith('#')
    )
    return libraries


def check_libraries_installed(required_libraries: Tuple[str]) -> Iterable[str]:
    """
    Check if required libraries are installed.
    Args:
        required_libraries (Tuple[str]): A tuple of library names to check
    Returns:
        Iterable[str]: Yields missing libraries
    """
    for library in required_libraries:
        try:
            __import__(library)
        except ImportError:
            yield library


def validate_requirements(requirements_path: Path):
    """
    Validate if all required libraries specified in a requirements.txt file are installed.
    Args:
        requirements_path (Path): The path to the requirements.txt file
        logger (logging.Logger): Logger object for logging errors
    """
    # Check if required libraries are installed
    required_libraries = read_requirements_txt(requirements_path)
    missing_libraries = list(check_libraries_installed(required_libraries))

    if missing_libraries:
        logger.error("The following libraries are missing: %s", ', '.join(missing_libraries))
        sys.exit()


def get_docker_client() -> Optional[docker.DockerClient]:
    """
    Get a Docker client using Docker SDK for Python.
    Returns:
        docker.DockerClient: A Docker client, or None if failed.
    """
    try:
        client = docker.from_env()
        client.ping()
        return client
    except (docker.errors.DockerException, AttributeError):
        return None


def check_docker_installed() -> bool:
    """
    Check if Docker is installed using Docker SDK for Python.
    Returns:
        bool: True if Docker is installed, False otherwise.
    """
    return get_docker_client() is not None


def check_docker_running() -> bool:
    """
    Check if Docker daemon is running using Docker SDK for Python.
    Returns:
        bool: True if Docker daemon is running, False otherwise.
    """
    client = get_docker_client()

    if client is None:
        return False

    try:
        client.info()
        return True
    except docker.errors.APIError:
        return False


def clean_docker_containers():
    """
    Clean unused Docker containers.

    Returns:
    None
    """
    client = get_docker_client()

    try:
        client.containers.prune()
        logger.info("Successfully cleaned unused Docker containers.")
    except docker.errors.APIError as api_error:
        logger.error("Failed to clean Docker containers: %s", api_error)
        raise


def clean_docker_images(filters=None):
    """
    Clean unused Docker images based on filters.

    Parameters:
    filters (dict): Filters for image pruning. Defaults to {"dangling": True}.

    Returns:
    None
    """
    client = get_docker_client()

    if filters is None:
        filters = {"dangling": True}

    try:
        client.images.prune(filters=filters)
        logger.info("Successfully cleaned Docker images.")
    except docker.errors.APIError as api_error:
        logger.error("Failed to clean Docker images: %s", api_error)
        raise


def clean_docker_build_cache():
    """
    Clean unused Docker build cache.

    Returns:
    None
    """
    client = get_docker_client()

    try:
        client.api.prune_builds()
        logger.info("Successfully cleaned Docker build cache.")
    except docker.errors.APIError as api_error:
        logger.error("Failed to clean Docker build cache: %s", api_error)
        raise


def clean_local_folders(folders=None):
    """
    Remove specified local folders.

    Parameters:
    folders (list): List of folder paths to remove.

    Returns:
    None
    """
    for folder in folders:
        try:
            # Using subprocess to delete folder with sudo permissions
            subprocess.run(["sudo", "rm", "-rf", folder], check=True)
            logger.info("Successfully removed %s.", folder)
        except Exception as error:
            logger.error("Failed to remove %s: %s", folder, error)
            raise


def clean_docker_environment(filters=None, folders=None):
    """
    Clean the Docker environment.

    Parameters:
    filters (dict): Filters for image pruning. Defaults to {"dangling": True}.
    folders (list): List of folder names to remove. 

    Returns:
    None
    """
    if filters is None:
        filters = {"dangling": True}

    logger.info("Starting cleaning environment...")

    # Cleaning various Docker components and local folders
    clean_docker_containers()
    clean_docker_images(filters)
    clean_docker_build_cache()
    clean_local_folders(folders)

    logger.info("Done cleaning environment.")
