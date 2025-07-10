package io.temporal.samples;

import io.temporal.client.WorkflowClient;
import io.temporal.samples.bookingsaga.SampleWorkflowImpl;
import io.temporal.samples.cancel_signal.SampleWorkflowSignalImpl;
import io.temporal.samples.untyped_sample.SampleWorkflowUntypedImpl;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.worker.WorkerFactory;

public class Worker {

  @SuppressWarnings("CatchAndPrintStackTrace")
  public static void main(String[] args) {
    // gRPC stubs wrapper that talks to the local docker instance of temporal service.
    WorkflowServiceStubs service = WorkflowServiceStubs.newLocalServiceStubs();
    // client that can be used to start and signal workflows
    WorkflowClient client = WorkflowClient.newInstance(service);

    // worker factory that can be used to create workers for specific task queues
    WorkerFactory factory = WorkerFactory.newInstance(client);

    // Worker that listens on a task queue and hosts both workflow and activity implementations.
    io.temporal.worker.Worker worker = factory.newWorker(Starter.TASK_QUEUE);

    // Workflows are stateful. So you need a type to create instances.
    //    worker.registerWorkflowImplementationTypes(SampleWorkflowSignalImpl.class);
    worker.registerWorkflowImplementationTypes(SampleWorkflowImpl.class);
    worker.registerWorkflowImplementationTypes(SampleWorkflowSignalImpl.class);
    worker.registerWorkflowImplementationTypes(SampleWorkflowUntypedImpl.class);

    // Activities are stateless and thread safe. So a shared instance is used.
    Activities activities = new ActivitiesImpl();
    worker.registerActivitiesImplementations(activities);

    // Start all workers created by this factory.
    factory.start();
    System.out.println("Worker started for task queue: " + Starter.TASK_QUEUE);
  }
}
