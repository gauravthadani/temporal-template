package com.example.hangingtest

import io.temporal.activity.ActivityInterface
import io.temporal.activity.ActivityMethod
import io.temporal.activity.ActivityOptions
import io.temporal.workflow.Workflow
import io.temporal.workflow.WorkflowInterface
import io.temporal.workflow.WorkflowMethod
import java.lang.Thread.sleep
import java.time.Duration
import java.time.Instant.now


@WorkflowInterface
interface GreetingWorkflow {
    @WorkflowMethod
    fun greeting(name: String): String
}

class GreetingWorkflowImpl : GreetingWorkflow {
    private val activities by lazy {
        Workflow.newActivityStub(
            GreetingActivities::class.java,
            ActivityOptions.newBuilder()
                .setStartToCloseTimeout(Duration.ofSeconds(30))
                .build()
        )
    }

    override fun greeting(name: String): String {
        println("Starting greeting at ${now()}")
        return activities.composeGreeting("hello", name)
    }
}

class GreetingActivitiesImpl : GreetingActivities {
    override fun composeGreeting(greeting: String, name: String): String {
        sleep(Duration.ofSeconds(2))
        println("Greeting started: $greeting")
        if (greeting == "namaste") {
            throw Exception("I dont like this greeting")
        }
        return "$greeting, $name!"
    }
}

@ActivityInterface
interface GreetingActivities {
    @ActivityMethod(name = "greet")
    fun composeGreeting(greeting: String, name: String): String
}

