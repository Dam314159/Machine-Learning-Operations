@echo off
title IT3385 MLflow Tracking Server

cd /d "%~dp0"

echo ==========================================
echo Starting MLflow Tracking Server
echo ==========================================
echo.

env\python.exe -m mlflow ui ^
    --backend-store-uri "file:///%CD%/mlruns" ^
    --host 127.0.0.1 ^
    --port 5000

pause