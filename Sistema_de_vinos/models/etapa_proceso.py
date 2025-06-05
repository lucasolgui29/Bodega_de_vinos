import uuid
from models.db import db
from datetime import datetime
import json 

class EtapaProceso(db.Model):
    __tablename__ = 'etapa_proceso'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proceso_id = db.Column(db.String(36), db.ForeignKey('proceso_vinificacion.id'), nullable=False)
    tipo_etapa = db.Column(db.String(50), nullable=False)
    fecha_inicio_etapa = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_fin_etapa = db.Column(db.DateTime, nullable=True)
    parametros_json = db.Column(db.Text, nullable=True)
    observaciones = db.Column(db.String(500), nullable=True)

    proceso_vinificacion = db.relationship('ProcesoVinificacion', 
                                         backref=db.backref('etapas_del_proceso', lazy=True))

    def __init__(self, proceso_id, tipo_etapa, parametros_dict=None, observaciones=None):
        self.proceso_id = proceso_id
        self.tipo_etapa = tipo_etapa
        self.parametros_json = json.dumps(parametros_dict) if parametros_dict else None
        self.observaciones = observaciones

    def get_parametros(self):
        return json.loads(self.parametros_json) if self.parametros_json else {}


    def serialize(self):
        return {
            'id': self.id,
            'proceso_id': self.proceso_id,
            'tipo_etapa': self.tipo_etapa,
            'fecha_inicio_etapa': self.fecha_inicio_etapa.isoformat(),
            'fecha_fin_etapa': self.fecha_fin_etapa.isoformat() if self.fecha_fin_etapa else None,
            'parametros': self.get_parametros(),
            'observaciones': self.observaciones
        }
    
