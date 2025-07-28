@echo off
setlocal enabledelayedexpansion

:: CV Quality Scanner - Docker Run Script for Windows
:: This script starts both the FastAPI backend and React frontend using Docker

:: Define colors for output
set "GREEN=[92m"
set "YELLOW=[93m"
set "NC=[0m"

:: Print banner
echo %GREEN%=========================================%NC%
echo %GREEN%   CV Quality Scanner Docker Startup    %NC%
echo %GREEN%=========================================%NC%

:: Check for Docker
where docker >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %YELLOW%Docker is not installed. Please install Docker to continue.%NC%
    exit /b 1
)

echo %GREEN%Using Docker as container engine%NC%

:: Check for docker-compose
where docker-compose >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %YELLOW%docker-compose not found. Checking if Docker Desktop includes Compose V2...%NC%
    
    :: Check for Docker Compose V2
    docker compose version >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo %YELLOW%Docker Compose not found. Please install Docker Compose to continue.%NC%
        exit /b 1
    ) else (
        echo %GREEN%Using Docker Compose V2%NC%
        set "COMPOSE_CMD=docker compose"
    )
) else (
    echo %GREEN%Using docker-compose%NC%
    set "COMPOSE_CMD=docker-compose"
)

:: Check if .env file exists for GROQ_API_KEY
if not exist "py_backend_logic\.env" (
    echo %YELLOW%.env file not found in py_backend_logic directory.%NC%
    
    :: Check if .env.example exists
    if exist "py_backend_logic\.env.example" (
        echo %YELLOW%Creating .env file from .env.example%NC%
        copy py_backend_logic\.env.example py_backend_logic\.env
        echo %YELLOW%Please edit py_backend_logic\.env to set your GROQ_API_KEY%NC%
    ) else (
        echo %YELLOW%Creating empty .env file%NC%
        echo GROQ_API_KEY= > py_backend_logic\.env
        echo %YELLOW%Please edit py_backend_logic\.env to set your GROQ_API_KEY%NC%
    )
    
    :: Give user a chance to edit the file
    echo Press Enter to continue after editing the .env file...
    pause > nul
)

:: Start the containers
echo %GREEN%Building and starting containers...%NC%
%COMPOSE_CMD% up --build -d

echo %GREEN%=========================================%NC%
echo %GREEN%   Containers are now running!          %NC%
echo %GREEN%   Backend: http://localhost:5000       %NC%
echo %GREEN%   Frontend: http://localhost:80        %NC%
echo %GREEN%=========================================%NC%
echo %GREEN%To stop the containers, run:            %NC%
echo %GREEN%   %COMPOSE_CMD% down                   %NC%
echo %GREEN%=========================================%NC%

:: Keep the window open
echo Press any key to exit this window (containers will continue running)
pause > nul