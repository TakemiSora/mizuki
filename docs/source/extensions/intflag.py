from sphinx.application import Sphinx
from sphinx.ext.autodoc import ClassDocumenter


def add_lines(instance: ClassDocumenter, *lines: str, source: str) -> None:
    for line in lines:
        instance.add_line(line, source)


class IntFlagDocumenter(ClassDocumenter):
    objtype = "intflag"
    directivetype = "class"

    def add_content(self, more_content):
        super().add_content(more_content)
        source_name = self.get_sourcename()

        members = sorted(
            self.object.__members__.items(),
            key=lambda pair: pair[1].value,
        )

        add_lines(
            self,
            "",
            ".. list-table::",
            "   :header-rows: 1",
            "",
            "   * - Name",
            "     - Bit",
            source=source_name,
        )

        for name, member in members:
            add_lines(
                self,
                f"   * - {name}",
                f"     - {member.value.bit_length() - 1}",
                source=source_name,
            )

        self.add_line("", source_name)


def setup(app: Sphinx) -> None:
    app.add_autodocumenter(IntFlagDocumenter)
