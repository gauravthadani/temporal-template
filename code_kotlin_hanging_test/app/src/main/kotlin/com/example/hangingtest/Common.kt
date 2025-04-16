package com.example.hangingtest

import com.sksamuel.hoplite.ConfigLoaderBuilder
import com.sksamuel.hoplite.addResourceSource
import com.sun.net.httpserver.HttpExchange
import com.sun.net.httpserver.HttpServer
import com.uber.m3.tally.RootScopeBuilder
import com.uber.m3.tally.Scope
import com.uber.m3.tally.StatsReporter
import com.uber.m3.util.Duration
import io.micrometer.prometheus.PrometheusConfig
import io.micrometer.prometheus.PrometheusMeterRegistry
import io.temporal.client.WorkflowClient
import io.temporal.client.WorkflowClientOptions
import io.temporal.common.reporter.MicrometerClientStatsReporter
import io.temporal.serviceclient.SimpleSslContextBuilder
import io.temporal.serviceclient.WorkflowServiceStubs
import io.temporal.serviceclient.WorkflowServiceStubsOptions
import java.io.IOException
import java.io.InputStream
import java.net.InetSocketAddress


fun readFileAsInputStream(fileName: String): InputStream = object {}.javaClass.getResourceAsStream("/$fileName")!!


fun serviceStubs(
    useApiKey: Boolean = false,
    withMetrics: Boolean = false,
    localClient: Boolean = false
): WorkflowServiceStubs {

    val newServiceStubs = WorkflowServiceStubs.newServiceStubs(
        WorkflowServiceStubsOptions {
            if (!localClient) {
                setEnableHttps(true)
                setTarget(config.endpoint)
                when {
                    useApiKey ->
                        addApiKey { "eyJhbGciOiJFUzI1NiIsImtpZCI6Ild2dHdhQSJ9.eyJhY2NvdW50X2lkIjoiYTJkZDYiLCJhdWQiOlsidGVtcG9yYWwuaW8iXSwiZXhwIjoxODAzNTI1ODIxLCJpc3MiOiJ0ZW1wb3JhbC5pbyIsImp0aSI6InRLSmE1OEt2Z0xIRENDcUpHREhBcWRJa1NhREJsZXkxIiwia2V5X2lkIjoidEtKYTU4S3ZnTEhEQ0NxSkdESEFxZElrU2FEQmxleTEiLCJzdWIiOiJlYmMyZTgwM2RkZmM0NjQ1ODMwNTUxZjBkODc4N2VjMyJ9.kja1cZaGQX02TkGP8ZNYNiP_M0gDMdRfMWZ92Pbdjmc9PViQUeL2BJwewIvIfb6St_DkE259jMZXub4i51JQnw" }

                    else -> {
                        val clientCert = readFileAsInputStream("ca.pem")
                        val clientKey = readFileAsInputStream("ca.key")
                        setSslContext(SimpleSslContextBuilder.forPKCS8(clientCert, clientKey).build())
                    }
                }
            }


            if (withMetrics) {
                val registry = PrometheusMeterRegistry(PrometheusConfig.DEFAULT)
                val reporter: StatsReporter = MicrometerClientStatsReporter(registry)
                val scope: Scope = RootScopeBuilder()
                    .reporter(reporter)
                    .reportEvery(Duration.ofSeconds(1.0))
                setMetricsScope(scope)
                val scrapeEndpoint: HttpServer = startPrometheusScrapeEndpoint(registry, 8077)
                Runtime.getRuntime().addShutdownHook(Thread { scrapeEndpoint.stop(1) })
            }
        }
    )
    return newServiceStubs
}

fun localClient(withMetrics: Boolean = false, namespace: String? = null) = WorkflowClient.newInstance(
    serviceStubs(withMetrics = withMetrics, localClient = true),
    WorkflowClientOptions { if (!namespace.isNullOrEmpty()) setNamespace(namespace) })

fun client(withMetrics: Boolean = false, namespace: String? = null) = WorkflowClient.newInstance(
    serviceStubs(useApiKey = true, withMetrics = withMetrics),
    WorkflowClientOptions { if (!namespace.isNullOrEmpty()) setNamespace(namespace) })

fun startPrometheusScrapeEndpoint(
    registry: PrometheusMeterRegistry, port: Int
): HttpServer {
    try {
        val server = HttpServer.create(InetSocketAddress(port), 0)
        server.createContext(
            "/metrics"
        ) { httpExchange: HttpExchange ->
            val response = registry.scrape()
            httpExchange.sendResponseHeaders(200, response.toByteArray().size.toLong())
            httpExchange.responseBody.use { os ->
                os.write(response.toByteArray())
            }
        }

        server.start()
        return server
    } catch (e: IOException) {
        throw RuntimeException(e)
    }
}

data class AppConfig(val namespace: String, val endpoint: String)

val config: AppConfig by lazy {
    ConfigLoaderBuilder.default()
        .addResourceSource("/config.json")
        .build()
        .loadConfigOrThrow<AppConfig>()
}