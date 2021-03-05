"""
GUI initiation.

Creates a ``Tuner()``object and runs ``Tuner().mainloop()``
"""

__author__ = 'Vedant Mehta'

import os
import tkinter as tk
from tkinter import ttk, Tk
from tkinter.ttk import Style
import sounddevice as sd
import tunertools
from dropdown import LabelDropdown


class AboutDialog(tk.Toplevel):
    """AboutDialog.
    """

    def __init__(
            self,
            about,
            master,
            mastertitle='PyTuner',
            bg_hex='#ffffff',
            fg_hex='#000000'):
        """__init__.

        Parameters
        ----------
        about : str
            string to be stored in window (about statement)
        master : tk.Tk
            Parent window of about dialog
        mastertitle : str
            Title of master
        bg_hex : str
            background color for about dialog
        fg_hex : str
            font color for about dialog
        """

        tk.Toplevel.__init__(self)

        self.abtframe = tk.Frame(
            self,
            relief='flat',
            width=200,
            height=200,
            bg='white')
        self.abtframe.pack(fill='both', expand=False)

        self.abtstyle = ttk.Style()
        self.abtstyle.configure(
            'About.TLabel',
            font='Futura 14',
            background=bg_hex,
            foreground=fg_hex)

        self.about = ttk.Label(
            text=about,
            master=self.abtframe,
            style='About.TLabel')
        self.about.pack(fill='both', pady=10, padx=10)
# Note Playing ttk.Button


class CustomPlayButton(ttk.Button):
    """CustomPlayButton.
    """

    def play_sound_file_path(self, file_path):
        """play_sound_file_path.

        Parameters
        ----------
        file_path : str
            path to audio file
        """
        self.file_path = file_path
        self['command'] = lambda: tunertools.play(self.file_path)
        """callback function for the InputStream

        Parameters
        ----------
        indata :
            indata
        frames :
            frames
        time :
            time
        status :
            status
        """


class Tuner(Tk):
    """Tuner.
    """

    def __init__(self):
        """__init__.
        """
        # initialize window

        super(Tuner, self).__init__()
        self.geometry('600x600')
        self.title('PyTuner 1.0.0')
        self.minsize(640, 480)
        self.maxsize(640, 480)
        self.background = tk.Label(self)
        filepath = os.path.abspath(__file__)
        dirpath = os.path.dirname(filepath)
        img_path = os.path.join(
            dirpath, 'images/neck_cropped_enhanced_resized.png')
        self.background.image = tk.PhotoImage(file=img_path)
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
        self.note_label.place(relx=.11, rely=.13, anchor='center')

    def style_init(self):
        """style_init.
        """
        self.style.theme_use('default')

        # note button
        self.style.configure(
            'Note.TButton',
            font='Futura 16',
            foreground='#ffffff',
            background='#95341f',
            relief='flat')
        self.style.map('Note.TButton',
                       foreground=[('pressed', '#95341f')],
                       background=[('pressed', '#ffffff'), ])
        # recording and about button
        self.style.configure('Rec.TButton', font='Futura 16',
                             foreground='white', background='black',
                             padx=10, pady=10, relief='flat')
        self.style.map('Rec.TButton',
                       foreground=[('active', '#bbff00')],
                       background=[('active', '#000000')])
        # tuning labels
        self.style.configure('Tuned.TLabel', font='Futura 16',
                             foreground='green', background='white')
        
        self.style.configure('NotTuned.TLabel', font='Futura 16',
                             foreground='red', background='white')
        # title label
        self.style.configure('Title.TLabel', font='Futura 48',
                             foreground='black', background='white')

    def create_stream(self):
        """
        create_stream is a function that creates an input stream for sound data from the main Microphone.
        Uses sounddevice library InputStream class to record data
        """
        if self.rec is not None:
            self.rec.close()
        self.on_rec()
        self.rec = sd.InputStream(samplerate=44100, device='Microphone',
                                  callback=self.callback, blocksize=4 * 44100)
        self.rec.start()

    def callback(self, indata, frames, time, status):
        """
        Function for internal use by
        sd.InputStream (self.rec)

        Parameters
        ----------
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
        # get data
        if self.recording:
            data = indata.copy()
        # run pitch detection algorithms
        self.yin, *others = tunertools.YIN([i for j in data for i in j], 44100)
        del others
        self.YAAPT = tunertools.yaapt([i for j in data for i in j])
        # set the pitch
        self.pitch = tunertools.avg_pitch(self.YAAPT.samp_values)
        # Get the list of possible notes
        self.noteslist = dict(tunertools.notes())
        # Round the pitch to the nearest note
        self.note = tunertools.quantize(self.pitch,
                                        list(self.noteslist.values()))
        # Map the notes
        self.label = {v: k for (k, v) in self.noteslist.items()}[self.note]
        # Update the style on label
        if abs(self.pitch - self.note) <= 1:
            self.update_labels(
                self.label + ' ' + str(round(self.pitch, ndigits=2)), 'Tuned.TLabel')
        else:
            self.update_labels(
                self.label + ' ' + str(round(self.pitch, ndigits=2)), 'NotTuned.TLabel')

    def on_stop(self):
        """on_stop.
        Sets the stop setting for tuner
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
        """on_rec.
        Sets the start setting for tuner
        """
        self.recording = True
        self.rec_button['text'] = 'Stop Tuning'
        self.rec_button['command'] = self.on_stop

    def update_labels(self, label, style):
        self.note_label['text'] = label
        self.note_label['style'] = style

    def create_note_widgets(self):
        """create_note_widgets.
        """
        notes = ['Elo', 'A', 'D', 'G', 'B', 'Ehi']
        label_text = ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']
        pos_label = [(175, 260), (175, 205), (175, 140),
                     (470, 140), (470, 205), (470, 260)]
        self.button_list = []
        pos = -1
        for i in notes:
            pos += 1
            self.button_list.append(CustomPlayButton(self,
                                                     style='Note.TButton'))
            self.button_list[pos]['text'] = label_text[pos]
            self.button_list[pos].play_sound_file_path(f'GuitarNotes/\
                                        {notes[pos]}0.wav'.replace(" ", ""))
            self.button_list[pos].place(
                x=pos_label[pos][0], y=pos_label[pos][1])

    def create_tuner_widgets(self):
        """create_tuner_widgets.
        """
        self.rec_button = ttk.Button(self, style='Rec.TButton')
        self.rec_button['text'] = 'Start Tuning'
        self.rec_button['command'] = self.create_stream
        self.rec_button.place(x=20, y=10)

    def create_about_dialog(self):
        """create_about_dialog.
        """
        self.f = open('about.txt')
        self.f_lines = self.f.readlines()
        self.about = ''.join(self.f_lines)
        self.about_dialog = AboutDialog(self.about, self)

    def create_about_dialog_widget(self):
        """create_about_dialog_widget.
        """
        self.abtbutton = ttk.Button(
            self, text='About PyTuner', style='Rec.TButton')
        self.abtbutton['command'] = self.create_about_dialog
        self.abtbutton.place(x=210, y=430)

    def cosmetics(self):
        """cosmetics.
        """
        self.title_label = ttk.Label(
            self, text='PyTuner', style='Title.TLabel')
        self.title_label.place(x=275, y=0)
        self.dropdown_label = "E2: 82.42\nA2: 110.00\nD3: 146.83\nG3: 196.00\nB3: 246.94\nE4: 329.63"
        self.dropdown = LabelDropdown(
            self,
            self.dropdown_label,
            "View Pitch Frequencies",
            'Futura 12',
            '#000000',
            '#ffffff',
            'Futura 14',
            '#000000',
            '#ffffff')
        self.dropdown.place(x=5, y=85)


def main():
    """Create and Display Tuner() class"""
    root = Tuner()
    root.mainloop()


if __name__ == '__main__':
    main()
