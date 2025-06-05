from flask import Flask, blueprints, render_template
from config.config import DATABASE_CONNECTION_URI
from models.db import db
from routes.vino_productos_routes import vino_productos
from routes.variedad_uva_routes import variedad_uva
from routes.about import about
from routes.proceso_routes import proceso_vitivinicultura
from flask_migrate import Migrate

app= Flask(__name__)
app.secret_key="clave_secreta"
app.register_blueprint(vino_productos,url_prefix="/vinos")
app.register_blueprint(variedad_uva,url_prefix="/variedades_uva")
app.register_blueprint(proceso_vitivinicultura)
app.register_blueprint(about)



app.config["SQLALCHEMY_DATABASE_URI"]= DATABASE_CONNECTION_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False


db.init_app(app)
migrate = Migrate(app, db)

@app.route("/")
def index():
    return render_template("layaut.html")


with app.app_context():
    from models.vino_producto import VinoProducto
    from models.proceso_vinificacion import ProcesoVinificacion 
    from models.variedad_uva import VariedadUva 
    #db.drop_all()  esto se descomenta cuando se quiere recrear la base de datos, se debe hacer al principio   
    db.create_all()




if __name__ == '__main__':
    app.run(debug=True)

