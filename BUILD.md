# Сборка SolidCraft под Windows 7 SP1 x64

Сборка ведётся на Linux (проверено: Ubuntu 24.04, 1 ядро, 4 ГБ ОЗУ). Время первой сборки на одном ядре — 2–3 часа, повторной — минуты.

## 1. Инструменты

| Что | Зачем |
|---|---|
| Rust **stable** (rustup, профиль minimal) + компонент **rust-src** | компилятор; std для цели win7 собирается из исходников |
| RUSTC_BOOTSTRAP=1 | разрешает -Zbuild-std на stable (nightly не подходит: крейт branches на nightly не компилируется) |
| mingw-w64 | линкер x86_64-w64-mingw32-gcc, windres, ar, gcc для C-зависимостей |
| python3, python3-pefile | проверка и правка таблиц импорта exe |
| wine64, wine32:i386, wine-mono 8.1.0, WiX Toolset 3.14 | сборка MSI с мастером установки |
| xvfb (необязательно) | проверка запуска под Wine перед выдачей |

```
curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal -c rust-src
sudo dpkg --add-architecture i386 && sudo apt update
sudo apt install mingw-w64 python3-pefile p7zip-full wine64 wine32:i386 xvfb
```

Мало памяти (меньше 6 ГБ): CARGO_BUILD_JOBS=1 и файл подкачки 2–3 ГБ, иначе rustc падает на крейте cadmpeg-ir. Для него в профиле win7 задан opt-level = 1.

## 2. Исходники и патчи

```
unzip solidcraft-X.Y.Z.zip && cd solidcraft-X.Y.Z
patch -p1 < ../solidcraft-win7/patches/solidcraft-win7.patch
```

Что меняет [patches/solidcraft-win7.patch](patches/solidcraft-win7.patch):

1. **Cargo.toml**: профиль win7 (release без LTO и отладочной информации), подмена wgpu-hal на vendor/wgpu-hal.
2. **apps/solidcraft/Cargo.toml**: функция angle — включает в wgpu-hal путь EGL/ANGLE.
3. **native_frame.rs**: GetDpiForWindow и GetSystemMetricsForDpi (Windows 10) ищутся в user32 во время работы, без них — 96 DPI.
4. **startup.rs**: запасная графика DX12 | GL вместо одного DX12.
5. **win7.rs, main.rs**: журнал в %LOCALAPPDATA%\SolidCraft\solidcraft-log.txt (шаги запуска, первые кадры), стандартная рамка окна, автовыбор графики.
6. **toolbar.rs, metrics.rs**: кнопки ленты до 96 px, колонка подписей диалогов до 1,85 базовой ширины, подписи панелей с заглавной только первого слова — под русский текст.
7. **assets/locales/ru.json**: русский каталог.

Если патч не ложится на новую версию, перенесите эти правки вручную — они небольшие.

### wgpu-hal с EGL/ANGLE на Windows

Официальный wgpu-hal на Windows умеет OpenGL только через WGL. EGL-путь в нём уже поддерживает окна Win32 и ANGLE, он просто отключён для Windows. Скопируйте крейт версии из Cargo.lock в vendor/wgpu-hal и примените [patches/wgpu-hal-angle.patch](patches/wgpu-hal-angle.patch): функция angle_win подключает модуль egl вместо wgl, а для Windows добавляется заглушка wayland_sys.

```
cargo fetch
cp -r ~/.cargo/registry/src/*/wgpu-hal-<версия> vendor/wgpu-hal
cd vendor/wgpu-hal && patch -p1 < ../../../solidcraft-win7/patches/wgpu-hal-angle.patch && cd ../..
cargo metadata --offline --format-version 1 >/dev/null   # обновит Cargo.lock
```

## 3. Компиляция

Всё это делает [tools/build_win7.sh](tools/build_win7.sh). Вручную:

```
export RUSTC_BOOTSTRAP=1 CARGO_BUILD_JOBS=1
export CARGO_TARGET_X86_64_WIN7_WINDOWS_GNU_LINKER=x86_64-w64-mingw32-gcc
export CARGO_TARGET_X86_64_WIN7_WINDOWS_GNU_RUSTFLAGS="-C target-feature=+crt-static -C link-arg=-static-libgcc -C link-arg=-static"
export CC_x86_64_win7_windows_gnu=x86_64-w64-mingw32-gcc RC_x86_64_win7_windows_gnu=x86_64-w64-mingw32-windres
cargo build -Zbuild-std=std,panic_abort --profile win7 --locked --target x86_64-win7-windows-gnu -p solidcraft --features angle
cargo build -Zbuild-std=std,panic_abort --profile win7 --locked --target x86_64-win7-windows-gnu -p solidcraft-cli
```

Готовый solidcraft.exe переименуйте в **solidcraft-angle.exe**. Не кладите рядом файл с именем solidcraft.exe: сборка ANGLE передаёт ему ключи --software и --safe-mode и ушла бы в цикл.

## 4. Импорты Windows 8+ и w7shim.dll

Крейт windows подключает несколько функций, которых нет в Windows 7: exe с ними не запустится («точка входа не найдена»).

| Функция | Библиотека | Что делает w7shim |
|---|---|---|
| GetOverlappedResultEx | kernel32 | ожидание с тайм-аутом через WaitForSingleObjectEx + GetOverlappedResult |
| PathCchStripPrefix | api-ms-win-core-path-l1-1-0 | убирает префиксы \\?\ и \\?\UNC\ |
| RoOriginateErrorW | api-ms-win-core-winrt-error-l1-1-0 | заглушка (FALSE) |
| CoTaskMemFree, CoCreateFreeThreadedMarshaler | combase | переадресация в ole32 |

```
x86_64-w64-mingw32-gcc -O2 -shared -s -o w7shim.dll shim/w7shim.c shim/w7shim.def -static-libgcc
python3 tools/patch.py solidcraft-angle.exe solidcraft-cli.exe   # переименует дескрипторы импорта в w7shim.dll
python3 tools/scan.py  solidcraft-angle.exe solidcraft-cli.exe   # должен показать только w7shim.dll
```

Если в новой версии появятся другие функции Windows 8+, добавьте их в BAD в tools/patch.py и реализацию в shim/.

## 5. ANGLE

libEGL.dll, libGLESv2.dll, d3dcompiler_47.dll берутся из [Electron 22.3.27 win32-x64](https://github.com/electron/electron/releases/download/v22.3.27/electron-v22.3.27-win32-x64.zip) — последней ветки Chromium с поддержкой Windows 7. Их импорты проверены: функций Windows 8+ нет.

## 6. Установщик MSI

Установщик **обязательно с мастером на русском языке и страницей выбора папки** (по умолчанию C:\Program Files\SolidCraft). Инструмент — WiX 3.14 под Wine в режиме wow64 ([tools/make_installer.sh](tools/make_installer.sh)):

```
# один раз
WINEPREFIX=~/.wine-wix wine64 wineboot -i            # должна появиться папка syswow64
WINEPREFIX=~/.wine-wix wine64 msiexec /i wine-mono-8.1.0-x86.msi /qn
unzip wix314-binaries.zip -d ~/wix
# сборка
WINEPREFIX=~/.wine-wix tools/make_installer.sh solidcraft-X.Y.Z-win7-x64-d3d11_v1.msi
```

Тонкости: расширения WiX указывать по имени файла (путь Linux WiX принимает за ключ); сжатие только mszip (LZX под Wine не работает); ключ -sval обязателен (проверки ICE под Wine не работают). Тот же UpgradeCode 6A145FD6-D285-428D-AE84-A69570CDF4DB — новая версия заменяет старую и ставится в ту же папку.

## 7. Проверка перед выпуском

Под wine64 (winecfg -v win7) и Xvfb запустите solidcraft-angle.exe: в журнале должны быть adapter chosen Gl ANGLE … Direct3D11, frame 2 drawn и running; откройте образец Sample Plate и убедитесь, что 3D-вид рисуется. Затем msiexec /i — мастер и путь по умолчанию.

## Русификация

Каталог — [locales/ru.json](locales/ru.json); новые ключи из en.json переводятся в той же терминологии (документ, соединение, по траектории, по сечениям, вид по нормали, исходный вид, показать всё, коллизии, массив по сетке, визуализация, сетка). Скрипты [l10n/](l10n) повторяют раскладку ленты и диалогов со шрифтом IBM Plex Sans и показывают надписи, которые не помещаются: кнопка ленты — 2 строки по 86 px (12 pt), подпись поля — до ~125 px (12,5 pt).
