pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
set PLAYWRIGHT_DOWNLOAD_HOST=https://registry.npmmirror.com/-/binary/playwright&& python -m playwright install chromium
cd source
python -m nuitka --standalone --onefile --windows-console-mode=force --playwright-include-browser=all --assume-yes-for-downloads --include-module=icalendar --include-module=keyring --include-module=pandas --include-module=playwright --include-module=pytz --output-filename=../SZTU_course_xls2ics.exe main.py