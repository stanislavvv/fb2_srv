# fb2_srv

NIH-проект

Сиё есть сервер opds для кучи fb2 в нескольких zip. Предназначено для запуска на одноплатниках.

## Порядок работы при первоначальном запуске:

  1. либо делаем симлинк `./data` на каталог с .zip, либо правим в app/config.py пути
  2. запускаем `./managedb.py newdb` для создания пустой БД
  3. запускаем `./managedb.py refillall` для заполнения БД данными из .zip (параллельно будут созданы файлики `*.zip.list`)
  4. для локального применения запускаем `./opds.py`, после чего на порту 5000 ловим /opds

## Порядок работы при обновлении .zip:

  1. останавливаем `opds.py`
  2. запускаем `./managedb.py fillnew`
  3. запускаем `./opds.py`

## Параметры `managedb.py`:

  * `dropdb` -- база вам надоела
  * `newdb` -- надо свежую базу
  * `fillnew` -- загрузить обновлённые данные (`.zip` без соответствующего `.zip.list`, либо `.zip` новее, чем `.zip.list`). Старые записи будут удалены перед тем, как.
  * `refillall` -- плюнуть на всё, загрузить данные из всех `.zip` с нуля (перед загрузкой будут удалены записи о книгах из данного `.zip`).
  * `fill_lists` -- загрузить данные из готовых `.zip.list` (на случай битой базы, либо базы, на которую сказали newdb)

## Необходимые данные в комплекте:

  * `fb2_to_html.xsl` -- xsl для получения html с внедрёнными изображениями из fb2
  * `genres.list` -- список жанров с описаниями
  * `genres_replace.list` -- список жанров, которые требуется заменить на жанры из списка выше

## Дополнительные данные для исправления ошибок метаданных из книг -- `data/*.zip.replace`

Структура вида:

```json
{
  "177350.fb2": {
    "author": {
      "first-name": "Вадим",
      "middle-name": "Александрович",
      "last-name": "Чернобров"
    }
  },
  "176236.fb2": {
    "author": {
      "nick-name": "akchisk osan",
      "first-name": null,
      "middle-name": null,
      "last-name": null
    }
  },
  ...etc...
}
```

## Артефакты, получающиеся в процессе работы:

  * `genres_unknown` -- жанры, неучтённые в `genres.list` или `genres_replace.list` (например, жанры с опечаткой)
  * `data/*.zip.list` -- списки метаданных книг в json. Дата обновления файла является флагом для `managedb.py fillnew`
  * `data/*.zip.list.authors` -- отладочные данные, будет удалено

## Необязательные удобства:

  * `Makefile` -- Запускаем `make <команда>`, получаем результат. Команды - `make help` или автодополнение в шелле после `make<TAB>`
  * `other_tools/xmltojson.py` -- утилита, преобразующая xml в json.
