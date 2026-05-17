package io.temporal.samples.plm;

import io.temporal.workflow.QueryMethod;
import io.temporal.workflow.SignalMethod;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface TrusteeChangeWorkflow {

  String TASK_QUEUE = "PlmTrusteeChangeTaskQueue";

  @WorkflowMethod
  ChangeTrusteeResult execute(ChangeTrusteeRequest request);

  @SignalMethod
  void trustDeedReceived(String documentRef);

  @SignalMethod
  void idvCompleted(boolean verified);

  @QueryMethod
  ChangeTrusteeResult getCurrentResult();

  record ChangeTrusteeRequest(
      String trustId, String outgoingTrusteeId, String incomingTrusteeName) {}

  record ChangeTrusteeResult(String incomingTrusteeId, String trustDeedRef, boolean success) {}
}
