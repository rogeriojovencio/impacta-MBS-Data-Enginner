import json
import requests


# Acessos
# https://api.elsevier.com/content/metadata/article?query=aff%28broad%20institute%29&httpAccept=application/xml&apiKey=167021d4c58c07eb6d56968b6d41797a

# Como configurar
# https://dev.elsevier.com/tecdoc_sd_ir_integration.html

# Pegar metadado Science Direct
#https://dev.elsevier.com/documentation/ArticleMetadataAPI.wadl#d1e31



apikey = "167021d4c58c07eb6d56968b6d41797a"

# Documentação da chamada abaixo. scopus funciona.
# https://dev.elsevier.com/documentation/AbstractRetrievalAPI.wadl#d1e48
#url = "http://api.elsevier.com/content/abstract/scopus_id/SCOPUS_ID:84881866621"


# Doc https://dev.elsevier.com/documentation/AbstractRetrievalAPI.wadl#d1e48
# Não funciona
#url = "https://api.elsevier.com/content/metadata/article?apiKey=167021d4c58c07eb6d56968b6d41797a"

# Não funciona
url = "https://api.elsevier.com/content/metadata/article"


# Make a request for a given paper
resp = requests.get(url,
                    headers = {'Accept': 'application/json',
                               'X-ELS-APIKey': apikey,
                               'X-RateLimit-Reset': None})
 
#data = {'name': 'hello', 'data[]': ['hello', 'world']}
#response = requests.get('http://example.com/api/add.json', params=data)


# Check the status of the request
print(resp.headers['X-RateLimit-Remaining'])
print(resp.headers['X-ELS-Status'])
print(resp.headers)
print(resp)

# Check if the problem is the weekly download limit (usually 10000)
try:
    print(resp.header['X-RateLimit-Remaining'])
except:
    pass



