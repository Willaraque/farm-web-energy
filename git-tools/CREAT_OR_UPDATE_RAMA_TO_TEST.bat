@echo off
setlocal

REM === CONFIGURACIÓN ===
set RAMA_BASE=test

REM === INPUT ===
set /p NOMBRE_RAMA=Introduce el nombre de la nueva rama de trabajo (o existente): 

REM === CAMBIAR A RAMA BASE Y ACTUALIZARLA ===
echo Cambiando a la rama base '%RAMA_BASE%'...
git checkout %RAMA_BASE%
git pull origin %RAMA_BASE%

REM === COMPROBAR SI LA RAMA YA EXISTE LOCALMENTE ===
git show-ref --verify --quiet refs/heads/%NOMBRE_RAMA%
if %errorlevel%==0 (
    echo La rama '%NOMBRE_RAMA%' ya existe localmente. Cambiando a ella...
    git checkout %NOMBRE_RAMA%
    echo Actualizando con los cambios de '%RAMA_BASE%' mediante merge...
    git merge %RAMA_BASE%
) else (
    echo Creando nueva rama '%NOMBRE_RAMA%' desde '%RAMA_BASE%'...
    git checkout -b %NOMBRE_RAMA%
)

REM === SUBIR AL REMOTO SI ES NECESARIO ===
git push -u origin %NOMBRE_RAMA%

echo.
echo ✅ Rama '%NOMBRE_RAMA%' lista y actualizada con los cambios de '%RAMA_BASE%'.
endlocal
pause