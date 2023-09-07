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

import os
import click
from src import log
from src import utils
from src import lego
from src import gophish

CONFIG_FILE = os.path.join(os.getcwd(), "config.json")
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
@click.option('--volumes', is_flag=True, help='Clean specified local directories.')
@click.option('--complete', is_flag=True, help='Full cleanup: Purge Docker environment and local volume. Use --force to remove all images.')
@click.option('--force', is_flag=True, help='Force removal of all Docker images. Applicable with --images and --complete.')
@click.pass_context
@utils.handle_exceptions
def clean(ctx, containers, images, cache, volumes, complete, force):
    """Resource cleanup utilities."""
    if not any([containers, images, cache, volumes, complete]):
        click.echo("No options selected. Showing help:")
        click.echo(ctx.get_help())
        return

    config_data = utils.read_json_config(CONFIG_FILE)

    volume_path = utils.get_config_value(config_data, "volume_path")
    static_path = utils.get_config_value(config_data, "static_path")

    # Initialize filter for images
    img_filter = {"dangling": True} if not force else {"dangling": False}
    if containers:
        utils.clean_docker_containers()
    if images:
        utils.clean_docker_images(filters=img_filter)
    if cache:
        utils.clean_docker_build_cache()
    if volumes:
        utils.clean_local_folders(folders=[volume_path, static_path])
    if complete:
        # Include force option for full cleanup
        utils.clean_docker_environment(filters=img_filter, folders=[volume_path, static_path])


@main.command('build', context_settings={"ignore_unknown_options": True})
@click.option('--image', type=click.Choice(['lego', 'gophish']), help='Select either "lego" or "gophish"')
@click.option('--complete', is_flag=True, help='Build both "lego" and "gophish" images.')
@click.pass_context
@utils.handle_exceptions
def build(ctx, image, complete):
    """Compile Docker images."""
    config_data = utils.read_json_config(CONFIG_FILE)

    build_lego_image_tag = utils.get_config_value(config_data, "build", "lego", "image_tag")
    build_gophish_path = utils.get_config_value(config_data, "build", "gophish", "path")
    build_gophish_image_tag = utils.get_config_value(config_data, "build", "gophish", "image_tag")

    if complete:
        lego.pull_image(build_lego_image_tag)
        gophish.build_gophish_image(build_gophish_path, build_gophish_image_tag)
        return

    if image == 'lego':
        lego.pull_image(build_lego_image_tag)
    elif image == 'gophish':
        gophish.build_gophish_image(build_gophish_path, build_gophish_image_tag)
    else:
        print('No options specified.')
        click.echo(ctx.get_help())


@main.command('run', context_settings={"ignore_unknown_options": True})
@click.option('--container', type=click.Choice(['lego', 'gophish']), help='Run either "lego" for Let\'s Encrypt certificate deployment or "gophish" to launch phishing server.')
@click.option('--complete', is_flag=True, help='Run both "lego" and "gophish" containers.')
@click.pass_context
@utils.handle_exceptions
def run(ctx, container, complete):
    """Deploy Docker containers."""
    config_data = utils.read_json_config(CONFIG_FILE)

    run_lego_image_tag = utils.get_config_value(config_data, "run", "lego", "image_tag")
    run_lego_volume_path = utils.get_config_value(config_data, "run", "lego", "volume_path")
    run_lego_domain = utils.get_config_value(config_data, "run", "lego", "domain")
    run_lego_email = utils.get_config_value(config_data, "run", "lego", "email")

    run_gophish_image_tag = utils.get_config_value(config_data, "run", "gophish", "image_tag")
    run_gophish_volume_path = utils.get_config_value(config_data, "run", "gophish", "volume_path")
    run_gophish_domain = utils.get_config_value(config_data, "run", "gophish", "domain")
    run_gophish_email = utils.get_config_value(config_data, "run", "gophish", "email")

    if complete:
        lego.create_and_run_container(run_lego_image_tag, run_lego_email, run_lego_domain, run_lego_volume_path)
        gophish.run_gophish_container(run_gophish_domain, run_gophish_email, run_lego_volume_path, run_gophish_volume_path, run_gophish_image_tag)
        return

    if container == 'lego':
        lego.create_and_run_container(run_lego_image_tag, run_lego_email, run_lego_domain, run_lego_volume_path)
    elif container == 'gophish':
        gophish.run_gophish_container(run_gophish_domain, run_gophish_email, run_lego_volume_path, run_gophish_volume_path, run_gophish_image_tag)
    else:
        print('No options specified.')
        click.echo(ctx.get_help())


if __name__ == "__main__":
    main()
