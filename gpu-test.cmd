@echo off
rem ======================================================================
rem  gpu-test.cmd - тест графического ускорителя и драйверов (Windows 7+)
rem  Положите рядом с solidcraft.exe (или SolidCraft установлен в Program Files).
rem  Результат: gpu-report.txt рядом с этим файлом.
rem ======================================================================
setlocal EnableExtensions EnableDelayedExpansion
set "R=%~dp0gpu-report.txt"
set "DX=%TEMP%\sc_dxdiag.txt"
set "LOG=%LOCALAPPDATA%\SolidCraft\solidcraft-log.txt"
set "EXE="
if exist "%~dp0solidcraft.exe" set "EXE=%~dp0solidcraft.exe"
if not defined EXE if exist "%ProgramFiles%\SolidCraft\solidcraft.exe" set "EXE=%ProgramFiles%\SolidCraft\solidcraft.exe"

echo Тест графики запущен. Это займёт около 1 минуты...
call :main > "%R%" 2>&1
echo.
type "%R%"
echo.
echo Отчёт сохранён: %R%
pause
exit /b

:main
echo ===================== ТЕСТ ГРАФИКИ =====================
echo Дата: %date% %time%
ver
echo Разрядность ОС: %PROCESSOR_ARCHITECTURE%
echo.
echo ===== 1. Видеоадаптеры (WMI) =====
wmic path Win32_VideoController get Name,VideoProcessor,DriverVersion,DriverDate,AdapterRAM,Status /value | more
echo.

echo ===== 2. Системные библиотеки графических API =====
for %%F in (d3d9.dll d3d10.dll d3d11.dll d3d12.dll dxgi.dll opengl32.dll vulkan-1.dll OpenCL.dll) do (
  if exist "%SystemRoot%\System32\%%F" (echo   [есть] %%F) else (echo   [нет ] %%F)
)
echo.

echo ===== 3. DirectX (dxdiag) =====
echo   сбор отчёта dxdiag... >con
if exist "%DX%" del /q "%DX%"
start "" /wait dxdiag /whql:off /t "%DX%"
set /a n=0
:waitdx
if exist "%DX%" goto dxready
set /a n+=1
if !n! gtr 60 goto dxnone
ping -n 2 127.0.0.1 >nul
goto waitdx
:dxready
ping -n 3 127.0.0.1 >nul
findstr /i /c:"Operating System" /c:"DirectX Version" /c:"Card name" /c:"Chip type" /c:"Display Memory" /c:"Driver Version" /c:"Driver Date" /c:"DDI Version" /c:"Feature Levels" /c:"Direct3D Acceleration" "%DX%"
goto dxdone
:dxnone
echo   dxdiag не ответил за 60 с
:dxdone
echo.

echo ===== 4. OpenGL: драйвер видеокарты (ICD) =====
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\OpenGLDrivers" /s 2>nul
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}" /s /v OpenGLDriverName 2>nul | findstr /i "OpenGLDriverName"
if errorlevel 1 echo   ICD OpenGL в реестре не найден: есть только программный OpenGL 1.1 Microsoft
echo.

echo ===== 5. Vulkan =====
set "VK=0"
reg query "HKLM\SOFTWARE\Khronos\Vulkan\Drivers" 2>nul && set "VK=1"
if "!VK!"=="0" echo   драйверов Vulkan в системе нет
where vulkaninfo >nul 2>&1 && vulkaninfo 2>nul | findstr /i /c:"apiVersion" /c:"deviceName" /c:"driverVersion"
echo.

echo ===== 6. OpenCL =====
reg query "HKLM\SOFTWARE\Khronos\OpenCL\Vendors" 2>nul || echo   драйверов OpenCL нет
echo.

echo ===== 7. Проверка через SolidCraft (wgpu: D3D12 / Vulkan / OpenGL) =====
set "GLV="
if not defined EXE (
  echo   solidcraft.exe не найден - пункт пропущен
  goto verdict
)
echo   запуск SolidCraft на драйвере видеокарты, 25 с... >con
start "" "%EXE%" --hardware-gl
ping -n 26 127.0.0.1 >nul
taskkill /im solidcraft.exe /f >nul 2>&1
ping -n 3 127.0.0.1 >nul
if not exist "%LOG%" (
  echo   журнал SolidCraft не создан
  goto verdict
)
findstr /c:"adapters:" /c:"adapter chosen" /c:"graphics:" /c:"frame 2 drawn" "%LOG%"
for /f "tokens=2 delims=," %%a in ('findstr /c:"adapter chosen Gl" "%LOG%"') do set "DRV=%%a"
if defined DRV for /f "tokens=2" %%v in ("!DRV!") do set "GLV=%%v"
echo.

:verdict
echo ===================== ИТОГ =====================
set "HW=0"
if exist "%SystemRoot%\System32\d3d12.dll" (echo   D3D12 ........ есть & set "HW=1") else (echo   D3D12 ........ нет - в Windows 7 его нет)
if "!VK!"=="1" (echo   Vulkan ....... есть & set "HW=1") else (echo   Vulkan ....... нет)
if defined GLV (
  for /f "tokens=1,2 delims=." %%m in ("!GLV!") do (set "MAJ=%%m" & set "MIN=%%n")
  echo   OpenGL ....... !GLV! - драйвер видеокарты
  set "GLOK=0"
  if !MAJ! gtr 4 set "GLOK=1"
  if !MAJ! equ 4 if !MIN! geq 3 set "GLOK=1"
  if "!GLOK!"=="1" (set "HW=1") else (echo                  ниже 4.3 - для SolidCraft недостаточно)
) else (
  echo   OpenGL ....... версия не определена
)
echo.
if "!HW!"=="1" (
  echo   ВЫВОД: аппаратное ускорение для SolidCraft ДОСТУПНО.
) else (
  echo   ВЫВОД: аппаратного ускорения для SolidCraft НЕТ.
  echo   Нужен D3D12 ^(Windows 10+^), Vulkan или OpenGL 4.3+.
  echo   SolidCraft работает на программной графике Mesa ^(процессор^).
)
exit /b
