s
=

a web application

Install
-------
::

    git clone ssh://git@github.com/her0e1c1/s
    pyvenv venv34
	source venv34/bin/activate
	pip isntall -r requirements.txt


freetype is not installed
-------------------------
This error ``The C/C++ header for freetype2 (ft2build.h)`` may happen.
if your os is freebsd, then do this ::

     sudo pkg install print/freetype
     cd /usr/local/include
     sudo ln -s freetype2/ft2build.h .
