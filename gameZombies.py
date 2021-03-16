import random
from enum import IntEnum

# Default game interface :
def main():
    gameEngine= Engine()
    player= HumanPlayer()
    gameEngine.run( player )

# Agent as a very simple UI
class HumanPlayer() :

    def __int__( self, name= "bob" ):
        self.name= name

    def wakeUp( self, initialStateStr, actionSpace ):
        self.state= initialStateStr
        print( "Start on: "+ self.state )
        print( "> Possible actions: "+ str( actionSpace ) )
    
    def perceive(self, reachedStateStr, reward):
        self.state= reachedStateStr
        print( "Perception: "+ self.state  +" with reward : " + str(reward) )
    
    def action(self, isValidAction ) :
        print( "Action ?")
        actionStr= ""
        while not isValidAction( actionStr ) :
            actionStr= input()
        return actionStr
    
    def kill(self, score):
        print( "Game end on score: "+ str(score) )

# Zombie Game elements:

class DiceType(IntEnum):
    EASY= 0
    MEDIUM= 1
    HARD= 2
    UNDEF= 3

class DiceFace(IntEnum):
    BRAIN= 0
    GUN= 1
    RUN= 2

DiceType_str= ["EASY", "MEDI", "HARD","UNDEF"]
DiceFace_str= ["Brain", "Gun", "Run"]
DiceFace_weight= [
    [3, 1, 2 ], #EASY
    [2, 2, 2 ], #MEDIUM
    [1, 3, 2 ], #HARD
    [0, 0, 1 ], #UNDEF
]

class Dice():
    x= 0

    # Instance initialization
    #------------------------
    def __init__(self):
        self.type= DiceType.UNDEF
        self.face= DiceFace.RUN

    def __str__(self):
        if self.type == DiceType.UNDEF :
            return "UNDEFINED"
        return DiceType_str[self.type] +"("+ DiceFace_str[self.face] +")"

    # Builder
    #--------
    def setType(self, type):
        self.type= type
        self.face= DiceFace.RUN

    # Trandom transition
    #-------------------
    def random_face(self):
        weight= DiceFace_weight[self.type]
        rand= random.randrange( sum( weight ) )
        #print("random "+ str(rand) + " in [0, "+ str(sum(weight)) +"]")
        for face in DiceFace :
            if rand < weight[face] :
                return face
            rand-= weight[face]
        return DiceFace.RUN

    def roll(self):
        self.face= self.random_face()

class Engine :

    # Instance initialization
    #------------------------
    def __init__(self, nbDice=3, stockEASY=6, stockMEDIUM=4, stockHARD=3):
        self.nbDice= nbDice
        self.stockEASY= stockEASY
        self.stockMEDIUM= stockMEDIUM
        self.stockHARD= stockHARD

    # Instance initialization
    #------------------------
    def initialize( self ):
        self.hand= [0] * self.nbDice
        for i in range( 0, self.nbDice ) :
            self.hand[i]= Dice()
        self.brain= 0
        self.shot= 0
        self.stock= [ self.stockEASY, self.stockMEDIUM, self.stockHARD ]
        self.score= 0
        self.reward= 0

    # Engine
    #--------
    def valideAction(self, action) :
        return action in ( "go", "stop" )

    def run( self, player ):
        self.initialize()
        player.wakeUp( self.stateStr(), ["go", "stop"] )
        stop= False
        while not stop :
            # ask
            action= player.action( self.valideAction )

            if action == "go" :
                self.step()
                self.reward= self.brain - self.score
                self.score= self.brain

            if action == "stop" or self.remaining_dice() < 3 :
                self.reward= self.brain - self.score
                self.score= self.brain
                self.stock= [ 0, 0, 0 ]
                stop= True
                
            elif self.shot > 2 :
                self.reward= - self.score
                self.score= 0
                self.stock= [ 0, 0, 0 ]
                stop= True

            player.perceive( self.stateStr(), self.reward )

        player.kill( self.score )

    # Accessor
    #---------
    def handDieType(self, idice):
        if self.hand[idice].face == DiceFace.RUN :
            return self.hand[idice].type
        return DiceType.UNDEF

    def remaining_dice(self) :
        count= sum( self.stock )
        for die in self.hand :
            if die.face == DiceFace.RUN :
                count+= 1
        return count

    def remaining_dice(self) :
        count= sum(self.stock)
        for die in self.hand :
            if die.face == DiceFace.RUN :
                count+= 1
        return count

    def state(self):
        return {
            "Brain": self.brain,
            "Shoot": self.shot,
            "D1": str(self.hand[0]),
            "D2": str(self.hand[1]),
            "D3": str(self.hand[2]),
            "EASY": self.stock[DiceType.EASY],
            "MEDIUM": self.stock[DiceType.MEDIUM],
            "HARD": self.stock[DiceType.HARD]
        }

    def stateStr(self):
        return "-".join( [str(x) for x in self.state().values() ] )

    # String
    #-------
    def __str__(self):
        stockSum= 0
        for s in self.stock :
            stockSum= stockSum + s

        myStr= "Stock("+ str(stockSum) +"/"+ str(self.remaining_dice()) +"): "
        myStr+= "EASY("+ str(self.stock[DiceType.EASY]) +") "
        myStr+= "MEDIUM("+ str(self.stock[DiceType.MEDIUM]) +") "
        myStr+= "HARD("+ str(self.stock[DiceType.HARD]) +") "
        myStr+= "\t| Dice: "+ str(self.hand[0])
        for i in range(1, len(self.hand) ) :
            myStr+= " - "+ str(self.hand[i])

        return myStr +"\t| Brain: "+ str(self.brain) +" | Shoot: "+ str(self.shot)

    # random transition:
    #-------------------
    def randomType(self):
        rand= random.randrange( sum(self.stock) )
        for type in DiceType :
            if rand < self.stock[type] :
                return type
            rand-= self.stock[type]
        return DiceType.EASY

    def pullRandomDie(self):
        type= self.randomType()
        self.stock[type]-= 1
        return type

    def step(self) :
        for aDie in self.hand :
            # new dice ?
            if aDie.type == DiceType.UNDEF or not( aDie.face == DiceFace.RUN ) :
                type= self.pullRandomDie()
                aDie.setType(type)

            # roll and result:
            aDie.roll()
            if aDie.face == DiceFace.BRAIN :
                self.brain+= 1
            if aDie.face == DiceFace.GUN :
                self.shot+= 1


# Activate default interface :
if __name__ == '__main__':
    main()