from flask import Flask
from flask import render_template
from flask import request
from flask import flash
import os
from flask import redirect, url_for
from wtforms.validators import NoneOf
from utils import isUsernameValid, isEmailValid, isPasswordValid
import yagmail as yagmail
from forms import Registro_usuario, Login, Registrar_cita, Detalle_cita
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
    

@app.route('/')
@app.route('/index/')
def index():
    form = Registro_usuario( request.form )    
    return render_template('index.html')


@app.route('/detalle-cita')
@app.route('/detalle-cita/<int:id>/')
@app.route('/login/perfil/detalle-cita/<int:id>/')
def detalle_cita(id=0):
    form = Detalle_cita( request.form )
    #idu = request.args.get('id_paciente')
    #ido = form.id_paciente.data
    pacientes = sql_select_pacientes()
    citas = sql_select_citas()
    medicos = sql_select_medicos()
    especialidades = sql_select_especialidad()
    pacientes = [ paciente for paciente in pacientes if paciente[0] == id ]
    citas = [ cita for cita in citas if cita[6] == id ]
    cita_especifica = citas[0]
    medicos = [ medico for medico in medicos if medico[1] == cita_especifica[7]]#no esta leyendo el cita_especifica
    perfil_medico = medicos[0]
    especialidades = [ especialidad for especialidad in especialidades if especialidad[0] == perfil_medico[3] ]
    if len(pacientes)>0 and len(citas)>0 and len(medicos)>0 and len(especialidades)>0:
        perfil_paciente = pacientes[0]
        especialidad_medico = especialidades[0]
        #cita_especifica = citas[0]
        #perfil_medico = medicos[0]
        return render_template('detalle_cita.html', form=form, perfil_paciente=perfil_paciente, cita_especifica=cita_especifica, perfil_medico=perfil_medico, especialidad_medico=especialidad_medico)
    return render_template('detalle_cita.html', form=form, perfil_paciente=None, cita_especifica=None, perfil_medico=None, especialidad_medico=None)



@app.route('/login/perfil/<int:id>/')
@app.route('/perfil/<int:id>/')
def perfil(id=0):
    medicos = sql_select_medicos()
    pacientes = sql_select_pacientes()

    medicos = [ medico for medico in medicos if medico[1] == id ]
    pacientes = [ paciente for paciente in pacientes if paciente[0] == id ]
    if len(medicos)>0:
        perfil_medico = medicos[0] 
        return render_template('perfil.html', perfil_medico=perfil_medico, perfil_paciente=None)
    if len(pacientes)>0:
        perfil_paciente = pacientes[0]
        return render_template('perfil.html', perfil_paciente=perfil_paciente, perfil_medico=None )
    else:
        return render_template('perfil.html', medicos=medicos, pacientes=pacientes)


@app.route('/registrar-cita/', methods=['GET','POST'])
@app.route('/registrar-cita/<int:id>/', methods=['GET', 'POST'])
def registrar_cita(id=0):
    form = Registrar_cita( request.form )
    if request.method == 'POST':
        motivo = request.form['motivo']
        descripcion = request.form['descripcion']
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        estado = request.form['estado']
        id_paciente = request.form['id_paciente']
        id_medico = request.form['id_medico']
        direccion = request.form['direccion']
        ciudad = request.form['ciudad']
        celular = request.form['celular']
        vez = request.form['vez']
        especialidad = request.form['especialidad']
        comentarios = request.form['comentarios']
        valoracion = request.form['valoracion']

        insert_registro_cita(motivo, descripcion, date, start_time, end_time, estado, id_paciente, id_medico, direccion, ciudad, celular, vez, especialidad, comentarios, valoracion)
    return render_template('registrar_citas.html', form=form)



@app.route('/login/', methods=['GET','POST'])
def method_name():
    
    form = Login( request.form )
    #try:
    if request.method == 'POST':
        t_usuario_login = request.form['t_usuario_login']
        t_id_login = request.form['t_id_login']
        no_id_login = request.form['no_id_login']
        password_login = request.form['password_login']

        flash('Bienvenido')
        if t_usuario_login == "Administrador":
            return redirect( url_for( 'administrador' ) )
        if t_usuario_login == "Medico":
            return redirect('perfil/{}'.format(no_id_login) )#'perfil/{}'.format(no_id_login)
        if t_usuario_login == "Paciente":
            return redirect( 'perfil/{}'.format(no_id_login))
    return render_template('login.html', form=form)




@app.route('/registro_usuario/', methods=['GET','POST'])
def registro_usuario():
    form = Registro_usuario( request.form )
    try:
        if request.method == 'POST':   
            tipo_usuario = request.form['tipo_usuario']
            tipo_id = request.form['tipo_id']
            usuario = request.form['usuario']
            no_id = request.form['no_id']
            email = request.form['email']
            password = request.form['password']

            error = None
            if not isUsernameValid(usuario):
                error = "El usuario debe ser alfanumerico o incluir solo '.','_','-'"
                flash(error)
            if not isEmailValid(email):
                error = "Correo invalido"
                flash(error)
            if not isPasswordValid(password):
                error = "La contraseña debe contener al menos una minúscula, una mayúscula, un número y 8 caracteres"
                flash(error)
            if error is not None:
                return render_template('registro_usuario.html',form=form)

            else:

                yag = yagmail.SMTP('pruebas.programacion.test@gmail.com', 'Femizoo.1234') 
                yag.send(to=email, subject='Activa tu cuenta',
                    contents='Bienvenido, usa este link para activar tu cuenta ')
                flash('Revisa tu correo para activar tu cuenta')
                insert_registro_usuario(tipo_id, no_id, email, password, usuario, tipo_usuario)
                form=Registro_usuario()
                return render_template('registro_usuario.html',form=form)

        return render_template('registro_usuario.html',form=form)
    except:
        flash("Ha ocurrido un error, intentalo de nuevo")    
        return render_template('registro_usuario.html')

@app.route('/administrador', methods=['GET','POST'])
def administrador():
    return render_template('dashboard.html')

@app.route('/lista-citas', methods=['GET', 'POST'])
def citas():
    return render_template('list_citas.html')

@app.route('/resultado-busqueda', methods=['GET', 'POST'])
@app.route('/detalle.cita/<int:id>/')
def resultado(id=0):
    return render_template('Resultadodebusqueda.html')


#funciones 

def sql_connection():
    try:
        conn = sqlite3.connect('dbClinica.db')
        print("¡Conexión OK!")
        return conn
    except Error:
        print(Error)

def insert_registro_usuario(tipo_id, num_doc, email, password, nombre_ape, tipo_persona):
    sql = "INSERT INTO pacientes (tipo_doc, num_doc, email, password, nombre_ape, tipo_persona) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(tipo_id, num_doc, email, password, nombre_ape, tipo_persona)
    conn = sql_connection()
    cursoObj = conn.cursor()
    cursoObj.execute(sql)
    conn.commit()
    conn.close()

def insert_registro_cita(motivo_cita, descripcion, fecha, hora_cita, horario_salida, estado, id_paciente, idMedico, direccion, ciudad, celular, first_time, especialidad_consulta, comentarios, valoracion):
    sql = "INSERT INTO Citas (motivo_cita, descripcion, fecha, hora_cita, horario_salida, estado, id_paciente, idMedico, direccion, ciudad, celular, first_time, especialidad_consulta, comentarios, valoracion) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(motivo_cita, descripcion, fecha, hora_cita, horario_salida, estado, id_paciente, idMedico, direccion, ciudad, celular, first_time, especialidad_consulta, comentarios, valoracion)
    conn = sql_connection()
    cursoObj = conn.cursor()
    cursoObj.execute(sql)
    conn.commit()
    conn.close()

def sql_select_medicos():
    sql = "SELECT nombre, num_doc, email, especialidad FROM medico"
    conn = sql_connection()
    cursorObj = conn.cursor()
    cursorObj.execute(sql)
    medicos = cursorObj.fetchall()
    return medicos

def sql_select_pacientes():
    sql = "SELECT num_doc, email, nombre_ape FROM pacientes"
    conn = sql_connection()
    cursorObj = conn.cursor()
    cursorObj.execute(sql)
    pacientes = cursorObj.fetchall()
    return pacientes

def sql_select_citas():
    sql="SELECT id, motivo_cita, fecha, hora_cita, horario_salida, estado, id_paciente, idMedico, direccion, ciudad, celular, first_time, especialidad_consulta FROM Citas"
    conn = sql_connection()
    cursorObj = conn.cursor()
    cursorObj.execute(sql)
    citas = cursorObj.fetchall()
    return citas

def sql_select_especialidad():
    sql = "SELECT id, nombre FROM especialidad_medico"
    conn = sql_connection()
    cursorObj = conn.cursor()
    cursorObj.execute(sql)
    especialidades = cursorObj.fetchall()
    return especialidades