from bogo_engine import ime
def typ(keys, mode='telex', nw=False):
    buf = ''
    for k in keys:
        r = ime(buf, k, mode, nw) if buf else None
        buf = r if r is not None else buf + k
    return buf
T = [('Vieejt','Việt'),('dduwowcj','được'),('hoaf','hòa'),('thuowngj','thượng'),('toans','toán'),
 ('quas','quá'),('giaf','già'),('gif','gì'),('khuyeenf','khuyền'),('aas','ấ'),('ass','as'),
 ('Dduwowngf','Đường'),('nguwowif','người'),('tieengs','tiếng'),('Nam','Nam'),('ddd','dd'),
 ('hoawf','hoằ'),('muas','múa'),('thuys','thúy'),('cuoojc','cuộc'),('ww','ww'),('aaa','aa'),('toio','tôi'),('roio','rôi'),('ddoio','đôi'),('toioo','toio'),('toios','tối'),('doio','dôi')]
bad=0
for k,e in T:
    r=typ(k)
    if r!=e: bad+=1; print('TELEX LỖI',k,'->',r,'mong',e)
V=[('Vie6t5','Việt'),('d9u7o7c5','được'),('hoa2','hòa'),('thu7o7ng5','thượng'),('toan1','toán'),('D9u7o72ng','Đường'),('a66','a6')]
for k,e in V:
    r=typ(k,'vni')
    if r!=e: bad+=1; print('VNI LỖI',k,'->',r,'mong',e)
from docso import docso, convert_text
D=[('1250000','Một triệu hai trăm năm mươi nghìn'),('1001','Một nghìn không trăm linh một'),
 ('21.005.001,5','Hai mươi mốt triệu không trăm linh năm nghìn không trăm linh một phẩy năm'),('15','Mười lăm'),('105','Một trăm linh năm'),
 ('0','Không'),('1000000000000','Một nghìn tỷ'),('1000001','Một triệu không trăm linh một'),('-3','Âm ba'),('91','Chín mươi mốt')]
for a,e in D:
    r=docso(a)
    if r!=e: bad+=1; print('SỐ LỖI',a,'->',r,'mong',e)
if convert_text('Có 3 xe và 1.500 người')!='Có ba xe và một nghìn năm trăm người': bad+=1; print('LỖI convert_text')
print('mới:',typ('hoaf',nw=True),typ('thuys',nw=True))
print('xong, lỗi =',bad)
import sys;sys.exit(1 if bad else 0)
