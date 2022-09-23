# Youtube Web Scrapper
_Made by - Hitesh wadhwani_
## _special thanks to Ineuron team_
Youtube web scrapper can scrape the data (url, name, number of likes, number of comments, thumbnail, s3 bucket download
link, comments) from any youtube channel.
Project is divided in two Versions because selenium takes time to scrape data from web which gives timeout error when
deployed. To overcome this problem project is divided in version 1 and version 2.

In version 1(localhost version) i scrapped all the data with the help of selenium and stored on mysql and mongodb atlas and
video download link is also generated.

In version 2 (deployed version) only some GREAT youtubers (krish naik, hitesh choudhary, sir ji, telusko) data is saved
on server which is served. download link can also be generated

## Features of version 1

- Data will be scrapped using selenium
- data will be stored in mysql workbench and monogdb atlas
- download links can be generated

## Features of version 2

- Data is saved on the local server of 4 youtubers which will be shown
- video download links will be generated (s3 bucket)

## Tech

- [python](https://www.python.org/) - programming language
- [selenium](https://www.selenium.dev/) - for web automation
- [flask](https://flask.palletsprojects.com/en/2.2.x/) - Python web framework


**Free Software, Hell Yeah!**