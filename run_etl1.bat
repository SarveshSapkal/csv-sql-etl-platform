@echo off

echo ===========================
echo      ETL PROCESS START
echo ===========================

cd /d "C:\Users\Sarvesh\Excel_SQL_Importer"

call venv\Scripts\activate.bat

python etl_pipeline.py

echo.
echo ==========================
echo ETL PROCESS FINISHED
echo ==========================

pause