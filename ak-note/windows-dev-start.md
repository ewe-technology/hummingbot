# Windows 要進本地開發模式方式
1. 安裝 C++ 套件: 
   1. https://visualstudio.microsoft.com/visual-cpp-build-tools/
   2. 勾選 Desktop development with C++（使用 C++ 的桌面開發）」 這個 workload 其他保持default
   3. 安裝好後重新啟動一個terminal
2. 終端機進入專案根目錄 `cd D:\ewe\hummingbot\hummingbot`
3. (若第一次建立clone完需建立虛擬環境) `python -m venv venv`
4. 啟動虛擬環境 (windows) `.\venv\Scripts\Activate.ps1`
5. 用symblink editable模式安裝依賴(這樣才可以即改即應用，不用重新安裝一次依賴) `pip install -e .`
6. 安裝我們需要的額外依賴(debug模式) `pip install -r requirements.txt`
7. 執行你的策略進行測`python ak-code\hello-world-hyperliquid.py`


# 錯誤處理: 函式庫安裝失敗
1. 如果你的python版本不是 3.12 版 (目前套件需求 >3.10 <3.14) 先安裝python 3.12 版 https://www.python.org/downloads/release/python-3120/
2. 刪除之前的虛擬環境 (powerShell) `Remove-Item -Recurse -Force .\venv`
3. 用 Python 3.12 建新的 venv `py -3.12 -m venv venv`
4. 啟動新的 venv `.\venv\Scripts\Activate.ps1`
5. `python --version` 確認這裡看到的是：Python 3.12.x
6. 接下來回到上面的第3步