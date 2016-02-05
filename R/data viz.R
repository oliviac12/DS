##Data set is from library ISLR, data set name Auto

##boxplot break down by another categorical variable, key: facet_wrap
p = ggplot(Auto, aes(x = as.factor(mpg01), y = weight, fill = as.factor(mpg01))) 
p + geom_boxplot() +  facet_wrap(~ origin)
p + geom_boxplot() +  facet_wrap(~ year)

##visulize two way table 
ggplot(Auto, aes(as.factor(mpg01), ..count..)) + geom_bar(aes(fill = as.factor(origin)), position = "dodge")

##visulize contengency table, heatmap, works better when it's 3 way for 4 way visulization
counts = as.data.frame(table(Auto$year, Auto$mpg01))
colnames(counts) <- c("year", "mpg01", "Freq")
ggplot(counts, aes(year, mpg01)) + geom_tile(aes(fill = Freq), colour = "black") + 
  scale_fill_gradient(low = "white", high = "steelblue")