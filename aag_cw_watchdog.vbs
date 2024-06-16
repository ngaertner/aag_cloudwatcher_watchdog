Dim WinScriptHost
Set WinScriptHost = CreateObject("WScript.Shell")

Dim arguments

arguments = ""
Set args = Wscript.Arguments
For Each arg In args
   arguments = " " & arguments & " " & arg 
Next

WinScriptHost.Run Chr(34) & "aag_cw_watchdog.exe" & Chr(34) & arguments, 0
Set WinScriptHost = Nothing