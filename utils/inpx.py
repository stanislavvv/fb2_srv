# -*- coding: utf-8 -*-

import zipfile
import os


def array_strip_empty(arr):
    ret = []
    for v in arr:
        if v is not None:
            if isinstance(v, str):
                if v != "":
                    ret.append(v)
            else:
                ret.append(v)
    return ret


def authors2fields(authors):
    ret = []
    for a in authors:
        au = a.split(',')
        if len(au) >= 4:
            ret.append(
                {
                    "last-name": au[0],
                    "first-name": au[1],
                    "middle-name": au[2],
                    "nick-name": au[3]
                }
            )
        elif len(au) == 3:
            ret.append(
                {
                    "last-name": au[0],
                    "first-name": au[1],
                    "middle-name": au[2]
                }
            )
        elif len(au) == 2:
            ret.append(
                {
                    "last-name": au[0],
                    "first-name": au[1]
                }
            )
        else:
            ret.append(
                {
                    "last-name": au[0]
                }
            )
    return ret


def get_line_fields(line):
    r = {}
    li = line.split("\004")
    if len(li) >= 11:
        r["authors"] = authors2fields(
            array_strip_empty(li[0].split(":"))
        )
        r["genres"] = array_strip_empty(li[1].split(":"))
        r["book-title"] = li[2]
        r["sequences"] = li[3]
        r["seq_num"] = li[4]
        r["lang"] = li[11]
        return li[5] + ".fb2", r
    else:
        return None, None


def get_inpx_meta(inpx_data, zip_file):
    ret = {}
    inp_file = os.path.basename(zip_file).replace(".zip", ".inp")

    z = zipfile.ZipFile(inpx_data)
    try:
        f = z.open(inp_file, "r")
        line = f.readline().decode('utf-8').strip("\r").strip("\n")
        while len(line) > 10:
            fb2, meta = get_line_fields(line)
            ret.update({fb2: meta})
            line = f.readline().decode('utf-8').strip("\r").strip("\n")
        f.close()
    except Exception as e:
        print(e)
    return ret
