import pandas as pd
import matplotlib.pyplot as plt


def create_scatter_plot(df, columns):
	if len(columns) >= 2:
		plt.figure(figsize=(8, 6))
		plt.scatter(df[columns[0]], df[columns[1]])
		plt.xlabel(columns[0])
		plt.ylabel(columns[1])
		plt.title("Scatter Plot")
		return plt.gcf()
	else:
		return None
