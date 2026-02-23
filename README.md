# wine knowledge discovery with symbolic means

Possible datasets to explore

## Rustamov E. 2023. Wine Dataset. kaggle.
[https://www.kaggle.com/datasets/elvinrustam/wine-dataset/data](https://www.kaggle.com/datasets/elvinrustam/wine-dataset/data)

A web scraped dataset of a British online wine marketplace

Features:

* Title: The name or title of the wine.
* Description: A brief textual description providing additional details about the wine.
* Price: The cost of the wine.
* Capacity: The volume or size of the wine bottle.
* Grape: The primary grape variety used in making the wine.
* Secondary Grape Varieties: Additional grape varieties used in the wine blend.
* Closure: The type of closure used for the bottle.
* Country: The country where the wine is produced.
* Characteristics: The "Characteristics" feature encapsulates the unique and discernible flavors and aromas present in a particular wine.
* Per bottle / case / each: The quantity of wine included per unit (bottle, case, or each) sold.
* Type: The general category of the wine.
* ABV: The percentage of alcohol content in the wine.
* Region: The geographic region where the grapes used to make the wine are grown.
* Style: This feature describes the overall sensory experience and characteristics of the wine.
* Vintage: The year the grapes used to make the wine were harvested.
* Appellation: A legally defined and protected geographical indication used to identify where the grapes for a wine were grown.


## Daux, V., I. Garcia de Cortazar-Atauri, P. Yiou, I. Chuine, E. Garnier, E. Le Roy Ladurie, O. Mestre, and J. Tardaguila. 2012. An open-database of Grape Harvest dates for climate research: data description and quality assessment. Climate of the Past, 8, 1403-1418. doi: 10.5194/cp-8-1403-2012
[https://www.ncei.noaa.gov/access/paleo-search/study/13194](https://www.ncei.noaa.gov/access/paleo-search/study/13194)

Grapevine (Vitis vinifera L.) harvest date information for 27 regions in France, Switzerland, Italy, Spain and Luxemburg. The 27 regional composite grape harvest date (GHD) series are derived from 380 individual vinyard locations. Harvest dates are presented as the number of days after 31 August.


## de Azambuja, R. X., Morais, A. J., & Filipe, V. (2023). X-Wines: A Wine Dataset for Recommender Systems and Machine Learning. Big Data and Cognitive Computing, 7(1), Article 20. https://doi.org/10.3390/bdcc7010020.
[https://github.com/rogerioxavier/X-Wines/tree/main/Dataset](https://github.com/rogerioxavier/X-Wines/tree/main/Dataset)

* WineID: Integer. The wine primary key identification;
* WineName: String. The textual wine identification presented in the label;
* Type: String. The categorical type classification: Red, white or rosé for still wines, gasified sparkling or dessert for sweeter and fortified wines. Dessert/Port is a sub classification for liqueur dessert wines;
* Elaborate: String. Categorical classification between varietal or assemblage/blend. The most famous blends are also considered, such as Bordeaux red and white blend,Valpolicella blend and Portuguese red and white blend;
* Grapes: String list. It contains the grape varieties used in the wine elaboration. The
original names found have been kept;
* Harmonize: String list. It contains the main dishes set that pair with the wine item. These are provided by producers but openly recommended on the internet by sommeliers and even consumers;
* ABV: Float. The alcohol by volume (ABV) percentage. According to [1], the value shown on the label may vary, and a tolerance of 0.5% per 100 volume is allowed, reaching 0.8% for some wines;
* Body: String. The categorical body classification: Very light-bodied, light-bodied, medium-bodied, full-bodied or very full-bodied based on wine viscosity [37];
* Acidity: String. The categorical acidity classification: Low, medium, or high, based on potential hydrogen (pH) score [38];
* Code: String. It contains the categorical international acronym of origin country of
the wine production (ISO-3166);
* Country: String. The categorical origin country identification of the wine production (ISO-3166);
* RegionID: Integer. The foreign key of the wine production region;
* RegionName: String. The textual wine region identification. The appellation region name wasretained when identified;
* WineryID: Integer. The foreign key of the wine production winery;
* WineryName: String. The textual winery identification;
* Website: String. The winery’s URL, when identified;
* Vintages: String list. It contains the list of integers that represent the vintage years orthe abbreviation “N.V.” referring to “non-vintage
