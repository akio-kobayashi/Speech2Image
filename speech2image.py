#-*- coding: utf8 -*-
import tkinter
from PIL import Image, ImageTk
import wave, subprocess
import torch
from diffusers import DiffusionPipeline
import xformers
import whisper
import os, time, ffmpeg, numpy

class ModifiedEntry(tkinter.Entry):
    def __init__(self, *args, **kwargs):
        tkinter.Entry.__init__(self, *args, **kwargs)
        self.sv = tkinter.StringVar()
        self.sv.trace('w',self.var_changed)
        self.configure(textvariable = self.sv)

    # argsにはtrace発生元のVarの_nameが入っている
    # argsのnameと内包StringVarの_nameが一致したらイベントを発生させる。
    def var_changed(self, *args):
        if args[0] == self.sv._name:
            s = self.sv.get() 
            self.event_generate("<<TextModified>>")

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
entry1 = ModifiedEntry(width=200, font=("Helvetica", 24), bg="white" )
label2 = tkinter.Label(window, text='音声認識結果', font=("Helvetica", 24), bg="white" )
entry2 = ModifiedEntry(width=200, font=("Helvetica", 24), bg="white" )
label3 = tkinter.Label(window, text='Stable Diffusion', font=("Helvetica", 24), bg="white" )
entry3 = ModifiedEntry(width=200, font=("Helvetica", 24), bg="white")
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

def process1(event):
    entry1.delete(0, tkinter.END)
    button["state"] = tkinter.DISABLED
    entry1.insert(tkinter.END, "パソコンのマイクに向かって5秒話してください...")

def process2(event):
    record_audio()
    entry1.delete(0, tkinter.END)
    entry1.insert(tkinter.END, "録音終了")

def process3(event):
    entry3.delete(0, tkinter.END)
    entry3.insert(tkinter.END, "描画中...")

def process4(event):
    time.sleep(5)
    button["state"] = tkinter.NORMAL
    entry3.delete(0, tkinter.END)
    entry3.insert(tkinter.END, "描画終了")

# ウィンドウ
window.geometry(window_geometory)
window.title("Stable Diffusion w/ Whisper in Japanese")
window.configure(bg="white")

# 音声認識ボタン
button.bind("<Button-1>", process1)
button.pack(pady=10)

# 進行状況
entry1.pack(pady=10)
entry1.delete(0, tkinter.END)
entry1.bind("<<TextModified>>", process2, '+')

# 音声認識結果
label2.pack(pady=10)
entry2.pack(pady=10)
entry2.delete(0, tkinter.END)
entry2.bind("<<TextModified>>", process3, '+')

# 描画キャンバス
label3.pack(pady=10)
entry3.pack(pady=10)
entry3.delete(0, tkinter.END)
entry3.bind("<<TextModified>>", process4, '+')
canvas.pack(pady=10)
#canvas.place(x=0, y=0)

#pipeline = prepare_pipeline()
#model = prepare_whisper()

window.mainloop()


