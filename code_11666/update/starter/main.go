package main

import (
	"context"
	"log"

	"github.com/temporalio/samples-go/update"
	"go.temporal.io/sdk/client"
)

func main() {
	c, err := client.Dial(client.Options{})
	if err != nil {
		log.Fatalln("Unable to create client", err)
	}
	defer c.Close()

	workflowBOptions := client.StartWorkflowOptions{
		ID:        "update-workflowB-ID",
		TaskQueue: "update",
	}

	workflowAOptions := client.StartWorkflowOptions{
		ID:        "workflowA-ID",
		TaskQueue: "update",
	}

	we, err := c.ExecuteWorkflow(context.Background(), workflowBOptions, update.WorkflowB)
	if err != nil {
		log.Fatalln("Unable to execute workflow", err)
	}

	awe, err := c.ExecuteWorkflow(context.Background(), workflowAOptions, update.WorkflowA, we.GetID())
	if err != nil {
		log.Fatalln("Unable to execute workflow", err)
	}

	log.Println("Started workflow B", "WorkflowID", we.GetID(), "RunID", we.GetRunID())
	log.Println("Started workflow A", "WorkflowID", awe.GetID(), "RunID", we.GetRunID())

	var count int
	err = awe.Get(context.Background(), &count)
	log.Println("workflow result: count", count, err)
}
