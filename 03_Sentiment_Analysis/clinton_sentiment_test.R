library(tidyverse)
library(sentimentr)
library(xtable)

setwd("~/Work/UChicago/Leader-Sentiment-Earnings/03 Sentiment Analysis")
#add something for git

clinton_raw <- read_csv('clinton_test.csv')

clinton_processed <- clinton_raw %>%
  mutate(resolved_text = ifelse(is.na(resolved_text), text, resolved_text),
         articles_split = get_sentences(resolved_text)) %>%
  select(-c(text,link,bill_clinton))%>%
  unnest()%>%
  mutate(clinton_dummy = ifelse(grepl("clinton", articles_split, ignore.case =TRUE), "CLINTON", "OTHER"))

out <- clinton_processed$articles_split %>%
  sentiment_by(by=clinton_processed$clinton_dummy)
print(out)

print(xtable(out), digits =c(1,4, 3, 3))

clinton_fig <- plot(out)
