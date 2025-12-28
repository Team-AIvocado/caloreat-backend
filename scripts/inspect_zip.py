import zipfile
import sys
import os

zip_path = "21.한국음식/kfood.zip"
print(zip_path)

if not os.path.exists(zip_path):
    print(f"File not found: {zip_path}")
    # Try looking in absolute path just in case
    print(f"Current working directory: {os.getcwd()}")
    sys.exit(1)


# Fix for "File is not a zip file" / "BadZipFile" on Mac
# Monkeypatch to bypass "Corrupt extra field" error
def _decodeExtra(self):
    pass


zipfile.ZipInfo._decodeExtra = _decodeExtra

try:
    with zipfile.ZipFile(zip_path, "r") as z:
        print(f"Inspecting {zip_path}...")
        namelist = z.namelist()
        print(f"Total files: {len(namelist)}")
        print("First 20 items:")
        for name in namelist[:20]:
            print(name)
except Exception as e:
    print(f"Error: {e}")
