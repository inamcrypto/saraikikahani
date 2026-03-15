param(
    [Parameter(Mandatory = $true)]
    [string]$Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem

$sourcePath = (Resolve-Path $Path).Path
$sourceItem = Get-Item $sourcePath
$backupPath = [System.IO.Path]::Combine($sourceItem.DirectoryName, "$($sourceItem.BaseName).backup$($sourceItem.Extension)")
if (-not (Test-Path $backupPath)) {
    Copy-Item $sourcePath $backupPath
}

$tempRoot = Join-Path $env:TEMP ("docx-format-" + [guid]::NewGuid().ToString('N'))
[System.IO.Directory]::CreateDirectory($tempRoot) | Out-Null

try {
    [System.IO.Compression.ZipFile]::ExtractToDirectory($sourcePath, $tempRoot)

    $wordNs = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    $bodyFont = 'Urdu Typesetting'
    $bodyFontSize = '30'
    $titleFontSize = '40'
    $accentColor = '8B4513'

    $documentXmlPath = Join-Path $tempRoot 'word\document.xml'
    [xml]$docXml = Get-Content -LiteralPath $documentXmlPath
    $docNs = New-Object System.Xml.XmlNamespaceManager($docXml.NameTable)
    $docNs.AddNamespace('w', $wordNs)

    $paragraphs = $docXml.SelectNodes('//w:body/w:p', $docNs)
    $seenTitle = $false

    foreach ($paragraph in $paragraphs) {
        $textNodes = $paragraph.SelectNodes('.//w:t', $docNs)
        foreach ($textNode in $textNodes) {
            $textNode.InnerText = $textNode.InnerText -replace '\*\*', ''
        }

        $pPr = $paragraph.SelectSingleNode('w:pPr', $docNs)
        if ($null -eq $pPr) {
            $pPr = $docXml.CreateElement('w', 'pPr', $wordNs)
            if ($paragraph.FirstChild -ne $null) {
                [void]$paragraph.InsertBefore($pPr, $paragraph.FirstChild)
            }
            else {
                [void]$paragraph.AppendChild($pPr)
            }
        }

        $bidi = $pPr.SelectSingleNode('w:bidi', $docNs)
        if ($null -eq $bidi) {
            $bidi = $docXml.CreateElement('w', 'bidi', $wordNs)
            [void]$pPr.AppendChild($bidi)
        }

        $jc = $pPr.SelectSingleNode('w:jc', $docNs)
        if ($null -eq $jc) {
            $jc = $docXml.CreateElement('w', 'jc', $wordNs)
            [void]$pPr.AppendChild($jc)
        }
        [void]$jc.SetAttribute('val', $wordNs, 'right')

        $spacing = $pPr.SelectSingleNode('w:spacing', $docNs)
        if ($null -eq $spacing) {
            $spacing = $docXml.CreateElement('w', 'spacing', $wordNs)
            [void]$pPr.AppendChild($spacing)
        }
        [void]$spacing.SetAttribute('after', $wordNs, '180')
        [void]$spacing.SetAttribute('line', $wordNs, '420')
        [void]$spacing.SetAttribute('lineRule', $wordNs, 'auto')

        foreach ($runPr in $paragraph.SelectNodes('.//w:r/w:rPr', $docNs)) {
            $rFonts = $runPr.SelectSingleNode('w:rFonts', $docNs)
            if ($null -eq $rFonts) {
                $rFonts = $docXml.CreateElement('w', 'rFonts', $wordNs)
                if ($runPr.FirstChild -ne $null) {
                    [void]$runPr.InsertBefore($rFonts, $runPr.FirstChild)
                }
                else {
                    [void]$runPr.AppendChild($rFonts)
                }
            }
            foreach ($attr in @('ascii', 'hAnsi', 'cs', 'eastAsia')) {
                [void]$rFonts.SetAttribute($attr, $wordNs, $bodyFont)
            }

            $sz = $runPr.SelectSingleNode('w:sz', $docNs)
            if ($null -eq $sz) {
                $sz = $docXml.CreateElement('w', 'sz', $wordNs)
                [void]$runPr.AppendChild($sz)
            }
            [void]$sz.SetAttribute('val', $wordNs, $bodyFontSize)

            $szCs = $runPr.SelectSingleNode('w:szCs', $docNs)
            if ($null -eq $szCs) {
                $szCs = $docXml.CreateElement('w', 'szCs', $wordNs)
                [void]$runPr.AppendChild($szCs)
            }
            [void]$szCs.SetAttribute('val', $wordNs, $bodyFontSize)
        }

        $paragraphText = (($textNodes | ForEach-Object { $_.InnerText }) -join '').Trim()
        if ([string]::IsNullOrWhiteSpace($paragraphText)) {
            continue
        }

        if (-not $seenTitle) {
            $pStyle = $pPr.SelectSingleNode('w:pStyle', $docNs)
            if ($null -eq $pStyle) {
                $pStyle = $docXml.CreateElement('w', 'pStyle', $wordNs)
                if ($pPr.FirstChild -ne $null) {
                    [void]$pPr.InsertBefore($pStyle, $pPr.FirstChild)
                }
                else {
                    [void]$pPr.AppendChild($pStyle)
                }
            }
            [void]$pStyle.SetAttribute('val', $wordNs, 'Title')
            [void]$jc.SetAttribute('val', $wordNs, 'center')
            [void]$spacing.SetAttribute('after', $wordNs, '280')
            $seenTitle = $true
        }
    }

    $docXml.Save($documentXmlPath)

    $stylesXmlPath = Join-Path $tempRoot 'word\styles.xml'
    [xml]$stylesXml = Get-Content -LiteralPath $stylesXmlPath
    $stylesNs = New-Object System.Xml.XmlNamespaceManager($stylesXml.NameTable)
    $stylesNs.AddNamespace('w', $wordNs)

    $defaultsRPr = $stylesXml.SelectSingleNode('//w:docDefaults/w:rPrDefault/w:rPr', $stylesNs)
    $defaultsFonts = $defaultsRPr.SelectSingleNode('w:rFonts', $stylesNs)
    if ($null -eq $defaultsFonts) {
        $defaultsFonts = $stylesXml.CreateElement('w', 'rFonts', $wordNs)
        if ($defaultsRPr.FirstChild -ne $null) {
            [void]$defaultsRPr.InsertBefore($defaultsFonts, $defaultsRPr.FirstChild)
        }
        else {
            [void]$defaultsRPr.AppendChild($defaultsFonts)
        }
    }
    foreach ($attr in @('ascii', 'hAnsi', 'cs', 'eastAsia')) {
        [void]$defaultsFonts.SetAttribute($attr, $wordNs, $bodyFont)
    }

    foreach ($name in @('sz', 'szCs')) {
        $sizeNode = $defaultsRPr.SelectSingleNode("w:$name", $stylesNs)
        if ($null -eq $sizeNode) {
            $sizeNode = $stylesXml.CreateElement('w', $name, $wordNs)
            [void]$defaultsRPr.AppendChild($sizeNode)
        }
        [void]$sizeNode.SetAttribute('val', $wordNs, $bodyFontSize)
    }

    $lang = $defaultsRPr.SelectSingleNode('w:lang', $stylesNs)
    if ($null -eq $lang) {
        $lang = $stylesXml.CreateElement('w', 'lang', $wordNs)
        [void]$defaultsRPr.AppendChild($lang)
    }
    [void]$lang.SetAttribute('val', $wordNs, 'ur-PK')
    [void]$lang.SetAttribute('bidi', $wordNs, 'ur-PK')

    $defaultsPPr = $stylesXml.SelectSingleNode('//w:docDefaults/w:pPrDefault/w:pPr', $stylesNs)
    $defaultSpacing = $defaultsPPr.SelectSingleNode('w:spacing', $stylesNs)
    if ($null -eq $defaultSpacing) {
        $defaultSpacing = $stylesXml.CreateElement('w', 'spacing', $wordNs)
        [void]$defaultsPPr.AppendChild($defaultSpacing)
    }
    [void]$defaultSpacing.SetAttribute('after', $wordNs, '180')
    [void]$defaultSpacing.SetAttribute('line', $wordNs, '420')
    [void]$defaultSpacing.SetAttribute('lineRule', $wordNs, 'auto')

    $defaultBidi = $defaultsPPr.SelectSingleNode('w:bidi', $stylesNs)
    if ($null -eq $defaultBidi) {
        $defaultBidi = $stylesXml.CreateElement('w', 'bidi', $wordNs)
        [void]$defaultsPPr.AppendChild($defaultBidi)
    }

    $normalStyle = $stylesXml.SelectSingleNode("//w:style[@w:styleId='Normal']", $stylesNs)
    if ($null -ne $normalStyle) {
        $normalPPr = $normalStyle.SelectSingleNode('w:pPr', $stylesNs)
        if ($null -eq $normalPPr) {
            $normalPPr = $stylesXml.CreateElement('w', 'pPr', $wordNs)
            [void]$normalStyle.AppendChild($normalPPr)
        }
        if ($null -eq $normalPPr.SelectSingleNode('w:bidi', $stylesNs)) {
            [void]$normalPPr.AppendChild($stylesXml.CreateElement('w', 'bidi', $wordNs))
        }
        $normalJc = $normalPPr.SelectSingleNode('w:jc', $stylesNs)
        if ($null -eq $normalJc) {
            $normalJc = $stylesXml.CreateElement('w', 'jc', $wordNs)
            [void]$normalPPr.AppendChild($normalJc)
        }
        [void]$normalJc.SetAttribute('val', $wordNs, 'right')

        $normalRPr = $normalStyle.SelectSingleNode('w:rPr', $stylesNs)
        if ($null -eq $normalRPr) {
            $normalRPr = $stylesXml.CreateElement('w', 'rPr', $wordNs)
            [void]$normalStyle.AppendChild($normalRPr)
        }
        $normalFonts = $normalRPr.SelectSingleNode('w:rFonts', $stylesNs)
        if ($null -eq $normalFonts) {
            $normalFonts = $stylesXml.CreateElement('w', 'rFonts', $wordNs)
            [void]$normalRPr.AppendChild($normalFonts)
        }
        foreach ($attr in @('ascii', 'hAnsi', 'cs', 'eastAsia')) {
            [void]$normalFonts.SetAttribute($attr, $wordNs, $bodyFont)
        }
    }

    $titleStyle = $stylesXml.SelectSingleNode("//w:style[@w:styleId='Title']", $stylesNs)
    if ($null -ne $titleStyle) {
        $titlePPr = $titleStyle.SelectSingleNode('w:pPr', $stylesNs)
        if ($null -eq $titlePPr) {
            $titlePPr = $stylesXml.CreateElement('w', 'pPr', $wordNs)
            [void]$titleStyle.AppendChild($titlePPr)
        }
        if ($null -eq $titlePPr.SelectSingleNode('w:bidi', $stylesNs)) {
            [void]$titlePPr.AppendChild($stylesXml.CreateElement('w', 'bidi', $wordNs))
        }
        $titleJc = $titlePPr.SelectSingleNode('w:jc', $stylesNs)
        if ($null -eq $titleJc) {
            $titleJc = $stylesXml.CreateElement('w', 'jc', $wordNs)
            [void]$titlePPr.AppendChild($titleJc)
        }
        [void]$titleJc.SetAttribute('val', $wordNs, 'center')

        $titleRPr = $titleStyle.SelectSingleNode('w:rPr', $stylesNs)
        if ($null -eq $titleRPr) {
            $titleRPr = $stylesXml.CreateElement('w', 'rPr', $wordNs)
            [void]$titleStyle.AppendChild($titleRPr)
        }
        $titleFonts = $titleRPr.SelectSingleNode('w:rFonts', $stylesNs)
        if ($null -eq $titleFonts) {
            $titleFonts = $stylesXml.CreateElement('w', 'rFonts', $wordNs)
            [void]$titleRPr.AppendChild($titleFonts)
        }
        foreach ($attr in @('ascii', 'hAnsi', 'cs', 'eastAsia')) {
            [void]$titleFonts.SetAttribute($attr, $wordNs, $bodyFont)
        }
        foreach ($name in @('sz', 'szCs')) {
            $sizeNode = $titleRPr.SelectSingleNode("w:$name", $stylesNs)
            if ($null -eq $sizeNode) {
                $sizeNode = $stylesXml.CreateElement('w', $name, $wordNs)
                [void]$titleRPr.AppendChild($sizeNode)
            }
            [void]$sizeNode.SetAttribute('val', $wordNs, $titleFontSize)
        }
        $titleColor = $titleRPr.SelectSingleNode('w:color', $stylesNs)
        if ($null -eq $titleColor) {
            $titleColor = $stylesXml.CreateElement('w', 'color', $wordNs)
            [void]$titleRPr.AppendChild($titleColor)
        }
        [void]$titleColor.SetAttribute('val', $wordNs, $accentColor)
    }

    $stylesXml.Save($stylesXmlPath)

    $tempZip = Join-Path $env:TEMP ("formatted-" + [guid]::NewGuid().ToString('N') + '.zip')
    if (Test-Path $tempZip) {
        Remove-Item $tempZip -Force
    }

    [System.IO.Compression.ZipFile]::CreateFromDirectory($tempRoot, $tempZip)
    Copy-Item $tempZip $sourcePath -Force
}
finally {
    if (Test-Path $tempRoot) {
        Remove-Item $tempRoot -Recurse -Force
    }
}
