# Title: Stance Detection in COVID-19 Teets
##### Author(s): Kyle Glandt, Sarthak Khanal, Yingjie Li, Doina Caragea, Cornelia Cragea
##### Year: 2021
##### Journal: *Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the International Conference on Natural Language Processing*

Abstract: The prevalence of the COVID-19 pandemic in day-to-day life has yielded large amounts of stance detection data on social media sites, as users turn to social media to share their views regarding various issues related to the pandemic, e.g. stay at home mandates and wearing face masks when out in public. We set out to make use of this data by collecting the stance expressed by Twitter users, with respect to topics revolving around the pandemic. We annotate a new stance detection dataset, called COVID-19-Stance. Using this newly annotated dataset, we train several established stance detection models to ascertain a baseline performance for this specific task. To further improve the performance, we employ self-training and domain adaptation approaches to take advantage of large amounts of unlabeled data and existing stance detection datasets. The dataset, code, and other resources are available on GitHub

URL/DOI: [https://aclanthology.org/2021.acl-long.127.pdf](https://aclanthology.org/2021.acl-long.127.pdf)

### Research question:
Is it possible to identify the stance of a Tweet with respect to an ex-ante known target/topic, (in this case COVID-19 related topics).

### Data:
- "We construct a COVID-19 Stance dataset that consists of 6,133 tweets covering user's stance towards four targets relevant to COVID-19 health mandates. The tweets are manually annotated for stand according to three categories: *in favor, against,* and *neither.*"
	-  Tweets starting on February 27th (re/quote-tweets are excluded) and ending on August 20th, 2020. (Aprox 30million)
	-  Subset of Tweets that mention the four targets' (listed below) associated hashtags
	-  7,122 (of approximately 36k) tweets are randomly selected to be scored by Amazon Mechanical Turk reviewers who evaluate:
		-  Stance: {in favor, against, neither}
		-  Opinion: {explicitly, implicitly, neither}
		-  Sentiment: {positive, negative, both, sarcasm, neither}
	-  ![[Stance Detection in COVID-19 Tweets  TAB 6-9png.png]]

### Relevant Literature:
- For U.S. politics stance detection papers see Mohammad et al., 2017; Ghosh et al., 2019; Xu et al., 2020. (2018 additionally)
	- See [[]] 
	- See [[]]
	- See [[DAN - Dual View Representation Learning for Adapting Stance Classifiers to New Domains]]; and See [[Cross-Target Stance Classification with Self-Attention Networks]]
- For COVID-19 pandemic Tweet databases see Mutlu et al., 2020; Miao et al., 2020; Hossain et al., 2020
	- See [[]]
	- See [[]]
		- This paper uses a similar a similar methodology but this paper focusses on "four targets using global English tweets, as opposed to Miao et al. (2020) who lavel data for just one targe ("lockdown") in one location ("New York")"
	- See [[]]
- 

### Hypothesis and setup:
- During the COVID-19 pandemic, populations took to Twitter to express their feelings about various public officials and public policies. In continuing to assess the population's sentiment about those officials and policies, social media posts can serve as a window into their general attitudes. This paper considers Tweets.
	- Targets of Interest:
		- "Wearing a Face Mask"
		- "Keeping Schools Closed"
		- "Anthony S Fauci, M.D."
		- "Stay at Home Orders"
	- ![[Stance Detection in COVID-19 Tweets  TAB 1.png.png]]
		- Example of how Tweets and their topic-stances are labelled.
- Methods tested in this paper
	- BERT
		- This is the baseline model 
	- Dual-view Adaptation Network (DAN)
		- "learns to predict the stance of a tweet by combining the subjective and objective views/representations of the tweet, while also learning to adapt them across domains."
		- Also combined with BERT

- Supervised Baseline Models
	- BiLSTM (Bi-Directional Long Short Term Memory Networks)
	- Kim-CNN (Convolutional Neural Network):
	- TAN (Target-specific Attention Networks):
	- ATGRU (The Bi-Directional Gated Recurrent Unit Network with Token-Level Attention Mechanism)
	- GCAE (Gated Convolutional Network with Aspect Embedding):
	- BERT 
- Self-training Baseline
	- BERT-NS (BERT with Noisy Student)
- Domain Adaptation Baseline
	- BERT-DAN (BERT with Dual-view Attention Networks)

- For each target, tweets are segregated into  "training", "validation", and "test" subsets. The training set is self-descriptive and following training, the model's hyperparameers are tuned against the "validation" set. This process repeats. Finally, following that process, the models are then set to evaluate the never-before-seen "test" subset.
	- ![[Stance Detection in COVID-19 Tweets TAB 11.png]]

### Headline results:
![[Stance Detection in COVID-19 Tweets  TAB 12.png]]

#### Important fIgures/viz:

### Concepts, models & tags:
- #Public_Health
	- #COVID19
- #Methods 
	- #Natural_Language_Processing 
	- #Sentiment_analysis 
	- #Stance_detection
- #Author/KyleGlandt
- #Author/SarthakKhanal 
- #Author/YingjieLi 
- #Author/DoinaCaragea
- #Author/CorneliaCaragea

### BibTeX and other citation information:
- **As it should appear in APA: ** Glandt, Kyle et al. (2021) "Stance Detection in COVID-19 Tweets" in *Proceedings for the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 1: Long Papers),* 1596-1611.
- **BibTeX key:** @inproceedings{glandt2021stance,
 title={Stance Detection in COVID-19 Tweets},
 author={Glandt, Kyle and Khanal, Sarthak and Li, Yingjie and Caragea, Doina and Caragea, Cornelia},
 booktitle={Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 1: Long Papers)},
 number={},
 pages={1596--1611},
 year={201},
 publisher={}
},