#!/usr/bin/env bash
PYTHON_ENV="venv"

cd ..
mkdir -p {logs,notebooks/{adhoc,clients,misc,scraper},test-samples/{secrets/{google,meta},email,odata,swagger-docs}}
mkdir -p ./aftafa/env
cp ./docs/examples/config.yaml ./aftafa/env/config.yaml

if [ -d "$PYTHON_ENV" ]; then
    echo 'Found one. Deleting it..'
    rm -rf $PYTHON_ENV
fi

python3 -m venv $PYTHON_ENV
source $PYTHON_ENV/bin/activate
python3 -m pip install --upgrade pip setuptools wheel

if ! dpkg -s libpq-dev &> /dev/null; then
    sudo apt-get install libpq-dev
fi

python3 -m pip install -r requirements.dev.txt --no-cache-dir

echo 'Setup successfull!'