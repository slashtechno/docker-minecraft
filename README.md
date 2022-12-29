# Docker-Minecraft
#### Easily use Docker to deploy a basic Minecraft server  
### Requirements
* [Basic knowledge](https://www.youtube.com/watch?v=eGz9DS-aIeY) of Docker (not needed, but recommended)
* Docker
* ~~Linux~~ This should now work on Linux, Windows (Docker Desktop can utilize WSL), and MacOS

### To use  
1. Clone the repo with `git clone https://github.com/slashtechno/docker-minecraft/`
2. Change to the directory with `cd docker-minecraft`. 
3. Install dependencies with `pip install -r requirements.txt` (`pip3` may need to be used instead)  
4. Run the script with `python3 server-manager.py` (you may need to use `python` instead of `python3`, and `sudo` may be required)  
Done!  
### Credits  
* [@Glitch752](https://github.com/glitch752)

### Roadmap  
- [X] Migrate from `os.system` to `subprocess.run` 
- [X] Allow port changes (save current container as an image, and run image with new ports)  
- [X] Use `pathlib` library  
- [X] Possibly migrate to the Docker API or [Python on Whales](https://github.com/gabrieldemarmiesse/python-on-whales)  
    - [ ] Check names of **all** existing containers and images when a new container or image is being created  
    - [ ] Instead of relying on container and image names, rely on the IDs (could be possible without the Docker API)  
- [ ] Allow name changes to containers and images
- [ ] Switch to [`docker export`](https://docs.docker.com/engine/reference/commandline/export/)
