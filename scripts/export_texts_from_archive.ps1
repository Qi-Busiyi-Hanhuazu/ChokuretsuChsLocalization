$ChokuretsuCli = "bin\ChokuretsuTranslationUtility\HaruhiChokuretsuCLI\bin\Release\net8.0\HaruhiChokuretsuCLI.exe"

# Build the CLI
if (-not(Test-Path -Path $ChokuretsuCli -PathType "Leaf")) {
  Push-Location "bin\ChokuretsuTranslationUtility\HaruhiChokuretsuCLI"
  dotnet restore
  dotnet build -c "Release" -f "net8.0"
  Pop-Location
}

& "$ChokuretsuCli" json-export -i "original_files\data\evt.bin" -o "temp\original_texts\" 2>$null | Out-Null
& "$ChokuretsuCli" json-export -i "original_files\data\dat.bin" -o "temp\original_texts\" -d 2>$null | Out-Null
