# NBA-Stat-Bot
Reddit bot that fetches submissions/comments from the r/fantasybball subreddit and parses them using regex expression to find player names contained within double brackets. These names are then passed to the NBA-API and season averages for those players are returned and then stored in a data frame. This data frame is then converted to markdown via the tabluate library which facilitates a table formatted response to the original comment. Sample output can be seen below.

![output](https://user-images.githubusercontent.com/47375187/108279734-e852aa80-7131-11eb-9c17-3c6867de3ed6.PNG)

APIs Utilized:
* NBA-API
* PRAW (Python Reddit API Wrapper)

Libraries Utilized:
* Pandas
* Tabulate
* Re
