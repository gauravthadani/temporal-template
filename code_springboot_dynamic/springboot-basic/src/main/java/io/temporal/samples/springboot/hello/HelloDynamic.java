package io.temporal.samples.springboot.hello;

import io.temporal.activity.Activity;
import io.temporal.activity.ActivityOptions;
import io.temporal.activity.DynamicActivity;
import io.temporal.common.converter.EncodedValues;
import io.temporal.workflow.ActivityStub;
import io.temporal.workflow.DynamicSignalHandler;
import io.temporal.workflow.DynamicWorkflow;
import io.temporal.workflow.Workflow;
import java.time.Duration;

public class HelloDynamic {
  // Define the task queue name
  public static final String TASK_QUEUE = "HelloDynamicTaskQueue";

  // Define our workflow unique id
  public static final String WORKFLOW_ID = "HelloDynamicWorkflow";

  // Dynamic Workflow Implementation
  public static class DynamicGreetingWorkflowImpl implements DynamicWorkflow {
    private String name;

    @Override
    public Object execute(EncodedValues args) {
      String greeting = args.get(0, String.class);
      String type = Workflow.getInfo().getWorkflowType();

      // Register dynamic signal handler
      Workflow.registerListener(
          (DynamicSignalHandler)
              (signalName, encodedArgs) -> name = encodedArgs.get(0, String.class));

      // Define activity options and get ActivityStub
      ActivityStub activity =
          Workflow.newUntypedActivityStub(
              ActivityOptions.newBuilder().setStartToCloseTimeout(Duration.ofSeconds(10)).build());
      // Execute the dynamic Activity. Note that the provided Activity name is not
      // explicitly registered with the Worker
      String greetingResult = activity.execute("DynamicACT", String.class, greeting, name, type);

      // Return results
      return greetingResult;
    }
  }

  // Dynamic Activity implementation
  public static class DynamicGreetingActivityImpl implements DynamicActivity {
    @Override
    public Object execute(EncodedValues args) {
      String activityType = Activity.getExecutionContext().getInfo().getActivityType();
      return activityType
          + ": "
          + args.get(0, String.class)
          + " "
          + args.get(1, String.class)
          + " from: "
          + args.get(2, String.class);
    }
  }
}
