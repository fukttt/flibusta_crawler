# Класс работы с сайтом Flibusta
# написан исключительно в целях обучения написания библиотек
#
import logging, sys
import asyncio, aiohttp
from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector
from bs4 import BeautifulSoup


logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class Flibusta_book:
    __type = "Flibusta_book"

    def __init__(self, author: str, name: str, download_link: str, author_link: str):
        self.author = author
        self.name = name
        self.download = download_link
        self.author_link = author_link


class Flibusta:
    """
    Главный класс для инициализации. \n
    Имеет такие настройки как: \n
    :param tor_proxy: Tor прокся для доступа к онион ссылкам (пример `127.0.0.1:9051`).
    :param busta_url: Onion линк на Flibusta (default `flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion`).
    :param timeout: таймаут запросов (default `5`).
    :return: объект с функциями для работы с книгами.
    """

    __type = "Flibusta"

    def __init__(
        self,
        tor_proxy: str,
        busta_url: str = "flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion",
        timeout: int = 5,
    ):
        self.url = f"http://{busta_url}"
        self.tor_proxy = {  # Прокси для доступа к сайту.
            "http": f"socks5h://{tor_proxy}",
            "https": f"socks5h://{tor_proxy}",
        }
        self.headers = {"User-Agent": "py/flibusta-crawler", "Accept": "*/*"}

    async def check_connection(self) -> bool:
        """
        Функция проверки подключения к сайту.
        :return: True если все ок.
        """
        try:
            async with self.get_tor_session() as session:
                await session.get(f"{self.url}/", headers=self.headers)
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
            proxy_type=ProxyType.SOCKS5, host="127.0.0.1", port=9052
        )
        session = aiohttp.ClientSession(connector=connector)
        return session

    async def search_for_books(self, query: str) -> list[Flibusta_book]:
        """
        Поиск
        """
        books = []
        try:
            async with self.get_tor_session() as session:
                req = await session.get(
                    f"{self.url}/booksearch?ask={query}",
                    headers=self.headers,
                )
                resp_text = await req.text()
                soup = BeautifulSoup(resp_text, "html.parser")
                ul = soup.find(id="main").find_all("ul")[2].find_all("li")
                for el in ul:
                    if el:
                        book = Flibusta_book(
                            author=el.find_all("a")[1].get_text(),
                            name=el.find_all("a")[0].get_text(),
                            download_link=el.find_all("a")[0]["href"],
                            author_link=el.find_all("a")[1]["href"],
                        )
                        books.append(book)
        except IndexError:
            # Пассим ошибку, если где-то не хватает автора или названия.
            # Пока без понятия как ловить умнее )
            pass
        except aiohttp.ClientConnectorError as e:
            logging.error(f"aiohttp ClientConnectorError {str(e)}")
        except Exception as e:
            logging.error(f"Some other error {str(e)}")

        return books


async def main():
    ff = Flibusta("127.0.0.1:9052")
    if await ff.check_connection():
        books = await ff.search_for_books(query="Python")
        for book in books:
            print(book.name)
        print(len(books))


if __name__ == "__main__":
    asyncio.run(main())
