import PySimpleGUI as sg
from PIL import Image, ImageTk

canvas_width=640
canvas_height=640

def get_image_from_file(image_file):
    img = Image.open(image_file)
    img = img.resize(( int(img.width * (canvas_width/img.width)), int(img.height * (canvas_height/img.width)) ))
    img = ImageTk.PhotoImage(img)

blank_image = 'blank.png'
image_elem = sg.Image(data=get_image_from_file(blank_image))

sg.theme('white')
frame1 = sg.Frame(
    '', [], size=(640, 320)
)
frame2 = sg.Frame(
    '', 
    [ image_elem ], 
    size=(canvas_width, canvas_height)
)

layout = [ 
    [frame1],
    [frame2]
]
window = sg.Window('サンプル', layout, resizable=True)

while True:
    event, values = window.read()
    if event is None:
        print('exit')
        break

window.close()
