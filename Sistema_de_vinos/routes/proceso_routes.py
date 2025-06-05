import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.db import db 
from models.variedad_uva import VariedadUva 
from models.proceso_vinificacion import ProcesoVinificacion 
from models.etapa_proceso import EtapaProceso 
import json
from datetime import datetime

proceso_vitivinicultura = Blueprint("proceso_vitivinicultura", __name__, url_prefix="/proceso")

@proceso_vitivinicultura.route('/')
def list_procesos():
    procesos = ProcesoVinificacion.query.all()
    return render_template('proceso/list_procesos.html', procesos=procesos)

@proceso_vitivinicultura.route('/new', methods=['GET', 'POST'])
def new_proceso():
    if request.method == 'POST':
        nombre_lote = request.form['nombre_lote']
        variedad_uva_id = request.form['variedad_id'] 
        
        existing_proceso = ProcesoVinificacion.query.filter_by(nombre_lote=nombre_lote).first()
        if existing_proceso:
            flash(f"Error: Ya existe un proceso con el nombre de lote '{nombre_lote}'. Por favor, elige un nombre diferente.", "danger")
            return redirect(url_for('proceso_vitivinicultura.new_proceso'))

        new_proceso_obj = ProcesoVinificacion(
            variedad_uva_id=variedad_uva_id,
            nombre_lote=nombre_lote,
            estado_actual='Recepción de Uva'
        )
        db.session.add(new_proceso_obj)
        db.session.flush() 
        
        peso_uva = request.form.get('peso_uva')
        estado_sanitario = request.form.get('estado_sanitario')
        observaciones_form = request.form.get('observaciones')

        parametros_recepcion = {
            'peso_uva': peso_uva,
            'estado_sanitario': estado_sanitario
        }

        new_etapa_recepcion = EtapaProceso(
            proceso_id=new_proceso_obj.id,
            tipo_etapa='Recepción de Uva',
            parametros_dict=parametros_recepcion,
            observaciones=observaciones_form if observaciones_form else f"Registro inicial del lote {nombre_lote}"
        )
        db.session.add(new_etapa_recepcion)
        db.session.commit()

        flash(f'Proceso "{nombre_lote}" iniciado y etapa de Recepción registrada!', 'success')
        return redirect(url_for('proceso_vitivinicultura.details_proceso', proceso_id=new_proceso_obj.id))
    
    variedades_disponibles = VariedadUva.query.all() 
    return render_template('proceso/new_proceso.html', variedades=variedades_disponibles)

@proceso_vitivinicultura.route('/<string:proceso_id>/recepcion', methods=['GET', 'POST'])
def recepcion_uva(proceso_id):
    proceso = ProcesoVinificacion.query.get_or_404(proceso_id)
    etapa = EtapaProceso.query.filter_by(proceso_id=proceso_id, tipo_etapa='Recepción de Uva').first()

    if request.method == 'POST':
        peso_uva = request.form['peso_uva']
        estado_sanitario = request.form['estado_sanitario']
        observaciones = request.form.get('observaciones')

        parametros_recepcion = {
            'peso_uva': peso_uva,
            'estado_sanitario': estado_sanitario
        }

        if etapa: 
            etapa.parametros_json = json.dumps(parametros_recepcion)
            etapa.observaciones = observaciones
            etapa.fecha_fin_etapa = datetime.utcnow() 
        else: 
            etapa = EtapaProceso(
                proceso_id=proceso_id,
                tipo_etapa='Recepción de Uva',
                parametros_dict=parametros_recepcion,
                observaciones=observaciones
            )
            db.session.add(etapa)
        
        proceso.estado_actual = 'Recepción de Uva (Completada)'
        db.session.commit()
        flash(f'Datos de Recepción de Uva para "{proceso.nombre_lote}" guardados.', 'success')
        return redirect(url_for('proceso_vitivinicultura.details_proceso', proceso_id=proceso_id))
    
    parametros = etapa.get_parametros() if etapa else {}
    return render_template('proceso/recepcion.html', proceso=proceso, etapa=etapa, parametros=parametros)

@proceso_vitivinicultura.route('/<string:proceso_id>/fermentacion', methods=['GET', 'POST'])
def fermentacion_alcoholica(proceso_id):
    proceso = ProcesoVinificacion.query.get_or_404(proceso_id)
    etapa = EtapaProceso.query.filter_by(proceso_id=proceso_id, tipo_etapa='Fermentación Alcohólica').first()

    parametros = etapa.get_parametros() if etapa else {}

    if request.method == 'POST':
        grados_brix = request.form['grados_brix']
        temperatura = request.form['temperatura']
        ph = request.form['ph']
        acidez = request.form['acidez']
        observaciones = request.form.get('observaciones')

        parametros_to_save = {
            'grados_brix': grados_brix,
            'temperatura': temperatura,
            'ph': ph,
            'acidez': acidez
        }

        if not etapa:
            etapa = EtapaProceso(
                proceso_id=proceso_id,
                tipo_etapa='Fermentación Alcohólica',
                parametros_dict=parametros_to_save,
                observaciones=observaciones
            )
            db.session.add(etapa)
            flash('Etapa de Fermentación Alcohólica registrada con éxito!', 'success')
        else:
            etapa.parametros_json = json.dumps(parametros_to_save)
            etapa.observaciones = observaciones
            flash('Etapa de Fermentación Alcohólica actualizada con éxito!', 'success')
        
        proceso.estado_actual = 'Fermentación Alcohólica (En curso)'
        
        db.session.commit()
        return redirect(url_for('proceso_vitivinicultura.details_proceso', proceso_id=proceso_id))
    
    return render_template('proceso/fermentacion.html', proceso=proceso, etapa=etapa, parametros=parametros)

@proceso_vitivinicultura.route('/<string:proceso_id>/crianza', methods=['GET', 'POST'])
def crianza_almacenamiento(proceso_id):
    proceso = ProcesoVinificacion.query.get_or_404(proceso_id)
    etapa = EtapaProceso.query.filter_by(proceso_id=proceso_id, tipo_etapa='Crianza / Almacenamiento').first()

    parametros = etapa.get_parametros() if etapa else {}

    if request.method == 'POST':
        tipo_recipiente = request.form['tipo_recipiente']
        tiempo_crianza = request.form['tiempo_crianza']
        observaciones = request.form.get('observaciones')

        parametros_to_save = {
            'tipo_recipiente': tipo_recipiente,
            'tiempo_crianza': tiempo_crianza
        }

        if etapa:
            etapa.parametros_json = json.dumps(parametros_to_save)
            etapa.observaciones = observaciones
            etapa.fecha_fin_etapa = datetime.utcnow()
        else:
            etapa = EtapaProceso(
                proceso_id=proceso_id,
                tipo_etapa='Crianza / Almacenamiento',
                parametros_dict=parametros_to_save,
                observaciones=observaciones
            )
            db.session.add(etapa)
        
        proceso.estado_actual = 'Crianza / Almacenamiento (Completada)'
        db.session.commit()
        flash(f'Datos de Crianza/Almacenamiento para "{proceso.nombre_lote}" guardados.', 'success')
        return redirect(url_for('proceso_vitivinicultura.details_proceso', proceso_id=proceso_id))
    
    return render_template('proceso/crianza.html', proceso=proceso, etapa=etapa, parametros=parametros)

@proceso_vitivinicultura.route('/<string:proceso_id>/embotellado', methods=['GET', 'POST'])
def embotellado(proceso_id):
    proceso = ProcesoVinificacion.query.get_or_404(proceso_id)
    etapa = EtapaProceso.query.filter_by(proceso_id=proceso_id, tipo_etapa='Embotellado').first()

    parametros = etapa.get_parametros() if etapa else {}

    if request.method == 'POST':
        fecha_embotellado = request.form['fecha_embotellado']
        cantidad_botellas = request.form['cantidad_botellas']
        observaciones = request.form.get('observaciones')

        parametros_to_save = {
            'fecha_embotellado': fecha_embotellado,
            'cantidad_botellas': cantidad_botellas
        }

        if etapa:
            etapa.parametros_json = json.dumps(parametros_to_save)
            etapa.observaciones = observaciones
            etapa.fecha_fin_etapa = datetime.utcnow()
        else:
            etapa = EtapaProceso(
                proceso_id=proceso_id,
                tipo_etapa='Embotellado',
                parametros_dict=parametros_to_save,
                observaciones=observaciones
            )
            db.session.add(etapa)

        proceso.estado_actual = 'Embotellado (Completado)'
        db.session.commit()
        flash(f'Datos de Embotellado para "{proceso.nombre_lote}" guardados.', 'success')
        return redirect(url_for('proceso_vitivinicultura.details_proceso', proceso_id=proceso_id))
    
    return render_template('proceso/embotellado.html', proceso=proceso, etapa=etapa, parametros=parametros)

@proceso_vitivinicultura.route('/<string:proceso_id>')
def details_proceso(proceso_id):
    proceso = ProcesoVinificacion.query.get_or_404(proceso_id)
    etapas = EtapaProceso.query.filter_by(proceso_id=proceso_id).order_by(EtapaProceso.fecha_inicio_etapa).all()
    return render_template('proceso/details_proceso.html', proceso=proceso, etapas=etapas)

@proceso_vitivinicultura.route('/almacenamiento_search', methods=['GET'])
def almacenamiento_search():
    variedad_filtro_id = request.args.get('variedad_id')
    recipiente_filtro = request.args.get('recipiente')

    query = EtapaProceso.query.filter_by(tipo_etapa='Crianza / Almacenamiento')

    if variedad_filtro_id:
        query = query.join(ProcesoVinificacion).filter(ProcesoVinificacion.variedad_uva_id == variedad_filtro_id)
    
    if recipiente_filtro:
        query = query.filter(EtapaProceso.parametros_json.like(f'%{"\"tipo_recipiente\": \"" + recipiente_filtro + "\""}%'))

    resultados = query.all()

    variedades_disponibles = VariedadUva.query.all()

    return render_template('proceso/almacenamiento_search.html', 
                            resultados=resultados, 
                            variedades_disponibles=variedades_disponibles,
                            variedad_filtro_id=variedad_filtro_id, 
                            recipiente_filtro=recipiente_filtro)



