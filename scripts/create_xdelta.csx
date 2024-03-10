#!/usr/bin/env dotnet-script
#r "nuget: xdelta3.net, 1.0.1"

using xdelta3.net;

Directory.CreateDirectory("out/patch/xdelta/data/");
Directory.CreateDirectory("out/patch/xdelta/overlay/");
CreatePatch("original_files/arm9.bin", "temp_files/arm9.bin", "out/patch/xdelta/arm9.bin");
CreatePatch("original_files/banner.bin", "temp_files/banner.bin", "out/patch/xdelta/banner.bin");
CreatePatch("original_files/overlay/overlay_0012.bin", "temp_files/overlay_0012.bin", "out/patch/xdelta/overlay/overlay_0012.bin");
CreatePatch("original_files/data/dat.bin", "temp_files/dat.bin", "out/patch/xdelta/data/dat.bin");
CreatePatch("original_files/data/evt.bin", "temp_files/evt.bin", "out/patch/xdelta/data/evt.bin");
CreatePatch("original_files/data/grp.bin", "temp_files/grp.bin", "out/patch/xdelta/data/grp.bin");

void CreatePatch(string source, string target, string output) {
  var sourceBytes = File.ReadAllBytes(source);
  var targetBytes = File.ReadAllBytes(target);
  var delta = Xdelta3Lib.Encode(sourceBytes, targetBytes);
  File.WriteAllBytes(output, delta.ToArray());
}