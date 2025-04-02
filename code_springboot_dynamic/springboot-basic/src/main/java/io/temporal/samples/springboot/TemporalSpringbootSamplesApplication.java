/*
 *  Copyright (c) 2020 Temporal Technologies, Inc. All Rights Reserved
 *
 *  Copyright 2012-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 *  Modifications copyright (C) 2017 Uber Technologies, Inc.
 *
 *  Licensed under the Apache License, Version 2.0 (the "License"). You may not
 *  use this file except in compliance with the License. A copy of the License is
 *  located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 *  or in the "license" file accompanying this file. This file is distributed on
 *  an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 *  express or implied. See the License for the specific language governing
 *  permissions and limitations under the License.
 */

package io.temporal.samples.springboot;

import static io.temporal.samples.springboot.hello.HelloDynamic.TASK_QUEUE;
import static io.temporal.samples.springboot.hello.HelloDynamic.WORKFLOW_ID;

import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.client.WorkflowStub;
import java.util.function.Supplier;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class TemporalSpringbootSamplesApplication {
  public static void main(String[] args) {
    SpringApplication.run(TemporalSpringbootSamplesApplication.class, args).start();
  }

  @Autowired WorkflowClient client;

  @Bean
  public Supplier<WorkflowStub> MyWorkflow() {
    return () -> {
      WorkflowOptions workflowOptions =
          WorkflowOptions.newBuilder().setTaskQueue(TASK_QUEUE).setWorkflowId(WORKFLOW_ID).build();
      return client.newUntypedWorkflowStub("DynamicWF", workflowOptions);
    };
  }
}
