# Flibusta library
Асинхронная библиотека для работы с сайтом флибуста. 
Поддерживает подключение к прокси onion. 
Скачивает и сохраняет книги в указанную папку.

## Пример использования

```python 
async def main():
    ff = Flibusta(9052, "127.0.0.1") # Указывает данные от socks5 прокси tor
    if await ff.check_connection():  # Проверка работает ли все окей
        books = await ff.search_for_books(query="Python") # Поиск книги по запросу "Python"
        for book in books: # Перебираем все найденные 
            print(f"Название {book.name}") # Выводим в консоль название книги
            download_b = await book.download_book() #Скачиваем книгу в дефолтную папку - downloads
            print(download_b[1]) #Получаем размер скачанного файла и выводим в консоль
        print(len(books)) #Кол-во найденных книг


if __name__ == "__main__":
    asyncio.run(main()) #Запускаем асинхронно 

```


### Dev marks
-----
####  activate venv
```
source venv/bin/activate
```