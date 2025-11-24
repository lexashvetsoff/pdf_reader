import os
import sys
import json
import enum
import argparse
import pdfplumber
import pandas as pd
import xml.etree.ElementTree as et


class TableSettings:
    def __init__(self, data):
        self.row_table_headers: int = data['row_table_headers']
        self.start_row_table: int = data['start_row_table']
        self.stop_row_table: int = data['stop_row_table']
        self.headings_on_every_page: bool = data['headings_on_every_page']
        self.count_row_heders_other_pages: int = data['count_row_heders_other_pages']
        self.series_and_expiration_date_combined: bool = data['series_and_expiration_date_combined']
        self.separator_series_and_expiration: str = data['separator_series_and_expiration']


class OutputSettings:
    def __init__(self, data):
        self.output_format: str = data['output_format']


class ReestrColumns:
    def __init__(self, data):
        self.column_por_num: int = data['column_por_num']
        self.column_code_tov: int = data['column_code_tov']
        self.column_name_tov: int = data['column_name_tov']
        self.column_series: int = data['column_series']
        self.column_count: int = data['column_count']
        self.column_expiry_date: int = data['column_expiry_date']
        self.column_proizv: int = data['column_proizv']
        # self.column_declarant: int = data['column_declarant']
        # self.column_certificate_number: int = data['column_certificate_number']
        # self.column_AIS_number: int = data['column_AIS_number']
        # self.column_AIS_loading_date: int = data['column_AIS_loading_date']


class Reestr:
    def __init__(self, data):
        self.table_settings = TableSettings(data['table_settings'])
        self.columns = ReestrColumns(data['columns'])
        self.output_settings = OutputSettings(data['output_settings'])


class ProtocolColumns:
    def __init__(self, data):
        self.column_mnn: int = data['column_mnn']
        self.column_trade_name: int = data['column_trade_name']
        self.column_series: int = data['column_series']
        self.column_proizvod: int = data['column_proizvod']
        self.column_max_proizv_price: int = data['column_max_proizv_price']
        self.column_fakt_price_proizv: int = data['column_fakt_price_proizv']
        self.column_sale_date_RF: int = data['column_sale_date_RF']
        self.column_wholesale_price: int = data['column_wholesale_price']
        self.column_wholesale_markup: int = data['column_wholesale_markup']
        self.column_total_wholesale_price: int = data['column_total_wholesale_price']
        self.column_total_wholesale_markup: int = data['column_total_wholesale_markup']
        self.column_max_retail_price: int = data['column_max_retail_price']


class Protocol:
    def __init__(self, data):
        self.table_settings = TableSettings(data['table_settings'])
        self.columns = ProtocolColumns(data['columns'])
        self.output_settings = OutputSettings(data['output_settings'])


class ReestrOutputColumns:
    def __init__(self, data):
        self.column_por_num = data["column_por_num"]
        self.column_name_tov = data["column_name_tov"]
        self.column_code_tov = data["column_code_tov"]
        self.column_series = data["column_series"]
        self.column_expiry_date = data["column_expiry_date"]
        self.column_count = data["column_count"]
        self.column_proizv = data["column_proizv"]


class ProtocolOutputColumns:
    def __init__(self, data):
        pass


class Settings:
    def __init__(self, data_name_columns, data_params, type_data):
        # type_data: 'Reestr' or 'Protocol'
        if type_data == 'Reestr':
            self.out_colums = ReestrOutputColumns(data_name_columns['Reestr'])
            self.params = Reestr(data_params['Reestr'])
        elif type_data == 'Protocol':
            self.out_colums = ProtocolOutputColumns(data_name_columns['Protocol'])
            self.params = Protocol(data_params['Protocol'])
        else:
            raise ValueError


def list_dict_to_xml(data, root_tag='root', element_tag='item'):
    """
    Преобразует список словарей в XML-строку.
    
    :param data: List[Dict] - список словарей
    :param root_tag: str - тег корневого элемента
    :param element_tag: str - тег для каждого элемента списка
    :return: str - XML в виде строки
    """

    root = et.Element(root_tag)

    for item in data:
        element = et.SubElement(root, element_tag)
        for key, value in item.items():
            child = et.SubElement(element, str(key))
            child.text = str(value)
    
    tree = et.ElementTree(root)
    try:
        et.indent(tree, space='    ', level=0)
    except AttributeError:
        pass

    tree.write('output.xml', encoding='utf-8', xml_declaration=True)


def main(code: str, folder: str, file_name: str, type_data: str):
    with open('settings.json', 'r', encoding='utf-8') as file:
        file_settings = json.load(file)
    
    # type_data = 'Reestr'
    settings = Settings(file_settings['output_columns_name'], file_settings[code], type_data)

    tables_data = []
    file_path = os.path.join(folder, file_name)
    # with pdfplumber.open('pdf_files\АкрихинРеестр.PDF') as pdf:
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            # Настройки для лучшего распознавания
            table_settings = {
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines",
                "snap_tolerance": 4,
            }

            tables = page.extract_tables(table_settings)
            for table in tables:
                for row in table:
                    # Фильтрация пустых строк
                    if any(cell and cell.strip() for cell in row):
                        tables_data.append([cell.strip() if cell else "" for cell in row])

    results = []
    row_start = settings.params.table_settings.start_row_table
    row_stop = -settings.params.table_settings.stop_row_table if settings.params.table_settings.stop_row_table != 0 else len(tables_data)
    # for row_table in tables_data[settings.params.table_settings.start_row_table:-settings.params.table_settings.stop_row_table]:
    for row_table in tables_data[row_start:row_stop]:
        skip_row = False
        for ceil in row_table:
            if 'МНН' in ceil or 'Мнн' in ceil or 'мнн' in ceil:
                skip_row = True
                break
        
        if skip_row:
            continue

        if row_table[settings.params.columns.column_por_num]:
            name_tov = str(row_table[settings.params.columns.column_name_tov])
            name_tov = name_tov.replace('\n', ' ')

            name_proizvod = str(row_table[settings.params.columns.column_proizv])
            name_proizvod = name_proizvod.replace('\n', ' ')

            if settings.params.table_settings.series_and_expiration_date_combined:
                combined_str = str(row_table[settings.params.columns.column_series])
                combined_str_split = combined_str.split(sep=settings.params.table_settings.separator_series_and_expiration)
                series = combined_str_split[0].strip()
                expiration_date = combined_str_split[1].strip()
            else:
                series = str(row_table[settings.params.columns.column_series])
                expiration_date = str(row_table[settings.params.columns.column_expiry_date])
            
            if series[0] == "'":
                series = series.replace("'", '', 1)
            series = series.replace('\n', '')
            
            if expiration_date:
                if expiration_date[0] == "'":
                    expiration_date = expiration_date.replace("'", '', 1)
            
            data = {}
            if type_data == 'Reestr':
                name_columns: ReestrOutputColumns = settings.out_colums

                data[name_columns.column_por_num] = row_table[settings.params.columns.column_por_num]

                if settings.params.columns.column_code_tov:
                    data[name_columns.column_code_tov] = row_table[settings.params.columns.column_code_tov]

                data[name_columns.column_name_tov] = name_tov
                data[name_columns.column_series] = series
                
                if settings.params.columns.column_count:
                    data[name_columns.column_count] = row_table[settings.params.columns.column_count]
                
                data[name_columns.column_expiry_date] = expiration_date
                data[name_columns.column_proizv] = name_proizvod

                # data = {
                #     name_columns.column_por_num: row_table[settings.params.columns.column_por_num],
                #     name_columns.column_code_tov: row_table[settings.params.columns.column_code_tov],
                #     name_columns.column_name_tov: name_tov,
                #     name_columns.column_series: series,
                #     name_columns.column_count: row_table[settings.params.columns.column_count],
                #     name_columns.column_expiry_date: expiration_date,
                #     name_columns.column_proizv: name_proizvod
                # }

                # data = {
                #     'row_number': row_table[settings.params.columns.column_por_num],
                #     'code': row_table[settings.params.columns.column_code_tov],
                #     'name': name_tov,
                #     'series': series,
                #     'count': row_table[settings.params.columns.column_count],
                #     'expiration_date': expiration_date
                # }
            results.append(data)

    if settings.params.output_settings.output_format == 'json':
        with open('output.json', 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=4)
    elif settings.params.output_settings.output_format == 'xml':
        list_dict_to_xml(results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--code", "-c", type=str, required=True, help="Код поставщика")
    parser.add_argument("--folder", "-f", type=str, required=True, help="Директория файла")
    parser.add_argument("--file", "-fn", type=str, required=True, help="Имя файла")
    parser.add_argument("--type", "-t", choices=["Reestr", "Protocol"], default="Reestr", help="Тип документа")

    args = parser.parse_args()

    # print(args.code)
    # print(type(args.code))

    # print(args.folder)
    # print(type(args.folder))

    # print(args.file)
    # print(type(args.file))

    # print(args.type)
    
    main(args.code, args.folder, args.file, args.type)
