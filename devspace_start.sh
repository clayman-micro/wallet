#!/bin/bash
set +ex  # Continue on errors

apt-get update && apt-get install -y -qq libpq-dev curl

python3 -m pip install --no-cache-dir --quiet -U pip
python3 -m pip install --no-cache-dir --quiet poetry

poetry config installer.parallel false
poetry config virtualenvs.create false

poetry install

export POSTGRES_DATABASE=wallet_tests


COLOR_CYAN="\033[0;36m"
COLOR_RESET="\033[0m"

echo -e "${COLOR_CYAN}
   ____              ____
  |  _ \  _____   __/ ___| _ __   __ _  ___ ___
  | | | |/ _ \ \ / /\___ \| '_ \ / _\` |/ __/ _ \\
  | |_| |  __/\ V /  ___) | |_) | (_| | (_|  __/
  |____/ \___| \_/  |____/| .__/ \__,_|\___\___|
                          |_|
${COLOR_RESET}
Welcome to your development container!

This is how you can work with it:
- Run \`${COLOR_CYAN}python main.py${COLOR_RESET}\` to build the application
- ${COLOR_CYAN}Files will be synchronized${COLOR_RESET} between your local machine and this container
- Some ports will be forwarded, so you can access this container on your local machine via ${COLOR_CYAN}http://localhost:8080${COLOR_RESET}
"

bash
