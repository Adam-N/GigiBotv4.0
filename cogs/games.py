import asyncio
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
import random

from discord.ui import View

class AceButton(View):
    def __init__(self):
        super().__init__(timeout=10)
        self.value = None

    @discord.ui.button(label="1", style=discord.ButtonStyle.blurple, custom_id=f"one")
    async def one(self, interaction, button):
        self.value = 1
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="11", style=discord.ButtonStyle.green, custom_id=f"eleven")
    async def eleven(self, interaction, button):
        self.value = 11
        await interaction.response.defer()
        self.stop()


class PlayButtons(View):
    def __init__(self):
        super().__init__(timeout=10)
        self.value = None

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.blurple, custom_id=f"hit")
    async def hit(self, interaction, button):
        self.value = "HIT"
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.green, custom_id=f"stand")
    async def stand(self, interaction, button):
        self.value = "STAND"
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Double Down", style=discord.ButtonStyle.red, custom_id=f"double")
    async def double(self, interaction, button):
        self.value = "DOUBLEDOWN"
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Split", style=discord.ButtonStyle.red, custom_id=f"split")
    async def split(self, interaction, button):
        self.value = "SPLIT"
        await interaction.response.defer()
        self.stop()


class Games(commands.Cog):
    """Contains Games"""

    def __init__(self, bot):
        self.bot = bot
        self.cards = []
        self.card_values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'Ace', 'King', 'Queen', 'Jack']
        self.face_cards = ['King', 'Queen', 'Jack']
        self.suit_values = ['Spade', 'Heart', 'Club', 'Diamond']
        self.card_emojies = {'Spade': '\U00002660\U0000fe0f', 'Heart': '\U00002665\U0000fe0f',
                             'Club': '\U00002663\U0000fe0f', 'Diamond': '\U00002666\U0000fe0f'}

    async def build_view(self, view, hand: int, split=False):
        if hand == 1 and not split:
            view = view.remove_item(view.split)
        if hand > 1:
            view = view.remove_item(view.double)
            view = view.remove_item(view.split)
        return view

    async def edit_embed(self, to_change, embed, string, hand_2=""):
        dict = embed.to_dict()
        if to_change == 'dealer':
            try:
                if dict['description']:
                    embed = discord.Embed(title=dict['title'], description=dict['description'], type='rich', colour=dict['color'])
            except KeyError:
                embed = discord.Embed(title=dict['title'], type='rich', colour=dict['color'])
            try:
                 if dict['fields'][2]['value']:
                    embed.add_field(name="Dealer Hand",
                                    value=string,
                                    inline=False)
                    embed.add_field(name="Hand 1",
                                    value=dict['fields'][1]['value'],
                                    inline=False)
                    embed.add_field(name="Hand 2",
                                    value=dict['fields'][2]['value'],
                                    inline=False)
            except IndexError:
                embed.add_field(name="Dealer Hand",
                                value=string,
                                inline=False)
                embed.add_field(name="Your Hand",
                                value=dict['fields'][1]['value'],
                                inline=False)
            return embed
        elif to_change == 'player':
            embed = discord.Embed(title=dict['title'], type='rich', colour=dict['color'])
            try:
                if dict['description']:
                    embed.description = dict['description']
            except KeyError:
                pass
            embed.add_field(name="Dealer Hand",
                            value=dict['fields'][0]['value'],
                            inline=False)
            embed.add_field(name="Your Hand",
                            value=string,
                            inline=False)
            return embed
        elif to_change == "split1":
            embed = discord.Embed(title=dict['title'], type='rich', colour=dict['color'])
            embed.add_field(name="Dealer Hand",
                            value=dict['fields'][0]['value'],
                            inline=False)
            embed.add_field(name="Hand 1",
                            value=string,
                            inline=False)
            embed.add_field(name="Hand 2",
                            value=hand_2,
                            inline=False)
            return embed
        elif to_change == "split2":
            embed = discord.Embed(title=dict['title'], type='rich', colour=dict['color'])
            embed.add_field(name="Dealer Hand",
                            value=dict['fields'][0]['value'],
                            inline=False)
            embed.add_field(name="Hand 1",
                            value=dict['fields'][1]['value'],
                            inline=False)
            embed.add_field(name="Hand 2",
                            value=string,
                            inline=False)
            return embed

    @app_commands.command(name='blackjack')
    async def blackjack(self, interaction: discord.Interaction):
        """Play some blackjack!"""
        await interaction.response.defer()
        if len(self.cards) > 45:
            self.cards = []
        game = True
        dealer = True
        dealer_cards = await self.deal()
        player_cards = await self.deal()

        # For Testing
        # player_cards = [[2, 'Spade'], [2, 'Heart']]

        hand1 = None
        hand2 = None

        hand1_bust = False
        hand2_bust = False

        split_aces = False
        split = False

        play_colour = 0x00e4f5
        win_colour = 0x35f500
        lose_colour = 0xf50000

        player_bj_check = await self.blackjack_check(player_cards)
        dealer_bj_check = await self.blackjack_check(dealer_cards)

        dealer_dict = await self.hand_value(dealer_cards, self.bot.user, interaction.channel)
        dealer_total = dealer_dict['total']
        one_card_total = dealer_dict['dealer_total']
        dealer_card_string = dealer_dict['dealer']

        player_dict = await self.hand_value(player_cards, interaction.user, interaction.channel)
        player_total = player_dict['total']
        player_card_string = player_dict['card_string']



        embed = discord.Embed(title="Blackjack",
                              colour= play_colour,
                              timestamp=datetime.now(),
                              type="rich")

        embed.add_field(name="Dealer Hand",
                        value=f'`{dealer_card_string}, score {one_card_total}`',
                        inline=False)
        embed.add_field(name="Your Hand",
                        value=f'`{player_card_string}, score {player_total}`',
                        inline=False)

        await interaction.followup.send(embed=embed)
        game_message = await interaction.original_response()

        if player_bj_check and player_total == 21 and not dealer_bj_check:
            embed = await self.edit_embed("dealer", game_message.embeds[0],
                                          f'`{dealer_dict["card_string"]}, score {dealer_total}`')
            embed.description = "# **You win! Blackjack!**"
            embed.color = win_colour
            await game_message.edit(embed=embed, view=None)
            return
        elif dealer_bj_check and player_bj_check:
            embed = await self.edit_embed("dealer", game_message.embeds[0],
                                          f'`{dealer_dict["card_string"]}, score {dealer_total}`')
            embed.description = "# **Dealer pushes**"
            embed.color = win_colour
            await game_message.edit(embed=embed, view=None)
            return
        elif dealer_bj_check and not player_bj_check:
            embed = await self.edit_embed("dealer", game_message.embeds[0],
                                          f'`{dealer_dict["card_string"]}, score 21`')
            embed.description = "# **Dealer Blackjack! You lose.**"
            embed.color = lose_colour
            await game_message.edit(embed=embed)
            return

        i = 1
        hand = 1
        while game:
            try:
                if "SPLIT" == player_cards[0][0] and i == 1:
                    view = await self.build_view(PlayButtons(), i, split)
                    await game_message.edit(content=f"# Playing Hand {hand}",embed=embed, view=view)
                elif i == 1 and (player_cards[0][0] == player_cards[1][0] or
                                 (player_cards[0][0] in self.face_cards and player_cards[1][0] in self.face_cards)):
                    split = True
                    view = await self.build_view(PlayButtons(), i, split)
                    await game_message.edit(embed=embed, view=view)
                    split = False
                elif i == 1 and not player_cards[0][0] == player_cards[1][0]:
                    view = await self.build_view(PlayButtons(), i, split)
                    await game_message.edit(embed=embed, view=view)
                elif i > 1:
                    view = await self.build_view(PlayButtons(), i, split)
                    await game_message.edit(embed=embed, view=view)

                await view.wait()


            except asyncio.TimeoutError:
                await interaction.followup.send('Timed out. Try again!')
                return

            if view.value == "SPLIT" and (player_cards[0][0] == player_cards[1][0] or
                             (player_cards[0][0] in self.face_cards and player_cards[1][0] in self.face_cards)):
                if player_cards[0][0] == "Ace" and player_cards[1][0] == "Ace":
                    split_aces = True
                hand1 = [player_cards[0]]
                hand2 = [player_cards[1]]
                player_cards = [["SPLIT", 0], [1, 1]]
                card1 = await self.get_card()
                card2 = await self.get_card()
                hand1.append(list(card1))
                hand2.append(list(card2))
                hand1_dict = await self.hand_value(hand1, interaction.user, interaction.channel)
                hand1_string = hand1_dict['card_string']
                hand1_total = hand1_dict['total']
                hand2_dict = await self.hand_value(hand2, interaction.user, interaction.channel)
                hand2_string = hand2_dict['card_string']
                hand2_total = hand2_dict['total']
                embed = await self.edit_embed("split1",
                                              game_message.embeds[0],f" `{hand1_string}. Score: {hand1_total}`",
                                              hand_2=f"`{hand2_string}. Score: {hand2_total}`")
                game_message = await game_message.edit(embed=embed, view=None)
                if split_aces:
                    break
                if hand1_total == 21:
                    hand = 2
                if hand1_total and hand2_total == 21:
                    break

            if view.value == "STAND" and hand == 1 and 'SPLIT' == player_cards[0][0]:
                i = 1
                hand = 2
                continue
            elif view.value == "HIT" or view.value == "DOUBLEDOWN":
                if 'SPLIT' != player_cards[0][0]:
                    cards = await self.get_card()
                    player_cards.append(cards)
                    if view.value == "DOUBLEDOWN":
                        doubledown = True
                    else:
                        doubledown = False

                    player_dict = await self.hand_value(player_cards, interaction.user, interaction.channel)
                    player_total = player_dict['total']
                    player_card_string = player_dict['card_string']
                    embed = await self.edit_embed("player",
                                                  game_message.embeds[0], f"`{player_card_string}, score {player_total}`")
                    game_message = await game_message.edit(embed=embed)
                    if player_total > 21:
                        embed = await self.edit_embed( "dealer", game_message.embeds[0],
                                                      f'`{dealer_dict["card_string"]}, score {dealer_total}`')
                        embed.description = '# You __**BUSTED**__'
                        embed.color = lose_colour
                        await game_message.edit(embed=embed, view=None)
                        return
                    elif doubledown:
                        break
                    elif player_total == 21:
                        break
                elif "SPLIT" == player_cards[0][0]:
                    if hand == 1:
                        cards = await self.get_card()
                        hand1.append(cards)
                        if view.value == "DOUBLEDOWN":
                            doubledown = True
                        else:
                            doubledown = False
                        player_dict = await self.hand_value(hand1, interaction.user, interaction.channel)
                        hand1_total = player_dict['total']
                        hand1_string = player_dict['card_string']
                        embed = await self.edit_embed("split1",
                                                      game_message.embeds[0],
                                                       f'`{hand1_string}, score {hand1_total}`',
                                                      hand_2=f"`{hand2_string}. Score: {hand2_total}`")
                        game_message = await game_message.edit(embed=embed)
                        if hand1_total > 21:
                            embed = await self.edit_embed("split1",
                                                          game_message.embeds[0],
                                                          f'`{hand1_string}, score {hand1_total}` **Busted Hand 1**',
                                                          hand_2=f"`{hand2_string}. Score: {hand2_total}`")
                            hand1_bust = True
                            game_message = await game_message.edit(embed=embed)
                            hand = 2
                            i = 1
                            continue
                        elif doubledown:
                            hand = 2
                            i = 1
                            continue
                        elif player_total == 21:
                            hand = 2
                            i = 1
                            continue
                        i+=1
                        continue
                    if hand == 2:
                        cards = await self.get_card()
                        hand2.append(cards)
                        if view.value == "DOUBLEDOWN":
                            doubledown = True
                        else:
                            doubledown = False
                        player_dict = await self.hand_value(hand2, interaction.user, interaction.channel)
                        hand2_total = player_dict['total']
                        hand2_card_string = player_dict['card_string']
                        embed = await self.edit_embed("split2",
                                                      game_message.embeds[0],
                                                       f'`{hand2_card_string}, score {hand2_total}`')
                        game_message = await game_message.edit(embed=embed)
                        if hand2_total > 21:
                            embed = await self.edit_embed("split2",
                                                          game_message.embeds[0],
                                                          f'`{hand2_card_string}, score {hand2_total}` **Busted Hand 2**')
                            game_message = await game_message.edit(embed=embed)
                            hand2_bust = True
                            break
                        elif doubledown:
                            i += 1
                            break
                        elif player_total == 21:
                            i += 1
                            break
                        i+=1

                i += 1

            elif view.value == "STAND" or (view.value == "DOUBLEDOWN" and i > 1):
                break
        while dealer:
            if dealer_total >= 18:
                break
            cards = await self.get_card()
            dealer_cards.append(cards)
            dealer_dict = await self.hand_value(dealer_cards, self.bot.user, interaction.channel)
            dealer_total = dealer_dict['total']
            dealer_card_string = dealer_dict['card_string']
            embed = await self.edit_embed("dealer",
                                          game_message.embeds[0],
                                          f' `{dealer_card_string}, score {dealer_total}`')
            game_message = await game_message.edit(embed=embed)
            if dealer_total > 21:
                embed.description = f'# Dealer __**BUSTED**__'
                embed.color = win_colour
                await game_message.edit(content= "",embed=embed, view=None)
                return
            if dealer_total == 21:
                dealer = False
                break
            if dealer_total > 18:
                dealer = False
                break
        if player_cards[0][0] != 'SPLIT':
            if dealer_total == player_total:
                embed = await self.edit_embed("dealer", game_message.embeds[0],
                                          f' `{dealer_dict["card_string"]}, score {dealer_total}`')
                embed.description = "# **Dealer pushes**"
                embed.color = win_colour
                await game_message.edit(content= "",embed=embed, view=None)
            elif dealer_total > player_total:
                embed = await self.edit_embed("dealer",
                                              game_message.embeds[0],
                                              f' `{dealer_dict["card_string"]}, score {dealer_total}`')
                embed.description = "# **Dealer** wins"
                embed.color = lose_colour

                await game_message.edit(content= "",embed=embed, view=None)
            elif player_total > dealer_total:
                embed = await self.edit_embed("dealer",
                                              game_message.embeds[0],
                                              f' `{dealer_dict["card_string"]}, score {dealer_total}`')
                embed.description = "# \U0001f387 **You win** \U0001f387"
                embed.color = win_colour
                await game_message.edit(content= "",embed=embed, view=None)

        elif player_cards[0][0] == 'SPLIT':
            embed = await self.edit_embed("dealer",
                                          game_message.embeds[0],
                                          f' `{dealer_dict["card_string"]}, score {dealer_total}`')
            if hand1_bust:
                hand_1_result = " "
            elif hand1_total > dealer_total and not hand1_bust:
                hand_1_result = "# \U0001f387 **You win __hand 1__** \U0001f387"
            elif hand1_total == dealer_total and not hand1_bust:
                hand_1_result = '# **Dealer pushes on __hand 1__**'
            elif hand1_total < dealer_total and not hand1_bust:
                hand_1_result = '# **Dealer wins on __hand 1__**'

            if hand2_bust:
                embed.description = hand_1_result + " "
                await game_message.edit(content= "",embed=embed, view=None)
            elif hand2_total > dealer_total and not hand2_bust:
                embed.description = hand_1_result + "\n# \U0001f387 **You win __hand 2__** \U0001f387"
                await game_message.edit(content= "",embed=embed, view=None)
            elif hand2_total == dealer_total:
                embed.description = hand_1_result + '\n# **Dealer pushes on __hand 2__**'
                await game_message.edit(content= "",embed=embed, view=None)
            elif hand2_total < dealer_total:
                embed.description = hand_1_result + "\n# **Dealer wins on __hand 2__**"
                await game_message.edit(content="",embed=embed, view=None)

    async def deal(self):
        card_1 = await self.get_card()
        self.cards.append(card_1)
        card_2 = await self.get_card()
        self.cards.append(card_2)
        dealt = [card_1, card_2]
        return dealt

    async def get_card(self):
        card = [random.choice(self.card_values), random.choice(self.suit_values)]
        if self.cards:
            while card in self.cards:
                card = [random.choice(self.card_values), random.choice(self.suit_values)]
        return card

    async def hand_value(self, cards, player, channel):
        dict = {}
        hand_total = 0
        card_string = ""
        x = 1
        bj_check = await self.blackjack_check(cards)

        acenumber = sum(x.count("Ace") for x in cards)
        for list in cards:
            for element in list:
                if element in self.card_values:
                    if element in self.face_cards:
                        hand_total += 10
                    elif isinstance(element, int):
                        if element < 11:
                            hand_total += element
                    elif 'Ace' in cards and player.bot:
                        hand_total += 11
                if element in self.card_values:
                    card_string += str(element)
                if element in self.card_emojies.keys():
                    emoji = self.card_emojies[element]
                    card_string += emoji
                    card_string += " "
        if not player.bot and not bj_check:
            if 'Ace' in card_string:
                if hand_total + 11  > 21 and acenumber == 1:
                    hand_total += 1
                elif hand_total + 11 < 21 and acenumber == 1:
                    hand_total += 11
                elif hand_total + (11 + (1 * (acenumber-1))) < 21 and acenumber > 1:
                    hand_total += (11 + (1 * (acenumber-1)))
                elif hand_total + acenumber < 21 and acenumber > 2:
                    hand_total += acenumber
                else:
                    while x <= acenumber:
                        try:
                            view = AceButton()
                            acemessage = await channel.send(f'`Value for your ace? 1 or 11. Cards are '
                                                                         f'{card_string}`',
                                                                         view=view)
                            await view.wait()

                            if 1 == view.value:
                                acevalue = 1
                                x += 1
                                await acemessage.delete()
                                hand_total += acevalue

                            elif 11 == view.value:
                                x += 1
                                acevalue = 11
                                await acemessage.delete()
                                hand_total += acevalue

                        except asyncio.TimeoutError:
                            await channel.send("Timeout. Try again.")
        elif not player.bot and bj_check:
            hand_total += 11
        if player.bot:
            dealer_total = cards[0][0]
            dealer_hand = str(cards[0][0]) + self.card_emojies[cards[0][1]]
            if 'Ace' in cards:
                dict['dealer_total'] = 11
            elif cards[0][0] in self.face_cards:
                dict['dealer_total'] = 10
            else:
                dict['dealer_total'] = dealer_total
            dict['dealer'] = dealer_hand

            if 'Ace' in cards:

                if len(cards) >= 3:
                    hand_total -= 10

        dict['total'] = hand_total
        dict['card_string'] = card_string
        return dict

    async def blackjack_check(self, cards):
        ten = False
        ace = False
        for list in cards:
            for element in list:
                if element in self.face_cards or element == 10:
                    ten = True
            if 'Ace' in list:
                ace = True
        if ten and ace:
            return True
        else:
            return False


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Games(bot))