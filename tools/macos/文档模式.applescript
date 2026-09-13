use AppleScript version "2.4"
use scripting additions

-- Samsung U28E590 usable desktop: 2560 x 1415, below the 25-point menu bar.
set gptBounds to {0, 25, 640, 1440}
set notion1Bounds to {640, 25, 1792, 1440}
set notion2Bounds to {1792, 25, 2560, 1440}

tell application "Google Chrome"
	set gptWindowID to missing value
	set notion1WindowID to missing value
	set notion2WindowID to missing value
	repeat with chromeWindow in windows
		set activeURL to URL of active tab of chromeWindow
		if activeURL contains "chatgpt.com" or activeURL contains "chat.openai.com" then
			set gptWindowID to id of chromeWindow
		else if given name of chromeWindow is "L3-Notion-1" then
			set notion1WindowID to id of chromeWindow
		else if given name of chromeWindow is "L3-Notion-2" then
			set notion2WindowID to id of chromeWindow
		end if
	end repeat

	set gptWindow to first window whose id is gptWindowID
	set notion1Window to first window whose id is notion1WindowID
	set notion2Window to first window whose id is notion2WindowID

	set minimized of gptWindow to false
	set visible of gptWindow to true
	set bounds of gptWindow to gptBounds

	set minimized of notion1Window to false
	set visible of notion1Window to true
	set bounds of notion1Window to notion1Bounds

	set minimized of notion2Window to false
	set visible of notion2Window to true
	set bounds of notion2Window to notion2Bounds
end tell
