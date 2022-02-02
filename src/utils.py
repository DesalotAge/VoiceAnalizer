"""Define all basic functionality."""
import requests
from pathlib import Path
from typing import List
from bs4 import BeautifulSoup


def create_texts_directory() -> None:
    """Create texts directory."""
    texts_directory = Path('./source/texts')
    texts_directory.mkdir(parents=True, exist_ok=True)


def create_all_texts(new_text_id: int = 1) -> int:
    """Load all text, return value of loaded texts."""
    create_texts_directory()
    first_possible_text = Path('./source/texts/1.txt')

    if first_possible_text.is_file():
        return quantity_of_texts()

    TATAR_TEXT_URL = 'http://klavogonki.ru/vocs/141412/'
    RUSSIAN_TEXT_URL = 'http://klavogonki.ru/vocs/12726/'

    def get_texts_via_url(url: str) -> List[str]:
        """Return all texts from given url."""
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        return list(map(lambda x: str(x.text), soup.findAll('td', class_='text')))

    ALL_URLS = [TATAR_TEXT_URL, RUSSIAN_TEXT_URL]

    for url in ALL_URLS:
        for text in get_texts_via_url(url):
            file = Path(f'./source/texts/{new_text_id}.txt')
            file.touch()
            file.write_text(text)
            new_text_id += 1
    return new_text_id


def quantity_of_texts() -> int:
    """Return id of last created text."""
    left, right = 1, 10 ** 10
    while right - left > 1:
        m = (right + left) // 2
        file = Path(f'./source/texts/{m}.txt')
        if file.is_file():
            left = m
        else:
            right = m
    return left


if __name__ == "__main__":
    print(create_all_texts())
