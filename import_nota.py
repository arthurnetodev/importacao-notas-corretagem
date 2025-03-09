import os
import pandas as pd
from fileprocessor import FileProcessor
import openpyxl
from trading_note import TradingNote
from typing import List

def process_pdf_files(notas_folder):
    print("Processar arquivos pdf...")
    trading_notes = []
    files = os.listdir(notas_folder)
    for filename in files:
        if filename.endswith('.pdf'):
            print("Lendo arquivo " + filename)
            pdf_path = os.path.join(notas_folder, filename)
            file_processor = FileProcessor()
            trading_note = file_processor.execute(pdf_path)
            trading_notes.append(trading_note)

    return trading_notes

def save_to_excel_all(file, trading_notes: List[TradingNote]):
    sheetTitle = 'Trading notes'
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = sheetTitle

    counter = 1
    sheet['A' + str(counter)] = 'Data'
    sheet['B' + str(counter)] = 'Ativo'
    sheet['C' + str(counter)] = 'Operação'
    sheet['D' + str(counter)] = 'Preço'
    sheet['E' + str(counter)] = 'Quantidade'
    sheet['F' + str(counter)] = 'Valor'

    for trading_note in trading_notes:
        counter += 1
        sheet['A' + str(counter)] = trading_note.date
        for order in trading_note.orders.values():
            sheet['B' + str(counter)] = order.ticker
            sheet['C' + str(counter)] = order.operation
            sheet['D' + str(counter)] = order.price
            sheet['E' + str(counter)] = order.quantity
            sheet['F' + str(counter)] = order.value
            counter += 1
    wb.save(file)

def consolidate_data(trading_notes):
    print("Consolidar dados")
    all_orders = [order for trading_note in trading_notes for order in trading_note.orders.values()]
    data = pd.DataFrame([{
        'Ticker': order.ticker,
        'Operation': order.operation,
        'Price': order.price,
        'Quantity': order.quantity,
        'Value': order.value
    } for order in all_orders])

    # Agrupar dados por ticker e operação, somando os valores de quantidade e valor
    grouped_data = data.groupby(['Ticker', 'Operation']).agg({
        'Quantity': 'sum',
        'Value': 'sum'
    }).reset_index()
    grouped_data['Price'] = round(grouped_data['Value']/grouped_data['Quantity'], 2)
    print(grouped_data)
    return grouped_data

def save_to_excel_consolidated(file, grouped_data):
    print("Salvar dados consolidados em arquivo excel")
    grouped_data.to_excel(file, sheet_name='Resumo', index=False)

print("Iniciando aplicação...")
notas_folder = r".\notas"
trading_notes_file = "ordens.xlsx"
trading_notes_resume_file = "resumo_ordens.xlsx"

trading_notes = process_pdf_files(notas_folder)
save_to_excel_all(trading_notes_file, trading_notes)

grouped_data = consolidate_data(trading_notes)
save_to_excel_consolidated(trading_notes_resume_file, grouped_data)

print("Aplicação finalizada")
