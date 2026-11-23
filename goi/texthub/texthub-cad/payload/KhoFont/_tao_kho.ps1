# Tao lai KHO FONT gon cua phong tu may nguon.
# Bang ma SHX lay tu HEADER tep: unifont = Unicode, shapes = 8 bit (TCVN3), bigfont = BigFont. PowerShell 5.1.
# Chay: powershell -File _tao_kho.ps1            (chep cac tep con thieu, bao tep khong thay nguon)
# Chi chep tep; KHONG cai font, KHONG ghi registry. Nguon: %LOCALAPPDATA%\Microsoft\Windows\Fonts (TTF da cai cho nguoi dung)
# va thu muc Fonts cua AutoCAD (SHX). Bo font he thong cua Windows (Arial, Times New Roman, Segoe UI) va SHX di kem AutoCAD
# (txt, romans, simplex): luon co san tren may CAD.
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$ttfSrc = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts'
$shxSrc = @('C:\Program Files\Autodesk\AutoCAD 2020\Fonts', (Join-Path $root '..\04-Fonts-SHX'))

# ten tep | ho font | bang ma | ly do
$ttf = @(
    @('VnTime.TTF',                   '.VnTime',               'TCVN3', 'Font TCVN3 thuong, thuong gap trong ban ve cu'),
    @('VnTime-Bold.TTF',              '.VnTime Bold',          'TCVN3', 'Bien the dam'),
    @('VnTime-Italic.TTF',            '.VnTime Italic',        'TCVN3', 'Bien the nghieng'),
    @('VnTime-Bold-Italic.TTF',       '.VnTime Bold Italic',   'TCVN3', 'Bien the dam nghieng'),
    @('VnTimeH.TTF',                  '.VnTimeH',              'TCVN3', 'Font HOA di cap .VnTime'),
    @('VnTimeH-Bold.TTF',             '.VnTimeH Bold',         'TCVN3', 'Bien the dam'),
    @('VnTimeH-Italic.TTF',           '.VnTimeH Italic',       'TCVN3', 'Bien the nghieng'),
    @('VnTimeH-Bold-Italic.TTF',      '.VnTimeH Bold Italic',  'TCVN3', 'Bien the dam nghieng'),
    @('vnarial.ttf',                  '.VnArial',              'TCVN3', 'Font TCVN3 pho bien; co trong ma \f cua MTEXT ban ve Da giao xa mu'),
    @('vnarialb.ttf',                 '.VnArial Bold',         'TCVN3', 'Bien the dam'),
    @('VnArial-Italic.TTF',           '.VnArial Italic',       'TCVN3', 'Bien the nghieng'),
    @('VnArial-Bold-Italic.TTF',      '.VnArial Bold Italic',  'TCVN3', 'Bien the dam nghieng'),
    @('VnArialH.TTF',                 '.VnArialH',             'TCVN3', 'Font HOA, dung 53 lan trong Da giao xa mu'),
    @('VnArialH-Bold.TTF',            '.VnArialH Bold',        'TCVN3', 'Bien the dam'),
    @('VnArialH-Italic.TTF',          '.VnArialH Italic',      'TCVN3', 'Bien the nghieng'),
    @('VnArialH-Bold-Italic.TTF',     '.VnArialH Bold Italic', 'TCVN3', 'Bien the dam nghieng'),
    @('VnArial-Narrow.TTF',           '.VnArial Narrow',       'TCVN3', 'Kho hep'),
    @('VnArial-Narrow-Bold.TTF',      '.VnArial Narrow Bold',  'TCVN3', 'Bien the dam'),
    @('VnArial-Narrow-Italic.TTF',    '.VnArial Narrow Italic','TCVN3', 'Bien the nghieng'),
    @('VnArial-NarrowH.TTF',          '.VnArial NarrowH',      'TCVN3', 'Font HOA kho hep, dung 302 lan trong Da giao xa mu'),
    @('VnAvant.TTF',                  '.VnAvant',              'TCVN3', 'Font TCVN3 thuong'),
    @('VnAvant-Bold.TTF',             '.VnAvant Bold',         'TCVN3', 'Bien the dam'),
    @('VnAvant-Italic.TTF',           '.VnAvant Italic',       'TCVN3', 'Bien the nghieng'),
    @('VnAvant-Bold-Italic.TTF',      '.VnAvant Bold Italic',  'TCVN3', 'Bien the dam nghieng'),
    @('VnAvantH.TTF',                 '.VnAvantH',             'TCVN3', 'Font HOA, dung 304 lan trong Da giao xa mu'),
    @('VnAvantH-Bold.TTF',            '.VnAvantH Bold',        'TCVN3', 'Bien the dam'),
    @('VnAvantH-Italic.TTF',          '.VnAvantH Italic',      'TCVN3', 'Bien the nghieng'),
    @('VnAvantH-Bold-Italic.TTF',     '.VnAvantH Bold Italic', 'TCVN3', 'Bien the dam nghieng'),
    @('VNI-Times.TTF',                'VNI-Times',             'VNI',   'Font VNI pho bien nhat'),
    @('VNI-Times-Bold.TTF',           'VNI-Times Bold',        'VNI',   'Bien the dam'),
    @('VNI-Times-Italic.TTF',         'VNI-Times Italic',      'VNI',   'Bien the nghieng'),
    @('VNI-Times-Bold-Italic.TTF',    'VNI-Times Bold Italic', 'VNI',   'Bien the dam nghieng'),
    @('VNI-Helve.TTF',                'VNI-Helve',             'VNI',   'Font VNI khong chan'),
    @('VHELVEB.TTF',                  'VNI-Helve-Bold',        'VNI',   'Bien the dam'),
    @('VHELVEI.TTF',                  'VNI-Helve-Italic',      'VNI',   'Bien the nghieng'),
    @('VHELVEBI.TTF',                 'VNI-Helve-Bold-Italic', 'VNI',   'Bien the dam nghieng'),
    @('VHELVCN.TTF',                  'VNI-Helve-Condense',    'VNI',   'Kho hep'),
    @('BeVietnamPro-Regular.ttf',     '.Be Vietnam Pro',       'Unicode', 'Font Unicode dang dung trong ban ve moi'),
    @('BeVietnamPro-Bold.ttf',        '.Be Vietnam Pro Bold',  'Unicode', 'Bien the dam'),
    @('BeVietnamPro-Italic.ttf',      '.Be Vietnam Pro Italic','Unicode', 'Bien the nghieng'),
    @('BeVietnamPro-BoldItalic.ttf',  '.Be Vietnam Pro Bold Italic', 'Unicode', 'Bien the dam nghieng'),
    @('.BeVietnamProH-Regular.ttf',   '.Be Vietnam Pro H',     'Unicode', 'Ban chu HOA (khai bao trong style ban ve)'),
    @('BeVietnamProH-Bold.ttf',       '.Be Vietnam Pro H Bold','Unicode', 'Bien the dam'),
    @('BeVietnamProH-Italic.ttf',     '.Be Vietnam Pro H Italic', 'Unicode', 'Bien the nghieng'),
    @('BeVietnamProH-BoldItalic.ttf', '.Be Vietnam Pro H Bold Italic', 'Unicode', 'Bien the dam nghieng')
)
$shx = @(
    @('VN_UNI.shx',     'VN_UNI',     'Unicode', 'SHX unifont (Unicode) tieng Viet, dung 1.133 lan trong Da giao xa mu'),
    @('VN1.SHX',        'VN1',        'BigFont', 'SHX bigfont di cap vntime.shx (\Fvntime,vn1)'),
    @('VNTIME.SHX',     'vntime',     'TCVN3',   'SHX TCVN3, dung trong Style va MTEXT'),
    @('VNTIMEH.SHX',    'vntimeh',    'TCVN3',   'SHX TCVN3 chu HOA'),
    @('VN-ABC.SHX',     'vn-abc',     'TCVN3',   'SHX TCVN3 ABC, dung 168 lan'),
    @('uv-abc.shx',     'uv-abc',     'Unicode', 'SHX unifont (Unicode), co trong style cua ban ve'),
    @('VNSIMPLE.SHX',   'vnsimple',   'TCVN3',   'SHX net don gian, co trong style cua ban ve'),
    @('3T-Unicode.shx', '3T-Unicode', 'Unicode', 'SHX Unicode, co trong style cua ban ve'),
    @('ads civil.shx',  'ads civil',  'Unicode', 'SHX chuyen nganh xay dung, co trong style cua ban ve'),
    @('unicode.shx',    'unicode',    'Unicode', 'SHX Unicode chung'),
    @('vns.shx',        'vns',        'BigFont', 'SHX bigfont (header bigfont), khong phai font chu thuong')
)

New-Item -ItemType Directory -Force "$root\TTF", "$root\SHX" | Out-Null
$csv = @('file,type,family,charset,reason,status')
function Copy-One($name, $dir, $sources) {
    $dst = Join-Path $dir $name
    if (Test-Path -LiteralPath $dst) { return 'da co' }
    foreach ($s in $sources) {
        $p = Join-Path $s $name
        if (Test-Path -LiteralPath $p) { Copy-Item -LiteralPath $p -Destination $dst; return 'da chep' }
    }
    return 'THIEU NGUON'
}
foreach ($f in $ttf) { $st = Copy-One $f[0] "$root\TTF" @($ttfSrc);  $csv += ('"{0}",ttf,"{1}",{2},"{3}",{4}' -f $f[0], $f[1], $f[2], $f[3], $st); if ($st -eq 'THIEU NGUON') { "THIEU: $($f[0])" } }
foreach ($f in $shx) { $st = Copy-One $f[0] "$root\SHX" $shxSrc;     $csv += ('"{0}",shx,"{1}",{2},"{3}",{4}' -f $f[0], $f[1], $f[2], $f[3], $st); if ($st -eq 'THIEU NGUON') { "THIEU: $($f[0])" } }
[IO.File]::WriteAllLines("$root\_danh_sach.csv", $csv, (New-Object Text.UTF8Encoding($false)))
$n1 = (Get-ChildItem "$root\TTF" -File).Count; $n2 = (Get-ChildItem "$root\SHX" -File).Count
$mb = [math]::Round(((Get-ChildItem $root -Recurse -File | Measure-Object Length -Sum).Sum / 1MB), 1)
"Kho font: $n1 TTF + $n2 SHX = $($n1 + $n2) tep, $mb MB"
