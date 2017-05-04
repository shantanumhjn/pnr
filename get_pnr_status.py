import requests
from urllib import urlencode
from bs4 import BeautifulSoup as bs
import re
import sys
import json
import base64

url1 = base64.b64decode("aHR0cDovL3d3dy5pbmRpYW5yYWlsLmdvdi5pbi9wbnJfRW5xLmh0bWw=")
url = base64.b64decode("aHR0cDovL3d3dy5pbmRpYW5yYWlsLmdvdi5pbi9jZ2lfYmluL2luZXRfcG5zdGF0X2NnaV8xNDM1MC5jZ2k=")

# session = requests.Session()

headers = {
    # "Cookie": "adf",
    "Referer": url1
}

data = {
    "lccp_pnrno1": 123445667,
    "lccp_cap_value": 24357,
    "lccp_capinp_value": 24357,
    "submit": "Please Wait..."
}

def print_table(rows):
    # print rows
    output_template = "{{:<{}}}"
    header_lens = {}
    tr_values_list = []
    for row in rows:
        trs = row.find_all("td")
        tr_values = []
        for i in range(len(trs)):
            tr = trs[i]
            tr_values.append(tr.text)
            header_lens[i] = max(header_lens.get(i, 0), len(tr.text))
        tr_values_list.append(tr_values)
        # print output_template.format(*tr_values)
    new_header_lens = [None] * (len(header_lens))
    for k, v in header_lens.items():
        new_header_lens[k] = v + 5

    output_template = (output_template*len(new_header_lens)).format(*new_header_lens)
    for tr_values in tr_values_list:
        print output_template.format(*tr_values)
    print

def make_request(pnr = None, use_proxy = False):
    proxies = None
    if use_proxy:
        with open("test_proxy.json") as f:
            proxies = json.loads(f.read())
    if pnr is not None: data["lccp_pnrno1"] = pnr
    resp = requests.post(url, timeout = 30, proxies = proxies, data = data, headers = headers)
    print "status", resp.status_code
    # print "headers", resp.request.headers
    # print "body", resp.request.body
    # print "repsonse headers", resp.headers
    # print dir(resp.request)
    # print dir(resp)
    # print resp.content

    with open("result.html", 'w') as f:
        f.write(resp.content)
    soup = bs(resp.content, 'html.parser')
    with open("formattedresult.html", 'w') as f:
        f.write(soup.prettify().encode('UTF-8'))

    return resp.content

def parse_and_show(content):
    soup = bs(content, 'html.parser')
    # starting tag
    tag1 = soup.find("td", text = re.compile("You Queried For."))
    if tag1 is not None:
        print tag1.text.strip().replace("\n", "").replace("\r", "")
        print

        # first table of interest
        rows = tag1.find_next("table").find_all("tr")
        rows = rows[1:]
        print "train info:"
        print_table(rows)

        # second table of interest
        # PASSENGER list
        rows = tag1.find_next("table").find_next("table").find_next("table").find_all("tr")
        other_info = rows[-3:]

        # actual passenger list
        rows = rows[:-3]
        print "passenger info:"
        print_table(rows)

        print "other info:"
        for info in other_info:
            print_table([info])
    else:
        print "unable to find the required text"
        exit(1)

def parse_from_file(file_name):
    # read from file to parse html
    content = ""
    with open(file_name) as f:
        content = f.read()
    parse_and_show(content)

def check_pnr(pnr = None, use_proxy = False):
    parse_and_show(make_request(pnr, use_proxy))

def usage():
    print "usage:\n\t", sys.argv[0], "<pnr>"
    exit(1)

if __name__ == "__main__":
    inp = sys.argv
    use_proxy = False
    if len(inp) < 2:
        usage()
    elif len(inp) > 2:
        use_proxy = True
    pnr = inp[1]
    if pnr.isdigit():
        check_pnr(pnr = pnr, use_proxy = use_proxy)
    else:
        print "reading from file:", pnr
        parse_from_file(pnr)
