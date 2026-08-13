@echo off
echo Creating Python virtual environment...
python -m venv venv

echo Installing backend requirements...
call venv\Scripts\activate
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt

echo Installing frontend packages...
cd frontend
npm install
cd ..

echo Creating .env files...
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env

echo Setup complete!
