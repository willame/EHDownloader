#!/usr/bin/python3

### modules ###
import os
import re
import sys
import json
import time
import random
import argparse
import urllib.request


# global variables
agent_list_path = "./user-agent.txt"
if not os.path.exists(agent_list_path):
    print("User-agent list is not found.")
    os.exit(1)
f = open("user-agent.txt", "r")
user_agent = random.choice(f.readlines())


# functions
def save_image(img_url, img_path):
    global user_agent

    try:
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

    except:
        print("Error : Image download error.")
        return False


def get_html(url):
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

    return page_html


def ehentai_get_gurl(url):
    html = ""
    try:
        for _ in range(10):
            html = get_html(url)
            break
    except:
        pass

    m1 = re.search("http://g.e-hentai.org/g/.*", url)
    if m1 != None:
        return url

    m2 = re.search("http://g.e-hentai.org/s/.*", url)
    if m2 != None:
        m2_g = re.search("<div class=\"sb\"><a href=\"(.*?)\">", html)
        if m2_g != None:
            return m2_g.group(1)

    return ""


def ehentai_get_topurl(url):
    html = ""
    try:
        for _ in range(10):
            html = get_html(url)
            break
    except:
        pass

    m1 = re.search("http://g.e-hentai.org/g/.*", url)
    if m1 != None:
        m1_top = re.search("<div style=\".*?\"><a href=\"(.*)?\"><img alt=\"0*1\"", html)
        if m1_top != None:
            return m1_top.group(1)

    m2 = re.search("http://g.e-hentai.org/s/.*", url)
    if m2 != None:
        m2_top = re.search("<div class=\"sn\"><a onclick=\".*?\" href=\"(.*?)\">", html)
        if m2_top != None:
            return m2_top.group(1)

    return ""


def ehentai_get_title(top_url):
    html = ""
    try:
        for _ in range(10):
            html = get_html(top_url)
            break
    except:
        pass

    m1 = re.search("<h1 id=\"gj\">(.*?)</h1>", html)
    if m1 != None:
        return m1.group(1)

    m2 = re.search("<h1 id=\"gn\">(.*?)</h1>", html)
    if m2 != None:
        return m2.group(1)

    return "Unknown"


def ehentai_get_numimgs(top_url):
    num = 0
    html = ""
    try:
        for _ in range(10):
            html = get_html(top_url)
            break
    except:
        pass

    m = re.search("<div><span>1</span> / <span>(.*?)</span></div>", html)
    if m != None:
        num = int(m.group(1))

    return num


def ehentai_get_imginfo(html):
    img_name = ""
    img_size = 0
    img_byte_size = 0

    m = re.search("<img src=\".*?\" /></a></div><div>(.*?) :: .*? :: (.*?)([KMGT]?B)</div>", html)
    if m != None:
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
        if m2 != None:
            print("HTTPS access is not permitted in E-Hentai Gallery.")
            print("Please input url starts with \"http://\".")
            sys.exit(1)

        print("Error : URL is invalid.\n")
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
            print("Error : Input file of urls is not found.\n")
            sys.exit(1)

    return []


def check_file_corruption(img_size, img_path):
    diff_size = abs(img_size - os.path.getsize(img_path))
    if diff_size < 0.001 * img_size:
        return False
    else:
        return True


def ehentai_get_nexturl(html):
    m_next = re.search("<a id=\"next\" onclick=\".*?\" href=\"(.*?)\">", html)
    if m_next != None:
        next_url = m_next.group(1)
        return next_url

    return ""


def create_report(page_info):
    json_data = json.dumps(page_info)
    f.open(page_info["report_path"], "w")
    f.write(json_data)
    f.close()
    return


def ehentai_download(save_path, page_info):
    # variables
    count = 0
    count_stop = 0
    url        = page_info["top_url"]
    num_images = page_info["num_images"]
    flags      = page_info["flags"]

    if page_info["tmp_count"] > 0:
        url   = page_info["tmp_url"]
        count = page_info["tmp_count"]

    # download operation
    while count < num_images:

        if count_stop < 20:
            count_stop = 0
        else:
            break

        # get html
        try:
            html = get_html(url)
            time.sleep(1)
        except:
            print("Error : HTML document download error.")
            count_stop += 1
            continue

        if html == "":
            count_stop += 1
            continue

        m_img = re.search("<img id=\"img\" src=\"(.*?)\" style=\".*?\" />", html)

        if m_img != None:
            img_url = m_img.group(1)
            orig_name, img_size = ehentai_get_imginfo(html)
            _, ext = os.path.splitext(orig_name)

            img_name = ""
            if "no-numbering" in flags:
                img_name = orig_name
            else:
                img_name = "{0:03d}{1}".format(count+1, ext)

            img_path = os.path.join(save_path, img_name)
            if os.path.exists(img_path):
                print("{0:03d} : {1} ... already exists".format(count+1, img_url))
            else:
                if "no-filecheck" in flags:
                    if check_file_corrption(img_size, img_path):
                        print("Caution: File corrption is detected.")
                        print("Now, attempt to retry download...")
                        count_stop += 1
                        continue
                save_image(img_url, img_path)
                print("{0:03d} : {1} ... save".format(count+1, img_url))

            count += 1
            next_url = ehentai_get_nexturl(html)
            if next_url == "":
                break

            if url == next_url:
                print("\nSuccess: Finish downloading!\n")
                time.sleep(1)
                return True
            else:
                url = next_url

    page_info["tmp_url"] = url
    page_info["tmp_count"] = count

    return False


def sequence_download(page_info):
    args = page_info["args"]

    # make new directory
    save_path = os.path.join(page_info["root_path"], page_info["title"])
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    else:
        print("Caution: The directory already exists.")

    # print information
    print("\n< Page Information >")
    print("URL : {0}".format(page_info["top_url"]))
    print("Title : {0}".format(page_info["title"]))
    print("Total of Images : {0}\n".format(page_info["num_images"]))

    # download images
    ok = ehentai_download(save_path, page_info)

    # resume download
    retry_count = 0
    while not ok:
        if retry_count >= args.retry:
            #create_report(page_info)
            return False
        print("Notice: Retry limit exceeded. Now, Sleep...")
        print("Sleep time: {0} seconds".format(args.sleep))
        time.sleep(args.sleep)
        ok = ehentai_download(save_path, page_info)
        retry_count += 1

    return True


# main function
if __name__ == '__main__':
    # variables
    flags = []
    input_urls = []

    # file path
    root_path = ""
    report_path = "./interrupt-report.json"
    remain_urls_path = "./remaining-urls.txt"
    store_path = ["~/Pictures", "~/Picture", "~/ピクチャ", os.getcwd()]

    for i in store_path:
        tmp = os.path.expanduser(i)
        if os.path.exists(tmp):
            root_path = os.path.join(tmp, "E-Hentai_downloads")
            break

    # option parser
    desc_str = "This program for downloading images from E-Hentai org."
    parser = argparse.ArgumentParser(description=desc_str)
    parser.add_argument("-u", "--url", dest="url", nargs="*",
        help="Read URL of E-Hentai org")
    parser.add_argument("-f", "--filename", dest="filename", nargs="*",
        help="Read URLs of E-Hentai org from text file")
    parser.add_argument("-r", "--retry", type=int, nargs=1, default=3,
        help="Times of retry download (Default: 3 times)")
    parser.add_argument("-s", "--sleep", type=int, nargs=1, default=1800,
        help="Sleep time until next retry (Default: 1800 sec)")
    parser.add_argument("--no-resume", dest="noresume", action="store_true",
        default=False, help="Ignore resume of downloads.")
    parser.add_argument("--no-numbering", dest="nonumbering", action="store_true",
        default=False, help="Download image without file-name numbering")
    parser.add_argument("--no-filecheck", dest="nofilecheck", action="store_true",
        default=False, help="Download image without file-corruption check")
    args = parser.parse_args()

    # flags
    if args.noresume:
        flags.append("no-resume")
    if args.nonumbering:
        flags.append("no-numbering")
    if args.nofilecheck:
        flags.append("no-filecheck")

    # get input urls
    print("[ E-Hentai Downloader ]")
    argc = len(sys.argv)
    if argc == 1:
        input_str = ""
        while not re.match("[0-9a-zA-Z]+", input_str):
            print("Please input URL of E-Hentai Page.")
            input_str = input("URL > ")
            input_str.strip()
        print()
        input_urls += get_input_urls(input_str, flag_urlonly=True)
    else:
        if not args.url is None:
            for i in args.url:
                input_urls += get_input_urls(i, flag_urlonly=True)
        if not args.filename is None:
            for i in args.filename:
                input_urls += get_input_urls(i, flag_urlonly=False)
        if input_urls == []:
            parser.print_help()
            sys.exit(1)

    # show download options
    print("Now, Start downloading...\n")
    if flags != []:
        print("<Download Options>")
        print(flags)
        print()

    # exit
    if len(input_urls) == 0:
        print("Error : Input URLs don't exist.")
        sys.exit(1)

    # print input urls
    print("<List of input URL>")
    for url in input_urls:
        print(url)
    print()

    # resume interrupted download
    if not "no-resume" in flags and os.path.exists(report_path):
        print("Notice: Interrupted download will be resumed.")
        print("URL : {0}".format(data["url"]))
        f = open(report_path)
        page_info = json.load(f)
        finish = sequence_download(page_info)
        if not finish:
            print("\nNotice: Download is not finished.")
            print("Next time, remaining images will be downloaded...")
            sys.exit(1)

    # download images
    for i, url in enumerate(input_urls):
        top_url     = ehentai_get_topurl(url)
        g_url       = ehentai_get_gurl(url)
        title       = ehentai_get_title(g_url)
        num_images  = ehentai_get_numimgs(top_url)

        page_info = {
            "root_path"  : root_path,
            "report_path": report_path,
            "top_url"    : top_url,
            "g_url"      : g_url,
            "title"      : title,
            "num_images" : num_images,
            "args"       : args,
            "flags"      : flags,
            "tmp_url"    : "",
            "tmp_count"  : 0
        }
        finish = sequence_download(page_info)
        if not finish:
            print("\nNotice: Download is not finished.")
            print("Next time, remaining images will be downloaded...")
            f = open(remain_urls_path, "w")
            for line in input_urls[i:]:
                f.write("{0}\n".format(line))
            sys.exit(1)

