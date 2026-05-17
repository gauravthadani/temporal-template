package io.temporal.samples.plm;

import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.worker.WorkerFactory;

public class Worker {

  public static void main(String[] args) {
    WorkflowServiceStubs service = WorkflowServiceStubs.newLocalServiceStubs();
    WorkerFactory factory = WorkerFactory.newInstance(WorkflowClient.newInstance(service));

    setUpWorker(factory);
    factory.start();
    System.out.println("Worker polling task queue: " + TrusteeChangeWorkflow.TASK_QUEUE);
  }

  private static void setUpWorker(WorkerFactory factory) {
    var worker = factory.newWorker(TrusteeChangeWorkflow.TASK_QUEUE);
    worker.registerWorkflowImplementationTypes(TrusteeChangeWorkflowImpl.class);
    worker.registerActivitiesImplementations(new PartyActivitiesImpl());
  }
}
