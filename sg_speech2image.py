import PySimpleGUI as sg
from PIL import Image, ImageTk
import io
import wave, subprocess
import torch
from diffusers import DiffusionPipeline
import xformers
import whisper
import os, time, ffmpeg, numpy

# configuration
model_id="stabilityai/japanese-stable-diffusion-xl"
whisper_model="large"
generate_file="test.png"
audio_file="audio.wav"
second=5
command = ['parecord', '--channels=1', '--device=alsa_input.usb-Focusrite_iTrack_Solo-00.analog-stereo', 'audio.wav']

def _execute_shell_command(
    command,
    timeout=-1,  # *default= no limit
    # Debug
    verbose= False,
):
     with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT  # Example ['ls ','l']
    ) as terminal_subprocess:
        # Execute command depending or not in timeout
        try:
            if timeout == -1:
                stdout, stderr = terminal_subprocess.communicate()
            else:
                stdout, stderr = terminal_subprocess.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:  # When script finish in time
            terminal_subprocess.kill()
            stdout, stderr = terminal_subprocess.communicate()

        return stdout, stderr

def prepare_pipeline():
    pipeline=DiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16",
        trust_remote_code=True
    ).to("cuda")
    return pipeline

def prepare_whisper():
    model = whisper.load_model(whisper_model).to("cpu")
    return model

def record_audio():
    _execute_shell_command(command, second)

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
asr_progress_elem = sg.Text('', key='text1', font=('Helvetica', 24))

frame1 = sg.Frame(
    '', 
    [
        [ sg.Button(button_text='音声認識', button_color=('#000', '#fcc'), font=('Helvetica',24), size=(8,3), key='start_asr') ],
        [ asr_progress_elem ]
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
        asr_progress_elem.update('パソコンのマイクに向かって5秒話してください...')
        record_audio()
        print('Start Whisper ASR')
        asr_progress_elem.update('録音終了')
        window['start_asr'].update(disabled=False)

window.close()
