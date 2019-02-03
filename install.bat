@echo off
rem Change this if you installed WOT in a non-standard location
SET install_dir=C:\Games\World_of_Tanks

SET mod_dir=%install_dir%\res_mods\mods\shared_resources\xvm\res\clanicons\EU\

net session >nul 2>&1
    if %errorLevel% NEQ 0 (
        goto UACPrompt
    ) else (
        goto gotAdmin
    )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params= %*
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params:"=""%", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    pushd "%CD%"
    CD /D "%~dp0"

if exist %install_dir%\WorldOfTanks.exe (
  rd /Q /S %mod_dir%\clan  >NUL
  md %mod_dir%\clan
  rd /Q /S %mod_dir%\nick  >NUL
  md %mod_dir%\nick
  echo Installing forumite icons
  copy forumite_small.png %mod_dir%\nick\ >NUL
  copy warning_small.png %mod_dir%\nick\ >NUL
  for /F "tokens=*" %%N in (nicks.txt) do mklink %mod_dir%\nick\%%N.png %mod_dir%\nick\forumite_small.png >NUL 2>&1
  for /F "tokens=*" %%T in (trolls.txt) do mklink %mod_dir%\nick\%%T.png %mod_dir%\nick\warning_small.png >NUL
  for /F "tokens=1,2 delims=," %%i in (clans.txt) do copy clanicons\%%j.png %mod_dir%\clan\%%i.png >NUL
  for /F "tokens=1,2 delims=," %%i in (special.txt) do copy special\%%j.png %mod_dir%\nick\%%i.png >NUL
) else (
  echo World of Tanks not found.  Please update installation directory in install.bat
  pause
)
