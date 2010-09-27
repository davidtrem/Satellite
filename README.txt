========
 README
========

Howto ocreate an executable for windows
=======================================

- Make sure an up to date version of thunderstorm library is
in your path.
- Copy the three MS*90 DLL into satellite folder.
- Set properly the version number in the setup-py2exe.py file.
- run "python setup-py2exe.py py2exe",
- the exe is then located in the dist folder.
- You might then want to rename the "dist" folder as "satellite_package",
- and move this folder into satellite_exe folder which contain a bat
  file to directly launch the exe.
- Create a compressed of the satellite_exe folder
- and distribute it...

