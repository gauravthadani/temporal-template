package io.temporal.samples;

public final class Booking {
  private String field1;
  private String field2;
  private String field3;

  /** Empty constructor to keep Jackson serializer happy. */
  public Booking() {}

  public Booking(String field1, String field2, String field3) {
    this.field1 = field1;
    this.field2 = field2;
    this.field3 = field3;
  }

  public String getField1() {
    return field1;
  }

  public String getField2() {
    return field2;
  }

  public String getField3() {
    return field3;
  }

  @Override
  public String toString() {
    return "Booking{"
        + "field1='"
        + field1
        + '\''
        + ", field2='"
        + field2
        + '\''
        + ", field3='"
        + field3
        + '\''
        + '}';
  }
}
