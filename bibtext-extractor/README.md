# Bibtext Extractor

## How it works
This tool extracts a bibfile from iee, sciencedirect and dlacm and convert it to Json, CSV or Yaml based on config.yaml file.

#### Requirements
- Python 3+
- Pip
- Lib Pandas
- Lib Bibtexparser (https://bibtexparser.readthedocs.io/)
- Lib Yaml

#### config.yaml
type: <output file type, available options: json, csv or yaml>
file_name: <output file name>

#### main.py
Contains the main code with flow:
  * 1 - Read all bibtext file
  * 2 - Arrange columns 
  * 3 - Concat dataframe of Ieee, ScientDirect and Dl ACM
  * 4 - Read config.yaml file
  * 5 - Write json, csv or yaml output file.

#### file folder
Contains bibtex files from ieee, scientdirect and dl acm.
  
#### Using
```
python main.py
```
