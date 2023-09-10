# just-go-phishing
Phishing infrastructure deployment made easy.

License: GNU Affero General Public License v3.0 or later

### Overview

`just-go-phishing` is a Python tool to simplify the setup of phishing infrastructure using Docker containers.

### Instructions
[Install Docker for your operating system](https://docs.docker.com/engine/install/). Install dependencies with the following commands:

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

Run using the configuration specified in `config.json`:

```bash
$ python main.py build --complete
$ python main.py run --complete
```

 `just-go-phishing` has been tested exclusively on Linux.

### Commands

**Clean**
  - `--containers`: Remove all Docker containers
  - `--images`, `--force`: Delete unused or all Docker images
  - `--cache`: Clear Docker build cache
  - `--volumes`: Clean specified local directories
  - `--complete`, `--force`: Full cleanup of Docker environment and local volumes

**Build**
  - `--image`: Build "lego" or "gophish" images individually
  - `--complete`: Build "lego" and "gophish" images simultaneously

**Run**
  - `--container`: Deploy "lego" or "gophish" containers individually
  - `--complete`: Deploy both "lego" and "gophish" containers simultaneously
