package main

import (
	"log"

	"github.com/temporalio/samples-go/update"
	"go.temporal.io/sdk/client"
	"go.temporal.io/sdk/worker"
)

func main() {
	// The client and worker are heavyweight objects that should be created once per process.
	c, err := client.Dial(client.Options{})
	if err != nil {
		log.Fatalln("Unable to create client", err)
	}
	defer c.Close()

	w := worker.New(c, "update", worker.Options{})

	w.RegisterWorkflow(update.WorkflowB)
	w.RegisterWorkflow(update.WorkflowA)
	w.RegisterActivity(&update.Activities{Client: c})

	err = w.Run(worker.InterruptCh())
	if err != nil {
		log.Fatalln("Unable to start worker", err)
	}
}
