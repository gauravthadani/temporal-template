[working-directory: 'code']
start-worker SAMPLE:
    cd {{SAMPLE}} && go run worker/main.go

[working-directory: 'code']
start-starter SAMPLE:
    cd {{SAMPLE}} && go run starter/main.go