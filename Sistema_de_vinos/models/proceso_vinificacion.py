import uuid
from models.db import db
from datetime import datetime

class ProcesoVinificacion(db.Model):
    __tablename__ = 'proceso_vinificacion'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    variedad_uva_id = db.Column(
        db.String(36), 
        db.ForeignKey('variedad_uva.id', ondelete='CASCADE'), 
        nullable=False
    )
    nombre_lote = db.Column(db.String(100), unique=True, nullable=False)
    fecha_inicio_proceso = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_fin_proceso = db.Column(db.DateTime, nullable=True)
    estado_actual = db.Column(db.String(50), nullable=False, default='En Curso')


    variedad_uva = db.relationship('VariedadUva', backref=db.backref('procesos_vinificacion', lazy=True))

    def __init__(self, variedad_uva_id, nombre_lote, estado_actual='En Curso'):
        self.variedad_uva_id = variedad_uva_id
        self.nombre_lote = nombre_lote
        self.estado_actual = estado_actual

    def serialize(self):
        return {
            'id': self.id,
            'variedad_uva_id': self.variedad_uva_id,
            'nombre_lote': self.nombre_lote,
            'fecha_inicio_proceso': self.fecha_inicio_proceso.isoformat(),
            'fecha_fin_proceso': self.fecha_fin_proceso.isoformat() if self.fecha_fin_proceso else None,
            'estado_actual': self.estado_actual,
            'variedad_uva_nombre': self.variedad_uva.nombre 
        }