from flask_sqlalchemy import SQLAlchemy
import qrcode
import io


db = SQLAlchemy()

def generate_qr_code(url):
    img = qrcode.make(url)
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io