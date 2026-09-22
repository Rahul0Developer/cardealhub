# Car Deal Hub - Setup Guide for VS Code on Windows

This guide will walk you through setting up and running the Car Deal Hub project in Visual Studio Code on Windows.

## Prerequisites

Before starting, make sure you have the following installed on your Windows machine:

1. **Python 3.10+**: Download from [python.org](https://www.python.org/downloads/)
2. **PostgreSQL 14+**: Download from [postgresql.org](https://www.postgresql.org/download/windows/)
3. **Git**: Download from [git-scm.com](https://git-scm.com/download/win)
4. **Visual Studio Code**: Download from [code.visualstudio.com](https://code.visualstudio.com/download)

## Step 1: Clone the Repository

1. Open Command Prompt or PowerShell
2. Navigate to the directory where you want to store the project
3. Clone the repository:
   ```
   git clone https://github.com/yourusername/car-deal-hub.git
   cd car-deal-hub
   ```

## Step 2: Set Up Virtual Environment

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   ```
   venv\Scripts\activate
   ```

3. Your command prompt should now show `(venv)` indicating the environment is active

## Step 3: Install Dependencies

Install all required packages:

```
pip install -r requirements.txt
```

If the requirements.txt file doesn't exist, create it with these dependencies:

```
flask
flask-login
flask-sqlalchemy
flask-wtf
email-validator
gunicorn
numpy
pandas
psycopg2-binary
scikit-learn
sendgrid
werkzeug
xgboost
```

Then run the install command above.

## Step 4: Set Up PostgreSQL Database

1. During PostgreSQL installation, note your password and default port (usually 5432)
2. Open pgAdmin (installed with PostgreSQL)
3. Create a new database named `cardealhub`
4. Create a new `.env` file in your project root with the following:
   ```
   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/cardealhub
   SESSION_SECRET=your_secure_random_string
   SENDGRID_API_KEY=your_sendgrid_api_key
   ```
   
   Replace `yourpassword` with your PostgreSQL password and generate a secure random string for `SESSION_SECRET`.

## Step 5: Initialize Database

1. With your virtual environment activated, run:
   ```
   python db_migrate.py
   ```

2. Seed the database with sample data (optional):
   ```
   python seed_cars.py
   ```

## Step 6: Configure VS Code

1. Open the project folder in VS Code:
   ```
   code .
   ```

2. Install recommended VS Code extensions:
   - Python (Microsoft)
   - SQLTools (MTX Software)
   - SQLTools PostgreSQL/Redshift Driver
   - Pylance
   - Git Lens

3. Select the Python interpreter from your virtual environment:
   - Press `Ctrl+Shift+P`
   - Type "Python: Select Interpreter"
   - Choose the interpreter from your virtual environment (should have "venv" in the path)

## Step 7: Run the Application

1. In the VS Code terminal (ensure your virtual environment is active), run:
   ```
   python main.py
   ```

2. Alternatively, create a `launch.json` configuration in VS Code:
   - Go to the Run and Debug view (Ctrl+Shift+D)
   - Click "create a launch.json file"
   - Select "Python"
   - Configure it as follows:
     ```json
     {
         "version": "0.2.0",
         "configurations": [
             {
                 "name": "Python: Flask",
                 "type": "python",
                 "request": "launch",
                 "module": "flask",
                 "env": {
                     "FLASK_APP": "main.py",
                     "FLASK_DEBUG": "1"
                 },
                 "args": [
                     "run",
                     "--host=0.0.0.0",
                     "--port=5000"
                 ],
                 "jinja": true,
                 "justMyCode": true
             }
         ]
     }
     ```
   - Now you can start the application by clicking the green play button in the Debug panel

3. Open your browser and navigate to http://localhost:5000

## Common Issues and Troubleshooting

### Database Connection Issues

If you encounter database connection errors:
1. Verify your PostgreSQL service is running
2. Check your DATABASE_URL in the .env file
3. Ensure the postgres user has proper permissions

### Module Import Errors

If you see module import errors:
1. Make sure your virtual environment is activated
2. Reinstall the dependencies: `pip install -r requirements.txt`
3. Check for any missing packages and install them individually

### File Permission Issues

If you encounter permission errors when accessing files:
1. Run VS Code as administrator
2. Check file permissions in your project directory

## Additional Resources

- Flask Documentation: https://flask.palletsprojects.com/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- SendGrid Documentation: https://docs.sendgrid.com/

## Setting Up for Production

For production deployment, consider:
1. Using a production WSGI server like Gunicorn
2. Setting DEBUG=False in production
3. Using environment variables for sensitive configuration
4. Implementing proper SSL/TLS for security