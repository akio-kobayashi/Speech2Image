#-*- coding: utf8 -*-
import tkinter
from PIL import Image, ImageTk
import wave, subprocess
import torch
from diffusers import DiffusionPipeline
import xformers

window_geometory="1024x768"
canvas_width=640
canvas_height=480
model_id="stabilityai/japanese-stable-diffusion-xl"
whisper_model="large"

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

window = tkinter.Tk()
window.geometry(window_geometory)
window.title("Stable Diffusion w/ Whisper in Japanese")

canvas = tkinter.Canvas(window, bg="#fff", height=canvas_height, width=canvas_width)
canvas.place(x=0, y=0)

pipeline = prepare_pipeline()
model = prepare_whisper()

window.mainloop()

def draw_image():
    img = Image.open('test.png')
    img = img.resize(( int(img.width * (canvas_width/img.width)), int(img.height * (canvas_height/img.width)) ))
    img = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, image=img, anchor=tkinter.NW)

