import argparse
from subprocess import run as run_command
from sys import exit

MAX_VALUE = 1024
MIN_VALUE = 0

# Número do GPIO para _backlight_. Nesse exemplo: PIN 12
DEFAULT_PIN = 12
DEFAULT_AMOUNT = 1024

brightness_levels = [0, 16, 32, 64, 128, 256, 512, 1024]

BRIGHTNESS_LOG_PATH = "/home/pi/scripts/screen.log"

parser = argparse.ArgumentParser(description="Retrieve and update screen brightness using GPIO PWM", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("action", choices=["init", "get", "set", "increment", "decrement"], help="action to perform", default="get")
parser.add_argument("amount",type=int, nargs="?", help="amount to increase/decrease from screen brightness. (0-1024)", default=DEFAULT_AMOUNT)

parser.add_argument("-p", "--pin", help="BCM GPIO pin number.", default=DEFAULT_PIN)
parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode. Do not show results of changes.")

def retrieve_brightness():
	with open(BRIGHTNESS_LOG_PATH) as file:
		content = file.read()
		value = int(content)
		try:
			index = brightness_levels.index(value)
			return [value, index]
		except ValueError:
			return [value, 0]

def save_brightness(value, pin):
	run_command(["gpio", "-g", "pwm", str(pin), str(value)])
	with open(BRIGHTNESS_LOG_PATH, "w") as file:
		file.write(str(value))

def main():
	[brightness_value, brightness_idx] = retrieve_brightness()

	args = parser.parse_args()	
	config = vars(args)

	def log(message):
		if (config["quiet"]):
			return
		print(message)

	def check_brightness_range(value):
		if (value > MAX_VALUE or value < MIN_VALUE):
			log("Error: Invalid `amount` argument for brightness value")
			exit(1)

	if config["action"] == "init":
		# Initialize pin with PMW
		run_command(["gpio", "-g", "mode", str(config["pin"]), "pwm"])
		log("Initializing screen brightness with saved value: {}".format(brightness_value))
		return

	elif config["action"] == "get":
		print("Retrieving screen brigthness value: {}".format(brightness_value))
		return

	elif config["action"] == "set":
		check_brightness_range(config["amount"])
		log("Setting value for screen brightness: {}".format(config["amount"]))
		save_brightness(config["amount"], config["pin"])

	elif config["action"] == "increment":
		next_idx = min(brightness_idx + 1, len(brightness_levels) - 1)
		brightness_value = brightness_levels[next_idx]

	elif config["action"] == "decrement":
		next_idx = max(brightness_idx + 1, 0)
		brightness_value = brightness_levels[next_idx]

	log("Setting value for screen brightness: {}".format(brightness_value))
	save_brightness(brightness_value, config["pin"])

if __name__ == "__main__":
	main()
