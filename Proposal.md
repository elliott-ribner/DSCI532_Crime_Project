Proposal- Vancouver Crime Tracker
================
Chimaobi Amadi, Elliott Ribner, Shivam Verma, Xugang Zhong(Kirk)
22/11/2019

## Motivation and Purpose

-----

## Description of the data

-----

The dataset is obtained from the [Vancouver Police Department (VPD)
website](https://geodash.vpd.ca/opendata/). It is based on the VPD
Records Management System and contains information about the type of
crime, nearest block, nearest neighborhood and date & time of the crime.
The data contains information from 1st January 2003 to 31st October
2019. VPD aims to provide this data for the public interest, to enhance
awareness & maintain transparency about crimes in Vancouver. Please note
that the dataset does not include all the crimes because of privacy &
investigative reasons. Location information in the data was offset so
that no association with a specific person or property can be
made.

### Variable Description

| S No. | Variable | Description | Insight |
| ----------- | ----------- | ----------- | ----------- |
| 1 | TYPE | Type of crime reported | The most common type of crime is `Theft from Vehicle`, `Mischief` & `Break and Enter Residential/Other` |
| 2 | YEAR | Year of crime reported | Number of crime occurrences reduced from 2003 to 2011 after which it started increasing. In 2018 the number of crimes was the same as in 2007 |
| 3 | MONTH | Month of crime reported | There is no significant difference in the number of crimes by month |
| 4 | DAY | Day of the month when the crime was reported | There is no significant difference in the number of crimes by day of month |
| 5 | HOUR | Hour of crime reported | Most of the crimes happen between 5 PM and midnight. Past midnight there are fewer occurrences |
| 6 | NEIGHBOURHOOD | Neighbourhood of crime reported | The data is for 24 neighborhoods in Vancouver. 10.42% of the crimes had no neighborhood associated with it. Even though the neighbourhood is missing for some records, the crime did happen. Therefore, neither imputing the data nor excluding those records as it describes other relevant information. |
| 7 | X | X-coordinate of the location | Longitude |
| 8 | Y | Y-coordinate of the location | Latitude |
| 9 | HUNDRED_BLOCK | Generalized location of Crime Activity | Not using |
| 10 | MINUTE | Hour of crime reported | Not using |


## Research questions and usage scenarios

-----

Peter and his family plans to relocate to Canada. As a result of the
favourable weather condition in Vancouver, they decide to settle in
Vancouver. Their first goal is to find accommodation: renting and
eventually owning a house in a safe neighbourhood, as well as safety for
their kids especially at school. The family does not know anyone in
Vancouver and relies on a reliable source of information regarding the
crime situation and trend in each of the neighbourhoods in Vancouver.

There are many people like Peter and his family; and to help solve their
problem, we plan on creating an interactive app that has the capability
of displaying crime information at a glance. The secondary motivation
for this app is answer general crime trends in Vancouver and create
awareness about crime rates per neighbourhood and need for drastic
intervention.

Using the dataset provided by the Vancouver Police Department (VPD), we
will build an interactive dashboard with the historic crime situation in
the city from 2003 to 2019. There are 3 filters provided in the
dashboard which includes the neighborhood, type of crime and the period
in years. The filter option streamlines the visualization and produces
charts that answer the questions.

The filtered data is molded to show the crime occurrences by
Month-of-Year (Chart 1) & Time-of-Day (Chart 2) to help him understand
the behavior of crimes around the city. In addition to this, he can look
at the trend of crime rate by year (Chart 3) and get to know the
composition of crimes (Chart 4) as well.

-----

## Sketch of the Application

-----
### Design 1
![Sketch](https://raw.githubusercontent.com/vermashivam679/DSCI_532_Group114_SKEC/master/Img/sketch.png "Crime Information by Vancouver Neighbourhood")

### Design 2
![GitHub Logo](/Img/App Sketch Part 1.png)
### Add description of the App

##### END!
