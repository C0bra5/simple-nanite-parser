# Simple Nanite Parser
This is a simple parser for cooked Unreal Engine 5.3+ static meshes that uses Nanite with maximum quality. FModel only exports the fallback mesh, which tends to be low quality.

## Requirements:
- [Python 3.12](https://www.python.org/downloads/release/python-31210/)
    - 3.12 is the minimum version.
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
5. Drag and drop one of the files FModel created onto the `run.bat` file in this project's folder.
6. Wait a bit, the program takes a while to run, especially with larger meshes.
8. Your file will be waiting in the `out` folder.

## The script in action:

https://github.com/user-attachments/assets/af5ea32c-eace-4b33-822a-69fca2052a5e
