import webbrowser as web
from kivymd.app import MDApp
from kivy.lang import Builder
import pygame
from mutagen.mp3 import MP3
from kivymd.uix.list import MDList , TwoLineAvatarIconListItem , IconLeftWidget
import time
import threading as th

code = '''
<DrawerClickableItem@MDNavigationDrawerItem>

<Bar_T@MDTopAppBar>
	title : 'Sangeet'
	left_action_items : [['menu' , lambda x = '1' : app.root.ids.drawer.set_state('open')]]
	elevation : -1
	pos_hint : {'top':1}

MDNavigationLayout:
	ScreenManager:
		id : manager

		MDScreen:
			name : 'home'
			Bar_T
			ScrollView:
				pos_hint : {"center_y" : 0.425}
				MDList:
					id : list
		
		MDScreen:
			name : 'music'
			Bar_T
			MDFloatLayout:
				orientation : "vertical"
				pos_hint : {'center_x' : 0.5 , "center_y":0.5}
				size_hint : (0.9 , 0.7)
				canvas:
					Color:
				        rgba: 41/255, 44/255, 48/255 , 1
					RoundedRectangle:
						pos: self.pos
						size: self.size
						radius: [25,]
				MDLabel:
					text : ""
					bold : True
					text_color : 1,1,1,1
					id : song_name
					pos_hint : {"center_x" : 0.825 , "center_y" : 0.9}
					font_size : "25dp"
				
				MDFloatingActionButton:
					icon : "chevron-left"
					pos_hint : {"center_x" : 0.15 , "center_y" : 0.9}
					size_hint : (0.15 , 0.1)
					on_release : app.back()
					elevation : -1
				
				Image:
					source : "music-2.png"
					size_hint : (0.6 , 0.6)
					pos_hint : {"center_x" : 0.5 , "center_y" : 0.6}
				
				MDSlider:
					id : slider
					min : 0
					max : 100
					sizer_hint_y : 1
					hint: False
					pos_hint : {"center_x" : 0.5}
					on_active : app.set_song_pos(self.value)
					
				MDFloatingActionButton:
					icon : "play"
					id : control_button
					pos_hint : {"center_x" : 0.5 , "center_y" : 0.125}
					size_hint : (0.15 , 0.1)
					on_release : app.play()
				
				MDFloatingActionButton:
					icon : "skip-backward"
					pos_hint : {"center_x" : 0.25 , "center_y" : 0.125}
					size_hint : (0.15 , 0.1)
					on_release : app.set_song_pos(app.song_pos - 10)
				
				MDFloatingActionButton:
					icon : "skip-forward"
					pos_hint : {"center_x" : 0.75 , "center_y" : 0.125}
					size_hint : (0.15 , 0.1)
					on_release : app.set_song_pos(app.song_pos + 10)
				
				MDLabel:
					id : total_length
					text : "1:20"
					font_size : "13dp"
					bold : True
					pos_hint : {"center_x" : 1.335 , "center_y" : 0.25}
				
				MDLabel:
					id : played_length
					font_size : "13dp"
					text : "00:00 of"
					bold : True
					pos_hint : {"center_x" : 1.15 , "center_y" : 0.25}

	MDNavigationDrawer:
		id : drawer
		MDNavigationDrawerMenu:
			MDNavigationDrawerHeader:
				source : ""
				title : "Music App"
				spacing : '10dp'
				padding : '5dp',0,0,'5dp'

			MDNavigationDrawerDivider:
			MDNavigationDrawerLabel:
				text : 'Songs'
			DrawerClickableItem:
				text : 'Download'
				icon : 'download'
				text_color : 1,1,1,1
				on_release : app.download()
'''

class MyApp(MDApp):
	def on_start(self):
		self.get_songs()
		self.add_songs()
	
	def build(self):
		self.songs_name = []
		self.songs_path = []
		self.songs = 0
		self.song_num = 0
		self.music_playing = False
		self.pause = False
		self.song_length = 1
		self.song_time = ""
		self.thread = ""
		self.song_pos = 0
		self.brk = False
		self.website = "https://sangeet.github.io"
		self.theme_cls.primary_palette = "Orange"
		self.theme_cls.theme_style = "Dark"
		return Builder.load_string(code)

	def get_songs(self):
		files = os.listdir("/storage/emulated/0/Download")
		for file in files:
			if ".mp3" in file:
				self.songs_name.append(file)
				self.songs_path.append("/storage/emulated/0/Download/" + file)
				self.songs += 1
	
	def add_songs(self):
		for i in range(self.songs):
				list_item = TwoLineAvatarIconListItem(text = self.songs_name[i] , secondary_text = self.songs_path[i] , id = str(i) , on_release = lambda x: self.show_music_gui(int(x.id)))
				img = IconLeftWidget(icon = "music")
				list_item.add_widget(img)
				self.root.ids.list.add_widget(list_item)
	
	def download(self):
		web.open(self.website)
	
	def play(self):
		if self.music_playing:
			if self.pause:
				pygame.mixer.music.unpause()
				self.pause = False
				self.root.ids.control_button.icon = "pause"
			else:
				pygame.mixer.music.pause()
				self.pause = True
				self.root.ids.control_button.icon = "play"
		else:
			pygame.mixer.init()
			pygame.mixer.music.load(self.songs_path[self.song_num])
			pygame.mixer.music.set_volume(1)
			pygame.mixer.music.play(loops=0)
			self.music_playing = True
			self.root.ids.control_button.icon = "pause"
			self.thread = th.Thread(target = self.update_song_pos)
			self.thread.start()
	
	def back(self):
		self.open('home')
		self.music_playing = False
		self.song_pos = 0
		self.pause = False
		self.root.ids.played_length.text = "00:00  of"
		self.root.ids.control_button.icon = "play"
		self.brk = True
		self.root.ids.slider.value = 0
		try:
			pygame.mixer.music.stop()
		except:
			pass
	
	def music_gui(self , song_num):
		song = MP3(self.songs_path[self.song_num])
		self.song_length = song.info.length
		self.song_time = time.strftime('%M:%S',time.gmtime(self.song_length))
		self.root.ids.slider.max = self.song_length
		self.root.ids.total_length.text = self.song_time
		self.root.ids.manager.current='music'
		self.root.ids.song_name.text = self.songs_name[song_num].replace(".mp3","").replace("_"," ")
	
	def show_music_gui(self , song_num):
		self.song_num = song_num
		self.music_gui(song_num)

	def open(self , name):
		self.root.ids.manager.current = name
	
	def set_song_pos(self , val):
		if val>=self.song_length:
			self.back()
		else:
			try:
				pygame.mixer.music.set_pos(val)
				self.song_pos = val
				played_length = time.strftime('%M:%S',time.gmtime(self.song_pos))
				self.root.ids.played_length.text = played_length + "  of"
			except:
				pass
	
	def update_song_pos(self):
		while True:
			time.sleep(1)
			if self.music_playing:
				if self.pause:
					pass
				else:
					self.song_pos += 1
			if self.brk:
				self.song_pos = 0
				self.brk = False
				break
			if self.song_pos >= self.song_length:
				self.back()
				break
			try:
				self.root.ids.slider.value = self.song_pos
			except:
				pass
			played_length = time.strftime('%M:%S',time.gmtime(self.song_pos))
			self.root.ids.played_length.text = played_length + "  of"

MyApp().run()