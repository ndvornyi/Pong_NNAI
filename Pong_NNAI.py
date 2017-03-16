try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
    from SimpleGUICS2Pygame.simplegui_lib_keys import Keys

import random
import pybrain 
from pybrain.structure import FeedForwardNetwork
from pybrain.structure import LinearLayer, SigmoidLayer, TanhLayer
from pybrain.structure import FullConnection
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure import RecurrentNetwork
# initialize globals - pos and vel encode vertical info for paddles
WIDTH = 600.0
HEIGHT = 400.0     
BALL_RADIUS = 15
PAD_WIDTH = 8
PAD_HEIGHT = 80
HALF_PAD_WIDTH = PAD_WIDTH / 2
HALF_PAD_HEIGHT = PAD_HEIGHT / 2
ball_pos = [0, 0]
LEFT = False
RIGHT = True
new_game_switch = False
ball_vel = [0,0]
pad_vel = 15
center = [WIDTH/2,HEIGHT/2]
wanted_direction = 0
frame_gap = 0  
frames_limit = 0
trained_status = False
# initialize ball_pos and ball_vel for new bal in middle of table
# if direction is RIGHT, the ball's velocity is upper right, else upper left
    
def spawn_ball(direction):
    global ball_pos, ball_vel, start_hor_vel, start_ver_vel
    
    ball_pos = center[:]
    
    start_hor_vel=random.randrange(5, 8)
    start_ver_vel=random.randrange(1, 3)
    float(start_hor_vel)
    float(start_ver_vel)
    
    if direction==True:
        ball_vel=[start_hor_vel,-start_ver_vel]
    elif direction==False: 
        ball_vel=[-start_hor_vel,-start_ver_vel]

# define event handlers
def new_game():
    global paddle1_pos, paddle2_pos, paddle1_vel, paddle2_vel, ball_pos  # these are numbers
    global score1, score2, new_game_switch, frames_limit, trained_status

    frames_limit = 0
    trained_status = False
    
    paddle1_pos = HEIGHT/2
    paddle2_pos = HEIGHT/2
    
    paddle1_vel = 0 
    paddle2_vel = 0 
    
    score1=0
    score2=0
    
    new_game_switch = not new_game_switch
    if new_game_switch==True: 
        spawn_ball(RIGHT)
    else: 
        spawn_ball(LEFT)

def print_connects():

    print nn.params

def nntrain():
    global frames_limit
    trainer.trainEpochs(300)
    ds.clear()
    print "Trained on ", frames_limit," frames"

def draw(canvas):
    global score1, score2, paddle1_pos, paddle2_pos, ball_pos, ball_vel, ds, start_hor_vel, start_ver_vel, trained_status, nnfire, wanted_direction, frames_limit, frame_gap

    # draw mid line and gutters
    canvas.draw_line([WIDTH / 2, 0],[WIDTH / 2, HEIGHT], 1, "White")
    canvas.draw_line([PAD_WIDTH, 0],[PAD_WIDTH, HEIGHT], 1, "White")
    canvas.draw_line([WIDTH - PAD_WIDTH, 0],[WIDTH - PAD_WIDTH, HEIGHT], 1, "White")
        
    # update ball and check collission  
    if ball_pos[1]-BALL_RADIUS<=0 or ball_pos[1]+BALL_RADIUS>=HEIGHT:
        ball_vel[1] = -ball_vel[1]
        
    if ball_pos[0]-BALL_RADIUS<=PAD_WIDTH:
         if paddle1_pos+HALF_PAD_HEIGHT+5>=ball_pos[1]>=paddle1_pos-HALF_PAD_HEIGHT-5:
                ball_vel[0]=-ball_vel[0]*1.1
                
                ball_vel[1]=ball_vel[1]*1.1
         else:       
            score2+=1
            spawn_ball(RIGHT)
   
    
    if ball_pos[0]+BALL_RADIUS>=WIDTH-PAD_WIDTH:
        if paddle2_pos+HALF_PAD_HEIGHT+5>=ball_pos[1]>=paddle2_pos-HALF_PAD_HEIGHT-5:
            ball_vel[0]= -ball_vel[0]*1.1
            ball_vel[1]=ball_vel[1]*1.1
            



        else:
            score1+=1
            spawn_ball(LEFT) 

    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]
    
       # collect frames in dataset, 1 frame by every 3
    if frame_gap == 3:
        frame_gap = 0
        if frames_limit == 50:
            if trained_status == False:
                nntrain()
                trained_status = True

        else:
            ds.addSample((ball_pos[0]/WIDTH,ball_pos[1]/HEIGHT,ball_vel[1]/start_ver_vel), ball_pos[1]/HEIGHT)
            frames_limit+=1
    frame_gap+=1

    nnfire=float(nn.activate([ball_pos[0]/WIDTH,ball_pos[1]/HEIGHT,ball_vel[1]/start_ver_vel]))

    # draw ball
    canvas.draw_circle(ball_pos, BALL_RADIUS, 1, "Red", "Red")

    # update paddle's vertical position, keep paddle on the screen
    if paddle1_pos + paddle1_vel >= HALF_PAD_HEIGHT and paddle1_pos + paddle1_vel <= HEIGHT - HALF_PAD_HEIGHT:
        paddle1_pos += paddle1_vel
        
    # if paddle2_pos + pad_vel >= HALF_PAD_HEIGHT and paddle2_pos + pad_vel <= HEIGHT - HALF_PAD_HEIGHT:
    paddle2_pos = nnfire*HEIGHT

    # draw paddles
    canvas.draw_line([HALF_PAD_WIDTH, paddle1_pos - HALF_PAD_HEIGHT], [HALF_PAD_WIDTH, paddle1_pos + HALF_PAD_HEIGHT], PAD_WIDTH, "White")
    canvas.draw_line([WIDTH - HALF_PAD_WIDTH, paddle2_pos - HALF_PAD_HEIGHT], [WIDTH - HALF_PAD_WIDTH, paddle2_pos + HALF_PAD_HEIGHT], PAD_WIDTH, "White")
    # determine whether paddle and ball collide    
    
    # draw scores
    canvas.draw_text(str(score1),[150, 40],20,"White")
    canvas.draw_text(str(score2),[450, 40],20,"White")
    canvas.draw_text(str(frames_limit)+ " frames collected",[40, 360],20,"White")
    canvas.draw_text("Trained: " + str(trained_status),[440, 360],20,"White")

def keydown(key):
    global paddle1_vel, paddle2_vel
    if key == 172:
        key = 87
    elif key == 161:
        key = 83
    if key == simplegui.KEY_MAP["up"]:
        paddle2_vel -= pad_vel
    elif key == simplegui.KEY_MAP["down"]:
        paddle2_vel += pad_vel
    elif key == simplegui.KEY_MAP["w"]:
        paddle1_vel -= pad_vel
    elif key == simplegui.KEY_MAP["s"]:
        paddle1_vel += pad_vel

def keyup(key):
    global paddle1_vel, paddle2_vel
    if key == 172:
        key = 87
    elif key == 161:
        key = 83
    if key == simplegui.KEY_MAP["up"]:
        paddle2_vel += pad_vel
    elif key == simplegui.KEY_MAP["down"]:
        paddle2_vel -= pad_vel
    elif key == simplegui.KEY_MAP["w"]:
        paddle1_vel += pad_vel
    elif key == simplegui.KEY_MAP["s"]:
        paddle1_vel -= pad_vel

# NN implementation 
nn = FeedForwardNetwork()

inLayer = LinearLayer(3)
hidden1Layer = LinearLayer(5)
hidden2Layer = LinearLayer(5)
outLayer = LinearLayer(1)

nn.addInputModule(inLayer)
nn.addModule(hidden1Layer)
nn.addModule(hidden2Layer)
nn.addOutputModule(outLayer)

in_to_hidden1 = FullConnection(inLayer, hidden1Layer)
hidden1_to_hidden2=FullConnection(hidden1Layer, hidden2Layer)
hidden2_to_out = FullConnection(hidden2Layer, outLayer)
nn.addConnection(in_to_hidden1)
nn.addConnection(hidden1_to_hidden2)
nn.addConnection(hidden2_to_out)
#nn.addRecurrentConnection(FullConnection(outLayer,hidden1Layer))
#nn.addRecurrentConnection(FullConnection(hidden2Layer,hidden2Layer))
nn.sortModules()
# Dataset and trainer init
ds=SupervisedDataSet(3, 1)
trainer = BackpropTrainer(nn , dataset=ds, learningrate = 0.03)

# create frame
frame = simplegui.create_frame("Pong", WIDTH, HEIGHT)
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.add_button("New game!", new_game, 100)
frame.add_button("Print connects", print_connects, 100)
frame.add_button("Train", nntrain, 100)

# start frame
new_game()
frame.start()