#!/usr/local/bin/python2

import os, re, sqlite3
from bs4 import BeautifulSoup, NavigableString, Tag

docpath = 'Documents/api-reference'

def gen_index(cur, filename, typ):
    doc = open(os.path.join(docpath, filename))
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
    for tp in os.walk(docpath):
        if len(tp[1]) == 0:
            files.extend([os.path.join(tp[0], i) for i in tp[2]])
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

    for filename in iterate_dir(docpath):
        #gen_index("v1/operations.html", "Interface")
        relpath = filename[len(docpath)+1:]
        if relpath.endswith("definitions.html"):
            gen_index(cur, relpath, "Type")
        elif relpath.endswith("operations.html"):
            gen_index(cur, relpath, "Interface")

    db.commit()
    db.close()


if __name__ == '__main__':
    main()
