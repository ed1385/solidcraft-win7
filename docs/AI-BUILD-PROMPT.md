# Промт: сборка SolidCraft под Windows 7 SP1 x64 (графика ANGLE / Direct3D 11) и русификация

Скопируйте текст ниже в новый чат вместе с архивом исходников новой версии SolidCraft (solidcraft-X_Y_Z.zip) и этим комплектом solidcraft-win7-kit.zip.

---

Изучи исходники SolidCraft в архиве и собери установщик MSI для моего ПК. Работай по шагам ниже до конца, без промежуточных отчётов; если какой-то шаг не проходит, исправь причину и продолжай. Ответы давай на русском.

ЦЕЛЕВАЯ СИСТЕМА
- Windows 7 Профессиональная SP1 x64 (6.1.7601), Intel Core i5-3450, встроенная графика Intel HD Graphics 2500 (драйвер 9.17.10.4229: OpenGL 4.0, Direct3D 11, без Vulkan и D3D12).
- Работает только вариант с ANGLE (OpenGL ES 3.0 поверх Direct3D 11). Драйвер OpenGL Intel даёт чёрное окно, программная графика Mesa медленная — их в установщик не включать.

ШАГ 1. ИНСТРУМЕНТЫ (контейнер Linux)
- Rust stable (rustup, профиль minimal, компонент rust-src); собирать с RUSTC_BOOTSTRAP=1. Nightly не использовать: крейт branches на nightly не компилируется.
- Цель x86_64-win7-windows-gnu (tier 3), флаги: -Zbuild-std=std,panic_abort, профиль win7 (наследует release, lto=false, debug=false, codegen-units=16, strip=true).
- mingw-w64 (x86_64-w64-mingw32-gcc как линкер и CC/CXX/AR/RC для цели), RUSTFLAGS цели: -C target-feature=+crt-static -C link-arg=-static-libgcc -C link-arg=-static.
- msitools и wixl (MSI в синтаксисе WiX v3), python3-pefile, p7zip, при желании wine64 и xvfb для проверки.
- Машина маленькая: CARGO_BUILD_JOBS=1, файл подкачки 1,5–3 ГБ (иначе rustc падает по памяти на cadmpeg-ir). Для cadmpeg-ir в профиле win7 задать opt-level = 1.
- Контейнер может перезапускаться: сборку вести в фоне (setsid nohup), после перезапуска просто запускать снова — собранное сохраняется.

ШАГ 2. ПАТЧИ ИСХОДНИКОВ (комплект, папка patches)
- Сначала попробуй patch -p1 < patches/solidcraft-win7.patch в корне исходников. Если версия другая и патч не ложится, внеси те же изменения вручную:
  1) apps/solidcraft/src/native_frame.rs: GetDpiForWindow и GetSystemMetricsForDpi (Windows 10) искать через GetProcAddress в user32; без них 96 DPI и GetSystemMetrics.
  2) apps/solidcraft/src/startup.rs: запасной вариант графики DX12 | GL вместо одного DX12 (на Win7 нет D3D12/WARP).
  3) apps/solidcraft/src/win7.rs (новый) и main.rs: журнал stderr в %LOCALAPPDATA%\SolidCraft\solidcraft-log.txt (SetStdHandle через GetProcAddress, чтобы не менять набор features windows-sys), простой логгер, вывод шагов запуска (log_phase, startup_step) и строк frame 1/2 drawn.
  4) main.rs: стандартная рамка окна Windows по умолчанию (своя рамка — ключ --custom-frame); с собственной рамкой верхняя панель на Win7 не рисуется.
  5) Cargo.toml приложения: функция angle = ["dep:wgpu-hal"], зависимость wgpu-hal =ВЕРСИЯ с features = ["angle_win"]; в корневом Cargo.toml [patch.crates-io] wgpu-hal = { path = "vendor/wgpu-hal" }; в main.rs при cfg!(feature = "angle") не включать Mesa и автопереключение.
  6) crates/ui-egui/src/toolbar.rs: BUTTON_MAX_WIDTH 76 → 96; подписи панелей ленты для нелатинских языков — заглавная только у первого слова (короткие аббревиатуры DXF, 3D не трогать).
  7) crates/ui-egui/src/ui_kit/metrics.rs: LABEL_COLUMN_MAX 1.6 → 1.85.
- wgpu-hal: скопируй крейт той версии, что в Cargo.lock, в vendor/wgpu-hal и примени patches/wgpu-hal-angle.patch (или вручную): функция angle_win = ["gles"]; в src/gles/mod.rs на Windows при angle_win подключать модуль egl вместо wgl (Instance, Surface, AdapterContext, AdapterContextLock из egl); в src/gles/egl.rs добавить для Windows заглушку модуля wayland_sys (тип egl::wl_egl_window, функция wayland_egl_handle и пустой макрос ffi_dispatch). EGL сам грузит libEGL.dll и на Windows берёт ANGLE через eglGetDisplay(DEFAULT).
- После правки Cargo.toml обнови Cargo.lock одной командой cargo metadata --offline, дальше собирай с --locked.

ШАГ 3. РУСИФИКАЦИЯ (папка l10n, ru_v2.json)
- Каталог интерфейса: assets/locales/ru.json. Возьми мой ru_v2.json и перенеси переводы для совпадающих ключей; новые ключи из en.json переведи в том же стиле.
- Терминология (Компас/SolidWorks): design → документ; Joint → соединение; Sweep → по траектории; Loft → по сечениям; Look At → вид по нормали; Home → исходный вид; Fit → показать всё; Interference → коллизии; Rectangular Pattern → массив по сетке; Render → визуализация; Mesh → сетка; Box → параллелепипед; Press Pull → тянуть/толкать; Hem → подгибка; Thicken → придать толщину. Слово «дизайн» не использовать.
- Помещаемость проверяй скриптами l10n (шрифт assets/fonts/ibm-plex-sans, uharfbuzz): кнопка ленты — до 2 строк по 86 px при 12 pt (перенос только по пробелу и «/»); подпись панели ленты — ширина панели минус ~20 px при 11,5 pt полужирным; подпись поля диалога — до ~125 px при 12,5 pt. Что не влезает — сокращай общепринятыми сокращениями (пов-ть, направл., коэфф., МЦХ, КТЛР) или заменяй синонимом; полный текст остаётся во всплывающей подсказке. Заполнители {name} и т. п. сохранять все.

ШАГ 4. СБОРКА
- Только приложение с ANGLE и CLI: cargo build -Zbuild-std=std,panic_abort --profile win7 --locked -p solidcraft --features angle --target x86_64-win7-windows-gnu (скрипт tools/build_angle.sh), затем отдельно -p solidcraft-cli без features. Готовый solidcraft.exe переименовать в solidcraft-angle.exe (имя solidcraft.exe рядом не класть: ANGLE-сборка вызывает соседний solidcraft.exe для --software и ушла бы в цикл).

ШАГ 5. СОВМЕСТИМОСТЬ С WINDOWS 7 (папки shim и tools)
- Проверь импорты exe (objdump -p): все DLL и функции должны существовать в Win7 SP1. Известные нарушители (крейт windows): GetOverlappedResultEx, PathCchStripPrefix (api-ms-win-core-path-l1-1-0), RoOriginateErrorW (api-ms-win-core-winrt-error-l1-1-0), CoTaskMemFree и CoCreateFreeThreadedMarshaler (combase).
- Собери shim/w7shim.dll (x86_64-w64-mingw32-gcc -O2 -shared -s, .def с реализациями и переадресациями в kernel32/ole32) и прогони tools/patch.py: он переименовывает затронутые дескрипторы импорта в w7shim.dll. Новые функции Win8+, если появятся, добавь в w7shim.c/.def. В конце tools/scan.py не должен находить ничего, кроме w7shim.dll.

ШАГ 6. ANGLE
- libEGL.dll, libGLESv2.dll, d3dcompiler_47.dll из Electron 22.3.27 win32-x64 (последний с поддержкой Win7): https://github.com/electron/electron/releases/download/v22.3.27/electron-v22.3.27-win32-x64.zip, плюс файл LICENSE как ANGLE-ELECTRON-LICENSE.txt. Проверь их импорты на функции Win8+.

ШАГ 7. УСТАНОВЩИК (обязательно с мастером и выбором папки)
- Установщик всегда делать с мастером установки на русском языке: приветствие → окно выбора папки, где виден путь по умолчанию C:\Program Files\SolidCraft и есть кнопка «Изменить…» → «Готово к установке» → ход установки → завершение с галочкой «Запустить SolidCraft» и текстом, в какую папку установлено. Установщик без интерфейса выбора папки (только wixl) не выдавать.
- Инструмент: WiX Toolset 3.14 (wix314-binaries.zip с GitHub wixtoolset/wix3) под Wine в режиме wow64: пакеты wine64 и wine32:i386, новый префикс (wineboot -i, должна появиться папка syswow64), wine-mono 8.1.0 (msi с dl.winehq.org). candle.exe и light.exe 32-битные — запускать как есть, флаги не менять.
- Расширения WixUIExtension.dll и WixUtilExtension.dll скопировать в папку сборки и указывать по имени (путь Linux в -ext WiX принимает за ключ).
- Исходник: installer/solidcraft-win7-angle-wixui.wxs: Language 1049, Codepage 1251, UIRef WixUI_InstallDir со страницей лицензии, пропущенной через Publish (Welcome → InstallDirDlg), WIXUI_INSTALLDIR = INSTALLDIR, при обновлении папка берётся из HKLM\Software\SolidCraft\InstallDir, MediaTemplate CompressionLevel="mszip" (high/LZX в Wine не сжимает).
- Команды: candle.exe -nologo -arch x64 -ext WixUIExtension.dll -ext WixUtilExtension.dll solidcraft.wxs; light.exe -nologo -sval -ext WixUIExtension.dll -ext WixUtilExtension.dll -cultures:ru-ru -out setup.msi solidcraft.wixobj (-sval: проверка ICE под Wine не работает).
- Program Files\SolidCraft, ярлыки «SolidCraft» в Пуске и на рабочем столе, «SolidCraft (безопасный режим)», ассоциации .solidcraft и «Открыть с помощью» для STEP/IGES/3MF/STL, тот же UpgradeCode 6A145FD6-D285-428D-AE84-A69570CDF4DB (новая версия заменяет старую), Version — номер новой версии.
- Проверка: msiexec /i под Wine показывает мастер (в английской Wine кириллица искажена — это нормально, на русской Windows отображается правильно), окно выбора папки содержит C:\Program Files\SolidCraft\; тихая установка /qb кладёт файлы в Program Files\SolidCraft.
- Имя файла: solidcraft-X.Y.Z-win7-x64-d3d11_vN.msi, где N — следующий номер после предыдущей выдачи (не перезаписывать старую версию).

ШАГ 8. ПРОВЕРКА ПЕРЕД ВЫДАЧЕЙ
- Под wine64 (winecfg -v win7) и Xvfb запусти solidcraft-angle.exe: в журнале должны быть «adapter chosen Gl ANGLE … Direct3D11», «frame 2 drawn», «running»; сними снимок экрана, открой образец Sample Plate и убедись, что 3D-вид рисуется.
- Выдай MSI и коротко (до 10 строк) напиши, что изменилось.
