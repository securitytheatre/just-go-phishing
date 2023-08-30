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

import click
from src import log
from src import utils
from src import lego
from src import gophish

DOMAIN = "domain.com"
EMAIL_ADDRESS = f"no-reply@{DOMAIN}"
CERTIFICATE_PATH = "certificates"

@click.group()
@click.version_option(version="just-go-phishing 0.2.0")
def main():
    """
    Phishing infrastructure deployment made easy.
    """
    logger = log.configure_logging()
    utils.initialise()

@main.command('clean')
@click.option('--containers', is_flag=True, help='Clean Docker containers')
@click.option('--images', is_flag=True, help='Clean Docker images')
@click.option('--build-cache', is_flag=True, help='Clean Docker build cache')
@click.option('--local-folders', is_flag=True, help='Clean local folders')
@click.option('--all', is_flag=True, help='Clean entire Docker environment')
def clean(containers, images, build_cache, local_folders, all):
    if containers:
        utils.clean_docker_containers()
    if images:
        utils.clean_docker_images(filters={"dangling": False})
    if build_cache:
        utils.clean_docker_build_cache()
    if local_folders:
        utils.clean_local_folders(folders=["certificates", "assets"])
    if all:
        utils.clean_docker_environment(filters={"dangling": False}, folders=["certificates", "assets"])

@main.command('generate-certs')
def generate_certs():
    lego.pull_image()
    lego.create_and_run_container(EMAIL_ADDRESS, DOMAIN, CERTIFICATE_PATH)

@main.command('build')
@click.argument('target', type=click.Choice(['build', 'app']))
def build(target):
    gophish.build_gophish_image("docker/.", target)

@main.command('run')
def run():
    gophish.run_gophish_container(DOMAIN, EMAIL_ADDRESS)

if __name__ == "__main__":
    main()
