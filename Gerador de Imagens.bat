@echo off
title Gerador de Imagens de Produto
cd /d "%~dp0"

rem --- primeira execucao: cria ambiente proprio e instala tudo ---
if not exist ".venv\Scripts\python.exe" (
  echo.
  echo  Primeira vez: preparando o ambiente. Pode levar 1-2 minutos...
  echo.
  python -m venv .venv 2>nul || py -3 -m venv .venv
  if not exist ".venv\Scripts\python.exe" (
    echo  ERRO: nao encontrei o Python. Instale em https://python.org e tente de novo.
    pause
    exit /b 1
  )
  call ".venv\Scripts\activate.bat"
  python -m pip install --upgrade pip -q
  pip install -q -r requirements.txt
) else (
  call ".venv\Scripts\activate.bat"
)

rem --- abre o app (a propria janela abre o navegador) ---
python app.py
echo.
echo  App encerrado. Pode fechar esta janela.
pause
