import json

with open('./alphs.json', 'r', encoding='utf-8') as f:
    alphabets: dict[str, str] = json.load(f)
    playfair_alphabets = {
        "ru": "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
        "RU": "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
        "en": "abcdefghijklmnopqrstuvwxyz",
        "EN": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "digits": "0123456789",
        "specs": " ,.!@#$%^&*()-=_+<>?/~"
    }
