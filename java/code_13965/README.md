Run Worker

```bash
./gradlew -q execute -PmainClass=io.temporal.samples.Worker --console=plain
```


Run Starter
```bash
./gradlew -q execute -PmainClass=io.temporal.samples.Starter --console=plain
```


Send Cancel
```bash
❯ temporal workflow signal --name "Cancel" --workflow-id <WFID>
```

