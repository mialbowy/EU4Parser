# EU4Parser
Framework for parsing Europa Universalis IV data / save files

# Current Functionality
It is currently set up to parse tags and their names / localisations from the EU4 game files. It then parses a save file, popoulating a list of provinces with basic information. It uses this information to calculate the dev each tag owns and how much dev it has cores on. The difference of owned dev vs cored dev gives an indicator of how good a tag would be to vassalise / release as vassal.

# Requirements

It requires Python 3.6 or newer.

# Using It

Two values may need to be changed to use this script, which are in the clearly marked SETTING section of eu4-parser.py.

By default, it will look for EU4 game files in 'C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV'. If your installation of EU4 is somewhere else, then you must update URL. Note: there is no \ at the end (to avoid escape issues).

The default save file is 'test.eu4' and is in the same directory as these files. Either replace this file with your save file, or change the value in the script to match your save file. If it is a compressed, non-ironman save file, then open it with an unzip program and use the 'gamedata' file.

# Limitations

First and foremost, this is in Python and fairly slow given the size of even 1444 save files. It also requires that save files are not from ironman games.

# Future / Ongoing Work

I might have a look at ironman, but it probably will only be a look--I don't want to get involved with anything too technical.

I would like to add save editing in the form of filtered building removal (i.e., make room for townhalls in player-owned provinces). I am fairly confident print_tree (with a small adjustment) will produce valid save files, so I may go that route. Otherwise, it is easy to make a script that edits the save file in place.

I don't expect much interest, so that will probably be it. The only other meaningful change would be to use e.g. C++ for more reasonable speeds.