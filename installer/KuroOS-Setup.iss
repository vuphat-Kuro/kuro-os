; ============================================================
; KURO OS - bo cai dat Windows (Inno Setup 6). Build: installer\build-installer.bat -> installer\Output\KuroOS-Setup.exe
;
; Day la bo cai MONG (bootstrapper), cung huong voi JavisOS-Setup.exe: .exe chi chep bootstrap.ps1 + bieu tuong,
; roi bootstrap.ps1 (chay an, tien do hien ngay trong wizard) cai Git, git clone Kuro, goi cai-dat-tu-dong.ps1
; cai Python / Node / WebView2 / CLI AI / .venv / thu vien. Ma nguon di bang git clone de nut Cap nhat
; trong app (git fetch + merge) hoat dong va .exe khong bao gio loi thoi.
;
; Cai cho rieng nguoi dung (khong can quyen admin; winget tu hoi UAC khi cai Git / Node).
; Go cai dat: xoa bieu tuong, tat Kuro; GIU thu muc Kuro (ky uc, lich su, .env) de nguoi dung tu xoa.
; Cai im lang: KuroOS-Setup.exe /VERYSILENT /KURODIR="D:\Kuro" /TASKS="desktopicon,brains"
; ============================================================
#ifndef AppVer
  #define AppVer "0.0.0"
#endif

[Setup]
AppId={{B7E1D3A4-6C52-4F9A-8D0E-3A1F5C7B9E24}
AppName=Kuro OS
AppVerName=Kuro OS {#AppVer}
AppVersion={#AppVer}
AppPublisher=Kuro
AppPublisherURL=https://github.com/vuphat-Kuro/kuro-os
AppSupportURL=https://github.com/vuphat-Kuro/kuro-os/issues
VersionInfoVersion={#AppVer}
VersionInfoDescription=Kuro OS Setup
DefaultDirName={localappdata}\Programs\Kuro OS
DisableDirPage=yes
DisableProgramGroupPage=yes
SetupIconFile=..\kuro_logo.ico
UninstallDisplayIcon={app}\kuro_logo.ico
UninstallDisplayName=Kuro OS
OutputDir=Output
OutputBaseFilename=KuroOS-Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
WizardImageFile=img\WizardImage0.bmp,img\WizardImage1.bmp,img\WizardImage2.bmp,img\WizardImage3.bmp,img\WizardImage4.bmp,img\WizardImage5.bmp,img\WizardImage6.bmp
WizardSmallImageFile=img\WizardSmallImage0.bmp,img\WizardSmallImage1.bmp,img\WizardSmallImage2.bmp,img\WizardSmallImage3.bmp,img\WizardSmallImage4.bmp,img\WizardSmallImage5.bmp,img\WizardSmallImage6.bmp
ShowLanguageDialog=auto
ChangesAssociations=no

[Languages]
Name: "vi"; MessagesFile: "vi.isl"; InfoBeforeFile: "viInfoBefore.txt"
Name: "en"; MessagesFile: "compiler:Default.isl"; InfoBeforeFile: "enInfoBefore.txt"

[Files]
Source: "bootstrap.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\kuro_logo.ico"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopIconTask}"
Name: "autostart"; Description: "{cm:AutostartTask}"; Flags: unchecked
Name: "brains"; Description: "{cm:BrainsTask}"

[Icons]
Name: "{autoprograms}\Kuro OS"; Filename: "{sys}\wscript.exe"; Parameters: "//nologo ""{code:CodeDir}\kuro.vbs"""; WorkingDir: "{code:CodeDir}"; IconFilename: "{app}\kuro_logo.ico"
Name: "{autodesktop}\Kuro OS"; Filename: "{sys}\wscript.exe"; Parameters: "//nologo ""{code:CodeDir}\kuro.vbs"""; WorkingDir: "{code:CodeDir}"; IconFilename: "{app}\kuro_logo.ico"; Tasks: desktopicon
Name: "{userstartup}\Kuro OS"; Filename: "{sys}\wscript.exe"; Parameters: "//nologo ""{code:CodeDir}\kuro.vbs"""; WorkingDir: "{code:CodeDir}"; IconFilename: "{app}\kuro_logo.ico"; Tasks: autostart
Name: "{autoprograms}\{cm:StopApp}"; Filename: "{code:CodeDir}\tat-kuro.bat"; WorkingDir: "{code:CodeDir}"; IconFilename: "{app}\kuro_logo.ico"
Name: "{autoprograms}\{cm:UpdateApp}"; Filename: "{code:CodeDir}\cap-nhat.bat"; WorkingDir: "{code:CodeDir}"; IconFilename: "{app}\kuro_logo.ico"

[Registry]
Root: HKCU; Subkey: "Software\KuroOS"; ValueType: string; ValueName: "InstallDir"; ValueData: "{code:CodeDir}"; Flags: uninsdeletekey

[Run]
Filename: "{sys}\wscript.exe"; Parameters: "//nologo ""{code:CodeDir}\kuro.vbs"""; WorkingDir: "{code:CodeDir}"; Description: "{cm:LaunchNow}"; Check: BootstrapOk; Flags: postinstall skipifsilent nowait
Filename: "{win}\notepad.exe"; Parameters: """{app}\install.log"""; Description: "{cm:OpenLog}"; Check: not BootstrapOk; Flags: postinstall skipifsilent nowait

[UninstallDelete]
Type: files; Name: "{app}\install.log"

[CustomMessages]
vi.DesktopIconTask=Đặt biểu tượng Kuro OS ra Desktop
vi.AutostartTask=Tự chạy Kuro OS khi tôi đăng nhập Windows
vi.BrainsTask=Cài các công cụ AI dòng lệnh từ chính hãng (Claude Code, Antigravity, Codex)
vi.LaunchNow=Mở Kuro OS ngay
vi.OpenLog=Mở nhật ký lỗi để gửi cho người hỗ trợ
vi.FinishedHelp=Còn MỘT bước bạn làm tay: đăng nhập AI.%n- Claude: mở Kuro > Cài đặt > chọn Tài khoản Claude > bấm "Đăng nhập Claude CLI".%n- Antigravity: mở PowerShell, gõ agy một lần, đăng nhập Google.
vi.StopApp=Tắt Kuro OS
vi.UpdateApp=Cập nhật Kuro OS
vi.DirTitle=Thư mục chứa Kuro
vi.DirDesc=Kuro được tải về đây (kèm ký ức, lịch sử và tệp .env của bạn).
vi.DirLabel=Chọn thư mục. Nên để mặc định. Thư mục này phải trống hoặc đã là bản Kuro cài trước đó.
vi.DirBad=Đường dẫn không hợp lệ hoặc không tạo được thư mục. Chọn ổ đĩa và thư mục bạn có quyền ghi.
vi.DirNotEmpty=Thư mục này đã có tệp nhưng không phải bản Kuro. Chọn thư mục trống hoặc thư mục Kuro cũ.
vi.Bootstrapping=Đang kiểm tra máy và cài những gì còn thiếu
vi.BootstrappingDesc=Việc này mất vài phút, lần đầu lâu hơn. Windows có thể hỏi quyền quản trị: bấm Yes.
vi.Step1=Bước 1/5: kiểm tra Git
vi.Step2=Bước 2/5: tải Kuro về máy
vi.Step3=Bước 3/5: kiểm tra Python, Node.js và các bộ não AI
vi.Step4=Bước 4/5: cài thư viện Python (bước lâu nhất)
vi.Step5=Sắp xong: hoàn tất cài đặt
vi.BootstrapFailed=Cài đặt chưa xong:%n%n%1%n%nSửa xong thì chạy lại KuroOS-Setup.exe, các bước đã xong sẽ được bỏ qua.%n%nNhật ký đầy đủ: %2
vi.NotFinishedTitle=Kuro OS chưa cài xong
vi.NotFinishedText=Có một bước cài chưa xong. Chạy lại KuroOS-Setup.exe, các bước đã xong sẽ được bỏ qua.%n%nNhật ký: %1
vi.DataKept=Đã gỡ Kuro OS khỏi máy.%n%nThư mục Kuro (ký ức, lịch sử, .env) vẫn được giữ ở:%n%1%n%nMuốn xóa sạch thì tự xóa thư mục đó.
en.DesktopIconTask=Put a Kuro OS icon on the Desktop
en.AutostartTask=Start Kuro OS when I sign in to Windows
en.BrainsTask=Install the AI command-line tools from their vendors (Claude Code, Antigravity, Codex)
en.LaunchNow=Open Kuro OS now
en.OpenLog=Open the error log to send to support
en.FinishedHelp=One step is left for you: sign in to the AI.%n- Claude: open Kuro > Settings > Claude account > click "Sign in to Claude CLI".%n- Antigravity: open PowerShell, type agy once, sign in with Google.
en.StopApp=Stop Kuro OS
en.UpdateApp=Update Kuro OS
en.DirTitle=Kuro folder
en.DirDesc=Kuro is downloaded here (with your memory, history and .env file).
en.DirLabel=Pick a folder. The default is fine. It must be empty or an earlier Kuro install.
en.DirBad=Invalid path or the folder cannot be created. Pick a drive and folder you can write to.
en.DirNotEmpty=This folder has files but is not a Kuro install. Pick an empty folder or the old Kuro folder.
en.Bootstrapping=Checking this computer and installing what is missing
en.BootstrappingDesc=This takes a few minutes, longer the first time. Windows may ask for admin rights: click Yes.
en.Step1=Step 1 of 5: checking Git
en.Step2=Step 2 of 5: downloading Kuro
en.Step3=Step 3 of 5: checking Python, Node.js and the AI brains
en.Step4=Step 4 of 5: installing Python libraries (the longest step)
en.Step5=Almost done: finishing up
en.BootstrapFailed=Setup did not finish:%n%n%1%n%nFix it, then run KuroOS-Setup.exe again: steps already done are skipped.%n%nFull log: %2
en.NotFinishedTitle=Kuro OS is not installed yet
en.NotFinishedText=One install step did not finish. Run KuroOS-Setup.exe again: steps already done are skipped.%n%nLog: %1
en.DataKept=Kuro OS was removed from this computer.%n%nYour Kuro folder (memory, history, .env) is kept in:%n%1%n%nDelete that folder by hand if you want everything gone.

[Code]
var
  DirPage: TInputDirWizardPage;
  ProgPage: TOutputMarqueeProgressWizardPage;
  LogMemo: TNewMemo;
  LastLogCount: Integer;
  BootOk: Boolean;
  KeptDir: String;

function SendMessage(hWnd: HWND; Msg: UINT; wParam: Longint; lParam: Longint): Longint;
  external 'SendMessageW@user32.dll stdcall';

function CodeDir(Param: String): String;
begin
  Result := DirPage.Values[0];
end;

function BootstrapOk: Boolean;
begin
  Result := BootOk;
end;

function DefaultKuroDir: String;
var
  S: String;
begin
  S := ExpandConstant('{param:KURODIR|}');
  if S = '' then
    if not RegQueryStringValue(HKCU, 'Software\KuroOS', 'InstallDir', S) or (S = '') then
      S := 'C:\Kuro-os\Kuro';
  Result := S;
end;

procedure InitializeWizard;
begin
  DirPage := CreateInputDirPage(wpWelcome, CustomMessage('DirTitle'), CustomMessage('DirDesc'),
    CustomMessage('DirLabel'), False, '');
  DirPage.Add('');
  DirPage.Values[0] := DefaultKuroDir;
end;

{ Hiện 200 dòng cuối của nhật ký trong khung log, cuộn xuống cuối }
procedure ShowLogTail(const LogFile: String);
var
  Lines: TArrayOfString;
  I, N, First: Integer;
  S: String;
begin
  try
    if not LoadStringsFromFile(LogFile, Lines) then Exit;
  except
    Exit;   { bootstrap đang ghi dở: lần quét sau đọc được }
  end;
  N := GetArrayLength(Lines);
  if N = LastLogCount then Exit;
  LastLogCount := N;
  First := N - 200;
  if First < 0 then First := 0;
  S := '';
  for I := First to N - 1 do
    S := S + Lines[I] + #13#10;
  LogMemo.Text := S;
  SendMessage(LogMemo.Handle, $0115, 7, 0);   { WM_VSCROLL, SB_BOTTOM }
end;

function DirHasFiles(const D: String): Boolean;
var
  FR: TFindRec;
begin
  Result := False;
  if FindFirst(D + '\*', FR) then
  try
    repeat
      if (FR.Name <> '.') and (FR.Name <> '..') then
      begin
        Result := True;
        Break;
      end;
    until not FindNext(FR);
  finally
    FindClose(FR);
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  D: String;
begin
  Result := True;
  if CurPageID = DirPage.ID then
  begin
    D := RemoveBackslashUnlessRoot(Trim(DirPage.Values[0]));
    DirPage.Values[0] := D;
    if (Length(D) < 4) or (Copy(D, 2, 2) <> ':\') then
    begin
      MsgBox(CustomMessage('DirBad'), mbError, MB_OK);
      Result := False;
    end
    else if DirExists(D) and DirHasFiles(D) and not DirExists(D + '\.git') then
    begin
      MsgBox(CustomMessage('DirNotEmpty'), mbError, MB_OK);
      Result := False;
    end
    else if not ForceDirectories(D) then
    begin
      MsgBox(CustomMessage('DirBad'), mbError, MB_OK);
      Result := False;
    end;
  end;
end;

{ Dòng đầu của tệp trạng thái: "<bước>|<chi tiết>" khi đang chạy, "DONE|<mã thoát>|<thông báo>" khi xong. }
function ReadStatus(const FileName: String; var Step: Integer; var Detail: String;
  var Done: Boolean; var Code: Integer; var Msg: String): Boolean;
var
  Lines: TArrayOfString;
  L, Rest: String;
  P: Integer;
begin
  Result := False;
  try
    if not LoadStringsFromFile(FileName, Lines) then Exit;
  except
    Exit;   { bootstrap đang ghi dở: lần quét sau sẽ đọc được }
  end;
  if GetArrayLength(Lines) = 0 then Exit;
  L := Lines[0];
  P := Pos('|', L);
  if P = 0 then Exit;
  if Copy(L, 1, P - 1) = 'DONE' then
  begin
    Rest := Copy(L, P + 1, Length(L));
    P := Pos('|', Rest);
    if P = 0 then Exit;
    Code := StrToIntDef(Copy(Rest, 1, P - 1), 1);
    Msg := Copy(Rest, P + 1, Length(Rest));
    Done := True;
  end
  else
  begin
    Step := StrToIntDef(Copy(L, 1, P - 1), 1);
    Detail := Copy(L, P + 1, Length(L));
  end;
  Result := True;
end;

procedure RunBootstrap;
var
  Args, StatusFile, LogFile, Detail, Msg: String;
  RC, Step, Code, Waited: Integer;
  Done: Boolean;
begin
  StatusFile := ExpandConstant('{tmp}\kuro-status.txt');
  LogFile := ExpandConstant('{app}\install.log');
  DeleteFile(StatusFile);
  DeleteFile(LogFile);
  Args := '-NoProfile -ExecutionPolicy Bypass -File "' + ExpandConstant('{app}\bootstrap.ps1') +
    '" -Dir "' + DirPage.Values[0] + '" -LogFile "' + LogFile + '" -StatusFile "' + StatusFile +
    '" -NoIcon -NoPause';
  if WizardIsTaskSelected('brains') then Args := Args + ' -Codex' else Args := Args + ' -SkipCli';

  ProgPage := CreateOutputMarqueeProgressPage(CustomMessage('Bootstrapping'), CustomMessage('BootstrappingDesc'));
  { Khung log trực tiếp (thay cửa sổ dòng lệnh đen) nằm dưới thanh tiến độ }
  LogMemo := TNewMemo.Create(ProgPage);
  LogMemo.Parent := ProgPage.Surface;
  LogMemo.Left := 0;
  LogMemo.Top := ProgPage.ProgressBar.Top + ProgPage.ProgressBar.Height + ScaleY(12);
  LogMemo.Width := ProgPage.Surface.Width;
  LogMemo.Height := ProgPage.Surface.Height - LogMemo.Top;
  LogMemo.Anchors := [akLeft, akTop, akRight, akBottom];
  LogMemo.ReadOnly := True;
  LogMemo.ScrollBars := ssVertical;
  LogMemo.Font.Name := 'Consolas';
  LogMemo.Font.Size := 8;
  ProgPage.Show;
  try
    Step := 1; Detail := ''; Done := False; Code := 1; Msg := ''; Waited := 0;
    ProgPage.SetText(CustomMessage('Step1'), '');
    if not Exec(ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe'), Args, '', SW_HIDE, ewNoWait, RC) then
      Msg := SysErrorMessage(RC)
    else
      { Tối đa 150 phút (bootstrap tự giới hạn từng bước); bootstrap luôn ghi DONE kể cả khi lỗi. }
      while (not Done) and (Waited < 9000000) do
      begin
        Sleep(300);
        Waited := Waited + 300;
        if ReadStatus(StatusFile, Step, Detail, Done, Code, Msg) and not Done then
        begin
          ProgPage.SetText(CustomMessage('Step' + IntToStr(Step)), Detail);
        end;
        ShowLogTail(LogFile);
        ProgPage.Animate;
      end;
    ShowLogTail(LogFile);
    BootOk := Done and (Code = 0);
    if not BootOk then
    begin
      if Msg = '' then Msg := '?';
      MsgBox(FmtMessage(CustomMessage('BootstrapFailed'), [Msg, LogFile]), mbError, MB_OK);
    end;
  finally
    ProgPage.Hide;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then RunBootstrap;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if (CurPageID = wpFinished) and BootOk then
    WizardForm.FinishedLabel.Caption := WizardForm.FinishedLabel.Caption + #13#10#13#10 + CustomMessage('FinishedHelp');
  if (CurPageID = wpFinished) and not BootOk then
  begin
    WizardForm.FinishedHeadingLabel.Caption := CustomMessage('NotFinishedTitle');
    WizardForm.FinishedLabel.Caption := FmtMessage(CustomMessage('NotFinishedText'), [ExpandConstant('{app}\install.log')]);
  end;
end;

{ Gỡ cài đặt: tắt Kuro đang chạy, nhưng giữ thư mục Kuro (ký ức, lịch sử, .env). }
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  RC: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    if RegQueryStringValue(HKCU, 'Software\KuroOS', 'InstallDir', KeptDir) and
       FileExists(KeptDir + '\tat-kuro.bat') then
      Exec(KeptDir + '\tat-kuro.bat', '', KeptDir, SW_HIDE, ewWaitUntilTerminated, RC);
  end
  else if (CurUninstallStep = usPostUninstall) and (KeptDir <> '') then
    MsgBox(FmtMessage(CustomMessage('DataKept'), [KeptDir]), mbInformation, MB_OK);
end;
