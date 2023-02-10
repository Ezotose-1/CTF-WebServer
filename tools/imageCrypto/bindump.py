# Packages
from PIL import Image

# Python Modules
from math import sqrt, ceil
import io


def encodeFile(path, out='img.png'):
    """
    Encode a file into a image (bytes to pixels)
    
    :param path: Position of the file to encode
    :optional out: Path where to create the image
    :return: None
    """
    with io.open(path, "rb", buffering = 0) as file:
        data = file.read()

    l = ceil(sqrt(len(data)))    
    img = Image.new('RGB', (l + 1, l + 1), color='white')
    x, y = 0, 0

    for bit in data:
        color = (bit, bit, bit)
        img.putpixel((x, y), color)
        x += 1
        if (x > l):
            x = 0
            y += 1
    print(f"Image '{out}': {l + 1}x{l + 1}")
    img.save(out)


def decodeFile(path='img.png', out="decode.out"):
    """
    Decode a image (pixel to bytes) into an executable.

    :param path: Position of the image to decode
    :opional out: Path of the executable to create
    :return: None
    """
    with Image.open(path) as img:
        pixels = list(img.getdata())
        data = b''
        for p in pixels:
            data += p[0].to_bytes(1, byteorder='big')

    with open(out, "wb+") as fp:
        fp.write(data)



if (__name__ == "__main__"):
    encodeFile('a.out')
    decodeFile('img.png', 'decode.out')