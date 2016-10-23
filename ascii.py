import subprocess

from PIL import Image
from io import BytesIO

def cvt(istr):
    im = Image.open(BytesIO(istr))
    im.save
