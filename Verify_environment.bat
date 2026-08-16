@echo off
title IT3385 Environment Verification
setlocal EnableExtensions

echo ===========================================================
echo            IT3385 PyCaret Environment Verification
echo ===========================================================
echo.

REM Resolve paths relative to this batch file
set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

set "ENV_DIR=%ROOT_DIR%\env"
set "PYTHON_EXE=%ENV_DIR%\python.exe"

REM Check that portable Python exists
if not exist "%PYTHON_EXE%" (
    echo ERROR: Portable Python was not found:
    echo %PYTHON_EXE%
    goto :error
)

REM Prevent system Anaconda and user packages from leaking in
set "PYTHONNOUSERSITE=1"
set "PYTHONPATH="
set "PYTHONHOME="

REM Use only the portable environment and Windows system folders
set "PATH=%ENV_DIR%;%ENV_DIR%\Scripts;%ENV_DIR%\Library\bin;%ENV_DIR%\Library\usr\bin;%ENV_DIR%\Library\mingw-w64\bin;%SystemRoot%\System32;%SystemRoot%"

cd /d "%ROOT_DIR%"

echo [1/7] Checking Python...
"%PYTHON_EXE%" --version
if errorlevel 1 goto :error

echo.
echo [2/7] Checking Python executable...
"%PYTHON_EXE%" -c "import sys; print(sys.executable)"
if errorlevel 1 goto :error

echo.
echo [3/7] Checking core packages...
"%PYTHON_EXE%" -c "import pycaret, pandas, sklearn"
if errorlevel 1 goto :error

"%PYTHON_EXE%" -c "import pycaret; print('PyCaret      :', pycaret.__version__)"
"%PYTHON_EXE%" -c "import pandas; print('Pandas       :', pandas.__version__)"
"%PYTHON_EXE%" -c "import sklearn; print('Scikit-Learn :', sklearn.__version__)"

echo.
echo [4/7] Checking optional ML packages...

"%PYTHON_EXE%" -c "import xgboost; print('XGBoost      :', xgboost.__version__)"
if errorlevel 1 echo WARNING: XGBoost not found

"%PYTHON_EXE%" -c "import lightgbm; print('LightGBM     :', lightgbm.__version__)"
if errorlevel 1 echo WARNING: LightGBM not found

"%PYTHON_EXE%" -c "import catboost; print('CatBoost     :', catboost.__version__)"
if errorlevel 1 echo WARNING: CatBoost not found

echo.
echo [4a/7] Checking supporting packages...

"%PYTHON_EXE%" -c "import sktime; print('sktime       :', sktime.__version__)"
if errorlevel 1 goto :error

"%PYTHON_EXE%" -c "import dask; print('Dask         :', dask.__version__)"
if errorlevel 1 goto :error

"%PYTHON_EXE%" -c "import mlflow; print('MLflow       :', mlflow.__version__)"
if errorlevel 1 echo WARNING: MLflow not installed

echo.
echo [5/7] Checking JupyterLab...

REM Test imports needed to start both JupyterLab and a notebook kernel
"%PYTHON_EXE%" -c "import ssl, zmq, tornado, jupyter_client, ipykernel, jupyterlab; print('Jupyter dependencies OK')"
if errorlevel 1 goto :error

REM Call the JupyterLab Python module directly
"%PYTHON_EXE%" -m jupyterlab --version
if errorlevel 1 goto :error

echo.
echo [6/7] Running a simple PyCaret test...

"%PYTHON_EXE%" -c "from pycaret.datasets import get_data; from pycaret.classification import setup; data=get_data('juice', verbose=False); setup(data=data, target='Purchase', html=False, verbose=False, session_id=123); print('PyCaret setup successful')"
if errorlevel 1 goto :error

echo.
echo [7/7] Environment verification completed.
echo.
echo ===========================================================
echo                 ALL CHECKS PASSED
echo ===========================================================
echo.
echo The IT3385 environment is ready for use.
echo.
pause
exit /b 0

:error
echo.
echo ===========================================================
echo                  VERIFICATION FAILED
echo ===========================================================
echo.
echo One or more checks failed.
echo Please inform the lecturer before starting the practical.
echo.
pause
exit /b 1