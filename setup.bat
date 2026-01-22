@echo off
echo Setting up Library Management System...
echo.

echo Step 1: Installing dependencies...
pip install -r requirements.txt

echo.
echo Step 2: Initializing database...
python -c "from app import init_db; init_db(); print('Database initialized!')"

echo.
echo Step 3: Adding sample data...
python add_sample_data.py

echo.
echo Setup complete! 
echo.
echo To run the application:
echo python app.py
echo.
echo Then open your browser and go to: http://127.0.0.1:5000
echo.
echo Default admin login:
echo Username: admin
echo Password: admin123
echo.
pause