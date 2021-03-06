# fb2_srv

NIH-проект

Сиё есть сервер opds для кучи fb2 в нескольких zip. Предназначено для запуска на одноплатниках.

## Порядок работы при первоначальном запуске:

  1. либо делаем симлинк `./data` на каталог с .zip, либо правим в app/config.py пути
  2. запускаем `./managedb.py newdb` для создания пустой БД
  3. запускаем `./managedb.py refillall` для заполнения БД данными из .zip (параллельно будут созданы файлики `*.zip.list`)
  4. для локального применения запускаем `./opds.py`, после чего на порту 5000 ловим /opds

## Параметры `managedb.py`:

  * `dropdb` -- база вам надоела
  * `newdb` -- надо свежую базу
  * `fillnew` -- загрузить обновлённые данные (`.zip` без соответствующего `.zip.list`, либо `.zip` новее, чем `.zip.list`). Старые записи будут удалены перед тем, как.
  * `refillall` -- плюнуть на всё, загрузить данные из всех `.zip` с нуля (перед загрузкой будут удалены записи о книгах из данного `.zip`).
  * `fill_lists` -- загрузить данные из готовых `.zip.list` (на случай битой базы, либо базы, на которую сказали newdb)
  * `renew_lists` -- пересоздать `.zip.list` заново без их загрузки в БД
  * `new_lists` -- обновить `.zip.list` (появились новые или обновились старые `.zip` или `.zip.replace`) без загрузки в БД
  * `fsck` -- убрать авторов/серии/жанры без книг (медленно и печально, быстрее `newdb` + `fill_lists`)

## Необходимые данные в комплекте:

  * `fb2_to_html.xsl` -- xsl для получения html с внедрёнными изображениями из fb2
  * `genres.list` -- список жанров с описаниями (в основном, совпадают с fb2)
  * `genres_meta.list` -- список групп жанров
  * `genres_replace.list` -- список жанров, которые требуется заменить на жанры из списка выше

## Дополнительные данные для исправления ошибок метаданных из книг -- `data/*.zip.replace`

Структура вида:

```json
{
  "1234567.fb2": {
    "author": {
      "first-name": "Иван",
      "middle-name": "Иванович",
      "last-name": "Иванов"
    }
  },
  "987654.fb2": {
    "author": [
      {
        "nick-name": "akchisk osan",
        "first-name": null,
        "middle-name": null,
        "last-name": null
      },
      {
        ...
      }
    ],
    "book-title": "Типа-книга",
    "sequence": {
      "@name": "Типа серия",
      "@number": 1
    },
  },
  ...etc...
}
```

Замена идёт "первый уровень на первый", т.е. если вписать только last-name в author, то потом у автора будет только last-name, даже если в оригинале был полный набор полей.

## Артефакты, получающиеся в процессе работы:

  * `data/*.zip.list` -- списки метаданных книг в json. Дата обновления файла является флагом для `managedb.py fillnew`
  * `data/*.zip.list.authors` -- отладочные данные при DEBUG=True

## Необязательные удобства:

  * `Makefile` -- Запускаем `make <команда>`, получаем результат. Команды - `make help` или автодополнение в шелле после `make<TAB>`
  * `other_tools/xmltojson.py` -- утилита, преобразующая xml в json, пригодна на предмет подсмотреть содержимое fb2.

## Что делать при добавлении данных

Сейчас на моём домашнем хранилище делается примерно такой цикл:

1. появляются новые `.zip` с `.fb2` внутри
2. запускается `managedb.py fillnew`

В случае изменения содержимого старых `.zip` для уменьшения времени, когда БД недоступна (т.е. 500 на выходе):

1. обновляются `.zip` с `.fb2`
2. запускается `managedb.py new_lists` для обновления `.zip.list`
3. запускается `managedb.py newdb; managedb.py fill_lists`

Пункты 2 и 3 в сумме дают значительно меньшее время даунтайма, чем запуск `managedb.py fillnew; managedb.py fsck`, как предполагалось изначально.
