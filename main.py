"""

GUI initiation.

Creates a ``Tuner()``object and runs ``Tuner().mainloop()``
"""

import tkinter as tk
from tkinter import ttk, Tk
from tkinter.ttk import Style
import sounddevice as sd
import tuner.tunertools as tunertools

class AboutDialog(tk.Toplevel):
    """
    A class for creating simple dialogs that
    display one label.

    Attributes:
        abtframe tk.Frame:
            GUI Frame
        abtstyle ttk.Style:
            style settings for about text
        about str:
            text to be displayed

    Inheritance:
        tk.Toplevel:
            top level window (child window) to main (parent) window

    Args:
        about str:
        master tk.Tk:
        mastertitle='PyTuner' str:
        bg_hex='#ffffff' str:
        fg_hex='#000000' str:

    """
    
    def __init__(self, about, master, mastertitle='PyTuner', bg_hex = '#ffffff', fg_hex='#000000'):
        """
        Description of __init__

        Args:
            self tk.Toplevel:
            about str:
            master tk.TK:
            mastertitle='PyTuner' str:
            bg_hex='#ffffff' str:
            fg_hex='#000000' str:

        """
        
        tk.Toplevel.__init__(self)

        self.abtframe = tk.Frame(self, relief='flat', width=200, height=200, bg='white')
        self.abtframe.pack(fill='both', expand=False)
        
        self.abtstyle = ttk.Style()
        self.abtstyle.configure('About.TLabel', background=bg_hex, foreground=fg_hex)
        
        self.about = ttk.Label(text=about, master=self.abtframe, style='About.TLabel')
        self.about.pack(fill='both', pady=10, padx=10)
# Note Playing ttk.Button
class CustomPlayButton(ttk.Button):
    """
    Description of CustomPlayButton

    Attributes:
        file_path (type):
        'command'] (type):
        file_path) (type):

    Inheritance:
        ttk.Button:

    """
    def play_sound_file_path(self, file_path):
        self.file_path = file_path
        self['command'] = lambda: tunertools.play(self.file_path)


class Tuner(Tk):
    """
    A class for creating a guitar tuner.

    Attributes:
        background tk.Label:
            Background image placeholder
        background.image tk.PhotoImage:
            file path to background image
        background['image'] tk.PhotoImage:
            reference to background.image
        style ttk.Style:
            style config for gui
        recording bool:
            whether or not tuner is actively recording
        previously_recording bool:
            whether or not tuner has previously recorded
        rec sd.InputStream, None:
            Input for live sound data. If not recording then none.
        note_label tk.Label:
            Output Note for last 4 seconds of recording input

    Inheritance:
        Tk:
            Tkinter GUI

    """
    def __init__(self):
        """
        Initiates all needed varialbles to create class

        Args:
            self tk.Tk:
                parent for storing instances created

        """
        # initialize window

        super(Tuner, self).__init__()
        self.geometry('600x600')
        self.title('PyTuner v1')
        self.minsize(640, 480)
        self.maxsize(640, 480)
        self.background = tk.Label(self)
        self.background.image = tk.PhotoImage(file = 'tuner/images/neck_cropped_enhanced_resized.png')
        self.background['image'] = self.background.image
        self.background.place(x=0, y=0, relwidth=1, relheight=1,)
        self.style = Style()
        self.style_init()
        self.create_note_widgets()
        self.create_tuner_widgets()
        self.create_about_dialog_widget()
        self.cosmetics()
        
        # recording settings

        self.recording = self.previously_recording = False
        self.rec = None
        self.note_label = ttk.Label(self, style='Tuned.TLabel')
        self.note_label.place(x=0, y=50)

    def style_init(self):
        """
        creates style settings for gui widgets

        Args:
            self tk.Tk:
                parent for storing instances created

        """
        self.style.theme_use('default')
        self.style.configure('Note.TButton', font='Futura 16',
                                foreground='#ffffff', background='#95341f',relief='flat')
        self.style.map('Note.TButton',
                        foreground=[('pressed', '#95341f')],
                        background=[('pressed','#ffffff'),])

        self.style.configure('Rec.TButton', font='Futura 16',
                                foreground='white', background='black',
                                padx=10, pady=10, relief='flat')
        self.style.map('Rec.TButton',
                        foreground=[('active', '#bbff00')],
                        background=[('active', '#000000')])
        self.style.configure('Tuned.TLabel', font='Futura 24',
                                foreground='green', background='white')
        self.style.configure('NotTuned.TLabel', font='Futura 24',
                                foreground='red', background='white')
        self.style.configure('Title.TLabel', font='Futura 48',
                                foreground='black', background='white')

    def create_stream(self):
        """
        Initializes an input stream for audio

        Args:
            self tk.Tk:
                parent for storing instances created

        """
        if self.rec is not None:
            self.rec.close()
        self.on_rec()
        self.rec = sd.InputStream(samplerate=44100, channels=1,
                                    callback=self.callback, blocksize=4*44100)
        self.rec.start()

    def callback(self, indata, frames, time, status):
        """
        Function for internal use by
        sd.InputStream (self.rec)

        Args:
            self tk.Tk:
                parent for storing instances created
            indata np.ndarray:
                data from self.rec for pitch determination
            frames int:
                samplerate of audio input (Not Directly Used)
            time undefined:
                time for execution (Not Used)
            status undefined:
                status of stream (Not Used)

        """
        self.on_rec()
        if self.recording:
            data = indata.copy()

        self.yin, *others = tunertools.YIN([i for j in data for i in j], 44100)
        del others
        self.pitch = tunertools.avg_pitch(self.yin)

        self.noteslist = dict(tunertools.notes())
        self.note = tunertools.quantize(self.pitch,
                                        list(self.noteslist.values()))
        self.label = {v: k for (k, v) in self.noteslist.items()}[self.note]
        if abs(self.pitch-self.note) <= 1:
            self.update_labels(self.label + ' ' + str(round(self.pitch, ndigits=2)), 'Tuned.TLabel')
        else:
            self.update_labels(self.label + ' ' + str(round(self.pitch, ndigits=2)), 'NotTuned.TLabel')


    def on_stop(self):
        """
        what to do when audio input needs to be stopped

        Args:
            self tk.Tk:
                parent for storing instances created
        """
        self.recording = False
        self.previously_recording = True
        self.rec.stop()
        self.rec.close()
        self.rec = None
        self.rec_button['command'] = self.create_stream
        self.update_labels('', 'Tuned.TLabel')
        self.rec_button['text'] = 'Start Tuning'


    def on_rec(self):
        """
        changes self.recording instance to true and modifies a gui widget

        Args:
            self tk.Tk:
                parent for storing instances created
        """
        self.recording = True
        self.rec_button['text'] = 'Stop Tuning'
        self.rec_button['command'] = self.on_stop



    def update_labels(self, label, style):
        """
        update note label based on pitch of audio input

        Args:
            self tk.TK:
                parent for storing instances created
            label str:
                text for label
            style str:
                style configuration to be used for label

        """
        self.note_label['text'] = label
        self.note_label['style'] = style

    def create_note_widgets(self):
        """
        creates six buttons and assign them each a command to play a different string

        Args:
            self tk.Tk:
                parent for storing instances created

        """
        notes = ['Elo', 'A', 'D', 'G', 'B', 'Ehi']
        label_text = ['E2', 'A2', 'D3','G3', 'B4', 'E4']
        pos_label = [(175, 140), (175, 205), (175, 260), (470, 140), (470, 205), (470, 260)]
        self.button_list = []
        pos = -1
        for i in notes:
            pos += 1
            self.button_list.append(CustomPlayButton(self,
                                                        style='Note.TButton'))
            self.button_list[pos]['text'] = label_text[pos]
            self.button_list[pos].play_sound_file_path(f'tuner/GuitarNotes/\
                                        {notes[pos]}0.wav'.replace(" ", ""))
            self.button_list[pos].place(x=pos_label[pos][0],y=pos_label[pos][1])

    def create_tuner_widgets(self):
        """
        creates button to start and stop tuning

        Args:
            self tk.Tk:
                parent for storing instances created

        """
        self.rec_button = ttk.Button(self, style='Rec.TButton')
        self.rec_button['text'] = 'Start Tuning'
        self.rec_button['command'] = self.create_stream
        self.rec_button.place(x=20, y=10)
    def create_about_dialog(self):
        """
        creates a AboutDialog instance and assigns a parsed tuner/about.txt file to it

        Args:
            self tk.Tk:
                parent for storing instances created
        """
        self.f = open('tuner/about.txt')
        self.f_lines = self.f.readlines()
        self.about = ''.join(self.f_lines)
        self.about_dialog = AboutDialog(self.about, self)
    def create_about_dialog_widget(self):
        """
        creates a button which displays AboutDialog

        Args:
            self (undefined):

        """
        self.abtbutton = ttk.Button(self, text='About PyTuner', style='Rec.TButton')
        self.abtbutton['command'] = self.create_about_dialog
        self.abtbutton.place(x=210,y=430)
        
    def cosmetics(self):
        """
        extra widgets to enhance looks

        Args:
            self tk.Tk:
                parent for storing instances created

        """
        self.title_label = ttk.Label(self, text='PyTuner', style='Title.TLabel')
        self.title_label.place(x=275, y=0)

def main():
    """Create and Display Tuner() class"""
    root = Tuner()
    root.mainloop()

if __name__ == '__main__':
    main()
