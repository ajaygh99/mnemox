@echo off
:: ============================================================
:: MNEMOX — Git Checkpoint Manager
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

:: ── Check from highest step downward ──────────────────────────────────────

git rev-parse v0.7 >nul 2>&1
if %errorlevel% == 0 goto already_done

git rev-parse v0.6 >nul 2>&1
if %errorlevel% == 0 goto commit_v7

git rev-parse v0.5 >nul 2>&1
if %errorlevel% == 0 goto commit_v6_v7

git rev-parse v0.4 >nul 2>&1
if %errorlevel% == 0 goto commit_v5_v6_v7

git rev-parse v0.3 >nul 2>&1
if %errorlevel% == 0 goto commit_v4_v5_v6_v7

:: No tags at all — commit everything from scratch
git add .
git commit -m "feat: Steps 1-7 — extension, capture, backend, vectors, injection, dashboard, auth+billing"
git tag v0.1
git tag v0.2
git tag v0.3
git tag v0.4
git tag v0.5
git tag v0.6
git tag v0.7
echo.
echo  All checkpoints v0.1 through v0.7 created!
goto done

:commit_v4_v5_v6_v7
git add .
git commit -m "feat: Steps 4-7 — vectors, injection, dashboard, auth+billing"
git tag v0.4
git tag v0.5
git tag v0.6
git tag v0.7
echo.
echo  Checkpoints v0.4, v0.5, v0.6, v0.7 created!
goto done

:commit_v5_v6_v7
git add .
git commit -m "feat: Steps 5-7 — injection, dashboard, auth+billing"
git tag v0.5
git tag v0.6
git tag v0.7
echo.
echo  Checkpoints v0.5, v0.6, v0.7 created!
goto done

:commit_v6_v7
git add .
git commit -m "feat: Steps 6-7 — dashboard UI + Supabase auth, Stripe billing, team sharing"
git tag v0.6
git tag v0.7
echo.
echo  Checkpoints v0.6 and v0.7 created!
goto done

:commit_v7
git add .
git commit -m "feat: Step 7 — Supabase JWT auth, Stripe billing (Free/Pro/Team), team memory vault"
git tag v0.7
echo.
echo  Checkpoint v0.7 created!
goto done

:already_done
echo  v0.7 already tagged. Running git status...
git status --short

:done
echo.
echo  All checkpoints:
git log --oneline
echo.
git tag
echo.
echo  How to revert to any checkpoint:
echo    git checkout v0.X           (view that state)
echo    git checkout main           (back to latest)
echo.
pause
