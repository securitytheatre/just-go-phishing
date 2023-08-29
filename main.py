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

from src import log
from src import menu
from src import utils
from src import lego
from src import gophish

DOMAIN = "domain.com"
EMAIL_ADDRESS = f"no-reply@{DOMAIN}"
CERTIFICATE_PATH = "certificates"


if __name__ == "__main__":
    logger = log.configure_logging()
    utils.initialise()

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
        gophish.build_gophish_image("docker/.", args.build)

    if args.run:
        gophish.run_gophish_container(DOMAIN, EMAIL_ADDRESS)
