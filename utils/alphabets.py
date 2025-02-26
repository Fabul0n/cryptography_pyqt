import json

with open('./utils/alphs.json', 'r', encoding='utf-8') as f:
    alphabets: dict[str, str] = json.load(f)
