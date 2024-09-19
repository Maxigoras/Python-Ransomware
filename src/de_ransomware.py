#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
@brief: 解密 Windows 上的个人文件
"""

from en_de_cryptor import CallMsgBox, En_De_cryptFile
import ctypes


"""请填写你的解密密钥"""
g_key_val = b''


def main():
	global g_key_val
	
	# 如果此脚本没有管理员权限
	is_admin = ctypes.windll.shell32.IsUserAnAdmin()
	if is_admin != 1:
		CallMsgBox(1, "Error", "Try To Re-Run As Administrator")

	# 解密
	else:
		flag = En_De_cryptFile(2, g_key_val)
		
		if flag == True: CallMsgBox(2, "Successful", "Your files has been decrypted")
		else: CallMsgBox(1, "Error", "The key is invalid")

if __name__ == '__main__':
	main()
