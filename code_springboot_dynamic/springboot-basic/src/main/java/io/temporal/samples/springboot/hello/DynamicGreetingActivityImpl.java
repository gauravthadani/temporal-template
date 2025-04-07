package io.temporal.samples.springboot.hello;

import io.temporal.activity.Activity;
import io.temporal.common.converter.EncodedValues;
import io.temporal.spring.boot.ActivityImpl;
import org.springframework.stereotype.Component;

@Component
@ActivityImpl(taskQueues = "HelloDynamicTaskQueue")
public class DynamicGreetingActivityImpl implements DynamicGreetingActivity {
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
