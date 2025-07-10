package io.temporal.samples.bookingsaga;

import io.temporal.activity.ActivityOptions;
import io.temporal.failure.CanceledFailure;
import io.temporal.samples.Activities;
import io.temporal.samples.Booking;
import io.temporal.workflow.Workflow;
import java.time.Duration;
import java.util.concurrent.atomic.AtomicReference;

public class SampleWorkflowImpl implements SampleWorkflow {

  private final ActivityOptions options =
      ActivityOptions.newBuilder().setStartToCloseTimeout(Duration.ofSeconds(10)).build();
  private final Activities activities = Workflow.newActivityStub(Activities.class, options);

  @Override
  public Booking Start(String name) {
    // Configure SAGA to run compensation activities in parallel

    ResettableSaga saga = new ResettableSaga();
    AtomicReference<Booking> booking = new AtomicReference<>();

    Workflow.newCancellationScope(
            () -> {
              try {
                String requestID1 = Workflow.randomUUID().toString();
                saga.get().addCompensation(activities::cancelActivity1, requestID1, name);
                String result1 = activities.activity1(requestID1, name);

                String requestID2 = Workflow.randomUUID().toString();
                saga.get().addCompensation(activities::cancelActivity2, requestID2, name);
                String result2 = activities.activity2(requestID2, name);
                Workflow.sleep(100000);

                saga.Reset();
                String requestID3 = Workflow.randomUUID().toString();
                String flightReservationID = activities.activity3(requestID3, name);

                booking.set(new Booking(result1, result2, flightReservationID));
              } catch (CanceledFailure e) {
                // Ensure that compensations are executed even if the workflow is canceled.
                Workflow.newDetachedCancellationScope(() -> saga.get().compensate()).run();
                throw e;
              }
            })
        .run();
    return booking.get();
  }
}
