import os
from flask import Blueprint, render_template, request, redirect, url_for, flash 
from werkzeug.utils import secure_filename
from models.db import db
from models.variedad_uva import VariedadUva

variedad_uva = Blueprint("variedad_uva", __name__, url_prefix="/variedades_uva") 


UPLOAD_FOLDER = 'static/images/variedad_uva' 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@variedad_uva.route('/')
def get_variedades():
    variedades_list = VariedadUva.query.all()
    return render_template('variedad_uva/variedades.html', variedades=variedades_list)

@variedad_uva.route('/new', methods=["GET", "POST"]) 
def add_variedad():
    if request.method=="POST":
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        color = request.form['color']
        region = request.form['region']
        image_file = request.files.get('image')
        filename = None

        if image_file and image_file.filename != '':
            if allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename) 
                image_path = os.path.join(UPLOAD_FOLDER, filename) 
                image_file.save(image_path) 
            else:
                flash('Formato de imagen no permitido. Solo png, jpg, jpeg, gif.', 'danger')
                return redirect(request.referrer) 
            
        new_variedad = VariedadUva(
            nombre=nombre,
            descripcion=descripcion,
            color=color,
            region=region,
            ruta_foto=filename
        )

        db.session.add(new_variedad)
        db.session.commit()

        flash('Variedad de uva ({nombre}) agregada', 'success')
        return redirect(url_for('variedad_uva.get_variedades')) 
    else:
        return render_template("variedad_uva/add_variedad.html")    

@variedad_uva.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit_variedad(id):
    variedad = VariedadUva.query.get_or_404(id)
    
    if request.method == 'POST':
        variedad.nombre = request.form['nombre']
        variedad.descripcion = request.form['descripcion']
        variedad.color = request.form['color']
        variedad.region = request.form['region']
        image_file = request.files.get('ruta_foto')
        if image_file and image_file.filename != '':
            if allowed_file(image_file.filename):
                if variedad.ruta_foto: 
                    old_image_path = os.path.join(UPLOAD_FOLDER, variedad.ruta_foto)
                    if os.path.exists(old_image_path): 
                        os.remove(old_image_path)

                filename = secure_filename(image_file.filename)
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                image_file.save(image_path)
                variedad.ruta_foto = filename
            else:
                flash('Formato de imagen no permitido. Solo png, jpg, jpeg, gif.', 'danger')
                return redirect(request.referrer)

        db.session.commit()
        flash('Variedad de uva editada exitosamente!', 'success')
        return redirect(url_for('variedad_uva.get_variedades'))
    else: 
        return render_template('variedad_uva/edit_variedad.html', variedad=variedad)
    
@variedad_uva.route('/delete/<string:id>', methods=['POST'])
def delete_variedad(id):
    variedad = VariedadUva.query.get_or_404(id)
    if variedad.ruta_foto:
        image_path = os.path.join(UPLOAD_FOLDER, variedad.ruta_foto)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(variedad)
    db.session.commit()
    flash('Variedad de uva eliminada!', 'success')
    return redirect(url_for('variedad_uva.get_variedades'))