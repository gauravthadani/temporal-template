package io.temporal.samples.bookingsaga;

import io.temporal.workflow.Saga;

public class ResettableSaga {
  private Saga saga;

  public ResettableSaga() {
    Reset();
  }

  public void Reset() {
    saga = new Saga(new Saga.Options.Builder().setParallelCompensation(true).build());
  }

  public Saga get() {
    return saga;
  }
}
