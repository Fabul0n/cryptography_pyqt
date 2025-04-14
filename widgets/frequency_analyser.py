import sys
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTextEdit, QComboBox, QFileDialog, QLabel, 
                            QTableWidget, QTableWidgetItem, QDialog, QMessageBox, )
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QRect
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import math

class FrequencyAnalyzerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Теоретические вероятности для языков
        self.theoretical_probs = {
            'Русский': {
                'о': 0.1097, 'е': 0.0845, 'а': 0.0801, 'и': 0.0735, 'н': 0.0670,
                'т': 0.0626, 'с': 0.0547, 'р': 0.0473, 'в': 0.0454, 'л': 0.0440,
                'к': 0.0349, 'м': 0.0321, 'д': 0.0298, 'п': 0.0281, 'у': 0.0262,
                'я': 0.0201, 'ы': 0.0190, 'ь': 0.0174, 'г': 0.0170, 'з': 0.0165,
                'б': 0.0159, 'ч': 0.0144, 'й': 0.0121, 'х': 0.0097, 'ж': 0.0094,
                'ш': 0.0073, 'ю': 0.0064, 'ц': 0.0048, 'щ': 0.0036, 'э': 0.0032,
                'ф': 0.0026, 'ъ': 0.0004, 'ё': 0.0004
            },
            'Английский': {
                'e': 0.123, 't': 0.096, 'a': 0.081, 'o': 0.079, 'n': 0.072,
                'i': 0.071, 's': 0.066, 'r': 0.06, 'h': 0.051, 'l': 0.04,
                'd': 0.036, 'c': 0.032, 'u': 0.031, 'p': 0.023, 'f': 0.023,
                'm': 0.022, 'w': 0.020, 'y': 0.019, 'b': 0.016, 'g': 0.016,
                'v': 0.009, 'k': 0.005, 'q': 0.002, 'x': 0.002, 'j': 0.001,
                'z': 0.001
            }
        }

        # Алфавиты для фильтрации и отображения
        self.alphabets = {
            'Русский': 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
            'Английский': 'abcdefghijklmnopqrstuvwxyz'
        }

    def init_ui(self):
        self.setWindowTitle('Частотный анализатор')
        self.resize(800, 600)

        main_layout = QVBoxLayout()

        # Кнопки выбора типа анализа
        btn_layout = QHBoxLayout()
        self.analyze_text_btn = QPushButton('Проанализировать введенный текст')
        self.analyze_file_btn = QPushButton('Проанализировать текст из файла')
        self.analyze_text_btn.clicked.connect(self.show_text_analyzer)
        self.analyze_file_btn.clicked.connect(self.show_file_analyzer)
        btn_layout.addWidget(self.analyze_text_btn)
        btn_layout.addWidget(self.analyze_file_btn)
        main_layout.addLayout(btn_layout)

        # Основной виджет для анализа
        self.analyzer_widget = QWidget()
        self.analyzer_layout = QVBoxLayout()
        self.analyzer_widget.setLayout(self.analyzer_layout)
        main_layout.addWidget(self.analyzer_widget)

        self.setLayout(main_layout)

    def show_text_analyzer(self):
        self.clear_analyzer()
        
        # Выбор языка
        self.language_combo = QComboBox()
        self.language_combo.addItems(['', 'Русский', 'Английский'])
        self.analyzer_layout.addWidget(QLabel('Выберите язык:'))
        self.analyzer_layout.addWidget(self.language_combo)

        # Поле для текста
        self.text_input = QTextEdit()
        self.analyzer_layout.addWidget(QLabel('Введите текст:'))
        self.analyzer_layout.addWidget(self.text_input)

        # Кнопка анализа
        self.analyze_btn = QPushButton('Анализ')
        self.analyze_btn.clicked.connect(self.perform_analysis)
        self.analyzer_layout.addWidget(self.analyze_btn)

        # Поле для расшифрованного текста
        self.decrypted_text = QTextEdit()
        self.decrypted_text.setReadOnly(True)
        self.analyzer_layout.addWidget(QLabel('Расшифрованный текст:'))
        self.analyzer_layout.addWidget(self.decrypted_text)

    def show_file_analyzer(self):
        self.clear_analyzer()
        
        # Выбор языка
        self.language_combo = QComboBox()
        self.language_combo.addItems(['', 'Русский', 'Английский'])
        self.analyzer_layout.addWidget(QLabel('Выберите язык:'))
        self.analyzer_layout.addWidget(self.language_combo)

        # Кнопка выбора файла
        self.file_btn = QPushButton('Выбрать файл')
        self.file_btn.clicked.connect(self.choose_file)
        self.analyzer_layout.addWidget(self.file_btn)

        # Кнопка анализа
        self.analyze_btn = QPushButton('Анализ')
        self.analyze_btn.clicked.connect(self.perform_analysis)
        self.analyzer_layout.addWidget(self.analyze_btn)

        # Поле для расшифрованного текста
        self.decrypted_text = QTextEdit()
        self.decrypted_text.setReadOnly(True)
        self.analyzer_layout.addWidget(QLabel('Расшифрованный текст:'))
        self.analyzer_layout.addWidget(self.decrypted_text)

    def clear_analyzer(self):
        while self.analyzer_layout.count():
            item = self.analyzer_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Выберите текстовый файл', '', 'Text files (*.txt)')
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.file_text = file.read()

    def perform_analysis(self):
        plt.close()
        language = self.language_combo.currentText()
        if not language:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, выберите язык!')
            return

        text = ''
        if hasattr(self, 'text_input'):
            text = self.text_input.toPlainText()
        elif hasattr(self, 'file_text'):
            text = self.file_text
        else:
            QMessageBox.warning(self, 'Ошибка', 'Нет текста для анализа!')
            return

        if not text:
            QMessageBox.warning(self, 'Ошибка', 'Текст не может быть пустым!')
            return

        # Фильтрация букв согласно выбранному языку
        alphabet = set(self.alphabets[language])
        counter = Counter(c.lower() for c in text if c.lower() in alphabet)
        total = sum(counter.values())
        if total == 0:
            QMessageBox.warning(self, 'Ошибка', 'В тексте нет букв выбранного языка!')
            return
        empirical_probs = {char: count/total for char, count in counter.items()}

        # Создание диалогового окна с таблицей
        dialog = QDialog(self)
        dialog.setWindowTitle('Результаты анализа')
        dialog.resize(1200, 600)
        layout = QHBoxLayout()

        # Таблица
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Буква', 'Теор. вероятность', 'Эмпир. вероятность', 'Замена'])
        table.setRowCount(len(self.alphabets[language]))

        # Словарь для хранения данных строк
        self.table_data = []
        substitution = self.calculate_substitution(language, empirical_probs)

        # Заполнение таблицы всеми буквами алфавита
        for char in self.alphabets[language]:
            theor_prob = self.theoretical_probs[language].get(char, 0)
            emp_prob = empirical_probs.get(char, 0)
            subst_char = substitution.get(char, char)
            self.table_data.append({
                'char': char,
                'theor_prob': theor_prob,
                'emp_prob': emp_prob,
                'subst_char': subst_char
            })

        # Заполнение таблицы
        self.update_table(table)

        # Включение редактирования столбца "Замена"
        table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        table.cellChanged.connect(lambda row, col: self.on_cell_changed(row, col, table, substitution, language))

        # Кнопка сортировки
        sort_btn = QPushButton('Сортировать по эмпир. вероятности')
        sort_btn.clicked.connect(lambda: self.on_sort(table))
        right_layout = QVBoxLayout()
        right_layout.addWidget(sort_btn)

        layout.addWidget(table)

        # Картинка
        plt.bar(empirical_probs.keys(), empirical_probs.values())

        plt.title("Вероятности букв в тексте", fontsize=14)
        plt.xlabel("Буква", fontsize=12)
        plt.ylabel("Вероятность", fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        canvas = FigureCanvas(plt.gcf())
        right_layout.addWidget(canvas)

        # Кнопка расшифровки
        decrypt_btn = QPushButton('Расшифровать')
        decrypt_btn.clicked.connect(lambda: self.decrypt_text(text, substitution, dialog))
        right_layout.addWidget(decrypt_btn)

        layout.addLayout(right_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def update_table(self, table):
        """Обновляет таблицу на основе self.table_data"""
        table.blockSignals(True)
        for i, data in enumerate(self.table_data):
            table.setItem(i, 0, QTableWidgetItem(data['char']))
            table.setItem(i, 1, QTableWidgetItem(f"{data['theor_prob']:.4f}"))
            table.setItem(i, 2, QTableWidgetItem(f"{data['emp_prob']:.4f}"))
            table.setItem(i, 3, QTableWidgetItem(data['subst_char']))
            # Отключаем редактирование первых трех столбцов
            for col in range(3):
                item = table.item(i, col)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        table.blockSignals(False)

    def on_sort(self, table):
        """Сортирует таблицу по эмпирическим вероятностям"""
        table.blockSignals(True)
        # Сортируем self.table_data по эмпирическим вероятностям (по убыванию)
        self.table_data.sort(key=lambda x: x['emp_prob'], reverse=True)
        # Обновляем таблицу
        self.update_table(table)
        table.blockSignals(False)

    def on_cell_changed(self, row, col, table, substitution, language):
        if col != 3:  # Изменения только в столбце "Замена"
            return

        table.blockSignals(True)

        # Получаем текущую букву из таблицы
        original_char = self.table_data[row]['char']
        new_char = table.item(row, col).text().lower()

        # Проверка валидности введенной буквы
        if new_char and (new_char not in self.alphabets[language] or len(new_char) > 1):
            QMessageBox.warning(self, 'Ошибка', f'Введите одну букву из алфавита {language.lower()} языка!')
            table.setItem(row, col, QTableWidgetItem(self.table_data[row]['subst_char']))
            table.blockSignals(False)
            return

        # Если новая буква уже используется, делаем свап
        if new_char and new_char != self.table_data[row]['subst_char']:
            for data in self.table_data:
                if data['char'] != original_char and data['subst_char'] == new_char:
                    data['subst_char'] = self.table_data[row]['subst_char']
                    substitution[data['char']] = self.table_data[row]['subst_char']
                    break

        # Обновляем данные и словарь замен
        self.table_data[row]['subst_char'] = new_char if new_char else self.table_data[row]['subst_char']
        substitution[original_char] = new_char if new_char else self.table_data[row]['subst_char']

        # Обновляем таблицу
        self.update_table(table)

        table.blockSignals(False)

    def calculate_substitution(self, language, empirical_probs):
        # Создаем биективное отображение
        alphabet = list(self.alphabets[language])
        substitution = {char: char for char in alphabet}  # Инициализация тождественным отображением
        
        # Сортируем эмпирические и теоретические вероятности
        theoretical = sorted(self.theoretical_probs[language].items(), key=lambda x: x[1], reverse=True)
        empirical = sorted(empirical_probs.items(), key=lambda x: x[1], reverse=True)
        
        # Сопоставляем буквы по вероятностям
        used_theoretical = set()
        for emp_char, emp_prob in empirical:
            if emp_char in alphabet:
                min_diff = float('inf')
                best_theor_char = emp_char
                for theor_char, theor_prob in theoretical:
                    if theor_char not in used_theoretical and theor_char in alphabet:
                        diff = abs(theor_prob - emp_prob)
                        if diff < min_diff:
                            min_diff = diff
                            best_theor_char = theor_char
                if best_theor_char != emp_char:
                    # Находим текущую замену best_theor_char
                    for c in substitution:
                        if substitution[c] == best_theor_char and c != emp_char:
                            substitution[c] = substitution[emp_char]
                            break
                    substitution[emp_char] = best_theor_char
                    used_theoretical.add(best_theor_char)
        
        return substitution

    def decrypt_text(self, text, substitution, dialog):
        decrypted = ''
        for char in text:
            if char.lower() in substitution:
                new_char = substitution[char.lower()]
                decrypted += new_char if char.islower() else new_char.upper()
            else:
                decrypted += char
        
        self.decrypted_text.setText(decrypted)
        dialog.accept()