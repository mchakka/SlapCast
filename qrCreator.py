import pyqrcode

q1 = pyqrcode.create('1:1')
q1.png('1.png', scale = 7)

q2 = pyqrcode.create('1:2')
q2.png('2.png', scale = 7)

q3 = pyqrcode.create('1:3')
q3.png('3.png', scale = 7)

q4 = pyqrcode.create('1:4')
q4.png('4.png', scale = 7)