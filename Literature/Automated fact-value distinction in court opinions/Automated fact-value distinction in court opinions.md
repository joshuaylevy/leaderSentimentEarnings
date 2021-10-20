# Title: Automated fact-value distinction in court opinions
##### Author(s): Yu Cao, Elliott Ash, Daniel Chen
##### Year: 2020
##### Journal: _European Journal of Law and Economics_

Abstract: This paper studies the problem of automated fact statements and value statements in written judicial decisions. We compare a range of methods and demonstrate that the linguistic features of sentences and paragraphs can be used to successfully classify them along this dimension. The Wordscores method by Laver et al. (Am Polit Sci Rev 92(7):311-331, 2003) performs best in held out data. In application, we show that the value segments of opinions are more informative than fact segments of the ideological direction of U.S. circuit court opinions.

URL/DOI:  https://doi.org/10.1007/s10657-020-09645-7

### Research question:
How can factual statements be separated and/or classifed from ethical/legal/normative/value statements in written legal opinions? Will answering this question help us answer questions about the way judges reach their decisions?

### Data:

Corpus of text "compromises the full set of judicial opinions from CourtListener.com, spanning over a wide range of U.S. courts and years. This corpus includes 216 courts and the corpus goes back to the 1800s for some courts"
- Using a combination of expert labelling (i.e. the judges who wrote the opinions) and a set of baseline "ground-truth" section-headers using a dictionary of words to identify such sections (see Table 1, page 457)

SAMPLE SIZE: 1,301,609 paragraphs.
- 36.5% fact-bound, 63.5% value-bound
	- Imbalance due to more section headers have value-laden words (see Table 1)
- 80% training set, 20% test set
	- Because of the cost of using NLP to do the dependency parsing, 1000 grafs from each class are randomly sampled to be used in the supervised learning stage.

### Relevant Literature:
- "Smith (2014) shows that judges are more likely to exercise policy preference in legal disputes focusing more on interpretations of legal principles."
	- See [[]]


Other attempts/methods for solving this problem:
- "In Smith (2014), a list of terms highly indicative factual statements are and a list of terms highly indicative of legal statements rae manually created based on a statistical anlaysis of 142 annotated opinions drawn from _United States Courts of Appeals Database_ ... For a given opinion, a function of the _standardized freqencies_ (see Appendix 1 for details) of the terms in each list ist aken as a quantitative measure of the extent to which the opinion concerns the kind of statements the respective list pertains to."
	- See [[]]
- "Similarly, applying Laver et al.'s (2003) _Wordscore_ algorithm, Sarel and Demirtas (2017) use two dictionaries, _Black's Law Dictionary_ as an index of legal texts and _The Oxford Thesaurus_ as an index of factual texts, to calculate a score of a given text that measures its legality or factuality. The score in question sums up the precalculated scores of the bigram sin the respective dictionaries, weighted by their frequency."
	- See [[]]
	- See [[]]
- "To date, the only study in this area that sets accurate classification as its primary goal is Shulayeva et al. (2017), where the authors adopt the standard featural representation of texts and train their naive Bayesian classifier on 2569 annotated sentences collected from 50 common law reports at the British and Irish Legal Information Institute (BAILII). Shulayeva et al.'s model employs a wide range of features besides unigrams, including part of speech tags, dependency pairs, sentence length, sentence position, and a Boolean feature that indicates whether the sentence contains a citation instance."
	- See [[]]

### Hypothesis and setup:

"Normative propositions are by nature factual propositions embedded under _modalities_ or _propositional attitudes_ ... which are encoded in English with modals, e.g., _can, may, must, should,_ etc., and attitude verbs, e.g., _believe, uphold, maintain, require,_ etc., respectivley. The above linguistic observation, we emphasize app,lies to English language in general and judicial opinions in particular."
- E.g. "The principle __established__ has also been __affirmed__ by so many decisions in the courts of New Jersey, that it __may__ now be considered as the settled law of that state. "

The "dependency features" method apparently has better syntatctic pick-up than word-pairs (bigrams) because it's more general...
- See [[Automated fact-value distinction in court opinions#^83e8f9]]

Unit of linguistic analysis is the paragraph as "our intuition is that readers can better determine whether a paragraph is about facts or values that they can do with either a single sentence, whose interpretations is susceptible to those surrounding it, or a longer document, which may consist of paragraphs pertinent to both facts and values."

### Headline results:

![[Automated fact-value distinction - FIG 2.PNG]]
These are the headline results. DEPN represents this paper's methodology (note that methodology does not perform as well as the Wordscore method). The F1 score is a measure of how well the model performs on the test set.

Disagreement analysis: "we inspect on the judicial documents on which the classification predictions by the previous models vary ... We retrained the \[first\] four models on a larger fraction of the training-development set, comprising 10,000 fact instance and 10,000 value instance and had them tested against 100 examples (50% facts, 50% values) randomly sampled from the test set. " See the degree of agreement in Table 3 below: 
![[Automated fact-value distinction - FIG 3.PNG]]
- There are some examples of the kind of text upon which there was disagreement on page 461

"As our fact-value classification model (depn) has achieved a reasonable precision and sensitivity, it would be beneficial to see how its predictions could be put to practical use ... here we are interested in whether the conservative or liberal inclination of a court opinion finds a stronger coorelation in the way it describes facts or the way it states values (i.e. applies legal principles). Conceivably our hypothesis goes to the latter, since we do not expect judges' conservative or liberal policy preference to influence their accounts of facts." See Table 4 below for results:
![[Automated fact-value distinction - FIG 4.PNG]]
- "While the absolute perforamnce is not great, a classifier using value-weighted _n_-gram representations does perform better in distinguishing liberal-inclined decisions and conservative-inclined decisions. This confirms our expectation that the value sections of a court opinion can better predict its liberalness or conservativeness."

### Important fIgures/viz:

^918787

![[Automated fact-value distinction - FIG 1.PNG]]
Sentence diagram identifying syntactic dependencies ^83e8f9


### Concepts, models & tags:
- #Law_and_Economics
	- #Courts
- #Methods
- #Natural_Language_Processing
	- #Sentiment_analysis
- #Author/DanielChen
- #Author/YuCao
- #Author/ElliottAsh

### BibTeX and other citation information:
- As it should appear in APA: 
- BibTeX key: @article{cao2020auomated,
 title={Automated fact-value distinction in court opinions},
 author={Cao, Yu and Ash, Elliott, and Chen, Daniel L.},
 journal={European Journal of Law and Economics},
 volume={50},
 number={},
 pages={451--467},
 year={2020},
 publisher={}
},