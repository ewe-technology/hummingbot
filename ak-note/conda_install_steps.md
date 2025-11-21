您提到沒有 `conda` 指令,這表示您的系統上還沒有安裝 Anaconda 或 Miniconda。<cite/>讓我為您提供替代方案。

## 解決方案

### 方案一:安裝 Conda(推薦)

Hummingbot 的安裝腳本需要 Conda 來管理 Python 環境。 [1](#5-0) 安裝腳本會檢查 Conda 是否存在,如果不存在會提示您安裝。 [2](#5-1) 

**安裝 Miniconda(較輕量)**:
1. 前往 https://docs.conda.io/en/latest/    miniconda.html
2. 下載適合您作業系統的安裝程式
3. 安裝完成後,重新開啟終端機
4. 驗證安裝:`conda --version`

**安裝 Anaconda(完整版)**:
1. 前往 https://www.anaconda.com/download
2. 下載並安裝
3. 重新開啟終端機

安裝完成後,您就可以執行之前提到的步驟:
```bash
cd hummingbot
./install
```

### 方案二:使用 Python venv(不推薦,可能遇到相容性問題)

如果您不想安裝 Conda,可以嘗試使用 Python 的 venv,但這**不是官方支援的方式**,可能會遇到依賴問題:<cite/>

```bash
# 確保有 Python 3.10.12 或更高版本
python --version

# 創建虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 手動安裝依賴(需要參考 environment.yml)
pip install -r setup/pip_packages.txt
# 還需要手動安裝 environment.yml 中列出的所有套件
```

這個方法的問題是 `setup/environment.yml` 中定義了許多 Conda 特定的依賴, [3](#5-2) 您需要手動將它們轉換為 pip 安裝指令,這會非常繁瑣且容易出錯。<cite/>

### 方案三:使用 Docker(最簡單,但您之前遇到問題)

如果您能解決 Docker Desktop 的問題,這是最簡單的方式,因為不需要在本機安裝任何 Python 環境:<cite/>

```bash
# 確保 Docker Desktop 正在運行
docker version

# 啟動 Hummingbot
docker compose up -d
docker attach hummingbot
```

## 推薦做法

**強烈建議安裝 Conda**,因為:<cite/>
1. Hummingbot 的官方安裝流程完全基於 Conda [4](#5-3) 
2. CI/CD 流程也使用 Conda [5](#5-4) 
3. 環境配置檔案 `setup/environment.yml` 是為 Conda 設計的 [6](#5-5) 
4. 避免依賴版本衝突和相容性問題

## Notes

如果您在 Windows 上使用 PowerShell 並看到 `(venv)` 前綴,這表示您已經在使用某個 Python 虛擬環境。<cite/>但這不是 Conda 環境,而是 Python 的 venv。<cite/>要使用 Hummingbot 的官方安裝流程,您需要先退出這個 venv(`deactivate`),然後安裝 Conda。<cite/>

Wiki pages you might want to explore:
- [Overview (hummingbot/hummingbot)](/wiki/hummingbot/hummingbot#1)

Wiki pages you might want to explore:
- [Setup and Deployment (hummingbot/hummingbot)](/wiki/hummingbot/hummingbot#7)

### Citations

**File:** install (L6-11)
```text
if [ "${CONDA_EXE} " == " " ]; then
    CONDA_EXE=$((find /opt/conda/bin/conda || find ~/anaconda3/bin/conda || \
	    find /usr/local/anaconda3/bin/conda || find ~/miniconda3/bin/conda  || \
	    find /root/miniconda/bin/conda || find ~/Anaconda3/Scripts/conda || \
	    find $CONDA/bin/conda) 2>/dev/null)
fi
```

**File:** install (L13-16)
```text
if [ "${CONDA_EXE}_" == "_" ]; then
    echo "Please install Anaconda w/ Python 3.7+ first"
    echo "See: https://www.anaconda.com/download"
    exit 1
```

**File:** install (L48-52)
```text
if ${CONDA_EXE} env list | egrep -qe "^hummingbot"; then
    ${CONDA_EXE} env update -f $ENV_FILE
else
    ${CONDA_EXE} env create -f $ENV_FILE
fi
```

**File:** setup/environment.yml (L1-60)
```yaml
name: hummingbot
channels:
  - conda-forge
  - defaults
dependencies:
  ### Packages needed for the build/install process
  - autopep8
  - conda-build>=3.26.0
  - coverage>=7.2.7
  - cython
  - flake8>=6.0.0
  - diff-cover>=7.7.0
  - pip>=23.2.1
  - pre-commit>=3.3.3
  - python>=3.10.12
  - pytest>=7.4.0
  - pytest-asyncio>=0.16.0
  - setuptools==80.8.0
  ### Packages used within HB and helping reduce the footprint of pip-installed packages
  - aiohttp>=3.8.5
  - asyncssh>=2.13.2
  - aioprocessing>=2.0.1
  - aioresponses>=0.7.4
  - aiounittest>=1.4.2
  - async-timeout>=4.0.2,<5
  - bidict>=0.22.1
  - bip-utils
  - cachetools>=5.3.1
  - commlib-py>=0.11
  - cryptography>=41.0.2
  - injective-py==1.11.*
  - eth-account>=0.13.0
  - msgpack-python
  - numpy>=1.25.0,<2
  - objgraph
  - pandas>=2.0.3
  - pandas-ta>=0.3.14b
  - prompt_toolkit>=3.0.39
  - protobuf>=4.23.3
  - psutil>=5.9.5
  - ptpython>3.0.25
  - pydantic>=2
  - pyjwt>=2.3.0
  - pyperclip>=1.8.2
  - requests>=2.31.0
  - ruamel.yaml>=0.2.5
  - rust
  - safe-pysha3
  - scalecodec
  - scipy>=1.11.1
  - six>=1.16.0
  - sqlalchemy>=1.4.49
  - tabulate>=0.9.0
  - ujson>=5.7.0
  # This needs to be restricted to <2.0 - tests fail otherwise
  - urllib3>=1.26.15,<2.0
  - web3
  - xrpl-py==4.1.0
  - yaml>=0.2.5
```

**File:** .github/actions/install_env_and_hb/action.yml (L27-31)
```yaml
    - name: Install Hummingbot
      if: ${{inputs.dependencies-cache-hit}} != 'true'
      shell: bash -l {0}
      run: |
        ./install
```
