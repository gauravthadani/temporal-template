package io.temporal.samples;

import io.temporal.activity.ActivityInterface;

@ActivityInterface
public interface Activities {

  String activity1(String requestId, String name);

  String activity2(String requestId, String name);

  String activity3(String requestId, String name);

  void sleep(String requestId, String name);

  String cancelActivity1(String requestId, String name);

  String cancelActivity2(String requestId, String name);
}
