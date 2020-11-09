import matplotlib.pyplot as plt
import scipy.stats as ss

x = [4.30, 4.30, 4.31, 4.31, 4.29, 4.30, 4.19, 4.19, 4.18, 4.18, 4.18, 4.19, 4.35, 4.35, 4.26, 4.26, 4.35, 4.26,
	 4.29, 4.30, 4.18, 4.17, 4.34, 4.25]
y = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]

err = [0.39, 0.39, 0.38, 0.38, 0.40, 0.39, 0.39, 0.40, 0.40, 0.39, 0.40, 0.40, 0.37, 0.37, 0.39, 0.39, 0.37, 0.39,
	   0.38, 0.38, 0.38, 0.39, 0.36, 0.38]
mean = sum(x)/len(x)
print(mean)


fig, ax = plt.subplots()
ax.errorbar(x, y, xerr=err, color="black", fmt='o', markersize=6, linewidth=1)
ax.vlines(mean, min(y)-0.5, max(y)+0.5, color="r", linestyle="--")
ax.axes.get_yaxis().set_visible(False)

plt.show()