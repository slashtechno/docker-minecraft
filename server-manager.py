import os
import json
import re

# Variables
original_version="1.18.1"
# Functions

def save_configuration(configuration):
	with open("config.json", "w") as config_file:
		configuration_json = json.dumps(configuration, indent=4)
		config_file.write(configuration_json)
		config_file.close()
def load_configuration():
	if os.path.exists("config.json"): # If config.json exists:
		with open("config.json", "r") as config_file: # Open config.json for reading
			config_json = config_file.read() # Read config.json
		configuration = json.loads(config_json) # Turn config_json into a dictionary and set that to configuration
		return configuration
	else:
		print("The configuration file is blank or does not exist.\nRunning image creation script.")
		configuration = {"images": [], "containers": []}
		save_configuration(configuration)
		# The following commands get run again as the configuration needs to be reloaded
		with open("config.json", "r") as config_file:
			config_json = config_file.read()
		configuration = json.loads(config_json)
		return configuration
		
def add_image(version, ram):
	configuration = load_configuration() # Load configuration
	name = "docker_mc-version"+version+"-ram"+ram # Set name to docker_mc-version<version>-ram<ram>
	if {"name": name} not in configuration["images"]: # If the name of the image to be added does not exist already in config.json:
		create_image(version, ram) # Create image, passing the version and ram
		print(name + " created")
		configuration["images"].append({"name": name, "version": version, "ram": ram, "containers": []}) # Append to the list of images. "containers" is a key that tracks what containers rely on the image in the form of a list 
		save_configuration(configuration)
	
def create_image(version, ram):
	# Copy Dockerfile
	with open("Dockerfile", "r") as dockerfile: # Open original Dockerfile for reading
		original_dockerfile=dockerfile.read()
		dockerfile.close()
	with open("Dockerfile_mc-version"+version+"-ram"+ram, "w") as dockerfile: # Create a new Dockerfile named Dockerfile_mc-version<version>-ram<ram>
		new_dockerfile = original_dockerfile.replace(original_version, version) # Replace the default version with the user inputed version
		new_dockerfile = new_dockerfile.replace("MAXRAM", ram) # Replace the maximum RAM placeholder with user inputed ram
		dockerfile.write(new_dockerfile) 
		dockerfile.close()
	os.system("docker build -t docker_mc-version"+version+"-ram"+ram + " --file Dockerfile_mc-version"+version+"-ram"+ram + " .") # Build the Dockerfile that was just made
def add_container():
	version = input("What would you like the version to be?\n") # Input version
	ram = input("How much RAM would you like the container to use at most, in MiB?\n") # Input RAM
	add_image(version, ram) # Pass version and ram to image addition 
	configuration = load_configuration()
	# Ask for various properties for the new container
	name = input("What would you like the name of the container to be?\n") 
	mc_port = input("What port would you like the minecraft server to use?\n")
	mc_rcon = input("What port would you like the minecraft rcon server to use?\n")			
	for image in configuration["images"]: # Iterate over images
		if(image["name"] == "docker_mc-version"+version+"-ram"+ram): # If an image matches:
			create_container(name, mc_port, mc_rcon, image) # Start container creation, passing various variables
			break # Exit the loop when an image is found and container created
	menu() # Display menu

def create_container(name, mc_port, rcon_port, image):
	configuration = load_configuration()
	if {"name": name} not in configuration["containers"]: # If the container's name does not exist in the list of containers:
		configuration["containers"].append({"name": name, "image": image}) # Append to the list of containers with the the name of the container being created as well as what image it relies on
	if { "name": name} not in image["containers"]: # If the image that the container relies does not contain the container in the list of containers that rely on it:
		image["containers"].append({"name": name}) # Append to the image's container list the name of the new container
	save_configuration(configuration) # Save the configuration
	print("[1m[41mDO NOT INTERACT WITH THE PROGRAM. DOING SO MAY RUN UNINTENTIONAL COMMANDS AS THE SCRIPT IS STILL RUNNING") # Using ANSI escape codes to make the text red and bold
	os.system("docker run -t -d -p" + mc_port + ":25565 -p" + rcon_port + ":25575 --name " + name + " " + image["name"]) # Create the container using Docker with a user generated name
	config_rcon(name) # Start the rcon configuration

def menu():
	selection = input("""Action (type number or captalized words as a lowercase word): 
  1) Add a new CONTAINER
  2) Add an IMAGE
  3) Manage CONTAINERS
  4) Manage IMAGES
  5) EXIT
""") # Options to list, stop, and start containers still needs to be added
	if(selection == "1" or selection == "container"):
		add_container() # Start container addition
	elif(selection == "2" or selection == "image"):
		add_image(input("What would you like the version to be?\n"), input("How much RAM would you like the image to use at most, in MiB?\n"))
	elif(selection == "3" or selection == "containers"):
		manage_containers()
	elif(selection == "4" or selection == "images"):
		manage_images()
	elif(selection == "5" or selection == "exit"):
		print("Exiting")
		exit()
	else:
		print("Invalid selection")
		menu()

def manage_containers():
	configuration = load_configuration()
	i = 0
	print("What container do you want to manage?")
	for container in configuration["containers"]:
		i += 1 # The same thing as i = i +1
		print("  " + str(i) + ") " + container["name"]) # {space} 1) container name
	print("  " + str(i + 1) + ") Cancel") # At the end of the menu, add an option to cancel
	selection = input("") # Ask for input without a prompt
	if(selection.isdigit()): # If the input is a digit
		selection = int(selection) #  Turn it into an integer
		if(selection <= i): # If the selection is valid, aka less than i
			manage_container(configuration["containers"][selection-1])
		else:
			print("Canceling")
			menu()


def manage_container(container):
	configuration= load_configuration
	print("""What would you like to do with this container?
  1) Start
  2) Stop
  3) Restart
  4) Remove
  5) Change RCON password
  6) Transfer files
  7) Access Shell
  8) Cancel""")
	selection = input("")
	if(selection == "1" or selection == "start"):
		containerName = container["name"]
		os.system(f"docker start {containerName}")
	elif(selection == "2" or selection == "stop"):
		containerName = container["name"]
		os.system(f"docker stop {containerName}")
	elif(selection == "3" or selection == "restart"):
		containerName = container["name"]
		os.system(f"docker restart {containerName}")
	elif(selection == "4" or selection == "remove"):
		confirmation = input("Are you sure you want to remove this container? If so, type \"Yes, I am sure I want to do this.\"\n")
		if(confirmation == "Yes, I am sure I want to do this."):
			containerName = container["name"]
			os.system(f"docker rm -f {containerName}")
			configuration["containers"].pop(selection-1)
			save_configuration(configuration)
	elif(selection == "5" or selection == "rcon"):
		config_rcon(container["name"])
	menu()

def manage_images():
	configuration = load_configuration()
	i = 0
	print("Select the image you want to manage:")
	for image in configuration["images"]:
		i += 1 # The same thing as i = i +1
		print("  " + str(i) + ") " + image["name"] + " - " + image["version"] + " - " + image["ram"] + " MiB") # {space} 1) <image name> - <version> - <ram amount> MiB 
	print("  " + str(i + 1) + ") Cancel") # At the end of the menu, add an option to cancel
	selection = input("") # Ask for input without a prompt
	if(selection.isdigit()): # If the input is a digit
		selection = int(selection) #  Turn it into an integer
		if(selection <= i): # If the selection is valid, aka less than i
			manage_image(configuration["images"][selection-1]) # Get the image selected and pass it to manage_image(image)
		else:
			menu()

def manage_image(image):
	configuration = load_configuration()
	print("""What would you like to do with this image?
  1) Remove
  2) Cancel""")
	selection = input("")
	if(selection == "1" or selection == "remove"):
		confirmation = input("Are you sure you want to remove this image? By doing so, you will remove all containers assosiated with it. If so, type \"Yes, I am sure I want to do this.\"\n")
		if(confirmation == "Yes, I am sure I want to do this."):
			image = configuration["images"][selection-1] # Get the image selected

			# remove the containers associated with the image
			for i in image["containers"]:
				os.system("docker rm -f " + image["containers"][i].image["name"])

			# remove the image 
			os.system("docker rmi " + image["name"])

			# remove the Dockerfile
			os.remove(image["name"].replace("docker", "Dockerfile"))
			
			configuration["images"].pop(selection-1) # Subtract 1 from the selection because Python lists are zero indexed
			save_configuration(configuration)
	menu()

# Set up rcon 
def change_rcon_password(container):
	password = input("What would you like the password to be?\n")
	print("Editing files\n")
	# Get the current server_properties
	os.system(f"docker cp {container}:/root/minecraft/server.properties ./server.properties")
	with open ("server.properties", "r") as container_config_file:
		container_config = container_config_file.read()
		container_config_file.close()
	new_config = re.sub(container_config, "^rcon\.password=[a-zA-Z0-9\"`'#%&,:!;\-\_\.<>=@{}~\$\(\)\*\+\/\\\?\[\]\^\|]+$", f"rcon.password={password}")
def config_rcon(container):
	# Set up rcon 
	# Request user input
	print("In order to remotely access the console of the Minecraft server, rcon needs to be setup\nrcon is a protcol for remotely managing game servers")
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
	os.system(f"sudo docker exec {container} rm -rf /root/minecraft/server.properties")
	# Copy server.properties to /root/minecraft/server.properties
	print("Copying server.properties to the container")
	os.system(f"sudo docker cp server.properties {container}:/root/minecraft/server.properties")
	# Restart the docker container
	print("Retarting the container\n")
	os.system(f"sudo docker restart {container}")


print("This program will ask for authentication in order to use sudo\n")
menu() # Show menu
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