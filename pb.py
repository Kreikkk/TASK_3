import time
import sys



def progressbar(entries, process_name="saying hello", bar_num=20):
	bars = 0
	perc = 0
	step = 0.1
	for i in range(entries):
		frac = (i+1)/entries
		progress = int(frac * bar_num)
		disp_frac = round(frac*1000)/10
		if disp_frac >= perc:
			bars = progress
			perc += step
			sys.stdout.write("{}{}|  {} {}%\r".format("#"*bars, " "*(bar_num - bars), process_name, disp_frac))

		if progress == bar_num:
			sys.stdout.write("\r{}|  {}  {}".format("#"*bar_num, process_name, "Done!\n"))


if __name__ == "__main__":
	progressbar(10000000)