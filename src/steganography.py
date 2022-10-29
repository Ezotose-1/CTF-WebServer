import shutil
from pathlib import Path

def hideTextInImage(text: str, image: str) -> str:
    newPath = Path(image).parent.resolve().joinpath('hidden.png')
    shutil.copyfile(image, newPath)
    with open(newPath, 'a') as fp:
        fp.write("\n" + text)
    return newPath

if (__name__ == "__main__"):
    p = hideTextInImage("Nullam-imperdiet-in", "hidden_based.png")
    print(f'"{p}"')