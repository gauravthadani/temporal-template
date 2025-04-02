# Temporal Java SDK Samples

This repository contains samples that demonstrate various capabilities of 
Temporal using the [Java SDK](https://github.com/temporalio/sdk-java).

It contains two modules:
* [SpringBoot Basic](/springboot-basic): Minimal sample showing SpringBoot autoconfig integration without any extra external dependencies.

## Learn more about Temporal and Java SDK

- [Temporal Server repo](https://github.com/temporalio/temporal)
- [Java SDK repo](https://github.com/temporalio/sdk-java)
- [Java SDK Guide](https://docs.temporal.io/dev-guide/java)

## Requirements

- Java 1.8+ for build and runtime of core samples
- Java 1.8+ for build and runtime of SpringBoot samples when using SpringBoot 2
- Java 1.17+ for build and runtime of Spring Boot samples when using SpringBoot 3
- Local Temporal Server, easiest to get started would be using [Temporal CLI](https://github.com/temporalio/cli).
For more options see docs [here](https://docs.temporal.io/kb/all-the-ways-to-run-a-cluster).


## Build and run tests

1. Clone this repository:

       git clone https://github.com/temporalio/samples-java
   
To run the basic sample run

       ./gradlew :springboot-basic:bootRun


2. Navigate to [localhost:3030](http://localhost:3030)
