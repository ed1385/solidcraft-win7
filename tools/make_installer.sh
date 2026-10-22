#!/bin/bash
# MSI с мастером установки (русский язык, выбор папки, по умолчанию C:\Program Files\SolidCraft).
# Нужны: wine64 + wine32:i386 (wow64), wine-mono 8.1.0, WiX Toolset 3.14 (wix314-binaries.zip) в $WIX.
set -euo pipefail
KIT=$(realpath "$(dirname "$0")/..")
WIX=${WIX:-$HOME/wix}; OUT=${1:-solidcraft-win7-x64-d3d11.msi}
export PATH=/usr/lib/wine:$PATH WINEDEBUG=-all
cd "$KIT/out"
cp "$KIT/installer/solidcraft-win7.wxs" "$KIT/installer/solidcraft.ico" .
cp "$WIX/WixUIExtension.dll" "$WIX/WixUtilExtension.dll" .
wine64 "$WIX/candle.exe" -nologo -arch x64 -ext WixUIExtension.dll -ext WixUtilExtension.dll solidcraft-win7.wxs
wine64 "$WIX/light.exe" -nologo -sval -ext WixUIExtension.dll -ext WixUtilExtension.dll -cultures:ru-ru -out "$OUT" solidcraft-win7.wixobj
ls -la "$OUT"
