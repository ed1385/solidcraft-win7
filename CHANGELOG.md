# Изменения

## 0.18.2-win7.8 — 2026-10-21

Первая публичная сборка. Исходники: SolidCraft [v0.18.2](https://github.com/tangency-labs/solidcraft/releases/tag/v0.18.2), коммит 4927214976ff20758fde35af03bd6b2d6cf73e18.

- Цель x86_64-win7-windows-gnu, статический CRT: дополнительные библиотеки Visual C++ не нужны.
- w7shim.dll: GetOverlappedResultEx, PathCchStripPrefix, RoOriginateErrorW, CoTaskMemFree, CoCreateFreeThreadedMarshaler для Windows 7; GetDpiForWindow / GetSystemMetricsForDpi — поиск во время работы.
- Графика через ANGLE (OpenGL ES 3.0 на Direct3D 11): аппаратное ускорение на Intel HD 2000–4000 и других видеокартах без Vulkan и OpenGL 4.3.
- Стандартная рамка окна Windows; журнал запуска в %LOCALAPPDATA%\SolidCraft\solidcraft-log.txt.
- Русский интерфейс в инженерной терминологии, проверка помещаемости надписей; лента и диалоги расширены под русский текст.
- Установщик MSI с мастером на русском языке и выбором папки (по умолчанию C:\Program Files\SolidCraft).
