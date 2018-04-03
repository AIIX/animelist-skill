import re
import sys
import json
import requests
import unidecode
from adapt.intent import IntentBuilder
from os.path import join, dirname
from string import Template
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.skills.context import *
from mycroft.util import read_stripped_lines
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

__author__ = 'aix'

LOGGER = getLogger(__name__)

class AnimeListSkill(MycroftSkill):
    def __init__(self):
        super(AnimeListSkill, self).__init__(name="AnimeListSkill")
        self.header = { "header": 
                        {"Content-Type": "application/json",
                            "User-Agent": "Mycroft AI",
                            "Accept": "application/json"
                        }
                      }
        self.authurl = self.settings['authurl']
        self.apiurl = self.settings['apiurl']
        self.csecret = self.settings['csecret']
        self.cid = self.settings['cid']
        self.token = self.settings['token']
        self.html_index = dirname(__file__) + '/html/'
        self.css_index = dirname(__file__) + '/html/style.css'

    @intent_handler(IntentBuilder("AnimeSearch").require("AnimeSearchKeyword").build())
    def handle_animesearch_intent(self, message):
        utterance = message.data.get('utterance').lower()
        utterance = utterance.replace(message.data.get('AnimeSearchKeyword'), '')
        searchString = utterance.encode('utf-8')
        searchterm = searchString.lstrip(' ')
        page = 1
        perpage = 5
        query_string = """\
            query ($query: String, $page: Int, $perpage: Int) {
                Page (page: $page, perPage: $perpage) {
                    pageInfo {
                        total
                        currentPage
                        lastPage
                        hasNextPage
                    }
                    media (search: $query, type: ANIME) {
                        id
                        title {
                            romaji
                            english
                        }
                        coverImage {
                            large
                        }
                        averageScore
                        popularity
                        episodes
                        season
                        hashtag
                        isAdult
                    }
                }
            }
        """
        vardata = {"query": searchterm, "page": page, "perpage": perpage}
        r = requests.post(self.apiurl,
                          headers=self.header['header'],
                          json={'query': query_string, 'variables': vardata})
        responseresult = r.text
        self.__genwebview(responseresult)
        self.enclosure.ws.emit(Message("data", {'desktop': {'url': self.html_index + 'animesearchresult.html'}}))
        speakMessage = "Following Series Were Found: {0}, {1}, {2}".format(res0title, res1title, res2title)
        self.speak(speakMessage)
        
    def __genwebview(self, res):
        global res0title, res1title, res2title
        animelistJSONResponse = json.loads(res)
        res0img = animelistJSONResponse['data']['Page']['media'][0]["coverImage"]["large"]
        res0title = animelistJSONResponse['data']['Page']['media'][0]["title"]["romaji"]
        res0episodecount = animelistJSONResponse['data']['Page']['media'][0]["episodes"]
        res1img = animelistJSONResponse['data']['Page']['media'][1]["coverImage"]["large"]
        res1title = animelistJSONResponse['data']['Page']['media'][1]["title"]["romaji"]
        res1episodecount = animelistJSONResponse['data']['Page']['media'][1]["episodes"]
        res2img = animelistJSONResponse['data']['Page']['media'][2]["coverImage"]["large"]
        res2title = animelistJSONResponse['data']['Page']['media'][2]["title"]["romaji"]
        res2episodecount = animelistJSONResponse['data']['Page']['media'][2]["episodes"]
        fname = self.html_index + 'animesearchresult.html'
        f = open(fname,'w')
        wrapper="""<html>
                    <head>
                    <link rel="stylesheet" href="{0}">
                    </head>
                    <body class="cstBody">
                        <ul class="img-list">
                                <li>
                                    <div class="li-content">
                                        <div class="li-img">
                                            <img src="{1}"/>
                                        </div>
                                        <div class="li-text">
                                            <h3 class="li-head">{2}</h3>
                                        </div>
                                        <div class="li-subtext">
                                            <p class="li-sub">Episodes: {3}</p>
                                        </div>
                                    </div>
                                </li>
                                <li>
                                    <div class="li-content">
                                        <div class="li-img">
                                            <img src="{4}" />
                                        </div>
                                        <div class="li-text">
                                            <h3 class="li-head">{5}</h3>
                                        </div>
                                        <div class="li-subtext">
                                            <p class="li-sub">Episodes: {6}</p>
                                        </div>
                                    </div>
                                </li>
                                <li>
                                    <div class="li-content">
                                        <div class="li-img">
                                            <img src="{7}" />
                                        </div>
                                        <div class="li-text">
                                            <h3 class="li-head">{8}</h3>
                                        </div>
                                        <div class="li-subtext">
                                            <p class="li-sub">Episodes: {9}</p>
                                        </div>
                                    </div>
                                </li>
                        </ul>
                    </body>
                    </html>""".format(self.css_index, res0img, res0title, res0episodecount, res1img, res1title, res1episodecount, res2img, res2title, res2episodecount)
        f.write(wrapper)
        f.close()
    
    def stop(self):
        pass
    
def create_skill():
    return AnimeListSkill()
