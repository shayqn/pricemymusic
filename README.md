# price my music
### market insights for musicians

This is the repo for www.pricemymusic.online, an app that predicts which combination of products & prices will maximize album sales on bandcamp for a specific band or artist. It uses data scraped from www.bandcamp.com. 

### Required packages:
- numpy
- pandas
- scikit-learn
- flask
- sqlalchemy

### model pipeline:

**1. find similar artists**

Here I used implicit **alternating least squares** regression to factorize the sparse matrix of `artists` x `supporters`. Similar artists were then determined by cosine distance in the lower dimensional factorized space (I used the first 50 factors). Ben Fredrickson has [a great post on using implicit alternating least squares to find similar artists](http://www.benfrederickson.com/matrix-factorization/) using soundcloud data. 

**2. recommend products & prices** 

Sales for any products sold by the **50 top related artists** were analyzed to determine the optimal mix of products and prices for this group of customers. 

**3. forecast revenue**

Here the intuition is that album sales are related to the mixture of products and prices offered, as well as the type of music it is. Clearly there are more factors that play into how an album sells (how good the particular music is, for example). Still, I think it is reasonable to hypothesize that the right combination of products and prices for particular music genres (and thus customer bases) may alone have some predictive power when considering overall sales. 

Album sales were classified as low (<100), medium (100-500) or high (>500) sellers. A Random Forest Classifier was fit to a training set, cross-validated to tune parameters, and then scored on a testing set. The model achieved an overall accuracy of ~80% on classifying all 3 categories correctly for each album. 

Link to presentation slides on [slideshare](https://www.slideshare.net/secret/mU1sD5QFulI76c). 
