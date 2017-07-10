#!/usr/bin/python
import Tkinter as tk
import os, sh, time
import ntpath, stat
import threading, shutil
import Queue

class PiCopy(tk.Frame):
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.grid()

		self.frame = tk.Frame(self)		
		self.frame.pack_propagate(0)
                self.frame.pack(fill=tk.BOTH, expand=tk.TRUE)
		self._init_display()

	def _init_display(self):
		self.source_frame = tk.Frame(self.frame, width=220, height=160, bd=3, relief=tk.RAISED)
		self.source_frame.grid_propagate(0)
		self.dest_frame = tk.Frame(self.frame, width=220, height=160, bd=3, relief=tk.RAISED)
                self.dest_frame.grid_propagate(0)

		self._display_storage_selection()

		source_text = tk.Label(self.source_frame, text='select source')
                source_text.grid(row=0, column=0, padx=5, pady=5)
                dest_text = tk.Label(self.dest_frame, text='select destination')
                dest_text.grid(row=0, column=0, padx=5, pady=5)

		self.reset_btn = tk.Button(self.frame, text='reset', command=lambda: self._reset_options(), bd=3, relief=tk.RAISED)
                self.submit_btn = tk.Button(self.frame, text='confirm selection', command=lambda: self._display_confirmation(), bd=3, relief=tk.RAISED)

		quit_btn = tk.Button(self.frame, text='quit', command=self.frame.quit, bd=3, relief=tk.RAISED)
                quit_btn.grid(row=1, column=1, ipadx=15, ipady=15, padx=10, sticky=tk.SE)

		self._populate_drive_list()

	def _display_storage_selection(self):
                self.source_frame.grid(row=0, column=0, padx=10, pady=10)
                self.dest_frame.grid(row=0, column=1, padx=10, pady=10)

	def _populate_drive_list(self):
		self.storage_drives = []
		for mounted_name in (next(os.walk("/media/pi"))[1]):
			mount_stats = sh.tail(sh.df("-h","/media/pi/"+mounted_name),"-1")
			filtered_stats = filter(None, mount_stats.split(' '))
			display_name=filtered_stats[1]+"\n------\n"+mounted_name
			
			source_storage = tk.Button(self.source_frame, text=display_name, command=self._create_callback_lambda(mounted_name, 'source'))
                        dest_storage = tk.Button(self.dest_frame, text=display_name, command=self._create_callback_lambda(mounted_name, 'dest'))
			
			source_storage_obj = StorageClass(filtered_stats[1], mounted_name, source_storage, 'source')
			dest_storage_obj = StorageClass(filtered_stats[1], mounted_name, dest_storage, 'dest')	
			self.storage_drives.append(source_storage_obj)
			self.storage_drives.append(dest_storage_obj)

		source_row_count=1
		dest_row_count=1
		for storage_drive in self.storage_drives:
			if storage_drive.locale == 'source':
				storage_drive.button.grid(row=source_row_count, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
				source_row_count+=1
			elif storage_drive.locale == 'dest':
				storage_drive.button.grid(row=dest_row_count, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
				dest_row_count+=1

	def _create_callback_lambda(self, mounted_name, locale):
		return lambda: self._button_select(mounted_name, locale)
	
	def _button_select(self, mounted_name, locale):
		reverse_locale_name = ''
		for storage_drive in self.storage_drives:
			if locale == 'dest' and storage_drive.locale == 'source' and storage_drive.button_selected:
				reverse_locale_name = storage_drive.mounted_name
			elif locale == 'source' and storage_drive.locale == 'dest' and storage_drive.button_selected:
				reverse_locale_name = storage_drive.mounted_name
		
		if mounted_name != reverse_locale_name:
			for storage_drive in self.storage_drives:
				if storage_drive.locale == locale:
					if storage_drive.mounted_name == mounted_name:
						storage_drive.button.configure(bg = 'light green')
						storage_drive.set_button_selected(True)
					else:
						storage_drive.button.configure(bg = 'light gray')
						storage_drive.set_button_selected(False)
		self._check_values_selected()
	
	def _check_values_selected(self):
		source_selected = False
		dest_selected = False
		error = False
		for storage_drive in self.storage_drives:
                        if storage_drive.locale == 'dest':
                                if not dest_selected and storage_drive.button_selected:
                                        dest_selected = True
                                elif dest_selected and storage_drive.button_selected:
                                        error = True
                        elif storage_drive.locale == 'source':
                                if not source_selected and storage_drive.button_selected:
                                       source_selected = True
                                elif source_selected and storage_drive.button_selected:
                                        error = True
		if error:
			print('error found in btn validation')
		elif dest_selected and source_selected:
                        self._display_submit()
                elif not dest_selected or not source_selected:
                        self.submit_btn.grid_forget()

                if dest_selected or source_selected:
                        self._display_reset()
                elif not dest_selected and not source_selected:
                        self.reset_btn.grid_forget()

	def _display_submit(self):
		self.submit_btn.grid(row=1, column=0, ipadx=15, ipady=15, padx=10, sticky=tk.SW)

	def _display_reset(self):
		self.reset_btn.grid(row=1, column=1, ipadx=15, ipady=15, padx=10, sticky=tk.SW)

	def _reset_options(self):
                for storage_drive in self.storage_drives:
                        storage_drive.button.configure(bg ='light gray')
                        storage_drive.set_button_selected(False)
                self._check_values_selected()

	def _display_confirmation(self):
		self._hide_storage_selection()

		self.center_frame = tk.Frame(self.frame, width=440, height=160, bd=3, relief=tk.RAISED)
                self.center_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E)
                self.center_frame.grid_propagate(0)

		self.source_drive = self._find_drive_by_location('source')
		self.dest_drive = self._find_drive_by_location('dest')

		source_text = self.source_drive.size+'-'+self.source_drive.mounted_name
                destination_text = self.dest_drive.size+'-'+self.dest_drive.mounted_name
                confirmation_label = tk.Label(self.center_frame, text='copy from:: '+source_text+' to '+destination_text)
                confirmation_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

		self.confirm_copy_btn = tk.Button(self.center_frame, text='confirm', bg='red', width=20, height=5, command=lambda: self._confirm_confirmation())
                self.cancel_copy_btn = tk.Button(self.center_frame, text='cancel', bg='light green', width=20, height=5, command=lambda: self._cancel_confirmation())
                self.confirm_copy_btn.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
                self.cancel_copy_btn.grid(row=1, column=1, padx=5, pady=5, sticky=tk.E)

	def _hide_storage_selection(self):
		self.source_frame.grid_forget()
                self.dest_frame.grid_forget()
                self.reset_btn.grid_forget()
                self.submit_btn.grid_forget()

	def _find_drive_by_location(self, locale):
                for storage_drive in self.storage_drives:
                        if storage_drive.locale == locale and storage_drive.button_selected:
                                return storage_drive

	def _cancel_confirmation(self):
		self.center_frame.grid_forget()
		self._display_storage_selection()
		self._check_values_selected()

        def _confirm_confirmation(self):
		self.confirm_copy_btn.grid_forget()
		self.cancel_copy_btn.grid_forget()
		self._create_destination_directory()
		self._copy_setup()
		
	def _create_destination_directory(self):
		folder_name = time.strftime('%m_%d_%y_%H_%M_%S', time.localtime())
                self.dest_dir = '/media/pi/'+self.dest_drive.mounted_name+'/'+folder_name
                if not os.path.exists(self.dest_dir):
                        os.makedirs(self.dest_dir)

	def _copy_setup(self):
		self.progress_var = tk.DoubleVar()
		progress_bar = tk.Scale(self.center_frame, length=400, orient=tk.HORIZONTAL, from_=0.0, to=100.0, resolution=0.1, tickinterval=20.0, variable=self.progress_var, label='progress')
		progress_bar.grid(row=1, column=0, padx=5, pady=0, columnspan=2)
		self.start_button = tk.Button(self.frame, text='begin copy', command=self._begin_copy, bg='light green', bd=3, relief=tk.RAISED)
		self.start_button.grid(row=1, column=0, ipadx=15, ipady=15, padx=10, sticky=tk.SW)

	def _begin_copy(self):
		self.start_button.grid_forget()
                file_copy_list = []
		source_dir = '/media/pi/'+self.source_drive.mounted_name
                for root_dir, dirs, files in os.walk(source_dir):
                        for file in files:
                                file_copy_list.append(root_dir+'/'+file)

		source_size = self._measure_file(source_dir)

		self.queue = Queue.Queue()
		SizeTracker(self.queue, source_size, self.dest_dir).start()
		self.master.after(5, self._check_size)

                self.file_copy_number = len(file_copy_list)
		for file_path in file_copy_list:
			dir_path = os.path.dirname(os.path.realpath(file_path))
       	        	neutral_dir = dir_path.replace(source_dir,'')
			if not os.path.isdir(self.dest_dir+neutral_dir):
               	        	os.makedirs(self.dest_dir+neutral_dir)
               	        file_name = ntpath.basename(file_path)

		copy_thread_class = CopyThread(source_dir, self.dest_dir, file_copy_list)
                copy_thread_class._copy_controller()
			
	def _check_size(self):
		try:			
			percent_complete = self.queue.get(0)
                        self.queue.queue.clear()
                        self.progress_var.set(percent_complete)
			if percent_complete < 100:
                        	self.master.after(5, self._check_size)
			else:
				print 'over 100, done'
		except Queue.Empty:
			self.master.after(5, self._check_size)

	def _measure_file(self, file_dir):
		total_size = 0
		for dirpath, dirnames, filenames in os.walk(file_dir):
			for f in filenames:
				fp = os.path.join(dirpath, f)
				total_size += os.path.getsize(fp)
		return total_size

class SizeTracker(threading.Thread):
	def __init__(self, queue, source_size, dest_dir):
		threading.Thread.__init__(self)
		self.queue = queue
		self.source_size = source_size
		self.dest_dir = dest_dir

	def run(self):
		self.check_size = True
		while self.check_size:
                        dest_size = self._measure_file(self.dest_dir)
                        percent_complete = (100.0 * float(dest_size) / float(self.source_size))
                        self.queue.put(percent_complete)
                        if not percent_complete < 100:
		        	self.check_size = False
	
	def _measure_file(self, file_dir):
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(file_dir):
                        for f in filenames:
                                fp = os.path.join(dirpath, f)
                                total_size += os.path.getsize(fp)
                return total_size

		

class StorageClass():
	def __init__(self, size, mounted_name, button, locale):
		self.size = size
		self.mounted_name = mounted_name
		self.button = button
		self.locale = locale
		self.button_selected = False
	
	def size(self):
		return self.size

	def mounted_name(self):
		return self.mounted_name

	def button(self):
		return self.button

	def locale(self):
		return self.locale

	def set_button_selected(self, button_selected):
		self.button_selected = button_selected

	def button_selected(self):
		return self.button_selected

class CopyThread():
	def __init__(self, source_dir, dest_dir, file_copy_list):
		self.source_dir = source_dir
		self.dest_dir = dest_dir
		self.file_copy_list = file_copy_list

	def _copy_controller(self):
		maxthreads = 5
		self.sema = threading.Semaphore(value=maxthreads)
		threads = list()

		self.files_completed = 0
		self.total_file_count = len(self.file_copy_list)		

		x = 0
		for file_path in self.file_copy_list:
			x += 1
			dir_path = os.path.dirname(os.path.realpath(file_path))
                        neutral_dir = dir_path.replace(self.source_dir,'')
                        file_name = ntpath.basename(file_path)
			ct = threading.Thread(target=self._copy_thread, args=(x, self.source_dir+neutral_dir, self.dest_dir+neutral_dir, file_name,))
                	threads.append(ct)
			ct.start()

        def _copy_thread(self, x, source_dir, dest_dir, file_name):
		self.sema.acquire()
		print 'starti :'+str(x)
		file_source = source_dir+'/'+file_name
                file_dest = dest_dir+'/'+file_name
		shutil.copy2(file_source, file_dest)
		self.sema.release()
		self.files_completed += 1
		print 'finish :'+str(x)
		print 'total  :'+str(self.files_completed)+'/'+str(self.total_file_count)

piCopy = PiCopy()
piCopy.mainloop()
