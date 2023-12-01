import PySimpleGUI as sg
from PIL import Image, ImageTk
import io

canvas_width=640
canvas_height=640

sg.theme('LightGrey')

def process():
    pass

def get_image_from_file(image_file, first=False):
    img = Image.open(image_file)
    #img = img.resize(( int(img.width * (canvas_width/img.width)), int(img.height * (canvas_height/img.width)) ))
    img.thumbnail((canvas_width, canvas_height))
    if first:
        bio = io.BytesIO()
        img.save(bio, format='PNG')
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)

blank_image = './blank.png'
image_elem = sg.Image(data=get_image_from_file(blank_image, first=True))

frame1 = sg.Frame(
    '', 
    [
        [ sg.Button(button_text='音声認識', button_color=('#000', '#fcc'), font=('Helvetica',24), size=(8,3), key='start_asr') ],
        [ sg.Text(key='text1')]
    ]
    , size=(640, 320)
)
frame2 = sg.Frame(
    '',
    [ 
        [ sg.Text('生成画像', font=('Helvetica', 24))],
        [ image_elem ], 
    ],
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
    elif event == 'start_asr':
        window['start_asr'].update(disabled=True)
        print('Start Whisper ASR')

window.close()
