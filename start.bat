@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   �����ղ� AI ֪ʶ�� - �����ű�
echo ========================================
echo.

cd /d "%~dp0"
echo ��ǰĿ¼: %CD%
echo.

REM ������־Ŀ¼
if not exist "data\logs" mkdir "data\logs"

REM ���Python
echo [1/6] ��� Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Python δ��װ
    echo ��� https://www.python.org/downloads/ ��װ Python 3.10+
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python �汾: %PYTHON_VERSION%
echo.

REM ���Node.js
echo [2/6] ��� Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Node.js δ��װ
    echo ��� https://nodejs.org/ ��װ Node.js 18+
    echo.
    pause
    exit /b 1
)
for /f %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
echo [OK] Node.js �汾: %NODE_VERSION%
echo.

REM ��鲢����������⻷��
echo [3/6] ����˻���...
if not exist "backend\venv\Scripts\activate.bat" (
    echo �������⻷��...
    cd backend
    python -m venv venv >> "..\data\logs\start.log" 2>&1
    if errorlevel 1 (
        echo [FAIL] �������⻷��ʧ��
        echo �鿴��־: data\logs\start.log
        pause
        exit /b 1
    )
    cd ..
)
echo [OK] ���⻷������
echo.

REM ��װ�������
echo [4/6] ��װ�������...
cd backend
call venv\Scripts\activate.bat
pip install -r requirements.txt -q >> "..\data\logs\start.log" 2>&1
if errorlevel 1 (
    echo [WARNING] ����������װ����ʧ�ܣ���������...
)
cd ..
echo [OK] ��������Ѱ�װ
echo.

REM ��鲢��װǰ������
echo [5/6] ���ǰ�˻���...
if not exist "frontend\node_modules" (
    echo ��װǰ������...
    cd frontend
    call npm install >> "..\data\logs\start.log" 2>&1
    if errorlevel 1 (
        echo [FAIL] ǰ��������װʧ��
        echo �鿴��־: data\logs\start.log
        pause
        exit /b 1
    )
    cd ..
)
echo [OK] ǰ�������Ѱ�װ
echo.

REM ����¼̬
echo [6/6] ����¼̬...
if exist "backend\data\douyin_auth.json" (
    echo [OK] ��¼̬�ļ�����
) else (
    echo [WARNING] ��¼̬�ļ�������
    echo ��������: cd backend ^&^& python login_manual.py
    echo.
)
echo.

echo ========================================
echo   ��������...
echo ========================================
echo.

REM ������ˣ�ʹ��cmd /k��ֹ���ڹرգ�
echo ������˷��� (�˿� 8000)...
start "Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && python run_server.py"

REM �ȴ��������
echo �ȴ��������...
timeout /t 5 /nobreak >nul

REM ����ǰ�ˣ�ʹ��cmd /k��ֹ���ڹرգ�
echo ����ǰ�˷��� (�˿� 5173)...
start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

REM �ȴ�ǰ������
echo �ȴ�ǰ������...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   ������������
echo ========================================
echo.
echo   ��˵�ַ: http://localhost:8000
echo   ǰ�˵�ַ: http://localhost:5173
echo   API�ĵ�:  http://localhost:8000/docs
echo.
echo   ����� http://localhost:5173 ʹ��
echo.
echo   ��Ҫ�رձ����ڣ�
echo ========================================
echo.

REM �������
start "" "http://localhost:5173"

REM ���ִ��ڴ�

pause >nul