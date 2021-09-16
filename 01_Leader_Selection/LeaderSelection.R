library(tidyverse)
library(readxl)
library(lubridate)
library(xtable)

# SET PATH: CHANGE AS APPROPRIATE FOR YOUR PATH
setwd("~/Work/UChicago/Leader-Sentiment-Earnings/01 Leader Selection")

`%notin%` <- Negate(`%in%`)

#Reading in raw data
polity_5 <- read_excel('p5v2018.xls')

reign_leaders <- read_csv('reign_leaders.csv')

#Basic time/democracy filtering to pare down the size of the datasets
polity_5_democ_7 <- polity_5 %>%
  filter(polity >=7, year > 1991)


# IF A LEADER IS AN INCUMBENT, THEIR END_YEAR IS COERCED TO 2021 (POST-2018 YEARS OF OBSERVATION WILL BE DROPPED ANYWAY)
reign_leaders_era <-reign_leaders %>%
  mutate(eyear = ifelse(is.na(eyear), year(today()), eyear),
         emonth = ifelse(is.na(emonth), month(today()), emonth))%>%
  rename(start_date = sdate,
         start_month = smonth,
         start_year = syear,
         end_month = emonth,
         end_year = eyear) %>%
  select(-c("X15", "X16"))

leaders_longified <- reign_leaders_era %>%
  group_by(rn = row_number()) %>%
  mutate(year = list(start_year:end_year)) %>%
  unnest() %>%
  ungroup()


matched <- polity_5_democ_7 %>%
  left_join(leaders_longified, by=c('year', 'ccode')) %>%
  group_by(ccode) %>%
  mutate(above_p8 = ifelse(polity>=8, 1,0)) %>%
  mutate(years_above_p8 = sum(above_p8))%>%
  ungroup() %>%
  filter(years_above_p8 >= 10,
         year >=1992) %>%
  relocate(scode, country, ccode, leader, year, polity, years_above_p8, start_date, start_month, start_year, end_month,end_year, gender, polity2)

# Output the countries of interest (and their CoW ccodes)
# We will use this list to develop a set of adjectives and denonyms

countries <- matched %>%
  select(country, ccode) %>%
  distinct()

write.csv(countries, "countries_pre_details.csv", row.names=FALSE)


# Output the leaders of interest, their leader-IDs, countries, and CoW ccodes
# We will use this list to identify the leaders of interest and check the economist to see how their names are styled

leaders <- matched %>%
  select(leader, leadid, country, scode, ccode) %>%
  distinct()

write.csv(leaders, 'leaders_names_pre_styling.csv', row.names=FALSE)


###################################################################


# Import leader-names after identifying the economist's styling
# Note that this includes manual leader-additions for Taiwan, Serbia, Montenegro, Kosovo
econ_styled_names <- read_csv('leaders_names_econ_styling.csv')


# Manually inputting taiwan leader dates
taiwan <- econ_styled_names %>%
  filter(ccode==713) %>%
  mutate(start_date = 0,
         start_month =0,
         start_year =0,
         end_month = 0, 
         end_year =0,
         gender=999)
# THE FORMAT: c(start_date, start_month, start_year, end_month, end_year,gender)
# This format is taken from the REIGN dataset
taiwan[taiwan$leader=="Lee Tenghui", 9:14] <- as.list(c(13,1,1988,5,2000,1))
taiwan[taiwan$leader=="Chen Shuibian", 9:14] <- as.list(c(20,5,2000,5,2008,1))
taiwan[taiwan$leader=="Ma Yingjeou", 9:14] <- as.list(c(20,5,2008,5,2016,1))
taiwan[taiwan$leader=="Tsai Ingwen", 9:14] <- as.list(c(20,5,2016,NA,NA,0))

# Longify leaders to get every year for which they were a leader.
taiwan <- taiwan %>%
  group_by(rn = row_number()) %>%
  mutate(end_year = ifelse(is.na(end_year), year(today()), end_year),
         end_month = ifelse(is.na(end_month), month(today()), end_month),
         year = list(start_year:end_year)) %>%
  unnest(year) %>%
  ungroup() %>%
  select(-rn)

#Manually inputting serbia leader dates
serbia <- econ_styled_names %>%
  filter(ccode==342)%>%
  mutate(start_date = 0,
         start_month =0,
         start_year =0,
         end_month = 0, 
         end_year =0,
         gender = 999)
# THE FORMAT: c(start_date, start_month, start_year, end_month, end_year, gender)
# This format is taken from the REIGN dataset
serbia[serbia$leader == "Vojislav Kostunica",9:14] <- as.list(c(5,6,2006,7,2008,1))
serbia[serbia$leader == "Mirko Cvetokovic",9:14] <- as.list(c(7,7,2008,7,2012,1))
serbia[serbia$leader == "Ivica Dacic" & serbia$leadid=="joshua-add-12",9:14] <- as.list(c(27,7,2012,4,2014,1))
serbia[serbia$leader == "Aleksandar Vucic",9:14] <- as.list(c(27,4,2014,5,2017,1))
serbia[serbia$leader == "Ivica Dacic" & serbia$leadid=="joshua-add-14",9:14] <- as.list(c(31,5,2017,6,2017,1))
serbia[serbia$leader == "Ana Brnabic",9:14] <- as.list(c(29,6,2016,NA,NA,0))

# Longify leaders to get every year for which they were a leader.
serbia <- serbia %>%
  group_by(rn = row_number()) %>%
  mutate(end_year = ifelse(is.na(end_year), year(today()), end_year),
         end_month = ifelse(is.na(end_month), month(today()), end_month),
         year = list(start_year:end_year)) %>%
  unnest(c(year)) %>%
  ungroup() %>%
  select(-rn)

#Manually inputting kosovo leader dates
kosovo <- econ_styled_names %>%
  filter(ccode==341) %>%
  mutate(start_date = 0,
         start_month =0,
         start_year =0,
         end_month = 0, 
         end_year =0,
         gender = 999)
# THE FORMAT: c(start_date, start_month, start_year, end_month, end_year, gender)
# This format is taken from the REIGN dataset
kosovo[kosovo$leader == "Agim Ceku", 9:14] <- as.list(c(10,3,2006,1,2008,1))
kosovo[kosovo$leader == "Hashim Thaci", 9:14] <- as.list(c(9,1,2008,12,2014,1))
kosovo[kosovo$leader == "Isa Mustafa", 9:14] <- as.list(c(9,12,2014,9,2017,1))
kosovo[kosovo$leader == "Ramush Haradinaj", 9:14] <- as.list(c(9,9,2017,12,2020,1))
kosovo[kosovo$leader == "Albin Kurti", 9:14] <- as.list(c(3,12,2020,NA,NA,1))

# Longify leaders to get every year for which they were a leader.
kosovo <- kosovo %>%
  group_by(rn = row_number()) %>%
  mutate(end_year = ifelse(is.na(end_year), year(today()), end_year),
         end_month = ifelse(is.na(end_month), month(today()), end_month),
         year = list(start_year:end_year)) %>%
  unnest(c(year))%>%
  ungroup() %>%
  select(-rn)

# Manually inputting serbia leader dates
montenegro <- econ_styled_names %>%
  filter(ccode==348) %>%
  mutate(start_date = 0,
         start_month =0,
         start_year =0,
         end_month = 0, 
         end_year =0,
         gender = 999)
# THE FORMAT: c(start_date, start_month, start_year, end_month, end_year, gender)
# This format is taken from the REIGN dataset
montenegro[montenegro$leader == "Sturanovic", 9:14] <- as.list(c(10,11,2006,2,2008,1))
montenegro[montenegro$leader == "Dukanovic" & montenegro$leadid == "cb-mng-3", 9:14] <- as.list(c(29,2,2008,12,2010,1))
montenegro[montenegro$leader == "Luksic", 9:14] <- as.list(c(29,12,2010,12,2012,1))
montenegro[montenegro$leader == "Dukanovic" & montenegro$leadid == "cb-mng-5", 9:14] <- as.list(c(4,12,2012,11,2016,1))
montenegro[montenegro$leader == "Dusko Markovic", 9:14] <- as.list(c(28,11,2016,12,2020,1))

# Longify leaders to get every year for which they were a leader
montenegro <- montenegro %>%
  group_by(rn = row_number()) %>%
  mutate(end_year = ifelse(is.na(end_year), year(today()), end_year),
         end_month = ifelse(is.na(end_month), month(today()), end_month),
         year = list(start_year:end_year)) %>%
  unnest(c(year)) %>%
  ungroup() %>%
  select(-rn)


manual_add_econ_style <- bind_rows(taiwan, serbia, kosovo, montenegro)

# Polity info for manually added nations
polity_5_manual_data <- polity_5_democ_7 %>%
  filter(ccode %in% c(713,341,342,348)) %>%
  left_join(manual_add_econ_style, by=c('ccode', 'year')) %>%
  select(ccode, country.x, year, leader, leadid, polity, start_date, start_month, start_year, end_month, end_year, gender,
         econ_style_first, econ_style_last, econ_style_alias)

###############################################################################

all_leaders_with_styling <- matched %>%
  full_join(econ_styled_names, by=c('ccode', 'leadid')) %>%
  select(ccode, country.x, year, leader.x, leadid, polity, start_date, start_month, start_year, end_month, end_year, gender,
         econ_style_first, econ_style_last, econ_style_alias)%>%
  filter(ccode %notin% c(713,341,342,348)) %>%
  bind_rows(polity_5_manual_data) %>%
  mutate(leader = ifelse(is.na(leader), leader.x, leader))%>%
  select(-c(leader.x)) %>%
  rename(country = country.x)

write.csv(all_leaders_with_styling, 'all_leaders_econ_styling.csv', row.names=FALSE)

  
  

