# reddit-sentiment
Computes general sentiment values of Reddit posts and outputs the overall ranking of Reddit's attitude towards companies. 

## Website
https://checkhivemind.herokuapp.com/

## Command-line usage
> cd collection &&
> python chat.py

*"The Reddit Hivemind Sentiment Analysis"*

  *Options :*                                                    
  1 = Fast scan using last updated data                       
  2 = Medium scan to recalc scores from corpora               
  3 = Scan all companies from scratch             
  4 = List companies                                          
  5 = Add company                                             
  6 = Remove company                                          
  7 = Input Survey Data for Test Evaluation
  8 = Graph Test Evaluation
  9 = Quit

## Corpora Locations
collection/tmp/companies: The list of company names to scan

collection/tmp/raw: The raw comments & upvotes pulled from reddit

collection/tmp/scores: Computed sentiment scores stored for quick retrieval


