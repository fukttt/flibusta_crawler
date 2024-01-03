# Класс работы с сайтом Flibusta
# написан исключительно в целях обучения написания библиотек
# 

class Flibusta():
    """
    Главный класс для инициализации. \n
    Имеет такие настройки как: \n
    :param tor_proxy: Tor прокся для доступа к онион ссылкам (пример `127.0.0.1:9051`).
    :param busta_url: Onion линк на Flibusta (default `flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion`).
    :return: объект с функциями для работы с книгами. 
    """
    __type = "Flibusta"
    def __init__( self, tor_proxy: str, busta_url: str = "flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion"):
        self.url = busta_url
        self.tor_proxy =  tor_proxy
    
    def check_connection(self) -> bool:
        """
        Функция проверки 
        """
        return True

if __name__ == "__main__":
    ff = Flibusta("127.0.0.1:9050")
    ff.check_connection()
        