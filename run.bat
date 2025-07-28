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

:: Start the FastAPI server in a new window
echo %GREEN%Starting FastAPI server on http://localhost:5000%NC%
start "CV Quality Scanner Backend" cmd /c "python main.py"

:: Go back to the root directory
cd ..

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
echo %GREEN%   Backend: http://localhost:5000%NC%
echo %GREEN%   Frontend: http://localhost:5173%NC%
echo %GREEN%   Close the server windows to stop%NC%
echo %GREEN%=================================%NC%

:: Keep the main window open
echo Press any key to exit this window (servers will continue running in their own windows)
pause > nul