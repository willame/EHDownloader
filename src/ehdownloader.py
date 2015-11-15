#!/usr/bin/python3

# modules
import os
import re
import sys
import json
import time
import math
import signal
import random
import argparse
import urllib.parse
import urllib.request
import xml.sax.saxutils

# mymodule
try:
    script_path = os.path.realpath(__file__)
except:
    script_path = os.path.realpath(sys.argv[0])
script_path = os.path.abspath(script_path)
root_path = os.path.dirname(script_path)
sys.path.append(script_path)
import agent

# global variables
user_agent = random.choice(agent.agent_list)


# exception
class ContentWarningException (Exception):
    def __str__ (self):
        return("Content Warning Exception\n")


# functions
def save_image(img_url, img_path):
    global user_agent

    try:
        for _ in range(5):
            req = urllib.request.Request(
                img_url,
                data=None,
                headers={
                    'User-Agent': user_agent
                }
            )

            with urllib.request.urlopen(req) as img:
                localfile = open(img_path, 'wb')
                localfile.write(img.read())
                img.close()
                localfile.close()

            return True

    except KeyboardInterrupt:
        return False

    except:
        time.sleep(1)
        pass

    print("Error: Image download error.")
    return False


def get_html(url, warn_check=False):
    global user_agent
    page_html = ""

    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'User-Agent': user_agent
        }
    )

    with urllib.request.urlopen(req) as page:
        for line in page.readlines():
            page_html += line.decode('utf-8')

    if warn_check:
        m = re.search("<h1>Content Warning</h1>", page_html)
        if not m is None:
            raise ContentWarningException

    return page_html


def ehentai_get_gurl(html):
    m1 = re.search("http://g.e-hentai.org/g/.*", url)
    if not m1 is None:
        return url

    m2 = re.search("http://g.e-hentai.org/s/.*", url)
    if not m2 is None:
        m2_g = re.search("<div class=\"sb\"><a href=\"(.*?)\">", html)
        if not m2_g is None:
            return m2_g.group(1)

    return ""


def ehentai_get_topurl(html):
    m1 = re.search("http://g.e-hentai.org/g/.*", url)
    if not m1 is None:
        pat1 = "<div style=\".*?\"><a href=\"(.*)?\"><img alt=\"0*1\""
        m1_top = re.search(pat1, html)
        if not m1_top is None:
            return m1_top.group(1)

    m2 = re.search("http://g.e-hentai.org/s/.*", url)
    if not m2 is None:
        pat2 = "<div class=\"sn\"><a onclick=\".*?\" href=\"(.*?)\">"
        m2_top = re.search(pat2, html)
        if not m2_top is None:
            return m2_top.group(1)

    return ""


def ehentai_get_title(html):
    entites = {}

    # for file-name in windows
    if sys.platform == "win32":
        entities = {
            "&#039;": "’",
            "&quot;": "”",
            "?"     : "？",
            "&yen;" : "￥",
            "*"     : "＊",
            ";"     : "；",
            "&lt;"  : "＜",
            "&gt;"  : "＞",
            "|"     : "｜",
            "&amp;" : "&"
        }
    else:
        entities = {
            "&#039;": "'",
            "&quot;": '"',
            "&lt;"  : "<",
            "&gt;"  : ">",
            "&amp;" : "&"
        }

    m1 = re.search("<h1 id=\"gj\">(.+?)</h1>", html)
    if not m1 is None:
        tmp = m1.group(1)
        title = xml.sax.saxutils.unescape(tmp, entities)
        return title

    m2 = re.search("<h1 id=\"gn\">(.+?)</h1>", html)
    if not m2 is None:
        tmp = m2.group(1)
        title = xml.sax.saxutils.unescape(tmp, entities)
        return title

    m3 = re.search("<title>(.+?)</title>", html)
    if not m3 is None:
        tmp = m3.group(1)
        title = xml.sax.saxutils.unescape(tmp, entities)
        return title

    return "Unknown"


def ehentai_get_numimgs(html):
    num = 0
    pat = "<div><span>1</span> / <span>(.*?)</span></div>"
    m = re.search(pat, html)
    if not m is None:
        num = int(m.group(1))

    return num


def ehentai_get_imginfo(html):
    img_name = ""
    img_size = 0
    img_byte_size = 0

    pat = "<img src=\".*?\" /></a></div><div>(.*?) :: .*? :: (.*?)([KMGT]?B)</div>"
    m = re.search(pat, html)
    if not m is None:
        img_name = m.group(1)
        img_size = float(m.group(2).strip())
        img_bpref = m.group(3)

    units = [('B',0),('KB',1),('MB',2),('GB',3),('TB',4)]
    for i, j in units:
        if i == img_bpref:
            img_byte_size = img_size * pow(1024, j)
            break

    return img_name, img_byte_size


def get_input_urls(input_str, flag_urlonly=False):
    pat1 = "http://g.e-hentai.org/.*"
    pat2 = "https://g.e-hentai.org/.*"

    if flag_urlonly:
        m1 = re.search(pat1, input_str)
        if not m1 is None:
            return [input_str]

        m2 = re.search(pat2, input_str)
        if not m2 is None:
            print("HTTPS access is not permitted in E-Hentai Gallery.")
            print("Please input url starts with \"http://\".")
            sys.exit(1)

        print("Error: URL is invalid.")
        sys.exit(1)
    else:
        urls = []
        if os.path.exists(input_str):
            f = open(input_str, "r")
            for line in f.readlines():
                tmp_str = line.strip()
                if tmp_str[0] == "#":
                    continue
                else:
                    m = re.search(pat1, tmp_str)
                    if not m is None:
                        urls.append(tmp_str)

            return urls
        else:
            print("Error: Input file of urls is not found.\n")
            sys.exit(1)

    return []


def check_file_corruption(img_size, img_path):
    diff_size = abs(img_size - os.path.getsize(img_path))
    if diff_size < 0.001 * img_size:
        return False
    else:
        return True


def ehentai_get_nexturl(html):
    pat = "<a id=\"next\" onclick=\".*?\" href=\"(.*?)\">"
    m_next = re.search(pat, html)
    if not m_next is None:
        next_url = m_next.group(1)
        return next_url

    return ""


def create_report(page_info):
    json_data = json.dumps(page_info)
    f = open(page_info["report_path"], "w")
    f.write(json_data)
    f.close()
    return


def ehentai_download(save_path, page_info):
    count = 0
    count_retry = 0
    interval = 0

    url        = page_info["top_url"]
    flags      = page_info["flags"]
    num_images = page_info["num_images"]

    if len(page_info["gal_urls"]) > 0:
        url   = page_info["gal_urls"][-1]
        count = len(page_info["gal_urls"])

    if count == num_images:
        print("\nSuccess: Finish downloading!\n")
        time.sleep(1)
        return True

    if not page_info["interval"] is None:
        interval = page_info["interval"]
    else:
        interval = math.sqrt(num_images*2) / 5
        if interval > 5: interval = 5

    # download operation
    while count < num_images:

        # count of retry
        if count_retry > 10:
            break

        # save state
        if not "no-backup" in flags and count % 10 == 0:
            create_report(page_info)

        # get html
        try:
            html = get_html(url)
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nNotice: You press Ctrl+C, and now quit...")
            create_report(page_info)
            sys.exit(1)
        except:
            print("Error: HTML document download error.")
            count_retry += 1
            continue

        if html == "":
            count_retry += 1
            continue

        m_img = re.search("<img id=\"img\" src=\"(.*?)\" style=\".*?\" />", html)

        if not m_img is None:
            img_url = m_img.group(1)
            img_url = xml.sax.saxutils.unescape(img_url)

            orig_name, img_size = ehentai_get_imginfo(html)
            _, ext = os.path.splitext(orig_name)

            img_name = ""
            if "no-numbering" in flags:
                img_name = orig_name
            else:
                img_name = "{0:03d}{1}".format(count+1, ext)

            img_path = os.path.join(save_path, img_name)

            flag_save = True
            if os.path.exists(img_path):
                if not "no-filecheck" in flags and check_file_corruption(img_size, img_path):
                    print("Caution: File-size is invalid.")
                    print("Now, attempt to retry download...")
                else:
                    print("{0:03d} : {1} ... already exists".format(count+1, img_url))
                    flag_save = False

            if flag_save:
                ok = save_image(img_url, img_path)
                if not ok:
                    count_retry += 1
                    continue

                if not "no-filecheck" in flags and check_file_corruption(img_size, img_path):
                    print("Caution: File-size is invalid.")
                    print("Now, attempt to retry download...")
                    count_retry += 1
                    continue

                print("{0:03d} : {1} ... save".format(count+1, img_url))

            count += 1
            count_retry = 0
            next_url = ehentai_get_nexturl(html)
            if next_url == "":
                break

            if url == next_url or count == num_images:
                print("\nSuccess: Finish downloading!\n")
                time.sleep(1)
                return True
            else:
                url = next_url
                page_info["gal_urls"].append(next_url)

    return False


def sequence_download(page_info):
    # make new directory
    save_path = os.path.join(page_info["save_path"], page_info["title"])
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # show download options
    print("< Download Options >")
    print(flags)
    print()

    # print input urls
    print("< List of Remaining URLs >")
    for url in page_info["remain_urls"]:
        print(url)
    print()

    # print information
    print("\n< Page Information >")
    print("URL : {0}".format(page_info["top_url"]))
    print("Title : {0}".format(page_info["title"]))
    print("Total of Images : {0}".format(page_info["num_images"]))
    if len(page_info["gal_urls"]) > 0:
        print("Downloaded : {0} ({1:.1f}%)".format(
                len(page_info["gal_urls"]),
                len(page_info["gal_urls"]) * 100 / page_info["num_images"]
            ))
    print()

    # download images
    ok = ehentai_download(save_path, page_info)

    # resume download
    retry_count = 0
    while not ok:
        if retry_count >= page_info["retry"]:
            create_report(page_info)
            return False

        create_report(page_info)
        print("\nNotice: Retry limit exceeded. Now, Sleep...")
        print("Sleep time: {0} sec".format(page_info["sleep"]))
        time.sleep(page_info["sleep"])
        ok = ehentai_download(save_path, page_info)
        retry_count += 1

    return True


# first input
def prompt_url_input():
    input_str = ""
    try:
        while not re.match("https?://.+", input_str):
            print("Please input URL of E-Hentai Page.")
            input_str = input("URL > ")
            input_str.strip()
        print()
    except KeyboardInterrupt:
        print("\nNotice: You press Ctrl+C, and now quit...")
        sys.exit(1)
    except:
        print("\nNotice: Exception is detected.")
        sys.exit(1)

    return input_str


# main function
if __name__ == '__main__':

    # variables
    page_info = {}
    flags = []
    input_urls = []
    flag_resume = False
    flag_recursive = False
    flag_useflask = False


    # file path
    report_path = os.path.join(root_path, "interrupt-report.json")

    save_path = ""
    store_path = ["~/Pictures", "~/Picture", "~/ピクチャ", os.getcwd()]
    for i in store_path:
        tmp = os.path.expanduser(i)
        if os.path.exists(tmp):
            save_path = os.path.join(tmp, "E-Hentai_downloads")
            break


    # option parser
    desc_str = "This program for downloading images from E-Hentai org."
    parser = argparse.ArgumentParser(description=desc_str)
    parser.add_argument("-u", "--url", dest="url", nargs="*",
                        help="Read URL of E-Hentai org")
    parser.add_argument("-f", "--filename", dest="filename", nargs="*",
                        help="Read URLs of E-Hentai org from text file")
    parser.add_argument("--retry", type=int, nargs=1,
                        metavar="TIMES", default=3,
                        help="Times of retry download (Default: 3 times)")
    parser.add_argument("--sleep", type=int, nargs=1,
                        metavar="SECONDS", default=900,
                        help="Sleep time until next retry (Default: 1800 sec)")
    parser.add_argument("--interval", type=int, nargs=1,
                        metavar="SECONDS", help="Interval between downloads")
    parser.add_argument("--no-resume", dest="noresume",
                        action="store_true", default=False,
                        help="Ignore resume of downloads.")
    parser.add_argument("--no-numbering", dest="nonumbering", action="store_true",
        default=False, help="Download image without file-name numbering")
    parser.add_argument("--no-filecheck", dest="nofilecheck", action="store_true",
        default=False, help="Download image without file-corruption check")
    parser.add_argument("--no-backup", dest="nobackup", action="store_true",
        default=False, help="Download image without backup JSON file")
    args = parser.parse_args()


    # flags
    if args.noresume:
        flags.append("no-resume")
    if args.nonumbering:
        flags.append("no-numbering")
    if args.nofilecheck:
        flags.append("no-filecheck")
    if args.nobackup:
        flags.append("no-backup")


    # get input urls
    print("[ E-Hentai Downloader ]")

    if "no-resume" in flags or not os.path.exists(report_path):
        if not args.url is None:
            for i in args.url:
                input_urls += get_input_urls(i, flag_urlonly=True)
        if not args.filename is None:
            for i in args.filename:
                input_urls += get_input_urls(i, flag_urlonly=False)
        if len(input_urls) == 0:
            flag_recursive = True
            input_str = prompt_url_input()
            input_urls += get_input_urls(input_str, flag_urlonly=True)
        if len(input_urls) == 0:
            print("Error: Input URLs don't exist.")
            sys.exit(1)

    # resume interrupted download
    if not "no-resume" in flags and os.path.exists(report_path):
        print("\nNotice: Interrupted download will be resumed.\n")
        f = open(report_path)
        page_info = json.load(f)
        input_urls = page_info["remain_urls"]
        f.close()

        flag_resume = True
        finish = sequence_download(page_info)
        if not finish:
            print("\nNotice: Download is not finished.")
            print("Next time, remaining images will be downloaded...")
            sys.exit(1)


    # show start message
    if not flag_resume:
        print("Now, Start downloading...\n")

    # download images
    while not flag_useflask:
        url = ""

        # get url
        if len(input_urls) == 0 and flag_recursive:
            if os.path.exists(report_path):
                os.remove(report_path)
            input_str = prompt_url_input()
            input_urls += get_input_urls(input_str, flag_urlonly=True)
            print("Now, Start downloading...\n")

        # check whether finish or not
        if len(input_urls) > 0:
            url = input_urls.pop(0)
        else:
            break

        # remove query from url
        r = urllib.parse.urlsplit(url)
        url = "{0}://{1}{2}".format(r.scheme, r.netloc, r.path)

        # get variables
        top_html  = ""
        gal_html  = ""
        init_html = ""

        try:
            for _ in range(5):
                init_html = get_html(url, True)
                break
        except ContentWarningException:
            print("Notice: 'Content Warning' is occured.\n")
            print("Skip and go to next URL...\n")
            continue
        except:
            time.sleep(1)
            pass

        top_url = ehentai_get_topurl(init_html)
        gal_url = ehentai_get_gurl(init_html)

        try:
            for _ in range(5):
                top_html = get_html(top_url, True)
                break
        except:
            time.sleep(1)
            pass

        try:
            for _ in range(5):
                gal_html = get_html(gal_url, True)
                break
        except:
            time.sleep(1)
            pass

        title      = ehentai_get_title(gal_html)
        num_images = ehentai_get_numimgs(top_html)

        # url check
        if num_images == 0 or top_url == "":
            print("Notice: The URL is probably wrong.\n")
            continue

        interval = None
        if not args.interval is None:
            interval = args.interval[0]

        page_info = {
            "save_path"   : save_path,
            "report_path" : report_path,
            "top_url"     : top_url,
            "title"       : title,
            "num_images"  : num_images,
            "retry"       : args.retry,
            "sleep"       : args.sleep,
            "interval"    : interval,
            "flags"       : flags,
            "gal_urls"    : [],
            "remain_urls" : input_urls
        }

        sequence_download(page_info)

    os.remove(report_path)


