> [!IMPORTANT]  
> This project is now archived as the latest versions of [FModel](https://github.com/4sval/FModel) and [CUE4Parse](https://github.com/FabianFG/CUE4Parse) natively support nanite mesh extraction for all games using UE 5.0 to UE 5.3.

# Simple Nanite Parser
This is a simple parser for cooked Unreal Engine 5.3 static meshes that uses Nanite with maximum quality.

## Requirements:
- [Python 3.12](https://www.python.org/downloads/release/python-31210/)
    - 3.12 is the minimum version required to run the extraction script.
- [Git](https://github.com/git-guides/install-git)
    - Used to download the custom version of [FModel](https://github.com/C0bra5/FModel/tree/nanite-patch-stable) and [CUE4Parse](https://github.com/C0bra5/CUE4Parse/tree/nanite-patch-stable) needed for this project.
- [.NET 8 SDK](https://dotnet.microsoft.com/en-us/download/dotnet/8.0)
    - Used to build the custom version of FModel and CUE4Parse needed for this project.

## How to use:
1. Run `setup.bat` to ensure you have the correct dependencies installed, download the custom version of FModel and CUE4Parse this project requires, and automatically build the custom version of FModel.
    - You only need to do this step once.
2. Start the custom version of FModel using `start_fmodel.bat`.
    - or you can manually launch it, it's in `FModel/FModel/bin/Debug/net8.0-windows/win-x64/FModel.exe`.
3. Find the static mesh you want to dump in FModel.
4. Right-click the entry and select `Export Raw Data (.uasset)`
5. Right-click the entry again and select `Save Properties (.json)`
6. Drag and drop one of the files FModel created onto the `extract.bat` file in this project's folder.
    - You may have to wait a bit for the program to complete its work, especially with larger meshes.
8. Your file will be waiting in the `out` folder.

## Video Example:

https://github.com/user-attachments/assets/c238b44e-559a-4f1e-858a-bac22af6f56d
