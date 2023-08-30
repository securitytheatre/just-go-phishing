# just-go-phishing
Phishing infrastructure deployment made easy.

To use, update `DOMAIN` and `EMAIL_ADDRESS` in `main.py`. Install the required dependencies and run using the following commands:

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ python main.py build --all
$ python main.py run --all
```
