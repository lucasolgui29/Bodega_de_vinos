import os
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from werkzeug.utils import secure_filename
from models.db import db
from models.vino_producto import VinoProducto
from models.proceso_vinificacion import ProcesoVinificacion
from models.variedad_uva import VariedadUva
import json 
import os

vino_productos = Blueprint("vino_productos", __name__, url_prefix="/vinos")

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@vino_productos.route('/')
def get_vinos():
    vinos_list = VinoProducto.query.all()
    return render_template('vinos/vinos.html', vinos=vinos_list)

@vino_productos.route('/new', methods=["GET", "POST"])
def add_vino():
    if request.method=="POST":
        nombre_vino = request.form["nombre_vino"]
        precio = request.form["precio"]
        proceso_id = request.form["proceso_id"]
        
        proceso = ProcesoVinificacion.query.get(proceso_id)
        if not proceso or proceso.estado_actual != 'Embotellado (Completado)':
            flash('El lote seleccionado no existe o no ha completado la etapa de embotellado.', 'danger')
            return redirect(request.referrer)

        image_file = request.files.get('image')
        filename = None

        if image_file and image_file.filename != '':
            if allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    image_file.save(image_path)
                except Exception as e:
                    flash(f'Error al guardar la imagen: {e}', 'danger')
                    return redirect(request.referrer)
            else:
                flash('Formato de imagen no permitido. Solo png, jpg, jpeg, gif.', 'danger')
                return redirect(request.referrer)

        new_vino = VinoProducto(
            nombre_vino=nombre_vino,
            precio=float(precio),
            imagen=filename,
            proceso_id=proceso_id
        )

        db.session.add(new_vino)
        db.session.commit()
        
        flash(f"El vino '{nombre_vino}' fue agregado exitosamente a la lista de productos.", "success")
        return redirect(url_for('vino_productos.get_vinos')) 
    else:
        procesos_completados = ProcesoVinificacion.query.filter_by(estado_actual='Embotellado (Completado)').all()
        return render_template("vinos/add_vino.html", procesos=procesos_completados)

@vino_productos.route('/delete/<string:id>', methods=['POST'])
def delete_vino(id):
    vino = VinoProducto.query.get_or_404(id)
    if vino.imagen:
        image_path = os.path.join(UPLOAD_FOLDER, vino.imagen)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(vino)
    db.session.commit()
    flash('Vino eliminado exitosamente de la lista de productos!', 'success')
    return redirect(url_for('vino_productos.get_vinos'))

@vino_productos.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit_vino(id):
    vino = VinoProducto.query.get_or_404(id)
    procesos_completados = ProcesoVinificacion.query.filter_by(estado_actual='Embotellado (Completado)').all()

    if request.method == 'POST':
        vino.nombre_vino = request.form["nombre_vino"]
        vino.precio = float(request.form["precio"])
        new_proceso_id = request.form["proceso_id"]

        if new_proceso_id != vino.proceso_id:
            proceso = ProcesoVinificacion.query.get(new_proceso_id)
            if not proceso or proceso.estado_actual != 'Embotellado (Completado)':
                flash('El nuevo lote seleccionado no existe o no ha completado la etapa de embotellado.', 'danger')
                return redirect(request.referrer)
            vino.proceso_id = new_proceso_id

        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            if allowed_file(image_file.filename):
                if vino.imagen:
                    old_image_path = os.path.join(UPLOAD_FOLDER, vino.imagen)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    image_file.save(image_path)
                    vino.imagen = filename
                except Exception as e:
                    flash(f'Error al guardar la nueva imagen: {e}', 'danger')
                    return redirect(request.referrer)
            else:
                flash('Formato de imagen no permitido. Solo png, jpg, jpeg, gif.', 'danger')
                return redirect(request.referrer)
        
        db.session.commit()
        flash(f"El vino '{vino.nombre_vino}' fue actualizado exitosamente.", "success")
        return redirect(url_for('vino_productos.get_vinos'))
    
    return render_template("vinos/edit_vino.html", vino=vino, procesos=procesos_completados)














