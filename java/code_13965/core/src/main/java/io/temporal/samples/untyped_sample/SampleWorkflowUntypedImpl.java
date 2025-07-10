package io.temporal.samples.untyped_sample;

import io.temporal.activity.ActivityOptions;
import io.temporal.failure.ActivityFailure;
import io.temporal.failure.CanceledFailure;
import io.temporal.samples.Booking;
import io.temporal.workflow.*;
import java.time.Duration;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Function;
import org.jetbrains.annotations.NotNull;

public class SampleWorkflowUntypedImpl implements SampleWorkflowUntyped {

  private final ActivityOptions options =
      ActivityOptions.newBuilder().setStartToCloseTimeout(Duration.ofSeconds(1000)).build();

  private final ActivityStub aStub = Workflow.newUntypedActivityStub(options);
  boolean isCancelled = false;
  CancellationScope scope;

  public <T> Function<T, String> run(Function<T, String> first, Function<T, String> second) {
    return input -> {
      String res = null;
      try {
        res = first.apply(input);
      } catch (ActivityFailure e) {
        if (e.getCause() instanceof CanceledFailure) {
          if (isCancelled && second != null) {
            Workflow.newDetachedCancellationScope(
                    () -> {
                      String unused = second.apply(input);
                    })
                .run();
          }
        }
      }
      return res;
    };
  }

  @NotNull
  private Function<Object, String> toFunc(String activityName) {
    return (arg) -> aStub.execute(activityName, String.class, arg);
  }

  @Override
  public Booking Start(String arg) {
    AtomicReference<Booking> booking = new AtomicReference<>();
    scope =
        Workflow.newCancellationScope(
            () -> {
              var res1 = run(toFunc("Activity1"), toFunc("CancelActivity1")).apply(arg);
              var res2 = run(toFunc("Sleep"), toFunc("CancelActivity2")).apply(arg);
              var res3 = run(toFunc("Activity3"), null).apply(arg);
              booking.set(new Booking(res1, res2, res3));
            });

    scope.run();
    return booking.get();
  }

  @Override
  public void Cancel(String name) {
    isCancelled = true;
    if (scope != null) {
      scope.cancel();
    }
  }
}
