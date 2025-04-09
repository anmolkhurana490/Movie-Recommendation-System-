import pandas as pd


movies=pd.read_csv("datasets/tmdb_5000_movies.csv")
movies.dropna(subset=["release_date"], inplace=True)

#popularity depends on language but not vote_average
#plt.scatter(movies["original_language"], movies["popularity"])
#plt.scatter(movies["original_language"], movies["vote_average"])
#plt.show()

#same in case of year
year=movies["release_date"].apply(lambda date: int(date.split('-')[0]))
#plt.scatter(year, movies["popularity"])
#plt.scatter(year, movies["vote_average"])
#plt.show()

#95% movies have upto 7 production companies
#print(movies["production_companies"].apply(lambda data: len(eval(data))).quantile(0.95))
company_series=pd.Series()
#for company in movies["production_companies"]:
#	company_series=company_series._append(pd.Series(eval(company))[:7])
	
#print(company_series.value_counts())


data=pd.read_csv("datasets/processed_data.csv")

		
lang_groups=data.groupby("original_language")
for i, group in lang_groups:
	print("\n", i)
	for name in group.columns:
		if name.startswith("company") and group[name].sum():
			print(name)
			
