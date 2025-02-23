[working-directory: 'code']
init SAMPLE:
    poetry install

[working-directory: 'code']
start-worker SAMPLE:
    cd {{SAMPLE}} && poetry run python worker.py

[working-directory: 'code']
start-starter SAMPLE:
    cd {{SAMPLE}} && poetry run python starter.py