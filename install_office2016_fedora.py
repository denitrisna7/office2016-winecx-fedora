#!/usr/bin/env python3
import os, re, shutil, subprocess, sys, time
from pathlib import Path

HOME=Path.home()
DOWNLOADS=HOME/"Downloads"
PREFIX=HOME/".office2016"
WINECX=Path("/opt/winecx")
WINE=WINECX/"bin/wine"
WINESERVER=WINECX/"bin/wineserver"
WINETRICKS=shutil.which("winetricks") or "/usr/bin/winetricks"
REQ=DOWNLOADS/"Requerimientos Office 2016"
REQ_ZIP=DOWNLOADS/"Requerimientos Office 2016.zip"
ISO=DOWNLOADS/"SW_DVD5_Office_Professional_Plus_2016_W32_English_MLF_X20-41353.ISO"
EXTRACTED=DOWNLOADS/"SW_DVD5_Office_Professional_Plus_2016_W32_English_MLF_X20-41353"
LOG=DOWNLOADS/"office2016_v3_13_4.log"

CORE=["WINWORD.EXE","EXCEL.EXE","POWERPNT.EXE"]
OPTIONAL=["OUTLOOK.EXE","MSACCESS.EXE","MSPUB.EXE"]
REPO_DISABLE=[
 "--disablerepo=gustavosett-clipboard-manager-source",
 "--disablerepo=gustavosett-clipboard-manager-noarch",
 "--disablerepo=gustavosett-clipboard-manager"
]
PACKAGES=("gcc gcc-c++ clang llvm lld flex bison glibc-devel glibc-devel.i686 "
"libX11-devel libX11-devel.i686 libXext-devel libXext-devel.i686 "
"libXinerama-devel libXinerama-devel.i686 libXrender-devel libXrender-devel.i686 "
"libXi-devel libXi-devel.i686 libXcursor-devel libXcursor-devel.i686 "
"libXrandr-devel libXrandr-devel.i686 libXcomposite-devel libXcomposite-devel.i686 "
"libXfixes-devel libXfixes-devel.i686 libXdamage-devel libXdamage-devel.i686 "
"libxkbcommon-devel libxkbcommon-x11-devel freetype-devel freetype-devel.i686 "
"fontconfig-devel fontconfig-devel.i686 libpng-devel libpng-devel.i686 "
"libjpeg-turbo-devel libjpeg-turbo-devel.i686 libtiff-devel libtiff-devel.i686 "
"libxml2-devel libxml2-devel.i686 libxslt-devel libxslt-devel.i686 libunwind-devel "
"wayland-devel wayland-devel.i686 alsa-lib-devel alsa-lib-devel.i686 "
"pulseaudio-libs-devel pulseaudio-libs-devel.i686 cups-devel cups-devel.i686 "
"sane-backends-devel sane-backends-devel.i686 libv4l-devel libv4l-devel.i686 "
"libgphoto2-devel libgphoto2-devel.i686 gsm-devel gsm-devel.i686 "
"openal-soft-devel openal-soft-devel.i686 vulkan-loader-devel vulkan-loader-devel.i686 "
"mesa-libGL-devel mesa-libGL-devel.i686 mesa-libEGL-devel mesa-libEGL.i686 "
"systemd-devel systemd-devel.i686 libusb1-devel libusb1-devel.i686 "
"pcsc-lite-devel pcsc-lite-devel.i686 krb5-devel krb5-devel.i686 "
"sdl2-compat-devel gstreamer1-devel gstreamer1-plugins-base-devel dbus-devel "
"gnutls-devel gnutls-devel.i686 openldap-devel openldap-devel.i686 "
"libpcap-devel libpcap-devel.i686 ocl-icd-devel ocl-icd-devel.i686 "
"git wget2-wget curl pkgconf-pkg-config gettext "
"mingw64-gcc mingw64-gcc-c++ mingw64-binutils mingw32-gcc mingw32-gcc-c++ mingw32-binutils "
"cups cups-client cups-pdf system-config-printer msitools "
"bzip2-devel.i686 harfbuzz-devel.i686 brotli-devel.i686 graphite2-devel.i686 "
"winetricks cabextract samba samba-winbind gnutls mesa-libGL.i686 libglvnd-glx.i686 "
"ncurses-libs.i686 wine libXcomposite.i686 libXcursor.i686 libXrandr.i686 "
"libXinerama.i686 libXdamage.i686 pipewire-alsa pipewire-pulseaudio "
"pulseaudio-libs.i686 sane-backends-libs.i686 libusb1.i686 7zip").split()

def log(s=""):
    print(s)
    with LOG.open("a",encoding="utf-8") as f: f.write(s+"\n")

def env():
    e=os.environ.copy()
    e.update(WINEPREFIX=str(PREFIX),WINE=str(WINE),WINESERVER=str(WINESERVER),
             WINEDLLPATH=str(WINECX/"lib/wine"),PATH=f"{WINECX}/bin:"+e.get("PATH",""))
    return e

def run(cmd,check=True,capture=False):
    if capture:
        log("$ "+" ".join(map(str,cmd)))
    p=subprocess.run(
        cmd,
        env=env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if capture and p.stdout:
        log(p.stdout.rstrip())
    if capture and p.stderr:
        log(p.stderr.rstrip())
    if check and p.returncode:
        log(f"[ ERROR ] Command failed ({p.returncode}): {' '.join(map(str,cmd))}")
        if p.stdout: log(p.stdout.rstrip())
        if p.stderr: log(p.stderr.rstrip())
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(map(str,cmd))}")
    return p
def sudo(cmd,check=True,capture=False):
    return run(["sudo",*cmd],check,capture)

def office_files():
    out={}
    if not PREFIX.exists(): return {n:None for n in CORE+OPTIONAL}
    for n in CORE+OPTIONAL:
        out[n]=next((p for p in PREFIX.rglob("*") if p.is_file() and p.name.lower()==n.lower()),None)
    return out

def reg_evidence():
    h=[]
    for f in [PREFIX/"system.reg",PREFIX/"user.reg"]:
        if f.exists():
            t=f.read_text(errors="ignore")
            for x in ["90160000","Microsoft Office","Office16","PROPLUS"]:
                if x.lower() in t.lower(): h.append(f"{f.name}: {x}")
    return h

def office_state():
    files=office_files()
    dirs=[p for p in PREFIX.rglob("*") if p.is_dir() and p.name.lower()=="office16"] if PREFIX.exists() else []
    regs=reg_evidence()
    count=sum(bool(files[x]) for x in CORE)
    state="COMPLETE" if count==3 else "PARTIAL" if count else "REGISTERED_PARTIAL" if dirs and regs else "ABSENT"
    return state,files,dirs,regs

def show_state():
    s,f,d,r=office_state()
    log("\n=== OFFICE STATE ===")
    log("State: "+s)
    log("Office16 directories:")
    for x in d: log("  "+str(x))
    log("Core/Office executables:")
    for x in CORE+OPTIONAL: log(f"  {x}: {f[x] or '(missing)'}")
    log("Registry evidence:")
    for x in r: log("  "+x)
    return s,f

def create_desktop(name,display,comment,exe,cats,mime):
    sh=Path("/opt/wine/launchers")/(name+".sh")
    content=(
        "#!/bin/bash\nset -e\n"
        'export WINEPREFIX="$HOME/.office2016"\n'
        'export WINE="/opt/winecx/bin/wine"\n'
        'export WINESERVER="/opt/winecx/bin/wineserver"\n'
        'export WINEDLLPATH="/opt/winecx/lib/wine"\n'
        'export PATH="/opt/winecx/bin:$PATH"\n'
        'export LANG=C.UTF-8\nexport WINEDEBUG=-all\n'
        f"app='C:\\\\Program Files (x86)\\\\Microsoft Office\\\\Office16\\\\{exe}'\n"
        "/opt/winecx/bin/wineserver -p >/dev/null 2>&1 || true\n"
        'if [ $# -eq 0 ]; then exec /opt/winecx/bin/wine "$app"; fi\n'
        'for file in "$@"; do fullpath=$(realpath "$file"); '
        'winpath="Z:${fullpath//\\//\\\\}"; /opt/winecx/bin/wine "$app" "$winpath"; done\n'
    )
    tmp=DOWNLOADS/(".tmp-"+name+".sh")
    tmp.write_text(content,encoding="utf-8")
    sudo(["cp",str(tmp),str(sh)]); sudo(["chmod","+x",str(sh)]); tmp.unlink()
    desktop=(
        "[Desktop Entry]\n"
        f"Name={display}\nComment={comment}\nExec={sh} %F\n"
        "Type=Application\nStartupNotify=true\nTerminal=false\n"
        f"Icon=/usr/share/icons/hicolor/256x256/apps/{name}.png\nCategories={cats}\nMimeType={mime}\n"
    )
    dt=DOWNLOADS/(".tmp-"+name+".desktop")
    dt.write_text(desktop,encoding="utf-8")
    sudo(["cp",str(dt),f"/usr/share/applications/{name}.desktop"]); dt.unlink()

PROGRESS_STAGES = [
    "Source files",
    "Fedora dependencies",
    "WineCX",
    "Office prefix",
    "Winetricks",
    "Office detection",
    "Gecko / Mono",
    "DirectX fixes",
    "Office DLLs",
    "Office icons",
    "Fonts",
    "Launchers",
    "Final verification",
]

def progress(index, message):
    pct=int(round(index*100/len(PROGRESS_STAGES)))
    log(f"[{pct:3d}%] {message}")

def main():
    LOG.write_text("",encoding="utf-8")
    log("="*72)
    log("OFFICE 2016 + WINECX — FEDORA 44")
    log("V3.13.4 — GITHUB READY: QUIET + PROGRESS + ROBUST SOURCES/FONTS/ICONS")
    log("Fix: quiet subprocess output + percentage progress + verified Office icons")
    log("="*72)
    try:
        run(["sudo","-v"]); log("[ OK ] Sudo authentication successful.")
        for p in [ISO,DOWNLOADS/"FuentesOffice365.zip"]:
            if not p.exists(): raise RuntimeError("Missing source file: "+str(p))
        progress(1, "Source files ready")
        log("[ OK ] Required source files exist.")

        # The requirements archive is an official input source. Extract it
        # automatically when the folder has not yet been created.
        if not REQ.exists():
            if REQ_ZIP.exists():
                log("\n=== EXTRACT OFFICE 2016 REQUIREMENTS ===")
                run(["unzip","-o",str(REQ_ZIP),"-d",str(DOWNLOADS)])
                if not REQ.exists():
                    raise RuntimeError("Requirements ZIP extracted, but the expected folder was not found: "+str(REQ))
                log("[ OK ] Requerimientos Office 2016 extracted.")
            else:
                raise RuntimeError("Missing source file: "+str(REQ_ZIP))

        progress(2, "Installing Fedora dependencies")
        log("\n=== FEDORA DEPENDENCIES ===")
        sudo(["dnf","install","-y","--skip-unavailable",*REPO_DISABLE,*PACKAGES])
        log("[ OK ] Fedora dependencies")

        progress(3, "Preparing WineCX")
        log("\n=== WINECX ===")
        if not WINE.exists():
            z=DOWNLOADS/"winecx.zip"; src=DOWNLOADS/"winecx"
            if not src.exists() and z.exists(): run(["unzip","-o",str(z),"-d",str(DOWNLOADS)])
            if not src.exists(): raise RuntimeError("winecx source folder/zip not found")
            sudo(["mkdir","-p",str(WINECX)]); sudo(["cp","-r",str(src),"/opt/"])
        else: log("[INFO] /opt/winecx already exists; preserving it.")
        sudo(["chown","-R","root:root",str(WINECX)])
        sudo(["chmod","-R","a+rX",str(WINECX)])
        run([str(WINESERVER),"-k"],False)

        progress(4, "Preparing Office prefix")
        log("\n=== OFFICE 2016 PREFIX ===")
        PREFIX.mkdir(parents=True,exist_ok=True)
        run([str(WINE),"winecfg","-v","win7"]); log("[ OK ] Prefix Windows 7")

        progress(5, "Installing Winetricks components")
        log("\n=== WINETRICKS ===")
        def wt(*a, **kw): return run([WINETRICKS,*a], **kw)
        wt("--force","-q","gdiplus")
        wt("-q","corefonts","msxml6","riched20","riched30","vb6run","vcrun2005","vcrun2008","vcrun2010")
        wt("--force","-q","vcrun2012"); wt("-q","vcrun2013","dotnet48")
        p=wt("list-installed",capture=True,check=False)
        txt=(p.stdout or "")+(p.stderr or "")
        if "vcrun2019" not in txt.lower(): wt("--force","-q","vcrun2019")
        else: log("[INFO] vcrun2019 already installed; skipping conflicting vcrun2015.")
        run([str(WINE),"winecfg","-v","win7"]); run([str(WINESERVER),"-k"],False)

        progress(6, "Checking Office 2016 installation")
        log("\n=== EXTRACT OFFICE 2016 ISO ===")
        setup=EXTRACTED/"setup.exe"
        if not setup.exists(): run(["7z","x",str(ISO),f"-o{EXTRACTED}"])
        if not setup.exists(): raise RuntimeError("setup.exe not found after ISO extraction")
        log("[ OK ] setup.exe: "+str(setup))

        state,files=show_state()
        if state=="ABSENT":
            log("\n=== OFFICE 2016 GUI INSTALLER ===")
            log("[INFO] Complete the Office GUI installation before returning here.")
            p=run([str(WINE),str(setup)],False)
            log(f"[INFO] setup.exe returned {p.returncode}")
            time.sleep(3)
            state,files=show_state()
            missing=[x for x in CORE if not files[x]]
            if missing: raise RuntimeError("Office setup did not produce: "+", ".join(missing))
            log("[ OK ] Office 2016 GUI installation verified.")
        else:
            log("[ OK ] Office 2016 is already installed/present.")
            log("[INFO] Skipping setup.exe only; continuing all remaining PDF stages.")

        progress(7, "Installing Gecko / Mono")
        log("\n=== GECKO / MONO ===")
        for n,dest in [
            ("wine-gecko-2.47.4-x86.msi","/usr/share/wine/gecko"),
            ("wine-gecko-2.47.4-x86_64.msi","/usr/share/wine/gecko"),
            ("wine-mono-9.4.0-x86.msi","/usr/share/wine/mono")]:
            src=REQ/n
            if src.exists():
                sudo(["mkdir","-p",dest]); sudo(["cp",str(src),dest])
        run([str(WINE),"reg","add",r"HKLM\Software\Wine\Gecko","/v","Version","/t","REG_SZ","/d","2.47.4","/f"],False)
        run([str(WINE),"reg","add",r"HKLM\Software\Wine\Mono","/v","Version","/t","REG_SZ","/d","9.4.0","/f"],False)

        progress(8, "Applying DirectX fixes")
        log("\n=== DIRECTX FIXES ===")
        run([str(WINE),"reg","add",r"HKCU\Software\Wine\Direct2D","/v","max_version_factory","/t","REG_DWORD","/d","0","/f"])
        run([str(WINE),"reg","add",r"HKCU\Software\Wine\Direct3D","/v","MaxVersionGL","/t","REG_DWORD","/d","0x30002","/f"])

        log("\n=== LAUNCH EXCEL ===")
        if files.get("EXCEL.EXE"):
            run([str(WINE),str(files["EXCEL.EXE"])],False)
            time.sleep(5); run([str(WINESERVER),"-k"],False)

        progress(9, "Applying Office DLLs")
        log("\n=== OFFICE SOFTWARE PROTECTION DLLS ===")
        z=REQ/"OfficeSoftwareProtectionPlatform.zip"; d=REQ/"OfficeSoftwareProtectionPlatform"
        if z.exists() and not d.exists(): run(["unzip","-o",str(z),"-d",str(REQ)])
        if d.exists():
            common=PREFIX/"drive_c/Program Files (x86)/Common Files/Microsoft Shared/OfficeSoftwareProtectionPlatform"
            off=PREFIX/"drive_c/Program Files (x86)/Microsoft Office/Office16"
            common.mkdir(parents=True,exist_ok=True); off.mkdir(parents=True,exist_ok=True)
            for n in ["OSPPC.DLL","OSPPCEXT.DLL","sppcs.dll"]:
                if (d/n).exists(): shutil.copy2(d/n,common/n)
            if (d/"sppcs.dll").exists(): shutil.copy2(d/"sppcs.dll",off/"sppcs.dll")
        else: log("[WARN] OfficeSoftwareProtectionPlatform not found; continuing.")

        progress(10, "Installing Office icons")
        log("\n=== OFFICE ICONS ===")

        req_zip=DOWNLOADS/"Requerimientos Office 2016.zip"
        req_dir=DOWNLOADS/"Requerimientos Office 2016"

        # The actual source is a nested ZIP:
        # Requerimientos Office 2016.zip
        #   -> Requerimientos Office 2016/
        #      -> Office 2016 icons.zip
        if req_zip.exists() and not req_dir.exists():
            log("[INFO] Extracting Requerimientos Office 2016.zip")
            run(["unzip","-o",str(req_zip),"-d",str(DOWNLOADS)])

        icons_zip=req_dir/"Office 2016 icons.zip"
        icons_dir=req_dir/"Office 2016 icons"

        if icons_zip.exists() and not icons_dir.exists():
            log("[INFO] Extracting Office 2016 icons.zip")
            run(["unzip","-o",str(icons_zip),"-d",str(req_dir)])

        icon_target=Path("/usr/share/icons/hicolor/256x256/apps")
        sudo(["mkdir","-p",str(icon_target)],False)

        icon_names={
            "word2016":"word2016.png",
            "excel2016":"excel2016.png",
            "powerpoint2016":"powerpoint2016.png",
            "outlook2016":"outlook2016.png",
            "access2016":"access2016.png",
            "publisher2016":"publisher2016.png",
        }

        found={}
        if icons_dir.exists():
            for p in icons_dir.rglob("*"):
                if p.is_file() and p.suffix.lower() in {".png",".jpg",".jpeg",".ico",".svg"}:
                    stem=p.stem.lower().replace(" ","").replace("-","").replace("_","")
                    for key,dst_name in icon_names.items():
                        normalized=key.replace("_","")
                        if stem==normalized or key in stem:
                            found.setdefault(key,p)

        log(f"[ OK ] Found {len(found)} Office icon image(s).")

        for key,dst_name in icon_names.items():
            if key in found:
                src_icon=found[key]
                dst_icon=icon_target/dst_name

                if src_icon.suffix.lower()==".png":
                    sudo(["cp","-f",str(src_icon),str(dst_icon)],False)
                else:
                    # Convert non-PNG sources only if ImageMagick is available.
                    magick=shutil.which("magick") or shutil.which("convert")
                    if magick:
                        sudo([magick,str(src_icon),str(dst_icon)],False)
                    else:
                        log(f"[WARN] {dst_name}: source is {src_icon.suffix}, ImageMagick unavailable.")
                        continue

                sudo(["chmod","644",str(dst_icon)],False)
                log(f"[ OK ] {dst_name} <- {src_icon.name}")
            else:
                log(f"[WARN] Missing source icon: {dst_name}")

        sudo(["gtk-update-icon-cache","-f","-t","/usr/share/icons/hicolor"],False)
        sudo(["update-desktop-database","/usr/share/applications"],False)

        log("\n=== FONTS ===")
        z=DOWNLOADS/"FuentesOffice365.zip"
        d=DOWNLOADS/"FuentesOffice365"

        if z.exists() and not d.exists():
            run(["unzip","-o",str(z),"-d",str(DOWNLOADS)])

        if d.exists():
            fontdir=PREFIX/"drive_c/windows/Fonts"
            fontdir.mkdir(parents=True,exist_ok=True)

            # A previous run may have copied fonts with sudo/root ownership.
            # Repair only this Wine Fonts directory; never chown the whole
            # Wine prefix.
            uid_gid=f"{os.getuid()}:{os.getgid()}"
            sudo(["chown","-R",uid_gid,str(fontdir)],False)
            sudo(["chmod","u+rwx",str(fontdir)],False)

            font_sources=[]
            for ext in ("*.ttf","*.TTF","*.ttc","*.TTC","*.otf","*.OTF"):
                font_sources.extend(d.rglob(ext))

            copied=0
            failed=[]

            for p in sorted(set(font_sources)):
                dst=fontdir/p.name
                try:
                    if dst.exists():
                        sudo(["chown",uid_gid,str(dst)],False)
                        sudo(["chmod","644",str(dst)],False)

                    shutil.copy2(p,dst)
                    sudo(["chown",uid_gid,str(dst)],False)
                    sudo(["chmod","644",str(dst)],False)

                    # System font copy is optional. A failure here must not
                    # abort Office installation.
                    sudo(["cp","-f",str(p),"/usr/share/fonts/Windows/"],False)
                    copied += 1

                except Exception as e:
                    failed.append((p.name,str(e)))

            log(f"[ OK ] Fonts copied: {copied}/{len(font_sources)}")

            if failed:
                log(f"[WARN] {len(failed)} font(s) could not be copied; continuing.")
                for name,err in failed[:10]:
                    log(f"  {name}: {err}")

            reg=PREFIX/"allfonts.reg"
            lines=[
                "REGEDIT4",
                "",
                "[HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Fonts]"
            ]

            if fontdir.exists():
                for p in sorted(fontdir.iterdir()):
                    if p.suffix.lower() in [".ttf",".ttc",".otf"]:
                        label=re.sub("Regular","",p.stem.replace("_"," ")).strip()
                        lines.append(f'"{label} (TrueType)"="{p.name}"')

            reg.write_text("\n".join(lines)+"\n",encoding="utf-8")
            run([str(WINE),"regedit",str(reg)],False)
            sudo(["fc-cache","-f"],False)
        else:
            log("[INFO] FuentesOffice365 directory not found; continuing.")

        log("\n=== CREATE LAUNCHERS / ALL APPS ===")
        sudo(["mkdir","-p","/opt/wine/launchers"])
        apps=[
            ("word2016","Microsoft Word 2016","Microsoft Office 2016 Word Processor","WINWORD.EXE","Office;WordProcessor;","application/msword;application/vnd.openxmlformats-officedocument.wordprocessingml.document;application/rtf;text/plain;"),
            ("excel2016","Microsoft Excel 2016","Microsoft Office 2016 Spreadsheet","EXCEL.EXE","Office;Spreadsheet;","application/vnd.ms-excel;application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;text/csv;"),
            ("powerpoint2016","Microsoft PowerPoint 2016","Microsoft Office 2016 Presentations","POWERPNT.EXE","Office;Presentation;","application/vnd.ms-powerpoint;application/vnd.openxmlformats-officedocument.presentationml.presentation;"),
            ("outlook2016","Microsoft Outlook 2016","Microsoft Office 2016 Email Client","OUTLOOK.EXE","Office;Email;","application/vnd.ms-outlook;message/rfc822;"),
            ("access2016","Microsoft Access 2016","Microsoft Office 2016 Database","MSACCESS.EXE","Office;Database;","application/vnd.ms-access;application/x-msaccess;"),
            ("publisher2016","Microsoft Publisher 2016","Microsoft Office 2016 Publishing Editor","MSPUB.EXE","Office;Publishing;","application/x-mspublisher;")]
        for a in apps: create_desktop(*a)

        log("\n=== EXCEL ASSOCIATIONS ===")
        reg=DOWNLOADS/".fix_excel_associations.reg"
        reg.write_text(
            "Windows Registry Editor Version 5.00\n\n"
            "[HKEY_CLASSES_ROOT\\.xls]\n@=\"Excel.Sheet.8\"\n"
            "[HKEY_CLASSES_ROOT\\.xlsx]\n@=\"Excel.Sheet.12\"\n"
            "[HKEY_CLASSES_ROOT\\Excel.Sheet.8\\shell\\Open\\command]\n"
            "@=\"\\\\\\\"C:\\\\\\\\Program Files (x86)\\\\\\\\Microsoft Office\\\\\\\\Office16\\\\\\\\EXCEL.EXE\\\\\\\" \\\\\\\"%1\\\\\\\"\"\n"
            "[HKEY_CLASSES_ROOT\\Excel.Sheet.12\\shell\\Open\\command]\n"
            "@=\"\\\\\\\"C:\\\\\\\\Program Files (x86)\\\\\\\\Microsoft Office\\\\\\\\Office16\\\\\\\\EXCEL.EXE\\\\\\\" \\\\\\\"%1\\\\\\\"\"\n"
            "[HKEY_CLASSES_ROOT\\Excel.Sheet.8\\shell\\Open\\ddeexec]\n@=\"\"\n"
            "[HKEY_CLASSES_ROOT\\Excel.Sheet.12\\shell\\Open\\ddeexec]\n@=\"\"\n",
            encoding="utf-8")
        run([str(WINE),"regedit","/S",str(reg)],False); reg.unlink()

        log("\n=== UPDATE APPLICATION DATABASE ===")
        sudo(["update-desktop-database","/usr/share/applications"])
        run(["gtk-update-icon-cache","-f","/usr/share/icons/hicolor/"],False)

        progress(13, "Final verification")
        log("\n=== FINAL OFFICE VERIFICATION ===")
        state,files=show_state()
        if any(not files[x] for x in CORE): raise RuntimeError("Final Office verification failed")
        for n in ["word2016","excel2016","powerpoint2016","outlook2016","access2016","publisher2016"]:
            if not Path(f"/usr/share/applications/{n}.desktop").exists():
                raise RuntimeError("Missing launcher: "+n)
            icon=Path(f"/usr/share/icons/hicolor/256x256/apps/{n}.png")
            if not icon.exists() or icon.stat().st_size==0:
                raise RuntimeError("Missing Office icon: "+str(icon))
        log("[ OK ] WINWORD.EXE, EXCEL.EXE, POWERPNT.EXE found.")
        log("[ OK ] All 6 Office 2016 launchers created in All Apps.")
        run([str(WINESERVER),"-k"],False)
        log(f"\n[LOG] Detailed log: {LOG}")
        log("[DONE] Source files in ~/Downloads were preserved.")
        return 0
    except Exception as e:
        log("\n[ FAILED ] "+str(e))
        run([str(WINESERVER),"-k"],False)
        sudo(["update-desktop-database","/usr/share/applications"],False)
        log("[INFO] Wine processes stopped. Source files in ~/Downloads were preserved.")
        return 1

if __name__=="__main__":
    sys.exit(main())
