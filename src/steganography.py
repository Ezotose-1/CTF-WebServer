import shutil
from pathlib import Path

def hideTextInImage(text: str, image: str) -> str:
    """Append the text string into the bottom of the image.
    It will not modify the given image but create a new one called
    'hidden.png' at the same position of the original.

    :param text: Plaintext to append at the bottom of the image data.
    :param image: Path to the given image.
    :return: The position of the new image.
    """
    newPath = Path(image).parent.resolve().joinpath('hidden.png')
    shutil.copyfile(image, newPath)
    with open(newPath, 'a') as fp:
        fp.write("\n" + text)
    return newPath

if (__name__ == "__main__"):
    p = hideTextInImage("Nullam-imperdiet-in", "hidden_based.png")
    print(f'"{p}"')