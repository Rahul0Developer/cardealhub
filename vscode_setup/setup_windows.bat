@echo off
echo Setting up Car Deal Hub on Windows...

echo.
echo 1. Creating virtual environment...
python -m venv venv

echo.
echo 2. Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo 3. Installing dependencies...
pip install -r requirements.txt

echo.
echo 4. Setting up VS Code configuration...
if not exist .vscode mkdir .vscode
copy vscode_setup\settings.json .vscode\settings.json
copy vscode_setup\launch.json .vscode\launch.json

echo.
echo 5. Creating .env file from example...
copy vscode_setup\.env.example .env

echo.
echo Setup complete! Please update the .env file with your database credentials and secrets.
echo.
echo To start the application, run:
echo   python main.py
echo.
echo Or use the VS Code Run and Debug feature with the "Python: Flask" configuration.
echo.
pause