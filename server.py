import BaseHTTPServer
import re
import get_pnr_status_v2
import os

# need to create a server
# then that server will need a handler to
class MyClass(BaseHTTPServer.BaseHTTPRequestHandler):
    regex = re.compile("\?pnr=(\d+)$")
    valid_paths = [
        "/pnr_status.txt",
        "/pnr_status.json"
    ]

    def check_path(self):
        pnr = None
        ret_type = None
        ret = 404 # invalid path
        path = self.path
        re1 = re.compile("/pnr_status(\.\w+)?")
        m = re1.match(path)
        if m:
            ret = 422 # missing query param
            ret_type = m.group(1) # get the extension
            if ret_type is not None and ret_type.find("json") > -1:
                ret_type = "json"
            else:
                ret_type = "txt" # default extension
            path = path.replace(m.group(), "")
            # now the path should be of the format ?pnr=12312
            m = self.regex.match(path)
            if m is not None:
                pnr = m.group(1)
                ret = 200
        return ret, pnr, ret_type

    def do_GET(self):
        path_status, pnr, ret_type = self.check_path()
        self.send_response(path_status)
        headers = {}
        headers["Access-Control-Allow-Origin"] = "*"
        ret = None
        if path_status == 200:
            headers["Content-Type"] = "text/plain"
            if ret_type == "json":
                headers['Content-Type'] = 'application/json'
                ret = get_pnr_status_v2.checkPnrStatus(pnr = pnr)
            else:
                ret = get_pnr_status_v2.checkPnrStatus(pnr = pnr, astext = True)
        elif path_status == 422:
            ret = "Missing or invalid query param\n"
        else:
            ret = self.responses[path_status][0]
            ret += "\n" + self.responses[path_status][1]
            ret += "\n"

        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(ret)
        self.wfile.flush()

port = int(os.environ.get("PORT", 8000))
server_address = ('', port)
httpd = BaseHTTPServer.HTTPServer(server_address, MyClass)
httpd.serve_forever()
