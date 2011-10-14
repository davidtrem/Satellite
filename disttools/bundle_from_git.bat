@echo off
echo ------------------------- >CON
echo Creating Satellite Bundle >CON
rmdir satellite_bundle /s /q
call git clone --depth 1 git://github.com/davidtrem/Satellite.git satellite_bundle
call git clone --depth 1 git://github.com/davidtrem/ThunderStorm.git
xcopy ThunderStorm\thunderstorm satellite_bundle\thunderstorm\ /e >NUL
rmdir ThunderStorm /s /q
xcopy msdll satellite_bundle >NUL
