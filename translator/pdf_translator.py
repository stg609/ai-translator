import tiktoken
from typing import Optional
from model import Model, OpenAIModel
from translator.pdf_parser import PDFParser
from translator.writer import Writer
from utils import LOG


class PDFTranslator:
    __cache = {}

    def __init__(self, model: Model):
        self.model = model
        self.pdf_parser = PDFParser()
        self.writer = Writer()

        if isinstance(model, OpenAIModel):
            openai_model: OpenAIModel = model
            self.__tiktoken_encoding = tiktoken.encoding_for_model(
                openai_model.model)

    def translate_pdf(self, pdf_file_path: str, file_format: str = 'PDF', target_language: str = '中文', output_file_path: str = None, start: Optional[int] = None, end: Optional[int] = None) -> int:
        self.book = self.pdf_parser.parse_pdf(pdf_file_path, start, end)
        cache_key = f"{self.book.hash}-{file_format}-{target_language}"
        if cache_key in PDFTranslator.__cache:
            LOG.info("return from cache")
            self.writer.save_translated_book(
                self.__cache[cache_key], output_file_path, file_format)
            return 0

        token_num = -1
        for page_idx, page in enumerate(self.book.pages):
            for content_idx, content in enumerate(page.contents):
                prompt = self.model.translate_prompt(content, target_language)
                
                if self.__tiktoken_encoding:
                    token_num = len(self.__tiktoken_encoding.encode(prompt))
                LOG.debug(f"Prompt:{prompt},Token number:{token_num}")

                translation, status = self.model.make_request(prompt)
                if self.__tiktoken_encoding:
                    token_num += len(self.__tiktoken_encoding.encode(translation))
                LOG.info(f"Answer:{translation}, Token number:{token_num}")

                # Update the content in self.book.pages directly
                self.book.pages[page_idx].contents[content_idx].set_translation(
                    translation, status)

        self.writer.save_translated_book(
            self.book, output_file_path, file_format)

        PDFTranslator.__cache[cache_key] = self.book

        return token_num
