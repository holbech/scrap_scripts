#!/usr/bin/env python
import gzip
import json
import os
import pickle
import string
import urllib2
import xml.etree.ElementTree as ET
from urllib2 import HTTPError
import time
from xml.etree.ElementTree import ParseError

def get_ids(filename='/tmp/ids'):
    all_id = set()
    with open(filename, 'w') as id_file:
        for char in string.ascii_lowercase:
            print "Checking " + char
            result = ET.fromstring(urllib2.urlopen('http://www.boardgamegeek.com/xmlapi2/search?type=boardgame&query=' + char).read())
            count = 0
            for item in result.iter('item'):
                count += 1
                id_file.write(item.attrib['id'] + '\n')
                all_id.add(int(item.attrib['id']))
            print "Found %d" % (count,)
    all_id = sorted(all_id)
    print "Re-writing sorted"
    with open(filename, 'w') as id_file:
        id_file.write('\n'.join( str(i) for i in all_id ) + '\n')
    print "All done"

def get_collection(username, filename='/tmp/collection'):
    with open(filename, 'w') as id_file:
        result = ET.fromstring(urllib2.urlopen('http://www.boardgamegeek.com/xmlapi/collection/' + username).read())
        ids = set()
        for item in result.iter('item'):
            status = item.find('status')
            if status is not None and status.attrib['own'] != "0":
                ids.add(item.attrib['objectid'])
        pickle.dump(tuple(ids), id_file)

def get_expansion_ids(filename='/tmp/exp_ids'):
    all_id = set()
    with open(filename, 'w') as id_file:
        for char in string.ascii_lowercase:
            print "Checking " + char
            result = ET.fromstring(urllib2.urlopen('http://www.boardgamegeek.com/xmlapi2/search?type=boardgameexpansion&query=' + char).read())
            count = 0
            for item in result.iter('item'):
                count += 1
                id_file.write(item.attrib['id'] + '\n')
                all_id.add(int(item.attrib['id']))
            print "Found %d" % (count,)
    all_id = sorted(all_id)
    print "Re-writing sorted"
    with open(filename, 'w') as id_file:
        id_file.write('\n'.join( str(i) for i in all_id ) + '\n')
    print "All done"

def get_ratings(out_filename):
    stride = 100
    for start_index in xrange(0, 160000, stride):
        batch_ids = ','.join( str(i) for i in xrange(start_index,start_index+stride) )
        filename = out_filename + '_%d_to_%d.json.gz' % (start_index, start_index+stride-1)
        if os.path.exists(filename):
            print "Skipping %d to %d" % (start_index, start_index+stride-1)
        else:
            print "Getting %d to %d" % (start_index, start_index+stride-1)
            games = []
            for bgtype in ('boardgame', 'boardgameexpansion'): 
                result = ET.fromstring(urllib2.urlopen('http://www.boardgamegeek.com/xmlapi2/thing?id=%s&stats=1&type=%s' % (batch_ids, bgtype)).read())
                for item in result.iter('item'):
                    if item.attrib['type'] == bgtype:
                        game = { 'type': bgtype, 'id': item.attrib['id'] }
                        for attr in ('name', 'minplayers', 'maxplayers'):
                            game[attr] = item.find(attr)
                            if game[attr] is not None:
                                game[attr] = game[attr].attrib['value']
                        for poll in item.iter('poll'):
                            if poll.attrib['name'] == 'suggested_numplayers':
                                game['players_votes'] = { i.attrib['numplayers']: [ (j.attrib['value'], j.attrib['numvotes']) for j in i.iter('result') ]
                                                          for i in poll.iter('results') }
                        stats = item.find('statistics')
                        if stats is not None:
                            stats = stats.find('ratings')
                            if stats is not None:
                                for attr in ('usersrated', 'average', 'bayesaverage'):
                                    game[attr] = stats.find(attr)
                                    if game[attr] is not None:
                                        game[attr] = game[attr].attrib['value']
                        games.append(game)
            with gzip.GzipFile(filename, 'w') as out_file:
                json.dump(games, out_file)
            

def get_expansion_connections(in_file_dir, out_file):
    expansion_ids = []
    games_ids = set()
    for filename in os.listdir(in_file_dir):
        if filename.endswith('.json.gz'):
            with gzip.GzipFile(os.path.join(in_file_dir, filename), 'r') as input_file:
                for game in json.load(input_file):
                    if game['type'] == 'boardgameexpansion':
                        expansion_ids.append(game['id'])
                    else:
                        games_ids.add(game['id'])
    expansion_ids = sorted(expansion_ids)
    expansion_map = {}
    stride = 100
    for start_index in xrange(0, len(expansion_ids), stride):
        end = min(start_index+stride, len(expansion_ids))
        batch_ids = ','.join( expansion_ids[start_index:end] )
        max_attempts = 14
        for attempt in xrange(max_attempts):
            try:
                print "Getting %s to %s (Attempt %d)" % (expansion_ids[start_index], expansion_ids[end-1], attempt + 1)
                url = 'http://www.boardgamegeek.com/xmlapi/boardgame/%s' % (batch_ids,)
                result = None or ET.fromstring(urllib2.urlopen(url).read())
                break
            except (HTTPError, ParseError):
                if attempt < max_attempts-1:
                    delay = min(2**attempt, 3600)
                    print "Failed getting %s. Waiting %d seconds before trying again." % (url, delay)
                    time.sleep(delay)
        if result is None:
            print "Failed getting", url
        for boardgame in result.iter('boardgame'):
            for exp in boardgame.iter('boardgameexpansion'):
                if exp.attrib['objectid'] in games_ids:
                    expansion_map[boardgame.attrib['objectid']] = exp.attrib['objectid']
    with gzip.GzipFile(out_file, 'w') as output_file:
        json.dump(expansion_map, output_file)
              
def rank(in_file_dir, expansion_connection_file, players=1, algorithm=1, collection_file=None):
    if collection_file:
        with open(collection_file, 'r') as cf:
            collection = pickle.load(cf)
    else:
        collection = None
    with gzip.GzipFile(expansion_connection_file, 'r') as em_file:
        expansion_map = json.load(em_file)
    games = {}
    expansions = {}
    for filename in os.listdir(in_file_dir):
        if filename.endswith('.json.gz'):
            with gzip.GzipFile(os.path.join(in_file_dir, filename), 'r') as input_file:
                for game in json.load(input_file):
                    if game['type'] == 'boardgameexpansion':
                        expansions[game['id']] = game
                    else:
                        games[game['id']] = game
    players = str(players)
    def rating(game):
        if not game.get('usersrated') or (collection and game['id'] not in collection):
            return 0.0
        try:
            base_rate = float(game['bayesaverage'])
            all_player_votes = { p: { v1: int(v2) for (v1,v2) in votes }
                                 for p, votes in game['players_votes'].iteritems() }
            all_votes = sum( v for votes in all_player_votes.itervalues() for v in votes.itervalues()  )
            avg_votes_cast = all_votes/float(len(all_player_votes))
            player_votes = all_player_votes.get(players, {})
            if not player_votes or sum(player_votes.itervalues()) < (avg_votes_cast/4):
                return 0.0
            if algorithm == 1:
                for_votes = player_votes['Recommended']/2.0 + player_votes['Best']
            else:
                for_votes = player_votes['Recommended'] + (player_votes['Best'] * 2.0)
            against_votes = player_votes['Not Recommended']
            total_votes = for_votes + against_votes
            if total_votes == 0:
                return 0.0
            else:
                return base_rate*(for_votes/total_votes)
        except Exception as ex:
            print ex, game
            return 0.0
    print "Games:"
    for r, game in sorted(( (rating(g),g) for g in games.itervalues() ), reverse=True):
        if r > 0.0:
            print (u'%s (%s): %2.2f' % (game['name'], game['id'], r)).encode('utf-8')
    print "Expansions:"
    for r, exp in sorted(( (rating(e),e) for e in expansions.itervalues() ), reverse=True):
        game = games.get(expansion_map.get(exp['id']))
        if r > 0.0 and game is not None:
            print (u'%s - %s (%s/%s): %2.2f' % (exp['name'], game['name'], exp['id'], game['id'], r)).encode('utf-8')
    
if __name__ == '__main__':
    # get_collection("holbech", "/home/holbech/ratings/collection")
    # get_ids()
    #get_ratings('/home/holbech/ratings/ratings')
    #get_expansion_connections('/home/holbech/ratings/', '/home/holbech/expansion_connections.json.gz')
    rank('/home/holbech/ratings/', '/home/holbech/expansion_connections.json.gz', players=3, algorithm=1, collection_file="/home/holbech/ratings/collection")
    