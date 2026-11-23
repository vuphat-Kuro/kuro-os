# Cong cu thu giao dien bang UI Automation (chi dieu khien phien AutoCAD cua em, theo PID).
# Dung: powershell -File uia.ps1 -Pid 123 -Action list|click|read -Name "Quet ban ve"
param([int]$ProcId, [string]$Action = 'list', [string]$Name = '', [int]$Max = 80)
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
$p = Get-Process -Id $ProcId
$cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $ProcId)
$tops = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)
$all = New-Object System.Collections.ArrayList
foreach ($tw in $tops) { [void]$all.Add($tw); foreach ($e in $tw.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)) { [void]$all.Add($e) } }
function Find-ByName($n) {
    foreach ($e in $all) { if ($e.Current.Name -eq $n) { return $e } }
    return $null
}
if ($Action -eq 'list') {
    $i = 0
    foreach ($e in $all) {
        $n = $e.Current.Name; $t = $e.Current.ControlType.ProgrammaticName -replace 'ControlType\.', ''
        if ($n -and $t -in 'Button', 'Tab', 'TabItem', 'Text', 'ComboBox', 'CheckBox', 'DataItem', 'Edit', 'List', 'ListItem', 'Table', 'MenuItem', 'Menu') { "{0,-10} {1}" -f $t, $n; if (++$i -ge $Max) { break } }
    }
}
elseif ($Action -eq 'click') {
    $e = Find-ByName $Name
    if (-not $e) { "KHONG THAY: $Name"; exit 3 }
    $ip = $null
    if ($e.TryGetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern, [ref]$ip)) { $ip.Invoke(); "da bam: $Name" }
    else {
        $sp = $null
        if ($e.TryGetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern, [ref]$sp)) { $sp.Select(); "da chon: $Name" } else { "khong bam duoc: $Name"; exit 4 }
    }
}
elseif ($Action -eq 'read') {
    $e = Find-ByName $Name
    if (-not $e) { "KHONG THAY: $Name"; exit 3 }
    $vp = $null
    if ($e.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern, [ref]$vp)) { $vp.Current.Value } else { $e.Current.Name }
}
