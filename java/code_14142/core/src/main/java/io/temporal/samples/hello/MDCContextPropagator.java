package io.temporal.samples.hello;

import io.temporal.api.common.v1.Payload;
import io.temporal.common.context.ContextPropagator;
import io.temporal.common.converter.DefaultDataConverter;
import java.util.HashMap;
import java.util.Map;
import org.slf4j.MDC;

public class MDCContextPropagator implements ContextPropagator {
  @Override
  public String getName() {
    return this.getClass().getName();
  }

  @Override
  public Object getCurrentContext() {
    return new HashMap<>(MDC.getCopyOfContextMap());
  }

  @Override
  public void setCurrentContext(Object context) {
    Map<String, String> contextMap = (Map<String, String>) context;
    for (Map.Entry<String, String> entry : contextMap.entrySet()) {
      MDC.put(entry.getKey(), entry.getValue());
    }
  }

  DefaultDataConverter defaultDataConverter = DefaultDataConverter.newDefaultInstance();

  @Override
  public Map<String, Payload> serializeContext(Object context) {
    Map<String, String> contextMap = (Map<String, String>) context;
    Map<String, Payload> serializedContext = new HashMap<>();
    contextMap.forEach(
        (key, value) -> serializedContext.put(key, defaultDataConverter.toPayload(value).get()));

    return serializedContext;
  }

  @Override
  public Object deserializeContext(Map<String, Payload> context) {
    Map<String, String> contextMap = new HashMap<>();

    context.forEach(
        (key, value) -> {
          contextMap.put(key, defaultDataConverter.fromPayload(value, String.class, String.class));
        });
    return contextMap;
  }
}
