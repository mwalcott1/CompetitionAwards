# Please read this file in its entirety before using this tool. It's not that long. I beg you.

This tool is owned by Miles Walcott, who retains full privileges of ownership of the tool.
Others are allowed to use the code in this tool for personal use, or for use pertaining to official WCA (World Cube Association) competitions.
Others are not allowed to use this tool for personal or monetary gain of any form.
By using this tool, you agree not to hold the owner responsible for any damages caused by its usage.
I claim a Creative Commons license for this tool, whatever that means. There's a copy of what that entails in here somewhere.


## Usage

There are two intended uses of the code in this tool.

### Obtaining results from a WCA competition
This can be done by running the awards.py file, either by running in an IDE, or by typing 'python awards.py' in a terminal window with Python installed in the same working directory as the base level of the tool (which should end in 'CompetitionAwards/' if nothing has been renamed). This will prompt the user to input the ID of a competition. This can be taken from the WCA Live website for the competition - specifically, the last 4 (possibly 5, soon) numbers at the end of the URL. From there, users can choose which awards to print out. Currently, the following are supported:

Podiums
Newcomer Podiums
SOR (Sum Of Ranks)

The contents of awards.py should work as implemented, and no changes should ever be required. It is recommended that this file never be altered, unless you wish to implement a function to find awards of your own construction. If you'd like support for more award types to be added, please contact me (details below) and I will consider adding the feature for all users.

### Exporting certificates for a WCA competition
This process is somewhat more involved. The program essentially pastes content on top of a base certificate. To use this functionality, you must put .png files in the unfilledCerts directory of this tool. For participation certificates, this file must be named part.png, and for all podium certificates, they must be titled 1.png, 2.png, and 3.png for 1st, 2nd, and 3rd place, respectfully. If you wish to use the same certificate, make duplicates with the given names. Be aware that for the text to fit to the certificate nicely, **you may need to change the global variable values at the top of cert.py**. cert.py is the only file that should need to be changed by the user for any reason. To edit how the certificates are filled further, you may experiment with the file, but please have caution while doing this, and only change code if you know what it does. If you have any questions, please contact me (details below).
Once this is done, you can run the certs.py file, either by running in an IDE, or by typing 'python awards.py' in a terminal window with Python installed in the same working directory as the base level of the tool (which should end in 'CompetitionAwards/' if nothing has been renamed). This will prompt the user to input the ID of a competition. This can be taken from the WCA Live website for the competition - specifically, the last 4 (possibly 5, soon) numbers at the end of the URL. From there, users can choose which awards to print out. Currently, the following certificates are supported:

Participation certificates
Podium certificates
Newcomer Podium certificates

Please contact me (details below) if you'd like support for more certificates to be added. Please note that the newcomerCerts, podiumCerts, and partCerts directories should be kept empty for intended results.

Currently, most of the world's alphabets (by users) are supported by this tool. If you run into a character not supported, a message will be printed to the terminal including that character. Please contact me (details below) and I can add support for that family of characters/symbols.

### Bonus tool: competitionCardsShifter
This one is pretty simple - I got annoyed with Groupifier printing competitor cards too close to the top margin which would then get cut off by my printer. I am unaware if this is an issue for similar softwares (e.g. Delegate Dashboard), but this tool, when run like the other ones, shifts an inputted PDF down by the inputted number of pixels. It should work for any PDF file, you just input the filepath (without quotation marks) (either relative or absolute path) and the number of pixels, and it saves the result file to the same directory as the original one.


## Contact
If you run into any issues with this tool, have any questions, etc., I encourage you to email me. Here is a (non-exhaustive) list of things I would like to be emailed about:

Feature suggestions
Bugs
Unintended results
Errors/Exceptions
Desire for additional text language support
Questions about how the tool works
Other questions

You can contact me at mwalcott@worldcubeassociation.org, or miles_walcott@yahoo.com if my WCA tenure has concluded. Please do not spam me or do anything malicious with my email as I am being very nice by providing this tool to you.