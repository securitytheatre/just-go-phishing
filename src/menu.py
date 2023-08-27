"""
menu.py: Menu functions for just-go-phishing

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

import argparse

def build_parser():
    """
    Build and return an argument parser for the CLI.
    
    Returns:
        argparse.ArgumentParser: The argument parser configured with the necessary arguments.
    """
    parser = argparse.ArgumentParser(description="Phishing infrastructure deployment made easy.")
    parser.add_argument("--version", action="version", version="just-go-phishing 0.2.0", help="Show the version number and exit")
    parser.add_argument("--clean", action="store_true", help="Clean the Docker environment")
    parser.add_argument("--generate-certs", action="store_true", help="Generate SSL certificates")
    parser.add_argument("--build", choices=['build', 'app'], help="Build a GoPhish Docker image. Targets: 'build' or 'app'")
    parser.add_argument("--run", action="store_true", help="Run the GoPhish Docker container")
    return parser
