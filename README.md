# FPL-Analysis
Fantasy Premier League Dashboard

Currently in progress but this is what I have so far. My idea was to create a dashboard where someone could quickly compare two players that they were thinking about putting in their fantasy team.

"FPL_Dashboard.py" calls and uses tables from "FPL_Analysis.py" and that calls functions from "build_out.py"
So if you would like to run the entire dashboard all in one go, run "FPL_Dashboard.py".

Things I still need to do:
- Format everything correctly
- Make the graphs selectable, so you can select the metric to compare
- Add in a few more key statistics
- Create a prediction model to predict a players points for the next game week


This is currently what the dashboard looks like:

![alt text](https://github.com/ksauln/FPL-Analysis/blob/master/Dashboard1.png)
![alt text](https://github.com/ksauln/FPL-Analysis/blob/master/Dashboard2.png)




Required packages:
- dash
- dash_core_components
- dash_html_components
- dash.dependencies
- plotly.graph_objs
- pandas 
- pathlib
- os
- numpy
- requests
- lxml.html
