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

def make_request(pnr = None, use_proxy = False):
    proxies = None
    if use_proxy:
        with open("test_proxy.json") as f:
            proxies = json.loads(f.read())
    if pnr is not None: data["lccp_pnrno1"] = pnr
    resp = requests.post(url, timeout = 30, proxies = proxies, data = data, headers = headers)
    # print "status", resp.status_code
    # print "headers", resp.request.headers
    # print "body", resp.request.body
    # print "repsonse headers", resp.headers
    # print dir(resp.request)
    # print dir(resp)
    # print resp.content

    # with open("result.html", 'w') as f:
    #     f.write(resp.content)
    # soup = bs(resp.content, 'html.parser')
    # with open("formattedresult.html", 'w') as f:
    #     f.write(soup.prettify().encode('UTF-8'))

    return resp.content

def create_table_str(rows):
    output = ""
    headers = rows[0].keys()
    header_locs = {}
    header_lens = []
    for i in range(len(headers)):
        header_locs[headers[i]] = i
        header_lens.append(len(headers[i]))
    vals = []
    for row in rows:
        val = [0]*len(row)
        for k, v in row.items():
            idx = header_locs[k]
            val[idx] = v
            header_lens[idx] = max(header_lens[idx], len(v))
        vals.append(val)
    del header_locs

    header_lens = [i+5 for i in header_lens]
    vals.insert(0, headers)
    output_template = "{{:<{}}}"
    output_template = (output_template*len(header_lens)).format(*header_lens)
    for val in vals:
        output += output_template.format(*val)
        output += "\n"
    return output

def create_data_str(data):
    output = ""
    if data["status"] != "failed":
        output += "PNR Number:" + data["PNR"]
        output += "\n\n"

        output += "train info:\n"
        output += create_table_str(data["train"])
        output += "\n"

        output += "passenger info:\n"
        output += create_table_str(data["passengers"])
        output += "\n"

        output += "Other info:\n"
        for item in data.get("other_info", []):
            for k, v in item.items():
                output += k + ": " + v + "\n"
        output += "\n"
    else:
        output += data["message"]
    return output

# assumes data in format:
# each row is inside a tr tag and each tr tag has multiple td tags
# if there is only one tr tag and there are 2 td tags then assume key value pair
def parse_table(rows):
    result = None
    headers = []
    if len(rows) == 1:
        tds = rows[0].find_all("td")
        if len(tds) == 2:
            result = {}
            result[tds[0].text.strip()] = tds[1].text.strip()
    else:
        result = []
        for i in range(len(rows)):
            row = rows[i]
            trs = row.find_all("td")
            single_row = {}
            for j in range(len(trs)):
                tr = trs[j]
                if i == 0:
                    headers.append(tr.text.strip())
                else:
                    single_row[headers[j]] = tr.text.strip()
            if i != 0: result.append(single_row)
    return result

# will parse the html content into a json
def parse(content):
    soup = bs(content, 'html.parser')
    r = re.compile("You Queried For.:")

    # starting tag
    tag1 = soup.find("td", text = r)
    if tag1 is not None:
        result = {}
        pnr_str = tag1.text.strip().replace("\n", "").replace("\r", "")
        pnr = [i.strip() for i in r.sub("", pnr_str).strip().split(":")]
        result["PNR"] = pnr[1]

        # first table of interest
        rows = tag1.find_next("table").find_all("tr")
        rows = rows[1:]
        result["train"] = parse_table(rows)

        # second table of interest
        # PASSENGER list
        rows = tag1.find_next("table").find_next("table").find_next("table").find_all("tr")
        other_info = rows[-3:]
        # actual passenger list
        rows = rows[:-3]
        result["passengers"] = parse_table(rows)

        others = []
        for info in other_info:
            ret = parse_table([info])
            if ret is not None:
                others.append(ret)
        result["other_info"] = others

        result["status"] = "successful"
        # print json.dumps(result, indent = 2)
        return result
    else:
        result = {
            "status": "failed",
            "message": "unable to find the required text"
        }
        return result

def parse_from_file(file_name):
    # read from file to parse html
    content = ""
    with open(file_name) as f:
        content = f.read()
    print create_data_str(parse(content))
    # parse_and_show(content)

def pnr_status_json(pnr):
    return json.dumps(parse(make_request(pnr)))

def pnr_status_text(pnr):
    return create_data_str(parse(make_request(pnr)))

def check_pnr(pnr = None, use_proxy = False):
    print create_data_str(parse(make_request(pnr, use_proxy)))

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
