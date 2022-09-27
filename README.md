# CraigslistCarFinder
Python program to scrape car listings from craigslist based off of a users filters
# To Use:
in main:
Fill in the base URL (Just the cars and trucks page for your area
read through the filter details comment and fill the params dictionary accordingly to set any filters you want to use
Tweak the isDeal function to flag whatever you would like. Should be done easily by changing values of the variables up top

# V1 Issues:
For now. Sending emails has been disabled due to bugs with getting the email recipient from the post. I am open to suggestions or contributions to improve this. The code to send an email is there, and just needs a recipient argument for anyone that would like to leverage it. 

For now, instead of emailing it is just logging to a csv. I would reccomend installing a crontab to run this program on an interval and then just checking the csv for any 'deals' it finds. It reads the csv of deals in to be sure to not double log a post as well as skipping multiple posts about the same car.

# Coming Up:
Fixing sending emails to the recipient. 
Grabbing the Kelley Blue Book value of the vehicle 
Using the KBB value to make an equation to score the vehicles. 
Potententially using ML to score the vehicles based on other used car sales history.
Writing out all of this data to a sqllite table

9/27/22 I am still working on this :)
