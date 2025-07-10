package io.temporal.samples;

import com.google.common.base.Throwables;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.samples.cancel_signal.SampleWorkflowSignal;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.util.UUID;

public class Starter {

  static final String TASK_QUEUE = "MyTaskQueue";

  public static void main(String[] args) {
    WorkflowServiceStubs service = WorkflowServiceStubs.newLocalServiceStubs();
    WorkflowClient client = WorkflowClient.newInstance(service);

    WorkflowOptions options =
        WorkflowOptions.newBuilder()
            .setTaskQueue(TASK_QUEUE)
            .setWorkflowId(String.format("SampleWF_%s", UUID.randomUUID()))
            .build();
    SampleWorkflowSignal trip = client.newWorkflowStub(SampleWorkflowSignal.class, options);
    try {
      Booking booking = trip.Start("workflow");
      System.out.println("Booking: " + booking);
    } catch (Exception e) {
      System.out.println(Throwables.getStackTraceAsString(e));
    }
    System.exit(0);
  }
}
