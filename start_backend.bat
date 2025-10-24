@echo off
REM Activa el entorno virtual de Python.
CALL .\venv\Scripts\activate.bat

REM Ejecuta las migraciones de la base de datos.
echo "Ejecutando migraciones..."
python manage.py migrate

REM Inicia el servidor de desarrollo de Django.
echo "Iniciando el servidor de desarrollo en http://127.0.0.1:8000/"
python manage.py runserver
