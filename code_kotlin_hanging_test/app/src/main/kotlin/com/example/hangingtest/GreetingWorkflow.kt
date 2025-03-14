package com.example.hangingtest

import io.temporal.activity.Activity
import io.temporal.activity.ActivityInterface
import io.temporal.activity.ActivityMethod
import io.temporal.activity.ActivityOptions
import io.temporal.workflow.Workflow
import io.temporal.workflow.WorkflowInterface
import io.temporal.workflow.WorkflowMethod
import java.lang.Thread.sleep
import java.time.Duration


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
                .setStartToCloseTimeout(Duration.ofSeconds(10000))
                .setHeartbeatTimeout(Duration.ofSeconds(20))
                .build()
        )
    }

    override fun greeting(name: String): String {
        Workflow.sleep(Duration.ofSeconds(2))
        return activities.composeGreeting("Salutations", name)
    }
}

@ActivityInterface
interface GreetingActivities {
    @ActivityMethod(name = "greet")
    fun composeGreeting(greeting: String, name: String): String
}

class GreetingActivitiesImpl : GreetingActivities {
    override fun composeGreeting(greeting: String, name: String): String {
        sleep(Duration.ofSeconds(5))
        val context = Activity.getExecutionContext()
        context.heartbeat("test");
        sleep(Duration.ofSeconds(5))
        return "$greeting, $name!"
    }
}