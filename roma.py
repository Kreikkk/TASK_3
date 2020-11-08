from time import perf_counter as timer


def main():
	st = timer()
	for i in range(1, 10000):
		for j in range(1, 10000):
			for k in range(1000):
				x = i*j + i*i - i/j
	tm = timer() - st
	return tm


if __name__ == "__main__":
	tm = main()
	print(tm)