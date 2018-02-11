#!/usr/local/bin/python3

import os
import sqlite3
from bs4 import BeautifulSoup


DOC_API_REFERENCE = "Kubernetes.docset/Contents/Resources/Documents/api-reference"


def fix_links(filename):
    doc_path = os.path.join(DOC_API_REFERENCE, filename)
    changed_content = None

    with open(doc_path) as doc:
        soup = BeautifulSoup(doc, "html.parser")

        def find_definitions(href):
            return href.startswith("../definitions#")

        changed = False
        a_tags = soup.find_all("a", href=find_definitions)
        for a in a_tags:
            changed = True
            a["href"] = a["href"].replace("../definitions#", "definitions.html#")

        if changed:
            changed_content = str(soup)

    if changed_content is not None:
        with open(doc_path, "w") as f:
            f.write(changed_content)


def gen_index(cur, filename, typ):
    doc = open(os.path.join(DOC_API_REFERENCE, filename))
    soup = BeautifulSoup(doc, "html.parser")
    group, version = parse_group_version_from_filename(filename)

    for div in soup.find_all('div', {'class': "sect2"}):
        try:
            name = div.h3.string
            if len(group) == 0:
                fullname = "%s/%s" % (version, name)
            else:
                fullname = "%s/%s/%s" % (group, version, name)
            path = os.path.join("api-reference", filename) + "#" + div.h3.attrs["id"]
            cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (fullname, typ, path))
        except:
            continue


def iterate_dir(dir_name):
    files = []
    for dir_path, dir_names, file_names in os.walk(dir_name):
        if len(dir_names) == 0:
            files.extend([os.path.join(dir_path, i) for i in file_names])
    return files


def parse_group_version_from_filename(filename):
    spl = filename.split("/")
    if len(spl) == 3:
        group = spl[0]
        version = spl[1]
    elif len(spl) == 2:
        group = ""
        version = spl[0]
    else:
        raise Exception("bad filename: %s", filename)
    return group, version


def main():
    db = sqlite3.connect('./docSet.dsidx')
    cur = db.cursor()

    try:
        cur.execute('DROP TABLE searchIndex;')
    except:
        pass

    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

    for filename in iterate_dir(DOC_API_REFERENCE):
        relative_path = filename[len(DOC_API_REFERENCE) + 1:]
        if relative_path.endswith("definitions.html"):
            gen_index(cur, relative_path, "Type")
        elif relative_path.endswith("operations.html"):
            fix_links(relative_path)
            gen_index(cur, relative_path, "Interface")

    db.commit()
    cur.execute("VACUUM;")
    db.close()


if __name__ == '__main__':
    main()
