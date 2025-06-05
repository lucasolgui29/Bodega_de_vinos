import uuid
from models.db import db

class VariedadUva(db.Model):
    __tablename__ = 'variedad_uva'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200), nullable=True)
    color = db.Column(db.String(20), nullable=False)
    region = db.Column(db.String(50), nullable=False)
    ruta_foto = db.Column(db.String(255), nullable=True)

    

    def __init__(self, nombre, descripcion, color, region, ruta_foto=None, etapa=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.color = color
        self.region = region
        self.ruta_foto = ruta_foto

    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'color': self.color,
            'region': self.region,
            'ruta_foto': self.ruta_foto
        }