import PySimpleGUI as sg

sg.theme('white')
frame1 = sg.Frame(
    [], size=(640, 320)
)
frame2 = sg.Frame(
    [], size=(640, 320)
)

layout = [ 
    [frame1],
    [frame2]
]
window = sg.Window('サンプル', layout)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break

window.close()
