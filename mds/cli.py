import contextlib
import csv
import typing as t

import click
from numbers_parser import Document


@click.group()
def cli():
    pass


def _read_stories(file: str) -> t.Iterable[dict]:
    with open(file) as f:
        stories = [story for story in csv.DictReader(f) if story["mp3_url"]]
    stories = sorted(stories, key=lambda story: story["date"])
    yield from stories


@contextlib.contextmanager
def _create_doc(filename: str) -> t.Generator:
    doc = Document(
        table_name="Модель для сборки",
        num_header_cols=0,
        num_rows=1,
        num_cols=7,
    )
    yield doc
    doc.save(filename)


@cli.command()
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path(exists=False))
def generate_numbers_doc(input: str, output: str) -> None:
    DATE = 0
    AUTHOR = 1
    TITLE = 2
    LISTENED = 3
    MP3_URL = 4
    STORY_RATING = 5
    MUSIC_RATING = 6
    URL = 7

    with _create_doc(output) as doc:
        table = doc.sheets[0].tables[0]
        table.write(0, DATE, "Дата")
        table.write(0, AUTHOR, "Автор")
        table.write(0, TITLE, "Название")
        table.write(0, LISTENED, "Просл.")
        table.write(0, MP3_URL, "Запись")
        table.write(0, STORY_RATING, "Рассказ")
        table.write(0, MUSIC_RATING, "Музыка")
        table.write(0, URL, "Ссылка")

        table.col_width(DATE, 70)
        table.col_width(AUTHOR, 120)
        table.col_width(TITLE, 180)
        table.col_width(LISTENED, 50)
        table.col_width(MP3_URL, 200)
        table.col_width(STORY_RATING, 100)
        table.col_width(MUSIC_RATING, 100)
        table.col_width(URL, 250)

        for i, story in enumerate(_read_stories(input), 1):
            table.write(i, DATE, story["date"])
            table.write(i, AUTHOR, story["author"])
            table.write(i, TITLE, story["title"])
            table.write(i, LISTENED, False)
            table.write(i, MP3_URL, f'=HYPERLINK("{story["mp3_url"]}")')
            table.write(i, STORY_RATING, 0)
            table.write(i, MUSIC_RATING, 0)
            table.write(i, URL, f'=HYPERLINK("{story["url"]}")')

            table.set_cell_formatting(i, LISTENED, "tickbox")
            table.set_cell_formatting(i, STORY_RATING, "rating")
            table.set_cell_formatting(i, MUSIC_RATING, "rating")


if __name__ == "__main__":
    cli()
