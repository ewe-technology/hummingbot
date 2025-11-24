# MAC dev environemt setting
1.  Install Xcode Command Line Tools `xcode-select --install`
2. Install Anaconda

For macOS with Intel (x86):
``` bash
curl -O https://repo.anaconda.com/archive/Anaconda3-2024.10-1-MacOSX-x86_64.sh
bash Anaconda3-2024.10-1-MacOSX-x86_64.sh
```

For macOS with Apple Silicon (M1/M2/M3):
``` bash
curl -O https://repo.anaconda.com/archive/Anaconda3-2024.10-1-MacOSX-arm64.sh
bash Anaconda3-2024.10-1-MacOSX-arm64.sh
```
Do you wish to update your shell profile to automatically initialize conda?

-> choose yes and restart terminal

6. Clone the repository `git clone git@github.com:ewe-technology/hummingbot.git -b ak`
7. `cd hummingbot`
8. Install the environment and dependencies `./install`
9. Activate the environment `conda activate hummingbot`
10. Compile the code `./compile`
11. Install lib for custimized script `pip install -r requirements.txt`
12. Launch Hummingbot `./start`

# debug mode on Mac
1. Open VScode
2. Click Extension buttom on the left
3. Install python
4. Click the Run and Debug buttom on the left (looks like a bug)
5. add configuration
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Attach to Hummingbot",
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
6. Click the Green play buttom left of Attach to Hummingbot
7. and then if you uncomment this section, it will stop at the break point that you set on the VScode
```python
        # 如果要 debugpy，在這裡放
        import debugpy

        debugpy.listen(("0.0.0.0", 5678))
        self.logger().info("🐞 Debugger waiting... Attach with VSCode.")
        # 這行會讓 HBOT 停在這裡，直到 VSCode attach
        debugpy.wait_for_client()
```
