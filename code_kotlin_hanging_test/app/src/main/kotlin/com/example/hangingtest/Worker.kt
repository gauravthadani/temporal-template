/*
 * This source file was generated by the Gradle 'init' task
 */
package com.example.hangingtest

import io.temporal.worker.WorkerFactory
import io.temporal.worker.WorkerOptions
import java.time.Duration


fun worker() {
    WorkerFactory.newInstance(client()).also { factory ->
        factory.newWorker(TASK_QUEUE, WorkerOptions {
            setDefaultHeartbeatThrottleInterval(Duration.ofSeconds(10))
        }).apply {
            registerWorkflowImplementationTypes(GreetingWorkflowImpl::class.java)
            registerActivitiesImplementations(GreetingActivitiesImpl())
        }
    }.start()
}


