#! /bin/bash

if [ ! -d "venv" ]; then
    echo "Criando venv..."

    python -m venv venv
    ./venv/bin/pip install flask matplotlib numpy duckdb pandas
fi

./venv/bin/python3 -m flask --app app run --host=0.0.0.0
