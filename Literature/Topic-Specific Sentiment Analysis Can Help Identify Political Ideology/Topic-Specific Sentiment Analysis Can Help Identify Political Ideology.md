# Title: Topic-Specifc Sentiment Analysis Can Help Identify Political Iedology
##### Author(s): Sumit Bhatia, Deepak Padmanabhan
##### Year: 2018
##### Journal: *arXiv Preprint*

Abstract: Ideological leanings of an individual can often be gauged by the sentiment one expresses about different issues. We propose a simple framework that represents a political ideology as a distribution of sentiment polarities towards a set of topics. This representation can then be used to detect ideological leanings of documents (speeches, news articles, etc.) based on the sentiments expressed towards different topics. Experiments performed using a widely used dataset show the promise of our proposed approach that achieves comparable performance to other methods despite being much simpler and more interpretable.

URL/DOI: [https://arxiv.org/abs/1810.12897](https://arxiv.org/abs/1810.12897)

### Research question: 
Is it possible to use to detect the left-right ideological bias of a document based on the sentiment it expressed with respect to a set of known topics.

### Data:
- A corpus of US Congressional debates curated by Thomas et al. (2006)
	- See [[]]
	- All floor-debates in the House of Representatives in 2005,
	- Each document also has the political affiliation of the speaker
	- ![[Topic-Specific Sentiment Analysis Can Help Identify Political Ideology TAB 1.png]]

### Relevant Literature:
- **Political Ideology Detection:** Past work has tried to identify ideological leaning using a combination of a bag-of-words approach and syntatic/linguistic features. See Sim et al. (2013); Biessmann, (2016); Iyyer et al. (2014)
	- See [[]]
- Sim et al. (2013)
	- See [[]]
	- bag-of-word features for ideology detection 
	- Labeled corpus of political writing (German parliament, party manifestos, Facebook posts) used to generate "ideology lexicons"
		- Use those lexicons to analyze political speeches.
- Iyyer et al. (2014)
	- See [[]]
	- Recursive Netural Network (RNN) to identify ideology at the sentence-level
- Lin et al. (2008), Ahmed and Xing (2010) try to connnect legislative text to voting patterns.
	- See [[]]
	- See [[]]

- **Controvery Detection:** Trying to identify how controversial topics ellicit emotion among those who disagree with a specific argument.
- Mejova et al. (2014)
	- See [[]]
	- How do news articles highlight negative aspects of opposing viewpoints rather than positive aspects of concurring ones? 
	- Using large variation in BM25 scores to identify controversy.
- Lourtenzou et al. (2015)
	- How do social media comments identify a news topic as controversial?

### Hypothesis and setup:
- Rather than use a bag-of-words, this paper uses sentiment with respect to a handful of ex ante known topics to assess left-right ideologicla leaning.
	- This assumes that left-wing and right wing politicians (pseudo-)uniformly have certain sets of views
		- Eg. "right wing followers are often positive towards free markets, lower tax rates, etc."
	- "A political ideology can be represented by a characteristic sentiment distribution over different topics. This topic-specific sentiment representation of a political ideology can then be used for automatic ideology detection by comparing the topic-specific sentiments as expressed by the content in a document. " (p1)
- A set of documents: $\mathcal{D}=\{\ldots,d, \ldots\}$
- A set of ideology labels: $\mathcal{L}=\{\ldots, l, \ldots\}$
	- In this case there is only a left-right/democrat-republican divide so $|\{\mathcal{L}\}|=2$
	- A document $d\in\mathcal{D}$ has a label $l_d\in\mathcal{L}$.
- The set of topics come from $\mathcal{D}$ and are identified in a set $\mathcal{T}$
	- These topics could be identified by LDA, for instance (see Blei et al. (2003))
		- See [[]]
	- For a document $d$ and topic $t$ a sentiment score is generated and denoted as $s_{dt}$. This could be categorical but in this paper is in an ordinal set that spans from *strongly positive* to *strongly negative.*
	- $s_{dt}(x)$ is the probability that the sentiment of $d$ with respect to $t$ falls into ordinal class $x$. Repeated over every document, topic, and sentiment class, this generates a "topic-sentiment matrix" (TSM):
	$$\mathcal{S}_{d,\mathcal{T}}\begin{bmatrix}
	\dots & s_{dt1}(x) & \dots\\
	\dots & s_{dt2}(x) & \ldots\\
	\vdots & \vdots & \vdots 
	\end{bmatrix}
	 \tag{1}$$
	 - Each row corresponds to a topic $t\in\mathcal{T}$
	 - Each document produces a pseudo-unique sentiment "signature" over topic set $\mathcal{T}$ characterized by $\mathcal{S}_{d,\mathcal{T}}$
	 - To generate a TSM, it is necesary to segregate topics within a single document. For every document-topic pair $(d,t)$ sentences that contain at least one of the top-$k$ words associated with topic $t$ are extracted and collated (in order of appearance in $d$) in a sub-document $d_t$.  This sub-document is then passed to a conventional sentiment analysis tool to generate a vector $s_{dt}(\cdot)$ which represents the sentiment polarity as a probability distribution over the sentiment polarity classes. (This is a row in the TSM) 
		 - This paper uese $k=5$ and an RNN-based sentiment analyzer (Socher et al., 2013)
			 - See [[]]
 - It is also necessary to generate a TSM "signature" that stands in as the proto-typical $l$-type document.  This is done by generating the matrix that minimizes the cumulative deviation to each of the TSMs of the documents with label $l$. That is:
	 - $$\mathcal{S}_\mathcal{l, \mathcal{T}}=\underset{X}{\arg\min}\sum_{d\in\mathcal{D}\bigwedge l_d=l}\Vert X - \mathcal{S}_{d,\mathcal{T}}\Vert_F^2 \tag{2}$$
		 - where $\Vert \cdot\Vert_F$ represents the [Frobenius norm](https://mathworld.wolfram.com/FrobeniusNorm.html)
		 - This happens to work out as the mean of each of the respectively labeled TSMs
		 - $$\mathcal{S}_{l,\mathcal{T}} = \frac{1}{|\{ d : d\in \mathcal{D} \bigwedge l_d = l\}|} \sum_{d\in \mathcal{D} \bigwedge l_d = l}\mathcal{S}_{d, \mathcal{T}} \tag{3}$$
- When encountering an unseen (unclassified) document, $d'_t$ we can categorize it by first computing its TSM, $\mathcal{S}_{d', \mathcal{T}}$, and then finding the label that is characterized by a TSM $\mathcal{S}_{l,\mathcal{T}}$ that minimizes its distance to $\mathcal{S}_{d', \mathcal{T}}$: 
	- $$l_{d'} = \underset{l}{\arg\min} \Vert \mathcal{S}_{d', \mathcal{T}} - \mathcal{S}_{l, \mathcal{T}} \Vert_F^2 \tag{4}$$
	- In this paper, the two-label $l$ special case means that this process can be replicated by logistic regression ckassufucatuib where the TSMs are instead vectors that have weights equal to coefficients for each topic (and each sentiment class). This model can then be used to estimate an unseen document's label-affinity.

### Headline results:
- An LDA algorithm is run on the training set to generate 50 topics.
- The TSMs are generated using the Stanford CoreNLP sentiment API
- ![[Topic-Specific Sentiment Analysis Can Help Identify Political Ideology TAB 2.png]]
- "The document-specific TSM matricies do *not* contain any information about the topics themselves, but only about the sentiment in the document towards each topic; one may recollect that $s_{dt}(\cdot)$ is a quantification of the strength of the sentiment in $d$ towards topic $t$. Thus, in contrast to distributional embeddings such as doc2vec, TSMS contain only the niformation that directly relateds to sentiment towards specific topics that are learnt from across the corpus. The results indicate that TSM methods are able to achieve comparable performance to doc2vec-based methods despite usage of only a small slice of information."
- The most controversial/poltically polarizing topics can be determined by using the equation below and finding the greatest values.:
	- $$\text{dist}(t,R,D) = \Vert s_{R,t} - s_{D,t} \Vert \tag{5}$$
	- where $R,D$ are labels and $t$ represents a topic in $\mathcal{T}$.
	- ![[Topic-Specific Sentiment Analysis Can Help Identify Political Ideology TAB 3.png]]
	- Note that some of these might be polarizing because of a small sample of "training" speeches that may produce inconsistent underlying probability distributions.

#### Important fIgures/viz:

### Concepts, models & tags:
- #Political_Science
	- #Polarization
- #Methods 
	- #Natural_Language_Processing 
	- #Sentiment_analysis 
- #Author/SumitBhatia
- #Author/DeepakPadmanabhan

### BibTeX and other citation information:
- **As it should appear in APA: ** Bhatia, Sumit and Deepak Padmanabhan (2018), "Topic-Specific Sentiment Analysis Can Help Identify Political Ideology," *arXiv Preprint arXiv:1810.12897*
- **BibTeX key:** @article{bhatia2018topic,
 title={Topic-Specific Sentiment Analysis Can Help Identify Political Ideology},
 author={Bhatia, Sumit and Padmanabhan, Deepak},
 journal={arXiv Preprint arXiv:1810.12897},
 volume={},
 number={},
 pages={--},
 year={2018},
 publisher={}
},