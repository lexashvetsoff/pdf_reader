import pdfplumber
from typing import List


def clean_headers_row(row: List):
    result = []
    # Заголовки протокола Биннофарм
    # [
    #     'Междуна-\nродное\nнепатен-\nтованное (или\nхимическое,\nили группиро-\nвочное)\nнаименование', 
    #     'Торговое\nнаименование,\nлекарственная\nформа,\nдозировка,\nколичество в\nпотребительск\nой упаковке,\nштриховой код', 
    #     'яиреС', 
    #     'ьлетидовзиорП', 
    #     'Зарегистрир\nованная\nпредельная\nотпускная\nцена\nпроизводите\nля (рублей)2', 
    #     'Фактическая отпускная\nцена, установленная\nпроизводителем (рублей)3', 
    #     '', 
    #     'Дата\nреализации\nлекарственн\nого\nпрепарата\nпроизводите\nлем на\nтерритории\nРоссийской\nФедерации', 
    #     'Отпускная цена организации\nоптовой торговли 4', 
    #     '', 
    #     '', 
    #     'Размер оптовой\nнадбавки\nорганизации\nоптовой торговли 5', 
    #     '', 'Отпускная цена организацией оптовой\nторговли 6', 
    #     '', 
    #     '', 
    #     'Суммарный размер\nоптовых надбавок\nорганизаций\nоптовой торговли 7', 
    #     '', 
    #     'Предельная отпускная\nцена организации\nрозничной торговли 8', 
    #     ''
    # ]
    for item in row:
        # ame_tov = str(row_table[idx_name_tov])
        #     name_tov = name_tov.replace('\n', ' ')
        str_res = str(item)
        str_res = str_res.replace('-\n', '')
        str_res = str_res.replace('\n', ' ')
        result.append(str_res)
    return result


def main():
    tables_data = []
    with pdfplumber.open('pdf_files\ПротоколСибмединфо.pdf') as pdf:
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

    result_row = clean_headers_row(tables_data[-2])
    for i, row in enumerate(result_row):
        print(f'{i}: {row}')


    # 0: №
    # 1: Код товара
    # 2: Наименование товара
    # 3:
    # 4: Серия
    # 5: Количество
    # 6: Срок годности
    # 7: Наименование и местонахождение производителя
    # 8: Декларант* /компания, выпускающая ЛП в гражданский оборот**
    # 9: № декларации* /№ Разрешения на реализацию**
    # 10: Орган сертификации* /номер записи в реестре АИС РЗН **
    # 11: Дата выдачи декларации*/ Дата занесения записи в АИС РЗН**
    
    # print(len(tables_data[0]))
    # print(len(tables_data[1]))
    # print(tables_data[0])
    # print(tables_data[2])

    # print(tables_data[0].index('№'))
    # print(tables_data[0].index('Код товара'))
    # print(tables_data[0].index('Наименование товара'))
    # print(tables_data[0].index('Серия'))    
    # print(tables_data[0].index('Количество'))
    # print(tables_data[0].index('Срок\nгодности'))


if __name__ == '__main__':
    main()
