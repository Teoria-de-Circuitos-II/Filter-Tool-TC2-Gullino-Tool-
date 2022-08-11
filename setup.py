import PyInstaller.__main__
import sys

if sys.platform == 'win32' or sys.platform == 'cygwin':
    PyInstaller.__main__.run([
        'main.py',
        '--onefile',
        '--windowed',
        '--add-data=info.png;.'
    ])
else:
    PyInstaller.__main__.run([
        'main.py',
        '--onefile',
        '--windowed',
        '--add-data=info.png:.'
    ])
