import tkinter as tk
from tkinter import ttk



class LabelDropdown(tk.Frame):
    """
    Description of LabelDropdown

    Attributes:
        'background' str:
            background of frame
        label str:
            label for dropdown
        buttonlabel (type): 
            text on dropdown (button)
        label_font str:
            font config for label
        label_fg str:
            hex color for foreground
        label_bg str:
            hex color for background
        buttonlabel_font str:
            font config for button text
        buttonlabel_fg str:
            foreground hex for button
        buttonlabel_bg str:
            background hex for button
        indent str:
            indent of text in spaces
        button ttk.Button:
            button widget

    Inheritance:
        tk.Frame:
            widget conainter

    Args:
        master tk.Toplevel, tk.Tk, etc.:
        label str:
            text under button (to be displayed)
        buttonlabel str:
            label for button
        label_font str:
            font config for label
        label_fg str:
            foreground hex for label
        label_bg str:
            background hex for label
        buttonlabel_font str:
            font config for button
        buttonlabel_fg str:
            foreground hex for button
        buttonlabel_bg str:
            background hex for button
        indent='' str:
            indent in spaces for text

    """
    def __init__(self, master, label, buttonlabel, label_font, label_fg, label_bg,
                 buttonlabel_font, buttonlabel_fg, buttonlabel_bg, indent='  '):
        super(LabelDropdown, self).__init__()
        self['background'] = '#ffffff'
        self.label = label
        self.buttonlabel = buttonlabel
        self.label_font = label_font
        self.label_fg = label_fg
        self.label_bg = label_bg
        self.buttonlabel_font = buttonlabel_font
        self.buttonlabel_fg = buttonlabel_fg
        self.buttonlabel_bg = buttonlabel_bg
        self.indent = indent
        self.button = ttk.Button(self, text=self.buttonlabel+' ▶', style='DD.TButton', command=self.show)
        self.button.grid(row=0, column=0)
        self.style_init()
    def show(self):
        """
        Show Label
        """
        self.button['command'] = self.hide
        self.button['text'] = self.buttonlabel + ' ▼'
        self.label_list = self.label.split('\n')
        self.label_widgets = []
        if len(self.label_widgets) == 0:
            for i in range(len(self.label_list)):
                self.label_list[i] = self.indent+self.label_list[i] # notice that indent.join(label_list) would leave out the first line.
                self.label_widgets.append(ttk.Label(self, text=self.label_list[i], style='DD.TLabel'))
                self.label_widgets[i].grid(row=i+1, column=0)
        else:
            for i in range(len(self.label_widgets)):
                self.label_widgets[i].grid(row=i+1,column=0)
    def hide(self):
        """
        Hide Docstring
        """
        self.button['command'] = self.show
        self.button['text'] = self.buttonlabel + ' ▶'
        for i in self.label_widgets:
            i.grid_forget()
    def style_init(self):
        """
        initialize styles
        """
        self.style = ttk.Style(self)
        self.style.configure('DD.TLabel',
                             font=self.buttonlabel_font,
                             foreground=self.buttonlabel_fg,
                             background=self.buttonlabel_bg,
                             relief='flat', pady=10)
        self.style.configure('DD.TButton',
                             font=self.buttonlabel_font,
                             foreground=self.buttonlabel_fg,
                             background=self.buttonlabel_bg,
                             relief='flat')
        self.style.map('DD.TButton',
                       foreground=[('active', '#000000')],
                       background=[('active', '#ffffff')])
        self.style.layout('DD.TButton',
                          [('Button.button',
                            {'sticky': 'nswe', 'children': 
                                #[('Button.padding', {'sticky': 'nswe', 'children': 
                                    [('Button.label', {'sticky': 'nswe'})]
                                   # })]
                                })]
                          )