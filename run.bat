@echo off
setlocal EnableDelayedExpansion
pushd %~pd0

if exist "./.venv/Scripts/activate.bat" goto venv_available
where py>nul
if !errorlevel!==0 (
	py -3 -c ""
	if not !errorlevel!==0 goto check_python
	rem a bit of future proofing
	py -3 -c "import sys; print(sys.version_info.minor > 12)" | findstr "True">nul
	if !errorlevel!==0 goto setup_with_py
)

:check_python
where python>nul
if !errorlevel!==0 (
	rem check if python is installed
	python -c ""
	if not !errorlevel!==0 goto python_missing
	rem ensure python 3 or higher
	python -c "import sys; print(sys.version_info.major > 3)" | findstr "True">nul
	if !errorlevel!==0 goto setup_with_python
	python -c "import sys; print(sys.version_info.major == 3)" | findstr "True">nul
	if not !errorlevel!==0 goto python_missing
	
	
	rem ensure python >= 3.12
	python -c "import sys; print(sys.version_info.minor > 12)" | findstr "True">nul
	if !errorlevel!==0 goto setup_with_python
)
goto python_missing

:python_missing
echo unable to identify a version of python greater or equal to 3.12
echo check to make sure you have the right dependencies installed
goto bad_end

:setup_with_python
echo creating venv using python
python -m venv "./.venv"
goto check_venv_creation

:setup_with_py
echo creating venv using py -3
py -3 -m venv "./.venv"
goto check_venv_creation

:check_venv_creation
if not !errorlevel!==0 (
	echo failed to create venv!
	goto bad_end
)
if not exist "./.venv/Scripts/activate.bat" (
	echo failed to create venv!
	goto bad_end
)
call "./.venv/Scripts/activate.bat"
python -m pip install -r "requirements.txt"
goto venv_ready

:venv_available
call "./.venv/Scripts/activate.bat"
goto venv_ready

:venv_ready
python __main__.py %1
if exist ".venv/Scripts/deactivate.bat" (
	call ".venv/Scripts/deactivate.bat"
)
if not !errorlevel!==0 goto bad_end
goto end

:bad_end
pause
goto end

:end
popd
endlocal
