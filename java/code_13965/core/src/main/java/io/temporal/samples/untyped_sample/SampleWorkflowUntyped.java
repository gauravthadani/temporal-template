package io.temporal.samples.untyped_sample;

import io.temporal.samples.Booking;
import io.temporal.workflow.SignalMethod;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface SampleWorkflowUntyped {

  @WorkflowMethod
  Booking Start(String name);

  @SignalMethod
  void Cancel(String name);
}
