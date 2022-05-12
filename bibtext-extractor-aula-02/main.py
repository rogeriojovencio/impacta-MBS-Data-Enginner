import bibtexparser
import pandas as pd
import json
import yaml

# Read a yaml file.


def read_yaml(name):
    with open(name+'.yaml') as file:
        try:
            databaseConfig = yaml.safe_load(file)
            return databaseConfig
        except yaml.YAMLError as exc:
            print(exc)

# Read a bibtext file and convert to dataframe.


def read_bib(name):
    print('Loading file/'+name+'.bib file')
    with open('file/'+name+'.bib', encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
    return pd.DataFrame.from_records(bib_database.entries)

# Convert a row to xml


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

# Correct columns position based on pattern.
    columns = ["author", "title", "keywords", "abstract", "year", "type_publication", "doi"]
    iee = iee.reindex(columns=columns)
    sciencedirect = sciencedirect.reindex(columns=columns)
    dlacm = dlacm.reindex(columns=columns)

    return pd.concat([iee, sciencedirect, dlacm], ignore_index=True)

# Load all csv files and return theis concatenation.


def load_csvs():
    jcr = pd.read_csv('file/jcr_2020.csv', delimiter=';')
    scimago = pd.read_csv('file/scimagojr_2020.csv',
                          delimiter=';', low_memory=False)

    jcr.rename(columns={'Rank': 'rank', 'Total Cites': 'total_cities', 'Full Journal Title': 'title', 'Journal Impact Factor': 'scimago_value'}, inplace=True)
    scimago.rename(columns={'Rank': 'rank', 'Title': 'title', 'Total Cites (3years)': 'total_cities','Type': 'type_publication', 'SJR': 'jcr_value'}, inplace=True)

    columns = ["rank", "jcr_value", "scimago_value", "title", "total_cities", "type_publication"]
    jcr = jcr.reindex(columns=columns)
    scimago = scimago.reindex(columns=columns)

    return pd.concat([jcr, scimago], ignore_index=True)


df_bib = load_bibs()
df_csv = load_csvs()

df_bib['title'] = df_bib['title'].str.upper()
df_csv['title'] = df_csv['title'].str.upper()

df = pd.merge(df_bib, df_csv, on=['title'], how='outer')

df = df.drop_duplicates(subset='title', ignore_index=True)

# Write output file with type set in config.yaml file.
configuration = read_yaml('config')
if (configuration['type'] == 'json'):
    df.to_json(configuration['file_name'] + '.json', orient='records')

elif (configuration['type'] == 'csv'):
    df.to_csv(configuration['file_name'] + ".csv")

elif (configuration['type'] == 'yaml'):
    # Convert dataframe into json object (easier to convert to yaml)
    data = json.loads(df.to_json(orient='records'))
    with open(configuration['file_name'] + '.yaml', 'w') as yml:
        yaml.dump(data, yml, allow_unicode=False)

elif (configuration['type'] == 'xml'):
    file = open(configuration['file_name'] + ".xml", "w", encoding='UTF-8')
    file.write('\n'.join(df.apply(to_xml, axis=1)),)
    file.close()

else:
    print('Option is not available')
