import os
import json
import pdfplumber
import pandas as pd
import xml.etree.ElementTree as et


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


def main():
    with open('settings.json', 'r', encoding='utf-8') as file:
        settings = json.load(file)
    
    acrichin = settings['Acrichin']
    print(acrichin)

    tables_data = []
    with pdfplumber.open('pdf_files\АкрихинРеестр.PDF') as pdf:
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
    
    # print(len(tables_data[0]))
    # print(len(tables_data[1]))
    # print(tables_data[0])
    # print(tables_data[2])

    # print(tables_data[0].index('№'))
    idx_row_number = tables_data[0].index('№')

    # print(tables_data[0].index('Код товара'))
    idx_code_tov = tables_data[0].index('Код товара')

    # print(tables_data[0].index('Наименование товара'))
    idx_name_tov = tables_data[0].index('Наименование товара')

    # print(tables_data[0].index('Серия'))
    idx_series = tables_data[0].index('Серия')

    # print(tables_data[0].index('Количество'))
    idx_count = tables_data[0].index('Количество')

    # print(tables_data[0].index('Срок\nгодности'))
    idx_expiration_date = tables_data[0].index('Срок\nгодности')

    results = []
    # print(tables_data[acrichin['start_row_table']:])
    for row_table in tables_data[acrichin['start_row_table']:-acrichin['stop_row_table']]:
        if row_table[idx_row_number]:
            name_tov = str(row_table[idx_name_tov])
            name_tov = name_tov.replace('\n', ' ')

            series = str(row_table[idx_series])
            if series[0] == "'":
                series = series.replace("'", '', 1)
            
            expiration_date = str(row_table[idx_expiration_date])
            if expiration_date[0] == "'":
                expiration_date = expiration_date.replace("'", '', 1)
            
            data = {
                'row_number': row_table[idx_row_number],
                'code': row_table[idx_code_tov],
                'name': name_tov,
                'series': series,
                'count': row_table[idx_count],
                'expiration_date': expiration_date
            }
            results.append(data)
    
    if acrichin['output_format'] == 'json':
        with open('output.json', 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=4)
    elif acrichin['output_format'] == 'xml':
        list_dict_to_xml(results)


if __name__ == '__main__':
    main()
