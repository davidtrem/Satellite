@echo off
echo ------------------------------ >CON
echo Preparing satellite window exe >CON
echo - First, cleaning... >CON
del output.txt
del error.txt
rmdir satellite_exe /s /q
cd satellite_bundle
rmdir build /s /q
rmdir dist /s /q
cd ..
echo Done. >CON

echo - Compiling with py2exe... >CON
cd satellite_bundle
python setup-py2exe.py py2exe>..\output.txt 2>..\error.txt
cd ..
echo Done. >CON
echo See generated error.txt and >CON
echo output.txt files in case of problem>CON

echo - Creating final satellite_exe folder... >CON
mkdir satellite_exe
xcopy satellite_bundle\dist satellite_exe\satellite_package\ /e >NUL
copy satellite_bundle\satellite_exe\launch_satellite.bat satellite_exe\launch_satellite.bat >NUL
cd satellite_exe\satellite_package\mpl-data\images
copy *.png *.svg >NUL
cd ..\..\..\..

echo Done! >CON
