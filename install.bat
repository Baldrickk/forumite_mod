@echo off
rem Change this if you installed WOT in a non-standard location
SET install_dir=C:\Games\World_of_Tanks

SET mod_dir=%install_dir%\res_mods\mods\shared_resources\xvm\res\clanicons\EU\

if exist %install_dir%\WorldOfTanks.exe (
  rd /Q /S %mod_dir%\clan
  md %mod_dir%\clan
  rd /Q /S %mod_dir%\nick
  md %mod_dir%\nick
  echo Installing forumite icons
  for /F "tokens=*" %%N in (nicks.txt) do copy forumite_small.png %mod_dir%\nick\%%N.png >NUL
  for /F "tokens=*" %%T in (trolls.txt) do copy warning_small.png %mod_dir%\nick\%%T.png >NUL
  for /F "tokens=1,2 delims=," %%i in (clans.txt) do copy clanicons\%%j.png %mod_dir%\clan\%%i.png >NUL
  for /F "tokens=1,2 delims=," %%i in (special.txt) do copy special\%%j.png %mod_dir%\nick\%%i.png >NUL
) else (
  echo World of Tanks not found.  Please update installation directory in install.bat
  pause
)
