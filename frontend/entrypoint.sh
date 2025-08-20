#!/bin/sh
echo "Instalando dependências..."
npm install

echo " Iniciando Vite..."
npm run dev -- --host 0.0.0.0 --port 5173