package io.temporal.samples.springboot.hello;

import io.temporal.activity.ActivityOptions;
import io.temporal.common.converter.EncodedValues;
import io.temporal.spring.boot.WorkflowImpl;
import io.temporal.workflow.*;
import java.time.Duration;
import java.util.concurrent.atomic.AtomicReference;

// Dynamic Workflow Implementation
@WorkflowImpl(taskQueues = "HelloDynamicTaskQueue")
public class GreetingWorkflowImpl implements GreetingWorkflow {
  private String name;
  EncodedValues updateArgs;

  @Override
  public Object execute(String greeting) {
    String type = Workflow.getInfo().getWorkflowType();

    AtomicReference<String> result = new AtomicReference<>("");

    Workflow.registerListener(
        new DynamicUpdateHandler() {
          @Override
          public void handleValidate(String updateName, EncodedValues args) {
            DynamicUpdateHandler.super.handleValidate(updateName, args);
          }

          @Override
          public Object handleExecute(String updateName, EncodedValues args) {
            ActivityStub activity =
                Workflow.newUntypedActivityStub(
                    ActivityOptions.newBuilder()
                        .setStartToCloseTimeout(Duration.ofSeconds(10))
                        .build());

            name = args.get(0, String.class);
            String greetingResult =
                activity.execute("MyActivity12345", String.class, greeting, name, type);

            result.set(greetingResult);
            return null;
          }
        });

    // Return results

    Workflow.await(() -> !result.get().isEmpty());
    return result.get();
  }
}
