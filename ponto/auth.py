import functools
from flask import (Blueprint,flash,g,redirect,render_template,request,session,url_for)
from werkzeug.security import check_password_hash,generate_password_hash
from pymongo import MongoClient
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        cpf=request.form['cpf']
        senha=request.form['senha']
        cliente = MongoClient('mongodb://localhost:27017/') #cria a conexão com o mongodb
        db = cliente['registro-ponto'] #acessa o banco de dados no mongodb
        funcionarios = db['Funcionario'] #acessa a tabela/coleção Funcionario no mongodb
        print(funcionarios.)
        error=None

        if funcionarios.count_documents == 0: #checa se a tabela Funcionario está vazia
            print('Não temos nenhum funcionário, estaremos criando o primeiro.')
            documento_padrao = {'nome':'admin','cpf':'123.456.789-09','senha':generate_password_hash('123456')}
            funcionarios.insert_one(documento_padrao)
            print('Criado funcionário padrão')

        if cpf is None:
            error='Dado cpf necessário'
        elif not senha:
            error='Dado senha necessário'

        if error is None:
            documento = funcionarios.find_one({ #pesquisa o cpf e a senha se estão no banco.
                '$and':[
                    {'cpf':cpf},
                    {'senha':check_password_hash('senha',senha)}
                ]
            })

            if documento is not None:
                print('Login aceito!')
                session.clear()
                session['cpf']=documento['cpf']
                return redirect(url_for('index'))
            else:
                error = 'Dados incorretos, cpf ou senha inválidos!'
            flash(error)
    return render_template('auth/login.html')

@bp.before_app_request
def carrega_usuario_logado():
    cpf=session.get('cpf')
    if cpf is None:
        g.cpf=None
    else:
        cliente = MongoClient('mongodb://localhost:27017/') #cria a conexão com o mongodb
        db = cliente['registro-ponto'] #acessa o banco de dados no mongodb
        funcionarios = db['Funcionario'] #acessa a tabela Funcionario no mongodb
        documento = funcionarios.find_one({'cpf',session.get('cpf')})
        g.cpf=documento

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.cpf is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    return wrapped_view
