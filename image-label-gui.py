import kivy

import scipy.ndimage
import os
import pprint
import pickle

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

_DOWN_ = 160

class DatasetApp(App):
    img1 = Image(source = 'main.png')
    layout = BoxLayout(orientation='vertical')
    img1.pos = (0,layout.height)
    img_vector = []
    proporcao = 0
    dropped = False
    count = 0
    tl = []
    br = []
    labels = []
    save_result = {}
    the_path = 0
    ipt1 = TextInput(size_hint_y=None,
                         height = 40,
                         font_size = 25)
    btn1 = Button(text="Pular Imagem", height=40, size_hint_y=None)
    btn2 = Button(text="Save", height=40, size_hint_y = None)
    btn3 = Button(text="Voltar", height=40, size_hint_y = None)
    First = True

    def build(self):
        Window.bind(on_dropfile=self._on_file_drop)
        Window.bind(on_motion=self.on_motion)
        self.btn1.bind(on_press=self._update_image)
        self.btn2.bind(on_press=self.save)
        self.btn3.bind(on_press=self.volta)

        h, w, channels = scipy.ndimage.imread('main.png').shape
        ratio = w/h
        Window.size = (ratio*500, 500 + _DOWN_)

        self.layout.add_widget(self.img1)
        self.layout.add_widget(self.ipt1)
        self.layout.add_widget(self.btn1)
        self.layout.add_widget(self.btn3)
        self.layout.add_widget(self.btn2)
        return self.layout

    def _on_file_drop(self, window, file_path):
        self.count = 0
        path = file_path.decode("utf-8")
        self.the_path = path
        for filename in os.listdir(path):
            if filename.endswith(".jpg"):
                self.img_vector.append(path+'/'+filename)
        self.dropped = True
        if os.path.isfile(path+'/labels.txt'):
            with open(path+'/img_vector.txt', "rb") as input:
                self.img_vector = pickle.load(input)
            with open(path+'/labels.txt', "rb") as input:
                self.labels = pickle.load(input)
            with open(path+'/tl.txt', "rb") as input:
                self.tl = pickle.load(input)
            with open(path+'/br.txt', "rb") as input:
                self.br = pickle.load(input)
            self.count = len(self.labels)
            print(self.count, self.labels, self.tl, self.br, self.img_vector)
        self._update_image()
        return

    def _update_image(self, *args):
        if(self.count <= len(self.img_vector) and self.dropped):
            if (self.count < len(self.img_vector)):
                self.img1.source = self.img_vector[self.count]

                h, w, channels = scipy.ndimage.imread(self.img_vector[self.count]).shape
                ratio = w/h
                Window.size = (ratio*500, 500 + _DOWN_)
                self.proporcao = h/500

            if self.First:
                self.First = False
            else:
                if (len(self.tl) < self.count):
                    self.tl.append((0,0))
                    self.br.append((0,0))
                    self.labels.append(0)

            self.count = self.count+1
            print(self.count)
        else:
            print("Cabou imagens!")
        return

    def on_motion(self, etype, motionevent, *args):
        if((etype.mouse_pos[1] >= _DOWN_) and not self.First):
            x = etype.mouse_pos[0]
            y = etype.mouse_pos[1] - _DOWN_

            if (motionevent == 'begin'):
                self.tl.append((int(x*self.proporcao), int(y*self.proporcao)))
            if (motionevent == 'end'):
                self.br.append((int(x*self.proporcao), int(y*self.proporcao)))
                self.labels.append(self.ipt1.text)
                self._update_image()
                print("DEU BOM!")
        return

    def save(self, *args):
        print(self.img_vector, self.labels, self.tl, self.br)
        for i in range(len(self.labels)):
            save = {i: {'location':self.img_vector[i],'label': self.labels[i], 'topleft': {'x': self.tl[i][0], 'y': self.tl[i][1]}, 'bottomright': {'x': self.br[i][0], 'y': self.br[i][1]}} }
            self.save_result.update(save)
        with open(self.the_path+'/img_vector.txt', 'wb') as f:
            pickle.dump(self.img_vector, f)
        with open(self.the_path+'/labels.txt', 'wb') as f:
            pickle.dump(self.labels, f)
        with open(self.the_path+'/tl.txt', 'wb') as f:
            pickle.dump(self.tl, f)
        with open(self.the_path+'/br.txt', 'wb') as f:
            pickle.dump(self.br, f)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.save_result)
        return

    def volta(self, *args):
        self.count = self.count - 2
        self._update_image()
        self.img_vector.insert(self.count, self.img_vector[self.count-1])
        self.count = self.count + 1
        return

DatasetApp().run()
