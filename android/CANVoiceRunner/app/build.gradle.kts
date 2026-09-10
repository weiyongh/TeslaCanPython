plugins { id("com.android.application") }

android {
    namespace = "com.teslacan.voicerunner"
    compileSdk = 36
    defaultConfig {
        applicationId = "com.teslacan.voicerunner"
        minSdk = 29
        targetSdk = 36
        versionCode = 2
        versionName = "0.2.0"
    }
    buildTypes {
        debug {
            // V2优化-任务02-调试包与手机中的旧签名版本并存，避免卸载旧 App。
            applicationIdSuffix = ".v2debug"
            versionNameSuffix = "-v2-debug"
        }
    }
}

dependencies {
    // V2优化-任务02-使用标准 JUnit 验证时间轴调度，不引入运行时依赖。
    testImplementation("junit:junit:4.13.2")
    implementation("androidx.camera:camera-core:1.4.2")
    implementation("androidx.camera:camera-camera2:1.4.2")
    implementation("androidx.camera:camera-lifecycle:1.4.2")
    implementation("androidx.camera:camera-view:1.4.2")
    implementation("androidx.activity:activity:1.10.1")
}
