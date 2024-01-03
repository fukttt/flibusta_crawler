# Класс работы с сайтом Flibusta
# написан исключительно в целях обучения написания библиотек
#
import logging, sys, os
import asyncio, aiohttp, aiofiles
from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector
from bs4 import BeautifulSoup


logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class Flibusta_book:
    __type = "Flibusta_book"

    def __init__(
        self,
        author: str,
        name: str,
        download_link: str,
        author_link: str,
        proxy_host: str,
        proxy_port: int,
    ):
        self.author = author
        self.name = name
        self.download = download_link
        self.author_link = author_link
        self.host = proxy_host
        self.port = proxy_port

    def get_tor_session(self) -> aiohttp.ClientSession:
        """
        Функция для получения сессии aiohttp.
        В сессии уже есть прокси, указанный при инициализации родительского класса.
        Можно использовать для кастомных запросов.
        :return: requests.Session .
        """
        connector = ProxyConnector(
            proxy_type=ProxyType.SOCKS5, host=self.host, port=self.port
        )
        session = aiohttp.ClientSession(connector=connector)
        return session

    def GetHumanReadable(self, size, precision=2):
        """
        Функция для конвертации размера файла в читаемый.
        """
        suffixes = ["B", "KB", "MB", "GB", "TB"]
        suffixIndex = 0
        while size > 1024 and suffixIndex < 4:
            suffixIndex += 1  # increment the index of the suffix
            size = size / 1024.0  # apply the division
        return "%.*f%s" % (precision, size, suffixes[suffixIndex])

    async def download_book(self, path: str = "./downloads/") -> list[str] | bool:
        """
        Скачивает книгу в указанную папку.
        :param path - папка куда скачивать файл (default `./downloads/`)
        :return [filename, size] | False
        """
        try:
            headers = {
                "Accept": "*/*",
                "User-Agent": "py/flibusta-crawler",
            }
            async with self.get_tor_session() as session:
                async with session.get(
                    f"{self.download}/download", headers=headers, allow_redirects=False
                ) as resp:
                    file_name = resp.headers["Location"].rsplit("/", 1)[1]
                    async with session.get(resp.headers["Location"]) as res:
                        file_path = f"{path}{file_name}"
                        f = await aiofiles.open(file_path, mode="wb")
                        await f.write(await res.read())
                        await f.close()
                        return [
                            file_path,
                            self.GetHumanReadable(os.path.getsize(file_path)),
                        ]
        except:
            return False


class Flibusta:
    """
    Главный класс для инициализации. \n
    Имеет такие настройки как: \n
    :param proxy_host Tor прокся для доступа к онион ссылкам (пример `127.0.0.1`).
    :param proxy_port: Порт прокси (пример `9051`).
    :param busta_url Onion линк на Flibusta (default `flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion`).
    :param timeout таймаут запросов (default `5`).
    :return: объект с функциями для работы с книгами.
    """

    __type = "Flibusta"

    def __init__(
        self,
        proxy_port: int,
        proxy_host: str,
        busta_url: str = "flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion",
    ):
        self.url = f"http://{busta_url}"
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.headers = {"User-Agent": "py/flibusta-crawler", "Accept": "*/*"}

    async def check_connection(self) -> bool:
        """
        Функция проверки подключения к сайту.
        :return: True если все ок.
        """
        try:
            async with self.get_tor_session() as session:
                async with session.get(f"{self.url}/", headers=self.headers):
                    return True
        except Exception as e:
            logging.error(str(e))
            return False

    def get_tor_session(self) -> aiohttp.ClientSession:
        """
        Функция для получения сессии aiohttp.
        В сессии уже есть прокси, указанный при инициализации родительского класса.
        Можно использовать для кастомных запросов.
        :return: requests.Session .
        """
        connector = ProxyConnector(
            proxy_type=ProxyType.SOCKS5, host=self.proxy_host, port=self.proxy_port
        )
        session = aiohttp.ClientSession(connector=connector)
        return session

    async def search_for_books(self, query: str, limit: int = 5) -> list[Flibusta_book]:
        """
        Поиск книг по названию и автору.
        :param query - Поисковой запрос.
        :param limit - Лимит по результатам. (default `5`)
        :return: `list[Flibusta_book]`
        """
        books = []
        try:
            async with self.get_tor_session() as session:
                async with session.get(
                    f"{self.url}/booksearch?ask={query}",
                    headers=self.headers,
                ) as req:
                    resp_text = await req.text()
                    soup = BeautifulSoup(resp_text, "html.parser")
                    ul = soup.find(id="main").find_all("ul")[2].find_all("li")
                    counter = 0
                    for el in ul:
                        if counter >= limit:
                            break
                        author = ""
                        author_link = ""

                        name = el.find_all("a")[0].get_text()
                        download = el.find_all("a")[0]["href"]

                        # Где-то нет автора. Поэтому проходим дополнительным условием.
                        if len(el.find_all("a")) > 1:
                            author = el.find_all("a")[1].get_text()
                            author_link = el.find_all("a")[1]["href"]

                        book = Flibusta_book(
                            author=author,
                            name=name,
                            download_link=f"{self.url}{download}",
                            author_link=f"{self.url}{author_link}",
                            proxy_host=self.proxy_host,
                            proxy_port=self.proxy_port,
                        )
                        books.append(book)
                        counter += 1

        except aiohttp.ClientConnectorError as e:
            logging.error(f"aiohttp ClientConnectorError: {str(e)}")
        except Exception as e:
            logging.error(f"Some other error: {str(e)}")

        return books


async def main():
    ff = Flibusta(9052, "127.0.0.1")
    if await ff.check_connection():
        books = await ff.search_for_books(query="Python")
        for book in books:
            print(f"{book.name}   --- {book.download}")
            download_b = await book.download_book()
            print(download_b[1])
        print(len(books))


if __name__ == "__main__":
    asyncio.run(main())
