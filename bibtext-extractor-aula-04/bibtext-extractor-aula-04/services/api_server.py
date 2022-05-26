import pandas as pd
from flask import Flask, jsonify, request
import uuid
from datetime import datetime
from sqlalchemy import create_engine
import socket
import json

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

# http://127.0.0.1:5000/search?code=c19272e3-454d-47a5-ab1d-61f2002331f8&string={%22rank%22:%20%22%20%3E%203600%22,%20%22totel%22:%20%22%20=%2058.477%22,%22title%22:%20%22=%20%27helio%27%20%22}
@app.route('/search', methods=['GET'])
def search():
    args = request.args
    code = args.get('code')
    
    if not code:
        return 'Please inform a code request like -> url:port/search?code=your code'

    query_string = args.get('string')

    if not query_string:
        return 'Please inform a string for a search -> url:port/search?code=your code&string=search'

    sqlEngine       = create_engine('mysql+pymysql://root:root@localhost:3306/impacta')
    dbConnection    = sqlEngine.connect()
    frame           = pd.read_sql("select * from impacta.search_codes where code = '" + code + "'", dbConnection)

    pd.set_option('display.expand_frame_repr', False)

    if frame.empty:
        return 'Your code is invalid, please set a valid code!'

    j = json.loads(query_string)

    where = '1=1 '
    for key, value in j.items():
        where = where + " and " + key + value

    print(where)

    frame_res = pd.read_sql("select * from impacta.data where " + where, dbConnection)
    
    print(frame_res['rank'])

    dbConnection.close()

    #response = {'rank': frame_res['rank'], 'title': frame_res['title']} #, 'total_cities': frame_res['total_cities'], 'type_publication_x': frame_res['type_publication_x'], 'jcr_value': frame_res['jcr_value'], 'scimago_value': frame_res['scimago_value'], 'author': frame_res['author'], 'keywords': frame_res['keywords'], 'abstract': frame_res['abstract'], 'year': frame_res['year'], 'type_publication_y': frame_res['type_publication_y'], 'doi': frame_res['doi']}
    #return response

    response = {'code': code, 'string': query_string}
    return jsonify(response)

# Rodar API
app.run()