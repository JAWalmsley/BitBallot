# Jack Walmsley 2020-12-26
BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
import random, pathlib, os

from PIL import Image, ImageFont, ImageDraw


def encode(num, alphabet):
    """Encode a positive number into Base X and return the string.

    :param num: the number to encode
    :param alphabet: the characters to use for the output
    """
    if num == 0:
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        num, rem = divmod(num, base)
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def decode(string, alphabet=BASE62):
    """Decode a Base X encoded string into the number

    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for decoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1

    return num


def create_card(id):
    imgpath = os.path.join(pathlib.Path(__file__).parent.absolute(), "BitBallot Card.png")
    img = Image.open(imgpath)
    draw = ImageDraw.Draw(img)
    w, h = draw.textsize(id, font)
    draw.text((200-w/2, 310-h/2), id, (0, 0, 0), font=font)
    img.save(os.path.join(pathlib.Path(__file__).parent.absolute(), "output/card_{}.png".format(id)))
    print("INSERT INTO uids VALUES(\"{}\");".format(id))


font = ImageFont.truetype("C:\\Windows\\Fonts\\micross.ttf", 12)
create_card('ffvZYcSaW17GHN0')
create_card('5KMeZ1Yc8c7sptQ')
create_card('cBZs0ITJfKvqwEt')
create_card('null')


def random_cards(num):
    for i in range(num):
        id = encode(random.randint(0, 768909704948766668552634367), BASE62)
        create_card(id)

