[working-directory: 'code']
init SAMPLE:
    npm install
    cd {{SAMPLE}} && npm install

[working-directory: 'code']
start-worker SAMPLE:
    cd {{SAMPLE}} && npm run start

[working-directory: 'code']
start-starter SAMPLE:
    cd {{SAMPLE}} && npm run workflow