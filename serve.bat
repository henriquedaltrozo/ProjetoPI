@echo off

if not exist "venv" (
    echo Criando venv...

    python -m venv venv    
    venv\Scripts\pip install flask matplotlib numpy duckdb pandas
)

venv\Scripts\python -m flask --app app run --host=0.0.0.0