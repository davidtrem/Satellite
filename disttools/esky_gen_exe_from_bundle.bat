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

echo - Compiling with esky... >CON
cd satellite_bundle
python setup-esky.py bdist_esky>..\output.txt 2>..\error.txt
cd ..
echo Done. >CON
echo See generated error.txt and >CON
echo output.txt files in case of problem>CON

echo - Copying dist files in this folder... >CON
xcopy satellite_bundle\dist .\ /e >NUL

echo Done! >CON
