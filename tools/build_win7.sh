#!/bin/bash
# Сборка SolidCraft (ANGLE / Direct3D 11) под Windows 7 SP1 x64 на Linux (Ubuntu 24.04).
# Использование: tools/build_win7.sh /путь/к/solidcraft-X.Y.Z   (распакованные исходники upstream)
set -euo pipefail
SRC=$(realpath "$1"); KIT=$(realpath "$(dirname "$0")/..")
. ~/.cargo/env
T=x86_64-win7-windows-gnu
cd "$SRC"
# 1. Патчи исходников и wgpu-hal с EGL/ANGLE на Windows
patch -p1 -N < "$KIT/patches/solidcraft-win7.patch" || echo "patch: проверьте .rej и перенесите правки вручную (BUILD.md)"
HAL=$(grep -A1 '^name = "wgpu-hal"' Cargo.lock | sed -n 's/version = "\(.*\)"/\1/p' | head -1)
cargo fetch
if [ ! -d vendor/wgpu-hal ]; then
  cp -r ~/.cargo/registry/src/*/wgpu-hal-$HAL vendor/wgpu-hal
  (cd vendor/wgpu-hal && rm -f .cargo_vcs_info.json && patch -p1 < "$KIT/patches/wgpu-hal-angle.patch")
fi
cp "$KIT/locales/ru.json" assets/locales/ru.json
cargo metadata --offline --format-version 1 >/dev/null
# 2. Компиляция: tier-3 цель win7, std собирается из rust-src
export RUSTC_BOOTSTRAP=1 CARGO_BUILD_JOBS=${JOBS:-1}
export CARGO_TARGET_X86_64_WIN7_WINDOWS_GNU_LINKER=x86_64-w64-mingw32-gcc
export CARGO_TARGET_X86_64_WIN7_WINDOWS_GNU_RUSTFLAGS="-C target-feature=+crt-static -C link-arg=-static-libgcc -C link-arg=-static"
export CC_x86_64_win7_windows_gnu=x86_64-w64-mingw32-gcc CXX_x86_64_win7_windows_gnu=x86_64-w64-mingw32-g++
export AR_x86_64_win7_windows_gnu=x86_64-w64-mingw32-ar RC_x86_64_win7_windows_gnu=x86_64-w64-mingw32-windres WINDRES=x86_64-w64-mingw32-windres
B="-Zbuild-std=std,panic_abort --profile win7 --locked --target $T"
cargo build $B -p solidcraft --features angle
mkdir -p "$KIT/out/s7"
cp target/$T/win7/solidcraft.exe "$KIT/out/s7/solidcraft-angle.exe"
cargo build $B -p solidcraft-cli
cp target/$T/win7/solidcraft-cli.exe "$KIT/out/s7/"
cp LICENSE-MIT LICENSE-APACHE NOTICE THIRD-PARTY-LICENSES.txt "$KIT/out/s7/"
# 3. Совместимость с Windows 7: w7shim.dll и переименование импортов Windows 8+
cd "$KIT/out"
x86_64-w64-mingw32-gcc -O2 -shared -s -o s7/w7shim.dll "$KIT/shim/w7shim.c" "$KIT/shim/w7shim.def" -static-libgcc
python3 "$KIT/tools/patch.py" s7/solidcraft-angle.exe s7/solidcraft-cli.exe
python3 "$KIT/tools/scan.py" s7/solidcraft-angle.exe s7/solidcraft-cli.exe
# 4. ANGLE из Electron 22 (последняя ветка Chromium с поддержкой Windows 7)
if [ ! -f s7/libGLESv2.dll ]; then
  curl -sL -o el.zip https://github.com/electron/electron/releases/download/v22.3.27/electron-v22.3.27-win32-x64.zip
  unzip -o -q el.zip libEGL.dll libGLESv2.dll d3dcompiler_47.dll LICENSE -d s7 && mv s7/LICENSE s7/ANGLE-ELECTRON-LICENSE.txt && rm el.zip
fi
cp "$KIT/installer/README-WIN7.txt" s7/
echo "Готово: $KIT/out/s7. Дальше: tools/make_installer.sh"
