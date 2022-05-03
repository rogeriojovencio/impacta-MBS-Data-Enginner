import bibtexparser
import pandas as pd
import json
import yaml

#Read a yaml file.
def read_yaml(name):
    with open(name+'.yaml') as file:
        try:
            databaseConfig = yaml.safe_load(file)   
            return databaseConfig
        except yaml.YAMLError as exc:
            print(exc)

#Read a bibtext file and convert to dataframe.
def read_bibtext(name):
    print('Loading file/'+name+'.bib file')
    with open('file/'+name+'.bib', encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
    return pd.DataFrame.from_records(bib_database.entries)

def to_xml(row):
    xml = ['<item>']
    for field in row.index:
        xml.append('  <field name="{0}">{1}</field>'.format(field, row[field]))
    xml.append('</item>')
    return '\n'.join(xml)

iee = read_bibtext('iee')
sciencedirect = read_bibtext('sciencedirect')
dlacm = read_bibtext('dlacm')

#Correct columns position based on pattern.
columns= ["author", "title", "keywords", "abstract", "year", "type_publication", "doi"]
iee=iee.reindex(columns=columns)
sciencedirect=sciencedirect.reindex(columns=columns)
dlacm=dlacm.reindex(columns=columns)

#Concat all dataframes.
df=pd.concat([iee,sciencedirect,dlacm], ignore_index=True)

# Write output file with type set in config.yaml file.
configuration = read_yaml('config')
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

else:
    print('Option is not available')