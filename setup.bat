@echo off
pushd
setlocal EnableDelayedExpansion



rem check git dep
where git>nul
if not !errorlevel!==0 goto git_missing
echo Git: OK



rem check dotnet dep
where dotnet>nul
if not !errorlevel!==0 goto dotnet_missing
rem check dotnet 8 installed
dotnet --list-sdks|findstr /R "8\.[0-9][0-9]*\.[0-9][0-9]*">nul
if not !errorlevel!==0 goto dotnet_missing
echo .NET 8 SDK: OK



rem check if python 3.12 or higher is installed using py launcher
if exist "./venv/Scripts/activate.bat" goto check_venv_version
where py>nul
if !errorlevel!==0 (
	rem check if 3.12 is installed specifically
	py -3.12 -c "import sys; print((sys.version_info.major > 3) or (sys.version_info.major == 3 and sys.version_info.minor >= 12))" | findstr "True">nul
	if !errorlevel!==0 goto setup_with_py_3_12
	rem else check the default/latest python 3 version installed
	py -3 -c "import sys; print((sys.version_info.major > 3) or (sys.version_info.major == 3 and sys.version_info.minor >= 12))" | findstr "True">nul
	if !errorlevel!==0 goto setup_with_py
)

where python>nul
if !errorlevel!==0 (
	rem ensure python 3.12 or higher
	python -c "import sys; print((sys.version_info.major > 3) or (sys.version_info.major == 3 and sys.version_info.minor >= 12))" | findstr "True">nul
	if !errorlevel!==0 goto setup_with_python
)
goto python_missing


:setup_with_python
echo creating venv using python
python -m venv "./venv"
goto check_venv_creation

:setup_with_py_3_12
echo creating venv using py -3.12
py -3.12 -m venv "./venv"
goto check_venv_creation

:setup_with_py
echo creating venv using py -3
py -3 -m venv "./venv"
goto check_venv_creation


rem check if venv was created correctly
:check_venv_creation
if not !errorlevel!==0 goto venv_creation_failed
if not exist "./venv/Scripts/activate.bat" goto venv_creation_failed
goto check_venv_version


rem activate venv and check the version
:check_venv_version
call "./venv/Scripts/activate.bat"
if not !errorlevel!==0 (
	echo failed to activate venv!
	goto bad_end
)
python -c "import sys; print((sys.version_info.major > 3) or (sys.version_info.major == 3 and sys.version_info.minor >= 12))" | findstr "True">nul
if not !errorlevel!==0 (
	echo venv has incorrect version of python!
	call "./venv/Scripts/deactivate.bat"
	goto bad_end
)



rem install python requirements
python -m pip install -r "requirements.txt"
if not !errorlevel!==0 (
	echo failed to install python requirements!
	call "./venv/Scripts/deactivate.bat"
	goto bad_end
)
call "./venv/Scripts/deactivate.bat"
echo Python: OK!



rem download FModel if the user forgot to use --recursive during the clone
if not exist "./FModel/FModel/FModel.sln" (
	if exist "./.git" (
		git submodule update --init --recursive
		if not !errorlevel!==0 (
			echo failed to clone custom version of FModel
			goto bad_end
		)
	) else (
		rem in case they downloaded the zip from github
		git clone https://github.com/C0bra5/FModel -b nanite-patch-stable --recursive
		if not !errorlevel!==0 (
			echo failed to clone custom version of FModel
			goto bad_end
		)
	)
)



rem build FModel if needed
if not exist ".\FModel\FModel\bin\Debug\net8.0-windows\win-x64\FModel.exe" (
	rem build FModel if needed
	pushd ".\FModel\FModel"
	dotnet build "FModel.sln" /property:WarningLevel=0
	echo !errorlevel!
	if not !errorlevel!==0 (
		echo failed to build FModel!
		popd
		goto bad_end
	)
	popd
)
goto good_end


:git_missing
echo You need to install git to use this: https://github.com/git-guides/install-git
goto bad_end

:dotnet_missing
echo you need to install .NET 8 SDK installed: https://dotnet.microsoft.com/en-us/download/dotnet/8.0
goto bad_end

:python_missing
echo you need to install python 3.12 or higher: https://www.python.org/downloads/release/python-31210/
goto bad_end

:venv_creation_failed
echo failed to create venv!
goto bad_end



:bad_end
popd
endlocal
pause
goto true_end

:good_end
popd
endlocal
goto true_end

:true_end
