package scheduler

import (
	"go.temporal.io/sdk/workflow"
	"time"
)

type Registration struct {
	modules        map[string]*Module
	allFutureQueue workflow.Channel
	requestCount   int
	lastFuture     workflow.ChildWorkflowFuture
}

// QueueRequest handles the addition of a request to the appropriate module's queue
// or creates a new module if needed.
func (r *Registration) QueueRequest(ctx workflow.Context, request LZRequest) {
	r.requestCount++
	if _, ok := r.modules[request.ModuleID]; ok {
		r.modules[request.ModuleID].requests.Send(ctx, request)
	} else {
		m := NewModule(ctx, request.ModuleID)
		r.modules[request.ModuleID] = m
		_ = m.Process(ctx, r.allFutureQueue)
		m.requests.Send(ctx, request)
	}
}

// Process manages the completion lifecycle of requests by monitoring child workflows
// and ensuring all requests are processed.
// if all queued futures are complete, it blocks on the last one to complete.
// Then it waits for 30 seconds in case another request gets queued and repeats.
func (r *Registration) Process(ctx workflow.Context) error {
	selector := workflow.NewSelector(ctx)
	selector.AddReceive(r.allFutureQueue, func(c workflow.ReceiveChannel, _ bool) {
		var fut workflow.ChildWorkflowFuture
		c.Receive(ctx, &fut)

		selector.AddFuture(fut, func(f workflow.Future) {
			r.lastFuture = fut
			r.requestCount--
		})
	})

	for {
		selector.Select(ctx)
		if complete, err := r.shouldComplete(ctx); err != nil {
			return err
		} else if complete {
			break
		}
	}
	return nil
}

// shouldComplete determines if the processing should complete
// by checking request counts, futures, and a timeout condition.
func (r *Registration) shouldComplete(ctx workflow.Context) (result bool, err error) {
	if r.requestCount > 0 || r.lastFuture == nil {
		return
	}
	err = r.lastFuture.Get(ctx, nil)
	if err != nil {
		return
	}
	condition := func() bool { return r.allFutureQueue.Len() > 0 }

	ctx, cancel := workflow.WithCancel(ctx)
	ok, err := workflow.AwaitWithTimeout(ctx, time.Second*30, condition)
	if err != nil {
		return
	}
	if !ok {
		result = true
		return
	}
	cancel()
	return
}

// NewRegistration initializes a new Registration instance.
func NewRegistration(ctx workflow.Context) *Registration {
	return &Registration{
		modules:        make(map[string]*Module),
		allFutureQueue: workflow.NewChannel(ctx),
	}
}
