from flask import render_template, redirect, url_for, flash, request, Response, jsonify
from HRrequest import app, database, bcrypt
from HRrequest.forms import FormLogin, FormCriarConta
from HRrequest.models import Usuario, RequestVacation, Employees
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
import pandas as pd
from io import BytesIO


@app.route('/')
@login_required
def home():
    return render_template('home.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/Consult', methods=['GET', 'POST'])
@login_required
def consult():
    requisitions = RequestVacation.query.all()
    return render_template('consult.html', requisitions=requisitions)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash('Login feito com sucesso', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'E-mail ou Senha incorretos', 'alert-danger')
    return render_template('login.html', form_login=form_login)


@app.route('/manager_user', methods=['GET', 'POST'])
def criarconta():
    form_criarconta = FormCriarConta()
    usuarios_cadastrados = Usuario.query.all()
    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_cript,createdate=datetime.now())
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta criada com sucesso', 'alert-success')
        return redirect(url_for('criarconta'))
    return render_template('manager_user.html', form_criarconta=form_criarconta, usuarios_cadastrados=usuarios_cadastrados)

@app.route('/logout')
@login_required
def Sair():
    logout_user()
    return redirect(url_for('home'))


@app.route('/request_vac', methods=['GET', 'POST'])
@login_required
def request_vac():

    id_employee = request.form.get("txtID", "")
    nome = request.form.get("txtName", "")
    funcao = request.form.get("txtFuncao", "")
    centrodecusto = request.form.get("txtCentrodeCusto", "")
    datalimite = request.form.get("txtDatalimite", "")
    cobertura = request.form.get("txttipocobertura", "")
    datainicio = request.form.get("txtDatainicio", "")
    datafim = request.form.get("txtDatafim", "")
    qtddias = request.form.get("txtQuantDias", "")
    dataretorno = request.form.get("txtDataretorno", "")
    abono = request.form.get("txtQtdabono", "0")
    decimoterceiro = request.form.get("txtdecimoterceiro", "")
    dataembarque = request.form.get("txtDataemb", "")
    nomecobertura = request.form.get("txtNomeCobertura", "")
    funcaocobertura = request.form.get("txtFuncaoCobertura", "")

    error = []

    if request.method == 'POST':
        try:
            datainicio = datetime.strptime(datainicio, '%Y-%m-%d')
            datafim = datetime.strptime(datafim, '%Y-%m-%d')
            dataembarque = datetime.strptime(dataembarque, '%Y-%m-%d')
            if int(qtddias) > 30:
                error.append('Não é permitido solicitar mais de 30 dias de férias.')
            if int(qtddias) < 5:
                error.append('Não é permitido solicitar menos de 4 dias de férias.')
            if int(abono) > 10:
                error.append('Não é permitido vender mais de 10 dias de férias.')
            if int(abono)+int(qtddias) > 30:
                error.append('Verificar quantidade de dias de férias e/ou abono.')
            if str(decimoterceiro) == 'Selecione sim ou Não':
                error.append('Selecione sim ou não para antecipação do 13º salário.')
            if datainicio <= datetime.now():
                error.append('Não é permitido cadastrar férias retroativa, verifique a data de inicio.')
            if int(datainicio.month) in(1,11,12) and decimoterceiro == 'Sim':
                error.append('Não é permitido antecipar a 1ª Parcela do 13º no mês solicitado.')
            if not error:

                cadastras_ferias = RequestVacation(id_employee=id_employee, name=nome, position=funcao, costcenter=centrodecusto, dtlimite=datalimite, typecoverage=cobertura, dtstart=datainicio, dtend=datafim, qtdday=qtddias, dtreturn=dataretorno, qtdsell=abono, advancesalary=decimoterceiro, dtemb=dataembarque, namecoverage=nomecobertura, positioncoverage=funcaocobertura, createdate=datetime.now(), createby=current_user.username, status='Aguardando aprovação')
                database.session.add(cadastras_ferias)
                database.session.commit()
                flash('Férias lançada com sucesso', 'alert-success')
                return redirect(url_for('request_vac'))
            else:
                for msg in error:
                    flash(msg, 'alert-danger')
        except ValueError:
            flash('Erro ao processar os dados. Verifique os valores inseridos.', 'alert-danger')
    return render_template('request_vac.html',
                           id_employee=id_employee,
                           nome=nome,
                           funcao=funcao,
                           Centrodecusto=centrodecusto,
                           Datalimite=datalimite,
                           cobertura=cobertura,
                           datainicio=datainicio,
                           datafim=datafim,
                           qtddias=qtddias,
                           dataretorno=dataretorno,
                           abono=abono,
                           dtemb=dataembarque,
                           nomecobertura=nomecobertura,
                           funcaocobertura=funcaocobertura)

@app.route('/export_excel')
@login_required
def export_excel():
    requests = RequestVacation.query.all()
    data = {
        'id': [r.id for r in requests],
        'name': [r.name for r in requests],
        'position': [r.position for r in requests],
        'costcenter': [r.costcenter for r in requests],
        'typecoverage': [r.typecoverage for r in requests],
        'namecoverage': [r.namecoverage for r in requests],
        'positioncoverage': [r.positioncoverage for r in requests],
        'dtlimite': [r.dtlimite for r in requests],
        'dtstart': [r.dtstart for r in requests],
        'dtend': [r.dtend for r in requests],
        'dtreturn': [r.dtreturn for r in requests],
        'qtdday': [r.qtdday for r in requests],
        'qtdsell': [r.qtdsell for r in requests],
        'advancesalary': [r.advancesalary for r in requests],
        'status': [r.status for r in requests],
        'createby': [r.createby for r in requests],
        'createdate': [r.createdate for r in requests]
    }
    df = pd.DataFrame(data)

    # Criação do buffer e exportação para Excel
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    buffer.seek(0)

    # Configuração da resposta
    return Response(
        buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-Disposition": "attachment;filename=dados.xlsx"}
    )

@app.route('/Consult/<RequestVacation_id>/excluir', methods=['POST'])
@login_required
def excluir_requisition(RequestVacation_id):
    requisition = RequestVacation.query.get(RequestVacation_id)
    if current_user.username == requisition.createby:
        database.session.delete(requisition)
        database.session.commit()
        flash('Requisição excluida com sucesso','alert-danger')
        return redirect(url_for('consult'))
    else:
        abort(403)


@app.route('/feriassolicitadas')
@login_required
def msg_conf():
    return render_template('msgconfirmacao.html')

@app.route('/Employees_folha')
@login_required
def employees_folha():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Número de registros por página
    start = (page - 1) * per_page
    end = start + per_page
    items = Employees.query.all()
    total_pages = (len(items) + per_page - 1) // per_page
    items = items[start:end]
    return render_template('Employees_folha.html', items=items, total_pages=total_pages, page=page)


@app.route('/Employees_folha', methods=['POST'])
@login_required
def upload_file():
    database.session.query(Employees).delete()
    database.session.commit()
    if 'file' not in request.files:
        flash('Nenhum arquivo selecionado')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('Nenhum arquivo selecionado')
        return redirect(request.url)

    if file and file.filename.endswith('.xlsx'):
        df = pd.read_excel(file)

        # Processar e salvar dados no banco de dados
        for index, row in df.iterrows():
            record = Employees(id_employee=row['id_employee'],
                               name=row['name'],
                               position=row['position'],
                               costcenter=row['costcenter'],
                               limitedate=datetime.strptime(row['limitedate'],"%d/%m/%Y").date(),
                               acperiod=row['Acperiod'],
                               balance=row['Balance'],
                               createdate=datetime.now())
            database.session.add(record)
            database.session.commit()

        flash('Arquivo importado com sucesso!','alert-success')
        return redirect(url_for('employees_folha'))

    flash('Formato de arquivo não suportado')
    return redirect(request.url)

@app.route('/buscar-funcionario', methods=['GET'])
@login_required
def buscar_funcionario():
    id_funcionario = request.args.get('id')
    funcionario = Employees.query.filter_by(id_employee=id_funcionario).first()

    if funcionario:
        def formatar_data(data):
            return data.strftime('%d/%m/%Y') if data else ''

        return jsonify({
            'nome': funcionario.name,
            'funcao': funcionario.position,
            'centrodecusto': funcionario.costcenter,
            'periodoaquisitivo': funcionario.acperiod,
            'datalimite': formatar_data(funcionario.limitedate)
        })
    else:
        return jsonify({'error': 'Funcionário não encontrado'}), 404