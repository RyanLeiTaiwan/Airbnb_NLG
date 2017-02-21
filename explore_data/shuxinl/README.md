### usage:

To install all the required Python dependencies needed in this tutorial, you need to run this command in the cloned directory:

    pip install -r requirements.txt

To install the spaCy model you need to run: (takes 1.3 GB)

    sputnik --name spacy --repository-url http://index.spacy.io install en==1.1.0

To generate imtermidiate data:

	python generateData.py [city]

To find name entities, especially LOC, FAC, GPE, ...

	python findNameEntites.py [city] [neighbourhood]

To find adj which describe neighbourhood:

	python findAdj.py [city] [neighbourhood] [keyword]

To generate heatmap for one city:

	python findKeywordsInCity.py [city]
	
For example:

	python generateData.py Boston
	python findNameEntites.py Boston Brighton
	python findAdj.py Boston Brighton
	python findKeywordsInCity.py Boston
