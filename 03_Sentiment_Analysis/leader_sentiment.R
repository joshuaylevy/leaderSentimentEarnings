library(tidyverse)
library(sentimentr)
library(xtable)
library(ggrepel)
library(lubridate)
library(stringr)

#setwd("~/Work/UChicago/Leader-Sentiment-Earnings/03 Sentiment Analysis")
setwd("~/leaderSentimentEarnings/03_Sentiment_Analysis")

files_list <- list.files(path='../02_Coreference_Resolution/leader_resolved')



### Using RegEx to extract leader and country information from file_name
# (NOTE THAT WE WILL EVENTUALLY HAVE TO DROP THE _temp.csv suffix)
files_df <- tibble(files_list) %>%
  rename(file_name = files_list) %>%
  mutate(ccode = str_match(file_name, "(?=ccode-(\\d{1,3}))")[2],
         leadid = str_match(file_name, "(?=leadid-(.*)(?=\\_temp.csv))")[2],)

#files_vect <- files_df %>%
#  filter(ccode = 230)

batch_sentiment <- function(ccode_param, leadid_param) {
  files_vect <- files_df %>%
    filter(ccode = ccode_param,
           leadid = leadid_param)
  
  # Read in and create all raw text files post-coreference resolution
  # Raw list has the format c(leader1_raw, leader1_name, leader2_raw, leader2_name)
  raw_list <- c()
  for (file in files_vect) {
    file_name <- file
    leader_name <- str_match(file_name, "(.*(?=_resolved))")
    append(raw_list,
           c(assign(paste0(leader_name, '_raw'), read_csv(file_name)),
             leader_name))
  }
  
  
  # Process each of those raw dfs to split on sentences, and subsequently to get sentiment
  processed_list <- c()
  for (i in 1:(length(raw_list)/2)) {
    leader_name <- raw_list[2*i]
    raw <- raw_list[2*i-1]
    caps_name <- toupper(leader_name)
    x <- raw %>%
      mutate(article_id = as.factor(row_number())) %>%
      select(-c(text)) %>%
      mutate(sentences = get_sentences(resolved_text)) %>%
      unnest(cols = c(sentences)) %>%
      mutate(leader_dummy = ifelse(grepl(caps_name, sentences, ignore.case=TRUE),
                                   caps_name,
                                   'OTHER'))
    append(processed_list,
           c(assign(paste0(leader_name, '_processed'), x),
             leader_name))
  }
  
  entity_sentiment_list <-c()
  for (i in 1:(length(processed_list)/2)) {
    leader_name <- processed_list[2*i]
    processed <- processed_list[2*i-1]
    append(entity_sentiment_list,
           c(assign(paste0(leader_name, "_entity_sentiment"),
                    processed %$%
                      sentiment_by(sentencces, list(leader_dummy, article_id, date)) %>%
                      mutate(article_id = as.numeric(article_id))),
             leader_name))
    
  }
  
  for (i in 1:(length(entity_sentiment_list)/2)) {
    leader_name <- processed_list[2*i]
    caps_name <= toupper(leader_name)
    entity_sentiment <-processed_list[2*i-1]
    assign(paste0(leader_name, "_sentence_sentiment"),
           entity_sentiment %>%
           uncombine() %>%
           mutate(alpha_setting = ifelse(leader_dummy==caps_name,
                                         0.8,
                                         0.2)))  
  }
  
}



for (alpha in raw_list_test) {
  print(alpha)
  CAPS_NAME <- deparse(alpha)
  print(CAPS_NAME)
}



file_name <- list.files('../02 Coreference Resolution/leader_resolved')[2]
print(file_name)
#caps_name <- toupper(strsplit(file_name, '_')[[1]][1])
caps_name <- "ZAPATERO"

leader_raw <- read_csv('../02_Coreference_Resolution/leader_resolved/Zapatero_resolved.csv')

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

