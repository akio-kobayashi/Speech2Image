#-*- coding: utf8 -*-
import tkinter
from PIL import Image, ImageTk
import wave, subprocess
import torch
from diffusers import DiffusionPipeline
import xformers
import whisper
import os, time, ffmpeg, numpy

window_geometory="1024x768"
canvas_width=640
canvas_height=480
model_id="stabilityai/japanese-stable-diffusion-xl"
whisper_model="large"
image_file="test.png"
audio_file="audio.wav"
second=5
command = ['parecord', '--channels=1', '--device=alsa_input.usb-Focusrite_iTrack_Solo-00.analog-stereo', 'audio.wav']

# ウィジェットパーツ
window = tkinter.Tk()
button = tkinter.Button(text=u'音声認識', width=100, font=("Helvetica", 24),bg="RosyBrown1" )
entry1 = tkinter.Entry(width=200, font=("Helvetica", 24), bg="white" )
label2 = tkinter.Label(window, text='音声認識結果', font=("Helvetica", 24), bg="white" )
entry2 = tkinter.Entry(width=200, font=("Helvetica", 24), bg="white" )
label3 = tkinter.Label(window, text='描画結果', font=("Helvetica", 24), bg="white" )
canvas = tkinter.Canvas(window, bg="white", height=canvas_height, width=canvas_width)

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

def draw_image():
    img = Image.open(image_file)
    img = img.resize(( int(img.width * (canvas_width/img.width)), int(img.height * (canvas_height/img.width)) ))
    img = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, image=img, anchor=tkinter.NW)

def record_audio():
    _execute_shell_command(command, second)

def process(event):
    entry1.delete(0, tkinter.END)
    entry1.insert(tkinter.END, "パソコンのマイクに向かって5秒話してください...")
    time.spee(1)
    record_audio()
    entry1.delete(0, tkinter.END)
    entry1.insert(tkinter.END, "録音終了")

# ウィンドウ
window.geometry(window_geometory)
window.title("Stable Diffusion w/ Whisper in Japanese")
window.configure(bg="white")

# 音声認識ボタン
button.bind("<Button-1>", process)
button.pack(pady=10)

# 進行状況
entry1.pack(pady=10)
entry1.delete(0, tkinter.END)

# 音声認識結果
label2.pack(pady=10)
entry2.pack(pady=10)
entry2.delete(0, tkinter.END)

# 描画キャンバス
label3.pack(pady=10)
canvas.pack(pady=10)
#canvas.place(x=0, y=0)

#pipeline = prepare_pipeline()
#model = prepare_whisper()

window.mainloop()


