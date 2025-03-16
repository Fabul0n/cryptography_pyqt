import json

with open('./alphs.json', 'r', encoding='utf-8') as f:
    alphabets: dict[str, str] = json.load(f)
