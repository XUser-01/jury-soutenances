@echo off
echo Lancement de l'application Jury Soutenances...
cd /d %~dp0
start "" http://127.0.0.1:8000
python manage.py runserver
