from .page import Page

class Book:
    def __init__(self, pdf_file_path):
        self.pdf_file_path = pdf_file_path
        self.pages:list[Page] = []
        self.hash = 0

    def add_page(self, page: Page):
        self.pages.append(page)