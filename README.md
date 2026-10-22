<h1 align="center">SolidCraft для Windows 7</h1>

<p align="center">
  <b>Неофициальная сборка параметрической 3D CAD <a href="https://github.com/tangency-labs/solidcraft">SolidCraft</a> для Windows 7 SP1 x64</b><br>
  с аппаратным ускорением через Direct3D 11 (ANGLE) и инженерной русификацией интерфейса
</p>

<p align="center">
  <a href="../../releases/latest"><img src="https://img.shields.io/github/v/release/ed1385/solidcraft-win7?label=%D1%80%D0%B5%D0%BB%D0%B8%D0%B7" alt="Релиз"></a>
  <img src="https://img.shields.io/badge/Windows-7%20SP1%20x64-0078D6" alt="Windows 7 SP1 x64">
  <img src="https://img.shields.io/badge/%D0%B3%D1%80%D0%B0%D1%84%D0%B8%D0%BA%D0%B0-Direct3D%2011%20(ANGLE)-555" alt="Direct3D 11">
  <a href="LICENSE-MIT"><img src="https://img.shields.io/badge/license-MIT%20%2F%20Apache--2.0-blue" alt="Лицензия"></a>
</p>

---

## Что это

**SolidCraft** — открытая параметрическая 3D CAD на Rust (эскизы, твёрдые тела, поверхности, листовой металл, сборки, экспорт STEP/STL/3MF). Её разрабатывает проект [tangency-labs/solidcraft](https://github.com/tangency-labs/solidcraft); официальные сборки выходят только для Windows 10/11, macOS и Linux.

**Этот репозиторий** — сборочный форк SolidCraft под **Windows 7 SP1 x64**: исходники берутся у автора, функциональность CAD не меняется, а здесь хранятся патчи совместимости с Windows 7, скрипты сборки и **готовые установщики** в [Releases](../../releases). Каждый релиз здесь соответствует версии официального проекта.

### Какую задачу решает

Официальный SolidCraft на Windows 7 не запускается вообще, а после переноса упирается в графику:

| Проблема на Windows 7 | Решение в этой сборке |
|---|---|
| Rust с версии 1.78 не собирает программы под Windows 7 | Сборка под цель **x86_64-win7-windows-gnu** со стандартной библиотекой из исходников |
| exe вызывает функции Windows 8/10 (GetDpiForWindow, PathCchStripPrefix, RoOriginateErrorW, GetOverlappedResultEx, combase) | Функции DPI ищутся во время работы; остальные даёт библиотека **w7shim.dll** |
| Нет Direct3D 12 и Vulkan, а OpenGL старых видеокарт (Intel HD 2000–4000: OpenGL 4.0) даёт чёрное окно | Рисование через **ANGLE**: OpenGL ES 3.0 поверх **Direct3D 11** — есть на любой видеокарте с драйвером для Win7 |
| Собственная рамка окна не отрисовывается | Стандартная рамка Windows (своя — ключ --custom-frame) |
| Буквальный русский перевод, надписи обрезаются на ленте | Перевод в терминологии Компас/SolidWorks, сокращения, проверка помещаемости по шрифту интерфейса |

Сборка проверена на: Windows 7 Профессиональная SP1 x64, Intel Core i5-3450, встроенная графика **Intel HD Graphics 2500** (драйвер 9.17.10.4229).

## Скачать и установить

1. Откройте [**последний релиз**](../../releases/latest) и скачайте файл **solidcraft-…-win7-x64-d3d11_vN.msi**.
2. Запустите его двойным щелчком: откроется мастер установки на русском языке.
3. На шаге выбора папки виден путь по умолчанию **C:\Program Files\SolidCraft** — его можно изменить.
4. После установки: ярлык **SolidCraft** в меню «Пуск» и на рабочем столе. Файлы .solidcraft открываются двойным щелчком, STEP/IGES/3MF/STL — через «Открыть с помощью».

Удаление: «Панель управления» → «Программы и компоненты». Новая версия ставится поверх старой в ту же папку.

### Требования

- Windows 7 SP1 x64 (подойдут и Windows 8.1/10/11, но для них лучше официальная сборка);
- видеокарта с драйвером Direct3D 11 (Intel HD 2000 и новее, NVIDIA GeForce 400+, AMD Radeon HD 5000+);
- Visual C++ Redistributable и .NET **не нужны**.

### Проверка видеокарты

[gpu-test.cmd](gpu-test.cmd) — командный файл, который показывает видеоадаптер, версию драйвера, наличие Direct3D 11/12, OpenGL, Vulkan, OpenCL и что из этого видит SolidCraft. Результат — gpu-report.txt рядом с файлом.

### Если что-то не так

- Журнал запуска: **%LOCALAPPDATA%\SolidCraft\solidcraft-log.txt** (строки adapter chosen … Direct3D11, frame 2 drawn, running).
- Ярлык **SolidCraft (безопасный режим)** запускает программу с настройками по умолчанию.
- Сообщения об ошибках самой CAD — в [официальный проект](https://github.com/tangency-labs/solidcraft/issues); об ошибках установки и работы на Windows 7 — сюда, в [Issues](../../issues).

## Состав установки

| Файл | Назначение |
|---|---|
| solidcraft-angle.exe | SolidCraft, графика через ANGLE (Direct3D 11) |
| libEGL.dll, libGLESv2.dll, d3dcompiler_47.dll | ANGLE из Electron 22.3.27 (последняя ветка Chromium с поддержкой Windows 7) |
| w7shim.dll | функции Windows 8+, реализованные для Windows 7 (исходник: [shim/](shim)) |
| solidcraft-cli.exe | командная строка SolidCraft и мост для чата с агентом |

## Сборка из исходников

Кратко: Linux (Ubuntu 24.04) → Rust stable с rust-src → mingw-w64 → патчи из [patches/](patches) → цель x86_64-win7-windows-gnu → w7shim → ANGLE → MSI через WiX 3.14 под Wine.

```
tools/build_win7.sh  /путь/к/solidcraft-X.Y.Z     # компиляция и подготовка файлов в out/s7
tools/make_installer.sh  solidcraft-X.Y.Z-win7-x64-d3d11_v1.msi
```

Подробно, со всеми подводными камнями: [**BUILD.md**](BUILD.md). Готовый промт для сборки новой версии с помощью ИИ-ассистента: [docs/AI-BUILD-PROMPT.md](docs/AI-BUILD-PROMPT.md).

## Структура репозитория

```
patches/      правки исходников SolidCraft и wgpu-hal (EGL/ANGLE на Windows)
shim/         w7shim.dll — функции Windows 8+ для Windows 7
tools/        сборка, проверка и правка импортов exe, сборка MSI
installer/    исходник установщика WiX (мастер на русском, выбор папки)
locales/      русский каталог интерфейса ru.json
l10n/         скрипты перевода и проверки помещаемости надписей
docs/         промт для сборки новых версий
gpu-test.cmd  тест видеокарты и графических драйверов
```

## Лицензия

SolidCraft © SolidCraft contributors, лицензии MIT или Apache 2.0 на выбор. Патчи, скрипты и перевод в этом репозитории распространяются на тех же условиях: [LICENSE-MIT](LICENSE-MIT), [LICENSE-APACHE](LICENSE-APACHE), [NOTICE](NOTICE). ANGLE — лицензия BSD (Google / The ANGLE Project Authors), поставляется в составе релиза.

Это неофициальная сборка; проект не связан с авторами SolidCraft и не поддерживается ими.

---

<details>
<summary><b>English</b></summary>

**Unofficial Windows 7 SP1 x64 build of [SolidCraft](https://github.com/tangency-labs/solidcraft)**, the open-source parametric 3D CAD written in Rust. Upstream ships Windows 10/11, macOS and Linux builds only. This is a build fork: CAD features are unchanged; the repository holds the Windows 7 compatibility patches, build scripts and the compiled installers, one release per upstream version.

Key changes: x86_64-win7-windows-gnu target with build-std; Windows 8+ API imports replaced by runtime lookups and a small w7shim.dll; rendering through ANGLE (OpenGL ES 3.0 on Direct3D 11) via a patched wgpu-hal EGL path, because Windows 7 has no D3D12/Vulkan and old OpenGL 4.0 drivers render black; native window frame; Russian UI catalog using standard CAD terminology. Download the MSI from [Releases](../../releases/latest); build steps are in [BUILD.md](BUILD.md).

</details>
