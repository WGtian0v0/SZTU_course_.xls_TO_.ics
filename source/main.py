from processor import process_all
from utils import get_course_online,save_account,get_account
import os
if __name__ == '__main__':
    def choose(is_save_account=False) -> tuple[bool, str]:
        """
        选择
        1-从网页获取课表并转换
        2-直接转换本地文件
        00-调试网页模式
        检测到输入00,打开调试并重新询问
        任意输入-使用保存的账户密码获取课表并转换(如果还未有保存的密码，则隐藏此项，如果用户输入其他内容，则提示重新输入)
        """
        is_choose = False
        if is_save_account:
            choice = input(
                "请选择操作：\n1-从网页获取课表并转换\n2-直接转换本地文件\n00-打开/关闭调试网页模式\n(其他任意输入)-使用保存的账户密码获取课表并转换\n")
        else:
            choice = input("请选择操作：\n1-从网页获取课表并转换\n2-直接转换本地文件\n00-打开/关闭调试网页模式\n")
        # 检测合法性
        if is_save_account and choice not in ['1', '2', '00']:
            is_choose = True
            return is_choose, choice
        else:
            if choice == '1' or choice == '2':
                is_choose = True
            return is_choose, choice

    def process_all_from_web(account: str, password: str, headless: bool, download_path: str) -> None:
        status, msg, file_path = get_course_online(account, password, headless, download_path)
        if not status:
            print(f"{msg},请检查你的网络环境以及账号密码。")
        else:
            process_all(file_path)



    is_choose = False
    debug = False
    is_saved_account, saved_account, saved_password = get_account()
    while not is_choose:
        #清屏
        os.system('cls' if os.name == 'nt' else 'clear')
        if debug:
            print("调试网页模式已开启")
        is_choose, choice = choose(is_saved_account)
        if choice == '00':
            debug = not debug

    download_path = "./"
    headless = not debug

    match choice:
        case '1':
            account = input("请输入您的学号：")
            password = input("请输入您的密码：")
            process_all_from_web(account, password, headless, download_path)
            answer = input("是否保存账户密码以便下次使用？(y/n)：")
            if answer.lower() == 'y':
                save_account(account, password)
                print("账户密码已保存。")
        case '2':
            file_path = input("请输入本地文件路径（含文件名及后缀）：")
            process_all(file_path)

        case _:
            process_all_from_web(saved_account, saved_password, headless, download_path)

    input('操作完成，按回车键退出...')
