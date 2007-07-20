@echo off

:: Setting variables
set PythonEXE=C:\Python25\python.exe
set UmitDir=C:\Umit\trunk
set DistDir=C:\Umit\trunk\dist
set GTKDir=C:\GTK
set NmapDir=C:\Nmap
set WinpcapDir=C:\Winpcap


:: Delete old copilation
rd %DistDir% /s /q

:: Create dist and dist\share directory
mkdir %DistDir%\share
mkdir %DistDir%\share\gtk-2.0
mkdir %DistDir%\share\gtkthemeselector
mkdir %DistDir%\share\themes
mkdir %DistDir%\share\xml

:: Copy GTK share to DistDir
xcopy %GTKDir%\share\gtk-2.0\*.* %DistDir%\share\gtk-2.0\ /S
xcopy %GTKDir%\share\gtkthemeselector\*.* %DistDir%\share\gtkthemeselector\ /S
xcopy %GTKDir%\share\themes\*.* %DistDir%\share\themes\ /S
xcopy %GTKDir%\share\xml\*.* %DistDir%\share\xml\ /S


:: Create Nmap dist dirs
mkdir %DistDir%\Nmap

:: Copy Nmap
xcopy %NmapDir%\*.* %DistDir%\Nmap


:: Compile Umit with py2exe
cd %UmitDir%

:: Copy umit as umit.pyw
copy %UmitDir%\umit %UmitDir%\umit.pyw

%PythonEXE% -OO setup.py py2exe


:: Remove umit.pyw
rd %UmitDir%\umit.pyw

:: Copy GTK files to DistDir
xcopy %GTKDir%\lib %DistDir%\lib /S /I
xcopy %GTKDir%\etc %DistDir%\etc /S /I


:: Remove build dir
rd %UmitDir%\build /s /q