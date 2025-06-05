import uuid
from models.db import db
from datetime import datetime

class VinoProducto(db.Model):
    __tablename__ = "vino_producto"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    nombre_vino = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(255), nullable=True)
    
    proceso_id = db.Column(db.String(36), db.ForeignKey('proceso_vinificacion.id'), nullable=False)
    
    proceso = db.relationship('ProcesoVinificacion', backref=db.backref('vinos_productos', lazy=True))

    def __init__(self, nombre_vino, precio, imagen, proceso_id):
        self.nombre_vino = nombre_vino
        self.precio = precio
        self.imagen = imagen
        self.proceso_id = proceso_id
    
    def serialize(self):
        return {
            "id": self.id,
            "nombre_vino": self.nombre_vino,
            "precio": self.precio,
            "imagen": self.imagen,
            "proceso_id": self.proceso_id,
            "nombre_lote": self.proceso.nombre_lote,
            "variedad_uva": self.proceso.variedad_uva.nombre
        }
    

