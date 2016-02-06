train_size <- floor(0.75 * nrow(Auto))
set.seed(123)
train_ind <- sample(seq_len(nrow(Auto)), size = train_size)
train <- mtcars[train_ind, ]
test <- mtcars[-train_ind, ]