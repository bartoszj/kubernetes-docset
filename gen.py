#!/usr/local/bin/python3

import os
import sqlite3
from bs4 import BeautifulSoup


DOC_API_REFERENCE = "Kubernetes.docset/Contents/Resources/Documents/index.html"


def clean():
    with open(DOC_API_REFERENCE) as doc:
        soup = BeautifulSoup(doc, "lxml")

        # Remove sidebar
        div = soup.find("div", id="sidebar-wrapper")
        if div is not None:
            div.decompose()

        # Remove `page-content-wrapper` id
        page_content_wrapper = soup.find("div", id="page-content-wrapper")
        if page_content_wrapper is not None:
            del page_content_wrapper["id"]

        # Remove 'copyright' classes
        div = soup.find("div", class_="copyright")
        if div is not None:
            div.decompose()

        # Remove 'text-right' classes
        div = soup.find("div", class_="text-right")
        if div is not None:
            div.decompose()

        # Fix script paths
        scripts = soup.find_all("script")
        for script in scripts:
            if script["src"].startswith("/"):
                script["src"] = script["src"][1:]
        
        # Fix link paths
        links = soup.find_all("link")
        for link in links:
            if link["href"].startswith("/"):
                link["href"] = link["href"][1:]

        # Fix `body-content` css
        body = soup.find("div", class_="body-content")
        body['style'] = "margin-left: 0px; max-width: 100%; flex-basis: 100%;"

        changed_content = str(soup)

    with open(DOC_API_REFERENCE, "w") as f:
        f.write(changed_content)


def gen_index(cur):
    t = "Type"
    basename = os.path.basename(DOC_API_REFERENCE)
    blocked = [
        "api overview", "api groups", "workloads apis", "service apis", "config and storage apis", "metadata apis",
        "cluster apis", "definitions", "old api versions", "resource categories", "resource objects",
        "resource operations", "write operations", "create", "patch", "replace", "delete", "delete collection",
        "read operations", "read", "list", "list all namespaces", "watch", "watch list", "watch list all namespaces",
        "status operations", "patch status", "read status", "replace status", "ephemeralcontainers operations",
        "patch ephemeralcontainers", "read ephemeralcontainers", "replace ephemeralcontainers", "misc operations", "read scale",
        "replace scale", "patch scale", "create eviction", "proxy operations", "create connect portforward",
        "create connect proxy", "create connect proxy path", "delete connect proxy", "delete connect proxy path",
        "get connect portforward", "get connect proxy", "get connect proxy path", "head connect proxy",
        "head connect proxy path", "replace connect proxy", "replace connect proxy path", "read log", "rollback",
        "http request", "path parameters", "query parameters", "body parameters", "response", "workloads", "metadata",
        "cluster"]

    with open(DOC_API_REFERENCE) as doc:
        soup = BeautifulSoup(doc, "lxml")

        # Links from navigation menu
        # def find_elements(tag):
        #     return tag.name == "li" \
        #            and tag.has_attr("class") \
        #            and "nav-level-1" in tag["class"] \
        #            and "strong-nav" not in tag["class"]
        #
        # # Find all objects:
        # objects = soup.find_all(find_elements)
        # i = 0
        # c = len(objects)
        # for o in objects:
        #     i += 1
        #
        #     # Split text to extract data
        #     s = o.string.split(" ")
        #     name = s[0]
        #     version = s[1]
        #     api = s[2]
        #     fullname = f"{name} {version}"
        #     href_id = o.a['href'][1:]
        #     # print(f"{name} {version} \tid:{href_id}")
        #
        #     # For each object find a tag
        #     h1 = soup.find("h1", id=href_id)
        #     # print(h1)
        #
        #     # Add a special `a` tag
        #     section_tag = soup.new_tag("a")
        #     section_tag["name"] = f"//apple_ref/cpp/{t}/{fullname}"
        #     section_tag["class"] = "dashAnchor"
        #     # h1.insert_before(section_tag)
        #
        #     # Insert to index
        #     path = f"{basename}#{href_id}"
        #     cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (fullname, t, path))
        #     print(f"{i}/{c}")

        objects = soup.find_all(["h1", "h2", "h3"])
        objects = [o for o in objects if o.string.lower() not in blocked]
        i = 0
        c = len(objects)
        for o in objects:
            i += 1

            # Split text to extract data
            s = o.string.split(" ")
            name = s[0]
            version = s[1]
            api = s[2]
            fullname = f"{name} {version}"
            object_id = o['id']
            # print(f"{name} {version} \tid:{id}")

            # Add a special `a` tag
            section_tag = soup.new_tag("a")
            section_tag["name"] = f"//apple_ref/cpp/{t}/{fullname}"
            section_tag["class"] = "dashAnchor"
            o.insert_before(section_tag)

            # Insert to index
            path = f"{basename}#{object_id}"
            cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (fullname, t, path))
            # print(f"{i}/{c}")

        changed_content = str(soup)

    with open(DOC_API_REFERENCE, "w") as f:
        f.write(changed_content)


def main():
    db = sqlite3.connect('./docSet.dsidx')
    cur = db.cursor()

    try:
        cur.execute('DROP TABLE searchIndex;')
    except:
        pass

    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

    gen_index(cur)
    clean()

    db.commit()
    cur.execute("VACUUM;")
    db.close()


if __name__ == '__main__':
    main()
