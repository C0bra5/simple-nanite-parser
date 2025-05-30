# Simple Nanite Parser
A simple parser for cooked Unreal Engine 5.3+ static meshes that uses Nanite with maximum quality. FModel only exports the fallback mesh which tends to be very low quality.

## Requirements:
- [Python 3.12](https://www.python.org/downloads/release/python-31210/) (you'll need to build compushady yourself if you use something older)
- [DotNET 8](https://dotnet.microsoft.com/en-us/download/dotnet/8.0) (to build FModel and CUE4Parse)
- A modified version of FModel with the fixes I've made for nanite (see instructions below)

## How to use:
1. As my fix for CUE4Parse hasn't been accepted into the main repo yet, you'll have to download a custom version of FModel with my fixes for it: 
    1. Download the source code for FModel: `git clone https://github.com/4sval/FModel --recursive`
    2. Open the folder you've downloaded and delete the CUE4Parse folder and replace it with a version of CUE4Parse with my fixes `git clone https://github.com/C0bra5/CUE4Parse -b nanite-patch-stable`
    4. Open `/FModel/CUE4Parse/CUE4Parse.sln` and build the solution (or else FModel won't be able to build)
    5. Open `/FModel/FModel.sln` and build/launch the application.
2. Find the static mesh you want to dump in FModel.
3. Right-click the entry again and select `Export Raw Data (.uasset)`
4. Right-click the entry and select `Save Properties (.json)`
5. Click the file name in the log at the bottom of FModel to open the directory where the files were extracted.
6. Copy the full path of the file eg: `C:/FModel_extracts/path/to/file.json`
7. run the script: `python __main__.py "C:/FModel_extracts/path/to/file.json"`
8. Your .obj will be waiting in the `out` folder.

## The script in action:

https://github.com/user-attachments/assets/2b7efd84-e7a1-452a-ae0a-ae956422734c

