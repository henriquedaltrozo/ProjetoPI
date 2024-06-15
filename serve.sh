#! /bin/bash

if [ ! -d "venv" ]; then
    echo "Criando venv..."

    python3 -m venv venv
    ./venv/bin/pip install flask matplotlib numpy duckdb pandas seaborn scikit-learn
fi

./venv/bin/python3 -m flask --app app run --host=0.0.0.0
