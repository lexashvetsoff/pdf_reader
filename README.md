# pdf_reader


## Settings

```json
    "Acrichin":
    {
        "Reestr":
        {
            "start_row_table": 2,
            "stop_row_table": 2,
            "output_format": "xml"
        },
        "Protocol":
        {}
    }
```

`Reestr` - Блок описания настроек для реестра    
`Protocol` - Блок описания настроек для протокола    

`row_table_headers` - Строка с заголовками в таблице
`start_row_table` - Первая строка в таблице pdf, до нее - заголовок таблицы
`stop_row_table` - Последняя строка в таблице pdf, после нее - различные сноски, дополнения
`output_format` - Формат выходного файла - json или xml