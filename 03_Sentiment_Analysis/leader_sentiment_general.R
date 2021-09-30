library(tidyverse)
library(sentimentr)
library(xtable)
library(ggrepel)
library(lubridate)
library(stringr)
library(tools)
library(ggtext)

#setwd("~/Work/UChicago/Leader-Sentiment-Earnings/03 Sentiment Analysis")
setwd("~/leaderSentimentEarnings/03_Sentiment_Analysis")

files_list <- list.files(path='../02_Coreference_Resolution/leader_resolved')

palette_generator <- function(df) {
  gg_color_hue <- function(n) {
    hues = seq(15, 375, length = n + 1)
    hcl(h = hues, l = 65, c = 100)[1:n]
  }

  leaders_vect <- unique(df$leader_sentence_dummy)
  leaders_vect <- leaders_vect[leaders_vect != "OTHER"]
  num_leaders <- length(leaders_vect)
  
  pal_vals <- gg_color_hue(num_leaders)
  pal_vals[length(pal_vals)+1] <- "#696969"
  pal_breaks <- leaders_vect
  pal_breaks[length(pal_breaks)+1] <- "OTHER"
  return(list(pal_vals, pal_breaks))
}


### Using RegEx to extract leader and country information from file_name
# (NOTE THAT WE WILL EVENTUALLY HAVE TO DROP THE _temp.csv suffix)
files_df <- tibble(files_list) %>%
  rename(file_name = files_list) %>%
  mutate(ccode = str_match(file_name, "(?=ccode-(\\d{1,3}))")[,2] %>%
           as.integer(),
         leadid = str_match(file_name, "(?=leadid-(.*)(?=\\_temp.csv))")[,2],)

#############################################
#Generating the sentiment dataframes en masse
batch_sentiment <- function(ccode_param, leadid_param) {
  print(c("CCODDE PARAMETER: ", ccode_param))
  print(c("LEADID PARAMETER: ", leadid_param))
  files_vect <- files_df %>%
    filter(ccode %in% ccode_param | leadid %in% leadid_param) %>%
    select(file_name)
  
  files_list <- deframe(files_vect)
  for (file in files_list) {
    print(file)
    # READING IN RAW 
    leader_name <- str_match(file,"(.*(?=_resolved))")[,2]
    print(leader_name)
    caps_name <- toupper(leader_name)
    file_path <- paste0('../02_Coreference_Resolution/leader_resolved/', file)
    assign(paste0(leader_name, '_raw'), read_csv(file_path, show_col_types=FALSE))
    
    # PROCESSING
    p <- get(paste0(leader_name, '_raw')) %>%
      mutate(article_id = as.factor(row_number())) %>%
      select(-c(text)) %>%
      mutate(sentences = get_sentences(resolved_text)) %>%
      unnest(cols = c(sentences)) %>%
      mutate(leader_sentence_dummy = ifelse(grepl(caps_name,
                                                  sentences,
                                                  ignore.case=TRUE),
                                            caps_name,
                                            'OTHER'))
    assign(paste0(leader_name, '_processed'), p, envir = .GlobalEnv)
    
    # GENERATE ENTITY SENTIMENT (with sentimentr)
    e <- get(paste0(leader_name, '_processed')) %$%
      sentiment_by(sentences, list(leader_sentence_dummy, article_id, date)) %>%
      mutate(article_id = as.numeric(article_id))
    assign(paste0(leader_name, '_entity_sentiment'), e, envir = .GlobalEnv)
    
    # GENERATE SENTENCE SENTIMENT (with sentimentr/unpacking)
    s <- get(paste0(leader_name, '_entity_sentiment')) %>%
      uncombine() %>%
      mutate(alpha_setting = ifelse(leader_sentence_dummy==caps_name,
                                    0.5,
                                    0.1))
    assign(paste0(leader_name, '_sentence_sentiment'), s, envir = .GlobalEnv)
    
  } 
}

#############################################
#Generating individual (leadid) leader-sentiment timeline figures
batch_leader_figures <- function(ccode_param, leadid_param){
  print(c("CCODDE PARAMETER: ", ccode_param))
  print(c("LEADID PARAMETER: ", leadid_param))
  files_vect <- files_df %>%
    filter(ccode %in% ccode_param | leadid %in% leadid_param) %>%
    select(file_name)
  
  files_list <- deframe(files_vect)
  for (file in files_list) {
    leader_name <- str_match(file, "(.*(?=_resolved))")[,2]
    country <- get(paste0(leader_name, '_processed')) %>%
      select(country) %>%
      unique() %>%
      toString()
    
    leader_sentence_sentiment <- get(paste0(leader_name, "_sentence_sentiment"))
    leader_entity_sentiment <- get(paste0(leader_name, "_entity_sentiment"))
    
    custom_palette <- palette_generator(leader_sentence_sentiment)
    lf <- ggplot()+
      geom_jitter(data=leader_sentence_sentiment,
                  aes(x=date, y=sentiment, color=leader_sentence_dummy, alpha=alpha_setting),
                  width=6)+
      geom_smooth(data=leader_entity_sentiment,
                  aes(x=date, y=ave_sentiment, color=leader_sentence_dummy),
                  size=2,
                  span=0.3,
                  se=FALSE)+
      scale_color_manual(guide='none', values=unlist(custom_palette[1]), breaks=unlist(custom_palette[2]))+
      scale_alpha_binned(guide='none')+
      scale_x_date(limits=as.Date(c(min(leader_entity_sentiment$date),
                                    max(leader_entity_sentiment$date) %m+% months(4))))+
      geom_label_repel(data=leader_entity_sentiment %>%
                         distinct(leader_sentence_dummy, date, .keep_all=TRUE) %>%
                         mutate(label_status=ifelse(date==max(date),
                                                    leader_sentence_dummy,
                                                    NA),
                                label_status = ifelse(is.na(label_status),
                                                      label_status,
                                                      ifelse(label_status=="OTHER",
                                                             "AMBIENT",
                                                             label_status))),
                       aes(x=date, y=ave_sentiment, label=label_status, color=leader_sentence_dummy),
                       nudge_x=80,
                       na.rm=TRUE,
                       arrow=NULL)+
      xlab("Date")+
      ylab("Sentiment")+
      ggtitle(paste0("Sentiment expressed by *The Economist* about ",
              toTitleCase(leader_name),
              " (",
              country,
              ")"))+
      annotate(geom="text",
               x=min(leader_entity_sentiment$date),
               y=1.1,
               label="more positive \u2192",
               size=2,
               color="#696969",
               angle='90',
               fontface='italic',
               hjust=0
               )+
      annotate(geom="text",
               x=min(leader_entity_sentiment$date),
               y=-1.1,
               label="\u2190 more negative",
               size=2,
               color='#696969',
               angle='90',
               fontface='italic',
               hjust=1
      )+
      theme_minimal()+
      theme(axis.title = element_text( 
        color="black", 
        size=12),
        plot.title=ggtext::element_markdown()
      )
    assign(paste0(leader_name, '_leader_figure'), lf, envir = .GlobalEnv)
  }
}

#############################################
#Generating national (ccode) leader=-sentiment timeline figures
batch_timeline_figures <- function(ccode_param) {
  for (ccode_p in ccode_param) {
    files_vect <- files_df %>%
      filter(ccode == ccode_p) %>%
      select(file_name)
    
    files_list <- deframe(files_vect)
    stand_in_name <- str_match(files_list[1],"(.*(?=_resolved))")[,2]
  
    x <- get(paste0(stand_in_name, '_entity_sentiment'))[FALSE,]
    y <- get(paste0(stand_in_name, '_sentence_sentiment'))[FALSE,]
    
    assign(paste0(ccode_p, '_entity_sentiment'), x)
    assign(paste0(ccode_p, '_sentence_sentiment'), y)
    
    for (file in files_list) {
      leader_name <- str_match(file,"(.*(?=_resolved))")[,2]
    
      e_1 <- get(paste0(leader_name, '_entity_sentiment'))
      s_1 <- get(paste0(leader_name, '_sentence_sentiment'))
      
      ##rbind all of these together
      assign(paste0(ccode_p, '_entity_sentiment'), rbind(get(paste0(ccode_p, '_entity_sentiment')),
                                                         e_1))
      assign(paste0(ccode_p, '_sentence_sentiment'), rbind(get(paste0(ccode_p, '_sentence_sentiment')),
                                                          s_1))
    }  
    
    ccode_sentence_sentiment <- get(paste0(ccode_p, '_sentence_sentiment'))
    assign(paste0(ccode_p, '_sentence_sentiment'), ccode_sentence_sentiment, envir = .GlobalEnv)
    ccode_entity_sentiment <- get(paste0(ccode_p, '_entity_sentiment'))
    assign(paste0(ccode_p, '_entity_sentiment'), ccode_entity_sentiment, envir = .GlobalEnv)
    
    custom_palette <- palette_generator(ccode_entity_sentiment)
    country <- get(paste0(leader_name, '_processed')) %>%
      select(country) %>%
      unique() %>%
      toString()
    
    tlf <- ggplot()+
      geom_jitter(data=ccode_sentence_sentiment,
                  aes(x=date, y=sentiment, color=leader_sentence_dummy, alpha=alpha_setting),
                  size=0.1,
                  width=6)+
      geom_smooth(data=ccode_entity_sentiment,
                  aes(x=date, y=ave_sentiment, color=leader_sentence_dummy),
                  size=2,
                  span=0.3,
                  se=FALSE)+
      scale_color_manual(guide='none', values=unlist(custom_palette[1]), breaks=unlist(custom_palette[2]))+
      scale_alpha_binned(guide='none')+
      scale_x_date(limits=as.Date(c(min(ccode_entity_sentiment$date),
                                    max(ccode_entity_sentiment$date) %m+% months(4))),
                   date_minor_breaks="5 years")+
      geom_label_repel(data=ccode_entity_sentiment %>%
                         group_by(leader_sentence_dummy) %>%
                         distinct(date, .keep_all=TRUE)%>%
                         mutate(label_status=ifelse(date==max(date),
                                                    leader_sentence_dummy,
                                                    NA)),
                       aes(x=date, y=ave_sentiment, label=label_status, color=leader_sentence_dummy),
                       nudge_x=80,
                       na.rm=TRUE,
                       arrow=NULL)+
      xlab("Date")+
      ylab("Sentiment")+
      ggtitle(paste0("Sentiment expressed by *The Economist* about leaders of ",
                     country))+
      annotate(geom="text",
               x=min(ccode_entity_sentiment$date),
               y=1.5,
               label="more positive \u2192",
               size=1.75,
               color="#696969",
               angle='90',
               fontface='italic',
               hjust=0
      )+
      annotate(geom="text",
               x=as.Date(min(ccode_entity_sentiment$date) %m-% months(6)),
               y=-1.5,
               label="\u2190 more negative",
               size=1.75,
               color='#696969',
               angle='90',
               fontface='italic',
               hjust=1
      )+
      theme_minimal()+
      theme(axis.title = element_text( 
        color="black", 
        size=12),
        plot.title=ggtext::element_markdown())
    assign(paste0(ccode_p, '_timeline_fig'), tlf, envir = .GlobalEnv)
    
  }
  
}

#############################################
#Generating leader-other sentiment correlation plots
batch_corel_figures <- function(ccode_param, leadid_param, facet_param, all_in_one_param, multi_name) {
  files_vect <- files_df %>%
    filter(ccode %in% ccode_param | leadid %in% leadid_param) %>%
    select(file_name)
  files_list <- deframe(files_vect)  
  
  
  #DEFAULT BEHAVIOR (ccode, leadid, facet=FALSE, all_in_one=FALSE)
  if (!facet_param & !all_in_one_param){
    for (file in files_list) {
      leader_name <- str_match(file,"(.*(?=_resolved))")[,2]
      caps_name <- toupper(leader_name)
      
      leader_entity_sentiment <- get(paste0(leader_name, '_entity_sentiment')) %>%
        pivot_wider(names_from="leader_sentence_dummy",
                    values_from=c("ave_sentiment",
                                  "sd",
                                  "word_count"))
      crf <- ggplot()+
        geom_point(data=leader_entity_sentiment,
                   aes(x=ave_sentiment_OTHER, y=get(paste0('ave_sentiment_', caps_name))),
                   alpha=0.5)+
        geom_abline(intercept=0, slope=1, size=1)+
        geom_smooth(data=leader_entity_sentiment,
                    aes(x=ave_sentiment_OTHER, y=get(paste0('ave_sentiment_', caps_name))),
                    method='lm',
                    color='red',
                    se=FALSE)+
        xlim(-1.1,1.1)+
        ylim(-1.1,1.1)+
        geom_vline(xintercept=0)+
        geom_hline(yintercept=0)+
        theme_minimal()+
        theme()
      
      assign(paste0(leader_name, '_corel_fig'), crf, envir = .GlobalEnv)   
    }
  } else if (facet_param) {
  # FACETING LEADERS OF INTEREST (ccode, leadid, facet=TRUE, all_in_one=FALSE)
    
    x <- data.frame()
    for (file in files_list) {
      leader_name <- str_match(file,"(.*(?=_resolved))")[,2]
      caps_name <- toupper(leader_name)
      leader_entity_sentiment <- get(paste0(leader_name, '_entity_sentiment')) %>%
        pivot_wider(names_from="leader_sentence_dummy",
                    values_from=c("ave_sentiment",
                                  "sd",
                                  "word_count")) %>%
        rename_with(.fn = ~ 'ave_sentiment_leader', .cols=paste0('ave_sentiment_', caps_name)) %>%
        mutate(name = as.factor(caps_name)) %>%
        select(article_id, date, ave_sentiment_leader, ave_sentiment_OTHER, name)
      x <- rbind(x, leader_entity_sentiment)
    }
    
    assign('multi_leader_entity_sentiment', x, envir = .GlobalEnv)
    print(multi_leader_entity_sentiment %>%
            slice_sample(n=10))
    
    crf_facet <- ggplot()+
      geom_point(data=multi_leader_entity_sentiment,
                 aes(x=ave_sentiment_OTHER,
                     y=ave_sentiment_leader,
                     color=name),
                 alpha=0.5)+
      geom_abline(intercept=0, slope=1, size=1)+
      xlim(-1.1,1.1)+
      ylim(-1.1,1.1)+
      geom_vline(xintercept=0)+
      geom_hline(yintercept=0)+
      theme_minimal()+
      theme()+
      facet_wrap(vars(name))
    
    temp_name <- multi_name
    assign(multi_name, crf_facet, envir = .GlobalEnv)
    
  } else if (all_in_one_param) {
    x <- data.frame()
    for (file in files_list) {
      leader_name <- str_match(file,"(.*(?=_resolved))")[,2]
      caps_name <- toupper(leader_name)
      leader_entity_sentiment <- get(paste0(leader_name, '_entity_sentiment')) %>%
        pivot_wider(names_from="leader_sentence_dummy",
                    values_from=c("ave_sentiment",
                                  "sd",
                                  "word_count")) %>%
        rename_with(.fn = ~ 'ave_sentiment_leader', .cols=paste0('ave_sentiment_', caps_name)) %>%
        mutate(name = as.factor(caps_name)) %>%
        select(article_id, date, ave_sentiment_leader, ave_sentiment_OTHER, name)
      x <- rbind(x, leader_entity_sentiment)
    }
    
    assign('multi_leader_entity_sentiment', x, envir = .GlobalEnv)
    
    custom_palette <- palette_generator(multi_leader_entity_sentiment %>%
                                          mutate(leader_sentence_dummy = as.character(name)))
    crf_together <-ggplot()+
      geom_point(data=multi_leader_entity_sentiment,
                 aes(x=ave_sentiment_OTHER,
                     y=ave_sentiment_leader,
                     color=name),
                 alpha=0.5)+
      geom_abline(intercept = 0, slope=1, size=1)+
      xlim(-1.1,1.1)+
      ylim(-1.1,1.1)+
      geom_vline(xintercept=0)+
      geom_hline(yintercept=0)
    
    for (smooth in unique(multi_leader_entity_sentiment$name)) {
      temp_leader_entity_sentiment <- multi_leader_entity_sentiment %>%
        filter(name==smooth)
      
      print(smooth)
      print(custom_palette[[1]][match(smooth, cust_pal[[2]])])
      crf_together <- crf_together+
        geom_smooth(data=temp_leader_entity_sentiment,
                    aes(x=ave_sentiment_OTHER, y=ave_sentiment_leader),
                    color=custom_palette[[1]][match(smooth, cust_pal[[2]])],
                    size=2,
                    method='lm',
                    se=FALSE)
    }

    crf_together <-crf_together+
      scale_color_manual(values=unlist(custom_palette[1]), breaks=unlist(custom_palette[2]))+
      theme_minimal()
    
    assign(multi_name, crf_together, envir = .GlobalEnv)
  }
  
}


  
batch_sentiment(c(230,), c())

batch_leader_figures(c(230), c())
aznar_leader_figure

batch_timeline_figures(c(230))
`230_timeline_fig`


batch_corel_figures(c(230), c(), TRUE, FALSE, '230_corel_facet')
`230_corel_facet`

batch_corel_figures(c(230), c(), FALSE, TRUE, '230_corel_together')
`230_corel_together`

zapatero_corel_fig
