# Docker-Minecraft
#### Easily use Docker to deploy a basic Minecraft server  
### Requirements
* [Basic knowledge](https://www.youtube.com/watch?v=eGz9DS-aIeY) of Docker
* Docker
* Linux

### To use
1. Clone the repo with `git clone https://github.com/slashtechno/docker-minecraft/`
2. Change to the directory with `cd docker-minecraft`
3. Create Docker image with `docker build -t docker-minecraft .`
4. Create container with `docker run -t -d -p 25565:25565 --name docker-minecraft-container docker-minecraft`  
  a. You can change the port that the server uses (outside of the container) by changing the first occurence of 25565.  
Done!

### Access Console  
#### Configure rcon  
In order to access the console of the server, rcon must be set up.  
Run `config-rcon.py`, to do this, make sure you are in the cloned repository and run it with Python.  
This can be accomplished with `python3 config-rcon.py`
#### Connect to the console  
While there are many rcon clients, one popular client is [mcrcon](https://github.com/Tiiffi/mcrcon) (other clients should work however)  
Install `mcrcon` by following the instructions on the [mcrcon Github repository](https://github.com/Tiiffi/mcrcon)  
If you are on the same computer as the server is running, run the following    
`mcrcon -H localhost -P <port you set> -p <password you set> -t`  
If you are on a diffrent computer, you can run the same command except you need to replace localhost with the server address

### RAM Limitations  
When experimenting with running a Minecraft server in Docker on my Raspberry Pi with 4 gigabytes of RAM, I noticed some limitations.  
One of these was the container consuming too much RAM, to fix this, I decreased the amount of RAM allocated to the Minecraft server.  
If you have less than 4 gigabytes of RAM, you may need to edit the Dockerfile. If you have more, you may prefer to increase the amount of RAM allocated.  
#### Change the amount of RAM allocated  
To change the amount of maximum RAM allocated change the numbers immediately after -Xmx and add `G` for migabytes or `M` for megabytes.  
To change the amount of minimum RAM allocated change the numbers immediately after -Xms and add `G` for migabytes or `M` for megabytes.  
