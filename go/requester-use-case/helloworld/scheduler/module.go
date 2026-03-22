package scheduler

import (
	"go.temporal.io/sdk/workflow"
)

type LZRequest struct {
	LZ        string
	ModuleID  string
	RequestID string
}

type LZResult struct {
}

type Module struct {
	moduleID string
	requests workflow.Channel
}

func NewModule(ctx workflow.Context, moduleID string) *Module {
	return &Module{
		moduleID: moduleID,
		requests: workflow.NewChannel(ctx),
	}
}

func (r *Module) Process(ctx workflow.Context, future workflow.Channel) (err error) {
	selector := workflow.NewSelector(ctx)
	workflow.Go(ctx, func(ctx workflow.Context) {
		selector.AddReceive(r.requests, func(c workflow.ReceiveChannel, _ bool) {
			request := &LZRequest{}
			c.Receive(ctx, request)
			childWorkflow := workflow.ExecuteChildWorkflow(ctx, LZRequestWorkflow, *request)
			future.Send(ctx, childWorkflow)
			err = childWorkflow.Get(ctx, nil)
		})
		for {
			selector.Select(ctx)
		}
	})
	return
}
