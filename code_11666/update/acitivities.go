package update

import (
	"context"
	"go.temporal.io/sdk/client"
)

type Activities struct {
	Client client.Client
}

type NotifyRequest struct {
	WorkflowID string
	Argument   []interface{}
}

// Notify Activity.
func (a *Activities) Notify(ctx context.Context, nr NotifyRequest) (int, error) {
	updateWorkflow, err := a.Client.UpdateWorkflow(ctx, client.UpdateWorkflowOptions{
		WorkflowID:   nr.WorkflowID,
		UpdateName:   FetchAndAdd,
		Args:         nr.Argument,
		WaitForStage: client.WorkflowUpdateStageCompleted,
	})
	if err != nil {
		return 0, err
	}

	var result int
	err = updateWorkflow.Get(ctx, &result)
	if err != nil {
		return 0, err
	}
	return result, nil
}
