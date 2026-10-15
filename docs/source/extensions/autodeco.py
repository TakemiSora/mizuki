from sphinx.application import Sphinx
from sphinx.ext.autodoc import DecoratorDocumenter


class AutoDecoratorDocumenter(DecoratorDocumenter):
    priority: int = DecoratorDocumenter.priority + 10
    objtype: str = "customdeco"

    @classmethod
    def can_document_member(cls, member, *_) -> bool:
        return getattr(member, "_is_decorator", False)


def setup(app: Sphinx) -> None:
    app.add_autodocumenter(AutoDecoratorDocumenter)
