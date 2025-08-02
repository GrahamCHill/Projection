@echo off
setlocal enabledelayedexpansion

:: Projection - Cross-Platform Docker Run Script for Windows
:: This script detects architecture and starts the application using Docker Compose

:: Define colors for output
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

:: Print banner
echo %GREEN%=====================================%NC%
echo %GREEN%   Projection - Cross-Platform      %NC%
echo %GREEN%=====================================%NC%

:: Check for required commands
where docker >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %YELLOW%Docker is not installed. Please install Docker to run the application.%NC%
    exit /b 1
)

where docker-compose >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %YELLOW%Docker Compose is not installed. Please install Docker Compose to run the application.%NC%
    exit /b 1
)

:: Detect system architecture
echo %BLUE%Detecting system architecture...%NC%
for /f "tokens=1" %%i in ('wmic os get OSArchitecture ^| findstr /r "[0-9]"') do (
    set "ARCH=%%i"
)

:: Set GOARCH based on detected architecture
if "%ARCH%"=="64-bit" (
    set "GOARCH=amd64"
) else if "%ARCH%"=="ARM64" (
    set "GOARCH=arm64"
) else (
    echo %YELLOW%Unrecognized architecture: %ARCH%%NC%
    echo %YELLOW%Defaulting to amd64%NC%
    set "GOARCH=amd64"
)

echo %BLUE%Detected architecture: %ARCH%%NC%
echo %BLUE%Using GOARCH=%GOARCH%%NC%

:: Set environment variable for Docker Compose
set "GOARCH=%GOARCH%"

:: Start the Docker containers with the detected architecture
echo %GREEN%Starting Docker containers...%NC%
docker-compose up -d

:: Show container status
echo %GREEN%Container status:%NC%
docker-compose ps

echo %GREEN%=====================================%NC%
echo %GREEN%   Services started successfully!    %NC%
echo %GREEN%   Frontend: http://localhost        %NC%
echo %GREEN%   Backend API: http://localhost:8000%NC%
echo %GREEN%   Go Backend: http://localhost:8001 %NC%
echo %GREEN%=====================================%NC%
echo %GREEN%To stop the containers, run:         %NC%
echo %GREEN%   docker-compose down               %NC%
echo %GREEN%=====================================%NC%

:: Keep the window open
pause