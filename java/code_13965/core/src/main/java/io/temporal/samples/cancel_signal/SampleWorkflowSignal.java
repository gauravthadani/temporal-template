package io.temporal.samples.cancel_signal;

import io.temporal.samples.Booking;
import io.temporal.workflow.SignalMethod;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface SampleWorkflowSignal {

  @WorkflowMethod
  Booking Start(String name);

  @SignalMethod
  void Cancel(String name);
}
