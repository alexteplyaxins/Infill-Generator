# infill_generator_imslab
A software to decompose and generate infill tool paths from custom `.DXF` files.

## Running the application
First install the requirements. It's recommended that you use a virtual environmemt. This is optional. Here we use `conda`.
```bash
conda create -n "infill" python==3.9
```
After that activate the virtual environment.
```bash
conda activate infill
```
Then install the requirements.
```bash
python -m pip install -r requirements.txt
```
To run application, run this command on the terminal.
```bash
python src/app.py
```
Some example `.DXF` files are under the `DXF files` directory. You can import these to the software.
## Building to executable
To build to executable run the following command.
```bash
cd src
python -m PyInstaller --onefile --windowed app.py
```
This might take a couple minutes to run. The command will generate an `app.exe` file under the `dist/` directory.

## To do

- Export each layers to a `.DXF` file.
- Export the layers decomposition to a file (perhaps `.json`).

To anyone working on this project on the future, I believe it is better to export the layer decompostion to a file then build a separate software that read this file then apply it as infills on a 3D model, rather than to continue to add more feature to this software. This project is already badly written as it is, it's best not to make it even more complex and jumbled.

