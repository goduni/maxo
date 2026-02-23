import re
import sys
import tomllib
from pathlib import Path
from typing import cast

# We need `maxo` to be importable from here:
_ROOT = Path("..").resolve(strict=True)
sys.path.insert(0, str(_ROOT))


# ----- Project Information -----

def _get_project_meta() -> dict[str, str]:
    pyproject = _ROOT / "pyproject.toml"
    return cast(
        dict[str, str],
        tomllib.loads(pyproject.read_text())["project"],
    )


pkg_meta = _get_project_meta()
project = str(pkg_meta["name"])

copyright = "2026, Kirill Lesovoy"
author = "Kirill Lesovoy"
version = str(pkg_meta["version"])
release = version

# ----- General configuration -----

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    # https://github.com/executablebooks/MyST-Parser
    "myst_parser",
    # 3rd party, order matters:
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx_contributors",
    "sphinx_tabs.tabs",
    "sphinx_iconify",
    "sphinxcontrib.mermaid",
]

# Napoleon:
napoleon_google_docstring = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_attr_annotations = True
napoleon_use_param = True
napoleon_use_ivar = True

# Autodoc settings
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_class_signature = "separated"
autodoc_default_options = {
    "undoc-members": True,
    "exclude-members": "__init__",
}


def setup(app):
    app.connect("autodoc-process-docstring", fix_docstring, priority=400)


def fix_docstring(app, what, name, obj, options, lines):
    """Исправляет Markdown, убирает дублирование и экранирует спецсимволы Sphinx."""
    if not lines:
        return

    # Только для наших модулей
    if not name.startswith("maxo"):
        return

    is_method = name.startswith("maxo.bot.methods")
    is_type = name.startswith("maxo.types")

    if not hasattr(app, "_method_args"):
        app._method_args = {}

    class_name = name if what == "class" else ".".join(name.split(".")[:-1])

    new_lines = []
    in_code = False
    in_args = False

    for line in lines:
        s = line.strip()

        # 1. Исправление списков (rST требует пустой строки перед списком)
        if s.startswith("- ") and new_lines and new_lines[-1].strip() != "":
            new_lines.append("")

        # 2. Обработка секции Args
        if (is_method or is_type) and s == "Args:":
            in_args = True
            continue

        if in_args:
            if s == "" or s.startswith("Источник:") or s.startswith("Example:") or s.startswith(".. "):
                in_args = False
                if s: new_lines.append(line)
            else:
                m = re.match(r"^([a-z0-9_]+)\s*:\s*(.*)", s, re.IGNORECASE)
                if m:
                    arg_name, arg_desc = m.groups()
                    if class_name not in app._method_args:
                        app._method_args[class_name] = {}
                    app._method_args[class_name][arg_name] = arg_desc.strip()
                continue

        # 3. Превращаем Markdown заголовки ## в rST стиль
        if s.startswith("## "):
            title = s[3:]
            new_lines.append(title)
            new_lines.append("-" * len(title))
            new_lines.append("")
            continue

        # 4. Исправляем блоки кода (``` -> .. code-block::)
        if s.startswith("```"):
            if not in_code:
                lang = s.replace("`", "").strip() or "bash"
                if new_lines and new_lines[-1].strip():
                    new_lines.append("")
                new_lines.append(f".. code-block:: {lang}")
                new_lines.append("")
                in_code = True
            else:
                in_code = False
                new_lines.append("")
            continue

        if in_code:
            new_lines.append("    " + line)
        else:
            # 5. Экранирование и конвертация Markdown -> rST
            # Конвертируем одинарные обратные кавычки в двойные (inline code)
            processed_line = re.sub(r"(?<!`)`([^`\n]+)`(?!`)", r"``\1``", line)

            # Экранируем висячие подчеркивания и звездочки
            processed_line = re.sub(r"(?<!\\)([_*])", r"\\\1", processed_line)

            # Удаляем только висячую кавычку в конце, если она не часть пары
            if processed_line.count("`") % 2 != 0:
                processed_line = re.sub(r"(?<!`)(`)\s*$", r"\\`", processed_line)

            new_lines.append(processed_line)

    # 6. Подставляем описание атрибута, если оно пустое
    if (is_method or is_type) and what in ("attribute", "variable"):
        if not any(l.strip() for l in new_lines):
            attr_name = name.split(".")[-1]
            if class_name in app._method_args and attr_name in app._method_args[class_name]:
                desc = app._method_args[class_name][attr_name]
                # Обрабатываем описание так же
                desc = re.sub(r"(?<!`)`([^`\n]+)`(?!`)", r"``\1``", desc)
                desc = re.sub(r"(?<!\\)([_*])", r"\\\1", desc)
                new_lines.append(desc)

    lines[:] = new_lines


# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
}

# MyST settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
myst_heading_anchors = 3

# Set `typing.TYPE_CHECKING` to `True`:
# https://pypi.org/project/sphinx-autodoc-typehints/
set_type_checking_flag = True

language = "ru"

# Theme options
html_theme = "shibuya"

html_static_path = ["_static"]
html_logo = "_static/maxo-logo.png"

html_favicon = "_static/maxo-logo.png"

html_theme_options = {
    "github_url": "https://github.com/k1rl3s/maxo",
    "readthedocs_url": "https://maxo.readthedocs.io",
    "globaltoc_expand_depth": 2,
    "nav_links": [
        {
            "title": "PyPI",
            "url": "https://pypi.org/project/maxo/",
        },
        {
            "title": "DeepWiki",
            "url": "https://deepwiki.com/k1rl3s/maxo",
        },
    ],
    "accent_color": "green",
    "dark_logo": "_static/maxo-logo.png",
}

html_context = {
    "source_type": "github",
    "source_user": "k1rl3s",
    "source_repo": "maxo",
    "source_version": "master",
}
