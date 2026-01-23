# JSON to CSV Converter

A script that reads a .json file containing an array of objects and converts it into a .csv file.

## Usage

```bash
python3 json2csv.py input.json [output.csv]
```

If the output filename is omitted, it will use the same name as the input file with a `.csv` extension.

## Requirement
Input JSON must be a list of objects, e.g.:
```json
[
  {"name": "Alice", "age": 30},
  {"name": "Bob", "age": 25}
]
```
