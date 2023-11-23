import tkinter as tk
from PIL import Image, ImageTk
import json
import sys
import os
import shutil


# Create the main Tkinter window
root = tk.Tk()
root.title("Cookie clicker")
root.geometry("750x400")

# Configure rows and columns for layout flexibility
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

# Create frames with different highlight colors for visual separation
frame1 = tk.Frame(root, highlightbackground="red", highlightthickness=2)
frame2 = tk.Frame(root, highlightbackground="green", highlightthickness=2)
frame3 = tk.Frame(root, highlightbackground="blue", highlightthickness=2)
frame4 = tk.Frame(root, highlightbackground="yellow", highlightthickness=2)

# Grid layout for frames
frame1.grid(row=0, column=0, columnspan=1, rowspan=4, sticky="nsew")
frame2.grid(row=0, column=1, columnspan=1, rowspan=4, sticky="nsew")
frame3.grid(row=1, column=2, columnspan=1, rowspan=3, sticky="nsew")
frame4.grid(row=0, column=2, columnspan=1, rowspan=1, sticky="nsew")

# Stop the frames from deforming and centering widgets
for frame in [frame1, frame2, frame3, frame4]:
	frame.columnconfigure(0, weight=1)
	frame.grid_propagate(False)
	frame.pack_propagate(False)

frame3.columnconfigure(1, weight=1)
frame3.columnconfigure(2, weight=1)


class CreateToolTip(object):
	def __init__(self, widget, text='widget info'):
		self.waittime = 50  # miliseconds
		self.wraplength = 180  # pixels
		self.widget = widget
		self.text = text
		self.widget.bind("<Enter>", self.enter)
		self.widget.bind("<Leave>", self.leave)
		self.widget.bind("<ButtonPress>", self.leave)
		self.id = None
		self.tw = None

	def enter(self, event=None):
		self.schedule()

	def leave(self, event=None):
		self.unschedule()
		self.hidetip()

	def schedule(self):
		self.unschedule()
		self.id = self.widget.after(self.waittime, self.showtip)

	def unschedule(self):
		id = self.id
		self.id = None
		if id:
			self.widget.after_cancel(id)

	def showtip(self, event=None):
		x = y = 0
		x, y, cx, cy = self.widget.bbox("insert")
		x += self.widget.winfo_rootx() + 25
		y += self.widget.winfo_rooty() + 20
		# creates a toplevel window
		self.tw = tk.Toplevel(self.widget)
		# Leaves only the label and removes the app window
		self.tw.wm_overrideredirect(True)
		self.tw.wm_geometry("+%d+%d" % (x, y))
		label = tk.Label(self.tw, text=self.text, justify='left',
										 background="#ffffff", relief='solid', borderwidth=1,
										 wraplength=self.wraplength)
		label.pack(ipadx=1)

	def hidetip(self):
		tw = self.tw
		self.tw = None
		if tw:
			tw.destroy()


class CookieClass:
	cookieTotal = 0
	gameClock = 1000

	def __init__(self):
		self.create_cookie_buttons()
		self.load_cookie_total()

	def create_cookie_buttons(self):
		self.cookie_count = tk.Label(frame1, text=f"Cookies = {int(CookieClass.cookieTotal)}", font=('Helvetica bold', 15))
		self.cookie_count.grid(row=0, column=0, pady=2)

		self.cps_label = tk.Label(frame1, text="Cps=0")
		self.cps_label.grid(row=1, column=0, pady=2)

		self.cookie_button = tk.Button(frame1, text="Cookie", width=14, height=7, command=self.cookie_click)
		self.cookie_button.grid(row=2, column=0, pady=20)

	def cookie_update(self):
		self.cookie_count.config(text=f"Cookies = {int(CookieClass.cookieTotal)}")
		self.cps_counter()

	def cookie_click(self):
		CookieClass.cookieTotal += 1
		self.cookie_update()

	@staticmethod
	def load_cookie_total():
		with open('cookieValue.json', 'r') as fp:
			CookieClass.cookieTotal = json.load(fp)

	@staticmethod
	def save_cookie_total():
		with open('cookieValue.json', 'w') as fp:
			json.dump(int(CookieClass.cookieTotal), fp, indent=2)

	def cps_counter(self):
		cps = 0
		for upgrade_type, upgrade in CookieUpgrade.values.items():
			cps += round(upgrade["produceRate"] * upgrade["amount"], 1)
			CookieUpgrade.cps_label.config(text=f"Cps={round(cps, 1)}")


class CookieUpgradeClass(CookieClass):
	def __init__(self):
		super().__init__()
		self.page = 1
		self.values = {}
		self.upgradeCheckDic = {}
		self.buttonUpgradeCheckDic = {}
		self.image_references = {}
		self.buttons = {}
		self.buttonLevels = {}
		self.levelup_buttons = {}
		self.level_up_buttons_values = {}
		self.load_upgrade_values()
		self.create_page_buttons()
		self.create_upgrade_buttons()
		self.create_new_and_exit_buttons()
		self.show_initial_level_up_buttons()
		self.auto_save()
		for upgrade_type in self.values:
			self.update_upgrade(upgrade_type, 0)


	def create_upgrade_buttons(self):
		pageLock = 0
		self.buttons = {}

		if self.page == 1:
			for upgrade_type in self.values:
				button_text = (
					f"{upgrade_type} ({self.values[upgrade_type]['amount']}x)"
					f"[{int(self.values[upgrade_type]['price'])}]"
				)
				self.buttons[upgrade_type] = tk.Button(
					frame3, text=button_text, height=1,
					command=lambda u=upgrade_type: self.upgrade_buy(u))
				self.buttons[upgrade_type].grid(row=len(self.buttons) + 1, column=1, pady=5)
				pageLock += 1
				if pageLock == 5:
					break

		if self.page == 2:
			for upgrade_type in self.values:
				if pageLock >= 5:
					button_text = (
						f"{upgrade_type} ({self.values[upgrade_type]['amount']}x)"
						f"[{int(self.values[upgrade_type]['price'])}]"
					)
					self.buttons[upgrade_type] = tk.Button(
						frame3, text=button_text, height=1,
						command=lambda u=upgrade_type: self.upgrade_buy(u))
					self.buttons[upgrade_type].grid(row=len(self.buttons) + 1, column=1, pady=5)
				pageLock += 1

	def create_page_buttons(self):
		self.page_button = tk.Label(frame3, text=f"Page {self.page}")
		self.page_button.grid(row=0, column=1, pady=5)

		self.page_down_button = tk.Button(frame3, text="<", command=self.page_down)
		self.page_down_button.grid(row=0, column=0, pady=5)

		self.page_up_button = tk.Button(frame3, text=">", command=self.page_up)
		self.page_up_button.grid(row=0, column=2, pady=5)

	def create_new_and_exit_buttons(self):
		new_button = tk.Button(frame3, text="Reset", width=5, height=1, command=self.new_game)
		new_button.place(rely=1.0, relx=1.0, x=-55, y=-3, anchor="se")

		exit_button = tk.Button(frame3, text="Exit", width=5, height=1, command=self.game_exit)
		exit_button.place(rely=1.0, relx=1.0, x=-3, y=-3, anchor="se")

		print_button = tk.Button(frame3, text="Print (Debug)", height=1, command=self.print_list)
		print_button.place(rely=1.0, relx=1.0, x=-160, y=-3, anchor="se")

		restart_button = tk.Button(frame3, text="Restart", width=5, height=1, command=self.restart)
		restart_button.place(rely=1.0, relx=1.0, x=-107, y=-3, anchor="se")

	def load_upgrade_values(self):
		with open('upgradeValues.json', 'r') as fp:
			self.values = json.load(fp)
		with open('upgradeCheck.json', 'r') as fp:
			self.upgradeCheckDic = json.load(fp)
		with open('buttonUpgradeCheck.json', 'r') as fp:
			self.buttonUpgradeCheckDic = json.load(fp)
		for upgrade_type, upgrade in self.values.items():
			image = Image.open(f"{upgrade_type}.png")
			resize_image = image.resize((25, 25))
			self.image_references[upgrade_type] = ImageTk.PhotoImage(resize_image)
		self.level_up_buttons_values = {
			"AutoClicker": {
				1: {"amount": 1, "cost": 100, "description": "Clickers are twice as efficient."},
				2: {"amount": 1, "cost": 500, "description": "Clickers are twice as efficient."},
				3: {"amount": 10, "cost": 10000, "description": "Clickers are twice as efficient."},
				4: {"amount": 25, "cost": 100000, "description": "Clickers are twice as efficient."},
				5: {"amount": 50, "cost": 10000000, "description": "Clickers are twice as efficient."},
				6: {"amount": 100, "cost": 100000000, "description": "Clickers are twice as efficient."},
				7: {"amount": 150, "cost": 1000000000, "description": "Clickers are twice as efficient."},
				8: {"amount": 200, "cost": 10000000000, "description": "Clickers are twice as efficient."},
				9: {"amount": 250, "cost": 10000000000000, "description": "Clickers are twice as efficient."},
				10: {"amount": 300, "cost": 10000000000000000, "description": "Clickers are twice as efficient."},
				11: {"amount": 350, "cost": 100000000000000000, "description": "Clickers are twice as efficient."},
				12: {"amount": 400, "cost": 1000000000000000000, "description": "Clickers are twice as efficient."},
				13: {"amount": 450, "cost": 10000000000000000000, "description": "Clickers are twice as efficient."},
				14: {"amount": 500, "cost": 100000000000000000000, "description": "Clickers are twice as efficient."},
				15: {"amount": 550, "cost": 1000000000000000000000, "description": "Clickers are twice as efficient."}
			},
			"Grandma": {
				1: {"amount": 1, "cost": 1000, "description": "Grandmas are twice as efficient."},
				2: {"amount": 5, "cost": 5000, "description": "Grandmas are twice as efficient."},
				3: {"amount": 25, "cost": 50000, "description": "Grandmas are twice as efficient."},
				4: {"amount": 50, "cost": 5000000, "description": "Grandmas are twice as efficient."},
				5: {"amount": 100, "cost": 500000000, "description": "Grandmas are twice as efficient."},
				6: {"amount": 150, "cost": 50000000000, "description": "Grandmas are twice as efficient."},
				7: {"amount": 200, "cost": 50000000000000, "description": "Grandmas are twice as efficient."},
				8: {"amount": 250, "cost": 50000000000000000, "description": "Grandmas are twice as efficient."},
				9: {"amount": 300, "cost": 50000000000000000000, "description": "Grandmas are twice as efficient."},
				10: {"amount": 350, "cost": 5000000000000000000000, "description": "Grandmas are twice as efficient."},
				11: {"amount": 400, "cost": 500000000000000000000000, "description": "Grandmas are twice as efficient."},
				12: {"amount": 450, "cost": 50000000000000000000000000, "description": "Grandmas are twice as efficient."},
				13: {"amount": 500, "cost": 5000000000000000000000000000, "description": "Grandmas are twice as efficient."},
				14: {"amount": 550, "cost": 500000000000000000000000000000, "description": "Grandmas are twice as efficient."},
				15: {"amount": 600, "cost": 50000000000000000000000000000000, "description": "Grandmas are twice as efficient."}
			},
			"Farm": {
				1: {"amount": 1, "cost": 11000, "description": "Farms are twice as efficient."},
				2: {"amount": 2, "cost": 55000, "description": "Farms are twice as efficient."},
				3: {"amount": 10, "cost": 550000, "description": "Farms are twice as efficient."},
				4: {"amount": 25, "cost": 5500000, "description": "Farms are twice as efficient."},
				5: {"amount": 50, "cost": 550000000, "description": "Farms are twice as efficient."},
				6: {"amount": 100, "cost": 5500000000, "description": "Farms are twice as efficient."},
				7: {"amount": 150, "cost": 55000000000, "description": "Farms are twice as efficient."},
				8: {"amount": 200, "cost": 550000000000, "description": "Farms are twice as efficient."},
				9: {"amount": 250, "cost": 550000000000000, "description": "Farms are twice as efficient."},
				10: {"amount": 300, "cost": 550000000000000000, "description": "Farms are twice as efficient."},
				11: {"amount": 350, "cost": 5500000000000000000, "description": "Farms are twice as efficient."},
				12: {"amount": 400, "cost": 550000000000000000000, "description": "Farms are twice as efficient."},
				13: {"amount": 450, "cost": 55000000000000000000000, "description": "Farms are twice as efficient."},
				14: {"amount": 500, "cost": 5500000000000000000000000, "description": "Farms are twice as efficient."},
				15: {"amount": 550, "cost": 5500000000000000000000000000, "description": "Farms are twice as efficient."},
			},
			"Mine": {
				1: {"amount": 1, "cost": 120000, "description": "Mines are twice as efficient."},
				2: {"amount": 2, "cost": 600000, "description": "Mines are twice as efficient."},
				3: {"amount": 10, "cost": 6000000, "description": "Mines are twice as efficient."},
				4: {"amount": 25, "cost": 60000000, "description": "Mines are twice as efficient."},
				5: {"amount": 50, "cost": 6000000000, "description": "Mines are twice as efficient."},
				6: {"amount": 100, "cost": 60000000000, "description": "Mines are twice as efficient."},
				7: {"amount": 150, "cost": 600000000000, "description": "Mines are twice as efficient."},
				8: {"amount": 200, "cost": 6000000000000, "description": "Mines are twice as efficient."},
				9: {"amount": 250, "cost": 60000000000000000, "description": "Mines are twice as efficient."},
				10: {"amount": 300, "cost": 600000000000000000, "description": "Mines are twice as efficient."},
				11: {"amount": 350, "cost": 6000000000000000000, "description": "Mines are twice as efficient."},
				12: {"amount": 400, "cost": 600000000000000000000, "description": "Mines are twice as efficient."},
				13: {"amount": 450, "cost": 60000000000000000000000, "description": "Mines are twice as efficient."},
				14: {"amount": 500, "cost": 6000000000000000000000000, "description": "Mines are twice as efficient."},
				15: {"amount": 550, "cost": 600000000000000000000000000, "description": "Mines are twice as efficient."},
			},
			"Factory": {
				1: {"amount": 1, "cost": 1300000, "description": "Factories are twice as efficient."},
				2: {"amount": 5, "cost": 6500000, "description": "Factories are twice as efficient."},
				3: {"amount": 25, "cost": 65000000, "description": "Factories are twice as efficient."},
				4: {"amount": 50, "cost": 6500000000, "description": "Factories are twice as efficient."},
				5: {"amount": 100, "cost": 65000000000, "description": "Factories are twice as efficient."},
				6: {"amount": 150, "cost": 6500000000000, "description": "Factories are twice as efficient."},
				7: {"amount": 200, "cost": 6500000000000000, "description": "Factories are twice as efficient."},
				8: {"amount": 250, "cost": 650000000000000000, "description": "Factories are twice as efficient."},
				9: {"amount": 300, "cost": 650000000000000000000, "description": "Factories are twice as efficient."},
				10: {"amount": 350, "cost": 65000000000000000000000, "description": "Factories are twice as efficient."},
				11: {"amount": 400, "cost": 6500000000000000000000000, "description": "Factories are twice as efficient."},
				12: {"amount": 450, "cost": 650000000000000000000000000, "description": "Factories are twice as efficient."},
				13: {"amount": 500, "cost": 65000000000000000000000000000, "description": "Factories are twice as efficient."},
				14: {"amount": 550,
						 "cost": 6500000000000000000000000000000, "description": "Factories are twice as efficient."},
				15: {"amount": 600, "cost": 650000000000000000000000000000000,
						 "description": "Factories are twice as efficient."}
			},
			"Bank": {
				1: {"amount": 1, "cost": 14000000, "description": "Banks are twice as efficient."},
				2: {"amount": 5, "cost": 70000000, "description": "Banks are twice as efficient."},
				3: {"amount": 25, "cost": 700000000, "description": "Banks are twice as efficient."},
				4: {"amount": 50, "cost": 70000000000, "description": "Banks are twice as efficient."},
				5: {"amount": 100, "cost": 7000000000000, "description": "Banks are twice as efficient."},
				6: {"amount": 150, "cost": 700000000000000, "description": "Banks are twice as efficient."},
				7: {"amount": 200, "cost": 700000000000000000, "description": "Banks are twice as efficient."},
				8: {"amount": 250, "cost": 70000000000000000000, "description": "Banks are twice as efficient."},
				9: {"amount": 300, "cost": 70000000000000000000000, "description": "Banks are twice as efficient."},
				10: {"amount": 350, "cost": 7000000000000000000000000, "description": "Banks are twice as efficient."},
				11: {"amount": 400, "cost": 700000000000000000000000000, "description": "Banks are twice as efficient."},
				12: {"amount": 450, "cost": 70000000000000000000000000000, "description": "Banks are twice as efficient."},
				13: {"amount": 500, "cost": 7000000000000000000000000000000, "description": "Banks are twice as efficient."},
				14: {"amount": 550, "cost": 700000000000000000000000000000000, "description": "Banks are twice as efficient."},
				15: {"amount": 600, "cost": 70000000000000000000000000000000000, "description": "Banks are twice as efficient."}
			},
			"Temple": {
				1: {"amount": 1, "cost": 200000000, "description": "Temples are twice as efficient."},
				2: {"amount": 5, "cost": 1000000000, "description": "Temples are twice as efficient."},
				3: {"amount": 25, "cost": 10000000000, "description": "Temples are twice as efficient."},
				4: {"amount": 50, "cost": 1000000000000, "description": "Temples are twice as efficient."},
				5: {"amount": 100, "cost": 100000000000000, "description": "Temples are twice as efficient."},
				6: {"amount": 150, "cost": 10000000000000000, "description": "Temples are twice as efficient."},
				7: {"amount": 200, "cost": 1000000000000000000, "description": "Temples are twice as efficient."},
				8: {"amount": 250, "cost": 100000000000000000000, "description": "Temples are twice as efficient."},
				9: {"amount": 300, "cost": 10000000000000000000000, "description": "Temples are twice as efficient."},
				10: {"amount": 350, "cost": 1000000000000000000000000, "description": "Temples are twice as efficient."},
				11: {"amount": 400, "cost": 100000000000000000000000000, "description": "Temples are twice as efficient."},
				12: {"amount": 450, "cost": 10000000000000000000000000000, "description": "Temples are twice as efficient."},
				13: {"amount": 500, "cost": 1000000000000000000000000000000, "description": "Temples are twice as efficient."},
				14: {"amount": 550, "cost": 100000000000000000000000000000000,
						 "description": "Temples are twice as efficient."},
				15: {"amount": 600, "cost": 10000000000000000000000000000000000,
						 "description": "Temples are twice as efficient."}
			}

		}

	def save_upgrade_values(self):
		with open('upgradeValues.json', 'w') as fp:
			json.dump(self.values, fp, indent=2)

	def upgrade_buy(self, upgrade_type):
		upgrade = self.values[upgrade_type]
		if CookieClass.cookieTotal >= upgrade["price"]:
			CookieClass.cookieTotal -= upgrade["price"]
			CookieClass.cookie_update(self)
			upgrade["amount"] += 1
			self.show_level_up_buttons()
			self.cps_counter()
			self.upgrade_cost(upgrade_type)
			self.buttons[upgrade_type].config(text=f"{upgrade_type} ({upgrade['amount']}x)[{int(upgrade['price'])}]")
			CookieClass.cookie_update(self)
			self.run_upgrade(upgrade_type)

	def show_level_up_buttons(self):
		for upgrade_type in self.level_up_buttons_values:
			for i in range(1, 11):
				values = self.level_up_buttons_values[upgrade_type][i]
				self.show_level_up_buttons_function(upgrade_type, i, values["amount"], values["cost"])

	def show_level_up_buttons_function(self, upgrade_type, numid, amount, cost):
		button_number = "upgradeCheck" + str(numid)
		check = self.upgradeCheckDic[upgrade_type][button_number]
		upgrade = self.values[upgrade_type]
		button_values = self.level_up_buttons_values[upgrade_type]
		ttpnum = numid + 0.1
		if amount <= upgrade["amount"] and check is False:
			self.levelup_buttons[upgrade_type][numid] = tk.Button(
				frame4,
				command=lambda u=upgrade_type: [
					self.auto_level_up(u, numid, cost)],
				image=self.image_references[upgrade_type]
			)
			self.levelup_buttons[upgrade_type][numid].pack(side="left")
			self.levelup_buttons[upgrade_type][ttpnum] = CreateToolTip(self.levelup_buttons[upgrade_type][numid],
													f"{button_values[numid]['description']} ({button_values[numid]['cost']})")
			self.buttonUpgradeCheckDic[upgrade_type][button_number] = True
			self.upgradeCheckDic[upgrade_type][button_number] = True

	def show_initial_level_up_buttons(self):

		for upgrade_type in self.upgradeCheckDic:
			self.levelup_buttons[upgrade_type] = {}

			for i in range(1, 15):
				check = self.upgradeCheckDic[upgrade_type]["upgradeCheck" + str(i)]
				buttonCheck = self.buttonUpgradeCheckDic[upgrade_type]["upgradeCheck" + str(i)]
				button_values = self.level_up_buttons_values[upgrade_type]
				ttpnum = i + 0.1
				numid = i

				if check and buttonCheck is True:

					cost = self.level_up_buttons_values[upgrade_type][i]["cost"]
					self.levelup_buttons[upgrade_type][i] = tk.Button(
						frame4,
						command=lambda u=upgrade_type, numid=i:
						[self.auto_level_up(u, numid, cost)],
						image=self.image_references[upgrade_type]
					)
					self.levelup_buttons[upgrade_type][ttpnum] = CreateToolTip(self.levelup_buttons[upgrade_type][numid],
															f"{button_values[numid]['description']} ({button_values[numid]['cost']})")
					self.levelup_buttons[upgrade_type][i].pack(side="left")
				else:
					continue

	def auto_level_up(self, upgrade_type, numid, cost):
		upgrade = self.values[upgrade_type]
		if CookieClass.cookieTotal >= cost:
			self.levelup_buttons[upgrade_type][numid].pack_forget()
			button_number = "upgradeCheck" + str(numid)
			self.buttonUpgradeCheckDic[upgrade_type][button_number] = False
			CookieClass.cookieTotal -= cost
			upgrade["upgradeLevel"] += 1
			self.cps_counter()
			self.upgrade_value(upgrade_type)
			CookieClass.cookie_update(self)

	def upgrade_value(self, upgrade_type):
		upgrade = self.values[upgrade_type]
		if upgrade["upgradeLevel"] > 1:
			stack = upgrade["upgradeLevel"] - 1
			upgrade["produceRate"] = upgrade["baseRate"] * 2 ** stack

	def upgrade_cost(self, upgrade_type):
		upgrade = self.values[upgrade_type]
		upgrade["price"] = upgrade["baseCost"] * 1.15 ** upgrade["amount"]

	def run_upgrade(self, upgrade_type):
		upgrade = self.values[upgrade_type]
		if upgrade["amount"] > 0:
			self.upgrade_value(upgrade_type)
			CookieClass.cookieTotal += upgrade["produceRate"]
			root.after(self.gameClock, CookieClass.cookie_update, self)
			root.after(self.gameClock, self.run_upgrade, upgrade_type)

	def update_upgrade(self, upgrade_type, counter):
		upgrade = self.values[upgrade_type]
		while counter < upgrade["amount"]:
			self.run_upgrade(upgrade_type)
			counter += 1

	def auto_save(self):
		self.save_upgrade_values()
		CookieClass.save_cookie_total()
		with open('upgradeCheck.json', 'w') as fp:
			json.dump(self.upgradeCheckDic, fp, indent=2)
		with open('buttonUpgradeCheck.json', 'w') as fp:
			json.dump(self.buttonUpgradeCheckDic, fp, indent=2)

		print("Debug")

		root.after(60000, self.auto_save)

	def game_exit(self):
		self.save_upgrade_values()
		CookieClass.save_cookie_total()
		with open('upgradeCheck.json', 'w') as fp:
			json.dump(self.upgradeCheckDic, fp, indent=2)
		with open('buttonUpgradeCheck.json', 'w') as fp:
			json.dump(self.buttonUpgradeCheckDic, fp, indent=2)
		root.quit()

	def new_game(self):
		shutil.copyfile("baseCookieValue.json", "cookieValue.json")
		shutil.copyfile("baseUpgradeValues.json", "upgradeValues.json")
		shutil.copyfile("baseUpgradeCheck.json", "upgradeCheck.json")
		shutil.copyfile("baseButtonUpgradeCheck.json", "buttonUpgradeCheck.json")

		python = sys.executable
		os.execl(python, python, *sys.argv)

	def print_list(self):
		print(self.buttons)
		print(len(self.buttons))

	def restart(self):
		self.save_upgrade_values()
		CookieClass.save_cookie_total()
		with open('upgradeCheck.json', 'w') as fp:
			json.dump(self.upgradeCheckDic, fp, indent=2)
		with open('buttonUpgradeCheck.json', 'w') as fp:
			json.dump(self.buttonUpgradeCheckDic, fp, indent=2)

		python = sys.executable
		os.execl(python, python, *sys.argv)

	def page_up(self):
		self.page_up_button.config(state="disabled")
		self.page_down_button.config(state="active")

		for upgrade_type in self.values:
			if upgrade_type in self.buttons:
				self.buttons[upgrade_type].grid_forget()

		self.page = 2
		self.page_button.config(text=f"Page {self.page}")
		self.create_upgrade_buttons()

	def page_down(self):
		self.page_down_button.config(state="disabled")
		self.page_up_button.config(state="active")

		for upgrade_type in self.values:
			if upgrade_type in self.buttons:
				self.buttons[upgrade_type].grid_forget()

		self.page = 1
		self.page_button.config(text=f"Page {self.page}")
		self.create_upgrade_buttons()


Cookie = CookieClass()
CookieUpgrade = CookieUpgradeClass()

root.mainloop()
