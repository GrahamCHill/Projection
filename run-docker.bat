@echo off
setlocal enabledelayedexpansion

:: Projection - Docker Run Script for Windows
:: This script starts the application using Docker Compose

:: Define colors for output
set "GREEN=[92m"
set "YELLOW=[93m"
set "NC=[0m"

:: Print banner
echo %GREEN%=================================%NC%
echo %GREEN%        Projection Docker        %NC%
echo %GREEN%=================================%NC%

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

:: Check for GitHub token
if "%GITHUB_TOKEN%"=="" (
    echo %YELLOW%No GitHub token found in environment. GitHub operations may be limited.%NC%
    echo %YELLOW%Set the GITHUB_TOKEN environment variable for full GitHub functionality.%NC%
) else (
    echo %GREEN%GitHub token found in environment. GitHub operations will be available.%NC%
)

:: Start the Docker containers
echo %GREEN%Starting Docker containers...%NC%
docker-compose up -d

:: Show container status
echo %GREEN%Container status:%NC%
docker-compose ps

echo %GREEN%=================================%NC%
echo %GREEN%   Servers are now running!      %NC%
echo %GREEN%   Backend: http://localhost:8000%NC%
echo %GREEN%   Git LFS: http://localhost:8001%NC%
echo %GREEN%   Frontend: http://localhost:80 %NC%
echo %GREEN%=================================%NC%
echo %GREEN%To stop the containers, run:     %NC%
echo %GREEN%   docker-compose down           %NC%
echo %GREEN%=================================%NC%

:: Keep the window open
pause