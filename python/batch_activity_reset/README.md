# batch_activity_reset

## Run

Install dependencies:

```bash
uv sync
```

Start Temporal local:

```bash
temporal server start-dev
```

Run worker:

```bash
uv run -m hello_worker.worker
```

Run starter:

```bash
uv run -m hello_worker.hello_activity_async
```

Activities fail and enter retry backoff (attempt 3 / 50):

![Pending activity, attempt 3 of 50](images/1-pending-activity.png)

## Issue

Run the batch reset against running workflows:

```bash
temporal activity reset --query='`ExecutionStatus`="Running"' --reset-attempts --reset-heartbeats
```

![Reset command in terminal](images/2-reset-command.png)

The batch operation reports success (10 succeeded):

![Batch operation completed, 10 succeeded](images/3-batch-succeeds.png)

But the activity attempt count is unchanged — still attempt 3 / 50, not reset to 1:

![Activity still at attempt 3 of 50 after reset](images/4-id-doesnt-reset.png)
