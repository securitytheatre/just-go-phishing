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
import json
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
@click.option('--volumes', is_flag=True, help='Clean specified local directories (certificates, assets).')
@click.option('--complete', is_flag=True, help='Full cleanup: Purge Docker environment and specified local folders. Use --force to remove all images.')
@click.option('--force', is_flag=True, help='Force removal of all Docker images. Applicable with --images and --complete.')
@click.pass_context
def clean(ctx, containers, images, cache, volumes, complete, force):
    """Resource cleanup utilities."""
    if not any([containers, images, cache, volumes, complete]):
        click.echo("No options selected. Showing help:")
        click.echo(ctx.get_help())
        return
    try:
        config = utils.read_json_config(CONFIG_FILE)
        required_keys = ["volume_path", "static_path"]
        is_valid = utils.validate_config_keys(config, required_keys)

        if not is_valid:
            raise ValueError("Invalid configuration: Missing required keys")

        volume_path = config.get("volume_path")
        static_path = config.get("static_path")

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
    except FileNotFoundError:
        logger.error("Configuration file not found: %s", CONFIG_FILE)
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from configuration file: %s", CONFIG_FILE)
    except ValueError as value_error:
        logger.error(value_error)
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
        config_data = utils.read_json_config(CONFIG_FILE)
        required_keys = ["build"]
        is_valid = utils.validate_config_keys(config_data, required_keys)

        if not is_valid:
            raise ValueError("Invalid configuration: Missing required keys in the config file")

        # General keys
        #volume_path = config_data.get("volume_path")
        #static_path = config_data.get("static_path")
        #staging = config_data.get("staging")
        #verbosity = config_data.get("verbosity")

        # Build keys
        #build_lego_path = config_data.get("build", {}).get("lego", {}).get("path")
        #build_lego_tag = config_data.get("build", {}).get("lego", {}).get("tag")
        build_gophish_path = config_data.get("build", {}).get("gophish", {}).get("path")
        #build_gophish_tag = config_data.get("build", {}).get("gophish", {}).get("tag")

        if complete:
            lego.pull_image()
            gophish.build_gophish_image(build_gophish_path, "build")
            gophish.build_gophish_image(build_gophish_path, "app")
            return

        if image == 'lego':
            lego.pull_image()
        elif image == 'gophish':
            if not target:
                logger.info('No target specified. Defaulting to build both "app" and "build" targets.')
                gophish.build_gophish_image(build_gophish_path, "build")
                gophish.build_gophish_image(build_gophish_path, "app")
            else:
                gophish.build_gophish_image(build_gophish_path, target)
        else:
            print('No options specified.')
            click.echo(ctx.get_help())
    except FileNotFoundError:
        logger.error("Configuration file not found: %s", CONFIG_FILE)
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from configuration file: %s", CONFIG_FILE)
    except ValueError as value_error:
        logger.error(value_error)
    except Exception as exception:
        logger.error("Build failed: %s", format(exception))


@main.command('run', context_settings={"ignore_unknown_options": True})
@click.option('--container', type=click.Choice(['lego', 'gophish']), help='Run either "lego" for Let\'s Encrypt certificate deployment or "gophish" to launch phishing server.')
@click.option('--complete', is_flag=True, help='Run both "lego" and "gophish" containers.')
@click.pass_context
def run(ctx, container, complete):
    """Deploy Docker containers."""
    try:
        config_data = utils.read_json_config(CONFIG_FILE)
        required_keys = ["run"]
        is_valid = utils.validate_config_keys(config_data, required_keys)

        if not is_valid:
            raise ValueError("Invalid configuration: Missing required keys in the config file")

        # General keys
        #volume_path = config_data.get("volume_path")
        #static_path = config_data.get("static_path")
        #staging = config_data.get("staging")
        #verbosity = config_data.get("verbosity")

        # Run keys
        #run_lego_tag = config_data.get("run", {}).get("lego", {}).get("tag")
        run_lego_volume_path = config_data.get("run", {}).get("lego", {}).get("volume_path")
        run_lego_domain = config_data.get("run", {}).get("lego", {}).get("domain")
        run_lego_email = config_data.get("run", {}).get("lego", {}).get("email")

        #run_gophish_tag = config_data.get("run", {}).get("gophish", {}).get("tag")
        #run_gophish_volume_path = config_data.get("run", {}).get("gophish", {}).get("volume_path")
        run_gophish_domain = config_data.get("run", {}).get("gophish", {}).get("domain")
        run_gophish_email = config_data.get("run", {}).get("gophish", {}).get("email")

        if complete:
            lego.create_and_run_container(run_lego_email, run_lego_domain, run_lego_volume_path)
            gophish.run_gophish_container(run_gophish_domain, run_gophish_email)
            return

        if container == 'lego':
            lego.create_and_run_container(run_lego_email, run_lego_domain, run_lego_volume_path)
        elif container == 'gophish':
            gophish.run_gophish_container(run_gophish_domain, run_gophish_email)
        else:
            print('No options specified.')
            click.echo(ctx.get_help())
    except FileNotFoundError:
        logger.error("Configuration file not found: %s", CONFIG_FILE)
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from configuration file: %s", CONFIG_FILE)
    except ValueError as value_error:
        logger.error(value_error)
    except Exception as exception:
        logger.error("Container deployment failed: %s", format(exception))


if __name__ == "__main__":
    main()
