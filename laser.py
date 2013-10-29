from __future__ import print_function
from pylab import *
import glob
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

## data, subdata = 
def read_file(filename):
	"""
		Data is used in various places within the module.  In some cases, analyte list is very long
		and needs to be truncated for easy use.  Here, common divalents are used.  Hard code as needed
		for now.  Will look into selection of check boxes using a checkbox widget in the future.
	"""
	data = pd.read_csv(filename, header=1)
	subdata = pd.read_csv(filename, header=1)
	subdata = subdata[['Ca43','Ba138','Sr88']]
	return (data, subdata)

## data, subdata =
def pick_gasblank(data, subdata):
	"""
		Gas blank is required for this type of data since it incorporates detector signal from a
		constant supply of carrier gas.  The background calculated here will be subtracted from
		actual signal given by sample.
	"""
	subdata.plot(legend=False, logy=True)
	txt = plt.title('Gas Blank - pick two points')
	xy = ginput(2,timeout=30)
	x1=xy[0][0]
	x2=xy[1][0]
	gas_blank = data.ix[x1:x2]
	plt.close("all")
	return gas_blank


def pick_data(data, subdata):
	"""
		Here, actual sample data is constrained.  In most laser ablation runs, the mass spectrometer
		is allowed to continue running until the detector returns to background levels, assuring
		complete sample cell washout.  It is therefore necessary to incorporate a constraint tool here.
	"""
	subdata.plot(legend=False, logy=True)
	txt = plt.title('Data - pick two points')
	xy = ginput(2,timeout=30)
	x1=xy[0][0]
	x2=xy[1][0]
	const_data=data.ix[x1:x2]
	plt.close("all")
	return const_data

def load_cal(filename='cal.csv'):
	"""
		
	"""
	cal = pd.read_csv(filename, skiprows=1, index_col=0)
	cali = cal.ix[:,['CPS/ppm','CPS']]
	return cali

def main():
	"""
		Main script runs here that loads each sample individually and saves each output file for later
		use.  A data combiner is not built in, since some users may not want all data in a single
		worksheet.  Double-click functionality doesn't seem to work using this method, but I may
		just not know what I'm doing yet.
	"""
	f_array = glob.glob('*.xl')
	for filename in f_array:
		data, subdata = read_file(filename)
		gas_blank = pick_gasblank(data, subdata)
		const_data = pick_data(data, subdata)
		means = gas_blank.mean()
		means['Time in Seconds '] = 0
		subt_signal = const_data - means
		cali = load_cal()
		offset = cali.iloc[:,1]
		cal_mult = cali.iloc[:,0]
		cal_signal = (subt_signal - offset)/cal_mult
		TiS = cal_signal['Time in Seconds ']
		cal_signal['Time in Seconds '] = cal_signal['Time in Seconds '] - TiS.min(0)
		cal_signal['Time in Seconds '] = cal_signal['Time in Seconds ']*15
		cal_signal = cal_signal.rename(columns={'Time in Seconds ': 'um from core'})
		df_ratios = pd.DataFrame({'um from Core' : cal_signal['um from core'],
			'Ba/Ca' : (cal_signal['Ba138']/cal_signal['Ca46'])*(40.078/137.327)*1000000,
			'Sr/Ca' : (cal_signal['Sr87']/cal_signal['Ca46'])*(40.078/87.62)*1000000,
			'Mg/Ca' : (cal_signal['Mg24']/cal_signal['Ca46'])*(40.078/24.305)*1000000})
		base, extn = filename.rsplit('.', 1)
		out_file = "%s.xls" % (base,)
		df_ratios.to_excel(out_file,sheet_name='data')
	
if __name__ == "__main__":
	main()

