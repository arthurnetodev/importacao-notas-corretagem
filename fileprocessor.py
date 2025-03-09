import pandas as pd
import PyPDF2
from order import Order
from trading_note import TradingNote

class FileProcessor:

    dt = None

    # Adicionar o mapeamento entre o nome do ativo que aparece na nota de corretagem e o ticker correspondente
    tickers = {
        "ABC BRASIL": "ABCB4",
        "ALUPAR": "ALUP11",
        "BRASIL": "BBAS3",
        "COPASA": "CSMG3",
        "ENGIE BRASIL": "EGIE3",
        "ITAUSA": "ITSA4",
        "KLABIN S/A": "KLBN4",
        "TAESA": "TAEE11",
        "ALIBABAGR": "BABA34",
        "BERKSHIRE": "BERK34",
        "JOHNSON": "JNJB34",
        "WAL MART": "WALM34",
        "WALT DISNEY": "DISB34"
    }        

    def __convertTitle2Ticker(self, value):
        ticker = value
        for name, val in self.tickers.items():
            ticker_description_len = len(name)
            if value[:ticker_description_len] == name:
                ticker = val
                break
        return ticker

    def __convertStringToFloat(self, value):
        if pd.isna(value):
            return 0
        return float(value.replace(".","").replace(",","."))

    def __orders_table_as_text_processing(self, pdf_path):
        
        pdf_file = open(pdf_path, 'rb')
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        pdf_file.close()
        print("########################################################")
        print(f"Process pdf as text:")
        #print(text)
        
        # As informações sobre as ordens estarão entre as linhas "Negócios realizados" e "NOTA DE NEGOCIAÇÂO"
        # A data estará na linha seguinte à linha "Data pregão"
        lines = text.split('\n')

        orders = []
        order_index = 0
        order_entry = []
        processing_orders = False
        date_in_next_line = False

        for i in range(len(lines)):
            # Processar linha por linha
            line = lines[i]

            if "Data pregão" == line:
                # Obter data na próxima linha
                date_in_next_line = True
                continue
            
            if "Negócios realizados" == line:
                # Inicio da seção que contem as ordens
                processing_orders = True
                continue

            if "NOTA DE NEGOCIAÇÃO" == line:
                # Fim da seção que contem as ordens
                processing_orders = False
                continue

            if date_in_next_line:
                date_in_next_line = False
                self.dt = line
                continue

            if processing_orders:
                if order_index == 0:
                    # Primeiro registro é o cabeçalho
                    if line == "D/C":
                        # Fim do cabeçalho, preparar para começar a processar a primeira ordem na sequencia
                        order_index += 1
                else:
                    # Processando registro de ordem, armazenar as linhas no vetor até encontrar o fim do registro
                    order_entry.append(line)
                    # Somente procurar pelo campo que indica o fim do registro (contendo D ou C) a partir do quinto item, pois nos campos iniciais pode ter um campo com o valor C tambem
                    if (len(order_entry) > 5):
                        # Identificar fim do registro
                        if (line == "D" or line == "C"):
                            # Obter os dados da ordem para esse registro finalizado
                            operation = order_entry[1]
                            market_type = order_entry[2]
                            title = order_entry[3]
                            ticker = self.__convertTitle2Ticker(title)
                            # O tamanho do vetor pode variar dependendo do tamanho do nome do ativo, então vamos pegar os ultimos 4 elementos com base no tamanho do vetor
                            entry_last_index = len(order_entry)-1
                            quantity = int(order_entry[entry_last_index-3])
                            price = self.__convertStringToFloat(order_entry[entry_last_index-2])
                            value = self.__convertStringToFloat(order_entry[entry_last_index-1])
                            debitcredit = order_entry[entry_last_index]
                            
                            order = Order(ticker, operation, market_type, title, quantity, price, value, debitcredit)
                            print(order)
                            orders.append(order)

                            # Inicia proximo registro
                            order_entry = []
                            order_index += 1

        # Agrupar ordens do mesmo ticker e mesma operação (compra ou venda)
        grouped_orders = {}
        for order in orders:
            key = order.ticker + "-" + order.operation
            if key in grouped_orders:
                grouped_orders[key].value = round(grouped_orders[key].value + order.value, 2)
                grouped_orders[key].quantity += order.quantity
                grouped_orders[key].price = round(grouped_orders[key].value / grouped_orders[key].quantity, 2)
            else:
                grouped_orders[key] = order        
                
        print("########################################################")
        return grouped_orders
    
    def execute(self, pdf_path):
        orders = {}
        orders = self.__orders_table_as_text_processing(pdf_path)
        trading_note = TradingNote(orders, self.dt)
        return trading_note

        

