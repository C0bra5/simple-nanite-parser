@echo off
setlocal EnableDelayedExpansion
pushd %~pd0

rem check if venv exists
if not exist "./venv/Scripts/activate.bat" (
	echo venv not found! did you forget to run setup.bat?
	goto bad_end
)

call "./venv/Scripts/activate.bat"
python __main__.py %1
if not !errorlevel!==0 (
	if exist "./venv/Scripts/deactivate.bat" (
		call "./venv/Scripts/deactivate.bat"
	)
	goto bad_end
) else {
	if exist "./venv/Scripts/deactivate.bat" (
		call "./venv/Scripts/deactivate.bat"
	)
	goto good_end
}

if not !errorlevel!==0 goto bad_end
goto end

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