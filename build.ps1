$ChokuretsuCli = "tools/HaruhiChokuretsuCLI/bin/Release/net6.0/HaruhiChokuretsuCLI.exe"

# Download the original files
if (-not(Test-Path -Path "original_files/arm9.bin" -PathType "Leaf")) {
  Invoke-WebRequest $env:ORIGINAL_FILES_URL -OutFile "original_files.zip"
  Expand-Archive -Path "original_files.zip" -DestinationPath "original_files/"
}

# Build and run the CLI
if (-not(Test-Path -Path $ChokuretsuCli -PathType "Leaf")) {
  Push-Location "tools/HaruhiChokuretsuCLI"
  dotnet restore
  dotnet build -c "Release" -f "net6.0"
  Pop-Location
}

New-Item "temp_files/" -Type "Directory" -Force
if (Test-Path -Path "out/" -PathType "Container") {
  Remove-Item -Path "out/" -Recurse -Force
}

# Patch arm9.bin for line height and font size
dotnet-script scripts/patch_arm9.csx

# Create new font
& "$ChokuretsuCli" extract -i "original_files/data/dat.bin" -n 0x071 -o "temp_files/dat_071.bin"
& "$ChokuretsuCli" extract -i "original_files/data/grp.bin" -n 0xE50 -o "temp_files/grp_E50.png"
python "scripts/create_font.py"
& "$ChokuretsuCli" replace -i "original_files/data/grp.bin" -o "temp_files/grp.bin" -r "temp_files/E50.bin"
& "$ChokuretsuCli" replace -i "temp_files/grp.bin" -o "temp_files/grp.bin" -r "temp_files/E50.png"

# Import texts
& "$ChokuretsuCli" json-import -i "original_files/data/evt.bin" -f "texts/zh_Hans/" -c "temp_files/char_map.json" -o "temp_files/evt.bin"
& "$ChokuretsuCli" json-import -i "original_files/data/dat.bin" -f "texts/zh_Hans/" -c "temp_files/char_map.json" -o "temp_files/dat.bin" -d
& "$ChokuretsuCli" replace -i "temp_files/dat.bin" -o "temp_files/dat.bin" -r "temp_files/071.bin"

# Import images
& "$ChokuretsuCli" replace -i "temp_files/grp.bin" -o "temp_files/grp.bin" -r "files/images/"

# Edit banner
dotnet-script scripts/edit_banner.csx

# Edit hardcoded string
python "scripts/edit_hardcoded_string.py"

# Create xdelta patches
dotnet-script scripts/create_xdelta.csx

# Copy md5.txt
Copy-Item -Path "files/md5.txt" -Destination "out/md5.txt" -Force

# create patch.zip
Compress-Archive -Path "out/*" -DestinationPath "patch.zip" -Force