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

import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowStub;
import io.temporal.client.WorkflowUpdateStage;
import io.temporal.samples.springboot.hello.GreetingWorkflow;
import io.temporal.samples.springboot.hello.model.Person;
import java.util.function.Function;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
public class SamplesController {

  @Autowired WorkflowClient client;
  @Autowired Function<String, GreetingWorkflow> myWorkflow;

  @GetMapping("/hello")
  public String hello(Model model) {
    model.addAttribute("sample", "Say Hello");
    return "hello";
  }

  @PostMapping(
      value = "/hello",
      consumes = {MediaType.APPLICATION_JSON_VALUE},
      produces = {MediaType.TEXT_HTML_VALUE})
  ResponseEntity<String> helloSample(@RequestBody Person person) {

    GreetingWorkflow workflow = myWorkflow.apply("hello");
    WorkflowStub stub = WorkflowStub.fromTyped(workflow);
    stub.startUpdate("somename", WorkflowUpdateStage.ACCEPTED, Object.class, person.getFirstName());

    // Wait for workflow to finish getting the results
    String result = stub.getResult(String.class);

    // bypass thymeleaf, don't return template name just result
    return new ResponseEntity<>("\"" + result + "\"", HttpStatus.OK);
  }
}
