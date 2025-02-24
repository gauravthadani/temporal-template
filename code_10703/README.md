# Temporal Python SDK Samples

This is built from from a set of samples to include

- interceptor
- encryption
- couple of activities
  - 1 constantly failing 

to try replicate the issue 

## Usage

Prerequisites:

* Python >= 3.9
* [Poetry](https://python-poetry.org)
* [Temporal CLI installed](https://docs.temporal.io/cli#install)
* [Local Temporal server running](https://docs.temporal.io/cli/server#start-dev)

With this repository cloned, run the following at the root of the directory:

    poetry install

That loads all required dependencies. Then to run a sample, usually you just run it in Python. For example:

Run worker
```bash
    poetry run python context_propagation/worker.py
```

Run starter
```bash
    poetry run python context_propagation/starter.py
```

Run codec server

```bash
  poetry run python context_propagation/codec_server.py
```


![img.png](img.png)
