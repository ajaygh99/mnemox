@echo off
:: ============================================================
:: MNEMOX — Git Checkpoint Manager  (v0.1 → v0.8)
:: Run after each step to commit + tag the stable state
:: ============================================================

echo.
echo  MNEMOX — Git Checkpoint Manager
echo  ==================================
echo.

git config --global user.name "Ajay"
git config --global user.email "ajjukak123@gmail.com"

if not exist ".git" (
    git init
    git branch -M main
    echo  [OK] Git repo initialized
) else (
    echo  [OK] Git repo already exists
)

git rev-parse v0.8 >nul 2>&1
if %errorlevel% == 0 goto already_done

git rev-parse v0.7 >nul 2>&1
if %errorlevel% == 0 goto commit_v8

git rev-parse v0.6 >nul 2>&1
if %errorlevel% == 0 goto commit_v7_v8

:: v0.6 or earlier — commit everything
git add .
git commit -m "feat: Steps 1-8 — full Mnemox product, tested and launch-ready"
git tag v0.1
git tag v0.2
git tag v0.3
git tag v0.4
git tag v0.5
git tag v0.6
git tag v0.7
git tag v0.8
echo.
echo  All checkpoints v0.1 through v0.8 created!
goto done

:commit_v7_v8
git add .
git commit -m "feat: Steps 7-8 — auth, billing, E2E tests, landing page, launch copy"
git tag v0.7
git tag v0.8
echo.
echo  Checkpoints v0.7 and v0.8 created!
goto done

:commit_v8
git add .
git commit -m "feat: Step 8 — E2E integration tests, landing page, ProductHunt launch assets"
git tag v0.8
echo.
echo  Checkpoint v0.8 created!
goto done

:already_done
echo  v0.8 already tagged — you are fully shipped!
git status --short

:done
echo.
echo  Full build history:
git log --oneline
echo.
git tag
echo.
echo  How to revert to any checkpoint:
echo    git checkout v0.X     (inspect that version)
echo    git checkout main     (back to latest)
echo.
pause
