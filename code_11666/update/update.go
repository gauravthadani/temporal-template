package update

import (
	"fmt"
	"time"

	"go.temporal.io/sdk/workflow"
)

const (
	FetchAndAdd = "fetch_and_add"
	Done        = "done"
)

func WorkflowA(ctx workflow.Context, wfID string) (int, error) {
	log := workflow.GetLogger(ctx)
	counter := 0

	ctx = workflow.WithActivityOptions(ctx, workflow.ActivityOptions{
		StartToCloseTimeout: time.Minute,
	})
	var activities *Activities
	for {
		log.Info("Calling Update via activities")
		activity := workflow.ExecuteActivity(ctx, activities.Notify, NotifyRequest{
			WorkflowID: wfID,
			Argument:   []interface{}{1},
		})

		var result int
		err := activity.Get(ctx, &result)
		if err != nil {
			return 0, err
		}
		counter += result

		_ = workflow.Sleep(ctx, time.Second*5)
		if counter > 10 {
			break
		}
	}
	return counter, nil
}

func WorkflowB(ctx workflow.Context) (int, error) {
	log := workflow.GetLogger(ctx)
	counter := 0

	if err := workflow.SetUpdateHandlerWithOptions(
		ctx,
		FetchAndAdd,
		func(ctx workflow.Context, i int) (int, error) {
			tmp := counter
			counter += i
			log.Info("counter updated", "addend", i, "new-value", counter)
			return tmp, nil
		},
		workflow.UpdateHandlerOptions{Validator: nonNegative},
	); err != nil {
		return 0, err
	}

	_ = workflow.GetSignalChannel(ctx, Done).Receive(ctx, nil)
	return counter, ctx.Err()
}

func nonNegative(ctx workflow.Context, i int) error {
	log := workflow.GetLogger(ctx)
	if i < 0 {
		log.Debug("Rejecting negative update", "addend", i)
		return fmt.Errorf("addend must be non-negative (%v)", i)
	}
	log.Debug("Accepting update", "addend", i)
	return nil
}
