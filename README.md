# fb2_srv

разное за fb2 и NNN fb2 в zip

  * `utils/list_fb2_in_zipfile.py` -- обрабатывает `.zip` с `.fb2` внутри, отдаёт данные в формате |-separated, поля обозначены в `show_headers()` (вывод отключен)
  * `utils/list2sqlite.py` -- обновляет данные в базе из файлов вида `*.zip.list`, полученных при помощи `list_fb2_in_zipfile.py`
