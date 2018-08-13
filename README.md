NaomiWeb
========
NAOMIWeb/NetDIMM Loader is A Python-based web interface for browsing games to send to a NetDIMM. It's powered by bottle.py and Bootstrap. I recommended using this with a Raspberry Pi, but other hardware can be used instead. All documentation will be written for using it with a Pi.

Note: This is still a major work in progress.

Requirements
------------
### Hardware:
 * Sega NAOMI mainboard (Must use one of the following BIOS revisions: E, F, G, H. Region shouldn't matter)
 -or-
 * Sega NAOMI 2 mainboard (Any BIOS revision will work)

 * NetDIMM cartridge w/ security PIC (NULL PIC recommended, but other PICs may work)
 * Raspberry Pi 3 (2 may work but will not be supported)
 * CAT5 Crossover Cable

### Software:
 * Raspbian (other Linux distros should work, but haven't been tested)
 * Python 3.3 with bottle and configparser
 * NetDIMM-compatible game images (these are usually .bin files; you're on your own to find these!)

Software Setup (rough draft)
----------------------------
1. install python 3
2. install required modules
3. put game images in some folder
4. start web server
5. change settings in /config to match your setup
6. choose a game on the main page to load
7. done

Hardware Setup Example
----------------------
	+---------+                         +--------------+
	| NetDIMM | <==[Crossover Cable]==> | Raspberry Pi |
	+---------+                         +--------------+
	                                          /\
	                                          ||
	                                    [WiFi Connection]
	                                          ||
	                                          \/
	                                  +------------------+
	                                  | Internet Browser |
	                                  +------------------+
Todo
----
 * Rework code to be more clean and efficient
 * Style the edit buttons to actually look and flow nice
 * Catch exit signals and close everything properly
 * Incorporate actual messaging between load jobs and interface
 * Create some kind of database manager so I don't have to support this forever or expect users to know SQL
 * Implement job system (loadgame.py). Jobs will keep track of threads sending data to a NetDIMM.
 * Maybe support multiple endpoints for netbooting? Could be useful for users with a number of systems, or for running a tournament or something.
 * Unit tests and E2E tests
 * Set up build pipeline and automatic SD image generation
