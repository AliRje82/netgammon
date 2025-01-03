@echo off
REM Check if the correct number of arguments are provided

REM Run the server.go file with the arguments
set ARG1="localhost:8000"
set ARG2="localhost:8001"
set ARG3="localhost:8002"
set SERVER="localhost:9000"
start cmd /k "go run .\Onionrouting\routers\router.go %ARG1% %ARG2%"
start cmd /k "go run .\Onionrouting\routers\router.go %ARG2% %ARG3%"
start cmd /k "go run .\Onionrouting\routers\router.go %ARG3% %SERVER%"
start cmd /k "go run .\Onionrouting\server.go %SERVER%"

REM Check the exit code of the Go program
if errorlevel 1 (
    echo Failed to run server.go
    exit /b %errorlevel%
)

echo server.go executed successfully
