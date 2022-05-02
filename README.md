# About

----------
This is the web app for @joshua-coppola's Ski-Trail-Ratings project, and all svg and csv files are from that repository. This repository should be placed in the same directory at the same level as Ski-Trail-Ratings. This portion of the project contains the database, flask web app, and website.

<https://github.com/joshua-coppola/Ski-Trail-Ratings>

## Usage

To update the contents of the database, run:

```bash
python3 init_db.py
```

To run the website on localhost, run:

```bash
python3 wsgi.py
```

## Todo

As things currently stand, most pages exist and work, but small tweaks need to be made. This README will be updated as features are completed and bugs are fixed. Every line item is denoted with a priority: high, medium, or low.

### Index Page

- [ ] Medium - improve appearance -- it is a rather plain landing page
- [ ] Low - improve mobile support

### About Page

- [ ] Medium - improve appearance -- I don't love the blue stripe and in general could be better with some tweaks
- [x] High - fix word choice in a couple spots
- [ ] Low - improve mobile support

### Search Page

- [x] High - fix off by one color error with difficulty slider
- [x] High - fix missing yellow section on difficulty slider
- [x] High - fix being able to move the left and right sliders past each other on the difficulty slider
- [x] High - add thumbnails to results
- [x] Medium - make thumbnails and mountain names clickable
- [x] High - implement sorting drop-down logic
- [x] Medium - add alphabetized sorts to drop down
- [x] Medium - add vertical sort to drop down
- [x] Medium - add trail count sort to drop down
- [ ] Medium - add slider to filter by vertical
- [ ] Medium - reorder filters
- [ ] Medium - add difficulty to each mountain in results
- [ ] Medium - improve filter by state to take abbreviations or full state names
- [ ] Low - improve default behavior for sliders
- [ ] Medium - fix search box not resetting correctly
- [ ] Low - UI/UX improvements
- [ ] Low - improve mobile support

### Map Pages

- [x] High - fix sidebar covering map by default
- [x] Medium - sort trails and lifts on sidebar
- [ ] Medium - optimize / remove 3D maps
- [ ] Medium - make zoom zoom in on cursor, not center of map
- [ ] Low - improve mobile support

### Rankings

- [x] High - fix how bar length for beginner friendliness is displayed
- [x] High - fix bar colors for beginner friendliness
- [x] High - difficulty blurb does not display
- [x] High - add better descriptions to difficulty and beginner friendliness
- [x] Medium - improve bar scaling
- [x] Medium - improve bar spacing
- [ ] Medium - add grid-lines to give sense of scale
- [x] Medium - add hover over text for difficulty numbers
- [x] Medium - add ranking numbers and state for each mountain
- [x] Medium - implement filters similar to search page
- [ ] Medium - add legend to top of page
- [ ] Medium - make bars clickable
- [ ] Low - UI/UX improvements
- [ ] Low - improve mobile support

### Trail Rankings

- [ ] Low - implement a trail rankings page similar to the mountain rankings

### Database

- [ ] Medium - don't store state in name for duplicate mountain names
- [ ] High - when initializing the trail data, use my reformatting function for mountain names so it doesn't break on edge case
