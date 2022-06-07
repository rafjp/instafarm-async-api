cd /home/ubuntu/coup

set -e
source /home/ubuntu/sanic/venv/bin/activate

python3 /home/ubuntu/sanic/rest_api_launcher.py

deactivate