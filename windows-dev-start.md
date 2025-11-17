# Windows 要進本地開發模式方式
1. 安裝 C++ 套件: 
   1. https://visualstudio.microsoft.com/visual-cpp-build-tools/
   2. 勾選 Desktop development with C++（使用 C++ 的桌面開發）」 這個 workload 其他保持default
   3. 安裝好後重新啟動一個terminal
2. 終端機進入專案根目錄 `cd D:\ewe\hummingbot\hummingbot`
3. 啟動虛擬環境 (windows) `.\venv\Scripts\Activate.ps1`
4. 用symblink editable模式安裝依賴(這樣才可以即改即應用，不用重新安裝一次依賴) `pip install -e .`
5. 執行你的策略進行測`python hello-world-hyperliquid.py`
