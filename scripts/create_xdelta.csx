#!/usr/bin/env dotnet-script
#r "nuget: xdelta3.net, 1.0.1"

using xdelta3.net;

Directory.CreateDirectory("out/xdelta/data/");
Directory.CreateDirectory("out/xdelta/overlay/");
CreatePatch("original_files/arm9.bin", "temp_files/arm9.bin", "out/xdelta/arm9.bin");
CreatePatch("original_files/banner.bin", "temp_files/banner.bin", "out/xdelta/banner.bin");
CreatePatch("original_files/overlay/overlay_0012.bin", "temp_files/overlay_0012.bin", "out/xdelta/overlay/overlay_0012.bin");
CreatePatch("original_files/data/dat.bin", "temp_files/dat.bin", "out/xdelta/data/dat.bin");
CreatePatch("original_files/data/evt.bin", "temp_files/evt.bin", "out/xdelta/data/evt.bin");
CreatePatch("original_files/data/grp.bin", "temp_files/grp.bin", "out/xdelta/data/grp.bin");

void CreatePatch(string source, string target, string output) {
  var sourceBytes = File.ReadAllBytes(source);
  var targetBytes = File.ReadAllBytes(target);
  var delta = Xdelta3Lib.Encode(sourceBytes, targetBytes);
  File.WriteAllBytes(output, delta.ToArray());
}