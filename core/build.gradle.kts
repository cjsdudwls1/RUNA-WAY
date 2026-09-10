plugins {
    kotlin("jvm") version "2.0.21"
}
group = "kr.runaway"
version = "0.1.0"
repositories { mavenCentral() }
dependencies {
    testImplementation(kotlin("test"))
}
kotlin { jvmToolchain(17) }
tasks.test { useJUnitPlatform() }
