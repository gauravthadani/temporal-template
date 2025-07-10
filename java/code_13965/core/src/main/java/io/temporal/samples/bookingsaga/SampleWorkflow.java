package io.temporal.samples.bookingsaga;

import io.temporal.samples.Booking;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface SampleWorkflow {

  @WorkflowMethod
  Booking Start(String name);
}
