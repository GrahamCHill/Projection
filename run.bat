@echo off
setlocal enabledelayedexpansion

:: CV Quality Scanner - Run Script for Windows
:: This script starts both the FastAPI backend and React frontend

:: Define colors for output
set "GREEN=[92m"
set "YELLOW=[93m"
set "NC=[0m"

:: Print banner
echo %GREEN%=================================%NC%
echo %GREEN%   CV Quality Scanner Startup   %NC%
echo %GREEN%=================================%NC%

:: Check for required commands
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %YELLOW%Node.js is not installed. Please install Node.js to run the frontend.%NC%
    exit /b 1
)

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %YELLOW%Python is not installed. Please install Python to run the backend.%NC%
    exit /b 1
)

where go >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %YELLOW%Go is not installed. Please install Go to run the Git LFS backend.%NC%
    echo %YELLOW%Git LFS functionality will not be available.%NC%
    set GO_AVAILABLE=false
) else (
    set GO_AVAILABLE=true
)

:: Start the backend server
echo %GREEN%Starting FastAPI backend server...%NC%
cd py_backend_logic

:: Check if virtual environment exists, if not create it
if not exist .venv (
    echo %YELLOW%Creating Python virtual environment...%NC%
    python -m venv .venv
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Install dependencies if needed
echo %GREEN%Installing/updating Python dependencies...%NC%
pip install -r requirements.txt

:: Check for MinIO client (for S3 storage)
where mc >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo %GREEN%MinIO client found. S3 storage will be available.%NC%
) else (
    echo %YELLOW%MinIO client not found. S3 storage features may not work properly.%NC%
    echo %YELLOW%Install MinIO client for full S3 functionality: https://min.io/docs/minio/windows/reference/minio-mc.html%NC%
)

:: Check if Qdrant client dependencies are installed
python -c "import qdrant_client" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo %GREEN%Qdrant client found. Vector database will be available.%NC%
) else (
    echo %YELLOW%Qdrant client not found. Vector database features may not work properly.%NC%
    echo %YELLOW%Install Qdrant client for full vector database functionality: pip install qdrant-client%NC%
)

:: Check if GitHub API dependencies are installed
python -c "import requests" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo %GREEN%GitHub API dependencies found. GitHub integration will be available.%NC%
) else (
    echo %YELLOW%GitHub API dependencies not found. GitHub integration may not work properly.%NC%
    echo %YELLOW%Install requests for full GitHub functionality: pip install requests%NC%
)

:: Start the FastAPI server in a new window
echo %GREEN%Starting FastAPI server on http://localhost:8000%NC%
start "CV Quality Scanner Backend" cmd /c "python main.py"

:: Go back to the root directory
cd ..

:: Start the Go backend if available
if "%GO_AVAILABLE%"=="true" (
    echo %GREEN%Starting Go Git LFS backend server...%NC%
    cd go_backend
    
    :: Start the Go server in a new window
    echo %GREEN%Starting Go Git LFS server on http://localhost:8001%NC%
    start "CV Quality Scanner Git LFS Backend" cmd /c "go run main.go"
    
    :: Go back to the root directory
    cd ..
    
    :: Set environment variable for Python backend to connect to Go backend
    set GO_BACKEND_URL=http://localhost:8001
) else (
    echo %YELLOW%Go is not available. Git LFS functionality will be disabled.%NC%
)

:: Start the frontend
echo %GREEN%Starting React frontend...%NC%
cd react_frontend

:: Install dependencies if needed
echo %GREEN%Installing/updating Node.js dependencies...%NC%
call npm install

:: Start the React development server in a new window
echo %GREEN%Starting React development server on http://localhost:5173%NC%
start "CV Quality Scanner Frontend" cmd /c "npm run dev"

:: Go back to the root directory
cd ..

echo %GREEN%=================================%NC%
echo %GREEN%   Servers are now running!      %NC%
echo %GREEN%   Backend: http://localhost:8000%NC%
if "%GO_AVAILABLE%"=="true" (
    echo %GREEN%   Git LFS: http://localhost:8001%NC%
)
echo %GREEN%   Frontend: http://localhost:5173%NC%
echo %GREEN%   Close the server windows to stop%NC%
echo %GREEN%=================================%NC%

:: Keep the main window open
echo Press any key to exit this window (servers will continue running in their own windows)
pause > nul