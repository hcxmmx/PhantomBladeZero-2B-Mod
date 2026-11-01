"""Package only allowlisted cooked assets; never installs into a game directory."""
from pathlib import Path
import argparse,json,subprocess,tempfile,shutil,zipfile
r=Path(__file__).resolve().parents[1];p=r/'project/ProjectPBZ';c=p/'Saved/Cooked/Windows'
a=argparse.ArgumentParser();a.add_argument('--unreal-root',type=Path,required=True);a.add_argument('--output',type=Path,default=r/'release');args=a.parse_args()
exe=args.unreal_root/'Engine/Binaries/Win64/UnrealPak.exe';assert exe.is_file(),exe
allow=json.loads((r/'metadata/cook-allowlist.json').read_text());settings=json.loads((r/'metadata/settings.json').read_text());version=settings['version'];args.output.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='hcx2b-package-') as temp:
 t=Path(temp);stage=t/'stage';dest=stage/'ProjectPBZ/Content/Paks/~mods';dest.mkdir(parents=True);name='zzz_Hcxmmx2B_Retarget_P';files=[]
 for rel in allow:
  f=c/'ProjectPBZ'/rel;assert f.is_file(),f
  files.append(f)
  files.extend(x for ext in ['.uexp','.ubulk','.uptnl'] if (x:=f.with_suffix(ext)).is_file())
 response=t/'response.txt';response.write_text('\n'.join(f'"{f.as_posix()}" "../../../{f.relative_to(c).as_posix()}"' for f in files),encoding='utf-8')
 commands=t/'commands.txt';commands.write_text(f'-Output="{(dest/(name+".utoc")).as_posix()}" -ContainerName={name} -ResponseFile="{response.as_posix()}"\n',encoding='utf-8')
 subprocess.run([str(exe),str(p/'ProjectPBZ.uproject'),'-CreateGlobalContainer='+str(t/'global.utoc'),'-CookedDirectory='+str(c),'-Commands='+str(commands),'-PackageStoreManifest='+str(c/'ProjectPBZ/Metadata/packagestore.manifest'),'-ScriptObjects='+str(c/'ProjectPBZ/Metadata/scriptobjects.bin'),'-TargetPlatform=Windows','-unattended'],check=True)
 marker=t/'marker.txt';marker.write_text('Hcxmmx 2B '+version,encoding='utf-8');mr=t/'marker-response.txt';mr.write_text(f'"{marker.as_posix()}" "../../../ProjectPBZ/Content/Hcx2B/marker.txt"\n',encoding='utf-8')
 subprocess.run([str(exe),str(dest/(name+'.pak')),'-Create='+str(mr)],check=True)
 shutil.copy2(r/'CREDITS.md',stage/'CREDITS.md');shutil.copy2(r/'docs/INSTALL.md',stage/'安装说明.md')
 archive=args.output/f'Hcxmmx_2B_PBZ_v{version}.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for f in stage.rglob('*'):
   if f.is_file():z.write(f,f.relative_to(stage).as_posix())
 print(archive)
