# Windows dev environemt setting with WSL2 Ubuntu
1. Install WSL2 and Ubuntu `wsl --install -d Ubuntu`
2. Install/Update System Packages `sudo apt update && sudo apt upgrade -y && sudo apt install -y gcc build-essential`
3. Install Anaconda
4. `curl -O https://repo.anaconda.com/archive/Anaconda3-2025.06-0-Linux-x86_64.sh`
5. `bash ./Anaconda3-2025.06-0-Linux-x86_64.sh`
6. Clone the repository `git clone git@github.com:ewe-technology/hummingbot.git -b ak`
7. `cd hummingbot`
8. Install the environment and dependencies `./install`
9. Activate the environment `conda activate hummingbot`
10. Compile the code `./compile`
11. Install lib for custimized script `pip install -r requirements.txt`
12. Launch Hummingbot `./start`

# debug mode on Ubuntu
1. Click the button in the bottom left corner of VScode. Looks like ><
2. Click Extension buttom on the left
3. Install python
4. Choose connect to WSL
5. Click the Run and Debug buttom on the left (looks like a bug)
6. add configuration
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Attach to Hummingbot (WSL)",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "justMyCode": false
        }
    ]
}
```
8. Click the Green play buttom left of Attach to Hummingbot(WSL)
9. and then if you uncomment this section, it will stop at the break point that you set on the VScode
```python
        # 如果要 debugpy，在這裡放
        import debugpy

        debugpy.listen(("0.0.0.0", 5678))
        self.logger().info("🐞 Debugger waiting... Attach with VSCode.")
        # 這行會讓 HBOT 停在這裡，直到 VSCode attach
        debugpy.wait_for_client()
```
