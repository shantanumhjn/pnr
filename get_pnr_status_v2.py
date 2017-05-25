import requests
import json
import time
import sys
from PIL import Image
# form PIL import ImageOps
from StringIO import StringIO
from pytesseract import image_to_string
from get_pnr_status import create_data_str

# proxies = {}
# with open('test_proxy.json') as f:
#     proxies = json.loads(f.read())

pnr = 4331777966

url1 = 'http://www.indianrail.gov.in/enquiry/PnrEnquiry.html'
url2 = 'http://www.indianrail.gov.in/enquiry/CommonCaptcha'
data = {
    "inputCaptcha": 0000,
    "inputPnrNo": pnr,
    "inputPage": 'PNR'
}
url3 = 'http://www.indianrail.gov.in/enquiry/captchaDraw.png?'

headers = {
    # 'Referer': url1,
    'Host': 'www.indianrail.gov.in',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

def create_session():
    session = requests.Session()
    return session

def getCaptcha(session):
    ts = int(time.time() * 1000)
    # print ts, '{}{}'.format(url3, ts)
    resp = session.get('{}{}'.format(url3, ts), proxies = None)
    # print 'captcha response:', resp.status_code
    # for k, v in resp.headers.items():
    #     print k, ':', v
    # print
    return resp.status_code, resp.content


def getStatus(session, pnr, captcha):
    session.headers.update(headers)

    # captcha = int(raw_input("enter captcha: "))

    data["inputCaptcha"] = captcha
    data["inputPnrNo"] = pnr

    resp = session.get(url2, proxies = None, params = data)
    # print 'request headers from second url:'
    # for k, v in resp.request.headers.items():
    #     print k, ":", v
    # print

    # print 'response headers from second url:', resp.status_code
    # for k, v in resp.headers.items():
    #     print k, ':', v
    # print

    # print 'response:'
    # print resp.content
    # with open('result.json', 'w') as f:
    #     f.write(json.dumps(json.loads(resp.content), indent = 2))
    return json.loads(resp.content)

# the code seems to recognise + fine
# but always seems to read 7 instead of -.
# the captchas are only + and -.
# the second operand seems to be always a single digist number
def fixCaptcha(inp):
    num1 = None
    num2 = None
    oper = None
    val = None
    # check for + sign
    idx = inp.find('+')
    if idx > -1:
        num1 = int(inp[:idx])
        oper = '+'
    else: # probably a minus operation
        idx = inp.find('7')
        num1 = int(inp[:idx])
        oper = '-'
    num2 = int(inp[idx+1])
    if oper is not None:
        if oper == '+': val = num1 + num2
        else: val = num1 - num2
    result = {
        "num1": num1,
        "num2": num2,
        "oper": oper,
        "val": val
    }
    return result

def readCaptcha(image):
    # with open('capta.png', 'wb') as f:
    #     f.write(image)
    im = Image.open(StringIO(image))
    result = image_to_string(im)
    return result

def createResponse(data, astext = False):
    result = {}
    error = data.get("errorMessage")
    if error is None:
        result['PNR'] = data["pnrNumber"]
        result['status'] = "successful"
        result['train'] = []
        train = {}
        train['trainName'] = data['trainName']
        train['trainNumber'] = data['trainNumber']
        train['sourceStation'] = data['sourceStation']
        train['destinationStation'] = data['destinationStation']
        d = data['dateOfJourney']
        train['dateOfJourney'] = '{}-{}-{}'.format(*[d['orig_day'], d['orig_month'], d['orig_year']])
        result['train'].append(train)
        # result['train'].append({'trainName': data['trainName']})
        # result['train'].append({'trainName': data['trainName']})

        result['passengers'] = []
        for p in data['passengerList']:
            new_p = {}
            new_p['bookingStatus'] = str(p["bookingStatus"]) + '-' + str(p["bookingBerthNo"])
            new_p['currentStatus'] = str(p["currentStatus"]) + '-' + str(p["currentBerthNo"])
            new_p['passengerSerialNumber'] = str(p["passengerSerialNumber"])
            result['passengers'].append(new_p)

        result['other_info'] = []
        result['other_info'].append({'bookingFare': str(data['bookingFare'])})
        result['other_info'].append({'chartStatus': str(data['chartStatus'])})
    else:
        result['status'] = 'failed'
        result['message'] = error
    # print json.dumps(result, indent = 2)
    # print '\n\n'
    if astext:
        result = create_data_str(result)
    return result

def checkPnrStatus(pnr, astext = False):
    num_retries = 3
    for i in range(num_retries):
        print 'try #', i
        pnr_data = {"errorMessage": "unknown error"}
        session = create_session()
        code, img = getCaptcha(session)
        if code != 200:
            print 'skipping, http code while fetching captcha:', code
            pnr_data["errorMessage"] = 'http code from server:' + str(code)
            continue
        result = readCaptcha(img)
        fixedResult = None
        try:
            fixedResult = fixCaptcha(result)
        except Exception as e:
            print "could not fix captcha:", e
        print 'captcha before and after: {} - {}'.format(result, fixedResult)
        if fixedResult is not None:
            pnr_data = getStatus(session, pnr, fixedResult['val'])
            if pnr_data.get("errorMessage") is None:
                print 'got result'
                break
            else:
                print 'error:', pnr_data["errorMessage"]
    response = createResponse(pnr_data, astext)
    return repsonse

def createResponseFromFile(fname, astext = False):
    content = None
    with open(fname) as f:
        content = f.read()
    print createResponse(json.loads(content), astext)

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
        checkPnrStatus(pnr = pnr)
    else:
        print "reading from file:", pnr
        createResponseFromFile(pnr, astext = False)
