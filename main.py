 
# -*- coding: utf-8 -*-

import remi.gui as gui
from remi import start, App
import brew_data
import math
import os
import ast

class customFileUploader(gui.FileUploader):
	def __init__(self, *args, **kwargs):
		super(customFileUploader, self).__init__(*args, **kwargs)

	@gui.decorate_set_on_listener("(self, emitter, filedata, filename)")
	@gui.decorate_event
	def ondata(self, filedata, filename):
		# print(os.path.join(self._savepath, filename))
		# print(len([f for f in os.listdir(self._savepath) if filename in f]))
		if len([f for f in os.listdir(self._savepath) if filename in f]) > 0:
			filename = '{0}'.format(len([f for f in os.listdir(self._savepath) if filename in f])).join(os.path.splitext(filename))
			# print(filename)
		self.current_file = os.path.join(self._savepath, filename)
		with open(os.path.join(self._savepath, filename), 'wb') as f:
			f.write(filedata)
		return (filedata, filename)

class AddNewDialog(gui.GenericDialog):
	def __init__(self, item_list,**kwargs):
		super(AddNewDialog, self).__init__(**kwargs)

		self.listView = gui.ListView().new_from_list(item_list)
		# self.listView.attributes['multiple'] = True
		self.listView.style.update({"margin":"0px", "height":"500px","overflow":"auto"})
		self.add_field('listview', self.listView)
		self.confirm_dialog.connect(self.confirm_value)

	@gui.decorate_set_on_listener("(self, emitter, value)")
	@gui.decorate_event
	def confirm_value(self, widget):
		"""Event called pressing on OK button."""
		return (self.listView.get_value(),)

	@gui.decorate_explicit_alias_for_listener_registration
	def set_on_confirm_value_listener(self, callback, *userdata):
		self.confirm_value.connect(callback, *userdata)

class customTable(gui.Table):
	def __init__(self, **kwargs):
		super(customTable, self).__init__(**kwargs)

	@gui.decorate_event
	def on_table_row_click(self, row, item):
		if hasattr(self, "last_clicked_row"):
			del self.last_clicked_row.style['outline']
		self.last_clicked_row = row
		#print(vars(self))
		row_index = [child[0] for child in self.children.items() if child[1] == row][0]
		# print(row_index)
		self.last_clicked_row_index = row_index
		if row_index != '0':
			self.last_clicked_row.style['outline'] = "1px dotted red"
		return (row, item, row_index)

# set_on_table_row_click_listener
class beer_engine(App):
	def __init__(self, *args, **kwargs):
		#DON'T MAKE CHANGES HERE, THIS METHOD GETS OVERWRITTEN WHEN SAVING IN THE EDITOR
		if not 'editing_mode' in kwargs.keys():
			super(beer_engine, self).__init__(*args, static_file_path={'my_res':'./res/'})

		self.hops = []
		self.ingredients = []
		self.og = 1000
		self.ibu = 0

	def idle(self):
		#idle function called every update cycle
		pass
	
	def main(self):
		return beer_engine.construct_ui(self)
		
	@staticmethod
	def construct_ui(self):
		

		###################### CONFIG SECTION ############################
		#DON'T MAKE CHANGES HERE, THIS METHOD GETS OVERWRITTEN WHEN SAVING IN THE EDITOR
		
		
		self.mainContainer = gui.Widget(width='100%', height='100%')
		self.mainContainer.style['background-color'] = 'white'
		menubar = gui.MenuBar(height='4%')
		menu = gui.Menu(width='100%',height='100%')
		menu.style['z-index'] = '1'
		file_menu = gui.MenuItem('File', width=150, height='100%')
		open_menu = gui.MenuItem('Open', width=150, height=30)
		export_menu = gui.MenuItem('Export', width=150, height=30)
		file_menu.append([open_menu, export_menu])

		menu.append([file_menu])
		
		menubar.append(menu)

		self.mainContainer.append(menubar,'menubar')

		self.fuploader = customFileUploader(savepath='./recipes', style={'display':'none'})
		self.fuploader.attributes['accept'] = '.berfx, .berf'
		self.fuploader.onsuccess.do(self.fileupload_on_success)
		self.fuploader.onfailed.do(self.fileupload_on_failed)
		
		self.mainContainer.append(self.fuploader, 'fuploader')

		self.fexporter = gui.FileDownloader('Export', 'none', style={"display": "none"}) 
		self.mainContainer.append(self.fexporter, 'fexporter')

		# self.fileOpenDialog = gui.FileUploader(savepath='./recipes', multiple_selection_allowed=False)
		# self.fileOpenDialog.confirm_value.do(self.on_open_dialog_confirm)
		open_menu.onclick.do(lambda args: self.execute_javascript("document.getElementById('{0}').click();".format(self.fuploader.identifier)))

		export_menu.onclick.do(lambda args: self.download())

		###################### INTERFACE SECTION #########################
		engine_room = gui.Widget()
		engine_room.attributes.update({"class":"Widget","editor_constructor":"()","editor_varname":"engine_room","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Widget"})
		engine_room.style.update({"margin":"0px","width":"800px","height":"480px","top":"5%","left":"15px","position":"absolute","overflow":"auto"})
		self.mainContainer.append(engine_room, 'engine_room')

		recipe_name_lbl = gui.Label('Recipe Name:')
		recipe_name_lbl.attributes.update({"class":"Label","editor_constructor":"('Recipe Name:')","editor_varname":"recipe_name_lbl","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
		recipe_name_lbl.style.update({"margin":"0px","width":"87px","height":"18px","top":"13px","left":"10px","position":"absolute","overflow":"false","font-size":"12px"})
		engine_room.append(recipe_name_lbl,'recipe_name_lbl')

		recipe_name_ent = gui.TextInput(True,'')
		recipe_name_ent.attributes.update({"class":"TextInput","autocomplete":"off","editor_constructor":"(False,'')","editor_varname":"recipe_name_ent","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
		recipe_name_ent.style.update({"margin":"0px","width":"200.8px","height":"18px","top":"13px","left":"100px","position":"absolute","overflow":"auto", "text-align": "center"})
		engine_room.append(recipe_name_ent,'recipe_name_ent')
		recipe_name_ent.set_value('No Name')

		volume_lbl = gui.Label('Volume:')
		volume_lbl.attributes.update({"class":"Label","editor_constructor":"('Recipe Name:')","editor_varname":"volume_lbl","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
		volume_lbl.style.update({"margin":"0px","width":"53px","height":"18px","top":"13px","left":"330px","position":"absolute","overflow":"false","font-size":"12px"})
		engine_room.append(volume_lbl,'volume_lbl')

		volume_ent = gui.TextInput(True,'')
		volume_ent.attributes.update({"class":"TextInput","autocomplete":"off","editor_constructor":"(False,'')","editor_varname":"volume_ent","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
		volume_ent.style.update({"margin":"0px","width":"36px","height":"20px","top":"12px","left":"390px","position":"absolute","overflow":"auto", "text-align": "center"})
		engine_room.append(volume_ent,'volume_ent')
		volume_ent.set_value('10')

		boil_volume_lbl = gui.Label('Boil Volume:')
		boil_volume_lbl.attributes.update({"class":"Label","editor_constructor":"('Recipe Name:')","editor_varname":"boil_volume_lbl","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
		boil_volume_lbl.style.update({"margin":"0px","width":"78px","height":"19px","top":"12px","left":"460px","position":"absolute","overflow":"false","font-size":"12px"})
		engine_room.append(boil_volume_lbl,'boil_volume_lbl')

		boil_volume_ent = gui.TextInput(True,'')
		boil_volume_ent.attributes.update({"class":"TextInput","autocomplete":"off","editor_constructor":"(False,'')","editor_varname":"Entry1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
		boil_volume_ent.style.update({"margin":"0px","width":"46px","height":"23px","top":"10px","left":"540px","position":"absolute","overflow":"auto", "text-align": "center"})
		engine_room.append(boil_volume_ent,'boil_volume_ent')
		boil_volume_ent.set_value('11')


		ingredient_container = gui.Widget(width='460px', height='140px')
		ingredient_container.style.update({"margin":"0px","width":"460px","height":"140px","top":"40px","left":"10px","position":"absolute","overflow":"auto"})
		engine_room.append(ingredient_container,'ingredient_container')

		self.table_ingredient = table_ingredient = customTable().new_from_list([('Fermentable Ingredients', "Ebc", "Grav", "lb:oz", "Grams", "%")], width='460px', margin='10px')
		for c in table_ingredient.children.values():
			c.style['height'] = '30px'

		table_ingredient.attributes.update({"class":"TableWidget","editor_constructor":"(5,2,False,False)","editor_varname":"table_ingredient","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TableWidget"})
		table_ingredient.style.update({"margin":"0px","width":"450px","top":"0px","left":"0px","position":"absolute","float":"none","display":"table","overflow":"true"})
		ingredient_container.append(table_ingredient,'table_ingredient')

		ingredient_rem_butt = gui.Button('Remove')
		ingredient_rem_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"ingredient_rem_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		ingredient_rem_butt.style.update({"margin":"0px","width":"76px","height":"29px","top":"190px","left":"10px","position":"absolute","overflow":"auto"})
		engine_room.append(ingredient_rem_butt,'ingredient_rem_butt')
		ingredient_rem_butt.onclick.connect(lambda e: self.delete_ingredient())

		ingredient_add_new_butt = gui.Button('Add New')
		ingredient_add_new_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"ingredient_add_new_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		ingredient_add_new_butt.style.update({"margin":"0px","width":"82px","height":"28px","top":"40px","left":"480px","position":"absolute","overflow":"auto"})
		engine_room.append(ingredient_add_new_butt,'ingredient_add_new_butt')
		ingredient_add_new_butt.onclick.connect(lambda e: self.add_new_grist())

		adjust_weight_ing_lbl = gui.Label('Adjust Weight')
		adjust_weight_ing_lbl.attributes.update({"class":"Label","editor_constructor":"('Adjust Weight')","editor_varname":"adjust_weight_ing_lbl","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
		adjust_weight_ing_lbl.style.update({"margin":"0px","width":"91px","height":"14px","top":"80px","left":"480px","position":"absolute","overflow":"false","font-size":"12px"})
		engine_room.append(adjust_weight_ing_lbl,'adjust_weight_ing_lbl')

		add_1000g_ing_butt = gui.Button('+1Kg')
		add_1000g_ing_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"add_1000g_ing_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		add_1000g_ing_butt.style.update({"margin":"0px","width":"45px","height":"28px","top":"100px","left":"480px","position":"absolute","overflow":"auto"})
		engine_room.append(add_1000g_ing_butt,'add_1000g_ing_butt')
		add_1000g_ing_butt.onclick.connect(lambda e: self.add_weight_ingredients(1000))


		add_100g_ing_butt = gui.Button('+100g')
		add_100g_ing_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"add_100g_ing_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		add_100g_ing_butt.style.update({"margin":"0px","width":"45px","height":"28px","top":"130px","left":"480px","position":"absolute","overflow":"auto"})
		engine_room.append(add_100g_ing_butt,'add_100g_ing_butt')
		add_100g_ing_butt.onclick.connect(lambda e: self.add_weight_ingredients(100))

		rem_1000g_ing_butt = gui.Button('-1Kg')
		rem_1000g_ing_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"rem_1000g_ing_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		rem_1000g_ing_butt.style.update({"margin":"0px","width":"45px","height":"28px","top":"100px","left":"530px","position":"absolute","overflow":"auto"})
		engine_room.append(rem_1000g_ing_butt,'rem_1000g_ing_butt')
		rem_1000g_ing_butt.onclick.connect(lambda e: self.add_weight_ingredients(-1000))

		rem_100g_ing_butt = gui.Button('-100g')
		rem_100g_ing_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"rem_100g_ing_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		rem_100g_ing_butt.style.update({"margin":"0px","width":"45px","height":"28px","top":"130px","left":"530px","position":"absolute","overflow":"auto"})
		engine_room.append(rem_100g_ing_butt,'rem_100g_ing_butt')
		rem_100g_ing_butt.onclick.connect(lambda e: self.add_weight_ingredients(-100))

		add_10g_ing_butt = gui.Button('+10g')
		add_10g_ing_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"add_10g_ing_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		add_10g_ing_butt.style.update({"margin":"0px","width":"45px","height":"28px","top":"160px","left":"480px","position":"absolute","overflow":"auto"})
		engine_room.append(add_10g_ing_butt,'add_10g_ing_butt')
		add_10g_ing_butt.onclick.connect(lambda e: self.add_weight_ingredients(10))

		rem_10g_ing_butt = gui.Button('-10g')
		rem_10g_ing_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"rem_10g_ing_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		rem_10g_ing_butt.style.update({"margin":"0px","width":"45px","height":"28px","top":"160px","left":"530px","position":"absolute","overflow":"auto"})
		engine_room.append(rem_10g_ing_butt,'rem_10g_ing_butt')
		rem_10g_ing_butt.onclick.connect(lambda e: self.add_weight_ingredients(-10))

		add_1g_ing_butt = gui.Button('+1g')
		add_1g_ing_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"add_1g_ing_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		add_1g_ing_butt.style.update({"margin":"0px","width":"45px","height":"28px","top":"190px","left":"480px","position":"absolute","overflow":"auto"})
		engine_room.append(add_1g_ing_butt,'add_1g_ing_butt')
		add_1g_ing_butt.onclick.connect(lambda e: self.add_weight_ingredients(1))

		rem_1g_ing_butt = gui.Button('-1g')
		rem_1g_ing_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"rem_1g_ing_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		rem_1g_ing_butt.style.update({"margin":"0px","width":"45px","height":"28px","top":"190px","left":"530px","position":"absolute","overflow":"auto"})
		engine_room.append(rem_1g_ing_butt,'rem_1g_ing_butt')
		rem_1g_ing_butt.onclick.connect(lambda e: self.add_weight_ingredients(-1))

		original_gravity_lbl = gui.Label('Original Gravity')
		original_gravity_lbl.attributes.update({"class":"Label","editor_constructor":"('Recipe Name:')","editor_varname":"original_gravity_lbl","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
		original_gravity_lbl.style.update({"margin":"0px","width":"79px","height":"14px","top":"40px","left":"580px","position":"absolute","overflow":"false","font-size":"9px"})
		engine_room.append(original_gravity_lbl,'original_gravity_lbl')

		original_gravity_ent = gui.TextInput(True,'')
		original_gravity_ent.attributes.update({"class":"TextInput","autocomplete":"off","editor_constructor":"(False,'')","editor_varname":"original_gravity_ent","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
		original_gravity_ent.style.update({"margin":"0px","width":"46px","height":"20px","top":"60px","left":"590px","position":"absolute","overflow":"auto", "text-align": "center"})
		engine_room.append(original_gravity_ent,'original_gravity_ent')
		original_gravity_ent.set_value('1000.0')

		ingredient_zero_butt = gui.Button('Zero')
		ingredient_zero_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"ingredient_zero_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		ingredient_zero_butt.style.update({"margin":"0px","width":"59px","height":"22px","top":"100px","left":"590px","position":"absolute","overflow":"auto"})
		engine_room.append(ingredient_zero_butt,'ingredient_zero_butt')
		ingredient_zero_butt.onclick.connect(lambda e: self.zero_ingredients())

		recalc_butt = gui.Button('Recalculate')
		recalc_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"recalc_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		recalc_butt.style.update({"margin":"0px","width":"97px","height":"29px","top":"10px","left":"680px","position":"absolute","overflow":"auto"})
		engine_room.append(recalc_butt,'recalc_butt')
		recalc_butt.onclick.connect(lambda e: self.recalculate())

		calc_lbl = gui.TextInput(False, '')
		calc_lbl.attributes.update({"class":"TextInput","editor_constructor":"('Recipe Name:')","editor_varname":"calc_lbl","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
		calc_lbl.style.update({"margin":"0px","width":"103px","height":"150px","top":"50.88px","left":"666.4px","position":"absolute","overflow":"false","font-size":"11.5px", 'resize': 'none'})
		engine_room.append(calc_lbl,'calc_lbl')
		calc_lbl.set_enabled(False)
		default_text = '''Efficiency: {efficiency}%{enter}Final Gravity: {final_gravity}{enter}Alcohol (ABV): {abv}{enter}Colour: {colour}EBC{enter}Mash Liquor: {mash_liquor}L{enter}IBU:GU: {ibu_gu}'''.format(efficiency=brew_data.constants['Efficiency']*100, final_gravity=1.000, abv=0, colour=0, mash_liquor=0, ibu_gu=0, enter='\n\n')
		calc_lbl.set_value(default_text)

		hop_container = gui.Widget(width='460px', height='140px')
		hop_container.style.update({"margin":"0px","width":"520px", "top":"260px","left":"10px","position":"absolute","overflow":"auto"})
		engine_room.append(hop_container,'hop_container')

		self.table_hop = table_hop = customTable().new_from_list([('Hop Variety', "Type", "Alpha", "Time", "% Util", "IBU", "lb:oz", "Grams", "%")], width='520px', margin='10px')
		for c in table_hop.children.values():
			c.style['height'] = '30px'
		
		table_hop.style.update({"margin":"0px","width":"520px","top":"0px","left":"0px","position":"absolute","float":"none","display":"table","overflow":"true"})
		table_hop.attributes.update({"class":"TableWidget","editor_constructor":"(5,2,False,False)","editor_varname":"table_ingredient","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TableWidget"})
		hop_container.append(table_hop,'table_hop')
		

		hop_add_new_butt = gui.Button('Add New')
		hop_add_new_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"hop_add_new_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		hop_add_new_butt.style.update({"margin":"0px","width":"80px","height":"29px","top":"240px","left":"560px","position":"absolute","overflow":"auto"})
		engine_room.append(hop_add_new_butt,'hop_add_new_butt')
		hop_add_new_butt.onclick.connect(lambda e: self.add_new_hop())

		adjust_weight_hop_lbl = gui.Label('Adjust Weight')
		adjust_weight_hop_lbl.attributes.update({"class":"Label","editor_constructor":"('Recipe Name:')","editor_varname":"adjust_weight_hop_lbl","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
		adjust_weight_hop_lbl.style.update({"margin":"0px","width":"91px","height":"14px","top":"280px","left":"570px","position":"absolute","overflow":"false","font-size":"12px"})
		engine_room.append(adjust_weight_hop_lbl,'adjust_weight_hop_lbl')

		add_100g_hop_butt = gui.Button('+100g')
		add_100g_hop_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"add_100g_hop_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		add_100g_hop_butt.style.update({"margin":"0px","width":"45px","height":"28px","top":"300px","left":"570px","position":"absolute","overflow":"auto"})
		engine_room.append(add_100g_hop_butt,'add_100g_hop_butt')
		add_100g_hop_butt.onclick.connect(lambda e: self.add_weight_hops(100))

		rem_100g_hop_butt = gui.Button('-100g')
		rem_100g_hop_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"rem_100g_hop_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		rem_100g_hop_butt.style.update({"margin":"0px","width":"45px","height":"28px","top":"300px","left":"620px","position":"absolute","overflow":"auto"})
		engine_room.append(rem_100g_hop_butt,'rem_100g_hop_butt')
		rem_100g_hop_butt.onclick.connect(lambda e: self.add_weight_hops(-100))

		add_25g_hop_butt = gui.Button('+25g')
		add_25g_hop_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"add_25g_hop_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		add_25g_hop_butt.style.update({"margin":"0px","width":"45px","height":"28px","top":"330px","left":"570px","position":"absolute","overflow":"auto"})
		engine_room.append(add_25g_hop_butt,'add_25g_hop_butt')
		add_25g_hop_butt.onclick.connect(lambda e: self.add_weight_hops(25))

		rem_25g_hop_butt = gui.Button('-25g')
		rem_25g_hop_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"rem_25g_hop_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		rem_25g_hop_butt.style.update({"margin":"0px","width":"45px","height":"28px","top":"330px","left":"620px","position":"absolute","overflow":"auto"})
		engine_room.append(rem_25g_hop_butt,'rem_25g_hop_butt')
		rem_25g_hop_butt.onclick.connect(lambda e: self.add_weight_hops(-25))

		add_10g_hop_butt = gui.Button('+10g')
		add_10g_hop_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"add_10g_hop_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		add_10g_hop_butt.style.update({"margin":"0px","width":"45px","height":"28px","top":"360px","left":"570px","position":"absolute","overflow":"auto"})
		engine_room.append(add_10g_hop_butt,'add_10g_hop_butt')
		add_10g_hop_butt.onclick.connect(lambda e: self.add_weight_hops(10))

		rem_10g_hop_butt = gui.Button('-10g')
		rem_10g_hop_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"rem_10g_hop_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		rem_10g_hop_butt.style.update({"margin":"0px","width":"45px","height":"28px","top":"360px","left":"620px","position":"absolute","overflow":"auto"})
		engine_room.append(rem_10g_hop_butt,'rem_10g_hop_butt')
		rem_10g_hop_butt.onclick.connect(lambda e: self.add_weight_hops(-10))

		add_1g_hop_butt = gui.Button('+1g')
		add_1g_hop_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"add_1g_hop_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		add_1g_hop_butt.style.update({"margin":"0px","width":"45px","height":"28px","top":"390px","left":"570px","position":"absolute","overflow":"auto"})
		engine_room.append(add_1g_hop_butt,'add_1g_hop_butt')
		add_1g_hop_butt.onclick.connect(lambda e: self.add_weight_hops(1))

		rem_1g_hop_butt = gui.Button('-1g')
		rem_1g_hop_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"rem_1g_hop_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		rem_1g_hop_butt.style.update({"margin":"0px","width":"45px","height":"28px","top":"390px","left":"620px","position":"absolute","overflow":"auto"})
		engine_room.append(rem_1g_hop_butt,'rem_1g_hop_butt')
		rem_1g_hop_butt.onclick.connect(lambda e: self.add_weight_hops(-1))

		hop_zero_butt = gui.Button('Zero')
		hop_zero_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"hop_zero_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		hop_zero_butt.style.update({"margin":"0px","width":"55px","height":"28px","top":"300px","left":"680px","position":"absolute","overflow":"auto"})
		engine_room.append(hop_zero_butt,'hop_zero_butt')
		hop_zero_butt.onclick.connect(lambda e: self.zero_hops())

		bitterness_ebu_lbl = gui.Label('Bitterness IBU')
		bitterness_ebu_lbl.attributes.update({"class":"Label","editor_constructor":"('Recipe Name:')","editor_varname":"bitterness_ebu_lbl","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Label"})
		bitterness_ebu_lbl.style.update({"margin":"0px","width":"79px","height":"14px","top":"240px","left":"670px","position":"absolute","overflow":"false","font-size":"12px"})
		engine_room.append(bitterness_ebu_lbl,'bitterness_ebu_lbl')

		bitterness_ibu_ent = gui.TextInput(True,'')
		bitterness_ibu_ent.attributes.update({"class":"TextInput","autocomplete":"off","editor_constructor":"(False,'')","editor_varname":"bitterness_ibu_ent","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"TextInput"})
		bitterness_ibu_ent.style.update({"margin":"0px","width":"46px","height":"20px","top":"260px","left":"680px","position":"absolute","overflow":"auto", "text-align": "center"})
		engine_room.append(bitterness_ibu_ent,'bitterness_ibu_ent')
		bitterness_ibu_ent.set_value('0')

		hop_rem_butt = gui.Button('Remove')
		hop_rem_butt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"hop_rem_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		hop_rem_butt.style.update({"margin":"0px","width":"76px","height":"28px","top":"390px","left":"10px","position":"absolute","overflow":"auto"})
		engine_room.append(hop_rem_butt,'hop_rem_butt')
		hop_rem_butt.onclick.connect(lambda e: self.delete_hop())

		add_time_butt_plus1 = gui.Button('Time +1')
		add_time_butt_plus1.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"add_time_butt_plus1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		add_time_butt_plus1.style.update({"margin":"0px","width":"78px","height":"29px","top":"390px","left":"330px","position":"absolute","overflow":"auto"})
		engine_room.append(add_time_butt_plus1,'add_time_butt_plus1')
		add_time_butt_plus1.onclick.connect(lambda e: self.add_time(1))

		rem_time_butt_min_1 = gui.Button('Time -1')
		rem_time_butt_min_1.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"rem_time_butt_min_1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		rem_time_butt_min_1.style.update({"margin":"0px","width":"78px","height":"29px","top":"420px","left":"330px","position":"absolute","overflow":"auto"})
		engine_room.append(rem_time_butt_min_1,'rem_time_butt_min_1')
		rem_time_butt_min_1.onclick.connect(lambda e: self.add_time(-1))

		add_time_butt_plus5 = gui.Button('Time +5')
		add_time_butt_plus5.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"add_time_butt_plus5","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		add_time_butt_plus5.style.update({"margin":"0px","width":"78px","height":"29px","top":"390px","left":"250px","position":"absolute","overflow":"auto"})
		engine_room.append(add_time_butt_plus5,'add_time_butt_plus5')
		add_time_butt_plus5.onclick.connect(lambda e: self.add_time(5))

		rem_time_butt_min_5 = gui.Button('Time -5')
		rem_time_butt_min_5.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"rem_time_butt_min_5","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		rem_time_butt_min_5.style.update({"margin":"0px","width":"78px","height":"29px","top":"420px","left":"250px","position":"absolute","overflow":"auto"})
		engine_room.append(rem_time_butt_min_5,'rem_time_butt_min_5')
		rem_time_butt_min_5.onclick.connect(lambda e: self.add_time(-5))

		add_alpha_butt_plus_pt1 = gui.Button('Alpha +0.1')
		add_alpha_butt_plus_pt1.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"add_alpha_butt_plus_pt1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		add_alpha_butt_plus_pt1.style.update({"margin":"0px","width":"78px","height":"29px","top":"390px","left":"90px","position":"absolute","overflow":"auto"})
		engine_room.append(add_alpha_butt_plus_pt1,'add_alpha_butt_plus_pt1')
		add_alpha_butt_plus_pt1.onclick.connect(lambda e: self.add_alpha(0.1))
		
		add_alpha_butt_rem_pt1 = gui.Button('Alpha -0.1')
		add_alpha_butt_rem_pt1.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"add_alpha_butt_rem_pt1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		add_alpha_butt_rem_pt1.style.update({"margin":"0px","width":"78px","height":"29px","top":"420px","left":"90px","position":"absolute","overflow":"auto"})
		engine_room.append(add_alpha_butt_rem_pt1,'add_alpha_butt_rem_pt1')
		add_alpha_butt_rem_pt1.onclick.connect(lambda e: self.add_alpha(-0.1))

		add_alpha_butt_plus_1 = gui.Button('Alpha +1')
		add_alpha_butt_plus_1.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"add_alpha_butt_plus_1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		add_alpha_butt_plus_1.style.update({"margin":"0px","width":"76px","height":"29px","top":"390px","left":"170px","position":"absolute","overflow":"auto"})
		engine_room.append(add_alpha_butt_plus_1,'add_alpha_butt_plus_1')
		add_alpha_butt_plus_1.onclick.connect(lambda e: self.add_alpha(1))

		add_alpha_butt_min_1 = gui.Button('Alpha -1')
		add_alpha_butt_min_1.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"add_alpha_butt_min_1","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		add_alpha_butt_min_1.style.update({"margin":"0px","width":"76px","height":"29px","top":"420px","left":"170px","position":"absolute","overflow":"auto"})
		engine_room.append(add_alpha_butt_min_1,'add_alpha_butt_min_1')
		add_alpha_butt_min_1.onclick.connect(lambda e: self.add_alpha(-1))

		quit_btt = gui.Button('Quit')
		quit_btt.attributes.update({"class":"Button","editor_constructor":"('button_text')","editor_varname":"quit_btt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"Button"})
		quit_btt.style.update({"margin":"0px","width":"0px","height":"0px","top":"440px","left":"730px","position":"absolute","overflow":"auto"})
		engine_room.append(quit_btt,'quit_btt')

		
		# ingredients_imperial_chk_butt gui.CheckBoxLabel('Imperial Units', False,'')
		# ingredients_imperial_chk_butt.attributes.update({"class":"CheckBoxLabel","editor_constructor":"('text',True,'')","editor_varname":"ingredients_imperial_chk_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"CheckBoxLabel"})
		# ingredients_imperial_chk_butt.style.update({"margin":"0px","width":"150px","height":"35.2px","top":"190px","left":"320px","position":"absolute","overflow":"false","font-size":"12px"})
		# engine_room.append(ingredients_imperial_chk_butt,'ingredients_imperial_chk_butt')

		# hops_imperial_chk_butt gui.CheckBoxLabel('Imperial Units', False,'')
		# hops_imperial_chk_butt.attributes.update({"class":"CheckBoxLabel","editor_constructor":"('text',True,'')","editor_varname":"hops_imperial_chk_butt","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"CheckBoxLabel"})
		# hops_imperial_chk_butt.style.update({"margin":"0px","width":"150px","height":"35.2px","top":"390px","left":"420px","position":"absolute","overflow":"false","font-size":"12px"})
		# engine_room.append(hops_imperial_chk_butt,'hops_imperial_chk_butt')

		ogfixed_chkbutton = gui.CheckBox(False,'')
		ogfixed_chkbutton.attributes.update({"class":"CheckBoxLabel","editor_constructor":"('text',True,'')","editor_varname":"ogfixed_chkbutton","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"CheckBoxLabel"})
		ogfixed_chkbutton.style.update({"margin":"0px","width":"21.12px","height":"26.4px","top":"60px","left":"570px","position":"absolute","overflow":"auto"})
		engine_room.append(ogfixed_chkbutton,'ogfixed_chkbutton')
		ogfixed_chkbutton.onclick.connect(lambda *args: self.og_fixed())

		ibufixed_chkbutton = gui.CheckBox(False,'')
		ibufixed_chkbutton.attributes.update({"class":"CheckBoxLabel","editor_constructor":"('text',True,'')","editor_varname":"ibufixed_chkbutton","editor_tag_type":"widget","editor_newclass":"False","editor_baseclass":"CheckBoxLabel"})
		ibufixed_chkbutton.style.update({"margin":"0px","width":"26px","height":"21px","top":"260px","left":"650px","position":"absolute","overflow":"auto"})
		engine_room.append(ibufixed_chkbutton,'ibufixed_chkbutton')
		ibufixed_chkbutton.onclick.connect(lambda *args: self.ibu_fixed())

		# print(engine_room.children)

		self.engine_room = engine_room
		return self.mainContainer
	
	def open_file(self, file):
		if file != '' and file != None and type(file) != tuple:
			is_ogfixed = 0
			is_ibufixed = 0
			self.ingredients = []
			self.hops = []
			if file.lower()[-5:] == '.berf':
				self.current_file = file
				with open(file, 'rb') as f:
					data = [line.replace(b'\xa7', b'\t').strip().decode('ISO-8859-1').split('\t') for line in f]
					for sublist in data:
						if sublist[0] == 'grain':
							grams = float(sublist[7])
							lb = grams/brew_data.constants['Conversion']['lb-g']
							oz = (lb-int(lb))*16
							percent = float(sublist[8])
							EBC = float(sublist[2])
							self.ingredients.append({'Name': sublist[1], 'Values': {'EBC': EBC, 'Grav': 0, 'lb:oz': (lb,oz), 'Grams': grams, 'Percent': percent}})
						elif sublist[0] == 'hop':
							alpha = float(sublist[3])
							grams = float(sublist[5])
							lb = grams/brew_data.constants['Conversion']['lb-g']
							oz = (lb-int(lb))*16
							time = float(sublist[6])
							percent = float(sublist[7])
							self.hops.append({'Name': sublist[1], 'Values': {'Type': sublist[2], 'Alpha': alpha, 'Time': time, 'Util': 0.0, 'ibu': 0.0, 'lb:oz': (lb,oz), 'Grams': grams, 'Percent': percent}})
						elif sublist[1] == 'recipename':
							self.engine_room.children['recipe_name_ent'].set_value(sublist[2])
						elif sublist[1] == 'volume':
							self.engine_room.children['volume_ent'].set_value(sublist[2])
							if not any(e[1] == 'boilvol' for e in data):
								self.engine_room.children['boil_volume_ent'].set_value(str(round(float(sublist[2])*brew_data.constants['Boil Volume Scale'], 2)))
						elif sublist[1] == 'boilvol':
							self.engine_room.children['boil_volume_ent'].set_value(str(round(float(sublist[2]), 2)))
						elif sublist[1] == 'efficiency':
							brew_data.constants['Efficiency'] = float(sublist[2])/100
						elif sublist[0] == 'miscel':
							if sublist[1] == 'ogfixed':
								is_ogfixed = sublist[2]
							elif sublist[1] == 'ibufixed':
								is_ibufixed = sublist[2]
					
		
		elif file.lower()[-6:] == '.berfx':
				self.current_file = file
				with open(file, 'r') as f:
					#data = [line.replace(b'\xa7', b'\t').strip().decode().split('\t') for line in f]
					data = [
						line.replace(
							'\xa7',
							'\t').strip().split('\t') for line in f]
					for sublist in data:
						if sublist[0] == 'grain':
							self.ingredients.append(
								{'Name': sublist[1], 'Values': ast.literal_eval(sublist[2])})
						elif sublist[0] == 'hop':
							self.hops.append(
								{'Name': sublist[1], 'Values': ast.literal_eval(sublist[2])})
						elif sublist[0] == 'add':
							name = sublist[1]
							dictionary = ast.literal_eval(sublist[2])

							if 'Lab' in dictionary:
								brew_data.yeast_data[name] = dictionary
							else:
								brew_data.water_chemistry_additions[name] = dictionary

						elif sublist[0] == 'database':
							if sublist[1] == 'grist':
								brew_data.grist_data[sublist[2]] = ast.literal_eval(
									sublist[3])
							elif sublist[1] == 'hop':
								brew_data.hop_data[sublist[2]] = ast.literal_eval(
									sublist[3])
							elif sublist[1] == 'yeast':
								brew_data.yeast_data[sublist[2]] = ast.literal_eval(
									sublist[3])
							elif sublist[1] == 'water_chem':
								brew_data.water_chemistry_additions[sublist[2]] = ast.literal_eval(
									sublist[3])
							elif sublist[1] == 'constant':
								for constant, value in ast.literal_eval(
										sublist[2]).items():
									brew_data.constants[constant] = value
						elif sublist[0] == 'miscel':
							if sublist[1] == 'ogfixed':
								is_ogfixed = sublist[2]
							elif sublist[1] == 'ebufixed':
								is_ibufixed = sublist[2]
							elif sublist[1] == 'recipename':
								self.recipe_name_ent.set_value(sublist[2])
							elif sublist[1] == 'notes':
								#notes += bytes(sublist[2],encoding='utf8')
								notes = sublist[2]
		self.refresh_tables()
		self.refresh_grist()
		self.refresh_hop()
		self.recalculate()
		
	def refresh_tables(self):
		for c in list(self.table_ingredient.children.values()):
			self.table_ingredient.remove_child(c)
		# print(self.ingredients)
		self.table_ingredient.append_from_list([('Fermentable Ingredients', "Ebc", "Grav", "lb:oz", "Grams", "%")]+[[ingredient['Name'], str(ingredient['Values']['EBC']), str(round(ingredient['Values']['Grav'], 1)), ':'.join(str(round(v, 1)) for v in ingredient['Values']['lb:oz']), str(ingredient['Values']['Grams']), str(ingredient['Values']['Percent'])] for ingredient in self.ingredients], fill_title=True)
		for c in self.table_ingredient.children.values():
			c.style['height'] = '30px'
	
		for c in list(self.table_hop.children.values()):
			self.table_hop.remove_child(c)
		# print(self.hops)
		self.table_hop.append_from_list([('Hop Variety', "Type", "Alpha", "Time", "% Util", "IBU", "lb:oz", "Grams", "%")]+[[hop['Name'], hop['Values']['Type'], str(hop['Values']['Alpha']), str(hop['Values']['Time']), str(round(hop['Values']['Util'], 1)), str(round(hop['Values']['ibu'])), ':'.join(str(round(v, 1)) for v in hop['Values']['lb:oz']), str(hop['Values']['Grams']), str(hop['Values']['Percent'])] for hop in self.hops], fill_title=True)
		for c in self.table_hop.children.values():
			c.style['height'] = '30px'

	def refresh_grist(self):
		def refresh_percentage():
			total_weight = sum([ingredient['Values']['Grams'] for ingredient in self.ingredients])
			if total_weight > 0:
				for ingredient in self.ingredients:
					weight = ingredient['Values']['Grams']
					percentage = round((weight/total_weight)*100, 1)
					ingredient['Values']['Percent'] = percentage

		def refresh_orig_grav():
			non_mashables = [6.0, 5.0]
			volume = float(self.engine_room.children['volume_ent'].get_value())
			points = sum([(brew_data.grist_data[ingredient['Name']]['Extract']*(ingredient['Values']['Grams'])/1000) * (1 if brew_data.grist_data[ingredient['Name']]['Type'] in non_mashables else brew_data.constants['Efficiency']) for ingredient in self.ingredients])

			orig_grav = ((points)/volume)+1000
			self.og = orig_grav
			self.engine_room.children['original_gravity_ent'].set_value(str(round(orig_grav, 1)))

		def refresh_indiv_grav():
			non_mashables = [6.0, 5.0]
			volume = float(self.engine_room.children['volume_ent'].get_value())
			for ingredient in self.ingredients:
				points = brew_data.grist_data[ingredient['Name']]['Extract']*(ingredient['Values']['Grams'])/1000
				eff = (1 if brew_data.grist_data[ingredient['Name']]['Type'] in non_mashables else brew_data.constants['Efficiency'])
				grav = ((points * eff)/volume)
				ingredient['Values']['Grav'] = grav

		print(self.engine_room.children['ogfixed_chkbutton'].get_value())
		if not self.engine_room.children['ogfixed_chkbutton'].get_value():
			refresh_orig_grav()
			refresh_percentage()
		else:
			non_mashables = [6.0, 5.0]
			factor = sum([ingredient['Values']['Percent']*brew_data.grist_data[ingredient['Name']]['Extract']*(1 if brew_data.grist_data[ingredient['Name']]['Type'] in non_mashables else brew_data.constants['Efficiency']) for idx, ingredient in enumerate(self.ingredients)])

			for idx, ingredient in enumerate(self.ingredients):
				EBC = int(brew_data.grist_data[ingredient['Name']]['EBC'])
				percent = ingredient['Values']['Percent']
				orig_grav = float(self.engine_room.children['original_gravity_ent'].get_value())-1000
				self.og = orig_grav + 1000
				vol = float(self.engine_room.children['volume_ent'].get_value())
				try:
					weight = percent*((orig_grav*vol)/factor)*1000
				except:
					weight = 0
				lb = weight/brew_data.constants['Conversion']['lb-g']
				oz = (lb-int(lb))*16
				self.ingredients[idx] = {'Name': ingredient['Name'], 'Values': {'EBC': EBC, 'Grav': 0.0, 'lb:oz': (lb,oz), 'Grams': weight, 'Percent': percent}}
			refresh_percentage()
		refresh_indiv_grav()
		self.refresh_tables()

	def refresh_hop(self):
		def refresh_percentage():
			total_weight = sum([hop['Values']['Grams'] for hop in self.hops])
			if total_weight > 0:
				for hop in self.hops:
					weight = hop['Values']['Grams']
					percentage = round((weight/total_weight)*100, 1)
					hop['Values']['Percent'] = percentage

		def refresh_util():
			def boil_grav():
				volume = float(self.engine_room.children['boil_volume_ent'].get_value())
				points = sum([brew_data.grist_data[ingredient['Name']]['Extract']*(ingredient['Values']['Grams'])/1000 for ingredient in self.ingredients])
				boil_grav = ((points * brew_data.constants['Efficiency'])/volume)+1000
				return boil_grav
			'''
			Utilization = f(G) x f(T)
			f(G) = 1.65 x 0.000125^(Gb - 1)
			f(T) = [1 - e^(-0.04 x T)] / 4.15
			Where Gb is boil gravity and T is time
			'''
			for hop in self.hops:
				boil_gravity = boil_grav()/1000 # Temporary Solution
				time = hop['Values']['Time']
				fG = 1.65 * (0.000125**(boil_gravity - 1))
				fT = (1 - math.e**(-0.04 * time)) / 4.15
				hop['Values']['Util'] = (fG * fT)*100

		def refresh_ibu():
			'''
			IBU    =    grams x alpha acid x utilisation rate
				   -------------------------------------------------
									 Volume x 10
			'''
			ibu = sum([(hop['Values']['Grams'] * hop['Values']['Alpha'] * hop['Values']['Util']) / (float(self.engine_room.children['boil_volume_ent'].get_value())*10)  for hop in self.hops])
			ibu = (ibu*float(self.engine_room.children['boil_volume_ent'].get_value()))/float(self.engine_room.children['volume_ent'].get_value())
			self.ibu = ibu
			self.engine_room.children['bitterness_ibu_ent'].set_value(str(round(ibu)))

		def refresh_indiv_ibu():
			for hop in self.hops:
				ibu = (hop['Values']['Grams'] * hop['Values']['Alpha'] * hop['Values']['Util']) / (float(self.engine_room.children['boil_volume_ent'].get_value())*10)
				hop['Values']['ibu'] = ibu

		if not self.engine_room.children['ibufixed_chkbutton'].get_value():
			refresh_percentage()
			refresh_ibu()
		else:
			factor = sum([hop['Values']['Percent']*hop['Values']['Alpha']*hop['Values']['Util'] for idx, hop in enumerate(self.hops)])

			for idx, hop in enumerate(self.hops):
				percent = hop['Values']['Percent']

				alpha =  hop['Values']['Alpha']
				type = brew_data.hop_data[hop['Name']]['Form']
				util = hop['Values']['Util']
				time = hop['Values']['Time']
				if util > 0 and alpha > 0:
					self.ibu = total_ibus = float(self.engine_room.children['bitterness_ibu_ent'].get_value())
					vol = float(self.engine_room.children['volume_ent'].get_value())
					try:
						weight = percent*((total_ibus*vol*10)/factor) #(((total_ibus*(percent/100))*(vol*10))/util)/alpha
					except:
						weight = 0
					lb = weight/brew_data.constants['Conversion']['lb-g']
					oz = (lb-int(lb))*16
					self.hops[idx] = {'Name': hop['Name'], 'Values': {'Type': type, 'Alpha': alpha, 'Time': time, 'Util': 0.0, 'ibu': 0.0, 'lb:oz': (lb, oz), 'Grams': weight, 'Percent': percent}}
			refresh_percentage()
		refresh_util()
		refresh_indiv_ibu()
		self.refresh_tables()

	def recalculate(self):
		def final_gravity():
			non_mashables = [6.0, 5.0]
			a = sum([(((62 if int(brew_data.grist_data[ingredient['Name']]['Fermentability']) == 200 else brew_data.grist_data[ingredient['Name']]['Fermentability'])/100)*((ingredient['Values']['Grams']/1000) * brew_data.grist_data[ingredient['Name']]['Extract'])) * (1 if brew_data.grist_data[ingredient['Name']]['Type'] in non_mashables else brew_data.constants['Efficiency']) for ingredient in self.ingredients])
			b = sum([(((100 - (62 if int(brew_data.grist_data[ingredient['Name']]['Fermentability']) == 200 else brew_data.grist_data[ingredient['Name']]['Fermentability']))/100)*((ingredient['Values']['Grams']/1000) * brew_data.grist_data[ingredient['Name']]['Extract'])) * (1 if brew_data.grist_data[ingredient['Name']]['Type'] in non_mashables else brew_data.constants['Efficiency']) for ingredient in self.ingredients])
			return ((b-(a*0.225))/float(self.engine_room.children['volume_ent'].get_value()))+1000
		def alcohol_by_volume(og, fg):
			#return (1.05/0.79) * ((og - fg) / fg) *100
			return (((1.05*(og-fg))/fg/0.79))*100
		def mash_liquor():
			non_mashables = [6.0, 5.0] # ["Copper Sugar", "Malt Extract"]
			grist_mass = sum([0 if brew_data.grist_data[ingredient['Name']]['Type'] in non_mashables else ingredient['Values']['Grams'] for ingredient in self.ingredients])/1000
			return grist_mass*brew_data.constants['Liquor To Grist Ratio']
		def colour_ebc():
			# [{'Name:': 'Wheat Flour', 'Values': {'EBC:': 0.0, 'Grav': 0.0, 'lb:oz': (0.0,0.0), 'Grams': 0.0, 'Percent': 0.0}}]
			def formula(ingredient, efficiency):
				ebc = ingredient['Values']['EBC']
				mass = ingredient['Values']['Grams']/1000
				volume = float(self.engine_room.children['volume_ent'].get_value())
				return (ebc*mass*efficiency*10)/volume

			non_mashables = [6.0, 5.0] # Not effected by efficiency  ["Copper Sugar", "Malt Extract"]
			return (sum([formula(ingredient, 1) if brew_data.grist_data[ingredient['Name']]['Type'] in non_mashables else formula(ingredient, brew_data.constants['Efficiency']) for ingredient in self.ingredients]))

		'''
		MCU = color rating of the malt °L × weight(lb)
			°SRM = MCU 					(Traditional)
			°SRM = 0.3 × MCU + 4.7		(Mosher)
			°SRM = 0.2 × MCU + 8.4		(Daniels)
			°SRM = 1.49 × MCU ^ 0.69	(Morey)
		'''
		#self.colour = 1.49 * (sum([((ingredient['Values']['EBC']*1.84)*(ingredient['Values']['lb:oz'][0] + (ingredient['Values']['lb:oz'][1]/16)))/(float(self.volume.get())/brew_data.constants['Conversion']['usg-l']) for ingredient in self.ingredients]) ** 0.69) # Morey's Formula
		self.refresh_grist()
		self.refresh_hop()
		self.colour = colour_ebc()
		self.fg = final_gravity()
		self.og = float(self.og)
		print(self.og)
		self.abv = alcohol_by_volume(self.og/1000, self.fg/1000)
		self.ibu_gu = float(self.ibu) / (self.og - 1000) if (self.og - 1000) != 0 else 0
		self.engine_room.children['calc_lbl'].set_value('''Efficiency: {efficiency}%{enter}Final Gravity: {final_gravity}{enter}Alcohol (ABV): {abv}{enter}Colour: {colour}EBC{enter}Mash Liquor: {mash_liquor}L{enter}IBU:GU: {ibu_gu}'''.format(
			efficiency=round(brew_data.constants['Efficiency']*100, 13), final_gravity=round(self.fg, 1),
			abv=round(self.abv, 1), colour=round(self.colour,1), mash_liquor=round(mash_liquor(),1),
			ibu_gu=round(self.ibu_gu, 2), enter='\n\n'))

	def add_weight_ingredients(self, weight): # Selected Item
		try:
			id = int([child[0] for child in self.table_ingredient.children.items() if child[1] == self.table_ingredient.last_clicked_row][0])
			grams = self.ingredients[id-1]['Values']['Grams']+weight
			if grams < 0: grams=0
			lb = grams/brew_data.constants['Conversion']['lb-g']
			oz = (lb-int(lb))*16
			self.ingredients[id-1]['Values']['Grams'] = grams
			self.ingredients[id-1]['Values']['lb:oz'] = (lb, oz)
			self.refresh_all()
			try:
				self.table_ingredient.on_table_row_click(self.table_ingredient.children['%s' % id], 'item')
			except Exception as e:
				print(e)

		except Exception as e:
			print(e)

	def add_weight_hops(self, weight): # Selected Item
		try:
			id = int([child[0] for child in self.table_hop.children.items() if child[1] == self.table_hop.last_clicked_row][0])
			grams = self.hops[id-1]['Values']['Grams']+weight
			if grams < 0: grams=0
			lb = grams/brew_data.constants['Conversion']['lb-g']
			oz = (lb-int(lb))*16
			self.hops[id-1]['Values']['Grams'] = grams
			self.hops[id-1]['Values']['lb:oz'] = (lb, oz)
			self.refresh_all()
			try:
				self.table_hop.on_table_row_click(self.table_hop.children['%s' % id], 'item')
			except Exception as e:
				print(e)
		except IndexError:
			pass

	def add_percent_ingredients(self, amount):
		''' Add a Percentage amount of Ingredients '''
		try:
			id = int([child[0] for child in self.table_ingredient.children.items() if child[1] == self.table_ingredient.last_clicked_row][0])
			percent = self.ingredients[id - 1]['Values']['Percent'] + amount
			if percent < 0:
				percent = 0
			self.ingredients[id - 1]['Values']['Percent'] = percent
			self.refresh_all()
			try:
				self.table_ingredient.on_table_row_click(self.table_ingredient.children['%s' % id], 'item')
			except Exception as e:
				print(e)
		except IndexError:
			pass
	
	def add_percent_hops(self, amount):
		try:
			id = int([child[0] for child in self.table_hop.children.items() if child[1] == self.table_hop.last_clicked_row][0])
			percent = self.hops[id - 1]['Values']['Percent'] + amount
			if percent < 0:
				percent = 0
			self.hops[id - 1]['Values']['Percent'] = percent
			self.refresh_all()
			try:
				self.table_hop.on_table_row_click(self.table_hop.children['%s' % id], 'item')
			except Exception as e:
				print(e)
		except IndexError:
			pass

	def delete_ingredient(self):
		try:
			id = int([child[0] for child in self.table_ingredient.children.items() if child[1] == self.table_ingredient.last_clicked_row][0])
			del self.ingredients[id-1]
			self.refresh_all()
		except Exception as e:
			pass

	def delete_hop(self):
		try:
			id = int([child[0] for child in self.table_hop.children.items() if child[1] == self.table_hop.last_clicked_row][0])
			del self.hops[id-1]
			self.refresh_all()
			
		except Exception as e:
			pass

	def zero_ingredients(self, curr_selection=None):
		try:
			if curr_selection is None:
				id = int([child[0] for child in self.table_ingredient.children.items() if child[1] == self.table_ingredient.last_clicked_row][0])
			else:
				id = curr_selection
			EBC = int(brew_data.grist_data[self.ingredients[id-1]['Name']]['EBC'])
			self.ingredients[id-1] = {'Name': self.ingredients[id-1]['Name'], 'Values': {'EBC': EBC, 'Grav': 0.0, 'lb:oz': (0.0,0.0), 'Grams': 0, 'Percent': 0.0}}
			self.refresh_all()
			try:
				self.table_ingredient.on_table_row_click(self.table_ingredient.children['%s' % id], 'item')
			except Exception as e:
				print(e)

		except Exception as e:
			pass

	def zero_hops(self):
		try:
			id = int([child[0] for child in self.table_hop.children.items() if child[1] == self.table_hop.last_clicked_row][0])
			alpha =  brew_data.hop_data[self.hops[id-1]['Name']]['Alpha']
			type = brew_data.hop_data[self.hops[id-1]['Name']]['Form']
			self.hops[id-1] = {'Name': self.hops[id-1]['Name'], 'Values': {'Type': type, 'Alpha': alpha, 'Time': 0.0, 'Util': 0.0, 'ibu': 0.0, 'lb:oz': (0.0,0.0), 'Grams': 0, 'Percent': 0.0}}
			self.refresh_all()
			try:
				self.table_hop.on_table_row_click(self.table_hop.children['%s' % id], 'item')
			except Exception as e:
				print(e)
		except Exception as e:
			pass

	def add_time(self, time):
		try:
			id = int([child[0] for child in self.table_hop.children.items() if child[1] == self.table_hop.last_clicked_row][0])
			time = round(self.hops[id-1]['Values']['Time']+time,1)
			if time < 0: time = 0
			self.hops[id-1]['Values']['Time'] = time
			self.refresh_all()
			try:
				self.table_hop.on_table_row_click(self.table_hop.children['%s' % id], 'item')
			except Exception as e:
				print(e)
		except IndexError:
			pass
	def add_alpha(self, alpha):
		try:
			id = int([child[0] for child in self.table_hop.children.items() if child[1] == self.table_hop.last_clicked_row][0])
			alpha = round(self.hops[id-1]['Values']['Alpha']+alpha, 1)
			if alpha < 0: alpha = 0
			self.hops[id-1]['Values']['Alpha'] = alpha
			self.refresh_all()
			try:
				self.table_hop.on_table_row_click(self.table_hop.children['%s' % id], 'item')
			except Exception as e:
				print(e)
		except IndexError:
			pass

	def add_new_grist(self):
		self.add_new_dialog = AddNewDialog(list(brew_data.grist_data.keys()))
		
		self.add_new_dialog.confirm_value.do(
			self.add_grist_confirm)

		self.add_new_dialog.show(self)

	def add_grist_confirm(self, widget, value):
		data = brew_data.grist_data[value]
		self.ingredients.append({'Name': value, 'Values': {'EBC': data['EBC'], 'Grav': 0, 'lb:oz': (0,0), 'Grams': 0, 'Percent': 0}})
		self.refresh_all()

	def add_new_hop(self):
		self.add_new_dialog = AddNewDialog(list(sorted(brew_data.hop_data.keys())))
		
		self.add_new_dialog.confirm_value.do(
			self.add_hop_confirm)

		self.add_new_dialog.show(self)

	def add_hop_confirm(self, widget, value):
		data = brew_data.hop_data[value]
		self.hops.append({'Name': value, 'Values': {'Type': data['Form'], 'Alpha': data['Alpha'], 'Time': 60, 'Util': 0.0, 'ibu': 0.0, 'lb:oz': (0, 0), 'Grams': 0, 'Percent': 0}})
		self.refresh_all()

	def refresh_all(self):
		self.recalculate()
		self.refresh_grist()
		self.refresh_hop()
		self.refresh_tables()
		self.recalculate()


	def fileupload_on_success(self, widget, filename):
		#self.lbl.set_text('File upload success: ' + filename)
		self.open_file('./recipes/{filename}'.format(filename=filename))
		print(filename)

	def fileupload_on_failed(self, widget, filename):
		#self.lbl.set_text('File upload failed: ' + filename)
		print(filename)

	def download(self):
		filename = '%s_%s.berfx' % (self.engine_room.children['recipe_name_ent'].get_value() ,len([f for f in os.listdir('./recipes') if self.engine_room.children['recipe_name_ent'].get_value() in f]))
		with open(f'./recipes/{filename}', 'w') as f:
			for ingredient in self.ingredients:
				f.write('grain\xa7{name}\t{data}\n'.format(name=ingredient['Name'], data=ingredient['Values']))
			for hop in self.hops:
				# 'Values': {'Type': 'Whole', 'Alpha': 12.7, 'Time': 0.0, 'Util': 0.0, 'ibu': 0.0, 'lb:oz': (0.0,0.0), 'Grams': 0.0, 'Percent': 0.0}
				f.write('hop\xa7{name}\t{data}\n'.format(name=hop['Name'], data=hop['Values']))
			# for addition in self.sixth_tab.added_additions:
			# 	all_chem = dict(brew_data.water_chemistry_additions)
			# 	all_chem.update(brew_data.yeast_data)
			# 	name = addition
			# 	addition_type = all_chem[name]
			# 	f.write('add\xa7{name}\t{type}\n'.format(name=name, type=addition_type))

			f.write('miscel\xa7ogfixed\t{ogfixed}\n'.format(ogfixed=0)) # self.is_ogfixed.get()))
			f.write('miscel\xa7ebufixed\t{ibufixed}\n'.format(ibufixed=0)) # self.is_ibufixed.get()))
			f.write('miscel\xa7recipename\t{recipename}\n'.format(recipename=self.engine_room.children['recipe_name_ent'].get_value()))
			f.write('default\xa7boilvol\t{boilvol}\n'.format(boilvol=self.engine_room.children['boil_volume_ent'].get_value())) 

			# notes = repr(self.seventh_tab.texpert.get('1.0', 'end'))
			# f.write('miscel\xa7notes\t{notes}\n'.format(notes=notes[1:-1]))

			for key, grist in brew_data.grist_data.items(): f.write('database\xa7grist\xa7{name}\t{data}\n'.format(name=key, data=grist))
			for key, hop in brew_data.hop_data.items(): f.write('database\xa7hop\xa7{name}\t{data}\n'.format(name=key, data=hop))
			for key, yeast in brew_data.yeast_data.items(): f.write('database\xa7yeast\xa7{name}\t{data}\n'.format(name=key, data=yeast))
			for key, water_chem in brew_data.water_chemistry_additions.items(): f.write('database\xa7water_chem\xa7{name}\t{data}\n'.format(name=key, data=water_chem))
			for key, constant in brew_data.constants.items(): f.write('database\xa7constant\xa7{name}\t{data}\n'.format(name=key, data=constant))
			f.write('database\xa7constant\xa7{constants}'.format(constants=brew_data.constants))

		self.fexporter.attributes['download'] = os.path.basename(filename)
		self.fexporter._filename = os.path.join('./recipes/', filename)
		self.execute_javascript("document.getElementById('{0}').click();".format(self.fexporter.identifier))

	def og_fixed(self):
		self.engine_room.children['ogfixed_chkbutton'].set_value(not self.engine_room.children['ogfixed_chkbutton'].get_value())
		if self.engine_room.children['ogfixed_chkbutton'].get_value():
			#for butt in ['add_1000g_ing_butt', 'add_100g_ing_butt', 'add_10g_ing_butt', 'add_1g_ing_butt',  'rem_1000g_ing_butt', 'rem_100g_ing_butt', 'rem_10g_ing_butt', 'rem_1g_ing_butt']:
			self.engine_room.children['add_1000g_ing_butt'].set_text('+10%')
			self.engine_room.children['add_1000g_ing_butt'].onclick.connect(lambda e: self.add_percent_ingredients(10))
			self.engine_room.children['add_100g_ing_butt'].set_text('+5%')
			self.engine_room.children['add_100g_ing_butt'].onclick.connect(lambda e: self.add_percent_ingredients(5))
			self.engine_room.children['add_10g_ing_butt'].set_text('+1%')
			self.engine_room.children['add_10g_ing_butt'].onclick.connect(lambda e: self.add_percent_ingredients(1))
			self.engine_room.children['add_1g_ing_butt'].set_text('+0.1%')
			self.engine_room.children['add_1g_ing_butt'].onclick.connect(lambda e: self.add_percent_ingredients(0.1))
			
			self.engine_room.children['rem_1000g_ing_butt'].set_text('-10%')
			self.engine_room.children['rem_1000g_ing_butt'].onclick.connect(lambda e: self.add_percent_ingredients(-10))
			self.engine_room.children['rem_100g_ing_butt'].set_text('-5%')
			self.engine_room.children['rem_100g_ing_butt'].onclick.connect(lambda e: self.add_percent_ingredients(-5))
			self.engine_room.children['rem_10g_ing_butt'].set_text('-1%')
			self.engine_room.children['rem_10g_ing_butt'].onclick.connect(lambda e: self.add_percent_ingredients(-1))
			self.engine_room.children['rem_1g_ing_butt'].set_text('-0.1%')
			self.engine_room.children['rem_1g_ing_butt'].onclick.connect(lambda e: self.add_percent_ingredients(-0.1))
		else:
			self.engine_room.children['add_1000g_ing_butt'].set_text('+1Kg')
			self.engine_room.children['add_1000g_ing_butt'].onclick.connect(lambda e: self.add_weight_ingredients(1000))
			self.engine_room.children['add_100g_ing_butt'].set_text('+100g')
			self.engine_room.children['add_100g_ing_butt'].onclick.connect(lambda e: self.add_weight_ingredients(100))
			self.engine_room.children['add_10g_ing_butt'].set_text('+10g')
			self.engine_room.children['add_10g_ing_butt'].onclick.connect(lambda e: self.add_weight_ingredients(10))
			self.engine_room.children['add_1g_ing_butt'].set_text('+1g')
			self.engine_room.children['add_1g_ing_butt'].onclick.connect(lambda e: self.add_weight_ingredients(1))
			
			self.engine_room.children['rem_1000g_ing_butt'].set_text('-1Kg')
			self.engine_room.children['rem_1000g_ing_butt'].onclick.connect(lambda e: self.add_weight_ingredients(-1000))
			self.engine_room.children['rem_100g_ing_butt'].set_text('-100g')
			self.engine_room.children['rem_100g_ing_butt'].onclick.connect(lambda e: self.add_weight_ingredients(-100))
			self.engine_room.children['rem_10g_ing_butt'].set_text('-10g')
			self.engine_room.children['rem_10g_ing_butt'].onclick.connect(lambda e: self.add_weight_ingredients(-10))
			self.engine_room.children['rem_1g_ing_butt'].set_text('-1g')
			self.engine_room.children['rem_1g_ing_butt'].onclick.connect(lambda e: self.add_weight_ingredients(-1))

	def ibu_fixed(self):
		self.engine_room.children['ibufixed_chkbutton'].set_value(not self.engine_room.children['ibufixed_chkbutton'].get_value())
		if self.engine_room.children['ibufixed_chkbutton'].get_value():		
			self.engine_room.children['add_100g_hop_butt'].set_text('+10%')
			self.engine_room.children['add_100g_hop_butt'].onclick.connect(lambda e: self.add_percent_hops(10))
			self.engine_room.children['add_25g_hop_butt'].set_text('+5%')
			self.engine_room.children['add_25g_hop_butt'].onclick.connect(lambda e: self.add_percent_hops(5))
			self.engine_room.children['add_10g_hop_butt'].set_text('+1%')
			self.engine_room.children['add_10g_hop_butt'].onclick.connect(lambda e: self.add_percent_hops(1))
			self.engine_room.children['add_1g_hop_butt'].set_text('+0.1%')
			self.engine_room.children['add_1g_hop_butt'].onclick.connect(lambda e: self.add_percent_hops(0.1))

			self.engine_room.children['rem_100g_hop_butt'].set_text('-10%')
			self.engine_room.children['rem_100g_hop_butt'].onclick.connect(lambda e: self.add_percent_hops(-10))
			self.engine_room.children['rem_25g_hop_butt'].set_text('-5%')
			self.engine_room.children['rem_25g_hop_butt'].onclick.connect(lambda e: self.add_percent_hops(-5))
			self.engine_room.children['rem_10g_hop_butt'].set_text('-1%')
			self.engine_room.children['rem_10g_hop_butt'].onclick.connect(lambda e: self.add_percent_hops(-1))
			self.engine_room.children['rem_1g_hop_butt'].set_text('-0.1%')
			self.engine_room.children['rem_1g_hop_butt'].onclick.connect(lambda e: self.add_percent_hops(-0.1))
		else:
			self.engine_room.children['add_100g_hop_butt'].set_text('+100g')
			self.engine_room.children['add_100g_hop_butt'].onclick.connect(lambda e: self.add_weight_hops(100))
			self.engine_room.children['add_25g_hop_butt'].set_text('+25g')
			self.engine_room.children['add_25g_hop_butt'].onclick.connect(lambda e: self.add_weight_hops(25))
			self.engine_room.children['add_10g_hop_butt'].set_text('+10g')
			self.engine_room.children['add_10g_hop_butt'].onclick.connect(lambda e: self.add_weight_hops(10))
			self.engine_room.children['add_1g_hop_butt'].set_text('+1g')
			self.engine_room.children['add_1g_hop_butt'].onclick.connect(lambda e: self.add_weight_hops(1))

			self.engine_room.children['rem_100g_hop_butt'].set_text('-100g')
			self.engine_room.children['rem_100g_hop_butt'].onclick.connect(lambda e: self.add_weight_hops(-100))
			self.engine_room.children['rem_25g_hop_butt'].set_text('-25g')
			self.engine_room.children['rem_25g_hop_butt'].onclick.connect(lambda e: self.add_weight_hops(-25))
			self.engine_room.children['rem_10g_hop_butt'].set_text('-10g')
			self.engine_room.children['rem_10g_hop_butt'].onclick.connect(lambda e: self.add_weight_hops(-10))
			self.engine_room.children['rem_1g_hop_butt'].set_text('-1g')
			self.engine_room.children['rem_1g_hop_butt'].onclick.connect(lambda e: self.add_weight_hops(-1))

#Configuration
configuration = {'config_project_name': 'untitled', 'config_address': '0.0.0.0', 'config_port': 8081, 'config_multiple_instance': True, 'config_enable_file_cache': True, 'config_start_browser': False, 'config_resourcepath': './res/'}

if __name__ == "__main__":
	if not os.path.exists('./recipes'):
		os.makedirs('./recipes')
	# start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
	start(beer_engine, title="Wheeler's Wort Works", address=configuration['config_address'], port=configuration['config_port'], 
						multiple_instance=configuration['config_multiple_instance'], 
						enable_file_cache=configuration['config_enable_file_cache'],
						start_browser=configuration['config_start_browser'])