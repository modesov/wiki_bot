import uuid

import wikipediaapi
import hashlib
from aiogram.client.session import aiohttp

from config.texts import not_find_text
from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.utils.formatting import Bold


class Wiki:
    url_api = 'https://ru.wikipedia.org/w/api.php'

    def __init__(self, *, text_search: str):
        self.__found_options = None
        self.__text_search = text_search
        self.__info = None
        self.__sections = []

    async def init(self):
        try:
            wiki = wikipediaapi.Wikipedia(user_agent='WikiTelegramBot (msdenimod@yandex.ru)', language='ru',
                                          extract_format=wikipediaapi.ExtractFormat.WIKI)
            page = wiki.page(self.__text_search)

            if not page.exists():
                modification_str = self.clearStr(self.__text_search)
                variant = list(
                    filter(lambda item: self.clearStr(item) == modification_str, await self.getFoundOptions()))

                if len(variant):
                    self.__text_search = variant[0]
                    self.__found_options = []
                    page = wiki.page(self.__text_search)

            if page.exists():
                full_text = page.summary.split('\n')
                count_chunk = len(full_text)
                info = f'{Bold(f"Резюме по запросу «{self.__text_search}»").as_html()} \n\n {full_text[0]}{"..." if count_chunk > 1 else ""}'
                continuation = full_text[1:]
                continuation = list(filter(lambda chunk: chunk, continuation))
                continuation_text = '\n'.join(continuation)
                self.__info = info
                if count_chunk > 1:
                    self.__sections.append({
                        'title': '...продолжение резюме',
                        'slug': 'summary',
                        'text': f'{Bold("Резюме (продолжение)").as_html()} \n\n {continuation_text}',
                        'parent': ''
                    })
                self.setSections(sections=page.sections)
        except BaseException as inst:
            print(inst, type(inst))

    async def getInfo(self):
        return self.__info or not_find_text

    async def getFoundOptions(self):
        if self.__found_options is None:
            result = await self.openSearch(text_search=self.__text_search)
            self.__found_options = result[1]

        return self.__found_options

    def setSections(self, *, sections, parent=''):
        for section in sections:
            uid = uuid.uuid4().hex + section.title
            self.__sections.append({
                'title': section.title,
                'slug': hashlib.md5(uid.encode('utf-8')).hexdigest(),
                'text': f'{Bold(section.title).as_html()} \n\n {section.text}',
                'parent': parent
            })
            self.setSections(sections=section.sections, parent=section.title)

    def getSections(self):
        return self.__sections

    def getButtons(self, *, parent: str = ''):
        keyword = InlineKeyboardBuilder()
        sections = list(filter(lambda section: section['parent'] == parent, self.__sections))
        if len(sections):
            for item in sections:
                keyword.add(InlineKeyboardButton(text=item['title'],
                                                 callback_data=f"btn_section:{item['slug']}"))
        elif not len(self.__sections) and self.__found_options:
            found_options_kb = ReplyKeyboardBuilder()
            for item in self.__found_options:
                found_options_kb.add(KeyboardButton(text=item))
            return found_options_kb.adjust(1).as_markup(resize_keyboard=True)
        elif not len(self.__sections):
            return None

        if len(parent):
            current_section = list(filter(lambda section: section['title'] == parent, self.__sections))
            current_section = current_section[0] if len(current_section) else None

            if current_section is not None:
                previous_section = list(
                    filter(lambda section: section['title'] == current_section['parent'], self.__sections))
                previous_section = previous_section[0] if len(previous_section) else None

                slug = previous_section['slug'] if previous_section else 'main_menu_slug'

                keyword.add(
                    InlineKeyboardButton(text='Назад', callback_data=f'btn_section:{slug}'))

        return keyword.adjust(1).as_markup()

    @staticmethod
    def getPagination(*, count: int, current_page: int):
        callback_data = 'pagination_previous' if current_page > 1 else 'pagination_back'
        keyword = InlineKeyboardBuilder()
        keyword.add(InlineKeyboardButton(text='Назад', callback_data=callback_data))

        if current_page < count:
            keyword.add(InlineKeyboardButton(text='Далее', callback_data='pagination_next'))

        return keyword.adjust(2).as_markup()

    def getSectionBySlug(self, *, slug: str):
        res = list(filter(lambda section: section['slug'] == slug, self.__sections))
        return res[0] if len(res) else None

    def getSectionByTitle(self, *, title: str):
        res = list(filter(lambda section: section['title'] == title, self.__sections))
        return res[0] if len(res) else None

    async def openSearch(self, *, text_search: str):
        url = f'{self.url_api}?action=opensearch&format=json&formatversion=2&search={text_search}&namespace=0&limit=10'
        async with aiohttp.ClientSession() as session:
            return await self.fetch(url=url, session=session)

    @staticmethod
    async def fetch(*, url: str, session: aiohttp.ClientSession):
        async with session.get(url) as response:
            return await response.json()

    @staticmethod
    def clearStr(s: str) -> str:
        return s.lower().strip().replace(' ', '').replace('-', '').replace('_', '')
