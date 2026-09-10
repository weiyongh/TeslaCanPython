package com.teslacan.voicerunner;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

/** V2优化-任务08-验证 Session 目录具有可读性且文件名安全。 */
public class SessionStorageNamingTest {
    @Test public void sanitizesScriptNameWithoutLosingReadableChinese() {
        assertEquals("TM3-016_语音_脚本",
                SessionStorage.safeName("TM3-016 语音/脚本"));
    }

    @Test public void directorySeparatesRepeatedSessions() {
        String first = SessionStorage.directoryName("采集脚本.txt", 1_788_926_400_000L,
                "S0001");
        String second = SessionStorage.directoryName("采集脚本.txt", 1_788_926_400_000L,
                "S0002");
        assertTrue(first.startsWith("采集脚本__"));
        assertTrue(first.endsWith("__S0001"));
        assertTrue(second.endsWith("__S0002"));
    }
}
