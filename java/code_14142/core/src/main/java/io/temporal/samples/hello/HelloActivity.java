package io.temporal.samples.hello;

import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import io.temporal.activity.ActivityOptions;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowClientOptions;
import io.temporal.client.WorkflowOptions;
import io.temporal.common.context.ContextPropagator;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.worker.Worker;
import io.temporal.worker.WorkerFactory;
import io.temporal.workflow.Workflow;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import java.time.Duration;
import java.util.Collections;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class HelloActivity {

  static final String TASK_QUEUE = "HelloActivityTaskQueue";

  static final String WORKFLOW_ID = "HelloActivityWorkflow";

  @WorkflowInterface
  public interface GreetingWorkflow {

    @WorkflowMethod
    String getGreeting(String name);
  }

  @ActivityInterface
  public interface GreetingActivities {

    @ActivityMethod(name = "greet")
    String composeGreeting(String greeting, String name);
  }

  public static class GreetingWorkflowImpl implements GreetingWorkflow {

    private final GreetingActivities activities =
        Workflow.newActivityStub(
            GreetingActivities.class,
            ActivityOptions.newBuilder()
                .setStartToCloseTimeout(Duration.ofSeconds(2))
                //                .setContextPropagators(Collections.singletonList(new
                // MDCContextPropagator()))
                .build());

    @Override
    public String getGreeting(String name) {
      // This is a blocking call that returns only after the activity has completed.
      var log = Workflow.getLogger(GreetingWorkflowImpl.class);
      log.info("Printing MDC WF");
      MDC.getCopyOfContextMap().forEach((s, s2) -> log.info("MDC WF - {}: {}", s, s2));
      log.info("Printing MDC WF done");
      return activities.composeGreeting("Hello", name);
    }
  }

  public static class GreetingActivitiesImpl implements GreetingActivities {
    private static final Logger log = LoggerFactory.getLogger(GreetingActivitiesImpl.class);

    @Override
    public String composeGreeting(String greeting, String name) {
      log.info("Composing greeting...");

      log.info("Printing MDC");
      MDC.getCopyOfContextMap().forEach((s, s2) -> log.info("MDC - {}: {}", s, s2));
      log.info("Printing MDC done");
      return greeting + " " + name + "!";
    }
  }

  public static void main(String[] args) {
    List<ContextPropagator> contextPropagators =
        Collections.singletonList(new MDCContextPropagator());
    WorkflowServiceStubs service = WorkflowServiceStubs.newLocalServiceStubs();

    MDC.put("userId", "user123");
    MDC.put("sessionId", "session456");
    MDC.put("requestId", "req789");

    WorkflowClient client =
        WorkflowClient.newInstance(
            service,
            WorkflowClientOptions.newBuilder().setContextPropagators(contextPropagators).build());

    WorkerFactory factory = WorkerFactory.newInstance(client);
    Worker worker = factory.newWorker(TASK_QUEUE);
    worker.registerWorkflowImplementationTypes(GreetingWorkflowImpl.class);
    worker.registerActivitiesImplementations(new GreetingActivitiesImpl());
    factory.start();

    GreetingWorkflow workflow =
        client.newWorkflowStub(
            GreetingWorkflow.class,
            WorkflowOptions.newBuilder()
                .setWorkflowId(WORKFLOW_ID)
                //                .setContextPropagators(contextPropagators)
                .setTaskQueue(TASK_QUEUE)
                .build());

    String greeting = workflow.getGreeting("World");

    MDC.clear();

    System.out.println(greeting);
    System.exit(0);
  }
}
