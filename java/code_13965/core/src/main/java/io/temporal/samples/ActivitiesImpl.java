package io.temporal.samples;

import io.temporal.activity.Activity;
import java.util.UUID;

public class ActivitiesImpl implements Activities {
  @Override
  public String activity1(String requestId, String name) {
    System.out.println("reserving car for request '" + requestId + "` and name `" + name + "'");
    return UUID.randomUUID().toString();
  }

  @Override
  public String activity2(String requestId, String name) {
    System.out.println(
        "failing to book flight for request '" + requestId + "' and name '" + name + "'");
    //    throw ApplicationFailure.newNonRetryableFailure(
    //        "Flight booking did not work", "bookingFailure");
    return "booked";
  }

  @Override
  public String activity3(String requestId, String name) {
    System.out.println("booking hotel for request '" + requestId + "` and name `" + name + "'");
    return UUID.randomUUID().toString();
  }

  @Override
  public void sleep(String requestId, String name) {

    for (int i = 0; i < 100; i++) {
      try {
        Thread.sleep(1000);
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
      Activity.getExecutionContext().heartbeat("working");
    }
  }

  @Override
  public String cancelActivity1(String requestId, String name) {
    System.out.println("cancelling flight reservation '" + requestId + "' for '" + name + "'");
    return UUID.randomUUID().toString();
  }

  @Override
  public String cancelActivity2(String requestId, String name) {
    System.out.println("cancelling hotel reservation '" + requestId + "' for '" + name + "'");
    return UUID.randomUUID().toString();
  }
}
