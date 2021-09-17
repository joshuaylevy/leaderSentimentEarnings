library(tidyverse)
library(sentimentr)
library(xtable)
library(ggrepel)
library(lubridate)

setwd("~/Work/UChicago/Leader-Sentiment-Earnings/03 Sentiment Analysis")

obuchi_raw <- read_csv('../02 Coreference Resolution/leader_resolved/Obuchi_resolved.csv')

obuchi_processed <- obuchi_raw %>%
  mutate(article_id = as.factor(row_number())) %>%
  select(-c(Obuchi, link, text)) %>%
  mutate(sentences = get_sentences(resolved_text)) %>%
  unnest(cols=c(sentences)) %>%
  mutate(obuchi_dummy = ifelse(grepl('obuchi', sentences, ignore.case=TRUE), "OBUCHI", "OTHER"))

obuchi_entity_sentiment <- obuchi_processed %$%
  sentiment_by(sentences, list(obuchi_dummy, article_id, date)) %>%
  mutate(article_id = as.numeric(article_id))
print(obuchi_entity_sentiment)
obuchi_sentence_sentiment <- uncombine(obuchi_entity_sentiment) %>%
  mutate(alpha_setting = ifelse(obuchi_dummy == "OBUCHI", 0.8, 0.2))

obuchi_sentence_sentiment %>% 
  head(5)


obuchi_fig <- ggplot()+
  geom_jitter(data=obuchi_sentence_sentiment,
             aes(x=date, y=sentiment, color=obuchi_dummy, alpha=alpha_setting),
             width=6)+
  geom_smooth(data=obuchi_entity_sentiment,
              aes(x=date, y=ave_sentiment, color=obuchi_dummy),
              span=0.3)+
  #geom_line(data=obuchi_entity_sentiment,
  #          aes(x=date, y=ave_sentiment, color=obuchi_dummy))+
  scale_color_discrete(guide ='none')+
  scale_alpha_binned(guide ='none')+
  scale_x_date(limits = as.Date(c(min(obuchi_entity_sentiment$date), max(obuchi_entity_sentiment$date) %m+% months(4))))+
  geom_label_repel(data = obuchi_entity_sentiment %>%
                     mutate(label_status = ifelse(date == max(date), obuchi_dummy, NA)),
                   aes(x=date, y=ave_sentiment, label=label_status, color=obuchi_dummy),
                   nudge_x = 80,
                   na.rm=TRUE,
                   arrow = NULL)+
  theme_minimal()

obuchi_fig

ggsave('obuchi_sentiment_time.png', plot = obuchi_fig, dpi=300)


#view(obuchi_sentence_sentiment%>%
#       filter(sentiment == min(sentiment) && obuchi_dummy=="OBUCHI"))

