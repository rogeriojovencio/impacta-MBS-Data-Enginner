import bibtexparser
import pandas as pd
import json
import yaml
import requests
import pymysql
import sqlalchemy
from sqlalchemy import create_engine



#Read a yaml file.
def read_yaml(name):
    with open(name+'.yaml') as file:
        try:
            databaseConfig = yaml.safe_load(file)   
            return databaseConfig
        except yaml.YAMLError as exc:
            print(exc)

#Read a bibtext file and convert to dataframe.
def read_bib(name):
    print('Loading file/'+name+'.bib file')
    with open('file/'+name+'.bib', encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
    return pd.DataFrame.from_records(bib_database.entries)

#Convert a row to xml
def to_xml(row):
    xml = ['<item>']
    for field in row.index:
        xml.append('  <field name="{0}">{1}</field>'.format(field, row[field]))
    xml.append('</item>')
    return '\n'.join(xml)

# Load all bib files and return their concatenation.
def load_bibs():
    iee = read_bib('iee')
    sciencedirect = read_bib('sciencedirect')
    dlacm = read_bib('dlacm')

    #Correct columns position based on pattern.
    columns= ["author", "title", "keywords", "abstract", "year", "type_publication", "doi"]
    iee=iee.reindex(columns=columns)
    sciencedirect=sciencedirect.reindex(columns=columns)
    dlacm=dlacm.reindex(columns=columns)

    return pd.concat([iee,sciencedirect,dlacm], ignore_index=True)

# Load all csv files and return theis concatenation.
def load_csvs():
    jcr = pd.read_csv('file/jcr_2020.csv', delimiter=';')
    scimago = pd.read_csv('file/scimagojr_2020.csv', delimiter=';', low_memory=False)

    jcr.rename(columns={'Rank':'rank','Total Cites':'total_cities','Full Journal Title':'title','Journal Impact Factor':'jcr_value'}, inplace=True)
    scimago.rename(columns={'Rank':'rank','Title':'title','Total Cites (3years)':'total_cities','Type':'type_publication', "SJR" : "scimago_value"}, inplace=True)

    columns= ["rank", "title", "total_cities", "type_publication", "jcr_value", "scimago_value"]
    jcr=jcr.reindex(columns=columns)
    scimago=scimago.reindex(columns=columns)

    scimago['scimago_value']=scimago['scimago_value'].str.replace(',', '.')
    jcr['jcr_value']=jcr['jcr_value'].str.replace('Not Available', '0')    

    return pd.concat([jcr,scimago], ignore_index=True)

def ieee_api(query):
    #apikey = "swz7c76fvfhwvac69hmzukbx"
    apikey = "3fe5knc3hk4tbuwr2yrudu96"
    start_record=1
    max_records=50
    total_records=0
    df = pd.DataFrame()

    while True:
        print("retrieving data from IEEE API [max_records: " + str(max_records) + " , start_record: "+ str(start_record) +"]")
        url = "http://ieeexploreapi.ieee.org/api/v1/search/articles?apikey="+apikey+"&format=json&max_records="+str(max_records)+"&start_record="+str(start_record)+"&"+query
        
        # Make a request for a given paper
        resp = requests.get(url)

        print(resp)

        if (resp.ok):
            result = resp.json()

            total_records = result['total_records']
            print("Your search returned " + str(total_records) + " records")

            if (start_record <= total_records):
                start_record += max_records
            else:
                break

            df_nested_list = pd.json_normalize(result, record_path =['articles'])
            df = pd.concat([df, df_nested_list], ignore_index=True)
        else:
            break

    df.rename(columns={'authors.authors':'author','publication_year':'year'}, inplace=True)
    columns= ["author", "title", "keywords", "abstract", "year", "type_publication", "doi"]
    df=df.reindex(columns=columns)
    return df

configuration = read_yaml('config')

if (configuration['type'] not in ['json','yaml','csv','xml', 'mysql']):
    print('Invalid value')
    exit()

df_bib = pd.DataFrame()
try:
    query=configuration['query'] 
    print("Query active: " + query)
    df_bib=ieee_api(query) 
except Exception:
    df_bib=load_bibs()
    
df_csv=load_csvs()

#df_bib['title'] = df_bib['title'].str.upper()
df_csv['title'] = df_csv['title'].str.upper()
df = pd.merge(df_csv, df_bib, on=['title'], how='outer')

df=df.drop_duplicates(subset='title', ignore_index=True)

df['scimago_value']=pd.to_numeric(df['scimago_value'])
df['jcr_value']=pd.to_numeric(df['jcr_value'])

# Check if there is a filter
key = 'filter'
if key in configuration.keys():
    print('active filter')
    df=df.query(configuration['filter'])

# Generate output file.
if (configuration['type'] == 'json'):
    df.to_json(configuration['file_name'] + '.json', orient='records')

elif (configuration['type'] == 'csv'):
    df.to_csv(configuration['file_name'] +".csv")

elif (configuration['type'] == 'yaml'):
    # Convert dataframe into json object (easier to convert to yaml)
    data=json.loads(df.to_json(orient='records'))
    with open(configuration['file_name'] +'.yaml', 'w') as yml:
        yaml.dump(data, yml, allow_unicode=False)

elif (configuration['type'] == 'xml'):
    file = open(configuration['file_name'] +".xml", "w", encoding='UTF-8') 
    file.write('\n'.join(df.apply(to_xml, axis=1)),) 
    file.close()

elif (configuration['type'] == 'mysql'):
    print(df)
    print('mysql insertion started.')
    db_connection = 'mysql+pymysql://root:root@localhost:3306/impacta'
    db_connection = create_engine(db_connection)
    df.to_sql(con=db_connection, name='data2', if_exists='replace', index=False)

else:
    print('Option is not available')