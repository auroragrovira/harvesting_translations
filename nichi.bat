@echo off
setlocal EnableDelayedExpansion
REM =========================================================
REM  Nichibun JP-COAR 2.0 full harvest (sin cortes)
REM  Requiere: curl + PowerShell (Windows 10/11 estándar)
REM =========================================================

set "BASE_URL=https://nichibun.repo.nii.ac.jp/oai"
set "PREFIX=jpcoar_2.0"
set "OUT=nichibun_jpcoar2_all"
set "PAGE=1"

REM ---------- FUNCION CURL (argumento = token o vacío) ----------
:Fetch
echo(==== Descargando pagina !PAGE! ...
if "%~1"=="" (
  curl -sS -G "%BASE_URL%" --data-urlencode "verb=ListRecords" --data-urlencode "metadataPrefix=%PREFIX%" ^
       -o "%OUT%_!PAGE!.xml"
) else (
  curl -sS -G "%BASE_URL%" --data-urlencode "verb=ListRecords" --data-urlencode "resumptionToken=%~1" ^
       -o "%OUT%_!PAGE!.xml"
)
if errorlevel 1 (
  echo  ^^^! Error en cURL; abortando.
  goto :EOF
)

REM ---------- EXTRAER TOKEN, CURSOR Y TOTAL (PowerShell) ----------
for /f "usebackq delims=" %%T in (`powershell -NoProfile -Command ^
  "$xml=[xml](Get-Content -LiteralPath '%OUT%_!PAGE!.xml');" ^
  "$n=$xml.SelectSingleNode('//*[local-name()=\"resumptionToken\"]');" ^
  "if($n){$n.InnerText}"`) do set "TOKEN=%%T"

for /f "usebackq delims=" %%T in (`powershell -NoProfile -Command ^
  "$xml=[xml](Get-Content -LiteralPath '%OUT%_!PAGE!.xml');" ^
  "$n=$xml.SelectSingleNode('//*[local-name()=\"resumptionToken\"]');" ^
  "if($n){$n.getAttribute('cursor')}"`) do set "CURSOR=%%T"

for /f "usebackq delims=" %%T in (`powershell -NoProfile -Command ^
  "$xml=[xml](Get-Content -LiteralPath '%OUT%_!PAGE!.xml');" ^
  "$n=$xml.SelectSingleNode('//*[local-name()=\"resumptionToken\"]');" ^
  "if($n){$n.getAttribute('completeListSize')}"`) do set "TOTAL=%%T"

REM ---------- INFORME DE PROGRESO ----------
if defined TOTAL if defined CURSOR (
    set /a PCT=!CURSOR!*100/!TOTAL!
    echo  Página !PAGE!  –  !CURSOR! de !TOTAL! registros  (^!PCT!%%^!)
) else (
    echo  Página !PAGE!  –  tamaño total no disponible.
)

REM ---------- ¿HAY MÁS PÁGINAS? ------------
if "!TOKEN!"=="" (
    echo(==== Descarga completa: no hay mas resumptionToken ====
    goto :EOF
)

REM ---------- SIGUIENTE VUELTA -------------
set /a PAGE+=1
REM Escapar ^ & % en el token para cmd.exe
set "TOKEN_ESC=!TOKEN:^=^^!"
set "TOKEN_ESC=!TOKEN_ESC:&=^&!"
set "TOKEN_ESC=!TOKEN_ESC:%%=%%%%!"
goto :Fetch !TOKEN_ESC!


