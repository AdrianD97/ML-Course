from pyspark import SparkConf, SparkContext
from pyspark.mllib.feature import HashingTF
from pyspark.mllib.feature import IDF

# Boilerplate Spark stuff:
conf = SparkConf().setMaster("local").setAppName("SparkTFIDF")
sc = SparkContext(conf = conf)

# Load documents (one per line).
rawData = sc.textFile("subset-small.tsv")
# print(rawData.take(1))

fields = rawData.map(lambda x: x.split("\t")) # 12	Anarchism	2008-12-30 06:23:05	Anarchism ...
# print(fields.take(1))
documents = fields.map(lambda x: x[3].split(" "))
# print(documents.take(1))

# Store the document names for later:
documentNames = fields.map(lambda x: x[1])
# print(documentNames.collect())

# Now hash the words in each document to their term frequencies:
hashingTF = HashingTF(100000)  #100K hash buckets just to save some memory
tf = hashingTF.transform(documents)
# print(tf.take(2))

# At this point we have an RDD of sparse vectors representing each document,
# where each value maps to the term frequency of each unique hash value.

# Let's compute the TF*IDF of each term in each document:
tf.cache()
idf = IDF(minDocFreq=2).fit(tf)
tfidf = idf.transform(tf)
# print(tfidf.take(1))

# Now we have an RDD of sparse vectors, where each value is the TFxIDF
# of each unique hash value for each document.

# I happen to know that the article for "Abraham Lincoln" is in our data
# set, so let's search for "Gettysburg" (Lincoln gave a famous speech there):

# First, let's figure out what hash value "Gettysburg" maps to by finding the
# index a sparse vector from HashingTF gives us back:
gettysburgTF = hashingTF.transform(["Gettysburg"])
# print(gettysburgTF.indices)
gettysburgHashValue = int(gettysburgTF.indices[0])
# print("Gettysburg hash value: " + str(gettysburgHashValue))

# Now we will extract the TF*IDF score for Gettsyburg's hash value into
# a new RDD for each document:
gettysburgRelevance = tfidf.map(lambda x: x[gettysburgHashValue])
# print(gettysburgRelevance.collect())

# We'll zip in the document names so we can see which is which:
zippedResults = gettysburgRelevance.zip(documentNames)
# print(zippedResults.collect())

# # And, print the document with the maximum TF*IDF value:
print("Best document for Gettysburg is:")
print(zippedResults.max())
