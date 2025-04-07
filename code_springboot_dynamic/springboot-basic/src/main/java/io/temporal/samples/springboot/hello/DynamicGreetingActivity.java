package io.temporal.samples.springboot.hello;

import io.temporal.activity.ActivityInterface;
import io.temporal.activity.DynamicActivity;
import io.temporal.common.converter.EncodedValues;

@ActivityInterface
public interface DynamicGreetingActivity extends DynamicActivity {
  @Override
  Object execute(EncodedValues args);
}
