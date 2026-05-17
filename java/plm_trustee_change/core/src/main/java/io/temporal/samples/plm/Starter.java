package io.temporal.samples.plm;

import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.samples.plm.TrusteeChangeWorkflow.ChangeTrusteeRequest;
import io.temporal.serviceclient.WorkflowServiceStubs;

public class Starter {

  public static void main(String[] args) {
    WorkflowServiceStubs service = WorkflowServiceStubs.newLocalServiceStubs();
    WorkflowClient client = WorkflowClient.newInstance(service);

    String workflowId = "change-trustee-" + System.currentTimeMillis();
    TrusteeChangeWorkflow wf =
        client.newWorkflowStub(
            TrusteeChangeWorkflow.class,
            WorkflowOptions.newBuilder()
                .setWorkflowId(workflowId)
                .setTaskQueue(TrusteeChangeWorkflow.TASK_QUEUE)
                .build());

    WorkflowClient.start(
        wf::execute,
        new ChangeTrusteeRequest("trust-001", "party-outgoing-trustee", "New Trustee"));

    System.out.println();
    System.out.println("Started workflow: " + workflowId);
    System.out.println();
    System.out.println("Send signals:");
    System.out.println(
        "  temporal workflow signal --workflow-id "
            + workflowId
            + " --name trustDeedReceived --input '\"deed://trust-001/2026-05-18\"'");
    System.out.println(
        "  temporal workflow signal --workflow-id "
            + workflowId
            + " --name idvCompleted --input 'true'");
    System.out.println();
    System.out.println("Query current state:");
    System.out.println(
        "  temporal workflow query --workflow-id " + workflowId + " --type getCurrentResult");
    System.out.println();
    System.exit(0);
  }
}
