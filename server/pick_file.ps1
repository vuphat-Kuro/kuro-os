[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.Windows.Forms

$dialog = New-Object System.Windows.Forms.OpenFileDialog
$dialog.Title = "Chọn tệp đính kèm gửi cho Kuro OS"
$dialog.Filter = "Tất cả tệp (*.*)|*.*|Tài liệu (*.xlsx;*.docx;*.pdf;*.txt;*.md;*.dwg)|*.xlsx;*.docx;*.pdf;*.txt;*.md;*.dwg|Hình ảnh (*.png;*.jpg;*.jpeg;*.webp)|*.png;*.jpg;*.jpeg;*.webp"
$dialog.Multiselect = $true
$dialog.CheckFileExists = $true

$form = New-Object System.Windows.Forms.Form
$form.TopMost = $true
$form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen

$res = $dialog.ShowDialog($form)
if ($res -eq [System.Windows.Forms.DialogResult]::OK -and $dialog.FileNames) {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    foreach ($f in $dialog.FileNames) {
        [Console]::WriteLine($f)
    }
} else {
    [Console]::WriteLine("")
}
