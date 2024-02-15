# Mean reversion Models

Mean-reversion strategies work on the assumption that the price of an asset is prone to random fluctuation around an underlying stable trend. Therefore, values deviating far from the trend or observed mean will tend to reverse direction and revert to the mean. If the value is unusually high, we expect it to go back down and go up if it is unusually low. 


# Single-stock mean reversion

Mean reversion in the context of a stock price implies that periods of the price being far below the mean are followed by periods of the price going up, and vice versa. We can take advantage of this by buying the stock to go long when the price is lower than expected, and selling to go short when the price is higher than expected. We can plot the price of a stock along with the mean of the prices up to each day to see whether the price reverts to the mean.


```python
%matplotlib inline
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd
import auquanToolbox.dataloader as dl

# Load the prices data for a stock
start = '2013-06-01'
end = '2016-12-31'
m= 'PG'
data = dl.load_data_nologs('nasdaq', [m], start, end)
prices = data['ADJ CLOSE']

# Compute the cumulative moving average of the price
prices['mu'] = [prices[m][:i].mean() for i in range(len(prices))]
# Plot the price and the moving average
plt.figure(figsize=(15,7))
plt.plot(prices[m])
plt.plot(prices['mu']);
plt.show()
```

    C:\Users\Chandini\Miniconda3\envs\auquan\lib\site-packages\matplotlib\__init__.py:1401: UserWarning:  This call to matplotlib.use() has no effect
    because the backend has already been chosen;
    matplotlib.use() must be called *before* pylab, matplotlib.pyplot,
    or matplotlib.backends is imported for the first time.
    
      warnings.warn(_use_error_msg)
    

    Reading PG
    


    
![png](Mean%20reversion_files/Mean%20reversion_2_2.png)
    


Note that since we are computing the running average, "reverting to the mean" does not necessarily mean going as high or as low as it did before.

In order to trade using this strategy, we need to quantify what it means for the price to be higher or lower than expected. It's useful to compute the z-score of the price on each day, which tells us how many standard deviations away from the mean a value is:
$$ z = \frac{x - \mu}{\sigma} $$

where $x$ is the value, $\mu$ is the mean of the data set, and $\sigma$ is its standard deviation. So a price with a z-score $> 1$ is more than one standard deviation above the mean, and we will sell short when this happens. If the price on a day has a z-score $< 1$, we will buy long. If the price is within half a standard deviation of the mean, we will clear all positions.


```python
# Compute the z-scores for each day using the historical data up to that day
zscores = [(prices[m][i] - prices['mu'][i]) / np.std(prices[m][:i]) for i in range(len(prices))]

# Start with no money and no positions
money = 0
count = 0
for i in range(len(prices)):
    # Sell short if the z-score is > 1
    if zscores[i] > 1:
        money += prices[m][i]
        count -= 1
    # Buy long if the z-score is < 1
    elif zscores[i] < -1:
        money -= prices[m][i]
        count += 1
    # Clear positions if the z-score between -.5 and .5
    elif abs(zscores[i]) < 0.5:
        money += count*prices[m][i]
        count = 0
print money
```

    C:\Users\Chandini\Miniconda3\envs\auquan\lib\site-packages\ipykernel\__main__.py:2: RuntimeWarning: divide by zero encountered in double_scalars
      from ipykernel import kernelapp as app
    

    17705.496508
    

The danger of applying mean reversion to a single stock is that it exposes us to the movement of the market and the success or failure of the individual company, among other factors. If there is a persistent trend affecting the price of the security, we will find ourselves consitently undervaluing (if the price is moving steadily upward) or overvaluing (if the price is falling) the asset. Below we discuss two strategies that mitigate this risk.

# Mean reversion portfolio

Instead of taking the mean of the historical returns on an asset, we can look at the mean of the returns on all of the stocks in, say, the S&P 500. Hypothesizing that the worst-performing stocks last period will do better this period (that is, they are likely to be undervalued) and vice versa, we go long in stocks that performed poorly and short in stocks that performed well.

This approach has the advantage of being market-neutral, so that we do not treat stocks as undervalued just because the market as a whole is falling, or overvalued when the market is rising. Furthermore, by including a large number of securities in portfolio, we are likely to encounter many cases where our prediction is correct.

To construct a portfolio which takes advantage of mean reversion, we first select a universe, such as all S&P 500 stocks or the top-traded stocks on the NYSE. From this universe, we rebalance our portfolio every period (say, every week) by going short in the stocks in the bottom 20% of returns over the last period and long in the stocks in the top 20% of returns. If a stock is in neither of those quintiles, we do not include it in our portfolio.

We can construct a toy example using sector ETFs instead of a large basket of stocks:


```python
# Fetch prices data for 10 stocks from different sectors and plot returns
start = '2016-12-01'
end = '2016-12-31'
assets = ['AAPL', 'AIG', 'C', 'T', 'PG', 'JNJ', 'EOG', 'MET', 'DOW', 'AMGN']
data = dl.load_data_nologs('nasdaq', assets, start, end)
prices = data['ADJ CLOSE']
returns = prices/prices.shift(-1) -1
returns.plot(figsize=(15,7), color=['r', 'g', 'b', 'k', 'c', 'm', 'orange',
                                     'chartreuse', 'slateblue', 'silver'])
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.ylabel('Returns')

# Convert to numpy array to make manipulation easier
data = np.array(prices);
```

    Reading AAPL
    Reading AIG
    Reading C
    Reading T
    Reading PG
    Reading JNJ
    Reading EOG
    Reading MET
    Reading DOW
    Reading AMGN
    


    
![png](Mean%20reversion_files/Mean%20reversion_7_1.png)
    


We hypothesize that the stocks which do well for the first week will regress after another month, while those which do poorly at first will appreciate in value.


```python
# For each security, take the return for the first week
wreturns = (data[4] - data[0])/data[0]
# Rank securities by return, with 0 being the lowest return
order = wreturns.argsort()
ranks = order.argsort()

# For each security, take the return for the month following the first week
# Normalization for the time period doesn't matter since we're only using the returns to rank them
mreturns = (data[-1] - data[5])/data[5]
order2 = mreturns.argsort()
ranks2 = order2.argsort()

# Plot the returns for the first week vs returns for the next month to visualize them
plt.figure(figsize=(15,7))
plt.scatter(wreturns, mreturns)
plt.xlabel('Returns for the first week')
plt.ylabel('Returns for the following month');
```


    
![png](Mean%20reversion_files/Mean%20reversion_9_0.png)
    


The returns look like they could be anticorrelated, but what would have happened if we had followed the mean-reversion strategy when we examined the past week's returns?


```python
# Go long (by one share each) in the bottom 20% of securities and short in the top 20%
longs = np.array([int(x < 2)for x in ranks])
shorts = np.array([int(x > 7) for x in ranks])
print 'Going long in:', [assets[i] for i in range(len(assets)) if longs[i]]
print 'Going short in:', [assets[i] for i in range(len(assets)) if shorts[i]]

# Resolve all positions and calculate how much we would have earned
print 'Yield:', sum((data[-1] - data[4])*(longs - shorts))
```

    Going long in: ['AAPL', 'T']
    Going short in: ['EOG', 'DOW']
    Yield: 12.320874
    

# Pairs trading

In pairs trading, the quantity we are examining is the distance between two securities, which we expect to revert back to its mean. For this to be a reasonable assumption, we need the two securities to be statistically <i>cointegrated</i>. In practice, two companies whose products are substitutes for each other are often cointegrated. That is, they generally move together due to shifts in the market and in their specific industry, and move little relative to each other.

How do we incorporate the prediction about their difference into our portfolio? Suppose we are looking at two securities X and Y. Then we go long in X and short in Y when the two are closer together than expected, and short in X and long in Y when the two are far apart. In this way we remain neutral to the market, industry, and other shifts that cause X and Y to move together, while making money on their difference reverting to the mean. We can quantify "closer than expected" as the difference having a z-score of less than -1, and "farther apart than expected" as a z-score greater than 1. This is easier to picture if X's price is higher than Y's, but the end result is the same in either case.

Using the `coint` function from `statsmodels`, let's check whether HP and Microsoft stock prices are cointegrated.


```python
from statsmodels.tsa.stattools import coint
start = '2012-01-01'
end = '2016-12-31'
# Load prices data for HP and Microsoft
data = dl.load_data_nologs('nasdaq', ['MSFT', 'HP'], start, end)
X = data['ADJ CLOSE']['MSFT']
Y = data['ADJ CLOSE']['HP']
# Compute the p-value for the cointegration of the two series
_, pvalue, _ = coint(X,Y)
print pvalue
```

    Reading MSFT
    Reading HP
    0.963589073908
    

The p-value is low, so the two series are cointegrated. Next we need to find the mean of the difference. We'll compute the cumulative moving average - that is, the average of all the values up to each day - as though we were looking at the data every day without knowing the future.


```python
# Plot their difference and the cumulative moving average of their difference
val = pd.DataFrame(index = X.index, columns=['diff','mu'])
val['diff'] = X - Y
val['mu']= [val['diff'][:i].mean() for i in range(len(val['diff']))]
plt.figure(figsize=(15,7))
plt.plot(val['diff'])
plt.plot(val['mu'])
plt.show()
```


    
![png](Mean%20reversion_files/Mean%20reversion_15_0.png)
    


In some cases, we may instead want our mean to refer only to the moving average, excluding data from too long ago. Below we can see the difference between the cumulative moving average and the 60-day running average.


```python
mu_60d = pd.rolling_mean(val['diff'], window=90)
plt.figure(figsize=(15,7))
plt.plot(val['diff'], label='X-Y')
plt.plot(val['mu'], label='CMA')
plt.plot(mu_60d, label='60d MA')
plt.legend();
```

    C:\Users\Chandini\Miniconda3\envs\auquan\lib\site-packages\ipykernel\__main__.py:1: FutureWarning: pd.rolling_mean is deprecated for Series and will be removed in a future version, replace with 
    	Series.rolling(window=90,center=False).mean()
      if __name__ == '__main__':
    


    
![png](Mean%20reversion_files/Mean%20reversion_17_1.png)
    


From here our trading strategy is identical to that for a single security, where we replace the asset with the spread X-Y. When we short the spread, we buy Y and sell X, and vice versa for going long. We'll be using the CMA for the mean, but you can easily change it to see the difference. Keep in mind, however, that what works well with this data may not be suited for other situations, and each definition of the mean will sometimes outperform the other.


```python
# Compute the z-score of the difference on each day
zscores = [(val['diff'][i] - val['mu'][i]) / np.std(val['diff'][:i]) for i in range(len(val['diff']))]

# Start with no money and no positions
money = 0
count = 0
for i in range(len(val['diff'])):
    # Sell short if the z-score is > 1
    if zscores[i] > 1:
        money += val['diff'][i]
        count -= 1
    # Buy long if the z-score is < 1
    elif zscores[i] < -1:
        money -= val['diff'][i]
        count += 1
    # Clear positions if the z-score between -.5 and .5
    elif abs(zscores[i]) < 0.5:
        money += count*val['diff'][i]
        count = 0
        
print money
```

    C:\Users\Chandini\Miniconda3\envs\auquan\lib\site-packages\ipykernel\__main__.py:2: RuntimeWarning: divide by zero encountered in double_scalars
      from ipykernel import kernelapp as app
    

    6527.55837
    

# Alternative approaches

Mean-reversion strategies assume that trends tend to reverse direction. On the opposite end of the spectrum are trend-following or momentum-based strategies. These hypothesize that prices will, despite fluctuations, generally move in the direction they were moving in before. They can also take into account how quickly a price is moving, and anticipate changes in the direction of movement when it slows down. These are covered in more detail in another notebook.


```python

```
