import csv
import export_fast
import sys
import os

# # # # IMPORTANT
# This file takes a results data file (obtained from export_fast.py)
# and parses it to determine podiums, participants, etc.
# Currently supports podiums, newcomer podiums, and SOR podium.
# More functionality could be added in the future fairly easily

# If you're not using this program to make your certificates, this should be your main file
# Running as main will print to terminal the various award placements
# certs.py (the certificates program) uses some of these functions


# Asks user for the live ID (currently four digits, maybe five soon?)
# and returns a 2D data array and the filename data is stored in
def parseInput():
    comp = input("Enter live ID (NOT competitionID): ")
    try:
        comp = int(comp)
        filename = export_fast.fetch(comp)
    # please don't enter nonintegers
    except ValueError:
        print("Invalid input: the live ID is the 4 (possibly 5) digits at the end of the WCA Live URL")
        sys.exit()
    # this triggers if the comp is on Live but no results entered yet
    if filename is None:
        print("\nNo results found for that competition. Try checking back later.\n")
        sys.exit()

    # load data from csv exported by export_fast into 2D array
    try:
        with open(filename, encoding='utf-8-sig', newline='') as file:
            competitionResults = csv.reader(file)
            i = 0
            data = []
            for row in competitionResults:
                if i == 0:  # don't save the header row
                    i += 1
                    continue
                data.append(row)
            print("Data found and loaded")
            # returns filename as well so we can delete it later if desired
            return [data, filename]
    # I forget why I have this as well as the other no results found warning.
    # I am scared to remove it.
    except FileNotFoundError:
        print("No results found - check back when some results are entered.")
        sys.exit()


# from competition data file, returns list of all events with results at the competition
def getEventIDs(data):
    ids = []
    for row in data:
        if row[0] not in ids:
            ids.append(row[0])
    # the ids will look like 333, 222, 333fm, pyram, etc.
    return ids


# from competition data file, returns list of all competitors with results at the competition
def getPeople(data):
    people = []
    for row in data:
        if row[3] not in people:
            people.append(row[3])
    # it's just a list of names
    return people


# takes time in centiseconds and returns a formatted time e.g. 3:28.77, 2.11
# doesn't work for multi but whereever that's required it's just handled there
def formatTime(time):
    time = int(time)  # gets passed as string
    if time > 0:
        result = f'{time // 6000}:{(time % 6000 // 100):02}.{(time % 100):02}'
    elif time == -1:
        result = "DNF"
    elif time == -2:
        result = "DNS"
    elif time == 0:
        result = "None"
    else:
        result = "Error"
    return result


# from data file and event, returns placements for the entire event
# e.g.: competitor A gets 12th in R1 and 8th in finals, so they're placed 8th.
# competitor B got 17th in R1 and didn't qualify for finals, so they're placed 17th.
# returns a list of the entire result row for the latest round competitor K competed in
def getPlacements(data, eventID):

    results = []
    # get results for just this event
    for row in data:
        if row[0] == eventID:
            results.append(row)

    # find number of rounds held
    rounds = 1
    for row in results:
        if row[1] == "Semi Final":
            rounds = 4
    if rounds == 1:
        for row in results:
            if row[1] == "Second Round":
                rounds = 3
    if rounds == 1:
        for row in results:
            if row[1] == "First Round":
                rounds = 2

    # do rankings by round
    rankings = []

    # get all the results from the final
    roundResults = []
    for row in results:
        if row[1] == "Final":
            roundResults.append(row)
    # then assign rankings 1-n for those competitors
    for i in range(len(roundResults)):
        for row in roundResults:
            if row[2] == "":
                # probably head-to-head final
                return []
            if int(float(row[2])) == i + 1:
                rankings.append(roundResults[i])

    # get results from second to last round
    # depending on number of rounds, this round could be called different things
    roundResults = []
    if rounds == 2:
        for row in results:
            if row[1] == "First Round":
                roundResults.append(row)
    elif rounds == 3:
        for row in results:
            if row[1] == "Second Round":
                roundResults.append(row)
    elif rounds == 4:
        for row in results:
            if row[1] == "Semi Final":
                roundResults.append(row)
    # now make rankings for this round and append to prev. round
    # if a competitor is already ranked, they were in a future round and can be skipped
    # this skipping is reflected in the start index of the range()
    # will break if export formatting changes significantly but probably is safe
    for i in range(len(rankings), len(roundResults)):
        for row in roundResults:
            if row[2] == "":
                # probably head-to-head final
                return []
            if int(float(row[2])) == i + 1:
                rankings.append(roundResults[i])

    # third to last round
    roundResults = []
    if rounds == 3:
        for row in results:
            if row[1] == "First Round":
                roundResults.append(row)
    elif rounds == 4:
        for row in results:
            if row[1] == "Second Final":
                roundResults.append(row)
    for i in range(len(rankings), len(roundResults)):
        for row in roundResults:
            if row[2] == "":
                # probably head-to-head final
                return []
            if int(float(row[2])) == i + 1:
                rankings.append(roundResults[i])

    # four rounds??
    roundResults = []
    if rounds == 4:
        for row in results:
            if row[1] == "First Round":
                roundResults.append(row)
    for i in range(len(rankings), len(roundResults)):
        for row in roundResults:
            if row[2] == "":
                # probably head-to-head final
                return []
            if int(float(row[2])) == i + 1:
                rankings.append(roundResults[i])

    return rankings


# based on the given data, finds podiums of each event
def getPodiums(data):
    # finds events at the comp
    events = getEventIDs(data)

    # for each event, get the top three placers.
    # podiums looks like:
    # [["333", "Miles Walcott", "Miles2 Walcott", "Miles3 Walcott"], ["222", ... ], ... ]
    # unless I've lost touch which is possible
    podiums = []
    for i in range(len(events)):
        # get placements for event i
        placements = getPlacements(data, events[i])
        # empty placements usually means no results are entered
        if placements == []:
            podiums.append([events[i], []])
            continue

        # actually make the podium ["333", "Miles1", "Miles2", "Miles3"]
        newPodium = [events[i]]
        for j in range(min(3, len(placements))):  # if less than 3 competitors, don't find 3 podiumers
            newPodium.append(placements[j])
        # add this podium to list
        podiums.append(newPodium)
    return podiums


# If you aren't using certs.py, this is useful to actually print the podium placers
def printPodiums(data):
    # this determines whether people are ranked by single or average and prints the corresponding result
    avgEvents = ["222", "333", "444", "555", "pyram", "minx", "skewb", "clock", "333oh", "sq1", "666", "777"]
    singleEvents = ["333bf", "444bf", "555bf"]

    podiums = getPodiums(data)

    # for each event, print the podiums :O
    for event in podiums:
        print(f'\nEvent: {event[0]}')
        # if average is the ranked result, print based on that
        if event[0] in avgEvents:
            if event[1] == []:  # if no one on the podium
                print("H2H final or no rankings")
                continue
            for i in range(1, min(4, len(event))):  # don't print 3 podiums if only 2 people podiumed
                if int(event[i][7]) > 0:
                    print(f'{i}: {event[i][3]} has {formatTime(event[i][8])} avg with {formatTime(event[i][7])} single')

        elif event[0] in singleEvents:
            for i in range(1, min(4, len(event))):
                if int(event[i][7]) > 0:
                    print(f'{i}: {event[i][3]} has {formatTime(event[i][7])} single with {formatTime(event[i][8])} avg')

        elif event[0] == "333fm":
            # FMC requires handling for both single and average ranking based on format (bo1, bo2, mo3)
            if event[1][8] == 0:  # if first place didn't have an average
                for i in range(1, min(4, len(event))):
                    if int(event[i][7]) > 0:
                        print(f'{i}: {event[i][3]} has {event[i][7]} single')
            else:
                for i in range(1, min(4, len(event))):
                    if int(event[i][7]) > 0:
                        print(f'{i}: {event[i][3]} has {(float(event[i][8])/100):.2f} avg with {event[i][7]} single')

        else:
            for i in range(1, min(4, len(event))):
                # I don't think this check is required but it might be
                if int(event[i][7]) != -1:
                    # I had to look up how multi results are stored. It's kinda messy and I wouldn't recommend
                    # messing with this if you can avoid it
                    time = f'{int(event[i][7][2:7]) // 60}:{int(event[i][7][2:7]) % 60:02}'
                    missed = int(event[i][7][-2:])
                    solved = 99 - int(event[i][7][0:2]) + missed
                    print(f'{i}: {event[i][3]} has {solved}/{solved + missed} in {time}')


# returns full SOR rankings based on data
def getSOR(data):
    # get people and events :O
    people = getPeople(data)
    events = getEventIDs(data)

    # initialize everyone's SOR as 0 to be added to
    rankings = [[person, 0] for person in people]
    # for each event, iterate over the placements and add to each competitors running SOR
    for event in events:
        placements = getPlacements(data, event)
        for i in range(len(people)):
            found = False
            for j in range(len(placements)):
                if people[i] == placements[j][3]:
                    found = True
                    rankings[i][1] += j + 1
                    break
            # if a competitor didn't compete in an event, return the number of competitors in the event
            # plus one, as I believe is standard
            if not found:
                rankings[i][1] += len(placements) + 1
    # sort rankings by SOR
    rankings.sort(key=lambda x: x[1])
    # returns all people by [name, SOR] sorted so first place comes first
    # so you might return
    # [["Miles", 4], ["Miles2", 20], ... ]
    return rankings


# Prints the top 3 in SOR
def printSOR(data):
    # Literally just gets the SOR rankings and prints the first 3
    print("\nEvent: SOR")
    rankings = getSOR(data)
    for i in range(3):
        print(f'{i+1}: {rankings[i][0]} has SOR {rankings[i][1]}')


# works the exact same as normal podiums
# but only selects someone for a podium spot if they don't have a WCA ID
def getNewcomerPodiums(data):
    events = getEventIDs(data)
    podiums = []
    for i in range(len(events)):
        placements = getPlacements(data, events[i])
        newcomerPlacements = []
        for row in placements:
            if row[4] == "":  # this checks for newcomer status
                newcomerPlacements.append(row)
        newPodium = [events[i]]
        # if fewer than 3 newcomers in the event, don't try to return more
        for j in range(min(3, len(newcomerPlacements))):
            newPodium.append(newcomerPlacements[j])
        podiums.append(newPodium)
    return podiums


# prints newcomer podiums
def printNewcomerPodiums(data):
    avgEvents = ["222", "333", "444", "555", "pyram", "minx", "skewb", "clock", "333oh", "sq1", "666", "777"]
    singleEvents = ["333bf", "444bf", "555bf"]

    podiums = getNewcomerPodiums(data)  # this is the only line different from printPodiums()
    for event in podiums:
        print(f'\nEvent: {event[0]} Newcomer')
        if event[0] in avgEvents:
            if event[1] == []:
                print("H2H final - no rankings")
                continue
            for i in range(1, min(4, len(event))):
                if int(event[i][7]) > 0:
                    print(f'{i}: {event[i][3]} has {formatTime(event[i][8])} avg with {formatTime(event[i][7])} single')

        elif event[0] in singleEvents:
            for i in range(1, min(4, len(event))):
                if int(event[i][7]) > 0:
                    print(f'{i}: {event[i][3]} has {formatTime(event[i][7])} single with {formatTime(event[i][8])} avg')

        elif event[0] == "333fm":
            if event[1][8] == 0:
                for i in range(1, min(4, len(event))):
                    if int(event[i][7]) > 0:
                        print(f'{i}: {event[i][3]} has {event[i][7]} single')
            else:
                for i in range(1, min(4, len(event))):
                    if int(event[i][7]) > 0:
                        print(f'{i}: {event[i][3]} has {float(event[i][8]):.2f} avg with {event[i][7]} single')

        else:
            for i in range(1, min(4, len(event))):
                if int(event[i][7]) != -1:
                    time = f'{int(event[i][7][2:7]) // 60}:{int(event[i][7][2:7]) % 60:02}'
                    missed = int(event[i][7][-2:])
                    solved = 99 - int(event[i][7][0:2]) + missed
                    print(f'{i}: {event[i][3]} has {solved}/{solved + missed} in {time}')


# if this is the file being run
if __name__ == "__main__":
    # load data
    [data, filename] = parseInput()

    # I think most of this is self-explanatory
    toggle = input("\nPrint podiums? (y/[n=something else]): ")
    if toggle == "y":
        printPodiums(data)

    toggle = input("\nPrint newcomer podiums? (y/[n=something else)]: ")
    if toggle == "y":
        printNewcomerPodiums(data)

    toggle = input("\nPrint SOR? (y/[n=something else)]: ")
    if toggle == "y":
        printSOR(data)

    # give option to delete data file once done
    toggle = input("\nAll options given. Delete data file? (y/[n=something else)]: ")
    if toggle == "y":
        os.remove(filename)
        print("\nDeleted.")

    print("\nExiting.\n")
