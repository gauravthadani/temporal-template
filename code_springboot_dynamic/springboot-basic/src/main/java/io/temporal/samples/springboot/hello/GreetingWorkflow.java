package io.temporal.samples.springboot.hello;

import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface GreetingWorkflow {

  @WorkflowMethod
  Object execute(String greeting);
}
