package io.temporal.samples.cancel_signal;

import io.temporal.activity.ActivityOptions;
import io.temporal.failure.ActivityFailure;
import io.temporal.failure.CanceledFailure;
import io.temporal.samples.Activities;
import io.temporal.samples.Booking;
import io.temporal.workflow.CancellationScope;
import io.temporal.workflow.Saga;
import io.temporal.workflow.Workflow;
import java.time.Duration;
import java.util.concurrent.atomic.AtomicReference;

public class SampleWorkflowSignalImpl implements SampleWorkflowSignal {

  private final ActivityOptions options =
      ActivityOptions.newBuilder().setStartToCloseTimeout(Duration.ofSeconds(1000)).build();
  private final Activities activities = Workflow.newActivityStub(Activities.class, options);

  CancellationScope scope;

  @Override
  public Booking Start(String name) {
    Saga.Options sagaOptions = new Saga.Options.Builder().setParallelCompensation(true).build();
    AtomicReference<Saga> saga = new AtomicReference<>(new Saga(sagaOptions));
    AtomicReference<Booking> booking = new AtomicReference<>();

    scope =
        Workflow.newCancellationScope(
            () -> {
              try {
                String requestID1 = Workflow.randomUUID().toString();
                saga.get().addCompensation(activities::cancelActivity1, requestID1, name);
                String carReservationID = activities.activity1(requestID1, name);

                String hotelReservationRequestID = Workflow.randomUUID().toString();
                saga.get()
                    .addCompensation(activities::cancelActivity2, hotelReservationRequestID, name);
                String hotelReservationId = activities.activity2(hotelReservationRequestID, name);

                String flightReservationRequestID = Workflow.randomUUID().toString();

                activities.sleep("", "");

                String flightReservationID = activities.activity3(flightReservationRequestID, name);
                saga.set(new Saga(sagaOptions));
                Workflow.sleep(100000);

                booking.set(new Booking(carReservationID, hotelReservationId, flightReservationID));
              } catch (ActivityFailure e) {
                // Ensure that compensations are executed even if the workflow is canceled.
                if (e.getCause() instanceof CanceledFailure) {
                  Workflow.newDetachedCancellationScope(() -> saga.get().compensate()).run();
                }
                throw new CanceledFailure(e.getMessage());
              }
            });

    scope.run();
    return booking.get();
  }

  @Override
  public void Cancel(String name) {
    if (scope != null) {
      scope.cancel();
    }
  }
}
