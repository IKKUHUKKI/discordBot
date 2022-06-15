import discord
import random
import os
import asyncio

os.chdir("D:\\Kolja D\\Documents\\Python\\DiscordBot\\Assets")

client = discord.Client()

#I create empty lists to be used later. role_sets contains the role distribution for each possible number of players.
players = []
role_sets = [["L","L","L","F","H"],["L","L","L","L","F","H"],["L","L","L","L","F","F","H"],["L","L","L","L","L","F","F","H"],["L","L","L","L","L","F","F","F","H"],["L","L","L","L","L","L","F","F","F","H"]]
Liberals = []
Fascists = []
Hitler = []

#The player class keep track of all relevant variables for each player, both game wise as coding wise. Each private DM for example is kept as some sort of object under self.user_ID
class Player:
    def __init__(self, author):
        self.user_name = author
        self.user_ID = author.id
        self.was_pres = False
        self.was_canc = False
        self.vote = 0
        self.is_dead = False
        self.is_canc = False
        self.is_pres = False

    def confirm(self, confirm):
        self.confirmed = confirm

    def ini_dm(self, DM):
        self.dm = DM

    def set_index(self, index):
        self.index = index
        
    def role_sel(self, role):
        if role == "L":
            self.role = "Liberal"
            self.identity = "Liberal"
            self.role_file = discord.File("Liberal.png")
            self.colour = discord.Colour.blue()
            Liberals.append(self.user_name)
        elif role == "F":
            self.role = 'Fascist'
            self.identity = "Fascist"
            self.role_file = discord.File("Fascist.png")
            self.colour = discord.Colour.red()
            Fascists.append(self.user_name)
        elif role == "H":
            self.role = "Hitler"
            self.identity = "Fascist"
            self.role_file = discord.File("Hitler.png")
            self.colour = discord.Colour.dark_red()
            Hitler.append(self.user_name)
    def set_pres(self, bool):
        self.is_pres = bool
    def set_canc(self, bool):
        self.is_canc = bool
    def set_was_pres(self, bool):
        self.was_pres = bool
    def set_was_canc(self, bool):
        self.was_canc = bool

    def set_vote(self,int):
        if int == 1:
            self.vote = 1
            self.emoji = ja_emoji
        if int == -1:
            self.vote = -1
            self.emoji = nein_emoji
        if int == 0:
            self.vote = 0
            self.emoji = "None"
    def killed(self, bool):
        self.is_dead = bool



#Define a function that runs once the bot has initialized. Contains required setup
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    global phase
    global turn_counter
    global vote_counter
    global nominate_list
    global election_tracker
    global policy_deck
    global discard_deck
    global fascist_counter
    global liberal_counter
    global veto_unlock
    global first_veto
    global killed_players

    killed_players = 0
    first_veto = True
    veto_unlock = False
    liberal_counter = 0
    fascist_counter = 0
    policy_deck = ["liberal","liberal","liberal","liberal","liberal","liberal","fascist","fascist","fascist","fascist","fascist","fascist","fascist","fascist","fascist","fascist","fascist"]
    random.shuffle(policy_deck)
    discard_deck = []
    nominate_list = []
    turn_counter = -1
    phase = 0
    election_tracker = 0
    vote_counter = 0

#load_emoji is a function I call later on. It looks throught the guild (server)'s emojis and if the required once are not present it will create them. It will only give the bot permission to use said emojis.
async def load_emoji(guild):
    global ja_emoji
    global nein_emoji
    global fas_pol_emoji
    global lib_pol_emoji

    emojis = await guild.fetch_emojis()
    check = 0
    for emoji in emojis:
        if emoji.name == "ja":
            ja_emoji = emoji
            check += 1
        elif emoji.name == 'nein':
            nein_emoji = emoji
            check += 1
        elif emoji.name == 'lib_pol':
            lib_pol_emoji = emoji
            check += 1
        elif emoji.name == 'fas_pol':
            fas_pol_emoji = emoji
            check += 1
    if check == 4:
        return

    roles = await guild.fetch_roles()
    for role in roles:
        if role.name == "Gamey Bot":
            bot_role = role
            break

    with open("Ja.png", 'rb') as ja_file:
        ja_image = ja_file.read()
        ja_emoji = await guild.create_custom_emoji(
            name='ja',
            image=ja_image,
            roles=[bot_role]
        )
    with open("Nein.png", 'rb') as nein_file:
        nein_image = nein_file.read()
        nein_emoji = await guild.create_custom_emoji(
            name='nein',
            image=nein_image,
            roles=[bot_role]
        )
    with open("Lib_pol.png", 'rb') as lib_pol_file:
        lib_pol_image = lib_pol_file.read()
        lib_pol_emoji = await guild.create_custom_emoji(
            name='lib_pol',
            image=lib_pol_image,
            roles=[bot_role]
        )
    with open("Fas_pol.png", 'rb') as fas_pol_file:
        fas_pol_image = fas_pol_file.read()
        fas_pol_emoji = await guild.create_custom_emoji(
            name='fas_pol',
            image=fas_pol_image,
            roles=[bot_role]
        )



#All functions inside here are triggered upon a message being send in either the guild or in a DM with the bot
@client.event
async def on_message(message):
    global phase
    global turn_counter
    global nominate_list
    global election_tracker
    global vote_counter
    global policy_deck
    global discard_deck
    global hand
    global hand_emoji
    global fascist_counter
    global liberal_counter
    global original_players
    global players
    global veto_unlock
    global first_veto
    global killed_players
    if message.author == client.user: #This makes sure the function does nothing on a message send by the bot itself
        return
    for player in players: #Dead players can not interact with the bot
        if message.author == player.user_name and player.is_dead == True:
            return

    if phase == 0: #My code works with phases, each representing a phasse in the game
        if message.content.startswith("!here"): #choose one channel in the guild in which the bot will be active
            if type(message.channel) == discord.channel.DMChannel: #this channel can ofcourse not be a DM channel
                await message.channel.send("Cannot play inside a DM channel.")
                return
            else:
                global game_channel
                global guild
                guild = message.guild
                game_channel = message.channel
                await load_emoji(guild) #Here I load the emojis

                phase = 1 # signup phase
                await game_channel.send("The game will be played in this channel. Join by using !join")
                return
        else:
            return

    if message.channel != game_channel and type(message.channel) != discord.channel.DMChannel: #Commands will only work in the game channel and in DM
        return


    if message.content.startswith('!'): #I choose my commands to start with ! so that is stripped first to read the rest of the command
        command = message.content.strip("!")
        if command.startswith("test"): #Just a test function to see if the image works properly
            await game_channel.send(file=discord.File('Liberal.png'))
            return
        if phase == 1: #Phase 1 is the player gathering
            if command.startswith("join"): # a player can join the game with this command
                if len(players) >= 10:
                    await message.channel.send("The maximum number of players has been reached.")
                    return

                players.append(Player(message.author)) #A list of class instances of all the joined players
                index = len(players)-1
                DM = await players[index].user_name.create_dm() # DM is a variable containing the DM channel of the player that just joined
                players[index].ini_dm(DM) #A player class function to couple the DM channel to the player
                players[index].confirm(False) #If you want you player to confirm their participation in the DM channel you leave this False
                await players[index].dm.send('Confirm your participation by replying with !confirm. You can leave with !leave')
                return


            if command.startswith("confirm"): #Player have to use this command in the DM channel to confirm their participation
                if type(message.channel) == discord.channel.DMChannel:
                    for player in players:
                        if player.user_name == message.author:
                            player.confirm(True)
                            await game_channel.send(str(player.user_name) + ' is now participating.')
                            return
                    await message.channel.send("You haven't joined yet")

                else:
                    await message.channel.send(str(message.author) + " please confirm in a direct message.")

            if command.startswith("leave"): # If a player does not want to join
                for player in players:
                    if player.user_name == message.author:
                        players.remove(player)
                        await game_channel.send(str(message.author) + " has left")

            if command.startswith("start"): #Starts the game
                if message.channel != game_channel:
                    return
                else:
                    try:
                        if command.split()[1] == 'force': #If the command !start force, is given the game will start and force the unconfirmed players out of the game
                            for player in players:
                                if player.confirmed == False: #Uncomfirmed players get removed from the list
                                    players.remove(player)
                    except IndexError: #If only !start is given than this happens
                        unready_list = [] #I create a list of the unconfirmed players and the bot will call them out that they need to confirm their participation
                        for player in players:
                            if player.confirmed == False:
                                unready_list.append(player.user_name)
                        if len(unready_list) != 0:
                            await game_channel.send('\n'.join(str(i) for i in unready_list) + ' have not confirmed yet, force start by using !start force')
                            del unready_list
                            return

                    if len(players) < 5: # The game of course needs enough players, for testing purposes you can lower this to test the later features of the game
                        await message.channel.send("There aren't enough players yet.")
                        return
                    else:
                        original_players = players #List of all players at turn 0
                        random.shuffle(players)
                        await game_channel.send("The turn order is as follows:")
                        for i in range(len(players)):
                            await game_channel.send(str(i+1) + '.   ' + str(players[i].user_name))
                        await game_channel.send("Continue to role selection with !roles")
                        phase = 2 # Role selection, a phase change makes commands of different phases no longer work.
                        return
        elif phase == 2:
            if message.channel != game_channel:
                return
            else:
                if command.startswith("roles"): #randomly distributes the roles among the players
                    role_set = role_sets[len(players)-5]
                    random.shuffle(role_set)

                    for i in range(len(players)):
                        players[i].role_sel(role_set[i])
                        await players[i].dm.send("Your secret role is:") #role is send in DM of course
                        await players[i].dm.send(file=players[i].role_file)
                    await game_channel.send("Everyone has received their roles. The fascists will now meet in secret...")

                    if len(players) <= 6: #In secret hitler the fascists and hitler know each other for a <=6 players
                        for player in players:
                            if player.role == "Fascist" or player.role == "Hitler":
                                await player.dm.send("The fascists are:" + '\n'.join(str(i) for i in Fascists))
                                await player.dm.send("Hitler is: " + str(Hitler[0]))
                            else:
                                await player.dm.send("You'll have to find your comrades in the course of the game.")
                    else: #For a greater number of players only the fascists know eachother and hitler but hitler knows nothing
                        for player in players:
                            if player.role == "Fascist":
                                await player.dm.send("The fascists are:" + '\n'.join(str(i) for i in Fascists))
                                await player.dm.send("Hitler is: " + str(Hitler[0]))
                            else:
                                await player.dm.send("You'll have to find your comrades in the course of the game.")
                    await game_channel.send("The roles are in place the game can now be started with !newturn")
                    phase = 3 # The presidential phase
                    return
        elif phase == 3:
            if message.channel != game_channel:
                return
            else:
                if command.startswith('newturn'): #every turn is started with this comamand. Did not automate this because I wanted full control of the bot
                    turn_counter += 1
                    if turn_counter >= len(players):
                        turn_counter = 0
                    for i in range(len(players)):
                        if i == turn_counter and players[i].is_dead == True: #dead players don't get to play
                            turn_counter += 1
                            if turn_counter >= len(players):
                                turn_counter = 0
                    for i in range(len(players)):
                        if i == turn_counter:
                            players[i].set_pres(True) #the presidency status is passed every turn
                            await game_channel.send("The president is: " + str(players[i].user_name))
                    await game_channel.send("The president can nominate a chancellor using !nominate {username}")
                    phase = 4 # nomination phase
                    return
        elif phase == 4:
            if message.channel != game_channel:
                return
            else:
                print("check1") #some checks for the code, seen in the python console
                if command.startswith('nominate'): #president nominates someone
                    print("check2")
                    for player in players:
                        print(player.is_pres)
                        if message.author == player.user_name and player.is_pres == True: #only the president can use this command
                            print("check3")
                            try:
                                for player_i in players:
                                    if command.split()[1] == str(player_i.user_name) and player_i.is_pres != True and player_i.was_canc != True and ((player_i.was_pres != True) or len(players)<=5): #some logic as to who is allowed to be president
                                        nominate_list.append(player_i) #the nominated player is put in a list
                                        await game_channel.send("The president nominated: " + str(player_i.user_name))
                                        await game_channel.send("Everyone can now vote for a government with " + str(player.user_name) + " as president and " + str(player_i.user_name) + " as chancellor.")
                                        await game_channel.send("Vote by sending either !Ja or !Nein in the DM chat.")
                                        phase = 5 # voting phase
                                        return
                                await game_channel.send("A non existing user was selected")
                                return
                            except IndexError:
                                await game_channel.send("Specify who you'd like to nominate.")
                                return
                    else:
                        return
        elif phase == 5:
            if message.channel == game_channel:
                if command.startswith("results"): #sees the result of the vote, vote function is below
                    if vote_counter == len(players) - killed_players:
                        vote_counter = 0
                        vote_total = 0
                        for player in players:
                            await game_channel.send(str(player.user_name) + " has voted: " + str(player.emoji)) #send who voted what in the game channel
                            vote_total += player.vote #ja vote is 1, nein vote is -1
                            player.set_vote(0)
                        if vote_total > 0:
                            if nominate_list[0].role == "Hitler" and fascist_counter >= 3: #Game ends if hitler elected after 3 fascist policies
                                await game_channel.send("Hitler was enacted as chancellor, the fascists win. The roles were as follows:")
                                phase = 99
                                for player in original_players:
                                    await game_channel.send(str(player.user_name) + "'s role was: " + player.role)
                                return
                            await game_channel.send("The vote was a success. The president will now draw three policy cards.")
                            for player_j in players:
                                if player_j == nominate_list[0]: #the nominated player becomes chancellor
                                    player_j.set_canc(True)
                            nominate_list = []
                            hand = policy_deck[:3] #pres draw top 3 cards
                            hand_emoji = []
                            for card in hand: #3 cards get their representing emoji put in a list
                                if card == "liberal":
                                    hand_emoji.append(lib_pol_emoji)
                                elif card == "fascist":
                                    hand_emoji.append(fas_pol_emoji)
                            del policy_deck[:3] #3 cards get deleted from the plit
                            if len(policy_deck) < 3: #reshuffles empty deck
                                discard_deck = []
                                policy_deck = ["liberal","liberal","liberal","liberal","liberal","liberal","fascist","fascist","fascist","fascist","fascist","fascist","fascist","fascist","fascist","fascist","fascist"]
                                random.shuffle(policy_deck)
                                await game_channel.send("Reshuffling the deck.")
                            for player in players:
                                if player.is_pres == True:
                                    await player.dm.send("You've drawn: " + ' '.join(str(card) for card in hand_emoji) + ". Discard one card using !discard fascist/liberal.")
                            phase = 6  # policy selection
                            return
                        else: #failed chanc nomination, retry, and electrion tracker moves one space
                            await game_channel.send("The vote has failed. A new election will be held by using !newturn. The election tracker will move one space.")
                            phase = 3
                            election_tracker += 1
                            nominate_list = []
                            await game_channel.send("The election tracker is now on space: " + str(election_tracker))
                            if election_tracker == 3: ##add chaos function
                                await chaos()

                    return
            elif type(message.channel) == discord.channel.DMChannel:
                if command.startswith("Ja") or command.startswith("Nein"): #the voting commands
                    for player in players:
                        if message.author == player.user_name:
                            if player.vote != 0: #players can recast their vote, before results are revealed of course
                                if command.startswith("Ja"):
                                    player.set_vote(1)
                                    await message.channel.send("You have changed your vote to: " + str(player.emoji))
                                else:
                                    player.set_vote(-1)
                                    await message.channel.send("You have changed your vote to: " + str(player.emoji))
                            else:
                                if command.startswith("Ja"):
                                    player.set_vote(1)
                                    await message.channel.send("You have voted: " + str(player.emoji))
                                else:
                                    player.set_vote(-1)
                                    await message.channel.send("You have voted: " + str(player.emoji))
                                vote_counter += 1
                            if vote_counter == len(players)-killed_players:
                                await game_channel.send("Everyone has voted. View the results with !results")



        elif phase == 6:

            try:
                if command.startswith("discard") and (command.split()[1] == "fascist" or command.split()[1] == "liberal"): #the president discards one of the three cards
                    for player in players:
                        if player.dm == message.channel and player.is_pres == True:
                            if command.split()[1] in hand:
                                await player.dm.send("You have discarded " + str(hand_emoji[hand.index(command.split()[1])]))
                                await game_channel.send("The president has discarded a policy.")
                                discard_deck.append(command.split()[1])
                                del hand_emoji[hand.index(command.split()[1])]
                                del hand[hand.index(command.split()[1])]
                                for player_i in players:
                                    if player_i.is_canc == True: #the other two cards get passed to the chancellor
                                        await player_i.dm.send("The president has given you: " + ' '.join(str(card) for card in hand_emoji) + ". Enact one using !enact liberal/fascist.")
                                        phase = 7
                            else:
                                await player.dm.send("You don't have that card, so you cannot discard it.")
            except IndexError:
                return
        elif phase == 7:
            try:
                if command.startswith("veto") and first_veto == True and veto_unlock == True: #veto power unlocks later in the game
                    for player in players:
                        if player.dm == message.channel and player.is_canc == True:
                            await game_channel.send("The chancellor veto's this agenda. The president can accept or deny the veto by using !accept/!deny")
                            phase = 11
                            return
                elif command.startswith("enact") and (command.split()[1] == "fascist" or command.split()[1] == "liberal"): #one of the remaining two cards is enacted, the hands get reset and the played deck is updated
                    for player in players:
                        if player.dm == message.channel and player.is_canc == True:
                            if command.split()[1] in hand:
                                first_veto = True
                                await game_channel.send("The chancellor as enacted: " + str(hand_emoji[hand.index(command.split()[1])]))
                                discard_deck.append(command.split()[1])
                                del hand_emoji[hand.index(command.split()[1])]
                                del hand[hand.index(command.split()[1])]
                                discard_deck.append(hand[0])
                                del hand[0]
                                del hand_emoji[0]
                                if command.split()[1] == "fascist":
                                    fascist_counter += 1
                                    await update_deck()
                                else:
                                    liberal_counter += 1
                                    await update_deck()
                                return
            except IndexError:
                return

        elif phase == 8: #pres power to invesitgate one player
            try:
                if command.startswith("investigate"):
                    for player in players:
                        if message.channel == game_channel and player.is_pres == True:
                            for player_i in players:
                                if command.split()[1] == str(player_i.user_name) and player != player_i:
                                    await player.dm.send(str(player_i.user_name) + "'s party is: " + player_i.identity)
                                    await game_channel.send("Continue to the next turn by using !newturn")
                                    await update_pres()
                                    phase = 3
                                else:
                                    await message.channel.send("Player not found.")
            except IndexError:
                return

        elif phase == 9: #the president may elect the next president. Turn counter increase is prevented meaning after the turn it will resume where it should
            try:
                if command.startswith("elect"):
                    for player in players:
                        if message.channel == game_channel and player.is_pres == True:
                            for player_i in players:
                                if command.split()[1] == str(player_i.user_name) and player != player_i:
                                    await update_pres()
                                    player_i.set_pres(True)
                                    await game_channel.send(str(player_i.user_name) + " is the next president.\nThe president can nominate a chancellor using !nominate {username}")
                                    phase = 4 #jumps to the nomination phase
                                else:
                                    await message.channel.send("Player not found.")
            except IndexError:
                return

        elif phase == 10: #the pres has the power to kill one of the players
            try:
                if command.startswith("execute"):
                    for player in players:
                        if message.channel == game_channel and player.is_pres == True:
                            for player_i in players:
                                if command.split()[1] == str(player_i.user_name) and player != player_i:
                                    await update_pres()
                                    if player_i.role == "Hitler":
                                        await game_channel.send("Hitler was killed, the liberals win. The roles were as follows:")
                                        phase = 99
                                        for player in original_players:
                                            await game_channel.send(str(player.user_name) + "'s role was: " + player.role)
                                        return
                                    else:
                                        await game_channel.send(str(player_i.user_name) + " has been executed and is no longer part of the game.")
                                        await game_channel.send("Continue to the next turn by using !newturn")
                                        killed_players += 1
                                        player_i.killed(True)
                                        phase = 3
                            else:
                                await message.channel.send("Player not found.")
            except IndexError:
                return

        elif phase == 11:
            if command.startswith("deny"): # if pres deny veto the chanc will have to choose one of the twwo cards.
                for player in players:
                    if player.is_pres == True and player.user_name == message.author:
                        await game_channel.send("The president refuses the veto. The chancellor will be forced to enact a policy.")
                        first_veto = False
                        phase = 7
                    else:
                        return
            elif command.startswith("accept"): #if the veto is accepted the turn is over, election tracker moves one place.
                for player in players:
                    if player.is_pres == True and player.user_name == message.author:
                        await game_channel.send("The president agrees to the veto. This election is over and the election tracker will progress by one.")
                        hand = []
                        hand_emoji = []
                        election_tracker += 1
                        if election_tracker == 3: ## add chaos function
                            await chaos()
                        await game_channel.send("Continue to the next turn by using !newturn")
                        await update_pres()
                        phase = 3



async def update_deck(chaos=False): # a function which updates the played fascist and liberal cards, at certain milestones a power is enacted. If chaos is True, none of these powers can be used
    global phase
    global turn_counter
    global nominate_list
    global election_tracker
    global vote_counter
    global policy_deck
    global discard_deck
    global hand
    global hand_emoji
    global fascist_counter
    global liberal_counter
    global original_players
    global players
    global veto_unlock
    global first_veto

    await game_channel.send("There are " + str(liberal_counter) + " " + str(lib_pol_emoji) + " enacted.")
    await game_channel.send("There are " + str(fascist_counter) + " " + str(fas_pol_emoji) + " enacted.")

    if chaos == True:
        return
    elif fascist_counter == 1 and len(players) >= 9:
        await game_channel.send(
            "The president may choose to investigate one player's identity card by using !investigate {player}")
        phase = 8
        return

    elif fascist_counter == 2 and len(players) >= 7:
        await game_channel.send(
            "The president may choose to investigate one player's identity card by using !investigate {player}")
        phase = 8
        return

    elif fascist_counter == 3 and len(players) >= 7:
        await game_channel.send("The president may elect the next president by using !elect {president}")
        phase = 9
        return


    elif fascist_counter == 3 and len(players) <= 6:
        await game_channel.send(
            "The third fascist policy has been enacted. The president will now view the top three cards in the deck")
        examine = policy_deck[:3]
        examine_emoji = []
        for card in examine:
            if card == "liberal":
                examine_emoji.append(lib_pol_emoji)
            elif card == "fascist":
                examine_emoji.append(fas_pol_emoji)
        for player in players:
            if player.is_pres == True:
                await player.dm.send(
                    "The top three cards of the deck are: " + ' '.join(str(card) for card in examine_emoji))
        del examine
        del examine_emoji
        phase = 3
        await update_pres()
        await game_channel.send("Continue to next turn by using !newturn")
        return

    elif fascist_counter == 4 or fascist_counter == 5:
        if fascist_counter == 4:
            await game_channel.send(
                "The fourth fascist policy has been enacted. The president must kill a player by using !execute {player}.")
        else:
            await game_channel.send(
                "The fifth fascist policy has been enacted. The president must kill a player by using !execute {player}.\n The veto power has now been unlocked. A chancellor can choose to veto an agenda by using !veto instead of !enact.")
            veto_unlock = True
        phase = 10
        return

    elif fascist_counter == 6:
        await game_channel.send("The Fascists have won after enacting six fascist policies! The roles were as follows:")
        phase = 99
        for player in original_players:
            await game_channel.send(str(player.user_name) + "'s role was: " + player.role)
        return
    elif liberal_counter == 5:
        await game_channel.send("The Liberals have won after enacting five liberal policies! The roles were as follows:")
        phase = 99
        for player in original_players:
            await game_channel.send(str(player.user_name) + "'s role was: " + player.role)
        return
    else:
        phase = 3
        await update_pres()
        await game_channel.send("Continue to next turn by using !newturn")
        return



async def chaos(): #when election tracked is moved to 3 spaces, the top policy will be enacted without any powers triggering
    global policy_deck
    global discard_deck
    global fascist_counter
    global liberal_counter

    top_card = policy_deck[0]
    if top_card == 'fascist':
        await game_channel.send("The following policy was enacted by the people: " + str(fas_pol_emoji))
        fascist_counter += 1
        await update_deck(True)

    elif top_card == 'liberal':
        await game_channel.send("The following policy was enacted by the people: " + str(lib_pol_emoji))
        liberal_counter += 1
        await update_deck(True)

    if len(policy_deck) < 3:
        discard_deck = []
        policy_deck = ["liberal", "liberal", "liberal", "liberal", "liberal", "liberal", "fascist", "fascist",
                       "fascist", "fascist", "fascist", "fascist", "fascist", "fascist", "fascist", "fascist",
                       "fascist"]
        random.shuffle(policy_deck)
        await game_channel.send("Reshuffling the deck.")

async def update_pres(): #updates who was pres and chanc the previous round
    for player in players:
        if player.is_pres == True:
            player.set_was_pres(True)
            player.set_pres(False)
            player.set_canc(False)
            player.set_was_canc(False)

        elif player.is_canc == True:
            player.set_was_canc(True)
            player.set_canc(False)
            player.set_was_pres(False)
            player.set_pres(False)
        else:
            player.set_was_canc(False)
            player.set_was_pres(False)
            player.set_pres(False)
            player.set_canc(False)






client.run('') #fill in the bot code here.
