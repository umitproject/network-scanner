#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

script_content = dict(splash="share\\pixmaps\\splash.bmp",
                      app_name="Umit",
                      app_version="0.8.3",
                      app_header="Umit, Take the red pill",
                      release="(Testing release)",
                      nmap="Nmap 4.11",
                      nmap_installer="nmap-4.11-setup.exe",
                      python="Python 2.4.3",
                      python_installer="python-2.4.3.msi",
                      gtk="GTK 2.8.18",
                      gtk_installer="gtk-win32-2.8.18-rc1.exe",
                      pygtk="PyGTK 2.8.6",
                      pygtk_installer="pygtk-2.8.6-1.win32-py2.4.exe",
                      pysqlite="PySQLite",
                      pysqlite_installer="pysqlite-2.2.2.win32-py2.4.exe",
                      pycairo="PyCairo 1.0.2",
                      pycairo_installer="pycairo-1.0.2-1.win32-py2.4.exe",
                      psyco="Psyco 1.5.1",
                      psyco_module="psyco-1.5.1\\psyco",
                      uninstaller="$INSTDIR\\Umit-Uninstaller.exe",
                      script_header="""!include "MUI.nsh"
; MUI Settings:
;
; !define MUI_ICON icon_file # Installer icon
; !define MUI_UNICON icon_file # Uninstaller icon
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "%(splash)s"
!define MUI_HEADERIMAGE_UNBITMAP "%(splash)s"
!define MUI_ABORTWARNING
!define MUI_UNABORTWARNING

!define APPLICATION_NAME "%(app_name)s"
!define APPLICATION_VERSION "%(app_version)s"

Name "${APPLICATION_NAME}"
InstallDir "$PROGRAMFILES\\${APPLICATION_NAME}\\"

; Pages definitions
!define MUI_PAGE_HEADER_TEXT "%(app_header)s"
!define MUI_PAGE_HEADER_SUBTEXT "%(app_name)s %(app_version)s %(release)s"

; Finish page definitions
!define MUI_FINISHPAGE_LINK "Don't forget to visit Umit's website!"
!define MUI_FINISHPAGE_LINK_LOCATION "http://www.umitproject.org/" """,

                      
                      script_uninstaller="""Section "Uninstall"
  ReadRegStr $0 HKCU Software\\Python\\PythonCore\\2.4\\InstallPath ""
  StrCmp $0 "" notOnHKCU uninstall
  notOnHKCU:
    ReadRegStr $0 HKLM Software\\Python\\PythonCore\\2.4\\InstallPath ""
    StrCmp $0 "" notOnHKLM uninstall

  notOnHKLM:
    MessageBox MB_OK|MB_ICONEXCLAMATION "The uninstaller can not find Python on this computer!\\
      $\\r$\\nPlease install Python and run this or try to download the Umit's full version." \\
	IDOK remove_uninstaller

  abort:
    Banner::destroy
    Abort

  uninstall:
    Delete "$INSTDIR\\*"
    RMDir "$INSTDIR"
  
    Delete "$0\\Lib\\site-packages\\higwidgets\\*"
    RMDir "$0\\Lib\\site-packages\\higwidgets"

    Delete "$0\\Lib\\site-packages\\umitCore\\*"
    RMDir "$0\\Lib\\site-packages\\umitCore"

    Delete "$0\\Lib\\site-packages\\umitGUI\\*"
    RMDir "$0\\Lib\\site-packages\\umitGUI"

  remove_uninstaller:
      Delete "%(uninstaller)s"
  
SectionEnd""",


                      script_umit_install="""; Install umit files at installation directory
  SetOutPath $INSTDIR
  File COPYING
  File COPYING_HIGWIDGETS
  File README
  File umit
  File utils\\nmap-os-db
  File utils\\nmap-os-fingerprints
  File utils\\nmap-services
  File umit_version

  Rename umit umit.pyw

  SetOutPath $INSTDIR\\share\\pixmaps
  ; Install pixmaps files
  File /r share\\pixmaps\\*.png
  File /r share\\pixmaps\\*.op
  File /r share\\pixmaps\\*.opi
  File /r share\\pixmaps\\*.opt
  File /r share\\pixmaps\\*.opf

  ; Currently, GTK doesn't support SVG on windows
  ;File /r share\\pixmaps\\*.svg
  
  SetOutPath $INSTDIR\\share\\locale\\pt_BR\\LC_MESSAGES
  ; Install locale files
  File share\\locale\\pt_BR\\LC_MESSAGES\\umit.mo
  File share\\locale\\pt_BR\\LC_MESSAGES\\umit.po

  CreateDirectory "$SMPROGRAMS\\Umit"
  CreateShortCut "$SMPROGRAMS\\Umit\\Umit.lnk" "$INSTDIR\\umit.pyw" "" \\
    "$INSTDIR\\umit.pyw" 2 SW_SHOWNORMAL \\
    ALT|CTRL|SHIFT|F5 "Umit: Take the red pill" """)
    

########################################################################

def generate_installer():
    return ("""%(script_header)s

Outfile ${APPLICATION_NAME}-${APPLICATION_VERSION}.exe

; MUI Installer Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "COPYING"
;!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; MUI Uninstaller Pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language
!insertmacro MUI_LANGUAGE "English"

Section "Umit" SecUmit
  ReadRegStr $0 HKCU Software\\Python\\PythonCore\\2.4\\InstallPath ""
  StrCmp $0 "" notOnHKCU install
  notOnHKCU:
    ReadRegStr $0 HKLM Software\\Python\\PythonCore\\2.4\\InstallPath ""
    StrCmp $0 "" notOnHKLM install

  notOnHKLM:
    MessageBox MB_OK|MB_ICONEXCLAMATION "The installer can not find Python on this computer!\\
	$\\r$\\nPlease install Python and run this or try to download the Umit's full version." \\
	IDOK abort

  abort:
    Banner::destroy
    Abort

  install:
    %(script_umit_install)s
    WriteUninstaller "%(uninstaller)s"
SectionEnd

Section "Umit Core" SecUmitCore
  ReadRegStr $0 HKCU Software\\Python\\PythonCore\\2.4\\InstallPath ""
  StrCmp $0 "" notOnHKCU install
  notOnHKCU:
    ReadRegStr $0 HKLM Software\\Python\\PythonCore\\2.4\\InstallPath ""
    StrCmp $0 "" notOnHKLM install

  notOnHKLM:
    MessageBox MB_OK|MB_ICONEXCLAMATION "The installer can not find Python on this computer!\\
	$\\r$\\nPlease install Python and run this or try to download the Umit's full version." \\
	IDOK abort

  abort:
    Banner::destroy
    Abort

  install:
    SetOutPath $0\\Lib\\site-packages\\umitCore
    File umitCore\\*.py
SectionEnd

Section "Umit GUI" SecUmitGUI
  ReadRegStr $0 HKCU Software\\Python\\PythonCore\\2.4\\InstallPath ""
  StrCmp $0 "" notOnHKCU install
  notOnHKCU:
    ReadRegStr $0 HKLM Software\\Python\\PythonCore\\2.4\\InstallPath ""
    StrCmp $0 "" notOnHKLM install

  notOnHKLM:
    MessageBox MB_OK|MB_ICONEXCLAMATION "The installer can not find Python on this computer!\\
	$\\r$\\nPlease install Python and run this or try to download the Umit's full version." \\
	IDOK abort

  abort:
    Banner::destroy
    Abort

  install:
    SetOutPath $0\\Lib\\site-packages\\umitGUI
    File umitGUI\\*.py
SectionEnd

Section "HIGWidgets" SecHIG
  ReadRegStr $0 HKCU Software\\Python\\PythonCore\\2.4\\InstallPath ""
  StrCmp $0 "" notOnHKCU install
  notOnHKCU:
    ReadRegStr $0 HKLM Software\\Python\\PythonCore\\2.4\\InstallPath ""
    StrCmp $0 "" notOnHKLM install

  notOnHKLM:
    MessageBox MB_OK|MB_ICONEXCLAMATION "The installer can not find Python on this computer!\\
	$\\r$\\nPlease install Python and run this or try to download the Umit's full version." \\
	IDOK abort

  abort:
    Banner::destroy
    Abort

  install:
    SetOutPath $0\\Lib\\site-packages\\higwidgets
    File higwidgets\\*.py
SectionEnd

; Components descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
	!insertmacro MUI_DESCRIPTION_TEXT SecUmit "Install Umit scripts and auxiliary files"
	!insertmacro MUI_DESCRIPTION_TEXT SecUmitCore "Install Umit core scripts."
	!insertmacro MUI_DESCRIPTION_TEXT SecUmitGUI "Install Umit GUI scripts"
	!insertmacro MUI_DESCRIPTION_TEXT SecHIG "Install HIGWidgets scripts"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

%(script_uninstaller)s
""" % script_content) % script_content

def generate_full_installer():
    return ("""%(script_header)s

Outfile ${APPLICATION_NAME}-${APPLICATION_VERSION}-full.exe

; MUI Installer Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "COPYING"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; MUI Uninstaller Pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH


; Language
!insertmacro MUI_LANGUAGE "English"

Section "%(python)s" SecPython
  SetOutPath $INSTDIR
  File win_dependencies\\%(python_installer)s
  File win_dependencies\\msvcr71.dll
  ;DetailPrint '"msiexec " /qb /i "$INSTDIR\\%(python_installer)s"'

  ExecWait '"msiexec" /i "$INSTDIR\\%(python_installer)s"' $0
  DetailPrint "Python installer returned: $0"
  ReadRegStr $0 HKLM Software\\Python\\PythonCore\\2.4\\InstallPath ""
  DetailPrint "Python path: $0"
SectionEnd

Section "%(gtk)s" SecGTK
  SetOutPath $INSTDIR
  File win_dependencies\\%(gtk_installer)s
  ExecWait '"$INSTDIR\\%(gtk_installer)s" /S'
SectionEnd

Section "%(nmap)s" SecNmap
  SetOutPath $INSTDIR
  File win_dependencies\\%(nmap_installer)s
  ExecWait '"$INSTDIR\\%(nmap_installer)s" /S'
SectionEnd

Section "%(pygtk)s" SecPyGTK
  SetOutPath $INSTDIR
  File win_dependencies\\%(pygtk_installer)s
  ExecWait $INSTDIR\\%(pygtk_installer)s
SectionEnd

Section "%(pysqlite)s" SecPySQLite
  SetOutPath $INSTDIR
  File win_dependencies\\%(pysqlite_installer)s
  ExecWait $INSTDIR\\%(pysqlite_installer)s
SectionEnd

Section "%(pycairo)s" SecPyCairo
  SetOutPath $INSTDIR
  File win_dependencies\\%(pycairo_installer)s
  ExecWait $INSTDIR\\%(pycairo_installer)s
SectionEnd

Section "%(psyco)s" SecPsyco
  ReadRegStr $0 HKCU Software\\Python\\PythonCore\\2.4\\InstallPath ""
  StrCmp $0 "" onHKLM install
  onHKLM:
    ReadRegStr $0 HKLM Software\\Python\\PythonCore\\2.4\\InstallPath ""

  install:
    SetOutPath "$0\\Lib\\site-packages"
    File /r win_dependencies\\%(psyco_module)s
SectionEnd

Section "Umit" SecUmit
  %(script_umit_install)s
  
  WriteUninstaller %(uninstaller)s
  
  Delete "$INSTDIR\\%(python_installer)s"
  Delete "$INSTDIR\\%(gtk_installer)s"
  Delete "$INSTDIR\\%(nmap_installer)s"
  Delete "$INSTDIR\\%(pygtk_installer)s"
  Delete "$INSTDIR\\%(pysqlite_installer)s"
  Delete "$INSTDIR\\%(pycairo_installer)s"
  Delete "$INSTDIR\\msvcr71.dll"
SectionEnd

Section "Umit Core" SecUmitCore
  ReadRegStr $0 HKCU Software\\Python\\PythonCore\\2.4\\InstallPath ""
  StrCmp $0 "" onHKLM install
  onHKLM:
    ReadRegStr $0 HKLM Software\\Python\\PythonCore\\2.4\\InstallPath ""

  install:
    SetOutPath "$0\\Lib\\site-packages\\umitCore"
    File umitCore\\*.py
SectionEnd

Section "Umit GUI" SecUmitGUI
  ReadRegStr $0 HKCU Software\\Python\\PythonCore\\2.4\\InstallPath ""
  StrCmp $0 "" onHKLM install
  onHKLM:
    ReadRegStr $0 HKLM Software\\Python\\PythonCore\\2.4\\InstallPath ""

  install:
    SetOutPath "$0\\Lib\\site-packages\\umitGUI"
    File umitGUI\\*.py
SectionEnd

Section "HIGWidgets" SecHIG
  ReadRegStr $0 HKCU Software\\Python\\PythonCore\\2.4\\InstallPath ""
  StrCmp $0 "" onHKLM install
  onHKLM:
    ReadRegStr $0 HKLM Software\\Python\\PythonCore\\2.4\\InstallPath ""

  install:
    SetOutPath "$0\\Lib\\site-packages\\higwidgets"
    File higwidgets\\*.py
SectionEnd

; Components descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
	!insertmacro MUI_DESCRIPTION_TEXT SecUmit "Install Umit scripts and auxiliary files"
	!insertmacro MUI_DESCRIPTION_TEXT SecUmitCore "Install Umit core scripts."
	!insertmacro MUI_DESCRIPTION_TEXT SecUmitGUI "Install Umit GUI scripts"
	!insertmacro MUI_DESCRIPTION_TEXT SecHIG "Install HIGWidgets scripts"
	!insertmacro MUI_DESCRIPTION_TEXT SecNmap "Install %(nmap)s. Umit needs Nmap to run."
	!insertmacro MUI_DESCRIPTION_TEXT SecPython "Install %(python)s. Umit needs Python to run."
	!insertmacro MUI_DESCRIPTION_TEXT SecGTK "Install %(gtk)s. Umit needs GTK to run."
	!insertmacro MUI_DESCRIPTION_TEXT SecPyGTK "Install %(pygtk)s. Umit needs PyGTK to run."
	!insertmacro MUI_DESCRIPTION_TEXT SecPySQLite "Install %(pysqlite)s. Umit needs PySQLite to run."
	!insertmacro MUI_DESCRIPTION_TEXT SecPyCairo "Install %(pycairo)s."
	!insertmacro MUI_DESCRIPTION_TEXT SecPsyco "Install %(psyco)s."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

%(script_uninstaller)s""" % script_content) % script_content

if __name__ == "__main__":
    installer = "umit_win32_installer.nsi"
    full_installer = "umit_win32_installer_full.nsi"
    
    open(installer, "w").write(generate_installer())
    open(full_installer, "w").write(generate_full_installer())
    
