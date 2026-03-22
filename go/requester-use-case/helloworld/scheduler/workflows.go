package scheduler

import (
	"context"
	"go.temporal.io/sdk/activity"
	"go.temporal.io/sdk/workflow"
	"time"
)

// RequesterSchedulerWorkflow Workflow is a Hello World scheduler definition.
// Requests intra module are processed sequentially
// Requests inter module are processed concurrently
func RequesterSchedulerWorkflow(ctx workflow.Context) (string, error) {
	reg := NewRegistration(ctx)
	workflow.Go(ctx, func(ctx workflow.Context) {
		signalChannel := workflow.GetSignalChannel(ctx, "your-signal-name")
		for {
			var signal LZRequest
			signalChannel.Receive(ctx, &signal)
			reg.QueueRequest(ctx, signal)
		}
	})
	err := reg.Process(ctx)
	if err != nil {
		return "", err
	}
	return "success", nil
}

// LZRequestWorkflow executes a workflow that processes an LZRequest
// and returns an LZResult or an error if the execution fails.
func LZRequestWorkflow(ctx workflow.Context, request LZRequest) (LZResult, error) {
	ao := workflow.ActivityOptions{
		StartToCloseTimeout: 100 * time.Second,
	}
	ctx = workflow.WithActivityOptions(ctx, ao)

	var result string
	err := workflow.ExecuteActivity(ctx, Activity, request.RequestID).Get(ctx, &result)
	if err != nil {
		return LZResult{}, err
	}
	return LZResult{}, nil
}

func Activity(ctx context.Context, name string) (string, error) {
	logger := activity.GetLogger(ctx)
	logger.Info("Activity", "name", name)
	for i := 0; i < 30; i++ {
		time.Sleep(1 * time.Second)
		activity.RecordHeartbeat(ctx, "heartbeat")
	}
	return "Hello " + name + "!", nil
}
