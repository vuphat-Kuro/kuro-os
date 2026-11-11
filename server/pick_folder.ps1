[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.Windows.Forms

$dialog = New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description = "Chọn thư mục dự án làm việc cho Kuro OS"
$dialog.ShowNewFolderButton = $true
$dialog.AutoUpgradeEnabled = $true

# Form ảo TopMost để ép hộp thoại luôn hiển thị phía trước màn hình
$form = New-Object System.Windows.Forms.Form
$form.TopMost = $true
$form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen

$res = $dialog.ShowDialog($form)
if ($res -eq [System.Windows.Forms.DialogResult]::OK -and $dialog.SelectedPath) {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::WriteLine($dialog.SelectedPath)
} else {
    [Console]::WriteLine("")
}
