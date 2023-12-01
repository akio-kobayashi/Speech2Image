import PySimbleGUI as sg

sg.theme('white')
layout = [ 
    [sg.Text('Theme Browser')],
    [sg.Text('Clicka Theme Color')],
    [sg.Listbox(values.sg.theme_list(), size=(20, 12), key='-LIST-', enable_events=True)],
    [sg.Button('Exit')]
]
window = sg.Window('Theme Browser', layour)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    sg.theme(values['-LIST-'][0])
    sg.popup_get_text('This is {}'.format(values['-LIST-'][0]))

window.close()
