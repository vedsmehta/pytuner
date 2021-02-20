import tkinter as tk
from tkinter import ttk



class LabelDropdown(tk.Frame):
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
        self.button['command'] = self.show
        self.button['text'] = self.buttonlabel + ' ▶'
        for i in self.label_widgets:
            i.grid_forget()
    def style_init(self):
        self.style = ttk.Style(self)
        self.style.configure('DD.TLabel',
                             font=self.buttonlabel_font,
                             foreground=self.buttonlabel_fg,
                             background=self.buttonlabel_bg,
                             relief='flat')
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