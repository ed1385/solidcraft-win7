SolidCraft 0.18.2 - сборка для Windows 7 SP1 x64, графика ANGLE (Direct3D 11)
==========================================================================

Состав (C:\Program Files\SolidCraft):
- solidcraft-angle.exe - программа; рисует через ANGLE: OpenGL ES 3.0 поверх Direct3D 11
  (аппаратное ускорение на Intel HD 2500 и любой видеокарте с Direct3D 11).
- libEGL.dll, libGLESv2.dll, d3dcompiler_47.dll - ANGLE из Electron 22 (лицензия BSD).
- w7shim.dll - функции Windows 8+, реализованные для Windows 7. Обязателен.
- solidcraft-cli.exe - командная строка и мост для чата с агентом.

Журнал запуска: %LOCALAPPDATA%\SolidCraft\solidcraft-log.txt
Ключи: --safe-mode (настройки по умолчанию), --custom-frame (своя рамка окна SolidCraft).
Интерфейс: русский каталог в инженерной терминологии, включается на русской Windows сам.
Удаление: Панель управления - Программы и компоненты.
