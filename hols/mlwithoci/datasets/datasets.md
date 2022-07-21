# DataSets

Estimated Lab Time: xx minutes

There are two ways to proceed with the required datasets:
1. Basic way: download the datasets from Kaggle to proceed with the workshop. This is especially useful if you don't care about the size of the dataset / have no interest in having your own dataset stored in the Cloud. Also recommended if you haven't completed [the first workshop](../../dataextraction/) before trying this one out.
2. More extensive way: if you want to expand the basic dataset with your own players / regions, this way is recommended. For that, please refer to [this file](../../../dataextraction/optimizer/optimizer.md) from the previous workshop, where you'll find instructions on how to generate your own dataset.

Whether or not you're deciding which way to proceed, it's recommended to download Kaggle datasets, as these datasets have been processed and expanded for several iterations (weeks or months of execution), which will accelerate your data extraction and ingestion process.

Here are the official links for the Kaggle datasets:
- [Matchups](): this dataset is the one we'll use to implement our [previously mentioned](../../intro/intro.md) offline model.
- [Live Client-Compatible DataSet](): we'll use this dataset to deploy the [previously mentioned](../../intro/intro.md) online model.
- (Optional) [30.000+ Masters+ Players Dataset](https://www.kaggle.com/datasets/jasperan/league-of-legends-master-players): A collection of Riot Games API info for 30.000+ players above Master's elo. You can use this dataset to your advantage if you want a robust set of players from which to extract match statistics.


> Note: The intricacies of how we built the data structures are explained in the [previous article](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/main/articles/article2.md). It is important to remember that structuring and manipulating data in the data science process takes an average of 80 to 90% of the time, according to expert sources (image courtesy of [“2020 State of Data Science: Moving From Hype Toward Maturity.”](https://www.anaconda.com/state-of-data-science-2020)), and we shouldn't be discouraged when spending most of our time processing and manipulating data structures. The ML algorithm is the easy part if you've correctly identified the correct data structure and adapted it to the structure ML algorithms expect.

![Breakdown of effort to train model](https://raw.githubusercontent.com/oracle-devrel/leagueoflegends-optimizer/blob/main/images/lab1-anaconda_1.PNG?raw=true)



