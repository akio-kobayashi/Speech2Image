import PySimpleGUI as sg
from PIL import Image, ImageTk
import io
import wave, subprocess
import torch, torchaudio
from diffusers import DiffusionPipeline
import xformers
import whisper
import os, time, ffmpeg, numpy
import matplotlib.pyplot as plt

# configuration
model_id="stabilityai/japanese-stable-diffusion-xl"
whisper_model="large"
generate_file="test.png"
audio_file="audio.wav"
second=5
command = ['parecord', '--channels=1', '--device=alsa_input.usb-Focusrite_iTrack_Solo-00.analog-stereo', 'audio.wav']
asr_result=""

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

def asr(model):
    result = model.transcribe(audio_file, language='ja')
    asr_result=list(result['text'])    

def stable_diffusion():
    image = pipeline(asr_result).images[0]
    image.save(generate_file)

model = prepare_whisper()
pipeline = prepare_pipeline()

canvas_width=1280
canvas_height=1280

sg.theme('LightGrey')

def speech_analysis():
    y, sr = torchaudio.load(audio_file)
    plt.figure(figsize=(16,6))
    plt.plot(y.numpy(), linewidth=1)
    plt.savefig('wave.png')
    # spectrogram
    plt.specgram(y.numpy())
    plt.savefig('spec.png')

def get_image_from_file(image_file, width=canvas_width, height=canvas_height, first=False):
    img = Image.open(image_file)
    #img = img.resize(( int(img.width * (canvas_width/img.width)), int(img.height * (canvas_height/img.width)) ))
    img.thumbnail((width, height))
    if first:
        bio = io.BytesIO()
        img.save(bio, format='PNG')
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)

blank_image = './blank.png'
image_elem = sg.Image(data=get_image_from_file(blank_image, first=True))
asr_progress_elem = sg.Text('', key='text1', font=('Helvetica', 24))
asr_result_elem = sg.Text('', key='text2', font=('Helvetica', 24))
wave_elem = sg.Image(data=get_image_from_file(blank_image, height=480, first=True))
spectrogram_elem = sg.Image(data=get_image_from_file(blank_image, height=480, first=True))

frame1 = sg.Frame(
    '', 
    [
        [ sg.Button(button_text='音声認識', button_color=('#000', '#fcc'), font=('Helvetica',24), size=(8,3), key='start_asr'), asr_progress_elem ],
        [ sg.Text('音声認識結果: ', font=('Helvetica', 24)), asr_result_elem]
    ]
    , size=(2560, 320)
)
frame2 = sg.Frame(
    '',
    [ 
        [ sg.Text('生成画像', font=('Helvetica', 24))],
        [ image_elem ], 
    ],
    size=(canvas_width, canvas_height)
)

frame3 = sg.Frame(
    '',
    [
        [sg.Text('音声波形', font=('Helvetica, 24'))],
        [ wave_elem ],
        [ sg.Text('スペクトログラム（声紋）', font=('Helvetica', 24)) ],
        [ spectrogram_elem ]        
    ],
    size=(canvas_width, canvas_height)
)

layout = [ 
    [frame1],
    [frame2, frame3]
]
window = sg.Window('サンプル', layout, resizable=True)

while True:
    event, values = window.read()
    if event is None:
        print('exit')
        break
    elif event == 'start_asr':
        window['start_asr'].update(disabled=True)
        asr_result_elem.update('')
        asr_progress_elem.update('パソコンのマイクに向かって5秒話してください...')
        window.perform_long_operation(lambda:record_audio(), end_key="complete_record")
    elif event == 'complete_record':
        asr_progress_elem.update('録音終了')
        window.perform_long_operation(lambda:speech_analysis(), end_key="complete_analysis")
        asr_progress_elem.update('音声分析中...')
    elif event == 'complete_analysis':    
        wave_elem.update(data=get_image_from_file('wave.png', height=480, first=True))
        spectrogram_elem.update(data=get_image_from_file('spec.png', height=480, first=True))
        asr_progress_elem.update('音声認識中...')
        window.perform_long_operation(lambda:asr(model), end_key="complete_asr")
    elif event == 'complete_asr':
        asr_progress_elem.update('音声認識終了')
        if asr_result == '':
            asr_result=u'青い馬に乗った宇宙飛行士が砂漠を行くリアルな画像'
        asr_result_elem.update(asr_result)
        asr_progress_elem.update('画像生成中...')
        window.perform_long_operation(lambda:stable_diffusion(), end_key='complete_stable_diffusion')
    elif event == 'complete_stable_diffusion':
        image_elem.update(data=get_image_from_file(generate_file, first=True))
        asr_progress_elem.update('画像生成終了')
        window['start_asr'].update(disabled=False)

window.close()
exit(0)
