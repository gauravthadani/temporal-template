package main

import (
	"context"
	"github.com/gofrs/uuid"
	"log"
	"time"

	"go.temporal.io/sdk/client"

	"github.com/temporalio/samples-go/helloworld"
)

func main() {
	// The client is a heavyweight object that should be created once per process.
	c, err := client.Dial(client.Options{})
	if err != nil {
		log.Fatalln("Unable to create client", err)
	}
	defer c.Close()

	for i := 0; i < 200; i++ {
		go func() {
			for i := 0; i < 50; i++ {
				go func(c client.Client) {
					err = startWorkflow(c)
					if err != nil {
						log.Fatalln("Unable to start workflow", err)
					}
				}(c)
			}
		}()
	}

	time.Sleep(100 * time.Second)
}

func startWorkflow(c client.Client) error {

	uuid, err := uuid.NewV4()
	if err != nil {
		return err
	}
	workflowOptions := client.StartWorkflowOptions{
		ID:        "hello_world_workflowID_" + uuid.String(),
		TaskQueue: "hello-world",
	}

	we, err := c.ExecuteWorkflow(context.Background(), workflowOptions, helloworld.Workflow, "Temporal")

	if err != nil {
		log.Println(err)
		return err
	}
	log.Println("Started workflow", "WorkflowID", we.GetID(), "RunID", we.GetRunID())

	//// Synchronously wait for the workflow completion.
	//var result string
	//err = we.Get(context.Background(), &result)
	//if err != nil {
	//	log.Fatalln("Unable get workflow result", err)
	//}
	return nil
}
