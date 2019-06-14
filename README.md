# README #

Implementation of a genetic algorithm for finding best offensive trio (trio wiht most goals scored) within given overall limit.
Goals scored are counted for trios as a whole and only goals scored when trio is playing together in a match counts.
Distincions beetwen players is made only based on slected subset of attributes values.

Original dataset can be found here: https://www.kaggle.com/hugomathien/soccer/home

### Files ###

* input directory contains database files: 
	*database.sqlite is original db
	*trios.sqlite is modified db - after applying prepare_db script

* prepare_db.py -  a script that creates Trio_Stat table in DB and fills it with trios statistics.
				   Executing the script may take some time so this should only be called once before running any searche
				   
* trio_stat.py -  an interface for Trio_Stat table

* search.py - implementation of GA using DEAP module				   

