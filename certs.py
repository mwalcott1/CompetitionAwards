from PIL import Image, ImageDraw, ImageFont, features
from fontTools.ttLib import TTFont
import img2pdf
import os
import sys
import glob
import awards

# # # # IMPORTANT
# This file takes participant/results data from awards.py and prints it on certificates.
# Recommended usage: printing data on top of a base certificate
# As I used a template to determine default values, my y-values for various things may
# not work well with all certificates. I recommend editing these as global values here:

nameH = 635  # this is the y-value in pixels where the name is centered
iconsH = nameH + 100  # = 735, y-value where event icons are placed on partcipation certs
# I really like the icons being 100px below the name, but feel free to change that.
eventH = 885  # y-value of the event text on podium certs. e.g. "In the {event} event"
iconH = eventH - 100  # = 785, y-value where event icons are placed on podium certs
iconW = 300  # distance from each margin of the two event icons on podium certs
resultH = 1000  # y-value of the result text on podium certs. "with a result of {result}"

# This code is the hardest to get and is somewhat dense. I recommend being careful with any
# changes, and making sure you can revert to the original code if needed. If you have any questions,
# concerns, or feedback on how this works, please feel free to contact me and I can try to work stuff out


# returns an ImageFont type of the given font and size
def font(font, size):
    if font == "germ":
        return ImageFont.truetype('fonts/Plain Germanica.ttf', size)
    elif font == "times":
        return ImageFont.truetype('fonts/times.ttf', size)
    elif font == "notojp":
        return ImageFont.truetype('fonts/NotoSerifJP-Bold.ttf', size)
    elif font == "fetty":
        return ImageFont.truetype('fonts/FetteUNZFraktur.ttf', size)
    elif font == "notosc":
        return ImageFont.truetype('fonts/NotoSerifSC-Bold.ttf', size)
    elif font == "notoml":
        return ImageFont.truetype('fonts/NotoSerifMalayalam-Bold.ttf', size)
    elif font == "noto":
        return ImageFont.truetype('fonts/NotoSerif-Bold.ttf', size)
    elif font == "notodv":
        return ImageFont.truetype('fonts/NotoSerifDevanagari-Bold.ttf', size)
    elif font == "nototm":
        return ImageFont.truetype('fonts/NotoSerifTamil-Bold.ttf', size)
    elif font == "nototl":
        return ImageFont.truetype('fonts/NotoSerifTelugu-Bold.ttf', size)
    elif font == "notokn":
        return ImageFont.truetype('fonts/NotoSerifKannada-Bold.ttf', size)
    elif font == "notobn":
        return ImageFont.truetype('fonts/NotoSerifBengali-Bold.ttf', size)
    elif font == "nototc":
        return ImageFont.truetype('fonts/NotoSerifTC-Bold.ttf', size)
    elif font == "notokr":
        return ImageFont.truetype('fonts/NotoSerifKR-Bold.ttf', size)
    elif font == "notoar":
        return ImageFont.truetype('fonts/NotoNaskhArabic-Bold.ttf', size)
    elif font == "notohb":
        return ImageFont.truetype('fonts/NotoSerifHebrew-Bold.ttf', size)
    elif font == "nototh":
        return ImageFont.truetype('fonts/NotoSerifThai-Bold.ttf', size)
    elif font == "notokh":
        return ImageFont.truetype('fonts/NotoSerifKhmer-Bold.ttf', size)
    elif font == "notomy":
        return ImageFont.truetype('fonts/NotoSerifMyanmar-Bold.ttf', size)
    else:
        # this should only trigger if you mess with the code that determines font selection
        print("CRITICAL ERROR: NO FONT")
        sys.exit()


# converts a country name as the WCA stores it to the two-letter abbreviation
# not all countries currently supported as the flag pngs I downloaded don't include everything
# if there's a country that comes up that you'd like included, please let me know
def iocToIso2(country):
    d = {
        "Afghanistan": "af",
        "Albania": "al",
        "Algeria": "dz",
        "American Samoa": "as",
        "Andorra": "ad",
        "Angola": "ao",
        "Argentina": "ar",
        "Armenia": "am",
        "Aruba": "aw",
        "Australia": "au",
        "Austria": "at",
        "Azerbaijan": "az",
        "Bahamas": "bs",
        "Bahrain": "bh",
        "Bangladesh": "bd",
        "Barbados": "bb",
        "Belgium": "be",
        "Belize": "bz",
        "Benin": "bj",
        "Bermuda": "bm",
        "Bhutan": "bt",
        "Bolivia": "bo",
        "Bosnia and Herzegovina": "ba",
        "Botswana": "bw",
        "Brazil": "br",
        "British Virgin Islands": "vg",
        "Brunei Darussalam": "bn",
        "Bulgaria": "bg",
        "Burkina Faso": "bf",
        "Burundi": "bi",
        "Cabo Verde": "cv",
        "Cambodia": "kh",
        "Cameroon": "cm",
        "Canada": "ca",
        "Cayman Islands": "ky",
        "Central African Republic": "cf",
        "Chad": "td",
        "Chile": "cl",
        "Chinese Taipei": "tw",  # Taiwan is a country :(
        "Colombia": "co",
        "Comoros": "km",
        "Cook Islands": "ck",
        "Costa Rica": "cr",
        "Croatia": "hr",
        "Cuba": "cu",
        "Cyprus": "cy",
        "Czechia": "cz",
        "Democratic People's Republic of Korea": "kp",
        "Democratic Republic of the Congo": "cd",
        "Denmark": "dk",
        "Djibouti": "dj",
        "Dominica": "dm",
        "Dominican Republic": "do",
        "Ecuador": "ec",
        "Egypt": "eg",
        "El Salvador": "sv",
        "Equatorial Guinea": "gq",
        "Eritrea": "er",
        "Estonia": "ee",
        "Eswatini": "sz",
        "Ethiopia": "et",
        "Fiji": "fj",
        "Finland": "fi",
        "France": "fr",
        "Gabon": "ga",
        "Gambia": "gm",
        "Georgia": "ge",
        "Germany": "de",
        "Ghana": "gh",
        "United Kingdom": "gb",
        "Greece": "gr",
        "Grenada": "gd",
        "Guam": "gu",
        "Guatemala": "gt",
        "Guinea": "gn",
        "Guinea Bissau": "gw",
        "Guyana": "gy",
        "Haiti": "ht",
        "Honduras": "hn",
        "Hong Kong, China": "hk",
        "Hungary": "hu",
        "Iceland": "is",
        "India": "in",
        "Indonesia": "id",
        "Iran": "ir",
        "Iraq": "iq",
        "Ireland": "ie",
        "Israel": "il",
        "Italy": "it",
        "Jamaica": "jm",
        "Japan": "jp",
        "Jordan": "jo",
        "Kazakhstan": "kz",
        "Kenya": "ke",
        "Kiribati": "ki",
        "Kosovo": "xk",
        "Kuwait": "kw",
        "Kyrgyzstan": "kg",
        "Laos": "la",
        "Latvia": "lv",
        "Lebanon": "lb",
        "Lesotho": "ls",
        "Liberia": "lr",
        "Libya": "ly",
        "Liechtenstein": "li",
        "Lithuania": "lt",
        "Luxembourg": "lu",
        "Madagascar": "mg",
        "Malawi": "mw",
        "Malaysia": "my",
        "Maldives": "mv",
        "Mali": "ml",
        "Malta": "mt",
        "Marshall Islands": "mh",
        "Mauritania": "mr",
        "Mauritius": "mu",
        "Mexico": "mx",
        "Federated States of Micronesia": "fm",
        "Monaco": "mc",
        "Mongolia": "mn",
        "Montenegro": "me",
        "Morocco": "ma",
        "Mozambique": "mz",
        "Myanmar": "mm",
        "Namibia": "na",
        "Nauru": "nr",
        "Nepal": "np",
        "Netherlands": "nl",
        "New Zealand": "nz",
        "Nicaragua": "ni",
        "Niger": "ne",
        "Nigeria": "ng",
        "North Macedonia": "mk",
        "Norway": "no",
        "Oman": "om",
        "Pakistan": "pk",
        "Palau": "pw",
        "Palestine": "ps",
        "Panama": "pa",
        "Papua New Guinea": "pg",
        "Paraguay": "py",
        "China": "cn",
        "Peru": "pe",
        "Philippines": "ph",
        "Poland": "pl",
        "Portugal": "pt",
        "Puerto Rico": "pr",
        "Qatar": "qa",
        "Republic of Korea": "kr",
        "Moldova": "md",
        "Romania": "ro",
        "Russia": "ru",
        "Rwanda": "rw",
        "Saint Kitts and Nevis": "kn",
        "Saint Lucia": "lc",
        "Saint Vincent and the Grenadines": "vc",
        "Samoa": "ws",
        "San Marino": "sm",
        "Sao Tome and Principe": "st",
        "Saudi Arabia": "sa",
        "Senegal": "sn",
        "Serbia": "rs",
        "Seychelles": "sc",
        "Sierra Leone": "sl",
        "Singapore": "sg",
        "Slovakia": "sk",
        "Slovenia": "si",
        "Solomon Islands": "sb",
        "Somalia": "so",
        "South Africa": "za",
        "South Sudan": "ss",
        "Spain": "es",
        "Sri Lanka": "lk",
        "Sudan": "sd",
        "Suriname": "sr",
        "Sweden": "se",
        "Switzerland": "ch",
        "Syria": "sy",
        "Tajikistan": "tj",
        "Thailand": "th",
        "Timor-Leste": "tl",
        "Togo": "tg",
        "Tonga": "to",
        "Trinidad and Tobago": "tt",
        "Tunisia": "tn",
        "Turkey": "tr",
        "Turkmenistan": "tm",
        "Tuvalu": "tv",
        "Uganda": "ug",
        "Ukraine": "ua",
        "United Arab Emirates": "ae",
        "Tanzania": "tz",
        "United States": "us",
        "Uruguay": "uy",
        "Uzbekistan": "uz",
        "Vanuatu": "vu",
        "Venezuela": "ve",
        "Vietnam": "vn",
        "Virgin Islands, US": "vi",
        "Yemen": "ye",
        "Zambia": "zm",
        "Zimbabwe": "zw"
    }
    return d[country]


# determines best font for a given character (for writing multilingual names)
def fontForChar(char):
    # I like this font for parentheses
    if char == '(' or char == ')':
        return "notojp"
    fontAliases = [
        # ordered so preferred fonts are on top. I like Plain Germanica for a fancy championship
        # look, but you could move noto above it if you like that font or are substituting fonts.
        # Less common languages are towards the bottom so we don't have to parse the entire .ttf
        # file for Thai every time we print an english character
        "noto", #reordered
        "germ",
        "fetty",
        # "noto",
        # past here are non-english fonts
        "notosc",
        "notodv",
        "nototm",
        "nototl",
        "notoml",
        "notokn",
        "notobn",
        "nototc",
        "notojp",
        "notokr",
        "notoar",
        "notohb",
        "nototh",
        "notokh",
        "notomy"
    ]
    # these correspond exactly to the abbreviations above. If you reorder one you
    # need to reorder the other to avoid unexpected behavior (nothing should break
    # but you'll print in a different font than you want)
    fonts = [
        "fonts/NotoSerif-Bold.ttf", # reordered
        "fonts/Plain Germanica.ttf",
        "fonts/FetteUNZFraktur.ttf",
        # "fonts/NotoSerif-Bold.ttf",
        "fonts/NotoSerifSC-Bold.ttf",
        "fonts/NotoSerifDevanagari-Bold.ttf",
        "fonts/NotoSerifTamil-Bold.ttf",
        "fonts/NotoSerifTelugu-Bold.ttf",
        "fonts/NotoSerifMalayalam-Bold.ttf",
        "fonts/NotoSerifKannada-Bold.ttf",
        "fonts/NotoSerifBengali-Bold.ttf",
        "fonts/NotoSerifTC-Bold.ttf",
        "fonts/NotoSerifJP-Bold.ttf",
        "fonts/NotoSerifKR-Bold.ttf",
        "fonts/NotoNaskhArabic-Bold.ttf",
        "fonts/NotoSerifHebrew-Bold.ttf",
        "fonts/NotoSerifThai-Bold.ttf",
        "fonts/NotoSerifKhmer-Bold.ttf",
        "fonts/NotoSerifMyanmar-Bold.ttf",
    ]
    # search all of our fonts for the first that has a glyph for the given character
    for i in range(len(fonts)):
        fontA = TTFont(fonts[i])
        for cmap in fontA['cmap'].tables:
            if cmap.isUnicode() and ord(char) in cmap.cmap:
                return fontAliases[i]
    # fallback. This makes printName() print tofu (blank box)
    return "idk"


# converts each eventId (e.g. 333) to its name (e.g. 3x3x3 Cube)
def eventToName(id):
    d = {
        "333": "3x3x3 Cube",
        "222": "2x2x2 Cube",
        "444": "4x4x4 Cube",
        "555": "5x5x5 Cube",
        "666": "6x6x6 Cube",
        "777": "7x7x7 Cube",
        "333oh": "3x3x3 One-Handed",
        "333bf": "3x3x3 Blindfolded",
        "clock": "Clock",
        "pyram": "Pyraminx",
        "minx": "Megaminx",
        "skewb": "Skewb",
        "sq1": "Square-1",
        "333fm": "3x3x3 Fewest Moves",
        "444bf": "4x4x4 Blindfolded",
        "555bf": "5x5x5 Blindfolded",
        "333mbf": "3x3x3 Multi-Blindfolded"
    }
    return d[id]


# prints name based on given name, ImageDraw object, width of cert, and desired y-value
def printName(name, I1, imgW, h):
    # split name up into chunks based on language (or symbol type)
    nameChunks = []  # list of tuples like ("chunk text", "bestFontForChunkAbbreviation")
    currentChunk = ""
    currentFont = fontForChar(name[0])
    # iterate over the input name
    for char in name:
        if fontForChar(char) == "idk":  # if none of our fonts support this character
            print(f'Unsupported character found: {char}')
            # aforementioned tofu
            currentChunk = currentChunk + '􏿮'
        # if the best font for the current character matches the last one, they go in the same chunk
        # since all fonts should have spaces we let those be in the middle of any chunk to minimize breaks
        elif fontForChar(char) == currentFont or char == ' ':
            currentChunk = currentChunk + char
        # if the best font changes, end the chunk and start a new one
        else:
            nameChunks.append((currentChunk, currentFont))
            currentFont = fontForChar(char)
            currentChunk = f"{char}"
    # if we have a nontrivial chunk after reaching the end of the string (I believe this always happens)
    # then save the last chunk as well
    if len(currentChunk) > 0:
        nameChunks.append((currentChunk, currentFont))

    # determine max font size (capped at 100) that fits the name on the cert
    # the logic is cursed but it has yet to fail in my testing so I'd advise not to mess with it
    w = (1222/2000) * imgW + 1  # tracks the width of the total text box. Initialized to enter while loop
    nameFontSize = 101
    nameChunkLengths = []  # stores the length of each text box for x-value calculations later
    # I determined experimentally that 1222 is the maximum number of pixels that results in a good looking certificate
    # on a 2000px-wide certificate (which my 8.5x11"s were)
    while w > (1222/2000) * imgW:
        nameChunkLengths = []
        nameFontSize -= int(max(1, ((w/1222) - 1)*nameFontSize//3))  # faster than decrementing by 1 and also is safe
        # calculate the width of the total text box given the chosen font size
        for k in range(len(nameChunks)):
            nameChunkLengths.append(font(nameChunks[k][1], nameFontSize).getlength(nameChunks[k][0]))
        w = sum(nameChunkLengths)

    # draw text by chunk
    firstCharX = (imgW - w)//2  # x-value of the first chunk
    for k in range(len(nameChunks)):
        charX = firstCharX + sum(nameChunkLengths[0:k])  # x-value of the current chunk
        if nameChunks[k][1] == "fetty":
            # vertical adjustment for one of the fonts which is spaced weirdly for some reason
            hAdj = h + (nameFontSize//12)
            thisFont = font("fetty", nameFontSize)
            I1.text((charX, hAdj), nameChunks[k][0], font=thisFont, fill=(0, 0, 0), anchor='lm')
        else:
            thisFont = font(nameChunks[k][1], nameFontSize)
            I1.text((charX, h), nameChunks[k][0], font=thisFont, fill=(0, 0, 0), anchor='lm')
    # returns width of drawn text box, referenced by the code that draws the flag and WCA id
    return w


# generate the participation certificate for the inputted person given the inputted data
def partCert(name, data):

    # get wca id, represented country, and competed events to put on the cert
    id = "NULL"
    country = ""
    events = []
    for row in data:
        if row[3] == name:
            id = row[4]
            country = row[5]
            if row[0] not in events:
                events.append(row[0])
    if id == "":
        id = "Newcomer"

    # open and draw the base certificate
    img = Image.open('unfilledCerts/part.png')
    imgW, _ = img.size  # since y-values are hard-coded we don't store image height
    I1 = ImageDraw.Draw(img)

    # draw name text (complicated so it uses a helper function)
    w = printName(name, I1, imgW, nameH)

    # draw ID or Newcomer
    I1.text(((imgW + w)//2 + 100, nameH), id, font=font("times", 40), fill=(0, 0, 0), anchor='lm')

    # load flag, determine placement, and draw
    flag = Image.open(f'h80/{iocToIso2(country)}.png')
    flagW, flagH = flag.size
    img.paste(flag, (int((imgW - w)//2 - 100 - flagW), nameH - flagH//2))

    # load and draw event icons
    # default behavior (<= 13 events)
    if len(events) < 14:
        iconW = 100
    # otherwise scale icon width to fit
    else:
        iconW = int(((2000 / (3*len(events) + 1))*2)//1)
    # load event icons and scale as determined above
    icons = []
    for event in events:
        icons.append(Image.open(f'icons/{event}.png').resize((iconW, iconW)))
    # determine placement
    iconsHCentered = iconsH + (100 - iconW)//2
    firstIconW = imgW//2 - (len(icons) - 1) * (iconW * 1.5)//2 - iconW//2
    # actually apply icons
    for i in range(len(icons)):
        img.paste(icons[i], (int((firstIconW + i * (iconW * 1.5))//1), iconsHCentered), icons[i])

    # save certificate
    img.save(f"partCerts/{name.replace(' ', '')}.png")


# generate the podium certificates for the inputted event given the inputted data
def podiumCerts(event):
    eventId = event[0]
    if event[1] == []:
        # h2h final or no rankings is the only way this happens I think
        print(f'Event: {eventId} had a H2H final or had no rankings')
        return

    for i in range(1, len(event)):
        # make sure non-DNF result
        if float(event[i][7]) <= 0:
            continue

        # get details to put on cert
        name = event[i][3]
        id = "NULL"
        country = ""
        for row in data:
            if row[3] == name:
                id = row[4]
                country = row[5]
                break
        if id == "":
            id = "Newcomer"

        # open and draw the base certificate
        try:
            img = Image.open(f'unfilledCerts/{i}.png')
        except FileNotFoundError:
            print(f"Couldn't find a file for podium place {i}. Exception thrown")
            sys.exit()
        imgW, _ = img.size
        I1 = ImageDraw.Draw(img)

        # draw name text (complicated so it uses a helper function)
        w = printName(name, I1, imgW, nameH)

        # draw ID or Newcomer
        I1.text(((imgW + w)//2 + 100, nameH), id, font=font("times", 40), fill=(0, 0, 0), anchor='lm')

        # load flag, determine placement, and draw
        flag = Image.open(f'h80/{iocToIso2(country)}.png')
        flagW, flagH = flag.size
        img.paste(flag, (int((imgW - w)//2 - 100 - flagW), nameH - flagH//2))

        # draw event name
        eventFontSize = 80
        I1.text((imgW//2, eventH), eventToName(eventId), font=font("noto", eventFontSize), fill=(0, 0, 0), anchor='mm')

        # load and draw event icon (x2)
        iconSize = 200
        # load event icon and scale as determined above
        icon = Image.open(f'icons/{event[0]}.png').resize((iconSize, iconSize))
        # apply icon, left then right
        img.paste(icon, (iconW - iconSize//2, iconH), icon)
        img.paste(icon, (imgW - iconW - iconSize//2, iconH), icon)

        # result text
        # determine ranked result and translate to text
        result = None
        resultFontSize = 60
        if event[0] == "333fm":
            # determine whether fmc was bo1/2 or mo3 and print relevant result
            if event[1][8] <= 0:
                result = float(event[i][7])
                resultText = f'with a single of {int(result//1)} moves'
            else:
                result = float(event[i][8])
                resultText = f'with a mean of {(float(event[i][8])/100):.2f} moves'
        elif event[0] == "333mbf":
            # determine actual multi result from weird WCA formatting system
            result = float(event[i][7])
            time = f'{int(event[i][7][2:7]) // 60}:{int(event[i][7][2:7]) % 60:02}'
            missed = int(event[i][7][-2:])
            solved = 99 - int(event[i][7][0:2]) + missed
            resultText = f'with a result of {solved}/{solved + missed} in {time}'
            # multi has to draw its text differently because of the / in it
            # it also returns early
            # this is really cursed sorry
            mbldCharLengths = []
            mbldFonts = []
            mbldFontMain = font("noto", resultFontSize) # original germ
            mbldFontBackup = font("times", resultFontSize)
            for char in resultText:
                # write all but the '/' in Plain Germanic, and the '/' in Times New Roman
                if char != '/':
                    mbldCharLengths.append(mbldFontMain.getlength(char))
                    mbldFonts.append(mbldFontMain)
                else:
                    mbldCharLengths.append(mbldFontBackup.getlength(char))
                    mbldFonts.append(mbldFontBackup)
            w = sum(mbldCharLengths)
            # actually print the characters in the result one at a time
            firstCharX = (imgW - w)//2
            for k in range(len(resultText)):
                charX = firstCharX + sum(mbldCharLengths[0:k])
                I1.text((charX, resultH), resultText[k], font=mbldFonts[k], fill=(0, 0, 0), anchor='lm')
            # save certificate
            img.save(f"podiumCerts/{eventId}p{i}{name.replace(' ', '')}.png")
            continue
        else:
            # single events or missed cutoff
            if eventId == "333bf" or eventId == "444bf" or eventId == "555bf" or event[i][8] == '0':
                result = float(event[i][7])
            # average events
            else:
                result = float(event[i][8])
            if result < 6000:
                resultText = f'with a result of {result/100:.2f} seconds'
            elif result < 360000:
                resultText = f'with a result of {int(result//6000)}:{((result % 6000)/100):05.2f}'
        I1.text((imgW//2, resultH), resultText, font=font("noto", resultFontSize), fill=(0, 0, 0), anchor='mm') #originally germ
        # save certificate
        img.save(f"podiumCerts/{eventId}p{i}{name.replace(' ', '')}.png")


# generate the newcomer podium certificates for the inputted event given the inputted data
# should be the EXACT same as podiumCerts() but for the word Newcomer in the event text
def newcomerCerts(event):
    eventId = event[0]
    if len(event) == 1:
        print(f'Event: {eventId} had a H2H final or had no rankings')
        return

    for i in range(1, len(event)):
        if float(event[i][7]) <= 0:
            continue

        name = event[i][3]
        id = "NULL"
        country = ""
        for row in data:
            if row[3] == name:
                id = row[4]
                country = row[5]
                break
        if id == "":
            id = "Newcomer"

        img = Image.open(f'unfilledCerts/{i}.png')
        imgW, _ = img.size
        I1 = ImageDraw.Draw(img)

        w = printName(name, I1, imgW, nameH)

        I1.text(((imgW + w)//2 + 100, nameH), id, font=font("times", 40), fill=(0, 0, 0), anchor='lm')

        flag = Image.open(f'h80/{iocToIso2(country)}.png')
        flagW, flagH = flag.size
        img.paste(flag, (int((imgW - w)//2 - 100 - flagW), nameH - flagH//2))

        eventFontSize = 80
        eventText = eventToName(eventId) + " Newcomer"  # this + " Newcomer" is the mentioned only difference
        I1.text((imgW//2, eventH), eventText, font=font("noto", eventFontSize), fill=(0, 0, 0), anchor='mm')

        iconSize = 200
        icon = Image.open(f'icons/{event[0]}.png').resize((iconSize, iconSize))
        img.paste(icon, (iconW - iconSize//2, iconH), icon)
        img.paste(icon, (imgW - iconW - iconSize//2, iconH), icon)

        result = None
        resultFontSize = 60
        if event[0] == "333fm":
            if event[1][8] == 0:
                result = float(event[i][7])
                resultText = f'with a result of {int(result//1)} moves'
            else:
                result = float(event[i][8])
                resultText = f'with a result of {(float(event[i][8])/100):.2f} moves'
        elif event[0] == "333mbf":
            result = float(event[i][7])
            time = f'{int(event[i][7][2:7]) // 60}:{int(event[i][7][2:7]) % 60:02}'
            missed = int(event[i][7][-2:])
            solved = 99 - int(event[i][7][0:2]) + missed
            resultText = f'with a result of {solved}/{solved + missed} in {time}'
            mbldCharLengths = []
            mbldFonts = []
            mbldFontMain = font("germ", resultFontSize)
            mbldFontBackup = font("times", resultFontSize)
            for char in resultText:
                if char != '/':
                    mbldCharLengths.append(mbldFontMain.getlength(char))
                    mbldFonts.append(mbldFontMain)
                else:
                    mbldCharLengths.append(mbldFontBackup.getlength(char))
                    mbldFonts.append(mbldFontBackup)
            w = sum(mbldCharLengths)
            firstCharX = (imgW - w)//2
            for k in range(len(resultText)):
                charX = firstCharX + sum(mbldCharLengths[0:k])
                I1.text((charX, resultH), resultText[k], font=mbldFonts[k], fill=(0, 0, 0), anchor='lm')
            img.save(f"newcomerCerts/{eventId}p{i}{name.replace(' ', '')}.png")
            continue
        else:
            if eventId == "333bf" or eventId == "444bf" or eventId == "555bf" or event[i][8] == '0':
                result = float(event[i][7])
            else:
                result = float(event[i][8])
            if result < 6000:
                resultText = f'with a result of {result/100:.2f} seconds'
            elif result < 360000:
                resultText = f'with a result of {int(result//6000)}:{(result % 6000)/100:.2f}'
        I1.text((imgW//2, resultH), resultText, font=font("noto", resultFontSize), fill=(0, 0, 0), anchor='mm')
        img.save(f"newcomerCerts/{eventId}p{i}{name.replace(' ', '')}.png")


if __name__ == "__main__":

    # raqm needed to display some languages properly
    # if you're only dealing with languages with continuous characters
    # e.g. english, spanish, most eastern asian languages
    # you don't need this
    raqm = features.check_feature('raqm')
    if not raqm:
        print("Raqm (Complex Text Layout) not found. Please look into installing raqm to display all languages")
        print("It isn't directly a Python package but lies under something. I don't know. It's complicated.")
    # example of a string that wouldn't fully render properly without raqm:
    # Cube Č 气氣の큐 عربي עברית हिंदी বাংলা தமிழ் తెలుగు ಕನ್ನಡ മലയാളം ไทย ខ្មែរ မြန်မာ
    # some of it would and some wouldn't idk which parts are which fully

    # get data
    data, filename = awards.parseInput()

    # participation certs
    toggle = input("\nGenerate participation certificates? (y/[n=something else]): ")
    if toggle == 'y':
        people = awards.getPeople(data)  # get list of all competitors
        print("\nGenerating participation certificates")
        # make each cert (exports as png)
        for person in people:
            partCert(person, data)

        # combines them all to one pdf
        # note: if there are any png files in ./partCerts, they will be included in the pdf. Beware.
        folder_path = './partCerts'
        images = [os.path.join(folder_path, file) for file in sorted(os.listdir(folder_path)) if file.endswith(".png")]
        if images != []:
            with open(f"printables/{filename[:-11]}PartCerts.pdf", "wb") as f:
                f.write(img2pdf.convert(images))
        else:
            print("\nNo participation certificates to make.")
        # clean up ./partCerts
        files = glob.glob('./partCerts/*.png')
        for file in files:
            os.remove(file)
        print("Done")

    # generate podium certificates
    # logic is basically the exact same
    toggle = input("\nGenerate podium certificates? (y/[n=something else]): ")
    if toggle == 'y':
        podiums = awards.getPodiums(data)  # gets podiums for each event at the competition
        print("\nGenerating podium certificates")
        for event in podiums:
            podiumCerts(event)
        folder_path = './podiumCerts'
        images = [os.path.join(folder_path, file) for file in sorted(os.listdir(folder_path)) if file.endswith(".png")]
        if images != []:
            with open(f"printables/{filename[:-11]}PodiumCerts.pdf", "wb") as f:
                f.write(img2pdf.convert(images))
        else:
            print("\nNo podium certificates to make.")
        files = glob.glob('./podiumCerts/*.png')
        for file in files:
            os.remove(file)
        print("Done")

    # newcomer podium certificates
    # works the exact same way with one function call being different
    toggle = input("\nGenerate newcomer podium certificates? (y/[n=something else]): ")
    if toggle == 'y':
        podiums = awards.getNewcomerPodiums(data)  # this one
        print("\nGenerating newcomer podium certificates")
        for event in podiums:
            newcomerCerts(event)
        folder_path = './newcomerCerts'
        images = [os.path.join(folder_path, file) for file in sorted(os.listdir(folder_path)) if file.endswith(".png")]
        if images != []:
            with open(f"printables/{filename[:-11]}NewcomerCerts.pdf", "wb") as f:
                f.write(img2pdf.convert(images))
        else:
            print("\nNo newcomer podium certificates to make.")
        files = glob.glob('./newcomerCerts/*.png')
        for file in files:
            os.remove(file)
        print("Done")

    # choose whether to delete .csv file of competition results
    toggle = input("\nAll options given. Delete data file? (y/[n=something else]): ")
    if toggle == "y":
        os.remove(filename)
        print("\nDeleted.")
    print("\nExiting.\n")
