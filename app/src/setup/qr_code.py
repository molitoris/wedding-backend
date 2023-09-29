import qrcode
from PIL import Image
from typing import Optional
import pathlib

class QrCodeImageGenerator:

    def __init__(self, logo: Optional[Image.Image] = None) -> None:

        self.logo = None
        if logo:
            # taking base width
            basewidth = 100

            # adjust image size
            wpercent = (basewidth/float(logo.size[0]))
            hsize = int((float(logo.size[1])*float(wpercent)))
            self.logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)


    def get_image(self, text: str, output_path: pathlib.Path):
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(text)
        qr.make()

        img = qr.make_image(fill_color='black', back_color='white').convert('RGB')

        if self.logo:
            # set size of QR code
            pos = ((img.size[0] - img.size[0]) // 2, (img.size[1] - img.size[1]) // 2)
            img.paste(self.logo, pos)

        img.save(output_path)

if __name__ == '__main__':
    qr = QrCodeImageGenerator()
    qr.get_image('https://google.com', pathlib.Path('./test.png'))