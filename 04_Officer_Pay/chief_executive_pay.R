library(tidyverse)
library(readxl)
library(ggrepel)

setwd("~/Work/UChicago/Leader-Sentiment-Earnings/04 Officer Pay")

raw_data <- read_excel('paycheck_data.xlsx', sheet="Heads of government")

raw_usd_pay <- raw_data %>%
  select('Name', 'Country', 'Pay (USD)', 'Average wage (USD)', 'GDP in millions (USD)', 'Salary source', 'Salary source (additional)')


raw_usd_pay %>%
  select('Pay (USD)', 'Average wage (USD)', 'GDP in millions (USD)') %>%
  summary()

ggplot(raw_usd_pay)+
  geom_point(aes(x=`Average wage (USD)`, y=`Pay (USD)`, color=Country), size=2.5)+
  geom_text_repel(aes(x=`Average wage (USD)`, y=`Pay (USD)`, label=Country))+
  scale_color_discrete(guide="none")+
  theme_minimal()


ggsave('leader_pay.png', plot=last_plot(), dpi=300)
