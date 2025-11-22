這個錯 不是你環境壞掉，而是：
pysha3 這個套件太老了，不支援 Python 3.13，所以在編譯 C 擴充時爆炸。

關鍵在這幾行：

creating build\lib.win-amd64-cpython-313
...
fatal error C1083: 無法開啟包含檔案: 'pystrhex.h': No such file or directory
...
Failed to build pysha3
error: failed-wheel-build-for-install
× Failed to build installable wheels ... → pysha3


pysha3 本來是給 Python 2.7–3.5 用的舊版 backport，官方也已經宣告 EOL。
piwheels.org
+1

現在你在 Python 3.13 的 conda 環境裡裝它，就會因為少了舊版 CPython 的 header 檔 (pystrhex.h) 而編譯失敗。

eip712-structs 這個套件又強制依賴 pysha3，所以整個 pip install -r setup/pip_packages.txt 就卡住了。
piwheels.org

✅ 最實際的解法（建議你採用）

不要在 Python 3.13 上跑這個 Hummingbot env，改用 3.10（或 3.11/3.12），問題就會消失。
Hummingbot 官方目前是說「Python 3.10+」，但是這條依賴鏈還沒跟上 3.13。
hummingbot.org
+1

直接幫你排好指令（在 PowerShell）：

1️⃣ 新建一個專門給 Hummingbot 用的 3.10 環境
# 關掉現在這個 3.13 env（如果還在）
conda deactivate

# 建一個 python 3.10 的環境（名字你可以改）
conda create -n hummingbot310 python=3.10 -y

# 啟用新的環境
conda activate hummingbot310


確認一下：

python --version
# 應該要看到類似：Python 3.10.x

2️⃣ 在新環境裡重新裝 Hummingbot 依賴
cd D:\ewe\hummingbot\humming-bot-env3-conda\hummingbot

pip install -r setup/pip_packages.txt


這次 pysha3 就不會再噴 pystrhex.h 的錯了（因為在較舊的 Python 版本上，它還能編過）。

❌ 不建議走的硬幹路線（給你參考）

理論上可以：

改用 safe-pysha3（支援 Python 3.9–3.13 的新版 SHA-3 套件）
pypistats.org

或改用 eip712-structs-ng（宣稱是 eip712-structs 的現代替代版本）
SOOS

但這需要你去改 setup/pip_packages.txt，甚至要 patch Hummingbot 的 import 行為，維護成本高，而且未必每個地方都測過。

就你現在的目標來說，直接用一個乾淨的 python=3.10 conda 環境是最快、最穩的解。

總結一下你現在要做的事

用 conda create -n hummingbot310 python=3.10 新建環境

conda activate hummingbot310

回到 Hummingbot 專案目錄，重跑 pip install -r setup/pip_packages.txt

之後 Hummingbot 都用這個 hummingbot310 環境啟動

如果你等一下也想一起把「啟動 hummingbot / attach debugger / 多 Python 版本切換」都整理成一套標準流程，我可以幫你寫一份完整 step-by-step。
