# Jack Walmsley 2020-12-26
import os
import pathlib
import random
import qrcode
from PIL import Image, ImageFont, ImageDraw
BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
font = ImageFont.truetype("C:\\Windows\\Fonts\\micross.ttf", 12)


def encode(num: int, alphabet: str):
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


def create_card(id: str):
    """Creates a card image and saves it to /output/card_[ID].png

    :param id: id to print on card
    """
    imgpath = os.path.join(pathlib.Path(
        __file__).parent.absolute(), "BitBallot Card.png")
    img = Image.open(imgpath)
    draw = ImageDraw.Draw(img)
    textpos_x, textpos_y = 215, 385
    text_bord = 4
    qrpos_x, qrpos_y = 180, 315

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=4,
        border=0,
    )
    qr.add_data(id)
    qr.make(fit=True)
    code = qr.make_image(fill_color="black", back_color="white")

    w, h = draw.textsize(id, font)
    draw.text((textpos_x-w//2, textpos_y-h//2), id, (0, 0, 0), font=font)
    draw.rectangle(((textpos_x-w//2 - text_bord, textpos_y-h//2 - text_bord),
                    (textpos_x+w//2 + text_bord, textpos_y+h//2 + text_bord)), outline="black")
    img.paste(code, (qrpos_x-code.width//2, qrpos_y-code.height//2))
    img.save(os.path.join(pathlib.Path(__file__).parent.absolute(),
                          "output/card_{}.png".format(id)))
    print("INSERT INTO uids VALUES(\"{}\");".format(id))


def create_random_cards(num: int, code_length: int = 15):
    """Generates random cards

    :param num: number of cards to generate
    :param code_length: length of codes to print on cards
    """
    for i in range(num):
        id = encode(random.randint(0, 62**code_length), BASE62)
        create_card(id)
