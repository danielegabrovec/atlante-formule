#ifndef PayloadDir
  #define PayloadDir SourcePath + "..\dist\AtlanteFormule"
#endif
#ifndef ReleaseDir
  #define ReleaseDir SourcePath + "..\dist"
#endif
[Setup]
AppId={{0B2926D9-E677-474C-A257-11146C047564}
AppName=Atlante Formule
AppVersion=1.2.0
AppPublisher=Daniele Gabrovec
AppPublisherURL=https://github.com/danielegabrovec/atlante-formule
DefaultDirName={localappdata}\Programs\AtlanteFormule
DefaultGroupName=Atlante Formule
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.17763
OutputDir={#ReleaseDir}
OutputBaseFilename=AtlanteFormule-1.2.0-Windows-x64-Setup
SetupIconFile=..\atlante\assets\atlante.ico
UninstallDisplayIcon={app}\AtlanteFormule.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
CloseApplications=yes
[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
[Tasks]
Name: "desktopicon"; Description: "Crea un collegamento sul desktop"; Flags: unchecked
[Files]
Source: "{#PayloadDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\Atlante Formule"; Filename: "{app}\AtlanteFormule.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\Atlante Formule"; Filename: "{app}\AtlanteFormule.exe"; WorkingDir: "{app}"; Tasks: desktopicon
[Run]
Filename: "{app}\AtlanteFormule.exe"; Description: "Avvia Atlante Formule"; Flags: nowait postinstall skipifsilent unchecked
