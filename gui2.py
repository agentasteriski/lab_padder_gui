import tkinter as tk
from tkinter import filedialog
import os, ffmpeg
import customtkinter as ctk

script_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.exists('_assets/ds_gui.json'):
      ctk.set_default_color_theme("_assets/ds_gui.json")
else:
      pass
blank_file = os.path.join(script_dir, "blank.wav")

def input():
    global input_folder
    input_folder = filedialog.askdirectory(title="Select input folder")
    print("Input folder: " + input_folder)

def output():
    global output_folder
    output_folder = filedialog.askdirectory(title="Select output folder")
    print("Output folder: " + output_folder)

def create_blank_file(reference_file, output_file):
    probe = ffmpeg.probe(reference_file)
    audio_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'audio')
    
    sample_rate = audio_stream['sample_rate']
    channels = audio_stream['channels']
    ffmpeg.input('anullsrc=channel_layout=stereo:sample_rate={}'.format(sample_rate), f='lavfi').output(output_file, t=0.5, acodec='pcm_s16le', ac=channels).run(overwrite_output=True)

def runpad():
    # Get all .wav files in input folder
    files = [f for f in os.listdir(input_folder) if f.endswith('.wav')]

    for file in files:
        input_file = os.path.join(input_folder, file)
        output_file = os.path.join(output_folder, file)

        # Create a blank file with the same sample rate and number of channels as the input file
        create_blank_file(input_file, blank_file)

        # Create a temporary list file for ffmpeg concat
        concat_list_file = os.path.join(script_dir, 'concat_list.txt')
        with open(concat_list_file, 'w', encoding = "utf-8") as f:
            # Add silence (start), the original file, and silence (end)
            f.write(f"file '{blank_file}'\n")  # Silence at the beginning
            f.write(f"file '{input_file}'\n")  # Original audio file
            f.write(f"file '{blank_file}'\n")  # Silence at the end
        
        # Run ffmpeg using the concat list
        try:
            ffmpeg.input(concat_list_file, f='concat', safe=0).output(output_file, acodec='copy').run(overwrite_output=True)
        except ffmpeg.Error as e:
            print(f"Error while processing file {file}: {e.stderr.decode('utf8')}")

    # Clean up concat_list.txt after processing
    if os.path.exists(concat_list_file):
        os.remove(concat_list_file)

    # Run the additional script with relative paths
    print("Now for the labels...")

    os.system(f"python {script_dir}\lab_padder.py -d {input_folder} -o {output_folder}")

    print("Done!")
    

app = ctk.CTk()
app.title(".lab/.wav Padder 2")

button1 = ctk.CTkButton(app, text="Select input folder", command=input)
button1.grid(row=0, column=0, padx=10, pady=10)
button2 = ctk.CTkButton(app, text="Select output folder", command=output)
button2.grid(row=0, column=1, padx=10, pady=10)
button3 = ctk.CTkButton(app, text="Pad .lab/.wav", command=runpad)
button3.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

app.mainloop()

