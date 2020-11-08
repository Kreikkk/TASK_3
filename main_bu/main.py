import uproot
import ROOT as root

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config import *
from array import array
from matplotlib.ticker import MultipleLocator


def assemble_DF(tree):
	dataset = 	pd.DataFrame({"mJJ":			pd.Series(tree["mJJ"].array()),
							  "deltaYJJ":		pd.Series(tree["deltaYJJ"].array()),
							  "phCentrality":	pd.Series(tree["phCentrality"].array()),
							  "ptBalance":		pd.Series(tree["ptBalance"].array()),
							  "nJets":			pd.Series(tree["nJets"].array()),
							  "nLeptons":		pd.Series(tree["nLeptons"].array()),
							  "weightModified":	pd.Series(tree["weightModified"].array()),})

	return dataset


def readfile():
	signal_file = uproot.open(SIGNALPROCFNM)
	bg_file = uproot.open(BGPROCFNM)

	raw_signal_data = assemble_DF(signal_file[TREENM])
	raw_bg_data = assemble_DF(bg_file[TREENM])

	signal_data = raw_signal_data[raw_signal_data["nLeptons"] == N_LEP]
	signal_data = raw_signal_data[raw_signal_data["nJets"] > 1]

	bg_data = raw_bg_data[raw_bg_data["nLeptons"] == N_LEP]
	bg_data = raw_bg_data[raw_bg_data["nJets"] > 1]

	return bg_data, signal_data


def main(var, dataset):
	sign_data = iterational_filter(var, dataset)
	plot_set = sign_data[0]

	Bs, Ss = sign_data[1]

	ys = plot_set[1]
	xs = plot_set[0]
	max_ = 0
	ind = 0
	for i, item in enumerate(ys):
		if item > max_:
			max_ = item
			ind = i

	thrsh = xs[ind]

	peak_info = (xs[ind], max_)

	plot_sign_curve(plot_set, var, (xs[ind], max_, sum(dataset[0]["weightModified"]), sum(dataset[1]["weightModified"])))
	

	plot_eff_curve(plot_set[0], sign_data[2], var)


	bg_subset, sign_subset = dataset
	if STG[var]["sign"] == "+":

		dataset = (bg_subset[bg_subset[var] > thrsh], sign_subset[sign_subset[var] > thrsh])
		
	else:
		dataset = (bg_subset[bg_subset[var] < thrsh], sign_subset[sign_subset[var] < thrsh])

	return dataset


def iterational_filter(var, dataset):
	xs, ys, Bs, Ss, Brat, Srat = [], [], [], [], [], []
	bg_subset = dataset[0]
	sign_subset = dataset[1]

	min_, max_ = max((min(bg_subset[var]), min(sign_subset[var]))), min((max(bg_subset[var]), max(sign_subset[var])))

	cursor = min_
	
	if var != "ptBalance":
		max_ = STG[var]["max"]

	# sign = sign_subset[var]
	# bg = bg_subset[var]
	initS = sum(sign_subset["weightModified"])
	initB = sum(bg_subset["weightModified"])

	while cursor < max_:
		sign = get_response(var, cursor, sign_subset)
		bg = get_response(var, cursor, bg_subset)

		# print(cursor)
		cursor += STG[var]["step"]

		S = sum(sign["weightModified"])
		B = sum(bg["weightModified"])

		Bs.append(B)
		Ss.append(S)

		Brat.append(B/initB)
		Srat.append(S/initS)

		# print("Signal: {}, BG: {}".format(S, B))
		if B+S < 0:
			# print("WARNING!,B+S={}".format(B+S))
			continue
		xs.append(cursor)
		ys.append(S/(S+B)**0.5)

	output = (xs, ys)
	return output, (Bs, Ss), (Brat, Srat)

def plot_eff_curve(xs, ys, var):
	ysB = ys[0]
	ysS = ys[1]

	canvas = root.TCanvas("canvas", "CANVAS", 800, 800)

	xplot, yplot1, yplot2 = array("d"), array("d"), array("d")

	for x, yB, yS in zip(xs, ysB, ysS):
		xplot.append(x)
		yplot1.append(yB)
		yplot2.append(yS)


	curve1 = root.TGraph(len(xs), xplot, yplot1)
	curve2 = root.TGraph(len(xs), xplot, yplot2)

	# curve.SetLineColor(1)
	# curve.SetLineWidth(4)
	# curve.SetMarkerColor(1)
	# curve.SetMarkerStyle(3)
	# curve.SetMarkerSize(0)
	# curve.SetTitle("")
	# curve.GetXaxis().SetTitle(var)
	# curve.GetYaxis().SetTitle('Significance')
	curve1.Draw()
	curve2.Draw("SAME")
	canvas.Update()
	input()



def get_response(var, threshold, dataset):
	sign = STG[var]["sign"]

	if sign == "+":
		passed = dataset[dataset[var] > threshold]
	elif sign == "-":
		passed = dataset[dataset[var] < threshold]
	else:
		raise Exception("Inappropriate sign provided")

	return passed


def plot_sign_curve(plot_set, var, metadata):
	canvas = root.TCanvas("canvas", "CANVAS", 800, 800)

	xplot, yplot = array("d"), array("d")

	for x, y in zip(plot_set[0], plot_set[1]):
		xplot.append(x)
		yplot.append(y)

	curve = root.TGraph(len(plot_set[0]), xplot, yplot)

	curve.SetLineColor(1)
	curve.SetLineWidth(4)
	curve.SetMarkerColor(1)
	curve.SetMarkerStyle(3)
	curve.SetMarkerSize(0)
	curve.SetTitle("")
	curve.GetXaxis().SetTitle(var)
	curve.GetYaxis().SetTitle('Significance')
	curve.Draw()


	threshold = str(round(metadata[0], 2))
	peak = str(round(metadata[1], 2))
	B = str(round(metadata[2]))
	S = str(round(metadata[3]))

	text1 = "For {} signal and {} background".format(S, B)
	text2 = "events the maximum {} is".format("#frac{S}{#sqrt{S+B}}")
	text3 = "{} when cutting at {}".format(peak, threshold)
	latex = root.TLatex()
	latex.SetNDC()
	latex.SetTextSize(0.02)

	if var in ("mJJ", "deltaYJJ"):
		offset = 0
	else:
		offset = 0.65
	latex.DrawLatex(0.62, 0.87-offset, text1)
	latex.DrawLatex(0.62, 0.84-offset, text2)
	latex.DrawLatex(0.62, 0.80-offset, text3)

	canvas.SetGrid()
	canvas.Update()

	if SHOW_GRAPHS:
		input()


def error(S, B):
	BErr = B**0.5
	SErr = S**0.5

	BPart = -0.5*S*((S + B)**(-1.5))
	SPart = (S + B)**(-0.5) - 0.5*S*((S + B)**(-1.5))

	return ((SPart*SErr)**2 + (BPart*BErr)**2)**0.5


if __name__ == "__main__":
	newset = readfile()
	variables = ["deltaYJJ", "mJJ", "phCentrality", "ptBalance"]

	for var in variables:
		newset = main(var, newset)


	bg_events = np.sum(newset[0]["weightModified"])
	signal_events = np.sum(newset[1]["weightModified"])

	print(error(signal_events, bg_events))




