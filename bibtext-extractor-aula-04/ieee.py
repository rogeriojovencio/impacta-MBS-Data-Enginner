import json
import requests
import pandas as pd

query="sort_order=asc&sort_field=article_number&publication_title=python"
apikey = "swz7c76fvfhwvac69hmzukbx"
start_record=1
max_records=50
total_records=0

df = pd.DataFrame()

while True:
    print("retrieving data from IEEE API [max_records: " + str(max_records) + " , start_record: "+ str(start_record) +"]")
    url = "http://ieeexploreapi.ieee.org/api/v1/search/articles?apikey="+apikey+"&format=json&max_records="+str(max_records)+"&start_record="+str(start_record)+"&"+query
    
    # Make a request for a given paper
    resp = requests.get(url)

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

df.info()



