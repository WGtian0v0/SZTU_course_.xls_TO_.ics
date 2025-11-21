pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
set PLAYWRIGHT_DOWNLOAD_HOST=https://registry.npmmirror.com/-/binary/playwright&& python -m playwright install chromium
python source/main.py