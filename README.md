# Neptune 2.0 (jpg-Converter_GUI)

This tool convert png file to jpg file not only change name but also file format completely.
And this will help you change jpg Data set files name to recongnize easily.

# Change file name and .png to .jpg
First click Load button, and load png or jpg files to use Data set for DL.
And then write Target Name you want to change (e.g. hammer, 망치...)
If you choose Raw Data in Design Method then just you can change file name.
Finally Press Start Button. 
And if there is .txt file having same name with target png(jpg) file, then copy that conveted txt file at the same time in ./result path. But txt file SHOLUD BE EXISTS in same path target image file

When you want to reset current configuration, press reset button.

# Convert grayscale image, Rotate and Salt & Pepper noise
If you choose Gray Scale in Design Method then convert color image files to gray scale.
When you want to rotate images then write dgree on Rotate textbox.
And make Salt & Pepper noise in image by checking Salt Pepper check box 

# Bluring
This tool provide 5 knids of method
1. Convolution
2. Averaging Blurring
3. Gaussian Blurring
4. Median Blurring
5. Bilateral Filtering

# Image Quality (file size)
You can change image quality by using opencv method

# Nonlinear Mapping
Insert Nonlinear Mapping Effect

# Lens Distortion
Distort image with Lens Distortion effect

# save format
./result/'targetName'_'i'.jpg

# Make exe
pyinstaller --noconsole --add-binary "neptune.png";"." --add-binary "jpgConverter.ui";"." --add-binary "sampleOriginal.jpg";"." --add-binary "sampleResult.jpg";"." --onefile --icon=../icons/neptune.ico "Neptune(jpgConverter).py"

# icon, png
icon from https://icon-icons.com/ko/, and sampleOriginal.jpg has been taken by me
