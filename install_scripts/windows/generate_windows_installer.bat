@echo off

echo ####################
echo #                  #
echo # Umit for Windows #
echo #                  #
echo ####################


echo Setting installation variables...
set PythonEXE=C:\Python25\python.exe
set UmitDir=C:\Umit\trunk
set DistDir=C:\Umit\trunk\dist
set GTKDir=C:\GTK
set NmapDir=C:\Nmap
set WinpcapDir=C:\Winpcap


echo Removing old compilation...
rd %DistDir% /s /q


echo Creating dist and dist\share directories...
mkdir %DistDir%\share
mkdir %DistDir%\share\gtk-2.0
mkdir %DistDir%\share\gtkthemeselector
mkdir %DistDir%\share\themes
mkdir %DistDir%\share\xml


echo Copying GTK's share to dist directory...
xcopy %GTKDir%\share\gtk-2.0\*.* %DistDir%\share\gtk-2.0\ /S
xcopy %GTKDir%\share\gtkthemeselector\*.* %DistDir%\share\gtkthemeselector\ /S
xcopy %GTKDir%\share\themes\*.* %DistDir%\share\themes\ /S
xcopy %GTKDir%\share\xml\*.* %DistDir%\share\xml\ /S


echo Creating Nmap dist dirs...
mkdir %DistDir%\Nmap


echo Copying Nmap to his dist directory...
xcopy %NmapDir%\*.* %DistDir%\Nmap


echo Compiling Umit using py2exe...
cd %UmitDir%
copy %UmitDir%\umit %UmitDir%\umit.pyw
%PythonEXE% -OO setup.py py2exe
rd %UmitDir%\umit.pyw

echo Copying some more GTK files to dist directory...
xcopy %GTKDir%\lib %DistDir%\lib /S /I
xcopy %GTKDir%\etc %DistDir%\etc /S /I


echo Removing the build directory...
rd %UmitDir%\build /s /q


echo Done!