import pandas as pd
from flask import Flask, jsonify, request
import uuid
from datetime import datetime
from sqlalchemy import create_engine
import socket
import json
import bibtexparser

'''
Exemplo de chamadas:
http://127.0.0.1:5000/create
http://127.0.0.1:5000/search -> Pede o token
http://127.0.0.1:5000/search?code=XXXX -> Pede string de busca
http://127.0.0.1:5000/search?code=XXXX&string={"title":"like 'JOURNAL%'"} -> Código invalido

http://127.0.0.1:5000/search?code=e597af72-c8d5-4f42-a1b2-7eea95002a83&string={"`rank`":" = 425"} -> REtorna 1
http://127.0.0.1:5000/search?code=e597af72-c8d5-4f42-a1b2-7eea95002a83&string={"`rank`":" > 32950"} -> Retorna 2
http://127.0.0.1:5000/search?code=e597af72-c8d5-4f42-a1b2-7eea95002a83&string={"title":" like 'JOURNAL OF HA%%'"} -> Retorna 12 

Pode usar também dois valores no json

http://127.0.0.1:5000/search?code=e597af72-c8d5-4f42-a1b2-7eea95002a83&string={"total_cities":" > 3500", "`rank`": "< 100"}

POST: 
http://127.0.0.1:5000/store

code:
0ba10cd3-e47c-401f-a154-8ebebc323834

data:
@INPROCEEDINGS{8332632,
title={HELIO LEAL},
abstract={bla bla bla bla},
total_cities={10}
}

data2:
@INPROCEEDINGS{8332632,
title={TSS LEAL},
abstract={bla bla bla bla},
total_cities={10}
}

'''

# inicializar o flask
app = Flask(__name__)

# Construir as funcionalidades
@app.route('/')
def homepage():
    return 'A Api está no ar'

# Endpoint
@app.route('/pegarvendas')
def pegarvendas():
    total_vendas = 5000.680
    # Criar um dicionário python.
    resposta = {'total_vendas': total_vendas}
    return jsonify(resposta)

# Cria uma nova busca científica
@app.route('/create')
def create():  
    myUUID = uuid.uuid4()
    now = datetime.now()
    ip=socket.gethostbyname(socket.gethostname())
    data = [['api',myUUID,now,ip]]
    
    df = pd.DataFrame(data,columns=['type','code','datetime','ip'])

    print('mysql search_codes table created.')
    db_connection = 'mysql+pymysql://root:root@localhost:3306/impacta'
    db_connection = create_engine(db_connection)
    df.to_sql(con=db_connection, name='search_codes', if_exists='append', index=False)

    response = {'code': myUUID}
    return jsonify(response)

@app.route('/search', methods=['GET'])
def search():
    args = request.args
    code = args.get('code')
    
    if not code:
        return 'Please inform a code request like -> url:port/search?code=your code'

    query_string = args.get('string')

    if not query_string:
        return 'Please inform a string for a search -> url:port/search?code=your code&string=search'

    # Identify if customer generated a code.
    sqlEngine       = create_engine('mysql+pymysql://root:root@localhost:3306/impacta')
    dbConnection    = sqlEngine.connect()
    frame           = pd.read_sql("select * from impacta.search_codes where code = '" + code + "'", dbConnection)

    pd.set_option('display.expand_frame_repr', False)

    if frame.empty:
        return 'Your code is invalid, please set a valid code!'

    # Transform parameter into json
    j = json.loads(query_string)

    where = '1=1 '
    for key, value in j.items():
        where = where + " and " + key + value

    print("Query to be executed: select * from impacta.data where " + where)   

    frame_res = pd.read_sql("select * from impacta.data where " + where, dbConnection)
    
    print('query executada com sucesso')
    print(frame_res)

    dbConnection.close()

    ret = frame_res.to_json(orient='records')

    return jsonify(ret)

@app.route('/store', methods=['POST'])
def store_bibtex():
    code = request.form.get('code')

    if not code:
        return 'Please inform a code request like -> url:port/search?code=your code'

    # Identify if customer generated a code.
    sqlEngine       = create_engine('mysql+pymysql://root:root@localhost:3306/impacta')
    dbConnection    = sqlEngine.connect()
    frame           = pd.read_sql("select * from impacta.search_codes where code = '" + code + "'", dbConnection)

    pd.set_option('display.expand_frame_repr', False)

    if frame.empty:
        return 'Your code is invalid, please set a valid code!'


    data = request.form.get('data')
    print(data)   

    if not data:
        return 'Data is empty'

    bib_database = bibtexparser.loads(data)
    
    bib_df = pd.DataFrame.from_records(bib_database.entries)

    #Correct columns position based on pattern.
    columns= ["title","abstract","total_cities"]

    bib_df=bib_df.reindex(columns=columns)

    print('bib_df')
    print(bib_df)

    print('mysql insertion started.')
    db_connection = 'mysql+pymysql://root:root@localhost:3306/impacta'
    db_connection = create_engine(db_connection)
    bib_df.to_sql(con=db_connection, name='data', if_exists='append', index=False)

    return "sucess"





# Rodar API
app.run()