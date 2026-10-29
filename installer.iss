; Trình cài đặt: dựng bằng Inno Setup trong GitHub Actions (không cần quyền admin)
[Setup]
AppName=Bo go Viet
AppVersion=1.0
AppPublisher=Bao Khue
DefaultDirName={localappdata}\BoGoViet
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=out
OutputBaseFilename=CaiDat-BoGoViet
Compression=lzma
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
UninstallDisplayName=Bo go Viet

[Tasks]
Name: "autostart"; Description: "Tu chay cung Windows"; Flags: checkedonce
Name: "desktop"; Description: "Tao bieu tuong ngoai man hinh"; Flags: checkedonce
Name: "wpsaddin"; Description: "Cai add-in So thanh chu cho WPS Office"; Flags: checkedonce

[Files]
Source: "dist\BoGoViet.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "docs\index.html"; DestDir: "{app}"; DestName: "Cong-cu-tieng-Viet.html"; Flags: ignoreversion
Source: "manifest-word.xml"; DestDir: "{app}\Office-AddIn"; Flags: ignoreversion
Source: "manifest-excel.xml"; DestDir: "{app}\Office-AddIn"; Flags: ignoreversion
Source: "wps-addin\*"; DestDir: "{app}\wps-addin"; Flags: recursesubdirs createallsubdirs ignoreversion; Tasks: wpsaddin
Source: "HUONG-DAN.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{autoprograms}\Bo go Viet"; Filename: "{app}\BoGoViet.exe"
Name: "{autoprograms}\Cong cu tieng Viet"; Filename: "{app}\Cong-cu-tieng-Viet.html"
Name: "{userstartup}\Bo go Viet"; Filename: "{app}\BoGoViet.exe"; Parameters: "--tray"; Tasks: autostart
Name: "{userdesktop}\Bo go Viet"; Filename: "{app}\BoGoViet.exe"; Tasks: desktop
Name: "{userdesktop}\Cong cu tieng Viet"; Filename: "{app}\Cong-cu-tieng-Viet.html"; Tasks: desktop

[Registry]
; Đăng ký add-in Office (Word, Excel) cho người dùng hiện tại
Root: HKCU; Subkey: "Software\Microsoft\Office\16.0\WEF\Developer"; ValueType: string; ValueName: "d5034c15-8647-4176-8139-ff8ff59650bc"; ValueData: "{app}\Office-AddIn\manifest-word.xml"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Microsoft\Office\16.0\WEF\Developer"; ValueType: string; ValueName: "be727b5b-d7c2-48a4-ba5f-68052de95d40"; ValueData: "{app}\Office-AddIn\manifest-excel.xml"; Flags: uninsdeletevalue

[Run]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\wps-addin\cai-wps.ps1"""; Flags: runhidden; Tasks: wpsaddin; StatusMsg: "Dang cai add-in cho WPS..."
Filename: "{app}\BoGoViet.exe"; Description: "Chay Bo go Viet ngay"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\wps-addin\cai-wps.ps1"" -Go"; Flags: runhidden; RunOnceId: "GoWpsAddin"
