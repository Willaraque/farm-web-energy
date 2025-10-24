@echo off
setlocal

REM === CONFIGURACIÓN ===
set RAMA_PRINCIPAL=main
set NUEVA_RAMA=test

echo Cambiando a la rama principal '%RAMA_PRINCIPAL%'...
git checkout %RAMA_PRINCIPAL%
git pull origin %RAMA_PRINCIPAL%

echo Creando nueva rama '%NUEVA_RAMA%' desde '%RAMA_PRINCIPAL%'...
git checkout -b %NUEVA_RAMA%
git push -u origin %NUEVA_RAMA%

echo ✅ Rama '%NUEVA_RAMA%' creada correctamente desde '%RAMA_PRINCIPAL%' y subida al remoto.

endlocal
pause