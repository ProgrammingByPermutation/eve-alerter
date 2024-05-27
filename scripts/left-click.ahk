
Loop, 100000
{

SetTitleMatchMode, 2
CoordMode, Mouse, Window

tt = EVE - TTV OxCantEven ahk_class trinityWindow
WinWait, %tt%
IfWinNotActive, %tt%,, WinActivate, %tt%

Random, hello , 100, 500
Sleep, %hello%

Click

Random, hello , 1000, 5000
Sleep, %hello%

}

Esc::ExitApp