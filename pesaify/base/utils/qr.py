import qrcode
import base64
from io import BytesIO

def get_qrcode(token):
    img = qrcode.make(token)
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str.decode('utf-8')
