您想了解在本地開發 script 的完整步驟。<cite/>讓我為您整理一個清晰的流程。

## 本地開發 Script 的步驟

### 方案一:從源碼運行(推薦用於開發)

#### 1. 設置開發環境

```bash
# 克隆 Hummingbot repo
git clone https://github.com/hummingbot/hummingbot.git
cd hummingbot

# 創建 Conda 環境
conda env create -f setup/environment.yml
conda activate hummingbot

# 安裝依賴
pip install -r setup/pip_packages.txt
``` [1](#4-0)

#### 2. 啟動 Gateway(如果需要 DEX 交易)

如果您的 script 需要與 DEX 交易,需要啟動 Gateway:<cite/>

**選項 A: 使用 Docker 運行 Gateway**
```bash
# 在 docker-compose.yml 中取消註解 gateway 服務
docker compose up -d gateway
``` [2](#4-1)

**選項 B: 從源碼運行 Gateway**
```bash
# 克隆 Gateway repo
git clone https://github.com/hummingbot/gateway.git
cd gateway

# 安裝並啟動
yarn install
yarn start
``` [3](#4-2)

#### 3. 配置 Gateway 連接(如果使用)

在 Hummingbot 的 `conf/conf_client.yml` 中設置:<cite/>
```yaml
gateway:
  gateway_api_host: localhost
  gateway_api_port: 15888
  gateway_use_ssl: false  # 開發模式使用 HTTP
``` [4](#4-3)

#### 4. 創建您的 Script

在 `scripts/` 目錄下創建您的策略文件,例如 `my_strategy.py`:<cite/>
```python
from hummingbot.strategy.script_strategy_base import ScriptStrategyBase

class MyStrategy(ScriptStrategyBase):
    # 您的策略邏輯
    pass
``` [5](#4-4)

#### 5. 啟動 Hummingbot 並運行 Script

```bash
# 從源碼啟動 Hummingbot
./bin/hummingbot.py

# 在 Hummingbot CLI 中
>>> start --script my_strategy.py
``` [6](#4-5)

#### 6. 開發迭代流程

每次修改 script 後:<cite/>
1. 在 Hummingbot CLI 中運行 `stop`
2. 修改您的 script 文件
3. 運行 `start --script my_strategy.py` 重新加載

**不需要重啟 Hummingbot 或 Gateway**,script 會自動重新加載。<cite/>

### 方案二:使用 Docker(適合生產環境)

如果您想使用 Docker 但仍能本地開發:

```bash
# 只啟動 Gateway
docker compose up -d gateway

# 從源碼運行 Hummingbot(不用容器)
conda activate hummingbot
./bin/hummingbot.py
```

這樣您可以直接編輯本地的 `scripts/` 目錄,無需處理容器內的文件。<cite/>

## 開發工具配置(可選)

如果使用 VS Code 或 Cursor IDE,可以配置調試環境: [7](#4-6)

創建 `.vscode/launch.json`: [8](#4-7)

## Notes

**關鍵點**:
- Script 文件存放在 `scripts/` 目錄 [9](#4-8)
- 如果只使用 CEX(中心化交易所),不需要 Gateway<cite/>
- Gateway 只在使用 DEX 連接器時需要<cite/>
- 從源碼運行比使用 Docker 更適合開發,因為可以直接修改代碼並快速測試<cite/>
- Script 配置文件(可選)存放在 `conf/scripts/` 目錄 [10](#4-9)

Wiki pages you might want to explore:
- [Overview (hummingbot/hummingbot)](/wiki/hummingbot/hummingbot#1)

### Citations

**File:** CURSOR_VSCODE_SETUP.md (L1-4)
```markdown
## VS Code/Cursor Setup Guide for Hummingbot Testing

This guide outlines how to configure VS Code or Cursor to efficiently run and debug Hummingbot tests

```

**File:** CURSOR_VSCODE_SETUP.md (L7-8)
```markdown
* **Hummingbot Repository:** You have cloned the Hummingbot repository to your local machine.
* **Conda Environment:** You have created and activated the `hummingbot` Conda environment with all necessary dependencies installed.
```

**File:** CURSOR_VSCODE_SETUP.md (L52-65)
```markdown
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Hummingbot",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceRoot}/bin/hummingbot.py",
            "console": "integratedTerminal"
        }
    ]
}
```
```

**File:** docker-compose.yml (L17-17)
```yaml
      - ./scripts:/home/hummingbot/scripts
```

**File:** docker-compose.yml (L32-44)
```yaml
  # gateway:
  #  restart: always
  #  container_name: gateway
  #  image: hummingbot/gateway:latest
  #  ports:
  #    - "15888:15888"
  #  volumes:
  #    - "./gateway-files/conf:/home/gateway/conf"
  #    - "./gateway-files/logs:/home/gateway/logs"
  #    - "./certs:/home/gateway/certs"
  #  environment:
  #    - GATEWAY_PASSPHRASE=admin
```

**File:** README.md (L178-178)
```markdown
* [Gateway](https://github.com/hummingbot/gateway): Typescript based API client for DEX connectors
```

**File:** hummingbot/client/config/client_config_map.py (L336-353)
```python
class GatewayConfigMap(BaseClientModel):
    gateway_api_host: str = Field(
        default="localhost",
        json_schema_extra={"prompt": lambda cm: "Please enter your Gateway API host"},
    )
    gateway_api_port: str = Field(
        default="15888",
        json_schema_extra={"prompt": lambda cm: "Please enter your Gateway API port"},
    )
    gateway_use_ssl: bool = Field(
        default=False,
        json_schema_extra={"prompt": lambda cm: "Enable SSL endpoints for secure Gateway connection? (True / False)"},
    )
    certs_path: Path = Field(
        default=DEFAULT_GATEWAY_CERTS_PATH,
        json_schema_extra={"prompt": lambda cm: "Where would you like to save certificates that connect your bot to "
                                                "Gateway? (default 'certs')"},
    )
```

**File:** hummingbot/client/ui/parser.py (L72-76)
```python
    start_parser = subparsers.add_parser("start", help="Start the current bot")
    # start_parser.add_argument("--log-level", help="Level of logging")
    start_parser.add_argument("--script", type=str, dest="script", help="Script strategy file name")
    start_parser.add_argument("--conf", type=str, dest="conf", help="Script config file name")

```

**File:** hummingbot/client/settings.py (L38-38)
```python
SCRIPT_STRATEGY_CONF_DIR_PATH = CONF_DIR_PATH / "scripts"
```

**File:** hummingbot/client/settings.py (L42-43)
```python
SCRIPT_STRATEGIES_MODULE = "scripts"
SCRIPT_STRATEGIES_PATH = root_path() / SCRIPT_STRATEGIES_MODULE
```
