import os
import json
# Variables
original_version="1.18.1"
# Functions

def save_configuration(configuration):
	with open("config.json", "w") as config_file:
		configuration_json = json.dumps(configuration, indent=4)
		config_file.write(configuration_json)
		config_file.close()
def load_configuration():
	if os.path.exists("config.json"):
		with open("config.json", "r") as config_file:
			config_json = config_file.read()
		configuration = json.loads(config_json)
		return configuration
	else:
		print("The configuration file is blank or does not exist.\nRunning image creation script.")
		configuration = {"images": [], "containers": []}
		save_configuration(configuration)
		add_container()
		# The following commands get run again as the configuration needs to be reloaded
		with open("config.json", "r") as config_file:
			config_json = config_file.read()
		configuration = json.loads(config_json)
		return configuration
		
def add_image(version, ram):
	configuration = load_configuration()
	name = "docker_mc-version"+version+"-ram"+ram
	if {"name": name} not in configuration["images"]:
		create_image(version, ram)
		print(name+" created")
		configuration["images"].append({"name": name, "version": version, "ram": ram, "containers": []})
		save_configuration(configuration)
	
def create_image(version, ram):
	# Copy Dockerfile
	with open("Dockerfile", "r") as dockerfile:
		original_dockerfile=dockerfile.read()
		dockerfile.close()
	with open("Dockerfile_mc-version"+version+"-ram"+ram, "w") as dockerfile:
		new_dockerfile = original_dockerfile.replace(original_version, version)
		new_dockerfile = new_dockerfile.replace("MAXRAM", ram)
		dockerfile.write(new_dockerfile) 
		dockerfile.close()
	os.system("docker build -t docker_mc-version"+version+"-ram"+ram + " --file Dockerfile_mc-version"+version+"-ram"+ram + " .")
	print("docker build -t docker_mc-version"+version+"-ram"+ram + " --file Dockerfile_mc-version"+version+"-ram"+ram + " .")
def add_container():
	version = input("What would you like the version to be?\n")
	ram = input("How much RAM would you like the container to use at most, in MiB?\n")
	add_image(version, ram)
	configuration = load_configuration()
	name = input("What would you like the name of the container to be?\n")
	mc_port = input("What port would you like the minecraft server to use?\n")
	mc_rcon = input("What port would you like the minecraft rcon server to use?\n")			
	for image in configuration["images"]:
		if(image["name"] == "docker_mc-version"+version+"-ram"+ram):
			create_container(name, mc_port, mc_rcon, image)
			return
	print("Error: Image not found")
	menu()

def create_container(name, mc_port, rcon_port, image):
	configuration = load_configuration()
	if name not in configuration["containers"]:
		configuration["containers"].append(name)
	if name not in image["containers"]:
		image["containers"].append(name)
	save_configuration(configuration)
	print("docker run -t -d -p" + mc_port + "25565 -p" + rcon_port + "25575 --name " + name + " " + image["name"])
	os.system("docker run -t -d -p" + mc_port + "25565 -p" + rcon_port + "25575 --name " + name + " " + image["name"])

def menu():
	selection = input("""Action (type number or captalized words): 
  1) Add a new CONTAINER
  2) Add an IMAGE
  3) REMOVE an IMAGE
  4) REMOVE a CONTAINER
  5) Configure RCON
  6) EXIT
""") # Options to list, stop, and start containers still needs to be added
	if(selection == "1" or selection == "container"):
		add_container()
	elif(selection == "2" or selection == "image"):
		add_image(input("What would you like the version to be?\n"), input("How much RAM would you like the image to use at most, in MiB?\n"))
	elif(selection == "3" or selection == "remove image"):
		configuration = load_configuration()
		i = 0
		print("Select the image you want to remove:")
		for image in configuration["images"]:
			i += 1 # The same thing as i = i +1
			print("  " + str(i) + ") " + image["name"] + " - " + image["version"] + " - " + image["ram"] + " MiB") # {space} 1) <image name> - <version> - <ram amount> MiB 
		print("  " + str(i + 1) + ") Cancel") # At the end of the menu, add an option to cancel
		selection = input("") # Ask for input without a prompt
		if(selection.isdigit()): # If the input is a digit
			selection = int(selection) #  Turn it into an integer
			if(selection <= i): # If the selection is valid, aka less than i
				confirmation = input("Are you sure you want to remove this image and every single cotnainer associated with it? If so, type \"Yes, I am sure I want to do this.\"\n")
				if(confirmation == "Yes, I am sure I want to do this."):
					# Image removal from Docker needs to be added
					# Dockerfile for the image should be removed
					image = configuration["images"][selection-1] # Get the image selected

					# remove the containers associated with the image
					for i in image["containers"]:
						os.system("docker rm -f " + image["containers"][i])

					# remove the image 
					os.system("docker rm " + image["name"])

					# remove the Dockerfile
					os.remove(image["name"].replace("docker", "Dockerfile"))
					
					configuration["images"].pop(selection-1) # Remove the image selected from the list
					save_configuration(configuration) # save the configuration
				else:
					print("Canceling")
					menu()
		menu()
	elif(selection == "4" or selection == "remove container"): # Will resemble image removal
		print("Not yet implemented")
		menu()
	elif(selection == "5" or selection == "rcon"): # Majority of rcon support is added, however intergration with configuration is required
		config_rcon()
	elif(selection == "6" or selection == "exit"):
		print("Exiting")
		exit()
	else:
		print("Invalid selection")
		menu()

# Set up rcon 
def config_rcon():
	# Set up rcon 
	# Request user input
	print("In order to remotly access the console of the Minecraft server, rcon needs to be setup\nrcon is a protcol for remotely managing game servers")
	password = input("What is the password you would like to set for rcon?\n")
	# port=input("\nWhat is the port you would like to use for rcon?\n")
	print("\nEditing files\n")
	# Read original_server.properties
	with open ("original_server.properties", "r") as original_config_file:
		original_config = original_config_file.read()
		original_config_file.close()
	new_config = original_config.replace("rcon.password=", "rcon.password="+password)
	# new_config = original_config.replace("rcon.port=25575", "rcon.port="+port)
	# Write to server.properties
	with open ("server.properties", "w") as server_config:
		server_config.write(new_config)
		server_config.close()

	# Remove server.properties
	print("Removing server.properties in container\n")
	os.system("sudo docker exec docker-minecraft-container rm -rf /root/minecraft/server.properties")
	# Copy server.properties to /root/minecraft/server.properties
	print("Copying server.properties to the container")
	os.system("sudo docker cp server.properties docker-minecraft-container:/root/minecraft/server.properties")
	# Restart the docker container
	print("Retarting the container\n")
	os.system("sudo docker restart docker-minecraft-container")


print("This program will ask for authentication in order to use sudo\n")
menu()
# Load config


"""
NOTES:
[ ] Addition of containers from JSON and system (port, version, name rcon_port, image)
[ ] Removal of containers from JSON and system
[X] Removal of images from JSON and system
[ ] Rcon support
[ ] Support to accesss container's shell
[ ] File transfer
[ ] Abilty to start and stop containers
"""