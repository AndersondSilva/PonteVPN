@echo off
echo === Subindo PonteVPN para o GitHub ===
cd ..
git init
git add .
git commit -m "feat: Initial commit with Rust backend and Next.js frontend"
echo.
echo Agora, va ao GitHub, crie um novo repositorio chamado "PonteVPN" e copie a URL.
set /p repo_url="Cole a URL do repositorio (ex: https://github.com/usuario/PonteVPN.git): "
git remote add origin %repo_url%
git branch -M main
git push -u origin main
echo.
echo === Concluido! Agora o Railway e a Vercel podem ler seu codigo. ===
pause
