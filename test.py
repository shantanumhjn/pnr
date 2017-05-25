from get_pnr_status_v2 import create_session, getCaptcha
import process_image
from StringIO import StringIO
from PIL import Image

code, raw = getCaptcha(create_session())
print 'get captcha code:', code
im = Image.open(StringIO(raw))
# im = Image.open('capta.png')
process_image.do_stuff(im)
