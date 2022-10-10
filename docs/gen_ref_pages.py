"""Generate the code reference pages and navigation."""

from pathlib import Path

import mkdocs_gen_files
TOP_LEVEL_NAME = "staticmaps"
DIRECTORY = "reference"
SRC = "staticmaps"


def main() -> None:
    """
    main entry point
    """

    nav = mkdocs_gen_files.Nav()

    for path in sorted(Path(SRC).rglob("*.py")):
        module_path = path.relative_to(SRC).with_suffix("")

        doc_path = path.relative_to(SRC).with_suffix(".md")
        full_doc_path = Path(DIRECTORY, doc_path)

        parts = list(module_path.parts)
        # omit __init__, __main__, cli.py
        if parts[-1] in ["__init__", "__main__", "cli"]:
            continue

        if not parts:
            continue

        nav[parts] = doc_path.as_posix()

        with mkdocs_gen_files.open(full_doc_path, "w") as file_handle:
            ident = ".".join(parts)
            file_handle.write(f"::: {ident}")

        mkdocs_gen_files.set_edit_path(full_doc_path, path)
        # mkdocs_gen_files.set_edit_path(full_doc_path, Path("../") / path)

    with mkdocs_gen_files.open(f"{DIRECTORY}/SUMMARY.md", "w") as nav_file:
        nav_file.writelines(nav.build_literate_nav())


main()
