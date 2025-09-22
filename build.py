import PyInstaller.__main__

PyInstaller.__main__.run([
    'color_converter.py',
    '--onefile',
    '--windowed',
    '--name=Color_converter',
    '--clean'
])