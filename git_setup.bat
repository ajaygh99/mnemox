@echo off
:: ============================================================
:: MNEMOX — Git Setup + Checkpoint Script
:: Run from inside the mnemox folder (right-click > Open in Terminal, then: git_setup.bat)
:: After Step 1: run once to init repo
:: After each step: run to commit + tag the new checkpoint
:: ============================================================

echo.
echo  MNEMOX — Git Checkpoint Manager
echo  ==================================
echo.

:: Set identity
git config --global user.name "Ajay"
git config --global user.email "ajjukak123@gmail.com"

:: Init repo if not already done
if not exist ".git" (
    git init
    git branch -M main
    echo  [OK] Git repo initialized
) else (
    echo  [OK] Git repo already exists
)

:: Detect which step to commit based on existing tags
git rev-parse v0.3 >nul 2>&1
if %errorlevel% == 0 goto already_v3

git rev-parse v0.2 >nul 2>&1
if %errorlevel% == 0 goto commit_v3

git rev-parse v0.1 >nul 2>&1
if %errorlevel% == 0 goto commit_v2

:: No tags yet — commit Steps 1+2+3 together
git add .
git commit -m "feat: Step 1+2+3 — extension, prompt capture, FastAPI backend, Supabase storage"
git tag v0.1
git tag v0.2
git tag v0.3
echo.
echo  Checkpoints v0.1, v0.2 and v0.3 created!
goto done

:commit_v2
git add .
git commit -m "feat: Step 2 — prompt capture all 4 AI tools, toast, MutationObserver"
git tag v0.2

:commit_v3
git add .
git commit -m "feat: Step 3 — FastAPI backend, Supabase schema, models, config, health endpoint"
git tag v0.3
echo.
echo  Checkpoint v0.3 created!
goto done

:already_v3
echo  v0.3 already tagged. Nothing to do.

:done
echo.
echo  All checkpoints:
git log --oneline
echo.
git tag
echo.
echo  To revert to any checkpoint:  git checkout v0.X
echo.
pause
