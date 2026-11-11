import sys
import os

def try_tkinter(initialdir):
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        root.focus_force()
        folder = filedialog.askdirectory(
            title="Chọn thư mục dự án làm việc cho Kuro OS",
            initialdir=initialdir or None
        )
        root.destroy()
        if folder:
            return folder.strip()
    except Exception:
        pass
    return None

def try_powershell():
    import subprocess
    ps_code = (
        "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8\n"
        "Add-Type -AssemblyName System.Windows.Forms\n"
        "$f = New-Object System.Windows.Forms.FolderBrowserDialog\n"
        "$f.Description = 'Chon thu muc du an lam viec cho Kuro OS'\n"
        "$f.ShowNewFolderButton = $true\n"
        "$topForm = New-Object System.Windows.Forms.Form\n"
        "$topForm.TopMost = $true\n"
        "if ($f.ShowDialog($topForm) -eq [System.Windows.Forms.DialogResult]::OK) {\n"
        "    Write-Output $f.SelectedPath\n"
        "}\n"
    )
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-STA", "-Command", ps_code],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=180
        )
        out = res.stdout.strip()
        if out and os.path.isdir(out):
            return out
    except Exception:
        pass
    return None

def main():
    initial = sys.argv[1] if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]) else ""
    # Ưu tiên 1: tkinter (native Windows Folder Dialog, cực mượt, có TopMost)
    folder = try_tkinter(initial)
    # Dự phòng 2: PowerShell STA FolderBrowserDialog với TopMost Form
    if not folder:
        folder = try_powershell()

    if folder:
        # Ghi UTF-8 ra stdout
        sys.stdout.buffer.write(folder.encode("utf-8"))
        sys.stdout.buffer.flush()
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
