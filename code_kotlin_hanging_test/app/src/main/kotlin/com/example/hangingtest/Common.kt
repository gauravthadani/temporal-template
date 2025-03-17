package com.example.hangingtest

import com.sksamuel.hoplite.ConfigLoader
import com.sksamuel.hoplite.ConfigLoaderBuilder
import com.sksamuel.hoplite.addResourceSource
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

    val config = config()

    val newServiceStubs = WorkflowServiceStubs.newServiceStubs(
        WorkflowServiceStubsOptions {
            setSslContext(SimpleSslContextBuilder.forPKCS8(clientCert, clientKey).build())
            setEnableHttps(true)
            setTarget(config.endpoint)
        }
    )

    return WorkflowClient.newInstance(newServiceStubs, WorkflowClientOptions {
        setNamespace(config.namespace)
    })
}

data class AppConfig(val namespace: String, val endpoint: String)

fun config(): AppConfig {

    return ConfigLoaderBuilder.default()
        .addResourceSource("/config.json")
        .build()
        .loadConfigOrThrow<AppConfig>()
}