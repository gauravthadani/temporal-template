package com.example.hangingtest

import io.temporal.client.WorkflowClient
import io.temporal.client.WorkflowClientOptions
import io.temporal.serviceclient.SimpleSslContextBuilder
import io.temporal.serviceclient.WorkflowServiceStubs
import io.temporal.serviceclient.WorkflowServiceStubsOptions
import java.io.InputStream

fun readFileAsInputStream(fileName: String): InputStream = object {}.javaClass.getResourceAsStream("/$fileName")!!

fun client(): WorkflowClient {
    val clientCert = readFileAsInputStream("ca.pem")
    val clientKey = readFileAsInputStream("ca.key")

    val newServiceStubs = WorkflowServiceStubs.newServiceStubs(
        WorkflowServiceStubsOptions {
            setSslContext(SimpleSslContextBuilder.forPKCS8(clientCert, clientKey).build())
            setEnableHttps(true)
            setTarget("gaurav-test.a2dd6.tmprl.cloud:7233")
        }
    )

    return WorkflowClient.newInstance(newServiceStubs, WorkflowClientOptions {
        setNamespace("gaurav-test.a2dd6")
    })
}