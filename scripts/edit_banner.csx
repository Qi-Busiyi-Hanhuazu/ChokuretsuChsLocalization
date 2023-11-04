#!/usr/bin/env dotnet-script
#r "nuget: NitroHelper, 0.11.1"

var banner = new NitroHelper.Banner("original_files/banner.bin");
banner.japaneseTitle = "凉宫春日的串联\nSEGA";
banner.englishTitle = "凉宫春日的串联\nSEGA";
banner.frenchTitle = "凉宫春日的串联\nSEGA";
banner.germanTitle = "凉宫春日的串联\nSEGA";
banner.italianTitle = "凉宫春日的串联\nSEGA";
banner.spanishTitle = "凉宫春日的串联\nSEGA";
banner.WriteTo("temp_files/banner.bin");
Console.WriteLine("Banner saved.");