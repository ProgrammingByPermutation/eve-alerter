
Loop, 100000
{

SetTitleMatchMode, 2
CoordMode, Mouse, Window

tt = EVE - TTV OxCantEven ahk_class trinityWindow
WinWait, %tt%
IfWinNotActive, %tt%,, WinActivate, %tt%

Random, hello , 100, 500
Sleep, %hello%

Send, {Blind}v

Random, hello , 1000, 10000
Sleep, %hello%

}

Esc::ExitApp