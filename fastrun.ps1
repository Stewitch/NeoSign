.\.venv\Scripts\activate.ps1
uv run .\manage.py makemigrations
uv run .\manage.py migrate
uv run .\manage.py compilemessages -l en
uv run .\manage.py runserver_plus 0.0.0.0:8443 --cert-file=./localhost+2.pem --key-file=./localhost+2-key.pem