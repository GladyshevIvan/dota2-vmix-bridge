import aiohttp


#Словарь с id-героя и его названием
HEROES = {1: 'Anti-Mage', 2: 'Axe', 3: 'Bane', 4: 'Bloodseeker', 5: 'Crystal Maiden',
          6: 'Drow Ranger', 7: 'Earthshaker', 8: 'Juggernaut', 9: 'Mirana', 10: 'Morphling',
          11: 'Shadow Fiend', 12: 'Phantom Lancer', 13: 'Puck', 14: 'Pudge', 15: 'Razor',
          16: 'Sand King', 17: 'Storm Spirit', 18: 'Sven', 19: 'Tiny', 20: 'Vengeful Spirit',
          21: 'Windranger', 22: 'Zeus', 23: 'Kunkka', 25: 'Lina',
          26: 'Lion', 27: 'Shadow Shaman', 28: 'Slardar', 29: 'Tidehunter', 30: 'Witch Doctor',
          31: 'Lich', 32: 'Riki', 33: 'Enigma', 34: 'Tinker', 35: 'Sniper',
          36: 'Necrophos', 37: 'Warlock', 38: 'Beastmaster', 39: 'Queen of Pain', 40: 'Venomancer',
          41: 'Faceless Void', 42: 'Wraith King', 43: 'Death Prophet', 44: 'Phantom Assassin', 45: 'Pugna',
          46: 'Templar Assassin', 47: 'Viper', 48: 'Luna', 49: 'Dragon Knight', 50: 'Dazzle',
          51: 'Clockwerk', 52: 'Leshrac', 53: 'Nature"s Prophet', 54: 'Lifestealer', 55: 'Dark Seer',
          56: 'Clinkz', 57: 'Omniknight', 58: 'Enchantress', 59: 'Huskar', 60: 'Night Stalker',
          61: 'Broodmother', 62: 'Bounty Hunter', 63: 'Weaver', 64: 'Jakiro', 65: 'Batrider',
          66: 'Chen', 67: 'Spectre', 68: 'Ancient Apparition', 69: 'Doom', 70: 'Ursa',
          71: 'Spirit Breaker', 72: 'Gyrocopter', 73: 'Alchemist', 74: 'Invoker', 75: 'Silencer',
          76: 'Outworld Destroyer', 77: 'Lycan', 78: 'Brewmaster', 79: 'Shadow Demon', 80: 'Lone Druid',
          81: 'Chaos Knight', 82: 'Meepo', 83: 'Treant Protector', 84: 'Ogre Magi', 85: 'Undying',
          86: 'Rubick', 87: 'Disruptor', 88: 'Nyx Assassin', 89: 'Naga Siren', 90: 'Keeper of the Light',
          91: 'Io', 92: 'Visage', 93: 'Slark', 94: 'Medusa', 95: 'Troll Warlord',
          96: 'Centaur Warrunner', 97: 'Magnus', 98: 'Timbersaw', 99: 'Bristleback', 100: 'Tusk',
          101: 'Skywrath Mage', 102: 'Abaddon', 103: 'Elder Titan', 104: 'Legion Commander', 105: 'Techies',
          106: 'Ember Spirit', 107: 'Earth Spirit', 108: 'Underlord', 109: 'Terrorblade', 110: 'Phoenix',
          111: 'Oracle', 112: 'Winter Wyvern', 113: 'Arc Warden', 114: 'Monkey King', 119: 'Dark Willow', 120: 'Pangolier',
          121: 'Grimstroke', 123: 'Hoodwink', 126: 'Void Spirit', 128: 'Snapfire', 129: 'Mars', 131: 'Ringmaster',
          135: 'Dawnbreaker', 136: 'Marci', 137: 'Primal Beast', 138: 'Muerta', 145: 'Kez'}


def get_team_name(isRadiant, teams_stats):
    '''
    Определение названия команды для игрока по isRadiant

    Args:
        isRadiant (bool): True - если сторона radiant, Fale - если нет
        teams_stats (dict): словарь, который содержит в себе счет и названия команд

    Return str: название команды
    '''

    if isRadiant:
        return teams_stats['radiant']['name']
    return teams_stats['dire']['name']


async def get_match_stats_from_api(match_id):
    '''
    Получение статистики матча через API

    Args:
        match_id (str): id игры

    Return:
        (dict): словарь из teams_stats - счет и названия команд; players_stats - статистика игроков
    '''

    apiUrl = f'https://api.opendota.com/api/matches/{match_id}'
    async with aiohttp.ClientSession() as session:
        async with session.get(apiUrl) as response:
            data = await response.json()

            #Объявление словарей, где будет храниться информация о счете и статистика игроков
            teams_stats = {'radiant': {}, 'dire': {}}
            players_stats = {}

            teams_stats['radiant']['score'] = data.get('radiant_score', 0)
            teams_stats['dire']['score'] = data.get('dire_score', 0)

            try:
                teams_stats['radiant']['name'] = data['radiant_team'].get('name', 'Radiant')
                teams_stats['dire']['name'] = data['dire_team'].get('name', 'Dire')
            except:
                teams_stats['radiant']['name'] = 'Radiant'
                teams_stats['dire']['name'] = 'Dire'

            #Так как в api нет dire_win, победитель определяется через radiant_win
            is_radiant_win = data.get('radiant_win', False)
            teams_stats['radiant']['winner'] = is_radiant_win
            if is_radiant_win:
                teams_stats['dire']['winner'] = False
            else:
                teams_stats['dire']['winner'] = True


            raw_players_stats = data['players']

            for idx, stats in enumerate(raw_players_stats):
                #Из полученной через api статистики игроков выбирается нужная информация и записывается в словарь players_stats

                player_id = stats.get('account_id', idx)
                players_stats[player_id] = {}
                players_stats[player_id]['name'] = stats.get('personaname', 'Player')
                players_stats[player_id]['hero'] = HEROES.get(stats['hero_id'], 'Hero')
                is_radiant = stats.get('isRadiant', None)
                if is_radiant in (True, False):
                    players_stats[player_id]['team'] = get_team_name(is_radiant, teams_stats)
                else:
                    players_stats[player_id]['team'] = None
                players_stats[player_id]['kills'] = stats.get('kills', 0)
                players_stats[player_id]['assists'] = stats.get('assists', 0)
                players_stats[player_id]['deaths'] = stats.get('deaths', 0)
                players_stats[player_id]['net_worth'] = stats.get('net_worth', 0)
                players_stats[player_id]['last_hits'] = stats.get('last_hits', 0)
                players_stats[player_id]['denies'] = stats.get('denies', 0)
                players_stats[player_id]['gold_per_min'] = stats.get('gold_per_min', 0)
                players_stats[player_id]['xp_per_min'] = stats.get('xp_per_min', 0)
                players_stats[player_id]['hero_damage'] = stats.get('hero_damage', 0)
                players_stats[player_id]['tower_damage'] = stats.get('tower_damage', 0)
                players_stats[player_id]['hero_healing'] = stats.get('hero_healing', 0)
                players_stats[player_id]['obs_placed'] = stats.get('obs_placed', 0)
                players_stats[player_id]['sen_placed'] = stats.get('sen_placed', 0)

    return {'teams_stats': teams_stats, 'players_stats': players_stats}, match_id