$ChokuretsuCli = "bin\ChokuretsuTranslationUtility\HaruhiChokuretsuCLI\bin\Release\net8.0\HaruhiChokuretsuCLI.exe"

# Download the original files
if (-not(Test-Path -Path "original_files\arm9.bin" -PathType "Leaf")) {
  Invoke-WebRequest $env:ORIGINAL_FILES_URL -OutFile "original_files.zip"
  Expand-Archive -Path "original_files.zip" -DestinationPath "original_files\"
}

# Build the CLI
if (-not(Test-Path -Path $ChokuretsuCli -PathType "Leaf")) {
  Push-Location "bin\ChokuretsuTranslationUtility\HaruhiChokuretsuCLI"
  dotnet restore
  dotnet build -c "Release" -f "net8.0"
  Pop-Location
}

# Clean output folder
if (Test-Path -Path "out\" -PathType "Container") {
  Remove-Item -Path "out\" -Recurse -Force
}
if (Test-Path -Path "temp\" -PathType "Container") {
  Remove-Item -Path "temp\" -Recurse -Force
}

# Patch arm9.bin
python scripts\compile_arm9_patch.py

# Prepare for creating font and importing text
& "$ChokuretsuCli" extract -i "original_files\data\dat.bin" -n 0x071 -o "temp\font\071_dat.bin"
& "$ChokuretsuCli" extract -i "original_files\data\grp.bin" -n 0xE50 -o "temp\font\E50_grp.bin"
& "$ChokuretsuCli" json-export -i "original_files\data\evt.bin" -o "temp\original_texts\" 2>$null | Out-Null
& "$ChokuretsuCli" json-export -i "original_files\data\dat.bin" -o "temp\original_texts\" -d 2>$null | Out-Null

# Copy archive files
New-Item -Path "temp\out\data\" -Type "Directory" -Force | Out-Null
Copy-Item -Path "original_files\data\dat.bin", "original_files\data\evt.bin", "original_files\data\grp.bin" -Destination "temp\out\data\" -Force

# Generate character table
python scripts\generate_char_table.py

# Create font
python scripts\create_font.py
& "$ChokuretsuCli" replace -i "temp\out\data\dat.bin" -o "temp\out\data\dat.bin" -r "temp\import\071_dat.bin"
& "$ChokuretsuCli" replace -i "temp\out\data\grp.bin" -o "temp\out\data\grp.bin" -r "temp\import\E50_grp.bin"

# Convert and import texts
python scripts\convert_json_from_texts.py
python scripts\convert_binary_from_texts.py
& "$ChokuretsuCli" json-import -i "temp\out\data\evt.bin" -f "temp\edited_texts\" -o "temp\out\data\evt.bin" 2>$null | Out-Null
& "$ChokuretsuCli" json-import -i "temp\out\data\dat.bin" -f "temp\edited_texts\" -o "temp\out\data\dat.bin" -d 2>$null | Out-Null

# Import images
& "$ChokuretsuCli" replace -i "temp\out\data\grp.bin" -o "temp\out\data\grp.bin" -r "files\images\"

# Edit banner
python scripts\edit_banner.py

# Create xdelta patches
python scripts\create_xdelta.py

# Create patch
Copy-Item -Path "files\md5.txt" -Destination "out\md5.txt" -Force
Compress-Archive -Path "out\xdelta\", "out\banner.bin", "out\md5.txt" -Destination "patch-ds.zip" -Force
Move-Item -Path "patch-ds.zip" -Destination "out\patch-ds.xzp" -Force
