package main

import (
	"context"
	"encoding/json"
	"github.com/temporalio/samples-go/helloworld/scheduler"
	"log"
	"net/http"

	"go.temporal.io/sdk/client"
	"go.temporal.io/sdk/contrib/envconfig"
)

const (
	workflowID = "requester-scheduler-scheduler"
	taskQueue  = "hello-world"
	signalName = "your-signal-name"
)

func main() {
	c, err := client.Dial(envconfig.MustLoadDefaultClientOptions())
	if err != nil {
		log.Fatalln("Unable to create Temporal client", err)
	}
	defer c.Close()

	http.HandleFunc("/signal", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}

		var req scheduler.LZRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "invalid request body: "+err.Error(), http.StatusBadRequest)
			return
		}

		id := workflowID + "-" + req.LZ
		_, err := c.SignalWithStartWorkflow(
			context.Background(),
			id,
			signalName,
			req,
			client.StartWorkflowOptions{
				ID:        id,
				TaskQueue: taskQueue,
			},
			scheduler.RequesterSchedulerWorkflow,
		)
		if err != nil {
			log.Println("SignalWithStartWorkflow error", err)
			http.Error(w, "failed to signal scheduler: "+err.Error(), http.StatusInternalServerError)
			return
		}

		w.WriteHeader(http.StatusAccepted)
	})

	log.Println("Listening on :8080")
	log.Fatalln(http.ListenAndServe(":8080", nil))
}
