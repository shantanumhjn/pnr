import requests
import json
import time

proxies = {}
with open('test_proxy.json') as f:
    proxies = json.loads(f.read())

pnr = 4331777966

url1 = 'http://www.indianrail.gov.in/enquiry/PnrEnquiry.html'
url2 = 'http://www.indianrail.gov.in/enquiry/CommonCaptcha'
data = {
    "inputCaptcha": 0000,
    "inputPnrNo": pnr,
    "inputPage": 'PNR'
}
url3 = 'http://www.indianrail.gov.in/enquiry/captchaDraw.png?'

session = requests.Session()

# resp = session.get(url1, proxies = proxies)
# print 'response headers from first url:', resp.status_code
# for k, v in resp.headers.items():
#     print k, ':', v
# print

ts = int(time.time() * 1000)
# print ts, '{}{}'.format(url3, ts)
resp = session.get('{}{}'.format(url3, ts), proxies = None)
with open('capta.png', 'wb') as f:
    f.write(resp.content)
print 'captcha response:', resp.status_code
for k, v in resp.headers.items():
    print k, ':', v
print

headers = {
    'Referer': url1,
    'Host': 'www.indianrail.gov.in',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
session.headers.update(headers)

captchaVal = int(raw_input("enter captcha: "))

data["inputCaptcha"] = captchaVal

resp = session.get(url2, proxies = None, params = data)
print 'request headers from second url:'
for k, v in resp.request.headers.items():
    print k, ":", v
print

print 'response headers from second url:', resp.status_code
for k, v in resp.headers.items():
    print k, ':', v
print

print 'response:'
print resp.content
with open('result.json', 'w') as f:
    f.write(json.dumps(json.loads(resp.content), indent = 2))
