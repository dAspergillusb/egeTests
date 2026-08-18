@echo off
chcp 65001 > null

setlocal enabledelayedexpansion

set "USER_DIR=%USERPROFILE%"
set "PROJECT_DIR=ege_project"
cd %USER_DIR%
mkdir %PROJECT_DIR%
cd %PROJECT_DIR%

rem Нужно установить некоторые программы
echo ============================================================================
echo    Скрипт для автоматического скачивания и установки необходимых программ
echo ============================================================================
echo.
set "LIST_URLS[0]=https://sbp.enterprisedb.com/getfile.jsp?fileid=1260436"
set "LIST_URLS[1]=https://www.python.org/ftp/python/3.14.7/python-3.14.7-amd64.exe"
set "LIST_URLS[2]=https://github.com/git-for-windows/git/releases/download/v2.55.0.windows.4/Git-2.55.0.4-64-bit.exe"
set "LIST_NAMES[0]=PostgresSQL"
set "LIST_NAMES[1]=Python3.14"
set "LIST_NAMES[2]=Git"
set "LIST_FILES_NAMES[0]=postgres.exe"
set "LIST_FILES_NAMES[1]=python.exe"
set "LIST_FILES_NAMES[2]=git.exe"
set "INDEXES=0 1 2"


echo ============================================================================
echo                Начинаем скачивать...
echo                Всего файлов: 3
echo                Папка скачивания: %USER_DIR%\%PROJECT_DIR%
echo ============================================================================
echo.

set "CURRENT=1"
for %%i in (%INDEXES%) do (
    echo [!CURRENT! из 3] Скачиваем: !LIST_NAMES[%%i]!
    curl -sL -o "!LIST_FILES_NAMES[%%i]!" "!LIST_URLS[%%i]!"

    if !ERRORLEVEL! equ 0 (
        echo [УСПЕХ] Дистрибутив для установки !LIST_NAMES[%%i]! скачан.
    ) else (
        echo [Ошибка] Не удалось скачать дистрибутив
    )
    set /a "CURRENT+=1"
)
echo ============================================================================
echo                        Все файлы успешно скачаны
echo ============================================================================
echo.
echo ============================================================================
echo                Начинаем установку программ в тихом режиме
echo ============================================================================

set "ARGS[0]=--mode unattended --unattendedmodeui none --superpassword postgres"
set "ARGS[1]=/quiet InstallAllUsers=1 PrependPath=1 Include_test=0"
set "ARGS[2]=/VERYSILENT /NORESTART /NOCANCEL /SP-"

set "STEP=1"
for %%i in (%INDEXES%) do (
    echo.
    echo ============================================================================
    echo  [!STEP! из 3] Установка !LIST_NAMES[%%i]!
    echo ============================================================================

    start /wait "" "!LIST_FILES_NAMES[%%i]!" !ARGS[%%i]!

    if !ERRORLEVEL! equ 0 (
        echo [OK] !LIST_NAMES[%%i]! успешно установлен
    ) else (
        echo [ERROR] Ошибка во время установки !LIST_NAMES[%%i]! (Код: !ERRORLEVEL!)
    )
    set /a "STEP+=1"
)
cd ..
rmdir /S /Q %USER_DIR%\%PROJECT_DIR%

echo.
echo ============================================================================
echo                    Все программы установлены успешно
echo ============================================================================
echo.
echo ============================================================================
echo                       Начинаем установку egeTests
echo ============================================================================

set "GIT=C:\Program Files\Git\bin\git.exe"
set "PYTHON=C:\Program Files\Python314\python.exe"

"%GIT%" clone https://github.com/dAspergillusb/egeTests

cd egeTests
mkdir files
"%PYTHON%" -m venv venv

set "VENV_PYTHON=%USER_DIR%/egeTests/venv/Scripts/python.exe"
set "FASTAPI=%USER_DIR%/egeTests/venv/Scripts/fastapi.exe"
set "VENV_PIP=%USER_DIR%/egeTests/venv/Scripts/pip.exe"

echo [1 из 3] Обновление pip внутри venv
%VENV_PIP% install --upgrade pip
echo [2 из 3] Установка зависимостей из requirements.txt
%VENV_PIP% install -r "%USER_DIR%/egeTests/requirements.txt"
echo [3 из 3] Запускаем egeTests
%FASTAPI% fastapi dev main.py