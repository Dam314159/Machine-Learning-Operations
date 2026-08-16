@echo off
setlocal EnableExtensions

rem -------------------------------------------------
rem Resolve locations relative to this batch file
rem -------------------------------------------------
set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

set "ENV_DIR=%ROOT_DIR%\env"
set "NOTEBOOK_DIR=%ROOT_DIR%\notebooks"

rem -------------------------------------------------
rem Validate portable environment
rem -------------------------------------------------
if not exist "%ENV_DIR%\python.exe" (
    echo.
    echo ERROR: Portable Python was not found:
    echo %ENV_DIR%\python.exe
    echo.
    pause
    exit /b 1
)

if not exist "%NOTEBOOK_DIR%" (
    mkdir "%NOTEBOOK_DIR%"
)

set "COMSPEC=%SystemRoot%\System32\cmd.exe"
set "SHELL=%SystemRoot%\System32\cmd.exe"

rem -------------------------------------------------
rem Prevent system Python and Anaconda contamination
rem -------------------------------------------------
set "PYTHONNOUSERSITE=1"
set "PYTHONPATH="
set "PYTHONHOME="
set "JUPYTER_PATH=%ENV_DIR%\share\jupyter"
set "JUPYTER_CONFIG_DIR=%ROOT_DIR%\.jupyter"
set "JUPYTER_DATA_DIR=%ROOT_DIR%\.jupyter-data"
set "JUPYTER_RUNTIME_DIR=%ROOT_DIR%\.jupyter-runtime"
set "IPYTHONDIR=%ROOT_DIR%\.ipython"

set "PATH=%ENV_DIR%;%ENV_DIR%\Scripts;%ENV_DIR%\Library\bin;%ENV_DIR%\Library\usr\bin;%ENV_DIR%\Library\mingw-w64\bin;%SystemRoot%\System32;%SystemRoot%"

if not exist "%JUPYTER_CONFIG_DIR%" mkdir "%JUPYTER_CONFIG_DIR%"
if not exist "%JUPYTER_DATA_DIR%" mkdir "%JUPYTER_DATA_DIR%"
if not exist "%JUPYTER_RUNTIME_DIR%" mkdir "%JUPYTER_RUNTIME_DIR%"
if not exist "%IPYTHONDIR%" mkdir "%IPYTHONDIR%"

cd /d "%ROOT_DIR%"

echo ===============================================
echo IT3385 Portable JupyterLab
echo ===============================================
echo Python:
"%ENV_DIR%\python.exe" --version

echo.
echo Python executable:
"%ENV_DIR%\python.exe" -c "import sys; print(sys.executable)"

echo.
echo Testing required kernel packages...
"%ENV_DIR%\python.exe" -c "import ssl, zmq, ipykernel, jupyterlab; print('Environment check passed')" || goto :failed

echo.
echo Starting JupyterLab...
"%ENV_DIR%\python.exe" -m jupyterlab ^
  --notebook-dir="%NOTEBOOK_DIR%" ^
  --ServerApp.use_redirect_file=False

goto :end

:failed
echo.
echo ERROR: The portable environment verification failed.
echo Run Verify_Environment.bat and check the messages.
pause
exit /b 1

:end
endlocal