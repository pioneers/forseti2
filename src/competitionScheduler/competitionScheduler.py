import csv
import datetime

class MatchSchedule:
  defaultMatchSchedule = "matchSchedule.csv"
  defaultTeamNumbers = "teamNumbers.csv"

  def __init__(self, matchScheduleFile=defaultMatchSchedule, teamNumbersFile=defaultTeamNumbers):
    self.matches = [] # team, team, team, team, time, blueScore, goldScore
    self.labels = []

    self.numberToTeam = {}
    self.teamToNumber = {}

    self.teamRankings = {} # Key: team number -- Value: number:team, ranking points, 
                      # qualification points, wins, ties, losses

    self.currentMatch = 0

    with open(matchScheduleFile, 'r') as csvfile:
      scheduleReader = csv.reader(csvfile, delimiter=',')
      labels = scheduleReader.next()
      for match in scheduleReader:
        match += [0, 0, 0]
        self.matches.append(match)

    with open(teamNumbersFile, 'r') as csvfile:
      teamNumbersReader = csv.reader(csvfile, delimiter=',')
      _ = teamNumbersReader.next()
      for number, team in teamNumbersReader:
        number = int(number)
        self.numberToTeam[number] = team
        self.teamToNumber[team] = number

    for number, team in numberToTeam.iteritems():
      self.teamRankings[number] = [("%s:%s" % (number, team))] + [0]*5


  def getCurrentMatchInfo(self):
    match = self.matches[self.currentMatch]
    return match


  def advanceMatch(self):
    self.currentMatch += 1
    self.currentMatch %= len(self.matches)

  def rewindMatch(self):
    self.currentMatch -= 1
    if self.currentMatch < 0:
      self.currentMatch = 0

  def updateMatch(self, matchNum, time, blueScore, goldScore):
    match = self.currentMatch[matchNum]
    match[4:7] = (time, blueScore, goldScore)

  def readTeamNumbers(teamNumbersFile):
    with open(teamNumbersFile, 'r') as csvfile:
      teamNumbersReader = csv.reader(csvfile, delimiter=',') = teamNumbersReader.next() # Get rid of header information
      for number, team in teamNumbersReader:
        number = int(number)
        newTeam = Team(team, number)
        self.numberToTeam[number] = newTeam
        self.teamToNumber[team] = number



class Team:

  def teamCompare(this, other):
    if this.rankingPoints > other.rankingPoints: 
      return 1
    elif this.rankingPoints < other.rankingPoints:
      return -1
    else:
      return this.qualificationPoints - other.qualificationPoints

  def __init__(self, name, number):
    self.name = name
    self.number = number
    self.rankingPoints = 0
    self.qualificationPoints = 0
    self.numWins = 0
    self.numLosses = 0
    self.numTies = 0



MATCH_QUALIFICATION, MATCH_ELIMINATION = range(len(2))
MATCH_GOLD_ALLIANCE, MATCH_BLUE_ALLIANCE = range(len(2))

class Match:
  def __init__(self, gold0, gold1, blue0, blue1, matchType=MATCH_QUALIFICATION):
    self.goldAlliance = (gold0, gold1)
    self.blueAlliance = (blue0, blue1)
    self.matchTime = None # To be filled in when scores get entered
    self.goldScore = -1
    self.blueScore = -1
    self.matchType = matchType
    self.winner = None

  def getAlliance(self, alliance):
    if alliance == MATCH_GOLD_ALLIANCE:
      return self.goldAlliance
    elif alliance == MATCH_BLUE_ALLIANCE:
      return self.blueAlliance
    else: 
      return None

  def getMatchTime(self):
    return self.matchTime

  def getScore(self, alliance):
    if alliance == MATCH_GOLD_ALLIANCE:
      return self.goldScore
    elif alliance == MATCH_BLUE_ALLIANCE:
      return self.blueScore
    else: 
      return None

  def isMatchCompleted(self):
    return self.matchTime != None

  def getType(self):
    return self.matchType

  def getWinner(self):
    if self.matchTime == None:
      return None
    if self.goldScore > self.blueScore:
      return self.goldAlliance
    elif self.goldScore < self.blueScore:
      return self.blueAlliance
    else:
      return self.goldAlliance + self.blueAlliance

  def updateScore(self, goldScore, blueScore):
    self.goldScore = goldScore
    self.blueScore = blueScore
    if self.matchTime == None:
      self.matchTime = datetime.datetime.now()
