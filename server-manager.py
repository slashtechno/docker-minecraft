import os
import json
import re
import subprocess
import pathlib
from prettytable import PrettyTable

# subprocess.run debugging
# command = []
# space = " "
# print(space.join(command))

# Variables
original_version="1.18.1"
# Functions
config_file_path = str(pathlib.Path("config.json").resolve())
def save_configuration(configuration):
	with open(config_file_path, "w") as config_file:
		configuration_json = json.dumps(configuration, indent=4)
		config_file.write(configuration_json)
		config_file.close()
def load_configuration():
	if os.path.exists(config_file_path): # If config.json exists:
		with open(config_file_path, "r") as config_file: # Open config.json for reading
			config_json = config_file.read() # Read config.json
		configuration = json.loads(config_json) # Turn config_json into a dictionary and set that to configuration
		return configuration
	else:
		# print("The configuration file is blank or does not exist.\nRunning image creation script.")
		print("The configuration file is blank or does not exist.")
		configuration = {"images": [], "containers": []}
		save_configuration(configuration)
		# The following commands get run again as the configuration needs to be reloaded
		with open(config_file_path, "r") as config_file:
			config_json = config_file.read()
		configuration = json.loads(config_json)
		return configuration
		
def add_image(version, ram):
	configuration = load_configuration() # Load configuration
	name = "docker_mc-version"+version+"-ram"+ram # Set name to docker_mc-version<version>-ram<ram>
	for image in configuration["images"]:
		if image["name"] == name: # If the name of the image to be added does not exist already in config.json:
			print(f"Image {name} already exists")
			break
	else:
		create_image(version, ram) # Create image, passing the version and ram
		print(name + " created")
		configuration["images"].append({"name": name, "containers": []}) # Append to the list of images. "containers" is a key that tracks what containers rely on the image.
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
	# print("\u001b[1m\u001b[41mDO int. DOING SO MAY RUN UNINTENTIONAL COMMANDS AS THE SCRIPT IS STILL RUNNING") # Using ANSI escape codes to make the text red and bold
	# print("DON'T INTERACT WITH THE PROGRAM WHILE THE IMAGE IS BEING CREATED, DOING SO MAY RUN UNINTENTIONAL COMMANDS AS THE SCRIPT IS STILL RUNNING")
	image_name = "docker_mc-version"+version+"-ram"+ram
	dockerfile_name = pathlib.Path("Dockerfile_mc-version"+version+"-ram"+ram).resolve()
	# os.system("docker build -t docker_mc-version"+version+"-ram"+ram + " --file Dockerfile_mc-version"+version+"-ram"+ram + " .") # Build the Dockerfile that was just made 
	subprocess.run(["docker", "build", "-t", image_name, "--file", str(dockerfile_name), "."])
	pathlib.Path.unlink(dockerfile_name)
def configure_new_container():
	configuration = load_configuration()
	version = input("What would you like the version to be?\n") # Input version
	ram = input("How much RAM would you like the container to use at most, in MiB?\n") # Input RAM
	while True:
		name = input("What would you like the name of the container to be? ([a-zA-Z0-9][a-zA-Z0-9_.-] are allowed)\n") 
		for i in configuration["containers"]:
			if i["name"] == name:
				print("This container name is already in use")
				break
		else:
			break
	mc_port = input("What port would you like the minecraft server to use?\n")
	rcon_port = input("What port would you like the minecraft rcon server to use?\n")			
	add_image(version, ram) # Pass version and ram to image addition 
	configuration = load_configuration()
	# Ask for various properties for the new container
	for image in configuration["images"]: # Iterate over images
		if image["name"] == "docker_mc-version"+version+"-ram"+ram: # If an image matches:
			image_index = configuration["images"].index(image) # Get the index of the image
			create_container(mc_port, rcon_port, image, image_index, name) # Start container creation, passing various variables.
			break # Exit the for loop when an image is found and container created
	menu()
def create_container(mc_port, rcon_port, image, image_index, name):
	configuration = load_configuration()
	if {"name": name} not in configuration["containers"]: # If the container's name does not exist in the list of containers:
		configuration["containers"].append({"name": name, "image": image["name"], "ports": {mc_port:"25565", rcon_port:"25575"}}) # Append to the list of containers with container information; The first port is the host port, second is the container port
	if { "name": name} not in configuration["images"][image_index]["containers"]: # If the image that the container relies does not contain the container in the list of containers that rely on it:
		configuration["images"][image_index]["containers"].append(name) # Append to the image's container list the name of the new container
	save_configuration(configuration) # Save the configuration
	# print("\u001b[1m\u001b[41mDO int. DOING SO MAY RUN UNINTENTIONAL COMMANDS AS THE SCRIPT IS STILL RUNNING") # Using ANSI escape codes to make the text red and bold
	# print("DON'T INTERACT WITH THE PROGRAM WHILE THE CONTAINER IS BEING CREATED, DOING SO MAY RUN UNINTENTIONAL COMMANDS AS THE SCRIPT IS STILL RUNNING")
	# os.system("docker run -t -d -p " + mc_port + ":25565 -p " + rcon_port + ":25575 --name " + name + " " + image["name"]) # Create the container using Docker with a user generated name
	for i in configuration["containers"]:
		if i["name"] == name:
			container = i
			break
	else:
		print("Container not found in configuration")
			
	# subprocess.run(["docker", "run", "-t", "-d", "-p", mc_port+":25565", "-p", rcon_port+":25575", "--name", name, image["name"]])
	port_args = []
	for host_port, container_port in configuration["containers"][configuration["containers"].index(container)]["ports"].items():
		port_args.append("-p")
		port_args.append(host_port+":"+container_port)
	run_command = ["docker", "run", "-t", "-d", "--name", name, image["name"]]
	i = 0
	for port in port_args:
		run_command.insert(4+i, port)
		i+= 1
	subprocess.run(run_command)
	config_rcon(name) # Start the rcon configuration


def menu():
	print("""Action: 
  1) Add a new CONTAINER
  2) Add an IMAGE
  3) Manage CONTAINERS
  4) Manage IMAGES
  5) EXIT
""")
	selection = input("").lower()
	if selection == "1" or selection == "container":
		configure_new_container() # Start container addition
	elif selection == "2" or selection == "image":
		add_image(input("What would you like the version to be?\n"), input("How much RAM would you like the image to use at most, in MiB?\n"))
	elif selection == "3" or selection == "containers":
		manage_containers()
	elif selection == "4" or selection == "images":
		manage_images()
	elif selection == "5" or selection == "exit" :
		print("Exiting")
		exit()
	else:
		print("Invalid selection")
		menu()
	menu() # Repeat

def manage_containers():
	configuration = load_configuration()
	i = 0
	print("What container do you want to manage?")
	for container in configuration["containers"]:
		i += 1 # The same thing as i = i +1
		print("  " + str(i) + ") " + container["name"]) # {space} 1) container name
	print("  " + str(i + 1) + ") Cancel") # At the end of the menu, add an option to cancel
	selection = input("") # Ask for input without a prompt
	if selection.isdigit(): # If the input is a digit
		selection = int(selection) #  Turn it into an integer
		if selection <= i: # If the selection is valid, aka less than i
			manage_container(configuration["containers"][selection-1], selection-1) # In addition to passing the container dictionary, pass the index
		else:	
			menu()


def manage_container(container, container_index):
	configuration = load_configuration()
	container_name = container["name"]
	print("""What would you like to do with this container?
  1) START
  2) STOP
  3) RESTART
  4) REMOVE
  5) Change RCON password
  6) Access SHELL
  7) Manage PORTS 
  8) CANCEL""") # File transfer should be added later
	selection = input("").lower()
	if selection == "1" or selection == "start":
		# os.system(f"docker start {container_name}")
		subprocess.run(["docker", "start", container_name])
	elif selection == "2" or selection == "stop":
		# os.system(f"docker stop {container_name}")
		subprocess.run(["docker", "stop", container_name])
	elif selection == "3" or selection == "restart":
		# os.system(f"docker restart {container_name}")
		subprocess.run(["docker", "restart", container_name])
	elif selection == "4" or selection == "remove":
		delete_container(container, container_index)
	elif selection == "5" or selection == "rcon":
		config_rcon(container["name"])
	elif selection == "6" or selection == "shell":
		# os.system(f"docker exec -it {container_name} bash")
		subprocess.run(["docker", "exec", "-it", container_name, "bash"])
	elif selection == "7" or selection == "ports":
		manage_container_ports(container, container_index)
	elif selection == "8" or selection == "CANCEL":
		manage_containers()
	else:
		print("Invalid selection")
		manage_container(container, container_index)
	configuration = load_configuration()
	if container in configuration["containers"]: # If the container is deleted, this will be false
		manage_container(container, container_index)
	else:
		manage_containers()

def delete_container(container, container_index): # container paremeter should be a dictionary
	configuration = load_configuration()
	confirmation = input("Are you sure you want to remove this container? If so, type \"Yes, I am sure I want to do this.\"\n")
	if confirmation == "Yes, I am sure I want to do this.":
		container_name = container["name"]
		# Remove container from list of containers and from the image it relies on
		configuration["containers"].pop(container_index)
		for i in configuration["images"]: # Iterate over images
			if i["name"] == container["image"]: # When an image matches:
				image_index = configuration["images"].index(i)
				break
		else:
			print("Could not find image")
		for i in configuration["images"][image_index]["containers"]:
			container_rely_index = configuration["images"][image_index]["containers"].index(i)
			if configuration["images"][image_index]["containers"][container_rely_index] == container["name"]:
				# container_rely_index = configuration["images"][image_index]["containers"].index(i)
				break
		else:
			print("Container not found")
		configuration["images"][image_index]["containers"].pop(container_rely_index)
		# os.system(f"docker rm -f {container_name}")
		subprocess.run(["docker", "stop", container["name"]])
		subprocess.run(["docker", "rm", "-f", container["name"]])
		save_configuration(configuration)

def rerun_container(container, container_index):
	configuration = load_configuration()
	while True:	
		new_image_name = input("""What would you like the new image to be named?
Only lowercase letters may be used
Numeric values are allowed
Allowed special characters: . - / _
Special characters may not prefix nor trail the image name
Maximum length of an image name is 255 characters\n""")	
		for image in configuration["images"]:
			if image["name"] == new_image_name: # If the name of the image to be added does not exist already in config.json:
				print(f"\nImage {new_image_name} already exists\n") # Perhaps allow the user to add exclamation marks to the start and end of the image name to override this
				break
		else:
			break
	old_image = configuration["containers"][container_index]["image"]
	for image in configuration["images"]:
		if image["name"] == old_image:
			old_image = image
			break
	for i in configuration["images"][configuration["images"].index(old_image)]["containers"]:
		if i == container["name"]:
			configuration["images"][configuration["images"].index(old_image)]["containers"].pop(configuration["images"][configuration["images"].index(old_image)]["containers"].index(i))
			break
	configuration["containers"][container_index]["image"] = new_image_name
	subprocess.run(["docker", "stop", configuration["containers"][container_index]["name"]])
	subprocess.run(["docker", "commit", configuration["containers"][container_index]["name"], new_image_name])
	print(new_image_name + " created")
	configuration["images"].append({"name": new_image_name,"containers": [container["name"]]}) # Append to the list of images. "containers" is a key that tracks what containers rely on the image.
	save_configuration(configuration)
	port_args = []
	for host_port, container_port in configuration["containers"][container_index]["ports"].items():
		port_args.append("-p")
		port_args.append(host_port+":"+container_port)
	run_command = ["docker", "run", "-t", "-d", "--name", configuration["containers"][container_index]["name"], new_image_name]
	i = 0
	for port in port_args:
		run_command.insert(4+i, port)
		i+= 1
	subprocess.run(["docker", "rm", configuration["containers"][container_index]["name"]])
	subprocess.run(run_command)
	save_configuration(configuration)
	
def manage_container_ports(container, container_index):
	configuration = load_configuration()
	print("""Action:
  1) LIST ports
  2) ADD port 
  3) REMOVE port
  4) CANCEL
""")
	selection = input("").lower()
	if selection == "1" or selection == "list":
		# print("| Host Port | Container Port |")
		port_table = PrettyTable(["Host Port", "Container Port"	]) 
		for host_port, container_port in configuration["containers"][container_index]["ports"].items():
			# print(f"| {host_port} | {container_port} |")
			# print(f"Host port: {host_port}\nContainer port: {container_port}")
			port_table.add_row([host_port, container_port])
		print(port_table)
		manage_container_ports(container, container_index)
	elif selection == "2" or selection == "add":
		print("Changing ports will save the current container as a new image, and create a new container with the added ports from that image. The original container will be deleted.")
		host_port = input("What is the host port?\n")
		container_port = input("What is the container port?\n")
		configuration["containers"][container_index]["ports"][host_port] = container_port # For example, {8080:80}
		container = configuration["containers"][container_index] # Update container as it was changed during port addition
		save_configuration(configuration)
		rerun_container(container, container_index)
		manage_container_ports(configuration["containers"][container_index], container_index)
	elif selection == "3" or selection == "remove":
		print("Changing ports will save the current container as a new image, and create a new container with the added ports from that image. The original container will be deleted.")
		port_table = PrettyTable(["Host Port", "Container Port"]) 
		for host_port, container_port in configuration["containers"][container_index]["ports"].items():
			port_table.add_row([host_port, container_port])
		print(port_table)
		selection = input("Enter the host port which you would like to remove (both the host and container port will be removed)\n")
		configuration["containers"][container_index]["ports"].pop(selection)
		save_configuration(configuration)
		rerun_container(container, container_index)
		manage_container_ports(configuration["containers"][container_index], container_index)
	elif selection == "4" or selection == "cancel":
		manage_container(container, container_index)
	else:
		print("Invalid selection")
		manage_container_ports(container, container_index)

def manage_images():
	configuration = load_configuration()
	i = 0
	print("Select the image you want to manage:")
	for image in configuration["images"]:
		i += 1 # The same thing as i = i +1
		# print("  " + str(i) + ") " + image["name"] + " - " + image["version"] + " - " + image["ram"] + " MiB") # {space} 1) <image name> - <version> - <ram amount> MiB 
		print("  " + str(i) + ") " + image["name"]) # {space} 1) <image name>
	print("  " + str(i + 1) + ") Cancel") # At the end of the menu, add an option to cancel
	selection = input("") # Ask for input without a prompt
	if selection.isdigit(): # If the input is a digit
		selection = int(selection) #  Turn it into an integer
		if selection <= i: # If the selection is valid, aka less than i
			manage_image(configuration["images"][selection-1]) # Get the image selected and pass it to manage_image(image)
		elif selection == i+1:
			menu()
		else:
			print("Invalid selection")
			menu()

def manage_image(image):
	configuration = load_configuration()
	print("""What would you like to do with this image?
  1) REMOVE
  2) Cancel""")
	selection = input("").lower()
	if selection == "1" or selection == "remove":
		confirmation = input("Are you sure you want to remove this image? In order to do so, you must have no containers which rely on the image. If you're sure, type \"Yes, I am sure I want to do this.\"\n")
		if confirmation == "Yes, I am sure I want to do this.":
			if len(image["containers"]) == 0:
				# remove the image 
				# os.system("docker rmi " + image["name"])
				subprocess.run(["docker", "image", "rm", image["name"]])

				configuration["images"].pop(configuration["images"].index(image))
				save_configuration(configuration)
			else:
				print("You still have images which rely on this image")
	elif selection == "2" or selection == "cancel":
		manage_images()
	else:
		manage_image(image)
	# configuration = load_configuration()
	if image in configuration["images"]:
		manage_image(image)
	else:
		print("Image no longer exists")
		manage_images()
# Set up rcon 
def change_rcon_password(container):
	password = input("What would you like the password to be?\n")
	print("Editing files")
	# Get the current server_properties
	# os.system(f"docker cp {container}:/root/minecraft/server.properties ./server.properties")
	subprocess.run(["docker", "cp", container + ":/root/minecraft/server.properties", "./server.properties"])
	with open(str(pathlib.Path("server.properties").resolve()), "r") as container_config_file: # Migrate to pathlib
		container_config = container_config_file.read()
		container_config_file.close()
	new_config = re.sub(container_config, "^rcon\.password=[a-zA-Z0-9\"`'#%&,:!;\-\_\.<>=@{}~\$\(\)\*\+\/\\\?\[\]\^\|]+$", f"rcon.password={password}")
def config_rcon(container):
	# Set up rcon 
	# Request user input
	print("To remotely access the console of the Minecraft server, rcon needs to be setup\nrcon is a protcol for remotely managing game servers")
	password = input("What is the password you would like to set for rcon?\n")
	# port=input("\nWhat is the port you would like to use for rcon?\n")
	print("Editing files")
	# Read original_server.properties
	with open(str(pathlib.Path("original_server.properties").resolve()), "r") as original_config_file: # Migrate to pathlib
		original_config = original_config_file.read()
		original_config_file.close()
	new_config = original_config.replace("rcon.password=", "rcon.password="+password)
	# new_config = original_config.replace("rcon.port=25575", "rcon.port="+port)
	# Write to server.properties
	with open(str(pathlib.Path("server.properties").resolve()), "w") as server_config: # Migrate to pathlib
		server_config.write(new_config)
		server_config.close()

	# Remove server.properties
	print("Removing server.properties in container")
	# os.system(f"docker exec {container} rm -rf /root/minecraft/server.properties")
	subprocess.run(["docker", "exec", container, "rm", "-rf", "/root/minecraft/server.properties"])
	# Copy server.properties to /root/minecraft/server.properties
	print("Copying server.properties to the container")
	# os.system(f"docker cp server.properties {container}:/root/minecraft/server.properties")
	subprocess.run(["docker", "cp", "server.properties", container + ":/root/minecraft/server.properties"])
	# Restart the docker container
	print("Restarting the container")
	# os.system(f"docker restart {container}")
	subprocess.run(["docker", "restart", container])

print("To make a selection, type in the corresponding number or type in the capitalized keyword\nThen press enter\n")
menu() # Show menu