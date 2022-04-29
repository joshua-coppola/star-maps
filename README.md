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

As things currently stand, most pages exist and work, but small tweaks need to be made. This README will be updated as features are completed and bugs are fixed.

### Index Page

- [ ] Improve appearance -- it is a rather plain landing page

### About Page

- [ ] Improve appearance -- I don't love the blue stripe and in general could be better with some tweaks
- [x] Fix word choice in a couple spots

### Search Page

- [x] fix off by one color error with difficulty slider
- [x] fix missing yellow section on difficulty slider
- [x] fix being able to move the left and right sliders past each other on the difficulty slider
- [x] add thumbnails to results
- [x] make thumbnails and mountain names clickable
- [x] implement sorting drop-down logic
- [x] add alphabetized sorts to drop down
- [x] add vertical sort to drop down
- [x] add trail count sort to drop down
- [ ] add slider to filter by vertical
- [ ] reorder filters
- [ ] add difficulty to each mountain in results
- [ ] improve filter by state to take abbreviations or full state names
- [ ] UI/UX improvements

### Rankings

- [ ] fix how bar length for beginner friendliness is displayed
- [ ] difficulty blurb does not display
- [ ] add grid-lines to give sense of scale
- [ ] add ranking numbers
- [ ] implement filters similar to search page
- [ ] UI/UX improvements

### Trail Rankings

- [ ] implement a trail rankings page similar to the mountain rankings
