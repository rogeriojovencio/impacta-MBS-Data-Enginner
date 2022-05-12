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

#### Using
```
python main.py
```
