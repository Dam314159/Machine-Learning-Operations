@echo off
title Reset IT3385 MLflow
setlocal

cd /d "%~dp0"

echo ===========================================================
echo                 Reset IT3385 MLflow
echo ===========================================================
echo.
echo WARNING:
echo This will permanently delete all MLflow experiments,
echo runs, metrics, parameters and artifacts.
echo.
choice /C YN /M "Continue"

if errorlevel 2 (
    echo Reset cancelled.
    exit /b 0
)

echo.
echo Checking whether MLflow files can be removed...

if exist "mlflow.db" (
    del /f /q "mlflow.db"

    if exist "mlflow.db" (
        echo.
        echo ERROR: mlflow.db could not be deleted.
        echo Stop the MLflow server, then run this file again.
        echo.
        pause
        exit /b 1
    )
)

if exist "mlruns" (
    rmdir /s /q "mlruns"

    if exist "mlruns" (
        echo.
        echo ERROR: The mlruns folder could not be deleted.
        echo Close programs that may be using it and try again.
        echo.
        pause
        exit /b 1
    )
)

mkdir "mlruns"

echo.
echo ===========================================================
echo                 MLFLOW RESET COMPLETED
echo ===========================================================
echo.
echo A new empty mlruns folder has been created.
echo Start the MLflow server again when ready.
echo.
pause
exit /b 0