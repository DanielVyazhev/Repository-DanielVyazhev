# Decision Making in Business

To open a local business, an entrepreneur needs to understand the level of potential demand for his services or goods at a particular point. Actually, millions could be invested, a great level service could be achieved, but the business would go broke in a couple of months, because there is simply no target audience in the location.
Previously, this problem was solved in primitive ways. The entrepreneur chose several locations that seemed promising to him. Then he or specially hired people simply watched the passers-by, manually analyzed the buildings and establishments that already exist there. You can't collect a lot of data like that, but you can draw some conclusions.

#### Which goals do we have?

We have identified the best neighbourhoods and streets to open a café, on five levels: 

Scores Explanation:

• score_streets	0,3	The most important factor is a popularity of place, so the highest score is assigned

• score_distance	0,25	Distance from center indirectly defines the popularity of location and potential traffic, therefore it is second priority score

• score_aggregate_seats	0,2	Aggregate seats define the traffic, but not consider popularity of place, the weight is lower

• score_inverse_variable	0,15	Weight of penalizing score, it is less than weight for score of streets as there is no aversion of competition and future cafe would have powerful brand

• score_chains	0,1	Condition whether there are chain restaurants nearby does not directly define level of demand and popularity of place, so the weight is only 0,1


#### Project Task: 
The difficulty is that the investment risks in such an analysis are very high. After all, the patency of the point may be excellent, but there will be a minimum of the target audience in it. Starting a business turns into a lottery: lucky or not.
could be resolved:

• accurate assessment of the volume and solvency of the target audience interested in specific goods or services;

• analysis of the supply-demand graph in the location;

• saturation of the competitive environment check;

• tracking the availability and cost of available space for starting a business.

#### My role in the team
This project involved writing code, pre-processing data and visualising the data, and calculating the results.
