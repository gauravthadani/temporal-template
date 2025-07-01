# Temporal Python SDK Samples

This is a collection of samples showing how to use the [Python SDK](https://github.com/temporalio/sdk-python).

## Usage

Prerequisites:

* [uv](https://docs.astral.sh/uv/)
* [Temporal CLI installed](https://docs.temporal.io/cli#install)
* [Local Temporal server running](https://docs.temporal.io/cli/server#start-dev)

The SDK requires Python >= 3.9. You can install Python using uv. For example,

    uv python install 3.13

With this repository cloned, run the following at the root of the directory:

    uv sync --all-extras

That loads all required dependencies. Then to run a sample, usually you just run it under uv. For example:

    uv run hello/hello_activity.py

Some examples require extra dependencies. See each sample's directory for specific instructions.

