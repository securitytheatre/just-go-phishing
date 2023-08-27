"""
log.py: Logging functions for just-go-phishing

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
import coloredlogs

def configure_logging():
    """
    Configures the centralized logging settings for the application with colored output.

    Returns:
        logger: A configured logger instance for use in the main entry point.
    """
    coloredlogs.install(level='INFO', fmt='%(asctime)s %(hostname)s %(name)s[%(process)d] [%(filename)s:%(lineno)d] [%(levelname)s] - %(message)s')
    logger = logging.getLogger(__name__)
    return logger
