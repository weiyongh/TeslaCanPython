package com.teslacan.voicerunner;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

final class ScriptParser {
    private static final Pattern STEP = Pattern.compile("^\\s*(\\d+)s(?:（[^）]*）)?\\s+(.+?)\\s*$", Pattern.CASE_INSENSITIVE);
    static List<ScriptStep> parse(String text) {
        List<ScriptStep> out = new ArrayList<>();
        int sec = -1; String title = null; StringBuilder detail = new StringBuilder();
        for (String line : text.replace("\r", "").split("\n")) {
            Matcher m = STEP.matcher(line);
            if (m.matches()) {
                if (title != null) out.add(new ScriptStep(sec, title, detail.toString().trim()));
                sec = Integer.parseInt(m.group(1)); title = m.group(2).trim(); detail.setLength(0);
            } else if (title != null && !line.trim().isEmpty()) {
                if (detail.length() > 0) detail.append('\n');
                detail.append(line.trim());
            }
        }
        if (title != null) out.add(new ScriptStep(sec, title, detail.toString().trim()));
        if (out.isEmpty()) throw new IllegalArgumentException("未找到“20s  动作”格式的步骤");
        return out;
    }
}
