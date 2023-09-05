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
EMAIL_ADDRESS = f"no-reply@{format(DOMAIN)}"

logger = log.configure_logging()


@click.group()
@click.version_option(version="just-go-phishing 0.3")
def main():
    """
    Phishing infrastructure deployment made easy.
    """
    utils.initialise()


@main.command('clean', context_settings={"ignore_unknown_options": True})
@click.option('--containers', is_flag=True, help='Purge all Docker containers.')
@click.option('--images', is_flag=True, help='Remove all Docker images not in use. Use --force to remove all images.')
@click.option('--cache', is_flag=True, help='Flush Docker build cache.')
@click.option('--volumes', is_flag=True, help='Clean specified local directories (certificates, assets).')
@click.option('--complete', is_flag=True, help='Full cleanup: Purge Docker environment and specified local folders. Use --force to remove all images.')
@click.option('--force', is_flag=True, help='Force removal of all Docker images. Applicable with --images and --complete.')
@click.pass_context
def clean(ctx, containers, images, cache, volumes, purge, force):
    """Resource cleanup utilities."""
    if not any([containers, images, cache, volumes, purge]):
        click.echo("No options selected. Showing help:")
        click.echo(ctx.get_help())
        return
    try:
        # Initialize filter for images
        img_filter = {"dangling": True} if not force else {"dangling": False}
        if containers:
            utils.clean_docker_containers()
        if images:
            utils.clean_docker_images(filters=img_filter)
        if cache:
            utils.clean_docker_build_cache()
        if volumes:
            utils.clean_local_folders(folders=["certificates", "assets"])
        if purge:
            # Include force option for full cleanup
            utils.clean_docker_environment(filters=img_filter, folders=["certificates", "assets"])
    except Exception as exception:
        logger.error("Cleanup operation failed: %s", format(exception))


@main.command('build', context_settings={"ignore_unknown_options": True})
@click.option('--image', type=click.Choice(['lego', 'gophish']), help='Select either "lego" for Let\'s Encrypt or "gophish" for phishing server.')
@click.option('--target', type=str, default='', help='Build target; defaults to building both "app" and "build" targets for GoPhish.')
@click.option('--complete', is_flag=True, help='Build both "lego" and "gophish" images.')
@click.pass_context
def build(ctx, image, target, complete):
    """Compile Docker images."""
    try:
        if complete:
            lego.pull_image()
            gophish.build_gophish_image("docker/.", "build")
            gophish.build_gophish_image("docker/.", "app")
            return

        if image == 'lego':
            lego.pull_image()
        elif image == 'gophish':
            if not target:
                logger.info('No target specified. Defaulting to build both "app" and "build" targets.')
                gophish.build_gophish_image("docker/.", "build")
                gophish.build_gophish_image("docker/.", "app")
            else:
                gophish.build_gophish_image("docker/.", target)
        else:
            print('No options specified.')
            click.echo(ctx.get_help())
    except Exception as exception:
        logger.error("Build failed: %s", format(exception))


@main.command('run', context_settings={"ignore_unknown_options": True})
@click.option('--container', type=click.Choice(['lego', 'gophish']), help='Run either "lego" for Let\'s Encrypt certificate deployment or "gophish" to launch phishing server.')
@click.option('--complete', is_flag=True, help='Run both "lego" and "gophish" containers.')
@click.pass_context
def run(ctx, container, complete):
    """Deploy Docker containers."""
    try:
        if complete:
            lego.create_and_run_container(EMAIL_ADDRESS, DOMAIN, "certificates")
            gophish.run_gophish_container(DOMAIN, EMAIL_ADDRESS)
            return

        if container == 'lego':
            lego.create_and_run_container(EMAIL_ADDRESS, DOMAIN, "certificates")
        elif container == 'gophish':
            gophish.run_gophish_container(DOMAIN, EMAIL_ADDRESS)
        else:
            print('No options specified.')
            click.echo(ctx.get_help())
    except Exception as exception:
        logger.error("Container deployment failed: %s", format(exception))


if __name__ == "__main__":
    main()
