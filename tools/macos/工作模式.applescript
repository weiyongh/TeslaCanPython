use AppleScript version "2.4"
use scripting additions

-- Samsung U28E590 usable desktop: 2560 x 1415, below the 25-point menu bar.
set leftPosition to {0, 25}
set leftSize to {1600, 1415}
set topRightBounds to {1600, 25, 2560, 732}
set bottomRightPosition to {1600, 732}
set bottomRightSize to {960, 708}

-- The GPT window is the Chrome window whose active tab is ChatGPT.
tell application "Google Chrome"
	set gptWindow to missing value
	repeat with chromeWindow in windows
		set activeURL to URL of active tab of chromeWindow
		if activeURL contains "gpt" then
			set gptWindow to chromeWindow
			exit repeat
		end if
	end repeat
	if gptWindow is not missing value then
		set minimized of gptWindow to false
		set visible of gptWindow to true
		set bounds of gptWindow to topRightBounds
	end if
end tell

tell application "System Events"
	tell process "ChatGPT"
		set visible to true
		set value of attribute "AXMinimized" of front window to false
		set position of front window to leftPosition
		set size of front window to leftSize
	end tell
	tell process "Code"
		set visible to true
		set value of attribute "AXMinimized" of front window to false
		set position of front window to bottomRightPosition
		set size of front window to bottomRightSize
	end tell
end tell
