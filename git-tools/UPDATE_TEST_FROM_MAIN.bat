@echo off
setlocal

REM === CONFIGURACIÓN ===
set RAMA_PRINCIPAL=main
set RAMA_TEST=test

echo ✅ Iniciando actualización de '%RAMA_TEST%' con cambios de '%RAMA_PRINCIPAL%'

REM === 1. Ir a main y actualizarla
echo Cambiando a '%RAMA_PRINCIPAL%'...
git checkout %RAMA_PRINCIPAL%
git pull origin %RAMA_PRINCIPAL%

REM === 2. Ir a test y actualizarla desde main
echo Cambiando a '%RAMA_TEST%'...
git checkout %RAMA_TEST%

echo Haciendo merge de '%RAMA_PRINCIPAL%' en '%RAMA_TEST%'...
git merge %RAMA_PRINCIPAL%

REM === 3. Subir la rama test al remoto
git push origin %RAMA_TEST%

echo.
echo ✅ La rama '%RAMA_TEST%' está actualizada con los últimos cambios de '%RAMA_PRINCIPAL%' y subida al remoto.

endlocal
pause