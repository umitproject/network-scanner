!include "MUI.nsh"
; MUI Settings:
;
;!define MUI_ICON "share\icons\umit_32.ico" # Installer icon
;!define MUI_UNICON "share\icons\trash_32.ico" # Uninstaller icon
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "share\pixmaps\splash.bmp"
!define MUI_HEADERIMAGE_UNBITMAP "share\pixmaps\splash.bmp"
!define MUI_ABORTWARNING
!define MUI_UNABORTWARNING

!define APPLICATION_NAME "Umit"
!define APPLICATION_VERSION "0.9.5RC1"
!define WINPCAP "winpcap-nmap-4.01.exe"

Name "${APPLICATION_NAME}"
InstallDir "$PROGRAMFILES\${APPLICATION_NAME}\"

; Pages definitions
;!define MUI_PAGE_HEADER_TEXT "Umit, Take the red pill"
!define MUI_PAGE_HEADER_SUBTEXT "Umit"

; Finish page definitions
!define MUI_FINISHPAGE_LINK "Don't forget to visit Umit's website!"
!define MUI_FINISHPAGE_LINK_LOCATION "http://www.umitproject.org/" 

Outfile ${APPLICATION_NAME}-${APPLICATION_VERSION}.exe

; MUI Installer Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "COPYING"
!insertmacro MUI_PAGE_LICENSE "COPYING_HIGWIDGETS"
!insertmacro MUI_PAGE_LICENSE "COPYING_NMAP"
!insertmacro MUI_PAGE_LICENSE "COPYING_WINPCAP"
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
  SetOutPath $INSTDIR
  File COPYING
  File COPYING_HIGWIDGETS
  File COPYING_NMAP
  File COPYING_WINPCAP
  File README
  File share\icons\umit_*.ico

  File /r dist\*.*

  File "install_scripts\windows\win_dependencies\${WINPCAP}"
  ExecWait "$INSTDIR\${WINPCAP}"
  Delete "$INSTDIR\${WINPCAP}"

  CreateDirectory "$SMPROGRAMS\Umit"
  CreateShortCut "$SMPROGRAMS\Umit\Umit.lnk" "$INSTDIR\umit.exe" "" $INSTDIR\umit_48.ico
  CreateShortCut "$SMPROGRAMS\Umit\Umit-Uninstaller.lnk" "$INSTDIR\Umit-Uninstaller.exe" "" $INSTDIR\Umit-Uninstaller.exe

  WriteUninstaller "$INSTDIR\Umit-Uninstaller.exe"
SectionEnd

; Components descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
	!insertmacro MUI_DESCRIPTION_TEXT SecUmit "Install Umit and its dependencies"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Section "Uninstall"
    RMDir /r "$SMPROGRAMS\Umit"
    RMDir /r "$INSTDIR"
SectionEnd