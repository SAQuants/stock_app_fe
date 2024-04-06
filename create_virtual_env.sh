#!/bin/bash
# Copied, inspired from
# https://makwanadhruv.medium.com/automating-virtual-environments-bash-script-magic-for-python-developers-3a06df1777a6

check_install_virtualenv_lib() {
    # sudo apt install python3-pip
    if ! command -v virtualenv &> /dev/null; then
        echo "virtualenv is NOT installed. Installing..."
        python3 -m pip install virtualenv
        echo "virtualenv installation complete."
    else
      echo "virtualenv library is ALREADY installed..."
    fi
}

create_venv() {
    # Check if virtualenv is installed, if not, install it
    check_install_virtualenv_lib

    local env_name=${1:-"venv"}

    if [ -d "./$env_name" ]; then
        echo "Virtual environment '$env_name' already exists. Aborting."
        return 1
    else
        echo "virtual environment does not exists, will create now"
    fi

    python3 -m virtualenv "$env_name"
    source "$env_name/bin/activate"
    pip install -U pip
    if [ -f "requirements.txt" ]; then
        pip install -r ./requirements.txt
    fi
}

# main
export PATH=.:$PATH
# echo "PATH=$PATH"
env_name=${1:-"venv"}
echo "creating virtual environment with name $env_name"
create_venv "$env_name"