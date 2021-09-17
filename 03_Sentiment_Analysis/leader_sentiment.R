library(tidyverse)
library(sentimentr)
library(xtable)
library(ggrepel)
library(lubridate)

setwd("~/Work/UChicago/Leader-Sentiment-Earnings/03 Sentiment Analysis")


files_list <- list.files('../02 Coreference Resoltuion/leader_resolved')





file_name <- list.files('../02 Coreference Resolution/leader_resolved')[2]
#caps_name <- toupper(strsplit(file_name, '_')[[1]][1])
caps_name <- "ZAPATERO"

leader_raw <- read_csv('../02 Coreference Resolution/leader_resolved/Zapatero_resolved.csv')

leader_processed <- leader_raw %>%
  mutate(article_id = as.factor(row_number())) %>%
  select(date, link, ccode, country, resolved_text, article_id)%>%
  mutate(sentences = get_sentences(resolved_text))%>%
  unnest(cols=c(sentences))%>%
  mutate(leader_dummy = ifelse(grepl(caps_name, sentences, ignore.case=TRUE), caps_name, 'OTHER'))


leader_entity_sentiment <- leader_processed %$%
  sentiment_by(sentences, list(leader_dummy, article_id, date))%>%
  mutate(article_id = as.numeric(article_id))

leader_sentence_sentiment <- uncombine(leader_entity_sentiment)%>%
  mutate(alpha_setting = ifelse(leader_dummy == caps_name, 0.8, 0.2))


leader_fig <- ggplot()+
  geom_jitter(data = leader_sentence_sentiment,
              aes(x=date, y=sentiment, color=leader_dummy, alpha=alpha_setting),
              width=6)+
  geom_smooth(data = leader_entity_sentiment,
              aes(x=date, y=ave_sentiment, color=leader_dummy),
              span=0.3)+
  scale_color_discrete(guide = 'none', direction=-1)+
  scale_alpha_binned(guide = 'none')+
  scale_x_date(limits = as.Date(c(min(leader_entity_sentiment$date),
                                  max(leader_entity_sentiment$date) %m+% months(4))))+
  geom_label_repel(data = leader_entity_sentiment %>%
                     mutate(label_status = ifelse(date == max(date), leader_dummy, NA)),
                   aes(x=date, y=ave_sentiment, label=label_status, color=leader_dummy),
                   nudge_x=80,
                   na.rm=TRUE,
                   arrow=NULL)+
  theme_minimal()

leader_fig


#ggsave('obuchi_sentiment_time.png', plot = obuchi_fig, dpi=300)

