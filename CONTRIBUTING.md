# Contributing to Mnemox

## Development setup

Mnemox requires Python 3.12 or later. Verify the installed version:

```text
python --version
```

Create and activate an isolated environment:

```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

```bash
# macOS or Linux
python -m venv venv
source venv/bin/activate
```

Install the exact tracked dependencies:

```text
python -m pip install -r requirements.txt
```

If a task adds a dependency, update `requirements.txt` from a clean project virtual environment. Review the result before committing and reject editable installs, local paths, and `file:` URLs.

## Run tests locally

Run the complete suite before pushing:

```powershell
# Windows PowerShell
$env:PYTHONUTF8 = "1"
python -m pytest -q
```

```batch
:: Windows cmd.exe
set PYTHONUTF8=1
python -m pytest -q
```

```bash
# macOS or Linux
export PYTHONUTF8=1
python -m pytest -q
```

The current baseline is at least 391 passed tests, with no failures or skips. Do not hide failures with selection or skip flags.

For diagnosis after the full suite has run:

```text
python -m pytest tests/step1/test_manifest.py -v
python -m pytest -k "memory" -v
```

Coverage options require a separately approved and pinned coverage dependency; they are not part of the supported baseline command.

## Continuous integration

The `Test Suite` GitHub Actions workflow runs on:

- pushes to `main` and `agent/*` branches;
- pull requests targeting `main`; and
- manual runs from the GitHub Actions interface.

It uses `windows-latest`, Python 3.12, the pinned `requirements.txt`, and `PYTHONUTF8=1`. Results are visible in the repository's [Actions page](https://github.com/ajaygh99/mnemox/actions).

A green workflow proves the tested commit passed the configured suite. Branch protection must separately require the resulting check before it can block a merge; changing that repository setting requires owner approval.

If local and CI results disagree:

1. Confirm `PYTHONUTF8=1` is set.
2. Confirm Python is version 3.12 or later.
3. Create a fresh virtual environment and reinstall `requirements.txt`.
4. Confirm the checkout and `requirements.txt` have no uncommitted changes.
5. Report the exact failing test and compare it with the same commit, rather than assuming it is pre-existing.

## Pull requests

1. Start from the current `origin/main` on a scoped branch.
2. Change only paths authorized by the issue.
3. Run the complete supported suite.
4. Commit and push the scoped change.
5. Open a draft pull request with exact-head evidence.
6. Wait for CI and independent review.
7. Do not merge, deploy, publish, or perform another approval-gated action without exact owner approval.

## Version bumps

When an approved release task changes the extension version, update `extension/manifest.json` and the matching release assertion in `tests/performance/test_performance_guards.py` together. Tagging and publication remain separate owner-approved actions.

## Questions and issues

Review [existing issues](https://github.com/ajaygh99/mnemox/issues) before creating a new one. New implementation issues must state their phase, dependencies, allowed paths, non-goals, acceptance tests, risks, rollback, evidence location, and required approvals.
